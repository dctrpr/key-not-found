// Stills, contact sheets and the H.264/AAC export. Uses only system frameworks.
import AVFoundation
import CoreGraphics
import CoreMedia
import CoreVideo
import Foundation
import ImageIO
import UniformTypeIdentifiers

let bitmapInfo = CGImageAlphaInfo.premultipliedFirst.rawValue | CGBitmapInfo.byteOrder32Little.rawValue

func makeBitmap(width: Int, height: Int) -> CGContext {
  guard
    let context = CGContext(
      data: nil, width: width, height: height, bitsPerComponent: 8, bytesPerRow: 0, space: sRGB,
      bitmapInfo: bitmapInfo)
  else { fail("Could not create a bitmap.") }
  return context
}

/// Renders one frame at the given size (the film's 16:9 frame scaled to fit).
func renderStill(_ film: Film, time: Double, width: Int = Int(W), height: Int = Int(H)) -> CGImage {
  let context = makeBitmap(width: width, height: height)
  film.render(time: time, on: Canvas(context))
  return context.makeImage()!
}

func write(_ image: CGImage, to url: URL, jpegQuality: Double? = nil) {
  try? FileManager.default.createDirectory(
    at: url.deletingLastPathComponent(), withIntermediateDirectories: true)
  let type = (jpegQuality == nil ? UTType.png : UTType.jpeg).identifier as CFString
  guard let destination = CGImageDestinationCreateWithURL(url as CFURL, type, 1, nil) else {
    fail("Could not write \(url.lastPathComponent)")
  }
  var options: [CFString: Any] = [:]
  if let jpegQuality { options[kCGImageDestinationLossyCompressionQuality] = jpegQuality }
  CGImageDestinationAddImage(destination, image, options as CFDictionary)
  if !CGImageDestinationFinalize(destination) { fail("Could not write \(url.lastPathComponent)") }
}

/// A grid of small frames with their times, for a quick look at the whole film.
func contactSheet(_ film: Film, times: [Double], columns: Int, to url: URL) {
  let cellW = 640, cellH = 360, pad = 8, label = 30
  let rowsCount = Int(ceil(Double(times.count) / Double(columns)))
  let sheetW = columns * (cellW + pad) + pad
  let sheetH = rowsCount * (cellH + label + pad) + pad
  let sheet = makeBitmap(width: sheetW, height: sheetH)
  sheet.setFillColor(cg(RGB(0x2B2A27)))
  sheet.fill(CGRect(x: 0, y: 0, width: sheetW, height: sheetH))
  let font = film.assets.fonts.mono(18)
  for (index, time) in times.enumerated() {
    let column = index % columns, row = index / columns
    let x = pad + column * (cellW + pad)
    let top = pad + row * (cellH + label + pad)
    let frame = renderStill(film, time: time, width: cellW, height: cellH)
    // Sheet coordinates are bottom-up here.
    let y = sheetH - top - label - cellH
    sheet.draw(frame, in: CGRect(x: x, y: y, width: cellW, height: cellH))
    let text = String(format: "%05.2fs  f%04d", time, Int((time * Double(FPS)).rounded()))
    let attributes: [NSAttributedString.Key: Any] = [
      NSAttributedString.Key(kCTFontAttributeName as String): font,
      NSAttributedString.Key(kCTForegroundColorAttributeName as String): cg(Ink.paper),
    ]
    let line = CTLineCreateWithAttributedString(NSAttributedString(string: text, attributes: attributes))
    sheet.textPosition = CGPoint(x: x + 4, y: sheetH - top - 22)
    CTLineDraw(line, sheet)
  }
  write(sheet.makeImage()!, to: url)
}

// MARK: Movie

