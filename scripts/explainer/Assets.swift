// Fonts, scans and the line-exact transcript, all read from this repository.
import CoreGraphics
import CoreText
import Foundation
import ImageIO

/// The site's own typefaces, loaded from the packages `npm ci` installs.
final class FontBook {
  private let grotesk: CTFontDescriptor
  private let mono400: CTFontDescriptor
  private let mono500: CTFontDescriptor
  private var cache: [String: CTFont] = [:]

  init(root: URL) {
    let files = root.appendingPathComponent("node_modules")
    grotesk = FontBook.descriptor(
      files.appendingPathComponent(
        "@fontsource-variable/space-grotesk/files/space-grotesk-latin-wght-normal.woff2"))
    mono400 = FontBook.descriptor(
      files.appendingPathComponent(
        "@fontsource/ibm-plex-mono/files/ibm-plex-mono-latin-400-normal.woff2"))
    mono500 = FontBook.descriptor(
      files.appendingPathComponent(
        "@fontsource/ibm-plex-mono/files/ibm-plex-mono-latin-500-normal.woff2"))
  }

  private static func descriptor(_ url: URL) -> CTFontDescriptor {
    guard
      let list = CTFontManagerCreateFontDescriptorsFromURL(url as CFURL) as? [CTFontDescriptor],
      let first = list.first
    else { fail("Missing font \(url.lastPathComponent). Run `npm ci` in the repository first.") }
    return first
  }

  /// Space Grotesk at any weight on its variable axis.
  func sans(_ size: CGFloat, _ weight: CGFloat = 650) -> CTFont {
    let key = "s\(size)-\(weight)"
    if let font = cache[key] { return font }
    let axis = NSNumber(value: 0x7767_6874 as UInt32)  // 'wght'
    let described = CTFontDescriptorCreateCopyWithVariation(grotesk, axis, weight)
    let font = CTFontCreateWithFontDescriptor(described, size, nil)
    cache[key] = font
    return font
  }

  func mono(_ size: CGFloat, medium: Bool = true) -> CTFont {
    let key = "m\(size)-\(medium)"
    if let font = cache[key] { return font }
    let font = CTFontCreateWithFontDescriptor(medium ? mono500 : mono400, size, nil)
    cache[key] = font
    return font
  }
}

/// One printed character of the article, with where it sits on its page.
struct Particle {
  var glyph: CGGlyph = 0
  var page = 0  // 0...4 for printed pages 75...79
  var row = 0  // printed row within its page
  var col = 0
  var order = 0  // reading order across the whole article
  var u = 0.0  // centre in page-normalised coordinates
  var v = 0.0
  var pitch = 0.0  // character advance as a fraction of the page width
  var isHighlighted = false  // sits on the magazine's orange highlighter
  var isBar = false  // reversed out of a black bar
  var isFirstWord = false
  var numberToken = -1  // which of the selected printed numbers, if any
  var numberIndex = 0
  var fragment = -1  // highlighted run on page 75, if any
  var fragmentIndex = 0
  var s1 = 0.0
  var s2 = 0.0
  var s3 = 0.0
  var s4 = 0.0
}

struct PrintedRow {
  let page: Int
  let row: Int
  let text: String
  let firstWordLength: Int
}

final class Assets {
  static let pageNumbers = Array(73...80)
  static let bodyPages = Array(75...79)
  let fonts: FontBook
  private(set) var small: [Int: CGImage] = [:]
  private(set) var large: [Int: CGImage] = [:]
  private(set) var particles: [Particle] = []
  private(set) var rows: [PrintedRow] = []
  private(set) var numberTokens: [String] = []
  private(set) var fragmentCount = 0
  let particleFont: CTFont
  static let particleFontSize: CGFloat = 20

