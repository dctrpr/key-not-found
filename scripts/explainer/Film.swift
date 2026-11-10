// The film: every frame is drawn from the time alone.
//
// One idea carries it. The article's own printed characters are the cast: they
// flock, land on the scans they came from, lift off again and are re-read by
// each recorded method. Nothing here is a real key, seed or address.
import CoreGraphics
import CoreText
import Foundation

/// Scene boundaries in seconds. The score and captions use the same values.
enum Cue {
  static let key = 2.3
  static let pour = 3.45
  static let claim = 8.0
  static let push = 11.6
  static let lift = 15.8
  static let lines = 18.0
  static let firstWords = 22.2
  static let mirror = 25.5
  static let highlights = 30.3
  static let numbers = 34.3
  static let tally = 38.0
  static let open = 42.2
  static let funding = 48.2
  static let end = 56.0
}

/// When each of the 15 recorded methods is marked on the tally, in ledger order.
/// Tones follow the public ledger: tested with no result in its declared scope,
/// a corrected claim, a partial lead, or an open question.
let tallyPlan: [(id: String, tone: StampTone, at: Double)] = [
  ("raw-bip39", .tested, Cue.tally + 1.00),
  ("highlight-bip39", .tested, Cue.highlights + 3.05),
  ("physical-registration", .open, Cue.tally + 1.64),
  ("phrase-box-bug", .corrected, Cue.mirror + 3.45),
  ("typography", .open, Cue.tally + 1.80),
  ("corrected-orange", .tested, Cue.mirror + 2.05),
  ("corrected-inverted", .tested, Cue.tally + 1.32),
  ("faithful-lines", .tested, Cue.lines + 3.15),
  ("highlight-lines", .tested, Cue.highlights + 2.55),
  ("literal-ascii", .tested, Cue.tally + 1.16),
  ("firstword-sha256", .tested, Cue.firstWords + 2.35),
  ("numeric-256", .tested, Cue.numbers + 2.85),
  ("issue27", .tested, Cue.tally + 1.48),
  ("creator-sources", .open, Cue.tally + 1.96),
  ("author-manuscript", .question, Cue.tally + 2.12),
]

struct Dot {
  var x = 0.0
  var y = 0.0
  var size = 12.0
  var alpha = 1.0
  var color = Ink.paper
  var mirror = 1.0
  var highlight = 0.0  // orange highlighter behind the glyph
}

final class Film {
  let assets: Assets
  var debugAlignment = false

  private var flockBase: [P2] = []
  private var keyTarget: [P2] = []
  private var titleTarget: [P2] = []
  private var tokenOrigin: [P2] = []  // where each selected number sits in the panel
  private let particleCount: Int

  // Act two layout: the typeset block on the left, the reading on the right.
  private let blockX = 110.0, blockY = 132.0, advance = 12.6, pitchY = 27.4, blockSize = 21.0
  private let panelX = 1040.0
  private let titleSize: CGFloat = 290
  private let titleX = 88.0, titleY1 = 420.0, titleY2 = 664.0

  init(assets: Assets) {
    self.assets = assets
    particleCount = assets.particles.count
    prepareFormations()
  }

  // MARK: Formations

  private func prepareFormations() {
    let particles = assets.particles
    flockBase = particles.map { p in
      // Two Gaussian coordinates from the particle's seeds.
      let radius = sqrt(-2 * log(max(p.s1, 1e-9)))
      return P2(x: radius * cos(2 * .pi * p.s2), y: radius * sin(2 * .pi * p.s2))
    }

    // A key, drawn once into a mask and filled with the article's characters.
    let key = sampleMask(count: particleCount, seed: 7) { canvas in
      let ctx = canvas.ctx
      ctx.saveGState()
      ctx.translateBy(x: 800, y: 430)
      ctx.rotate(by: -0.2)
      ctx.setFillColor(cg(Ink.paper))
      ctx.addEllipse(in: CGRect(x: -205, y: -205, width: 410, height: 410))
      ctx.addEllipse(in: CGRect(x: -108, y: -108, width: 216, height: 216))
      ctx.fillPath(using: .evenOdd)
      ctx.fill(CGRect(x: 190, y: -36, width: 760, height: 72))
      ctx.fill(CGRect(x: 205, y: -58, width: 34, height: 116))
      ctx.fill(CGRect(x: 690, y: 36, width: 62, height: 128))
      ctx.fill(CGRect(x: 790, y: 36, width: 50, height: 92))
      ctx.fill(CGRect(x: 878, y: 36, width: 72, height: 150))
      ctx.restoreGState()
    }
    // Send each character to the nearest part of the key, left to right, so
    // the flock folds into the shape instead of crossing itself.
    let byFlock = (0..<particleCount).sorted { flockPoint($0, Cue.key).x < flockPoint($1, Cue.key).x }
    let keySorted = key.sorted { $0.x < $1.x }
    keyTarget = [P2](repeating: P2(x: 0, y: 0), count: particleCount)
    for (rank, index) in byFlock.enumerated() { keyTarget[index] = keySorted[rank] }

    // The title, filled in reading order: the article spells its own verdict.
    let title = sampleMask(count: particleCount, seed: 19) { canvas in
      self.drawTitle(canvas, color: Ink.paper, alpha: 1)
    }
    let split = (titleY1 + 24)
    let ordered = title.sorted { a, b in
      let lineA = a.y > split ? 1 : 0, lineB = b.y > split ? 1 : 0
      return lineA != lineB ? lineA < lineB : a.x < b.x
    }
    titleTarget = [P2](repeating: P2(x: 0, y: 0), count: particleCount)
    for particle in particles { titleTarget[particle.order] = ordered[particle.order] }

    // The selected printed numbers, laid out as a wrapped row in the panel.
    var x = 0.0, y = 0.0
    let step = 16.8
    for token in assets.numberTokens {
      let width = Double(token.count) * step
      if x + width > 770 {
        x = 0
        y += 46
      }
      tokenOrigin.append(P2(x: panelX + x, y: 512 + y))
      x += width + step * 1.5
    }
  }

  /// Uniform points inside whatever `draw` paints, at full-frame coordinates.
  private func sampleMask(count: Int, seed: Int, draw: (Canvas) -> Void) -> [P2] {
    let mw = Int(W) / 2, mh = Int(H) / 2
    var bytes = [UInt8](repeating: 0, count: mw * mh)
    bytes.withUnsafeMutableBytes { buffer in
      let context = CGContext(
        data: buffer.baseAddress, width: mw, height: mh, bitsPerComponent: 8, bytesPerRow: mw,
        space: CGColorSpaceCreateDeviceGray(), bitmapInfo: CGImageAlphaInfo.none.rawValue)!
      draw(Canvas(context))
    }
    var points: [P2] = []
    points.reserveCapacity(count)
    var attempt = 0
    while points.count < count && attempt < count * 4000 {
      let x = hash01(attempt, seed) * Double(W), y = hash01(attempt, seed + 1) * Double(H)
      attempt += 1
      if bytes[min(mh - 1, Int(y / 2)) * mw + min(mw - 1, Int(x / 2))] > 127 {
        points.append(P2(x: x, y: y))
      }
    }
    while points.count < count { points.append(P2(x: Double(W) / 2, y: Double(H) / 2)) }
    return points
  }

