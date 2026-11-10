// KEY NOT FOUND — explainer film renderer.
// Build and run from the repository root; see scripts/explainer/README.md.
import Foundation

let root = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
guard FileManager.default.fileExists(atPath: root.appendingPathComponent("package.json").path)
else { fail("Run this from the repository root (the folder that holds package.json).") }

var arguments = Array(CommandLine.arguments.dropFirst())
func option(_ name: String) -> String? {
  guard let index = arguments.firstIndex(of: name), index + 1 < arguments.count else { return nil }
  return arguments[index + 1]
}
let outputDirectory = URL(
  fileURLWithPath: option("--out") ?? "node_modules/.cache/key404-film", relativeTo: root)

let film = Film(assets: Assets(root: root))

if arguments.contains("--debug-alignment") {
  film.debugAlignment = true
  write(renderStill(film, time: 0), to: outputDirectory.appendingPathComponent("alignment.png"))
  print("Wrote alignment.png")
  exit(0)
}
if let list = option("--frames") {
  for value in list.split(separator: ",") {
    guard let time = Double(value) else { continue }
    let name = String(format: "frame-%05.2f.png", time)
    write(renderStill(film, time: time), to: outputDirectory.appendingPathComponent(name))
    print("Wrote \(name)")
  }
  exit(0)
}
if let step = option("--contact").flatMap(Double.init) {
  let times = Array(stride(from: 0.0, to: DURATION, by: step))
  contactSheet(film, times: times, columns: 4, to: outputDirectory.appendingPathComponent("contact.png"))
  print("Wrote contact.png with \(times.count) frames")
  exit(0)
}
if let time = option("--poster").flatMap(Double.init) {
  let target = URL(fileURLWithPath: option("--to") ?? "public/media/key404-film-poster.jpg", relativeTo: root)
  write(renderStill(film, time: time), to: target, jpegQuality: 0.86)
  print("Wrote \(target.lastPathComponent) from \(time)s")
  exit(0)
}
if arguments.contains("--score-levels") {
  let score = composeScore()
  for start in stride(from: 0.0, to: DURATION, by: 4) {
    let level = score.level(from: start, to: min(DURATION, start + 4))
    print(String(format: "%4.0fs  peak %5.1f dBFS  rms %5.1f dBFS", start, 20 * log10(max(level.peak, 1e-6)), 20 * log10(max(level.rms, 1e-6))))
  }
  exit(0)
}
if let path = option("--inspect") {
  let times = (option("--at") ?? "").split(separator: ",").compactMap { Double($0) }
  inspectMovie(at: URL(fileURLWithPath: path, relativeTo: root), frames: times, into: outputDirectory)
  exit(0)
}
if arguments.contains("--render") {
  let target = URL(fileURLWithPath: option("--to") ?? "public/media/key404-film.mp4", relativeTo: root)
  let bitrate = option("--bitrate").flatMap(Int.init) ?? 3_800_000
  let score = arguments.contains("--no-audio") ? nil : composeScore()
  // --seconds renders only the start of the film: a quick check of the export.
  exportMovie(
    film, score: score, to: target, bitrate: bitrate, seconds: option("--seconds").flatMap(Double.init))
  exit(0)
}
print("Nothing to do. Use --render, --poster, --frames, --contact, --score-levels or --inspect.")