  init(root: URL) {
    fonts = FontBook(root: root)
    particleFont = fonts.mono(Assets.particleFontSize, medium: true)
    let pagesDir = root.appendingPathComponent("public/research/sources/pages")
    var analysis: [Int: (bytes: [UInt8], w: Int, h: Int)] = [:]
    for number in Assets.pageNumbers {
      let url = pagesDir.appendingPathComponent("\(number).jpg")
      guard let source = CGImageSourceCreateWithURL(url as CFURL, nil) else {
        fail("Missing source scan public/research/sources/pages/\(number).jpg")
      }
      small[number] = Assets.thumbnail(source, 620)
      if number == 75 { large[number] = Assets.thumbnail(source, 2300) }
      if number == 73 { large[number] = Assets.thumbnail(source, 1500) }
      if Assets.bodyPages.contains(number) {
        analysis[number] = Assets.pixels(Assets.thumbnail(source, 1632))
      }
    }
    loadTranscript(root: root, analysis: analysis)
  }

  func page(_ number: Int, height: Double) -> CGImage {
    if height > 600, let image = large[number] { return image }
    return small[number]!
  }

  private static func thumbnail(_ source: CGImageSource, _ maxSide: Int) -> CGImage {
    let options: [CFString: Any] = [
      kCGImageSourceCreateThumbnailFromImageAlways: true,
      kCGImageSourceCreateThumbnailWithTransform: true,
      kCGImageSourceThumbnailMaxPixelSize: maxSide,
    ]
    guard let image = CGImageSourceCreateThumbnailAtIndex(source, 0, options as CFDictionary)
    else { fail("Could not decode a source scan.") }
    return image
  }