  /// The murmuration: one cloud, folded by a few slow waves.
  private func flockPoint(_ index: Int, _ t: Double) -> P2 {
    let u = flockBase[index]
    let wx = u.x + 0.55 * sin(1.7 * u.y + 1.9 * t + 0.4) + 0.24 * sin(3.1 * u.x + 2.3 * u.y + 2.7 * t)
    let wy = u.y + 0.55 * sin(1.3 * u.x - 1.4 * t + 2.1) + 0.24 * cos(2.7 * u.x - 3.3 * u.y - 2.1 * t)
    let angle = 0.5 * sin(0.7 * t + 0.3)
    let scale = 300 * (1 + 0.22 * sin(1.25 * t + 1.0))
    let rx = wx * cos(angle) - wy * sin(angle), ry = wx * sin(angle) + wy * cos(angle)
    let cx = 1010 + 470 * sin(0.62 * t + 0.2), cy = 400 + 120 * sin(1.02 * t + 1.3)
    return P2(x: cx + rx * scale, y: cy + ry * scale * 0.58)
  }

  /// A slow river of characters along the bottom of the frame.
  private func riverPoint(_ p: Particle, _ t: Double) -> P2 {
    let span = Double(W) + 300
    var x = (p.s1 * span + (16 + 26 * p.s3) * (t - Cue.tally)).truncatingRemainder(dividingBy: span)
    if x < 0 { x += span }
    x -= 150
    let lower = 150 * seg(t, Cue.funding - 0.4, Cue.funding + 0.6) * (1 - seg(t, Cue.end - 0.4, Cue.end + 0.2))
    let centre = 952 + lower + 44 * sin(x * 0.0042 + t * 0.45)
    let spread = 118 * (0.62 + 0.38 * sin(x * 0.007 + 1.3 + t * 0.2))
    return P2(x: x, y: centre + (p.s2 - 0.5) * spread)
  }

  private func blockPoint(_ p: Particle) -> P2 {
    P2(x: blockX + Double(p.col) * advance, y: blockY + Double(p.row) * pitchY)
  }

  private func ambientPoint(_ p: Particle, _ t: Double) -> P2 {
    P2(
      x: p.s1 * Double(W) + 16 * sin(0.31 * t + 6.28 * p.s3),
      y: p.s2 * Double(H) + 12 * cos(0.27 * t + 6.28 * p.s4))
  }

  // MARK: Page layout

  /// Wide shot: all eight source pages in a row.
  func wideBox(_ slot: Int) -> Box {
    let w = 196.0, h = w * 3264 / 2544, gap = 26.0
    let x0 = (Double(W) - (8 * w + 7 * gap)) / 2
    return Box(x: x0 + Double(slot) * (w + gap), y: 136, w: w, h: h)
  }

  /// Close-up on printed page 75.
  var closeBox: Box { Box(x: 800, y: -60, w: 1060, h: 1060 * 3264 / 2544) }

  /// When the characters of a body page begin to land on it.
  private func pourStart(_ page: Int) -> Double { Cue.pour + 0.34 * Double(page) }

  private func home(_ p: Particle, _ box: Box) -> P2 {
    P2(x: box.x + p.u * box.w, y: box.y + p.v * box.h)
  }

  // MARK: Characters

  /// Where a character is, how large and what colour, at time `t`.
  private func dot(_ index: Int, _ t: Double, paperBand: Box?) -> Dot? {
    let p = assets.particles[index]
    var d = Dot()

    if t < Cue.pour + 3.9 {
      // Flock, then a key, then down onto the pages.
      var position = flockPoint(index, t)
      d.size = 9 + 8 * p.s3
      d.alpha = 0.5 + 0.5 * p.s3
      let fold = easeInOut(seg(t, Cue.key + 0.3 * p.s1, Cue.key + 0.62 + 0.3 * p.s1))
      if fold > 0 {
        let wobble = P2(x: 3 * sin(5 * t + 40 * p.s2), y: 3 * cos(4.3 * t + 40 * p.s4))
        position = position.mix(keyTarget[index] + wobble, fold)
        d.size = lerp(d.size, 10.5, fold)
        d.alpha = lerp(d.alpha, 0.96, fold)
      }
      let start = pourStart(p.page) + 0.95 * (Double(p.row) / 32) + 0.25 * p.s2
      let pour = seg(t, start, start + 1.05)
      if pour > 0 {
        let box = wideBox(p.page + 2)
        let eased = easeInOut(pour)
        var landing = position.mix(home(p, box), eased)
        landing.y -= sin(pour * .pi) * (50 + 110 * p.s3)
        landing.x += sin(pour * .pi) * (p.s4 - 0.5) * 150
        position = landing
        d.size = lerp(d.size, p.pitch * box.w / 0.6, eased)
        d.color = Ink.paper.mix(Ink.ink, seg(pour, 0.72, 0.94))
        d.alpha *= 1 - seg(pour, 0.86, 1.0)
      }
      d.x = position.x
      d.y = position.y
      return d.alpha > 0.01 ? d : nil
    }
    if t < Cue.lift { return nil }  // the scans carry the text

    if t < Cue.tally + 1.4 {
      var position: P2
      if p.page == 0 {
        // Printed page 75: off the scan and into the typeset block.
        let origin = home(p, closeBox)
        let start = Cue.lift + 0.2 + 0.55 * (Double(p.row) / 32) + 0.25 * p.s2
        let move = seg(t, start, start + 1.15)
        let eased = easeInOut(move)
        position = origin.mix(blockPoint(p), eased)
        position.y -= sin(move * .pi) * (70 + 110 * p.s3)
        position.x -= sin(move * .pi) * (90 + 190 * p.s4)
        d.size = lerp(p.pitch * closeBox.w / 0.6, blockSize, eased)
        d.color = Ink.ink.mix(Ink.paper, seg(move, 0.04, 0.3))
        d.alpha = seg(t, Cue.lift, Cue.lift + 0.22)
        if p.isBar { d.color = Ink.sheet.mix(Ink.paper, seg(move, 0.04, 0.3)) }
        if t >= Cue.lines { readings(p, t, &position, &d) }
      } else {
        // The other body pages wait as dust until they are needed.
        position = ambientPoint(p, t)
        d.size = 9 + 5 * p.s3
        d.alpha = 0.07 * seg(t, Cue.lift + 0.5, Cue.lift + 1.8)
        if t >= Cue.numbers {
          let origin = position
          numberReading(p, t, &position, &d, from: origin)
        }
      }
      // Into the river for the count.
      let leave = seg(t, Cue.tally + 0.35 * p.s1, Cue.tally + 0.95 + 0.35 * p.s1)
      if leave > 0 {
        let eased = easeInOut(leave)
        position = position.mix(riverPoint(p, t), eased)
        d.size = lerp(d.size, 10 + 5 * p.s4, eased)
        d.alpha = lerp(d.alpha, 0.62, eased)
        d.color = d.color.mix(Ink.paper, eased)
        d.highlight *= 1 - eased
        d.mirror = lerp(d.mirror, 1, eased)
      }
      d.x = position.x
      d.y = position.y
      return d.alpha > 0.01 ? d : nil
    }

    // River, then the title.
    var position = riverPoint(p, t)
    d.size = 10 + 5 * p.s4
    d.alpha = 0.62 * (1 - seg(t, Cue.funding - 0.3, Cue.funding + 0.4))
      + 0.5 * seg(t, Cue.end - 0.55, Cue.end - 0.05)
    d.color = Ink.paper
    let start = Cue.end - 0.1 + 1.25 * (Double(p.order) / Double(particleCount)) + 0.2 * p.s2
    let gather = seg(t, start, start + 0.95)
    if gather > 0 {
      let eased = easeInOut(gather)
      var landing = position.mix(titleTarget[index], eased)
      landing.y -= sin(gather * .pi) * (40 + 90 * p.s3)
      position = landing
      d.size = lerp(d.size, 9, eased)
      d.alpha = lerp(d.alpha, 0.95, eased) * (1 - seg(t, Cue.end + 3.0, Cue.end + 3.7))
    }
    if let band = paperBand, band.contains(position) { d.color = Ink.ink }
    d.x = position.x
    d.y = position.y
    return d.alpha > 0.01 ? d : nil
  }