private func audioBuffer(_ score: Score, from start: Int, count: Int) -> CMSampleBuffer? {
  var description = AudioStreamBasicDescription(
    mSampleRate: score.rate, mFormatID: kAudioFormatLinearPCM,
    mFormatFlags: kAudioFormatFlagIsFloat | kAudioFormatFlagIsPacked, mBytesPerPacket: 8,
    mFramesPerPacket: 1, mBytesPerFrame: 8, mChannelsPerFrame: 2, mBitsPerChannel: 32, mReserved: 0)
  var layout = AudioChannelLayout()
  layout.mChannelLayoutTag = kAudioChannelLayoutTag_Stereo
  var format: CMAudioFormatDescription?
  guard
    CMAudioFormatDescriptionCreate(
      allocator: kCFAllocatorDefault, asbd: &description,
      layoutSize: MemoryLayout<AudioChannelLayout>.size, layout: &layout, magicCookieSize: 0,
      magicCookie: nil, extensions: nil, formatDescriptionOut: &format) == noErr, let format
  else { return nil }
  var interleaved = [Float](repeating: 0, count: count * 2)
  for n in 0..<count {
    interleaved[n * 2] = score.left[start + n]
    interleaved[n * 2 + 1] = score.right[start + n]
  }
  let bytes = count * 8
  var block: CMBlockBuffer?
  guard
    CMBlockBufferCreateWithMemoryBlock(
      allocator: kCFAllocatorDefault, memoryBlock: nil, blockLength: bytes,
      blockAllocator: kCFAllocatorDefault, customBlockSource: nil, offsetToData: 0,
      dataLength: bytes, flags: 0, blockBufferOut: &block) == kCMBlockBufferNoErr, let block
  else { return nil }
  let copied = interleaved.withUnsafeBytes {
    CMBlockBufferReplaceDataBytes(
      with: $0.baseAddress!, blockBuffer: block, offsetIntoDestination: 0, dataLength: bytes)
  }
  guard copied == kCMBlockBufferNoErr else { return nil }
  var sample: CMSampleBuffer?
  guard
    CMAudioSampleBufferCreateReadyWithPacketDescriptions(
      allocator: kCFAllocatorDefault, dataBuffer: block, formatDescription: format,
      sampleCount: count, presentationTimeStamp: CMTime(value: CMTimeValue(start), timescale: CMTimeScale(score.rate)),
      packetDescriptions: nil, sampleBufferOut: &sample) == noErr
  else { return nil }
  return sample
}

/// Counters shared between the two writer queues and the watchdog.
private final class ExportProgress {
  private let lock = NSLock()
  private var frames = 0
  private var samples = 0
  private var problem: String?

  func set(frames value: Int) {
    lock.lock()
    frames = value
    lock.unlock()
  }
  func set(samples value: Int) {
    lock.lock()
    samples = value
    lock.unlock()
  }
  func report(_ message: String) {
    lock.lock()
    if problem == nil { problem = message }
    lock.unlock()
  }
  func snapshot() -> (frames: Int, samples: Int, problem: String?) {
    lock.lock()
    defer { lock.unlock() }
    return (frames, samples, problem)
  }
}

private func describe(_ writer: AVAssetWriter) -> String {
  let status: String
  switch writer.status {
  case .unknown: status = "unknown"
  case .writing: status = "writing"
  case .completed: status = "completed"
  case .failed: status = "failed"
  case .cancelled: status = "cancelled"
  @unknown default: status = "other"
  }
  return "writer \(status)" + (writer.error.map { ": \($0.localizedDescription)" } ?? "")
}

/// The writer stages its fast-start copy beside the target. Clear whatever an
/// interrupted or finished export left there.
private func removeStagingFiles(for url: URL) {
  let manager = FileManager.default
  let folder = url.deletingLastPathComponent()
  let prefix = url.lastPathComponent + ".sb-"
  for name in (try? manager.contentsOfDirectory(atPath: folder.path)) ?? []
  where name.hasPrefix(prefix) {
    try? manager.removeItem(at: folder.appendingPathComponent(name))
  }
}

