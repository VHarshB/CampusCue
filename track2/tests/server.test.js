const test=require('node:test');const assert=require('node:assert/strict');
const {createServer}=require('../src/server');const {MeetupEngine}=require('../src/engine');
test('real HTTP API: opt in twice, ask each agent, get two yeses and revoke',async()=>{
  const srv=createServer(new MeetupEngine());await new Promise(r=>srv.listen(0,'127.0.0.1',r));
  const origin='http://127.0.0.1:'+srv.address().port;
  async function request(endpoint,data,token){
    const res=await fetch(origin+endpoint,{method:data?'POST':'GET',headers:{'Content-Type':'application/json',...(token?{Authorization:'Bearer '+token}:{})},body:data?JSON.stringify(data):undefined});return {code:res.status,body:await res.json()};
  }
  try{
    const initial={minutes:45,vibe:'social',activity:'coffee',interests:'music,coffee',area:'Palm Walk',consent:true};
    const a=await request('/api/join',{...initial,name:'Alex'});
    const b=await request('/api/join',{...initial,name:'Blair'});
    assert.equal(a.code,200);assert.equal(b.code,200);
    const A=a.body.token,B=b.body.token;
    let pa=await request('/api/status',null,A);assert.equal(pa.body.state,'pending');
    assert.ok(!JSON.stringify(pa.body).includes('Blair'));
    const ay=await request('/api/decide',{accept:true},A);assert.equal(ay.body.state,'pending');
    const by=await request('/api/decide',{accept:true},B);assert.equal(by.body.state,'confirmed');
    assert.equal(by.body.match.name,'Alex');
    const remove=await request('/api/stop',{},A);assert.equal(remove.code,200);
    const expired=await request('/api/status',null,A);assert.equal(expired.code,401);
  }finally{await new Promise(r=>srv.close(r));}
});
