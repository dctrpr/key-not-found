// Local, read-only Apple Vision support for the preregistered KEY404 batch.
// No network, accounts, telemetry, wallet actions or host identity collection.
// Build: swiftc -O scripts/batch20_vision.swift -o <explicit-output>/vision-reader
// All job paths are relative to the manifest directory. Outputs must stay there.
import Foundation
import Vision
import CoreImage
import CoreImage.CIFilterBuiltins
import AppKit
import ImageIO
import UniformTypeIdentifiers

struct Job: Decodable { let id: String; let path: String; let mode: String }
struct Manifest: Decodable { let jobs: [Job] }
enum Failure: Error { case usage, path, exists, image, filter }
func utc() -> String {
  let f = ISO8601DateFormatter(); f.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
  return f.string(from: Date())
}
func box(_ r: CGRect) -> [Double] { [Double(r.minX),Double(r.minY),Double(r.maxX),Double(r.maxY)] }
func metadata() -> [String:Any] {
  ["engine":"Apple Vision", "api":"VNRecognizeTextRequest / VNDetectBarcodesRequest",
   "osVersion":ProcessInfo.processInfo.operatingSystemVersionString,
   "ocrRevision":VNRecognizeTextRequestRevision3,
   "barcodeRevision":VNDetectBarcodesRequestRevision3,
   "recognitionLevel":"accurate", "recognitionLanguages":["en-US"],
   "usesLanguageCorrection":false, "automaticallyDetectsLanguage":false,
   "minimumTextHeight":0.001, "coordinateSpace":"normalized bottom-left origin",
   "barcodeSymbologies":["QR","DataMatrix","Aztec","Code128"],
   "networkRequests":0]
}
func writeJSON(_ value: Any, _ url: URL) throws {
  guard !FileManager.default.fileExists(atPath:url.path) else { throw Failure.exists }
  let data = try JSONSerialization.data(withJSONObject:value,options:[.prettyPrinted,.sortedKeys])
  try data.write(to:url,options:.withoutOverwriting)
}
func safeChild(_ root: URL,_ relative: String) throws -> URL {
  guard !relative.hasPrefix("/"), !relative.split(separator:"/").contains("..") else { throw Failure.path }
  let u=root.appendingPathComponent(relative).standardizedFileURL
  guard u.path.hasPrefix(root.standardizedFileURL.path+"/") else { throw Failure.path }
  if (try? u.resourceValues(forKeys:[.isSymbolicLinkKey]).isSymbolicLink)==true { throw Failure.path }
  return u
}
func textJob(_ u: URL) throws -> [[String:Any]] {
 return try autoreleasepool {
  let req=VNRecognizeTextRequest()
  req.revision=VNRecognizeTextRequestRevision3
  req.recognitionLevel = .accurate; req.recognitionLanguages=["en-US"]
  req.usesLanguageCorrection=false; req.automaticallyDetectsLanguage=false; req.minimumTextHeight=0.001
  try VNImageRequestHandler(url:u,options:[:]).perform([req])
  let tokenRE=try NSRegularExpression(pattern:"\\S+")
  return (req.results ?? []).compactMap { obs in
    guard let text=obs.topCandidates(1).first else { return nil }
    var words:[[String:Any]]=[]
    let ns=text.string as NSString
    for hit in tokenRE.matches(in:text.string,range:NSRange(location:0,length:ns.length)) {
      guard let range=Range(hit.range,in:text.string) else { continue }
      let word=String(text.string[range])
      if let observation=try? text.boundingBox(for:range) {
        words.append(["text":word,"box":box(observation.boundingBox)])
      } else { words.append(["text":word,"box":NSNull()]) }
    }
    return ["text":text.string,"confidence":Double(text.confidence),
      "box":box(obs.boundingBox),"words":words]
  }
}
}
func barcodeJob(_ u: URL) throws -> [[String:Any]] {
 return try autoreleasepool {
  let req=VNDetectBarcodesRequest(); req.revision=VNDetectBarcodesRequestRevision3
  req.symbologies=[.qr,.dataMatrix,.aztec,.code128]
  try VNImageRequestHandler(url:u,options:[:]).perform([req])
  return (req.results ?? []).map { obs in
    ["symbology":obs.symbology.rawValue,"confidence":Double(obs.confidence),
     "payload":obs.payloadStringValue as Any? ?? NSNull(),"box":box(obs.boundingBox)]
  }
}
}
func savePNG(_ image: CGImage,_ u: URL) throws {
  guard !FileManager.default.fileExists(atPath:u.path) else { throw Failure.exists }
  guard let dest=CGImageDestinationCreateWithURL(u as CFURL,UTType.png.identifier as CFString,1,nil) else { throw Failure.image }
  CGImageDestinationAddImage(dest,image,nil)
  guard CGImageDestinationFinalize(dest) else { throw Failure.image }
}
func makeControls(_ folder: URL) throws {
  guard !FileManager.default.fileExists(atPath:folder.path) else { throw Failure.exists }
  try FileManager.default.createDirectory(at:folder,withIntermediateDirectories:true)
  let payload="KEY404 CONTROL S6c56bnXQiBjk9mqSYE7ykVQ7NzrRy"
  let context=CIContext(options:[.useSoftwareRenderer:true])
  var made:[[String:String]]=[]
  for (name,filterName) in [("qr","CIQRCodeGenerator"),("code128","CICode128BarcodeGenerator"),("aztec","CIAztecCodeGenerator")] {
    guard let f=CIFilter(name:filterName) else { throw Failure.filter }
    f.setValue(payload.data(using:.ascii)!,forKey:"inputMessage")
    if name=="qr" { f.setValue("H",forKey:"inputCorrectionLevel") }
    if name=="code128" { f.setValue(20.0,forKey:"inputQuietSpace") }
    guard let raw=f.outputImage else { throw Failure.filter }
    let image=raw.transformed(by:CGAffineTransform(scaleX:8,y:8))
    guard let cg=context.createCGImage(image,from:image.extent) else { throw Failure.image }
    try savePNG(cg,folder.appendingPathComponent(name+".png"))
    made.append(["id":name,"path":name+".png","payload":payload])
  }
  // A deterministic plaintext control, with no system/user font metadata saved.
  let width=1800,height=320
  let space=CGColorSpaceCreateDeviceRGB()
  guard let ctx=CGContext(data:nil,width:width,height:height,bitsPerComponent:8,bytesPerRow:width*4,space:space,bitmapInfo:CGImageAlphaInfo.premultipliedLast.rawValue) else { throw Failure.image }
  ctx.setFillColor(NSColor.white.cgColor);ctx.fill(CGRect(x:0,y:0,width:width,height:height))
  NSGraphicsContext.saveGraphicsState(); NSGraphicsContext.current=NSGraphicsContext(cgContext:ctx,flipped:false)
  let attrs:[NSAttributedString.Key:Any]=[.font:NSFont.monospacedSystemFont(ofSize:56,weight:.medium),.foregroundColor:NSColor.black]
  (payload as NSString).draw(at:NSPoint(x:60,y:140),withAttributes:attrs)
  NSGraphicsContext.restoreGraphicsState()
  guard let text=ctx.makeImage() else { throw Failure.image }
  try savePNG(text,folder.appendingPathComponent("text.png"))
  try writeJSON(["expectedPayload":payload,"generated":made,"text":"text.png","metadata":metadata()],folder.appendingPathComponent("controls.json"))
}
func main() throws {
  let args=Array(CommandLine.arguments.dropFirst())
  if args==["--metadata"] {
    let d=try JSONSerialization.data(withJSONObject:metadata(),options:[.prettyPrinted,.sortedKeys]);print(String(decoding:d,as:UTF8.self));return
  }
  if args.count==2 && args[0]=="--make-controls" { try makeControls(URL(fileURLWithPath:args[1],isDirectory:true));return }
  guard args.count==4,args[0]=="--manifest",args[2]=="--out" else { throw Failure.usage }
  let manifestURL=URL(fileURLWithPath:args[1]).standardizedFileURL
  let parent=manifestURL.deletingLastPathComponent()
  let outputURL=URL(fileURLWithPath:args[3]).standardizedFileURL
  guard outputURL.path.hasPrefix(parent.path+"/") else { throw Failure.path }
  guard !FileManager.default.fileExists(atPath:outputURL.path) else { throw Failure.exists }
  let manifest=try JSONDecoder().decode(Manifest.self,from:Data(contentsOf:manifestURL))
  guard manifest.jobs.count<=2048 else { throw Failure.usage }
  var results:[[String:Any]]=[]
  for job in manifest.jobs {
    let start=Date(),began=utc()
    var row:[String:Any]=["id":job.id,"mode":job.mode,"startedAtUTC":began]
    do {
      let u=try safeChild(parent,job.path)
      if job.mode=="ocr" {row["observations"]=try textJob(u)}
      else if job.mode=="barcode" {row["observations"]=try barcodeJob(u)}
      else {throw Failure.usage}
      row["status"]="ok"
    } catch { row["status"]="error";row["errorClass"]="LocalVisionRequestFailed";row["observations"]=[] }
    row["completedAtUTC"]=utc();row["durationMs"]=Int(Date().timeIntervalSince(start)*1000)
    results.append(row)
  }
  try writeJSON(["metadata":metadata(),"jobs":results],outputURL)
}
do { try main() } catch { FileHandle.standardError.write(Data("Vision helper failed (usage, existing output, path or local engine error).\n".utf8)); exit(1) }