/// Writes the film as H.264 (and AAC when a score is given) in an MP4 whose
/// index sits at the front, with no descriptive metadata.
///
/// The writer interleaves the two tracks and holds one back until the other
/// catches up, so each input is fed from its own queue whenever the writer asks
/// for more. The calling thread only watches: it prints progress and stops the
/// export with the writer's state if nothing moves for `stallLimit` seconds.
func exportMovie(
  _ film: Film, score: Score?, to url: URL, bitrate: Int, seconds: Double? = nil,
  stallLimit: Double = 30
) {
  let manager = FileManager.default
  try? manager.createDirectory(at: url.deletingLastPathComponent(), withIntermediateDirectories: true)
  try? manager.removeItem(at: url)
  removeStagingFiles(for: url)
  guard let writer = try? AVAssetWriter(outputURL: url, fileType: .mp4) else {
    fail("Could not open \(url.lastPathComponent) for writing.")
  }
  writer.shouldOptimizeForNetworkUse = true
  writer.metadata = []
  let width = Int(W), height = Int(H)
  let frameTotal = min(FRAME_COUNT, max(1, Int(((seconds ?? DURATION) * Double(FPS)).rounded())))
  let length = Double(frameTotal) / Double(FPS)
  let video = AVAssetWriterInput(
    mediaType: .video,
    outputSettings: [
      AVVideoCodecKey: AVVideoCodecType.h264,
      AVVideoWidthKey: width,
      AVVideoHeightKey: height,
      AVVideoColorPropertiesKey: [
        AVVideoColorPrimariesKey: AVVideoColorPrimaries_ITU_R_709_2,
        AVVideoTransferFunctionKey: AVVideoTransferFunction_ITU_R_709_2,
        AVVideoYCbCrMatrixKey: AVVideoYCbCrMatrix_ITU_R_709_2,
      ],
      AVVideoCompressionPropertiesKey: [
        AVVideoAverageBitRateKey: bitrate,
        AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel,
        AVVideoMaxKeyFrameIntervalKey: FPS * 2,
        AVVideoExpectedSourceFrameRateKey: FPS,
        AVVideoAllowFrameReorderingKey: true,
      ],
    ])
  video.expectsMediaDataInRealTime = false
  let adaptor = AVAssetWriterInputPixelBufferAdaptor(
    assetWriterInput: video,
    sourcePixelBufferAttributes: [
      kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA,
      kCVPixelBufferWidthKey as String: width,
      kCVPixelBufferHeightKey as String: height,
      kCVPixelBufferCGBitmapContextCompatibilityKey as String: true,
    ])
  guard writer.canAdd(video) else { fail("The writer refused the video settings.") }
  writer.add(video)

  var audio: AVAssetWriterInput?
  if score != nil {
    var layout = AudioChannelLayout()
    layout.mChannelLayoutTag = kAudioChannelLayoutTag_Stereo
    let input = AVAssetWriterInput(
      mediaType: .audio,
      outputSettings: [
        AVFormatIDKey: kAudioFormatMPEG4AAC,
        AVSampleRateKey: 48_000,
        AVNumberOfChannelsKey: 2,
        AVEncoderBitRateKey: 160_000,
        AVChannelLayoutKey: Data(bytes: &layout, count: MemoryLayout<AudioChannelLayout>.size),
      ])
    input.expectsMediaDataInRealTime = false
    guard writer.canAdd(input) else { fail("The writer refused the audio settings.") }
    writer.add(input)
    audio = input
  }
  guard writer.startWriting() else { fail("Export could not start: \(describe(writer))") }
  writer.startSession(atSourceTime: .zero)

  let progress = ExportProgress()
  let inputs = DispatchGroup()
  let started = Date()
  func abandon(_ message: String) -> Never {
    writer.cancelWriting()
    removeStagingFiles(for: url)
    fail(message)
  }

  // Picture: render and append whenever the writer is ready for it.
  inputs.enter()
  var nextFrame = 0
  var videoDone = false
  video.requestMediaDataWhenReady(on: DispatchQueue(label: "key404.film.video")) {
    while !videoDone && video.isReadyForMoreMediaData {
      if nextFrame >= frameTotal || writer.status != .writing {
        if writer.status != .writing { progress.report("Picture stopped: \(describe(writer))") }
        videoDone = true
        video.markAsFinished()
        inputs.leave()
        return
      }
      autoreleasepool {
        var pixelBuffer: CVPixelBuffer?
        guard let pool = adaptor.pixelBufferPool,
          CVPixelBufferPoolCreatePixelBuffer(nil, pool, &pixelBuffer) == kCVReturnSuccess,
          let buffer = pixelBuffer
        else {
          progress.report("Could not allocate a video frame.")
          return
        }
        CVPixelBufferLockBaseAddress(buffer, [])
        if let context = CGContext(
          data: CVPixelBufferGetBaseAddress(buffer), width: width, height: height,
          bitsPerComponent: 8, bytesPerRow: CVPixelBufferGetBytesPerRow(buffer), space: sRGB,
          bitmapInfo: bitmapInfo)
        {
          film.render(time: Double(nextFrame) / Double(FPS), on: Canvas(context))
        }
        CVPixelBufferUnlockBaseAddress(buffer, [])
        let time = CMTime(value: CMTimeValue(nextFrame), timescale: CMTimeScale(FPS))
        if !adaptor.append(buffer, withPresentationTime: time) {
          progress.report("Frame \(nextFrame) was refused: \(describe(writer))")
        }
      }
      nextFrame += 1
      progress.set(frames: nextFrame)
    }
  }

  // Sound: fed from its own queue so neither track can starve the other.
  var sampleTotal = 0
  if let audio, let score {
    sampleTotal = min(score.left.count, Int(length * score.rate))
    inputs.enter()
    var cursor = 0
    var audioDone = false
    audio.requestMediaDataWhenReady(on: DispatchQueue(label: "key404.film.audio")) {
      while !audioDone && audio.isReadyForMoreMediaData {
        if cursor >= sampleTotal || writer.status != .writing {
          if writer.status != .writing { progress.report("Sound stopped: \(describe(writer))") }
          audioDone = true
          audio.markAsFinished()
          inputs.leave()
          return
        }
        let count = min(8192, sampleTotal - cursor)
        guard let buffer = audioBuffer(score, from: cursor, count: count), audio.append(buffer)
        else {
          progress.report("Sound was refused at sample \(cursor): \(describe(writer))")
          audioDone = true
          audio.markAsFinished()
          inputs.leave()
          return
        }
        cursor += count
        progress.set(samples: cursor)
      }
    }
  }

  // Watchdog: report progress, and never wait silently on a stalled writer.
  var seen = (frames: -1, samples: -1)
  var lastMove = Date()
  var lastLog = Date.distantPast
  while inputs.wait(timeout: .now() + 0.5) == .timedOut {
    let now = progress.snapshot()
    if let problem = now.problem { abandon("Export failed. \(problem)") }
    if now.frames != seen.frames || now.samples != seen.samples {
      seen = (now.frames, now.samples)
      lastMove = Date()
    }
    if Date().timeIntervalSince(lastLog) >= 5 {
      lastLog = Date()
      print(
        String(
          format: "  picture %4d/%d frames, sound %5.1f/%.1fs, %.0fs elapsed, %@", now.frames,
          frameTotal, Double(now.samples) / 48_000, Double(sampleTotal) / 48_000,
          Date().timeIntervalSince(started), describe(writer)))
      fflush(stdout)
    }
    if Date().timeIntervalSince(lastMove) > stallLimit {
      abandon(
        "Export stalled for \(Int(stallLimit))s at frame \(now.frames) of \(frameTotal), "
          + "sound sample \(now.samples) of \(sampleTotal); \(describe(writer)); "
          + "picture ready: \(video.isReadyForMoreMediaData), sound ready: \(audio?.isReadyForMoreMediaData ?? false)")
    }
  }
  if let problem = progress.snapshot().problem { abandon("Export failed. \(problem)") }

  writer.endSession(atSourceTime: CMTime(value: CMTimeValue(frameTotal), timescale: CMTimeScale(FPS)))
  let finished = DispatchSemaphore(value: 0)
  writer.finishWriting { finished.signal() }
  if finished.wait(timeout: .now() + 120) == .timedOut {
    abandon("The file could not be finalised within 120s; \(describe(writer))")
  }
  guard writer.status == .completed else { abandon("Export failed: \(describe(writer))") }
  removeStagingFiles(for: url)
  let size = (try? manager.attributesOfItem(atPath: url.path)[.size] as? Int) ?? 0
  print(
    String(
      format: "Wrote %@: %.1f MB, %.2fs of film, in %.0fs", url.lastPathComponent,
      Double(size) / 1_048_576, length, Date().timeIntervalSince(started)))
}

