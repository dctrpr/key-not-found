// An original procedural score: sine pads, filtered noise and a few struck
// tones, timed from the same cues as the picture. No samples, no recordings.
import Foundation

struct Score {
  let rate = 48_000.0
  var left: [Float]
  var right: [Float]

  init(duration: Double) {
    let count = Int(duration * 48_000)
    left = [Float](repeating: 0, count: count)
    right = [Float](repeating: 0, count: count)
  }

  private func gains(_ pan: Double) -> (Float, Float) {
    let p = (max(-1, min(1, pan)) + 1) * .pi / 4
    return (Float(cos(p)), Float(sin(p)))
  }

  /// A sustained tone with soft edges. `partials` are (ratio, gain) pairs.
  mutating func tone(
    at start: Double, length: Double, frequency: Double, to endFrequency: Double? = nil,
    gain: Double, attack: Double, release: Double, pan: Double = 0,
    partials: [(Double, Double)] = [(1, 1)], tremolo: Double = 0
  ) {
    let first = max(0, Int(start * rate))
    let total = Int(length * rate)
    let (gl, gr) = gains(pan)
    var phase = 0.0
    for offset in 0..<total {
      let index = first + offset
      if index >= left.count { break }
      let t = Double(offset) / rate
      let x = t / length
      let frequencyNow = endFrequency.map { frequency * pow($0 / frequency, x) } ?? frequency
      phase += 2 * .pi * frequencyNow / rate
      var envelope = min(1, t / attack)
      envelope = envelope * envelope * (3 - 2 * envelope)
      let tail = (length - t) / release
      if tail < 1 { envelope *= max(0, tail) * max(0, tail) }
      if tremolo > 0 { envelope *= 0.82 + 0.18 * sin(2 * .pi * tremolo * t + frequency) }
      var sample = 0.0
      for (ratio, level) in partials { sample += level * sin(phase * ratio) }
      let value = Float(sample * envelope * gain)
      left[index] += value * gl
      right[index] += value * gr
    }
  }

  /// Filtered noise. The low-pass cutoff can sweep to make a rush of air.
  mutating func noise(
    at start: Double, length: Double, gain: Double, lowpass: Double, to endLowpass: Double? = nil,
    highpass: Double = 120, attack: Double, release: Double, pan: Double = 0, seed: UInt64 = 1,
    swell: Bool = false
  ) {
    let first = max(0, Int(start * rate))
    let total = Int(length * rate)
    let (gl, gr) = gains(pan)
    var state = seed &* 0x9E37_79B9_7F4A_7C15 | 1
    var low = 0.0, low2 = 0.0, high = 0.0
    let highCoefficient = 1 - exp(-2 * .pi * highpass / rate)
    for offset in 0..<total {
      let index = first + offset
      if index >= left.count { break }
      state ^= state << 13
      state ^= state >> 7
      state ^= state << 17
      let white = Double(state >> 11) / Double(1 << 53) * 2 - 1
      let t = Double(offset) / rate
      let x = t / length
      let cutoff = endLowpass.map { lowpass * pow($0 / lowpass, x) } ?? lowpass
      let coefficient = 1 - exp(-2 * .pi * cutoff / rate)
      low += coefficient * (white - low)
      low2 += coefficient * (low - low2)
      high += highCoefficient * (low2 - high)
      var envelope: Double
      if swell {
        envelope = sin(.pi * x)
        envelope *= envelope
      } else {
        envelope = min(1, t / attack)
        let tail = (length - t) / release
        if tail < 1 { envelope *= max(0, tail) * max(0, tail) }
      }
      let value = Float((low2 - high) * envelope * gain)
      left[index] += value * gl
      right[index] += value * gr
    }
  }

  /// A stamp landing: a low thud with a little paper in it.
  mutating func thud(at time: Double, gain: Double = 1) {
    tone(at: time, length: 0.26, frequency: 96, to: 44, gain: 0.36 * gain, attack: 0.003, release: 0.22)
    noise(at: time, length: 0.07, gain: 0.36 * gain, lowpass: 1800, attack: 0.002, release: 0.06, seed: UInt64(time * 1000) + 3)
    noise(at: time, length: 0.03, gain: 0.18 * gain, lowpass: 7000, highpass: 2200, attack: 0.001, release: 0.025, seed: UInt64(time * 1000) + 9)
  }

  /// A small struck tone, used for the tally and list items.
  mutating func blip(at time: Double, frequency: Double, gain: Double, pan: Double = 0, length: Double = 0.34) {
    tone(
      at: time, length: length, frequency: frequency, gain: gain, attack: 0.004,
      release: length * 0.92, pan: pan, partials: [(1, 1), (2, 0.22), (3, 0.06)])
  }

