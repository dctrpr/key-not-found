// Drawing primitives on a top-left, y-down canvas.
import CoreGraphics
import CoreText
import Foundation

enum Align { case left, center, right }

struct Style {
  let font: CTFont
  var color: RGB
  var tracking: Double = 0
}

enum StampTone { case tested, open, corrected, question, plain }

final class Canvas {
  let ctx: CGContext

  init(_ context: CGContext) {
    ctx = context
    ctx.translateBy(x: 0, y: CGFloat(context.height))
    ctx.scaleBy(x: CGFloat(context.width) / W, y: -CGFloat(context.height) / H)
    ctx.textMatrix = .identity
    ctx.setShouldAntialias(true)
    ctx.setShouldSmoothFonts(false)
    ctx.setAllowsFontSubpixelPositioning(true)
    ctx.setShouldSubpixelPositionFonts(true)
    ctx.setAllowsFontSubpixelQuantization(false)
    ctx.setShouldSubpixelQuantizeFonts(false)
    ctx.interpolationQuality = .high
  }

  // MARK: Shapes

  func fill(_ box: Box, _ color: RGB, _ alpha: Double = 1) {
    guard alpha > 0.003 else { return }
    ctx.setFillColor(cg(color, alpha))
    ctx.fill(box.cg)
  }

  func stroke(_ box: Box, _ color: RGB, _ alpha: Double = 1, width: Double = 2, dash: [CGFloat] = []) {
    guard alpha > 0.003 else { return }
    ctx.saveGState()
    ctx.setStrokeColor(cg(color, alpha))
    ctx.setLineWidth(CGFloat(width))
    if !dash.isEmpty { ctx.setLineDash(phase: 0, lengths: dash) }
    ctx.stroke(box.cg.insetBy(dx: CGFloat(width) / 2, dy: CGFloat(width) / 2))
    ctx.restoreGState()
  }

  func line(_ a: P2, _ b: P2, _ color: RGB, _ alpha: Double = 1, width: Double = 2) {
    guard alpha > 0.003 else { return }
    ctx.saveGState()
    ctx.setStrokeColor(cg(color, alpha))
    ctx.setLineWidth(CGFloat(width))
    ctx.move(to: CGPoint(x: a.x, y: a.y))
    ctx.addLine(to: CGPoint(x: b.x, y: b.y))
    ctx.strokePath()
    ctx.restoreGState()
  }

  /// A highlighter stroke: slightly skewed, like the marker on the site.
  func marker(_ box: Box, _ color: RGB, _ alpha: Double = 1, skew: Double = -0.11, tilt: Double = -0.022) {
    guard alpha > 0.003, box.w > 0.5 else { return }
    ctx.saveGState()
    ctx.translateBy(x: CGFloat(box.x + box.w / 2), y: CGFloat(box.y + box.h / 2))
    ctx.rotate(by: CGFloat(tilt))
    ctx.concatenate(CGAffineTransform(a: 1, b: 0, c: CGFloat(skew), d: 1, tx: 0, ty: 0))
    ctx.setFillColor(cg(color, alpha))
    ctx.fill(CGRect(x: -box.w / 2, y: -box.h / 2, width: box.w, height: box.h))
    ctx.restoreGState()
  }

  func image(_ image: CGImage, in box: Box, alpha: Double = 1) {
    guard alpha > 0.003 else { return }
    ctx.saveGState()
    ctx.setAlpha(CGFloat(alpha))
    ctx.translateBy(x: CGFloat(box.x), y: CGFloat(box.y + box.h))
    ctx.scaleBy(x: 1, y: -1)
    ctx.draw(image, in: CGRect(x: 0, y: 0, width: box.w, height: box.h))
    ctx.restoreGState()
  }

  func clipped(_ box: Box, _ body: () -> Void) {
    ctx.saveGState()
    ctx.clip(to: box.cg)
    body()
    ctx.restoreGState()
  }

  // MARK: Text

  func typeset(_ string: String, _ style: Style, alpha: Double = 1) -> CTLine {
    let size = CTFontGetSize(style.font)
    let attributes: [NSAttributedString.Key: Any] = [
      NSAttributedString.Key(kCTFontAttributeName as String): style.font,
      NSAttributedString.Key(kCTForegroundColorAttributeName as String): cg(style.color, alpha),
      NSAttributedString.Key(kCTKernAttributeName as String): style.tracking * Double(size),
    ]
    return CTLineCreateWithAttributedString(NSAttributedString(string: string, attributes: attributes))
  }

  func width(_ string: String, _ style: Style) -> Double {
    let line = typeset(string, style)
    // The trailing kern is not part of the visible width.
    return CTLineGetTypographicBounds(line, nil, nil, nil)
      - (string.isEmpty ? 0 : style.tracking * Double(CTFontGetSize(style.font)))
  }

  /// Draws one line with its baseline at `y`. Returns the width drawn.
  @discardableResult
  func text(
    _ string: String, _ style: Style, x: Double, y: Double, align: Align = .left, alpha: Double = 1
  ) -> Double {
    let lineWidth = width(string, style)
    guard alpha > 0.003 else { return lineWidth }
    let line = typeset(string, style, alpha: alpha)
    let left = align == .left ? x : (align == .center ? x - lineWidth / 2 : x - lineWidth)
    ctx.saveGState()
    ctx.translateBy(x: CGFloat(left), y: CGFloat(y))
    ctx.scaleBy(x: 1, y: -1)
    ctx.textPosition = .zero
    CTLineDraw(line, ctx)
    ctx.restoreGState()
    return lineWidth
  }