  /// The five readings shown on the typeset block of printed page 75.
  private func readings(_ p: Particle, _ t: Double, _ position: inout P2, _ d: inout Dot) {
    if t < Cue.firstWords {
      // Every other printed line.
      let tau = t - Cue.lines
      let shift = easeInOut(seg(tau, 0.25, 0.85)) * (1 - easeInOut(seg(tau, 3.4, 4.0)))
      let close = easeInOut(seg(tau, 1.25, 2.05)) * (1 - easeInOut(seg(tau, 3.25, 3.85)))
      if p.row % 2 == 1 {
        position.x += 40 * shift
        position.y = lerp(position.y, blockY + (Double(p.row / 2) + 8) * pitchY, close)
        d.color = Ink.paper.mix(Ink.lime, shift)
      } else {
        d.alpha *= lerp(1, 0.42, shift) * (1 - close)
      }
    } else if t < Cue.mirror {
      // The first word of every line.
      let tau = t - Cue.firstWords
      let on = easeInOut(seg(tau, 0.15, 0.6)) * (1 - easeInOut(seg(tau, 2.7, 3.2)))
      if p.isFirstWord {
        d.color = Ink.paper.mix(Ink.lime, on)
        position.x -= 14 * on
      } else {
        d.alpha *= lerp(1, 0.2, on)
      }
    } else if t < Cue.highlights {
      // Mirror writing: the block turns over.
      let tau = t - Cue.mirror
      let flip = easeInOut(seg(tau, 0.15, 1.15)) - easeInOut(seg(tau, 3.85, 4.7))
      let turn = cos(.pi * flip)
      let centre = blockX + 34 * advance
      position.x = centre + (position.x - centre) * turn
      d.mirror = turn
      d.alpha *= 0.5 + 0.5 * abs(turn)
    } else if t < Cue.numbers {
      // The magazine's own orange highlights.
      let tau = t - Cue.highlights
      let on = easeInOut(seg(tau, 0.15, 0.65)) * (1 - easeInOut(seg(tau, 3.3, 3.85)))
      if p.isHighlighted {
        d.highlight = on
        d.color = Ink.paper.mix(Ink.ink, on)
        if p.fragment >= 0 && p.fragment < 9 {
          let out = easeInOut(seg(tau, 0.95 + 0.04 * Double(p.fragment), 1.75 + 0.04 * Double(p.fragment)))
            * (1 - easeInOut(seg(tau, 3.1, 3.7)))
          let slot = P2(
            x: panelX + Double(p.fragmentIndex) * advance, y: 490 + Double(p.fragment) * 26)
          position = position.mix(slot, out)
        }
      } else {
        d.alpha *= lerp(1, 0.18, on)
      }
    } else {
      let origin = position
      numberReading(p, t, &position, &d, from: origin)
    }
  }

  /// The printed numbers leave the text and line up in the panel.
  private func numberReading(
    _ p: Particle, _ t: Double, _ position: inout P2, _ d: inout Dot, from: P2
  ) {
    let tau = t - Cue.numbers
    let on = easeInOut(seg(tau, 0.1, 0.5)) * (1 - easeInOut(seg(tau, 3.15, 3.6)))
    guard p.numberToken >= 0, p.numberToken < tokenOrigin.count else {
      if p.page == 0 { d.alpha *= lerp(1, 0.26, on) }
      return
    }
    let delay = 0.022 * Double(p.numberToken)
    let fly = easeInOut(seg(tau, 0.55 + delay, 1.4 + delay)) * (1 - easeInOut(seg(tau, 3.0, 3.5)))
    let origin = tokenOrigin[p.numberToken]
    let slot = P2(x: origin.x + Double(p.numberIndex) * 16.8 + 8, y: origin.y)
    var path = from.mix(slot, fly)
    path.y -= sin(fly * .pi) * 60
    position = path
    d.color = d.color.mix(Ink.lime, on)
    d.size = lerp(d.size, 28, fly)
    d.alpha = lerp(d.alpha, 1, max(on, fly))
  }

  private func drawCharacters(_ canvas: Canvas, _ t: Double, paperBand: Box?) {
    let ctx = canvas.ctx
    let font = assets.particleFont
    let base = Double(Assets.particleFontSize)
    for index in 0..<particleCount {
      guard let d = dot(index, t, paperBand: paperBand) else { continue }
      if d.x < -40 || d.x > Double(W) + 40 || d.y < -40 || d.y > Double(H) + 40 { continue }
      if d.highlight > 0.01 {
        let w = d.size * 0.6 + 0.8, h = d.size * 1.18
        ctx.setFillColor(cg(Ink.orange, d.highlight * min(1, d.alpha * 1.4)))
        ctx.fill(CGRect(x: d.x - w / 2, y: d.y - h / 2, width: w, height: h))
      }
      ctx.setFillColor(cg(d.color, d.alpha))
      canvas.glyph(
        assets.particles[index].glyph, font: font, x: d.x, y: d.y, scale: d.size / base,
        mirror: d.mirror)
    }
  }

  // MARK: Shared lettering

  private func sans(_ size: CGFloat, _ color: RGB, weight: CGFloat = 650) -> Style {
    Style(font: assets.fonts.sans(size, weight), color: color, tracking: -0.04)
  }

  private func mono(_ size: CGFloat, _ color: RGB) -> Style {
    Style(font: assets.fonts.mono(size), color: color, tracking: 0.06)
  }

