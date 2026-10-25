'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {createServer}=require('../src/server');
const profile=(name)=>({name,consent:true,minutes:45,vibe:'social',activity:'coffee',interests:'music,books',area:'Palm Walk'});
async function withServer(run){const s=createServer();await new Promise(r=>s.listen(0,'127.0.0.1',r));try{await run('http://127.0.0.1:'+s.address().port);}finally{await new Promise(r=>s.close(r));}}
async function api(base,route,body,token){const headers={'Content-Type':'application/json'};if(token)headers.Authorization='Bearer '+token;const result=await fetch(base+route,{method:body===undefined?'GET':'POST',headers,body:body===undefined?undefined:JSON.stringify(body)});return {code:result.status,data:await result.json()};}
test('health check confirms single matcher architecture',async()=>withServer(async(base)=>{const r=await api(base,'/health');assert.equal(r.data.ok,true);assert.match(r.data.roles,/Cubbie/);}));
test('Cubbie clients join, poll and approve independently using private bearer tokens',async()=>withServer(async(base)=>{
 const a=(await api(base,'/api/join',profile('Alex'))).data;const b=(await api(base,'/api/join',profile('Blair'))).data;
 assert.equal(a.state,'searching');assert.equal(b.state,'pending');
 assert.equal((await api(base,'/api/status',undefined,a.token)).data.state,'pending');
 const denied=await api(base,'/api/status');assert.equal(denied.code,401);
 const one=await api(base,'/api/approve',{approve:true},a.token);assert.equal(one.data.state,'waiting');
 const two=await api(base,'/api/approve',{approve:true},b.token);assert.equal(two.data.state,'confirmed');
 assert.equal(two.data.match.name,'Alex');
 const stop=await api(base,'/api/stop',{},a.token);assert.equal(stop.data.state,'stopped');
 assert.equal((await api(base,'/api/status',undefined,a.token)).code,401);
}));
test('GPS link is random and one-time, refuses without explicit permission',async()=>withServer(async(base)=>{
 const s=(await api(base,'/api/join',profile('Alex'))).data;
 const link=(await api(base,'/api/gps-link',{},s.token)).data;
 const token=new URL(link.url).searchParams.get('token');assert.equal(token.length,48);
 const no=await api(base,'/api/gps-once',{linkToken:token,gpsConsent:false,coords:{lat:33.418,lon:-111.93}});assert.equal(no.code,400);
 const yes=await api(base,'/api/gps-once',{linkToken:token,gpsConsent:true,coords:{lat:33.418,lon:-111.93}});assert.equal(yes.code,200);assert.equal(yes.data.gpsSharedOnce,true);
 assert.equal((await api(base,'/api/gps-once',{linkToken:token,gpsConsent:true,coords:{lat:33.418,lon:-111.93}})).code,403);
}));