/// Reads the finished file back: container facts and a few decoded frames.
func inspectMovie(at url: URL, frames times: [Double], into directory: URL) {
  let asset = AVURLAsset(url: url)
  let done = DispatchSemaphore(value: 0)
  Task {
    defer { done.signal() }
    do {
      let duration = try await asset.load(.duration)
      print(String(format: "duration %.3fs", duration.seconds))
      for track in try await asset.load(.tracks) {
        let rate = try await track.load(.estimatedDataRate)
        if track.mediaType == .video {
          let size = try await track.load(.naturalSize)
          let fps = try await track.load(.nominalFrameRate)
          print(String(format: "video %.0fx%.0f, %.2f fps, %.2f Mbit/s", size.width, size.height, fps, rate / 1_000_000))
        } else {
          print(String(format: "%@ %.0f kbit/s", track.mediaType.rawValue, rate / 1000))
        }
      }
      let metadata = try await asset.load(.metadata)
      print("metadata items: \(metadata.count)")
      let generator = AVAssetImageGenerator(asset: asset)
      generator.requestedTimeToleranceBefore = .zero
      generator.requestedTimeToleranceAfter = .zero
      for time in times {
        let image = try await generator.image(at: CMTime(seconds: time, preferredTimescale: 600)).image
        let name = String(format: "decoded-%05.2f.png", time)
        write(image, to: directory.appendingPathComponent(name))
        print("Wrote \(name)")
      }
    } catch {
      print("Could not inspect the file: \(error.localizedDescription)")
    }
  }
  done.wait()
}
