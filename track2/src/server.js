/** HTTPS-deployed matchmaking API for Cubbie Skills. No student chat UI here. */
'use strict';
const http=require('node:http');
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const {MatchmakingAgent}=require('./engine');
const ROOT=path.join(__dirname,'../public');
function send(res,status,obj){res.writeHead(status,{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});res.end(JSON.stringify(obj));}
function createServer(agent=new MatchmakingAgent(),links=new Map()){
  return http.createServer(async(req,res)=>{
    res.setHeader('Cache-Control','no-store');res.setHeader('Referrer-Policy','no-referrer');res.setHeader('X-Frame-Options','DENY');
    const url=new URL(req.url,'http://localhost');
    if(req.method==='GET'&&(url.pathname==='/'||url.pathname==='/gps')){
      const filename=url.pathname==='/'?'index.html':'gps.html';res.writeHead(200,{'Content-Type':'text/html; charset=utf-8','Content-Security-Policy':"default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self'"});return fs.createReadStream(path.join(ROOT,filename)).pipe(res);
    }
    if(req.method==='GET'&&url.pathname==='/health')return send(res,200,{ok:true,mode:'hackathon-prototype',roles:'Cubbie speaks to students; CampusCue agent matches'});
    if(!url.pathname.startsWith('/api/'))return send(res,404,{error:'Not found'});
    if(!['GET','POST'].includes(req.method))return send(res,405,{error:'Method not allowed'});
    let data={};
    if(req.method==='POST'){try{const chunks=[];let size=0;for await(const c of req){size+=c.length;if(size>10000)return send(res,413,{error:'Request too large'});chunks.push(c);}data=JSON.parse(Buffer.concat(chunks).toString('utf8'));if(!data||Array.isArray(data)||typeof data!=='object')throw Error();}catch{return send(res,400,{error:'Invalid JSON'});}}
    const token=/^Bearer ([a-f0-9]{48})$/.exec(req.headers.authorization||'')?.[1];
    try{
      let out;
      switch(url.pathname){
        case '/api/join':if(req.method!=='POST')return send(res,405,{error:'Method not allowed'});out=agent.register(data);break;
        case '/api/status':if(req.method!=='GET')return send(res,405,{error:'Method not allowed'});out=agent.status(token);break;
        case '/api/approve':if(req.method!=='POST')return send(res,405,{error:'Method not allowed'});out=agent.decide(token,data.approve);break;
        case '/api/stop':if(req.method!=='POST')return send(res,405,{error:'Method not allowed'});out=agent.stop(token);for(const [k,v]of links)if(v.token===token)links.delete(k);break;
        case '/api/gps-link':{
          if(req.method!=='POST')return send(res,405,{error:'Method not allowed'});
          agent.get(token);const nonce=crypto.randomBytes(24).toString('hex');links.set(nonce,{token,expires:Date.now()+5*60000});
          // Prefer deployed HTTPS URL supplied by reverse proxy hosting (not untrusted Host header).
          const base=process.env.PUBLIC_BASE_URL||'http://localhost:3000';
          out={url:`${base.replace(/\/$/,'')}/gps?token=${nonce}`,expiresInSeconds:300,message:'Open this link on your phone and choose Share once. GPS is optional.'};break;
        }
        case '/api/gps-once':{
          if(req.method!=='POST')return send(res,405,{error:'Method not allowed'});
          const link=links.get(String(data.linkToken||''));if(!link||link.expires<Date.now())throw Object.assign(new Error('GPS link expired or invalid.'),{status:403});
          if(data.gpsConsent!==true)throw Object.assign(new Error('GPS consent was not given.'),{status:400});
          links.delete(String(data.linkToken));out=agent.shareOneTimeLocation(link.token,data.coords,true);break;
        }
        default:return send(res,404,{error:'Not found'});
      }
      return send(res,200,out);
    }catch(e){return send(res,e.status||500,{error:e.status?e.message:'Unexpected server error'});}
  });
}
if(require.main===module){const port=Number(process.env.PORT||3000),host=process.env.HOST||'0.0.0.0';createServer().listen(port,host,()=>console.log(`CampusCue matching API on ${host}:${port}`));}
module.exports={createServer};