  private static func pixels(_ image: CGImage) -> (bytes: [UInt8], w: Int, h: Int) {
    let w = image.width, h = image.height
    var bytes = [UInt8](repeating: 255, count: w * h * 4)
    bytes.withUnsafeMutableBytes { buffer in
      let context = CGContext(
        data: buffer.baseAddress, width: w, height: h, bitsPerComponent: 8, bytesPerRow: w * 4,
        space: sRGB, bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
      context.draw(image, in: CGRect(x: 0, y: 0, width: w, height: h))
    }
    return (bytes, w, h)
  }

  /// Places every printed character from the public transcript on its scan. The
  /// row bands come from the transcript; the left and right edges of each line
  /// are measured from the scan's ink so indents and highlights line up.
  private func loadTranscript(root: URL, analysis: [Int: (bytes: [UInt8], w: Int, h: Int)]) {
    let research = root.appendingPathComponent("public/research")
    guard
      let data = try? Data(contentsOf: research.appendingPathComponent("sources/printed-lines.json")),
      let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
      let list = json["rows"] as? [[String: Any]]
    else { fail("Could not read public/research/sources/printed-lines.json") }

    // The 24 printed numbers selected by the recorded numeric method.
    var numberSpans: [String: [(start: Int, end: Int, token: Int)]] = [:]
    let numericURL = research.appendingPathComponent(
      "analysis_outputs/continuation_20261109/numeric_inventory/numeric_inventory.json")
    if let numericData = try? Data(contentsOf: numericURL),
      let numeric = try? JSONSerialization.jsonObject(with: numericData) as? [String: Any],
      let events = numeric["numericEvents"] as? [[String: Any]],
      let selected = numeric["selectedEventIds"] as? [String]
    {
      for (token, id) in selected.enumerated() {
        guard let event = events.first(where: { $0["id"] as? String == id }),
          let rowId = event["rowId"] as? String, let start = event["start"] as? Int,
          let end = event["end"] as? Int, let surface = event["surface"] as? String
        else { continue }
        numberSpans[rowId, default: []].append((start, end, token))
        numberTokens.append(surface)
      }
    }

    // Pass 1: measure every row on its scan.
    struct Measured {
      let pageNumber: Int
      let printedRow: Int
      let rowId: String
      let characters: [Character]
      let firstWord: Int
      let origin: Double  // left edge of the locator band, in analysis pixels
      let midY: Double
      let band: Double
      let radians: Double
      let first: Double  // first and last inked column, relative to origin
      let last: Double
      let blobs: [Double]  // left edge of each dark run (a printed word)
      var spanPitch: Double { (last - first) / max(1, Double(characters.count) - 0.35) }
    }
    func locate(_ scan: (bytes: [UInt8], w: Int, h: Int), _ radians: Double, _ x: Double, _ y: Double)
      -> (Double, Double)
    {
      // Locator space (the scan turned counter-clockwise) back to the scan.
      let cx = Double(scan.w) / 2, cy = Double(scan.h) / 2
      let dx = x - cx, dy = y - cy
      return (cx + dx * cos(radians) - dy * sin(radians), cy + dx * sin(radians) + dy * cos(radians))
    }
    func pixel(_ scan: (bytes: [UInt8], w: Int, h: Int), _ radians: Double, _ x: Double, _ y: Double)
      -> (Int, Int, Int)
    {
      let (sx, sy) = locate(scan, radians, x, y)
      let ix = min(max(Int(sx.rounded()), 0), scan.w - 1)
      let iy = min(max(Int(sy.rounded()), 0), scan.h - 1)
      let o = (iy * scan.w + ix) * 4
      return (Int(scan.bytes[o]), Int(scan.bytes[o + 1]), Int(scan.bytes[o + 2]))
    }

    var measured: [Measured] = []
    for entry in list {
      guard let pageNumber = entry["page"] as? Int, let text = entry["text"] as? String,
        let locator = entry["locator"] as? [String: Any], let box = locator["box"] as? [Double],
        box.count == 4, let scan = analysis[pageNumber], let rowId = entry["id"] as? String
      else { continue }
      let radians = (locator["rotate_ccw_degrees"] as? Double ?? 0) * .pi / 180
      let k = Double(scan.w) / 2544
      let x0 = box[0] * k, y0 = box[1] * k, x1 = box[2] * k, y1 = box[3] * k
      let columns = max(Int(x1 - x0), 1)
      var inked = [Bool](repeating: false, count: columns)
      var dark = [Bool](repeating: false, count: columns)
      for column in 0..<columns {
        var any = 0, black = 0
        var y = y0
        while y <= y1 {
          let (r, g, b) = pixel(scan, radians, x0 + Double(column), y)
          if min(r, min(g, b)) < 120 { any += 1 }
          if (r * 3 + g * 6 + b) / 10 < 90 { black += 1 }
          y += 1
        }
        inked[column] = any >= 2
        dark[column] = black >= 2
      }
      var first = 0.0
      for column in 0..<columns {
        var hits = 0
        for offset in 0..<8 where column + offset < columns { if inked[column + offset] { hits += 1 } }
        if inked[column] && hits >= 4 {
          first = Double(column)
          break
        }
      }
      var last = Double(columns - 1)
      for column in stride(from: columns - 1, through: 0, by: -1) {
        var hits = 0
        for offset in 0..<8 where column - offset >= 0 { if inked[column - offset] { hits += 1 } }
        if inked[column] && hits >= 4 {
          last = Double(column)
          break
        }
      }
      // Dark runs separated by more than about half a character are words.
      var blobs: [Double] = []
      var empty = 99
      for column in 0..<columns {
        if dark[column] {
          if empty > 5 { blobs.append(Double(column)) }
          empty = 0
        } else {
          empty += 1
        }
      }
      measured.append(
        Measured(
          pageNumber: pageNumber, printedRow: (entry["printed_row"] as? Int ?? 1) - 1, rowId: rowId,
          characters: Array(text), firstWord: text.split(separator: " ").first.map { $0.count } ?? 0,
          origin: x0, midY: (y0 + y1) / 2, band: y1 - y0, radians: radians, first: first, last: last,
          blobs: blobs))
    }

    // The face is monospaced: one pitch per page, taken as the median.
    var pagePitch: [Int: Double] = [:]
    for number in Assets.bodyPages {
      let pitches = measured.filter { $0.pageNumber == number && $0.characters.count > 20 }
        .map { $0.spanPitch }.sorted()
      pagePitch[number] = pitches.isEmpty ? 12 : pitches[pitches.count / 2]
    }

    // Pass 2: place the characters.
    let glyphFont = particleFont
    var order = 0
    var fragments = 0
    for row in measured {
      guard let scan = analysis[row.pageNumber] else { continue }
      let pitch = pagePitch[row.pageNumber] ?? 12
      rows.append(
        PrintedRow(
          page: row.pageNumber - 75, row: row.printedRow, text: String(row.characters),
          firstWordLength: row.firstWord))
      // Column of each word's first character.
      var wordStarts: [Int] = []
      for (col, character) in row.characters.enumerated()
      where character != " " && (col == 0 || row.characters[col - 1] == " ") {
        wordStarts.append(col)
      }
      // Trust the word match only when it also lands the last word on the
      // line's measured right edge.
      var byWord = row.blobs.count == wordStarts.count && !wordStarts.isEmpty
      if byWord, let lastStart = wordStarts.last, let lastBlob = row.blobs.last {
        let end = lastBlob + (Double(row.characters.count - lastStart) - 0.35) * pitch
        if abs(end - row.last) > 1.6 * pitch { byWord = false }
      }
      let linear = abs(row.spanPitch / pitch - 1) < 0.05 ? row.spanPitch : pitch
      func centre(_ col: Int) -> Double {
        if byWord, let word = wordStarts.lastIndex(where: { $0 <= col }) {
          return row.origin + row.blobs[word] + (Double(col - wordStarts[word]) + 0.325) * pitch
        }
        return row.origin + row.first + (Double(col) + 0.325) * linear
      }
      let spans = numberSpans[row.rowId] ?? []
      var line: [Particle] = []
      for (col, character) in row.characters.enumerated() {
        if character == " " { continue }
        let x = centre(col)
        var orange = 0, black = 0
        // The cell's edges show the paper or highlighter between the strokes.
        for fx in [-0.45, -0.25, 0.0, 0.25, 0.45] {
          for fy in [-0.4, 0.0, 0.4] {
            let (r, g, b) = pixel(scan, row.radians, x + fx * pitch, row.midY + fy * row.band)
            if r > 185 && g > 90 && g < 205 && b < 135 && r - b > 80 { orange += 1 }
            if (r * 3 + g * 6 + b) / 10 < 85 { black += 1 }
          }
        }
        var particle = Particle()
        var unichars = Array(String(character).utf16)
        var glyphs = [CGGlyph](repeating: 0, count: unichars.count)
        CTFontGetGlyphsForCharacters(glyphFont, &unichars, &glyphs, unichars.count)
        particle.glyph = glyphs[0]
        if particle.glyph == 0 {
          // Not in the mono face (for example a long dash): use a hyphen.
          var dash: [UniChar] = [45]
          CTFontGetGlyphsForCharacters(glyphFont, &dash, &glyphs, 1)
          particle.glyph = glyphs[0]
        }
        let (sx, sy) = locate(scan, row.radians, x, row.midY)
        particle.page = row.pageNumber - 75
        particle.row = row.printedRow
        particle.col = col
        particle.order = order
        particle.u = sx / Double(scan.w)
        particle.v = sy / Double(scan.h)
        particle.pitch = pitch / Double(scan.w)
        particle.isHighlighted = orange >= 4
        particle.isBar = black >= 10
        particle.isFirstWord = col < row.firstWord
        if let span = spans.first(where: { col >= $0.start && col < $0.end }) {
          particle.numberToken = span.token
          particle.numberIndex = col - span.start
        }
        particle.s1 = hash01(order, 11)
        particle.s2 = hash01(order, 23)
        particle.s3 = hash01(order, 37)
        particle.s4 = hash01(order, 51)
        line.append(particle)
        order += 1
      }
      // A heavy glyph can hide the highlighter under it: close one- and
      // two-character gaps inside a highlighted run.
      if line.count > 3 {
        for index in 1..<(line.count - 1) where !line[index].isHighlighted {
          let before = line[index - 1].isHighlighted
          let after = line[index + 1].isHighlighted
          let afterNext = index + 2 < line.count && line[index + 2].isHighlighted
          if before && (after || afterNext) { line[index].isHighlighted = true }
        }
      }
      if row.pageNumber == 75 {
        // Highlighted runs on the featured page; a run continues across a space.
        var fragmentId = -1
        var fragmentStart = 0
        var previous = -9
        for index in line.indices where line[index].isHighlighted {
          let col = line[index].col
          if fragmentId < 0 || col - previous > 2 {
            fragmentId = fragments
            fragments += 1
            fragmentStart = col
          }
          line[index].fragment = fragmentId
          line[index].fragmentIndex = col - fragmentStart
          previous = col
        }
      }
      particles.append(contentsOf: line)
    }
    fragmentCount = fragments
    if particles.count < 1000 { fail("The transcript did not load as expected.") }
  }
}
