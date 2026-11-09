import Foundation
import Vision
import ImageIO
import CoreGraphics
struct Spec: Decodable { let page:Int; let label:String; let x0:Double; let y0:Double; let x1:Double; let y1:Double }
let args=CommandLine.arguments
let specs=try JSONDecoder().decode([Spec].self,from:Data(contentsOf:URL(fileURLWithPath:args[1])))
var records:[[String:Any]]=[]
for s in specs {
 let path=String(format:"%@/page_%02d.jpg",args[2],s.page)
 let imageSource=CGImageSourceCreateWithURL(URL(fileURLWithPath:path) as CFURL,nil)!
 let full=CGImageSourceCreateImageAtIndex(imageSource,0,nil)!
 let rect=CGRect(x:s.x0*Double(full.width),y:s.y0*Double(full.height),width:(s.x1-s.x0)*Double(full.width),height:(s.y1-s.y0)*Double(full.height))
 let crop=full.cropping(to:rect)!
 let req=VNRecognizeTextRequest()
 req.recognitionLevel = .accurate
 req.usesLanguageCorrection = false
 req.recognitionLanguages=["en-US"]
 try VNImageRequestHandler(cgImage:crop,options:[:]).perform([req])
 let ls=(req.results ?? []).sorted { a,b in
   if abs(a.boundingBox.midY-b.boundingBox.midY)<0.003 {return a.boundingBox.minX < b.boundingBox.minX}
   return a.boundingBox.midY>b.boundingBox.midY
 }
 for (n,r) in ls.enumerated() {
  guard let c=r.topCandidates(1).first else {continue}
  let b=r.boundingBox
  records.append(["page":s.page,"region":s.label,"line":n+1,"text":c.string,"confidence":c.confidence,"x0":s.x0+b.minX*(s.x1-s.x0),"y0":s.y0+(1-b.maxY)*(s.y1-s.y0),"x1":s.x0+b.maxX*(s.x1-s.x0),"y1":s.y0+(1-b.minY)*(s.y1-s.y0)])
 }
}
let data=try JSONSerialization.data(withJSONObject:records,options:[.prettyPrinted,.sortedKeys,.withoutEscapingSlashes])
FileHandle.standardOutput.write(data)