  private func drawTitle(_ canvas: Canvas, color: RGB, alpha: Double) {
    let style = Style(font: assets.fonts.sans(titleSize, 650), color: color, tracking: -0.075)
    canvas.text("KEY NOT", style, x: titleX, y: titleY1, alpha: alpha)
    canvas.text("FOUND.", style, x: titleX, y: titleY2, alpha: alpha)
  }

  /// Greedy line breaks for the few paragraphs in the film.
  private func wrap(_ string: String, _ style: Style, _ maxWidth: Double, on canvas: Canvas) -> [String] {
    var lines: [String] = []
    var current = ""
    for word in string.split(separator: " ").map(String.init) {
      let candidate = current.isEmpty ? word : current + " " + word
      if canvas.width(candidate, style) > maxWidth, !current.isEmpty {
        lines.append(current)
        current = word
      } else {
        current = candidate
      }
    }
    if !current.isEmpty { lines.append(current) }
    return lines
  }

  private func topline(_ canvas: Canvas, _ alpha: Double, onInk: Bool, right: String = "") {
    guard alpha > 0.003 else { return }
    let color = onInk ? Ink.paper : Ink.ink
    canvas.fill(Box(x: 96, y: 66, w: 16, h: 16), Ink.lime, alpha)
    canvas.stroke(Box(x: 96, y: 66, w: 16, h: 16), color, alpha, width: 2)
    canvas.text("CASE FILE 001 · UNSOLVED", mono(21, color), x: 126, y: 82, alpha: alpha * 0.92)
    if !right.isEmpty {
      canvas.text(right, mono(21, onInk ? Ink.dim : Ink.muted), x: Double(W) - 96, y: 82, align: .right, alpha: alpha)
    }
  }

  /// A soft darkening toward the corners of the ink stage.
  private func vignette(_ canvas: Canvas) {
    let colors = [cg(Ink.ink, 0), cg(RGB(0x000000), 0.55)] as CFArray
    guard let gradient = CGGradient(colorsSpace: sRGB, colors: colors, locations: [0.55, 1]) else { return }
    canvas.ctx.drawRadialGradient(
      gradient, startCenter: CGPoint(x: W / 2, y: H / 2), startRadius: 0,
      endCenter: CGPoint(x: W / 2, y: H / 2), endRadius: 1180, options: [.drawsAfterEndLocation])
  }

  /// Ink rising from the bottom so lettering reads over moving characters.
  private func ground(_ canvas: Canvas, from top: Double, alpha: Double) {
    guard alpha > 0.003 else { return }
    let colors = [cg(Ink.ink, 0), cg(Ink.ink, 0.9 * alpha)] as CFArray
    guard let gradient = CGGradient(colorsSpace: sRGB, colors: colors, locations: [0, 0.55]) else { return }
    canvas.ctx.drawLinearGradient(
      gradient, start: CGPoint(x: 0, y: top), end: CGPoint(x: 0, y: Double(H)),
      options: [.drawsAfterEndLocation])
  }

  // MARK: Frame

  func render(time t: Double, on canvas: Canvas) {
    let full = Box(x: 0, y: 0, w: Double(W), h: Double(H))
    if debugAlignment {
      renderAlignment(canvas)
      return
    }
    // Lights on: the stage turns from ink to newsprint when the work goes public.
    let lit = easeInOut(seg(t, Cue.open, Cue.open + 0.55))
    let band = Box(x: 0, y: 508 - 600 * lit, w: Double(W), h: 1200 * lit)
    canvas.fill(full, Ink.ink)

    if t < Cue.open + 0.6 {
      if t < Cue.lift + 1.3 { drawPages(canvas, t) }
      drawCharacters(canvas, t, paperBand: nil)
      vignette(canvas)
      if t < Cue.push + 0.3 {
        topline(
          canvas, 1 - seg(t, Cue.push - 0.1, Cue.push + 0.3), onInk: true,
          right: t > Cue.pour + 0.6 ? "BITCOIN MAGAZINE · ISSUE 24 · 8 SOURCE PAGES" : "")
      }
      if t < Cue.claim + 0.4 { sceneOpening(canvas, t) }
      if t >= Cue.claim - 0.1 && t < Cue.push + 0.5 { sceneClaim(canvas, t) }
      if t >= Cue.push && t < Cue.lift + 0.4 { sceneFound(canvas, t) }
      if t >= Cue.lift + 0.9 && t < Cue.tally + 0.5 { sceneReadings(canvas, t) }
      if t >= Cue.tally { sceneTally(canvas, t) }
    }
    if lit > 0 {
      canvas.fill(band, Ink.paper)
      canvas.clipped(band) {
        self.drawCharacters(canvas, t, paperBand: band)
        if t < Cue.funding + 0.4 { self.scenePublic(canvas, t) }
        if t >= Cue.funding - 0.05 && t < Cue.end + 0.4 { self.sceneFunding(canvas, t) }
        if t >= Cue.end - 0.2 { self.sceneEnd(canvas, t) }
      }
    }
  }

  // MARK: Pages

  private func drawPages(_ canvas: Canvas, _ t: Double) {
    guard t >= Cue.pour - 0.15 else { return }
    for pass in 0..<2 {
      for slot in 0..<8 {
        let number = 73 + slot
        if (number == 75) != (pass == 1) { continue }
        var box = wideBox(slot)
        var alpha = 1.0
        let pop = easeOutBack(seg(t, Cue.pour - 0.1 + 0.06 * Double(slot), Cue.pour + 0.34 + 0.06 * Double(slot)))
        if pop <= 0.001 { continue }
        let cx = box.x + box.w / 2, cy = box.y + box.h / 2
        box = Box(x: cx - box.w * pop / 2, y: cy - box.h * pop / 2, w: box.w * pop, h: box.h * pop)
        var bleach = 0.0
        if t >= Cue.push {
          if number == 75 {
            box = wideBox(slot).mix(closeBox, easeInOut(seg(t, Cue.push + 0.1, Cue.push + 1.7)))
            bleach = seg(t, Cue.lift, Cue.lift + 0.55)
            alpha = 1 - seg(t, Cue.lift + 0.5, Cue.lift + 1.15)
          } else {
            let away = seg(t, Cue.push, Cue.push + 0.7)
            alpha = 1 - away
            box.y -= 46 * easeIn(away)
          }
        }
        if alpha <= 0.003 { continue }
        let depth = lerp(8, 16, seg(box.w, 196, 1060))
        canvas.fill(Box(x: box.x + depth, y: box.y + depth, w: box.w, h: box.h), Ink.inkLine, alpha * 0.9)
        canvas.fill(box, Ink.sheet, alpha)
        // The print appears as its characters land.
        let page = number - 75
        let started = (0...4).contains(page) ? pourStart(page) + 0.5 : Cue.pour + 0.25 + 0.24 * Double(slot)
        let reveal = seg(t, started, started + 1.95)
        if reveal > 0 {
          canvas.clipped(Box(x: box.x, y: box.y, w: box.w, h: box.h * reveal)) {
            canvas.image(self.assets.page(number, height: box.h), in: box, alpha: alpha)
          }
        }
        if bleach > 0 { canvas.fill(box, Ink.sheet, bleach * 0.95 * alpha) }
        canvas.stroke(box, Ink.paper, alpha * 0.5, width: 1.5)
        let wide = 1 - seg(t, Cue.push, Cue.push + 0.4)
        canvas.text(
          String(number), mono(18, Ink.dim), x: box.x + box.w / 2, y: box.y + box.h + 34,
          align: .center, alpha: wide * seg(reveal, 0.2, 0.6))
      }
    }
  }