  /// Words rise into place one after another. `t` is seconds since the start.
  @discardableResult
  func reveal(
    _ string: String, _ style: Style, x: Double, y: Double, t: Double, align: Align = .left,
    stagger: Double = 0.055, rise: Double = 18, alpha: Double = 1
  ) -> Double {
    let total = width(string, style)
    guard t > 0, alpha > 0.003 else { return total }
    let left = align == .left ? x : (align == .center ? x - total / 2 : x - total)
    let words = string.split(separator: " ", omittingEmptySubsequences: false).map(String.init)
    var prefix = ""
    for (index, word) in words.enumerated() {
      let offset = prefix.isEmpty ? 0 : width(prefix + " ", style) + style.tracking * Double(CTFontGetSize(style.font))
      let progress = easeOut(seg(t, Double(index) * stagger, Double(index) * stagger + 0.32))
      if progress > 0.003 {
        text(word, style, x: left + offset, y: y + rise * (1 - progress), alpha: alpha * progress)
      }
      prefix = prefix.isEmpty ? word : prefix + " " + word
    }
    return total
  }

  /// One mono glyph centred on a point, optionally mirrored.
  func glyph(
    _ glyph: CGGlyph, font: CTFont, x: Double, y: Double, scale: Double, mirror: Double = 1
  ) {
    var g = glyph
    var position = CGPoint(x: -6, y: -5.4)  // half an advance, half an x-height at 20px
    ctx.saveGState()
    ctx.translateBy(x: CGFloat(x), y: CGFloat(y))
    ctx.scaleBy(x: CGFloat(scale * mirror), y: CGFloat(-scale))
    CTFontDrawGlyphs(font, &g, &position, 1, ctx)
    ctx.restoreGState()
  }

  // MARK: Marks from the site

  /// A status stamp that lands with a small overshoot. `t` is seconds since it hit.
  func stamp(
    _ label: String, tone: StampTone, font: CTFont, x: Double, y: Double, t: Double,
    onInk: Bool, angle: Double = -0.05, align: Align = .left, alpha sceneAlpha: Double = 1
  ) {
    guard t > 0, sceneAlpha > 0.003 else { return }
    let appear = seg(t, 0, 0.26)
    let scale = lerp(1.9, 1.0, easeOut(appear)) + 0.06 * sin(appear * .pi)
    let alpha = min(1, appear * 2.2) * sceneAlpha
    let size = Double(CTFontGetSize(font))
    let padX = size * 0.62, padY = size * 0.46
    let textColor: RGB
    let fillColor: RGB?
    let border: RGB
    var dash: [CGFloat] = []
    switch tone {
    case .tested:
      fillColor = onInk ? Ink.paper : Ink.ink
      textColor = onInk ? Ink.ink : Ink.paper
      border = fillColor!
    case .open:
      fillColor = Ink.lime
      textColor = Ink.ink
      border = onInk ? Ink.lime : Ink.ink
    case .corrected:
      fillColor = nil
      textColor = onInk ? Ink.redOnInk : Ink.red
      border = textColor
    case .question:
      fillColor = nil
      textColor = onInk ? Ink.paper : Ink.ink
      border = textColor
      dash = [7, 5]
    case .plain:
      fillColor = nil
      textColor = onInk ? Ink.paper : Ink.ink
      border = textColor
    }
    let style = Style(font: font, color: textColor, tracking: 0.06)
    let textWidth = width(label, style)
    let boxW = textWidth + padX * 2, boxH = size + padY * 2
    let left = align == .left ? x : (align == .center ? x - boxW / 2 : x - boxW)
    ctx.saveGState()
    ctx.translateBy(x: CGFloat(left + boxW / 2), y: CGFloat(y + boxH / 2))
    ctx.rotate(by: CGFloat(angle))
    ctx.scaleBy(x: CGFloat(scale), y: CGFloat(scale))
    ctx.translateBy(x: CGFloat(-boxW / 2), y: CGFloat(-boxH / 2))
    let box = Box(x: 0, y: 0, w: boxW, h: boxH)
    if let fillColor { fill(box, fillColor, alpha) }
    stroke(box, border, alpha, width: 2.5, dash: dash)
    text(label, style, x: padX, y: padY + size * 0.86, alpha: alpha)
    ctx.restoreGState()
  }

  /// One square per recorded method: a picture of the record, not of progress.
  func tally(
    states: [(tone: StampTone, amount: Double)], x: Double, y: Double, cell: Double, gap: Double,
    onInk: Bool, alpha: Double = 1
  ) {
    guard alpha > 0.003 else { return }
    let base = onInk ? Ink.paper : Ink.ink
    for (index, state) in states.enumerated() {
      let box = Box(x: x + Double(index) * (cell + gap), y: y, w: cell, h: cell)
      let landed = easeOutBack(clamp01(state.amount))
      if state.amount <= 0.001 {
        stroke(box, base, alpha * 0.34, width: 2)
        continue
      }
      let inset = cell * 0.5 * (1 - min(1.0, landed))
      let inner = Box(x: box.x + inset, y: box.y + inset, w: cell - inset * 2, h: cell - inset * 2)
      switch state.tone {
      case .tested, .plain:
        fill(inner, base, alpha)
      case .open:
        fill(inner, Ink.lime, alpha)
        stroke(box, base, alpha * (onInk ? 0 : 1), width: 2)
      case .corrected:
        fill(inner, onInk ? Ink.redOnInk : Ink.red, alpha)
      case .question:
        stroke(box, base, alpha, width: 2.5, dash: [6, 4])
      }
    }
  }
}
