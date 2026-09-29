
import AVFoundation
import AppKit
let a = CommandLine.arguments
let asset = AVURLAsset(url: URL(fileURLWithPath: a[1]))
let gen = AVAssetImageGenerator(asset: asset); gen.appliesPreferredTrackTransform = true
gen.requestedTimeToleranceBefore = .zero; gen.requestedTimeToleranceAfter = .zero
let sem = DispatchSemaphore(value: 0)
Task {
  let d = try await asset.load(.duration)
  let v = try await asset.loadTracks(withMediaType: .video), au = try await asset.loadTracks(withMediaType: .audio)
  print("duration", CMTimeGetSeconds(d), "video tracks", v.count, "audio tracks", au.count)
  for (i, s) in a.dropFirst(3).enumerated() {
    let t = CMTime(seconds: Double(s)!, preferredTimescale: 600)
    do { let (cg, _) = try await gen.image(at: t); let rep = NSBitmapImageRep(cgImage: cg)
      try rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: "\(a[2])/f\(String(format: "%02d", i)).png")) } catch { print("frame error", s, error) }
  }
  sem.signal()
}
sem.wait()