  // MARK: Scenes

  /// 0.0–8.0: the flock, the key, and the pages it came from.
  private func sceneOpening(_ canvas: Canvas, _ t: Double) {
    // The hook.
    let hook = 1 - seg(t, Cue.pour + 0.25, Cue.pour + 0.7)
    if hook > 0 {
      ground(canvas, from: 700, alpha: hook * seg(t, 0.2, 0.7))
      let style = sans(70, Ink.paper)
      canvas.text(
        "6,162 NON-SPACE CHARACTERS · 142 BODY LINES · PRINTED PAGES 75–79", mono(20, Ink.dim),
        x: 98, y: 800, alpha: hook * seg(t, 0.9, 1.4))
      canvas.reveal("Somewhere in these 6,162 printed characters", style, x: 96, y: 880, t: t - 0.45, alpha: hook)
      let lead = "there might be a "
      let leadWidth = canvas.width(lead, style) + style.tracking * 70
      let marked = "Bitcoin private key."
      let mark = easeOut(seg(t, 2.25, 2.7))
      canvas.marker(
        Box(x: 96 + leadWidth - 10, y: 916, w: (canvas.width(marked, style) + 22) * mark, h: 78),
        Ink.lime, hook)
      canvas.reveal(lead, style, x: 96, y: 972, t: t - 1.35, alpha: hook)
      canvas.reveal(
        marked, sans(70, Ink.paper.mix(Ink.ink, mark)), x: 96 + leadWidth, y: 972, t: t - 1.62,
        alpha: hook)
    }
    // What was said, and by whom. Orange marks source material.
    let said = window(t, Cue.pour + 0.9, Cue.claim + 0.25, 0.3)
    if said > 0 {
      let local = t - (Cue.pour + 0.9)
      canvas.fill(Box(x: 96, y: 598, w: 7, h: 208 * easeOut(seg(local, 0, 0.5))), Ink.orange, said)
      canvas.text("MAX KEISER · PUBLIC POST · 4 MARCH 2023", mono(21, Ink.orange), x: 130, y: 620, alpha: said * seg(local, 0.1, 0.5))
      let style = sans(70, Ink.paper)
      canvas.reveal("In 2023 he said he hid a Bitcoin private key", style, x: 130, y: 712, t: local - 0.3, alpha: said)
      canvas.reveal("in this magazine article.", style, x: 130, y: 796, t: local - 0.95, alpha: said)
    }
  }

  /// 8.0–11.6: the claim, and what is not known about it.
  private func sceneClaim(_ canvas: Canvas, _ t: Double) {
    let local = t - Cue.claim
    let alpha = window(t, Cue.claim, Cue.push + 0.35, 0.3)
    canvas.text("THE CLAIM", mono(22, Ink.dim), x: 100, y: 548, alpha: alpha * seg(local, 0.1, 0.4))
    let land = easeOutBack(seg(local, 0.15, 0.6))
    let big = Style(font: assets.fonts.sans(CGFloat(330 * max(land, 0.01)), 650), color: Ink.paper, tracking: -0.07)
    let width = canvas.text("20 BTC", big, x: 88, y: 850, alpha: alpha * seg(local, 0.15, 0.4))
    canvas.text(
      "claimed by Max Keiser. Not independently verified.", sans(40, Ink.dim, weight: 500),
      x: 100, y: 930, alpha: alpha * seg(local, 0.9, 1.3))
    canvas.stamp(
      "PRIZE UNVERIFIED", tone: .open, font: assets.fonts.mono(46), x: 96 + width + 70, y: 610,
      t: local - 1.35, onInk: true, angle: -0.07, alpha: alpha)
    let note = alpha * seg(local, 1.9, 2.3)
    canvas.text("No authenticated", sans(46, Ink.paper, weight: 560), x: 96 + width + 76, y: 770, alpha: note)
    canvas.text("prize address is known.", sans(46, Ink.paper, weight: 560), x: 96 + width + 76, y: 828, alpha: note)
  }

  /// 11.6–15.8: one solver, since 2023.
  private func sceneFound(_ canvas: Canvas, _ t: Double) {
    let local = t - Cue.push
    let alpha = window(t, Cue.push + 0.3, Cue.lift + 0.3, 0.3)
    canvas.fill(Box(x: 96, y: 262, w: 16, h: 16), Ink.lime, alpha * seg(local, 0.5, 0.8))
    canvas.text("ONE SOLVER · A SIDE PROJECT", mono(21, Ink.paper), x: 126, y: 278, alpha: alpha * seg(local, 0.5, 0.9))
    let style = sans(78, Ink.paper)
    canvas.reveal("I found this puzzle", style, x: 96, y: 410, t: local - 0.7, alpha: alpha)
    canvas.reveal("in 2023.", style, x: 96, y: 500, t: local - 1.0, alpha: alpha)
    canvas.reveal("I’ve been working", style, x: 96, y: 640, t: local - 1.9, alpha: alpha)
    canvas.reveal("on it ever since.", style, x: 96, y: 730, t: local - 2.2, alpha: alpha)
    canvas.text(
      "8 source pages · 142 body lines · 6,162 non-space characters", mono(20, Ink.dim), x: 96, y: 842,
      alpha: alpha * seg(local, 2.9, 3.3))
  }

  private struct Reading {
    let id: String
    let headline: [String]
    let facts: [String]
    let result: String
    let stampAt: Double
  }

