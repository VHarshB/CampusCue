const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {MeetupEngine} = require('./engine');

const ROOT=path.join(__dirname,'..','public');
function json(res,status,obj){res.writeHead(status,{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});res.end(JSON.stringify(obj));}
function createServer(engine=new MeetupEngine(), gpsLinks=new Map()) {
  return http.createServer(async(req,res)=>{
    res.setHeader('X-Frame-Options','DENY');
    res.setHeader('Referrer-Policy','no-referrer');
    res.setHeader('Cache-Control','no-store');
    const url=new URL(req.url,'http://localhost');
    if(req.method==='GET' && ['/','/gps'].includes(url.pathname)){
      const filename=url.pathname==='/gps'?'gps.html':'index.html';
      res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});
      return fs.createReadStream(path.join(ROOT,filename)).pipe(res);
    }
    if(req.method==='GET' && url.pathname==='/health')return json(res,200,{ok:true,mode:'prototype'});
    if(req.method!=='POST' && !(req.method==='GET' && url.pathname==='/api/status'))return json(res,404,{error:'Not found'});
    const token=String(req.headers.authorization||'').replace(/^Bearer /i,'').trim();
    let data={};
    if(req.method==='POST'){
      try{
        const chunks=[];let size=0;
        for await (const chunk of req){size+=chunk.length;if(size>12000)return json(res,413,{error:'Request too large'});chunks.push(chunk);}
        data=JSON.parse(Buffer.concat(chunks).toString('utf8'));
      }catch{return json(res,400,{error:'Invalid JSON'});}
    }
    try{
      let output;
      switch(url.pathname){
        case '/api/join': output=engine.join(data);break;
        case '/api/status': output=engine.status(token);break;
        case '/api/location': output=engine.updateGPS(token,data.coords,data.gpsConsent);break;
        case '/api/decide': output=engine.decide(token,data.accept);break;
        case '/api/stop': output=engine.stop(token);break;
        case '/api/gps-once': {
          const rec=gpsLinks.get(data.linkToken);
          if(!rec||rec.expires<Date.now())throw Object.assign(new Error('GPS link is invalid or expired.'),{status:403});
          gpsLinks.delete(data.linkToken);
          output=engine.updateGPS(rec.studentToken,data.coords,data.gpsConsent);
          break;
        }
        default:return json(res,404,{error:'Not found'});
      }
      return json(res,200,output);
    }catch(err){return json(res,err.status||500,{error:err.status?err.message:'Unexpected server error'});}
  });
}
if(require.main===module){
  const server=createServer();const port=Number(process.env.PORT)||3000;
  server.listen(port,'127.0.0.1',()=>console.log(`CampusCue Connect demo: http://127.0.0.1:${port}`));
}
module.exports={createServer};