  mutating func chord(
    at start: Double, length: Double, notes: [Double], gain: Double, attack: Double = 1.8,
    release: Double = 2.6, bright: Double = 0
  ) {
    for (index, note) in notes.enumerated() {
      let pan = notes.count > 1 ? -0.5 + Double(index) / Double(notes.count - 1) : 0
      tone(
        at: start, length: length, frequency: note, gain: gain, attack: attack, release: release,
        pan: pan, partials: [(1, 1), (2, 0.3 + 0.25 * bright), (3, 0.1 + 0.14 * bright), (4, 0.05 * bright)],
        tremolo: 0.13 + 0.05 * Double(index))
    }
  }

  /// A plain feedback-comb room so the dry parts sit in one space.
  mutating func room(mix: Float) {
    let combs = [1687, 1601, 2053, 2251, 1783, 1933]
    let passes = [245, 606]
    var wetLeft = [Float](repeating: 0, count: left.count)
    var wetRight = [Float](repeating: 0, count: left.count)
    for (index, length) in combs.enumerated() {
      for (channel, spread) in [(0, 0), (1, 31)] {
        var buffer = [Float](repeating: 0, count: length + spread)
        var cursor = 0
        var damp: Float = 0
        let feedback: Float = 0.78 - Float(index) * 0.01
        for n in 0..<left.count {
          let input = (left[n] + right[n]) * 0.5
          let delayed = buffer[cursor]
          damp = delayed * 0.72 + damp * 0.28
          buffer[cursor] = input + damp * feedback
          cursor = (cursor + 1) % buffer.count
          if channel == 0 { wetLeft[n] += delayed } else { wetRight[n] += delayed }
        }
      }
    }
    for length in passes {
      for channel in 0..<2 {
        var buffer = [Float](repeating: 0, count: length + channel * 17)
        var cursor = 0
        for n in 0..<left.count {
          let input = channel == 0 ? wetLeft[n] : wetRight[n]
          let delayed = buffer[cursor]
          let output = delayed - 0.5 * input
          buffer[cursor] = input + 0.5 * output
          cursor = (cursor + 1) % buffer.count
          if channel == 0 { wetLeft[n] = output } else { wetRight[n] = output }
        }
      }
    }
    let scale = mix / Float(combs.count)
    for n in 0..<left.count {
      left[n] += wetLeft[n] * scale
      right[n] += wetRight[n] * scale
    }
  }

  /// Gentle limiting, fades at both ends and a fixed peak level.
  mutating func master(peak: Float = 0.7) {
    let count = left.count
    let fadeIn = Int(0.05 * rate), fadeOut = Int(1.4 * rate)
    var maximum: Float = 0.0001
    for n in 0..<count {
      var fade: Float = 1
      if n < fadeIn { fade = Float(n) / Float(fadeIn) }
      if n > count - fadeOut {
        let x = Float(count - n) / Float(fadeOut)
        fade *= x * x
      }
      left[n] = tanh(left[n] * 1.3) * fade
      right[n] = tanh(right[n] * 1.3) * fade
      maximum = max(maximum, abs(left[n]), abs(right[n]))
    }
    let scale = peak / maximum
    for n in 0..<count {
      left[n] *= scale
      right[n] *= scale
    }
  }

  func level(from start: Double, to end: Double) -> (peak: Double, rms: Double) {
    let a = max(0, Int(start * rate)), b = min(left.count, Int(end * rate))
    guard b > a else { return (0, 0) }
    var peak: Float = 0
    var sum = 0.0
    for n in a..<b {
      peak = max(peak, abs(left[n]), abs(right[n]))
      sum += Double(left[n] * left[n] + right[n] * right[n]) / 2
    }
    return (Double(peak), sqrt(sum / Double(b - a)))
  }
}