  /// 18.0–38.0: five ways the text has been read, each with its recorded scope.
  private func sceneReadings(_ canvas: Canvas, _ t: Double) {
    let chrome = window(t, Cue.lift + 1.0, Cue.tally + 0.35, 0.5)
    canvas.text("PRINTED PAGE 75 · 32 LINES · EXACT LINE BREAKS", mono(19, Ink.dim), x: blockX, y: 88, alpha: chrome)
    drawTally(canvas, t, x: panelX, y: 962, cell: 30, gap: 9.6, alpha: chrome, onInk: true, label: true)

    let readings: [(start: Double, end: Double, reading: Reading)] = [
      (Cue.lines, Cue.firstWords,
        Reading(id: "faithful-lines", headline: ["Read every other", "printed line."],
          facts: ["142 printed lines", "parity, edge and reversal variants"],
          result: "No valid key in the recorded streams.", stampAt: 2.75)),
      (Cue.firstWords, Cue.mirror,
        Reading(id: "firstword-sha256", headline: ["Hash the first word", "of every line."],
          facts: ["36 first-word strings, one SHA-256 each", "180 addresses looked up"],
          result: "Zero transactions.", stampAt: 1.95)),
      (Cue.mirror, Cue.highlights,
        Reading(id: "corrected-orange", headline: ["Read it in a mirror.", "Fold the pages."],
          facts: ["20 page pairs", "80 reflected streams"],
          result: "No exact WIF or 64-hex output.", stampAt: 1.65)),
      (Cue.highlights, Cue.numbers,
        Reading(id: "highlight-lines", headline: ["Follow the orange", "highlights."],
          facts: ["46 highlighted fragments", "540 declared variants"],
          result: "One weak checksum hit. Zero transactions.", stampAt: 2.15)),
      (Cue.numbers, Cue.tally,
        Reading(id: "numeric-256", headline: ["Turn selected printed", "numbers into bits."],
          facts: ["24 selected numbers, 256 bits", "20 addresses looked up"],
          result: "Zero transaction activity.", stampAt: 2.45)),
    ]
    for (start, end, reading) in readings where t >= start - 0.05 && t < end + 0.3 {
      let local = t - start
      let alpha = window(t, start, end + 0.12, 0.22) * seg(t, Cue.lift + 1.2, Cue.lift + 1.7)
      canvas.fill(Box(x: panelX, y: 150, w: 14, h: 14), Ink.lime, alpha)
      canvas.text("METHOD · " + reading.id, mono(21, Ink.lime), x: panelX + 26, y: 164, alpha: alpha)
      let head = sans(70, Ink.paper)
      for (index, line) in reading.headline.enumerated() {
        canvas.reveal(line, head, x: panelX, y: 262 + Double(index) * 80, t: local - 0.12 - 0.22 * Double(index), alpha: alpha)
      }
      for (index, line) in reading.facts.enumerated() {
        canvas.text(line, mono(24, Ink.dim), x: panelX, y: 408 + Double(index) * 36, alpha: alpha * seg(local, 0.75 + 0.12 * Double(index), 1.1 + 0.12 * Double(index)))
      }
      canvas.text(reading.result, sans(40, Ink.paper, weight: 560), x: panelX, y: 792, alpha: alpha * seg(local, reading.stampAt - 0.4, reading.stampAt - 0.1))
      canvas.stamp(
        "TESTED · NO RESULT", tone: .tested, font: assets.fonts.mono(30), x: panelX, y: 824,
        t: local - reading.stampAt, onInk: true, alpha: alpha)
      if reading.id == "corrected-orange" { correctionNote(canvas, local, alpha) }
      if reading.id == "highlight-lines" {
        canvas.text("+ 350 highlight mnemonics · 1,050 addresses · no activity", mono(19, Ink.dim), x: panelX, y: 742, alpha: alpha * seg(local, 2.7, 3.0))
      }
      if reading.id == "numeric-256" { bitsBar(canvas, local, alpha) }
      if reading.id == "firstword-sha256" {
        let grow = easeOut(seg(local, 0.3, 0.9)) * (1 - seg(local, 2.7, 3.1))
        canvas.fill(Box(x: blockX - 34, y: blockY - 20, w: 5, h: (31 * pitchY + 26) * grow), Ink.lime, alpha)
      }
      if reading.id == "corrected-orange" {
        let on = seg(local, 0.1, 0.4) * (1 - seg(local, 4.2, 4.7))
        let centre = blockX + 34 * advance
        canvas.line(P2(x: centre, y: 96), P2(x: centre, y: 1004), Ink.lime, alpha * on * 0.9, width: 2)
        canvas.text("MIRROR", mono(17, Ink.lime), x: centre + 10, y: 1000, alpha: alpha * on)
      }
    }
  }

  /// A correction is part of the record: struck in red, never removed.
  private func correctionNote(_ canvas: Canvas, _ local: Double, _ alpha: Double) {
    let style = sans(38, Ink.paper, weight: 520)
    let show = alpha * seg(local, 2.25, 2.55)
    let first = "An earlier overlap graph"
    let second = "looked promising."
    canvas.text(first, style, x: panelX, y: 528, alpha: show)
    canvas.text(second, style, x: panelX, y: 576, alpha: show)
    let strike = easeOut(seg(local, 2.85, 3.2))
    if strike > 0 {
      canvas.line(P2(x: panelX - 6, y: 516), P2(x: panelX - 6 + (canvas.width(first, style) + 12) * strike, y: 512), Ink.redOnInk, alpha, width: 5)
      canvas.line(P2(x: panelX - 6, y: 564), P2(x: panelX - 6 + (canvas.width(second, style) + 12) * strike, y: 560), Ink.redOnInk, alpha, width: 5)
    }
    canvas.stamp(
      "CLAIM INVALIDATED · KEPT ON RECORD", tone: .corrected, font: assets.fonts.mono(24),
      x: panelX, y: 616, t: local - 3.3, onInk: true, angle: -0.035, alpha: alpha)
  }

  /// 256 marks, all alike: the count of bits, never their values.
  private func bitsBar(_ canvas: Canvas, _ local: Double, _ alpha: Double) {
    let show = alpha * seg(local, 1.45, 1.7)
    guard show > 0 else { return }
    let filled = Int(256 * easeInOut(seg(local, 1.6, 2.35)))
    for index in 0..<256 {
      let x = panelX + Double(index) * 3.0
      canvas.fill(Box(x: x, y: 672, w: 2, h: 34), index < filled ? Ink.lime : Ink.inkLine, show)
    }
    canvas.text("24 selected numbers", mono(19, Ink.dim), x: panelX, y: 660, alpha: show)
    canvas.text("256 bits", mono(19, Ink.lime), x: panelX + 768, y: 660, align: .right, alpha: show * seg(local, 2.2, 2.4))
  }

  private func tallyStates(_ t: Double) -> [(tone: StampTone, amount: Double)] {
    tallyPlan.map { ($0.tone, seg(t, $0.at, $0.at + 0.3)) }
  }

  private func drawTally(
    _ canvas: Canvas, _ t: Double, x: Double, y: Double, cell: Double, gap: Double, alpha: Double,
    onInk: Bool, label: Bool
  ) {
    guard alpha > 0.003 else { return }
    let states = tallyStates(t)
    canvas.tally(states: states, x: x, y: y, cell: cell, gap: gap, onInk: onInk, alpha: alpha)
    if label {
      let done = states.filter { $0.amount > 0 }.count
      let width = 15 * cell + 14 * gap
      canvas.text("RECORDED METHODS", mono(18, Ink.dim), x: x, y: y - 16, alpha: alpha)
      canvas.text(String(format: "%02d / 15", done), mono(18, Ink.paper), x: x + width, y: y - 16, align: .right, alpha: alpha)
    }
  }

