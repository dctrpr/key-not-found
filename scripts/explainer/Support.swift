// KEY NOT FOUND — explainer film. Shared constants, maths and colour.
// Every frame is a pure function of time, so any frame can be rendered alone.
import CoreGraphics
import Foundation

let W: CGFloat = 1920
let H: CGFloat = 1080
let FPS = 24
let DURATION = 62.0
let FRAME_COUNT = Int(DURATION * Double(FPS))

@inline(__always) func clamp01(_ x: Double) -> Double { x < 0 ? 0 : (x > 1 ? 1 : x) }
@inline(__always) func lerp(_ a: Double, _ b: Double, _ t: Double) -> Double { a + (b - a) * t }
/// 0 before `a`, 1 after `b`, linear in between.
@inline(__always) func seg(_ t: Double, _ a: Double, _ b: Double) -> Double {
  clamp01((t - a) / (b - a))
}
func easeOut(_ x: Double) -> Double { 1 - pow(1 - x, 3) }
func easeIn(_ x: Double) -> Double { x * x * x }
func easeInOut(_ x: Double) -> Double {
  x < 0.5 ? 4 * x * x * x : 1 - pow(-2 * x + 2, 3) / 2
}
func easeOutBack(_ x: Double) -> Double {
  let c1 = 1.70158, c3 = c1 + 1
  return 1 + c3 * pow(x - 1, 3) + c1 * pow(x - 1, 2)
}
func smooth(_ x: Double) -> Double { x * x * (3 - 2 * x) }
/// Rises over `fade` after `a` and falls over `fade` before `b`.
func window(_ t: Double, _ a: Double, _ b: Double, _ fade: Double = 0.3) -> Double {
  min(seg(t, a, a + fade), 1 - seg(t, b - fade, b))
}

/// Deterministic hash in [0, 1): the film renders identically every time.
func hash01(_ a: Int, _ b: Int) -> Double {
  var x = UInt64(truncatingIfNeeded: a) &* 0x9E37_79B9_7F4A_7C15
  x ^= UInt64(truncatingIfNeeded: b) &* 0xC2B2_AE3D_27D4_EB4F
  x ^= x >> 29
  x = x &* 0xBF58_476D_1CE4_E5B9
  x ^= x >> 32
  x = x &* 0x94D0_49BB_1331_11EB
  x ^= x >> 29
  return Double(x >> 11) / Double(1 << 53)
}

struct RGB {
  let r: CGFloat, g: CGFloat, b: CGFloat
  init(_ hex: UInt32) {
    r = CGFloat((hex >> 16) & 0xFF) / 255
    g = CGFloat((hex >> 8) & 0xFF) / 255
    b = CGFloat(hex & 0xFF) / 255
  }
  init(r: CGFloat, g: CGFloat, b: CGFloat) {
    self.r = r
    self.g = g
    self.b = b
  }
  func mix(_ other: RGB, _ t: Double) -> RGB {
    let k = CGFloat(clamp01(t))
    return RGB(r: r + (other.r - r) * k, g: g + (other.g - g) * k, b: b + (other.b - b) * k)
  }
}

// The site's "marked copy" palette. Lime is the solver's marker, orange is the
// magazine's own ink, red is the proofreader's pencil.
enum Ink {
  static let ink = RGB(0x0E0E0D)
  static let ink2 = RGB(0x1A1A18)
  static let inkLine = RGB(0x3B3A36)
  static let paper = RGB(0xF4F1E8)
  static let paper2 = RGB(0xE9E5D8)
  static let sheet = RGB(0xFBFAF6)
  static let line = RGB(0xCFCABB)
  static let muted = RGB(0x5F5C54)
  static let dim = RGB(0xB9B6AB)
  static let lime = RGB(0xD6FF3C)
  static let orange = RGB(0xFB8A24)
  static let red = RGB(0xC8281E)
  static let redOnInk = RGB(0xFF6A5C)
}

let sRGB = CGColorSpace(name: CGColorSpace.sRGB)!
func cg(_ c: RGB, _ alpha: Double = 1) -> CGColor {
  CGColor(colorSpace: sRGB, components: [c.r, c.g, c.b, CGFloat(clamp01(alpha))])!
}

struct P2 {
  var x: Double
  var y: Double
  static func + (a: P2, b: P2) -> P2 { P2(x: a.x + b.x, y: a.y + b.y) }
  static func - (a: P2, b: P2) -> P2 { P2(x: a.x - b.x, y: a.y - b.y) }
  static func * (a: P2, k: Double) -> P2 { P2(x: a.x * k, y: a.y * k) }
  func mix(_ b: P2, _ t: Double) -> P2 { P2(x: lerp(x, b.x, t), y: lerp(y, b.y, t)) }
}

struct Box {
  var x: Double, y: Double, w: Double, h: Double
  var cg: CGRect { CGRect(x: x, y: y, width: w, height: h) }
  func mix(_ b: Box, _ t: Double) -> Box {
    Box(x: lerp(x, b.x, t), y: lerp(y, b.y, t), w: lerp(w, b.w, t), h: lerp(h, b.h, t))
  }
  func contains(_ p: P2) -> Bool { p.x >= x && p.x <= x + w && p.y >= y && p.y <= y + h }
}

func fail(_ message: String) -> Never {
  FileHandle.standardError.write((message + "\n").data(using: .utf8)!)
  exit(1)
}