/// The score for the film, built from the picture's cues.
func composeScore() -> Score {
  var score = Score(duration: DURATION)
  let A2 = 110.0, C3 = 130.81, D3 = 146.83, E3 = 164.81, F3 = 174.61, G3 = 196.0, A3 = 220.0
  let B3 = 246.94, C4 = 261.63, D4 = 293.66, E4 = 329.63, G4 = 392.0, A4 = 440.0
  let C5 = 523.25, D5 = 587.33, E5 = 659.25, G5 = 783.99, A5 = 880.0

  // Harmony: a minor first half, resolving when the work goes public.
  let pads: [(Double, Double, [Double], Double)] = [
    (0, Cue.claim + 1.2, [A2, E3, A3, C4], 0),
    (Cue.claim - 0.6, Cue.lift + 1.0, [F3 / 2, C3, F3, A3], 0),
    (Cue.lift - 0.6, Cue.mirror + 1.0, [A2, E3, A3, C4], 0.1),
    (Cue.mirror - 0.6, Cue.numbers + 1.0, [D3, A3, D4, F3], 0.15),
    (Cue.numbers - 0.6, Cue.open + 0.6, [E3 / 2, B3 / 2, E3, 207.65], 0.3),
    (Cue.open - 0.3, Cue.funding + 1.2, [C3, G3, C4, E4], 0.6),
    (Cue.funding - 0.8, Cue.end + 1.2, [F3 / 2, C3, F3, A3], 0.4),
    (Cue.end - 0.8, DURATION, [C3, G3, E4, G4], 0.7),
  ]
  for (start, end, notes, bright) in pads {
    score.chord(at: max(0, start), length: end - max(0, start), notes: notes, gain: 0.052, bright: bright)
    score.tone(
      at: max(0, start), length: end - max(0, start), frequency: notes[0] / (notes[0] > 100 ? 2 : 1),
      gain: 0.07, attack: 2.0, release: 2.4, tremolo: 0.09)
  }

  // Opening: the flock, a key in the air, then the pour onto the pages.
  score.noise(at: 0, length: 2.6, gain: 0.16, lowpass: 500, to: 2600, attack: 0.3, release: 0.6, pan: 0.3, seed: 2, swell: true)
  score.noise(at: Cue.key - 0.1, length: 0.95, gain: 0.2, lowpass: 900, to: 5200, attack: 0.1, release: 0.3, seed: 4, swell: true)
  for (index, note) in [A4, C5, E5, A5].enumerated() {
    score.blip(at: Cue.key + 0.45 + 0.13 * Double(index), frequency: note, gain: 0.05, pan: -0.4 + 0.27 * Double(index), length: 1.5)
  }
  score.noise(at: Cue.pour, length: 3.4, gain: 0.15, lowpass: 3600, to: 500, attack: 0.3, release: 1.4, pan: -0.2, seed: 6, swell: true)
  for slot in 0..<8 {
    score.blip(at: Cue.pour + 0.55 + 0.34 * Double(min(slot, 6)) + 0.05 * Double(slot), frequency: [A3, C4, D4, E4, G4, A4, C5, D5][slot], gain: 0.022, pan: -0.8 + 0.23 * Double(slot), length: 0.5)
  }

  // The claim, and its stamp.
  score.tone(at: Cue.claim + 0.15, length: 1.6, frequency: 55, gain: 0.2, attack: 0.01, release: 1.5)
  score.noise(at: Cue.claim + 0.15, length: 0.12, gain: 0.3, lowpass: 900, attack: 0.002, release: 0.1, seed: 8)
  score.thud(at: Cue.claim + 1.35, gain: 1.1)

  // Push in, then the characters lift off the page.
  score.noise(at: Cue.push, length: 1.9, gain: 0.1, lowpass: 400, to: 1800, attack: 0.3, release: 0.5, pan: 0.4, seed: 10, swell: true)
  score.noise(at: Cue.lift, length: 2.2, gain: 0.2, lowpass: 600, to: 6000, attack: 0.2, release: 0.6, pan: -0.3, seed: 12, swell: true)
  score.tone(at: Cue.lift + 0.1, length: 1.9, frequency: 220, to: 440, gain: 0.03, attack: 0.5, release: 0.8)

  // The readings: a quiet pulse while each one is tried.
  var beat = Cue.lines
  var count = 0
  while beat < Cue.tally - 0.1 {
    if count % 4 == 0 {
      score.tone(at: beat, length: 0.22, frequency: 74, to: 46, gain: 0.16, attack: 0.004, release: 0.18)
    }
    score.noise(
      at: beat, length: 0.035, gain: count % 2 == 0 ? 0.05 : 0.03, lowpass: 9000, highpass: 3500,
      attack: 0.001, release: 0.03, pan: count % 2 == 0 ? -0.35 : 0.35, seed: UInt64(count) + 40)
    beat += 0.3125
    count += 1
  }
  for stamp in [Cue.lines + 2.75, Cue.firstWords + 1.95, Cue.mirror + 1.65, Cue.highlights + 2.15, Cue.numbers + 2.45] {
    score.thud(at: stamp)
  }
  score.thud(at: Cue.mirror + 3.3, gain: 0.8)
  score.tone(at: Cue.mirror + 2.85, length: 0.4, frequency: 311.1, to: 233.1, gain: 0.04, attack: 0.01, release: 0.3)
  // The mirror turning over, both ways.
  score.noise(at: Cue.mirror + 0.15, length: 1.0, gain: 0.14, lowpass: 700, to: 4200, attack: 0.1, release: 0.3, pan: -0.5, seed: 20, swell: true)
  score.noise(at: Cue.mirror + 3.85, length: 0.85, gain: 0.12, lowpass: 4200, to: 700, attack: 0.1, release: 0.3, pan: 0.5, seed: 22, swell: true)
  // Lines closing up, highlights and numbers leaving the text.
  score.noise(at: Cue.lines + 1.25, length: 0.8, gain: 0.08, lowpass: 1200, to: 3000, attack: 0.1, release: 0.3, seed: 24, swell: true)
  score.noise(at: Cue.highlights + 0.95, length: 0.9, gain: 0.1, lowpass: 1500, to: 4500, attack: 0.1, release: 0.3, pan: 0.4, seed: 26, swell: true)
  score.noise(at: Cue.numbers + 0.55, length: 0.95, gain: 0.1, lowpass: 1500, to: 5200, attack: 0.1, release: 0.3, pan: 0.4, seed: 28, swell: true)
  score.tone(at: Cue.numbers + 1.6, length: 0.8, frequency: 440, to: 880, gain: 0.02, attack: 0.05, release: 0.2)

  // Each square on the tally is a small struck note.
  let ladder = [A4, C5, D5, E5, G5, A5, 1046.5, 1174.66]
  var rung = 0
  for entry in tallyPlan.sorted(by: { $0.at < $1.at }) {
    if entry.at >= Cue.tally {
      score.blip(at: entry.at, frequency: ladder[min(rung, ladder.count - 1)], gain: 0.05, pan: -0.5 + 0.14 * Double(rung))
      rung += 1
    } else {
      score.blip(at: entry.at, frequency: entry.tone == .corrected ? 311.1 : E5, gain: 0.04, pan: 0.3)
    }
  }
  score.noise(at: Cue.tally, length: 1.3, gain: 0.14, lowpass: 5000, to: 600, attack: 0.1, release: 0.5, seed: 30, swell: true)
  score.tone(at: Cue.tally + 2.4, length: 1.7, frequency: 82.4, gain: 0.12, attack: 0.05, release: 1.4)

  // Lights on.
  score.noise(at: Cue.open - 0.1, length: 1.5, gain: 0.16, lowpass: 800, to: 8000, highpass: 300, attack: 0.1, release: 0.8, seed: 32, swell: true)
  for (index, note) in [C4, E4, G4, C5, E5].enumerated() {
    score.blip(at: Cue.open + 0.05 + 0.06 * Double(index), frequency: note, gain: 0.05, pan: -0.5 + 0.25 * Double(index), length: 2.6)
  }
  for index in 0..<5 {
    score.blip(at: Cue.open + 1.1 + 0.26 * Double(index), frequency: [G4, A4, C5, D5, E5][index], gain: 0.028, pan: -0.5, length: 0.5)
  }
  score.blip(at: Cue.open + 2.7, frequency: G4, gain: 0.04, pan: 0.5, length: 1.2)
  score.blip(at: Cue.open + 2.7, frequency: C5, gain: 0.03, pan: 0.5, length: 1.2)

  // Funding: three plain statements, one mark.
  for (index, at) in [0.7, 2.5, 4.7].enumerated() {
    score.tone(at: Cue.funding + at, length: 0.5, frequency: [F3, A3, C4][index], gain: 0.07, attack: 0.004, release: 0.45, pan: -0.5 + 0.5 * Double(index), partials: [(1, 1), (2, 0.4), (3, 0.15)])
    score.noise(at: Cue.funding + at, length: 0.04, gain: 0.12, lowpass: 2500, attack: 0.001, release: 0.035, seed: UInt64(index) + 50)
  }
  score.noise(at: Cue.funding + 3.2, length: 0.5, gain: 0.1, lowpass: 2000, to: 6000, attack: 0.05, release: 0.2, seed: 54, swell: true)

  // The characters gather into the title; one last chord under it.
  score.noise(at: Cue.end - 0.1, length: 2.6, gain: 0.18, lowpass: 500, to: 5000, attack: 0.3, release: 0.6, seed: 56, swell: true)
  score.tone(at: Cue.end + 0.2, length: 2.3, frequency: 196, to: 392, gain: 0.025, attack: 0.6, release: 0.6)
  score.thud(at: Cue.end + 2.7, gain: 0.7)
  for (index, note) in [C4, G4, C5, E5, G5].enumerated() {
    score.blip(at: Cue.end + 2.72 + 0.05 * Double(index), frequency: note, gain: 0.055, pan: -0.5 + 0.25 * Double(index), length: 3.2)
  }

  score.room(mix: 0.3)
  score.master()
  return score
}