  /// 38.0–42.2: the count, and what it does not mean.
  private func sceneTally(_ canvas: Canvas, _ t: Double) {
    let local = t - Cue.tally
    let alpha = 1 - seg(t, Cue.open + 0.05, Cue.open + 0.4)
    let move = easeInOut(seg(local, 0.25, 1.0))
    let cell = lerp(30, 78, move), gap = lerp(9.6, 20, move)
    let width = 15 * cell + 14 * gap
    let x = lerp(panelX, (Double(W) - width) / 2, move), y = lerp(962, 468, move)
    drawTally(canvas, t, x: x, y: y, cell: cell, gap: gap, alpha: alpha, onInk: true, label: false)
    topline(canvas, alpha * seg(local, 0.3, 0.7), onInk: true)
    canvas.reveal("15 recorded methods.", sans(84, Ink.paper), x: 96, y: 262, t: local - 0.45, alpha: alpha)
    let lead = "I still "
    let style = sans(84, Ink.paper)
    let leadWidth = canvas.width(lead, style) + style.tracking * 84
    let mark = easeOut(seg(local, 2.75, 3.15))
    let marked = "haven’t found the key."
    canvas.marker(Box(x: 96 + leadWidth - 5, y: 296, w: (canvas.width(marked, style) + 22) * mark, h: 92), Ink.lime, alpha)
    canvas.reveal(lead, style, x: 96, y: 366, t: local - 2.3, alpha: alpha)
    canvas.reveal(marked, sans(84, Ink.paper.mix(Ink.ink, mark)), x: 96 + leadWidth, y: 366, t: local - 2.42, alpha: alpha)

    // What the squares are.
    let legend: [(StampTone, String)] = [
      (.tested, "10 tested, no result"), (.corrected, "1 claim corrected"),
      (.open, "3 partial leads"), (.question, "1 open question"),
    ]
    var cursor = (Double(W) - width) / 2
    for (index, entry) in legend.enumerated() {
      let show = alpha * seg(local, 2.5 + 0.1 * Double(index), 2.8 + 0.1 * Double(index))
      canvas.tally(states: [(entry.0, show > 0 ? 1 : 0)], x: cursor, y: 604, cell: 22, gap: 0, onInk: true, alpha: show)
      cursor += 34
      cursor += canvas.text(entry.1, mono(23, Ink.paper), x: cursor, y: 623, alpha: show) + 46
    }
    canvas.text(
      "“No result” covers only the candidates tested. It does not close the wider idea.",
      mono(23, Ink.dim), x: (Double(W) - width) / 2, y: 690, alpha: alpha * seg(local, 3.0, 3.35))
  }

  /// 42.2–48.2: everything goes public.
  private func scenePublic(_ canvas: Canvas, _ t: Double) {
    let local = t - Cue.open
    let alpha = 1 - seg(t, Cue.funding - 0.05, Cue.funding + 0.3)
    topline(canvas, alpha * seg(local, 0.4, 0.8), onInk: false, right: "PUBLIC ON GITHUB")
    let style = sans(96, Ink.ink)
    let lead = "So I put all of it "
    let leadWidth = canvas.width(lead, style) + style.tracking * 96
    let mark = easeOut(seg(local, 1.0, 1.4))
    canvas.marker(Box(x: 96 + leadWidth - 12, y: 196, w: (canvas.width("in public.", style) + 28) * mark, h: 106), Ink.lime, alpha)
    canvas.reveal(lead, style, x: 96, y: 278, t: local - 0.3, alpha: alpha)
    canvas.reveal("in public.", style, x: 96 + leadWidth, y: 278, t: local - 0.62, alpha: alpha)

    let items = [
      "8 source pages", "the exact printed lines", "15 method records: scope, evidence, limits",
      "every dead end and correction", "the scripts and their exact output",
    ]
    for (index, item) in items.enumerated() {
      let at = 1.1 + 0.26 * Double(index)
      let show = alpha * easeOut(seg(local, at, at + 0.35))
      let y = 420 + Double(index) * 74
      let slide = 26 * (1 - easeOut(seg(local, at, at + 0.35)))
      canvas.fill(Box(x: 96 + slide, y: y - 28, w: 28, h: 28), Ink.lime, show)
      canvas.stroke(Box(x: 96 + slide, y: y - 28, w: 28, h: 28), Ink.ink, show, width: 2.5)
      canvas.text(item, sans(46, Ink.ink, weight: 560), x: 146 + slide, y: y, alpha: show)
    }

    // The invitation: optional, and open to people and models alike.
    let card = Box(x: 1090, y: 372, w: 734, h: 372)
    let show = alpha * easeOut(seg(local, 2.7, 3.1))
    let lift = 30 * (1 - easeOut(seg(local, 2.7, 3.1)))
    if show > 0 {
      canvas.fill(Box(x: card.x + 12, y: card.y + 12 + lift, w: card.w, h: card.h), Ink.ink, show)
      canvas.fill(Box(x: card.x, y: card.y + lift, w: card.w, h: card.h), Ink.sheet, show)
      canvas.stroke(Box(x: card.x, y: card.y + lift, w: card.w, h: card.h), Ink.ink, show, width: 3)
      canvas.text("START WHERE I GOT STUCK", mono(21, Ink.muted), x: card.x + 38, y: card.y + 62 + lift, alpha: show)
      canvas.text("Anyone, or any AI,", sans(56, Ink.ink), x: card.x + 36, y: card.y + 146 + lift, alpha: show)
      canvas.text("can pick it up from here.", sans(56, Ink.ink), x: card.x + 36, y: card.y + 212 + lift, alpha: show)
      canvas.text("github.com/dctrpr/key-not-found", mono(26, Ink.ink), x: card.x + 38, y: card.y + 282 + lift, alpha: show * seg(local, 3.2, 3.5))
      canvas.text("Help is optional. No token is needed.", mono(21, Ink.muted), x: card.x + 38, y: card.y + 328 + lift, alpha: show * seg(local, 3.5, 3.8))
    }
  }

  /// 48.2–56.0: what is active, what is committed, what is unknown.
  /// Few words, set large, so it still reads in a phone feed.
  private func sceneFunding(_ canvas: Canvas, _ t: Double) {
    let local = t - Cue.funding
    let alpha = seg(local, 0.25, 0.55) * (1 - seg(t, Cue.end, Cue.end + 0.3))
    guard alpha > 0 else { return }

    // Status comes first. The contract is never drawn here: the site is its one source.
    let tag = Style(font: assets.fonts.mono(34), color: Ink.ink, tracking: 0.06)
    let tagWidth = canvas.width("$KEY404 IS LIVE", tag) + 94
    canvas.fill(Box(x: 96, y: 74, w: tagWidth, h: 72), Ink.lime, alpha)
    canvas.stroke(Box(x: 96, y: 74, w: tagWidth, h: 72), Ink.ink, alpha, width: 3)
    canvas.fill(Box(x: 122, y: 102, w: 16, h: 16), Ink.ink, alpha)
    canvas.text("$KEY404 IS LIVE", tag, x: 158, y: 122, alpha: alpha)
    canvas.text(
      "official contract at keynotfound.com", mono(24, Ink.muted), x: Double(W) - 96, y: 122,
      align: .right, alpha: alpha * seg(local, 0.5, 0.9))

    func label(_ text: String, x: Double, y: Double, alpha: Double, onInk: Bool, dashed: Bool = false) {
      let style = Style(font: assets.fonts.mono(24), color: Ink.ink, tracking: 0.08)
      let box = Box(x: x, y: y, w: canvas.width(text, style) + 34, h: 46)
      if onInk { canvas.fill(box, Ink.lime, alpha) }
      canvas.stroke(box, onInk ? Ink.lime : Ink.ink, alpha, width: 2.5, dash: dashed ? [8, 6] : [])
      canvas.text(text, style, x: x + 17, y: y + 32, alpha: alpha)
    }

    // Active: the rule for fees the project actually receives. It states no amount
    // and no funded run.
    let activeIn = easeOut(seg(local, 0.7, 1.1))
    let active = alpha * activeIn, rise1 = 30 * (1 - activeIn)
    label("ACTIVE", x: 96, y: 196 + rise1, alpha: active, onInk: false)
    canvas.text("Creator fees actually received", sans(68, Ink.ink), x: 96, y: 326 + rise1, alpha: active)
    canvas.text("fund AI research runs.", sans(68, Ink.ink), x: 96, y: 406 + rise1, alpha: active)
    canvas.text(
      "each funded run publishes method, cost and result", mono(24, Ink.muted), x: Double(W) - 96,
      y: 402 + rise1, align: .right, alpha: active * seg(local, 1.3, 1.7))

    // Committed: the allocation is firm; it applies if the project recovers the prize.
    let committedIn = easeOut(seg(local, 2.5, 2.9))
    let committed = alpha * committedIn, rise2 = 36 * (1 - committedIn)
    canvas.fill(Box(x: 0, y: 470 + rise2, w: Double(W), h: 312), Ink.ink, committed)
    label("COMMITTED", x: 96, y: 502 + rise2, alpha: committed, onInk: true)
    let line = sans(82, Ink.paper)
    canvas.text("If this project recovers the prize BTC,", line, x: 96, y: 644 + rise2, alpha: committed)
    let mark = easeOut(seg(local, 3.2, 3.6))
    let hundred = canvas.width("100%", line)
    canvas.marker(Box(x: 96, y: 668 + rise2, w: (hundred + 30) * mark, h: 90), Ink.lime, committed)
    canvas.text("100%", sans(82, Ink.paper.mix(Ink.ink, mark)), x: 110, y: 742 + rise2, alpha: committed)
    canvas.text(
      " funds $KEY404 buybacks.", line, x: 116 + hundred + line.tracking * 82, y: 742 + rise2,
      alpha: committed)

    // Unknown: the prize and its recovery.
    let unknownIn = easeOut(seg(local, 4.7, 5.1))
    let unknown = alpha * unknownIn, rise3 = 30 * (1 - unknownIn)
    label("UNKNOWN", x: 96, y: 822 + rise3, alpha: unknown, onInk: false, dashed: true)
    canvas.text("The prize and its recovery are unverified.", sans(60, Ink.ink), x: 96, y: 944 + rise3, alpha: unknown)
  }

  /// 56.0–62.0: the article's characters spell the title.
  private func sceneEnd(_ canvas: Canvas, _ t: Double) {
    let local = t - Cue.end
    topline(canvas, seg(local, 0.5, 0.9), onInk: false)
    // The scan the whole thing started from.
    let arrive = easeOut(seg(local, 0.7, 1.5))
    if arrive > 0, let image = assets.large[73] {
      let box = Box(x: 1356 + 220 * (1 - arrive), y: 150, w: 452, h: 452 * 3264 / 2544)
      let ctx = canvas.ctx
      ctx.saveGState()
      ctx.translateBy(x: CGFloat(box.x + box.w / 2), y: CGFloat(box.y + box.h / 2))
      ctx.rotate(by: 0.028)
      let centred = Box(x: -box.w / 2, y: -box.h / 2, w: box.w, h: box.h)
      canvas.fill(Box(x: centred.x + 14, y: centred.y + 14, w: box.w, h: box.h), Ink.ink, arrive)
      canvas.fill(centred, Ink.sheet, arrive)
      canvas.image(image, in: centred, alpha: arrive)
      canvas.stroke(centred, Ink.ink, arrive, width: 2.5)
      ctx.restoreGState()
      canvas.text("EXHIBIT 01 · ISSUE 24 · P.73", mono(18, Ink.muted), x: box.x + 4, y: 786, alpha: arrive * seg(local, 1.5, 1.9))
    }
    // Marker behind NOT, then the title in solid ink over its own characters.
    let titleStyle = Style(font: assets.fonts.sans(titleSize, 650), color: Ink.ink, tracking: -0.075)
    let keyWidth = canvas.width("KEY ", titleStyle) + titleStyle.tracking * Double(titleSize)
    let notWidth = canvas.width("NOT", titleStyle)
    let mark = easeOut(seg(local, 2.7, 3.2))
    canvas.marker(
      Box(x: titleX + keyWidth - 14, y: titleY1 - 222, w: (notWidth + 34) * mark, h: 238),
      Ink.lime, 1, skew: -0.12, tilt: -0.024)
    drawTitle(canvas, color: Ink.ink, alpha: easeInOut(seg(local, 2.5, 3.3)))

    canvas.reveal("One solver. Since 2023. The work is public.", sans(54, Ink.ink), x: 96, y: 800, t: local - 3.3)
    canvas.text("keynotfound.com", mono(32, Ink.ink), x: 96, y: 872, alpha: seg(local, 3.9, 4.3))
    canvas.text("Help is optional. Reading, testing and correcting need no token.", mono(21, Ink.muted), x: 96, y: 924, alpha: seg(local, 4.3, 4.7))
  }

  // MARK: Debug

  private func renderAlignment(_ canvas: Canvas) {
    let box = closeBox
    canvas.fill(Box(x: 0, y: 0, w: Double(W), h: Double(H)), Ink.ink)
    canvas.image(assets.page(75, height: box.h), in: box)
    for particle in assets.particles where particle.page == 0 {
      let x = box.x + particle.u * box.w, y = box.y + particle.v * box.h
      let size = particle.pitch * box.w / 0.6
      canvas.ctx.setFillColor(
        cg(particle.isHighlighted ? RGB(0x0044FF) : (particle.isBar ? Ink.lime : Ink.red), 0.9))
      canvas.glyph(particle.glyph, font: assets.particleFont, x: x, y: y, scale: size / Double(Assets.particleFontSize))
    }
    canvas.text("Alignment check", sans(64, Ink.paper), x: 96, y: 200)
    canvas.text(
      "\(assets.particles.count) characters · \(assets.rows.count) rows · \(assets.numberTokens.count) numbers · \(assets.fragmentCount) fragments",
      mono(24, Ink.lime), x: 96, y: 260)
  }
}
