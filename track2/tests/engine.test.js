const test=require('node:test');const assert=require('node:assert/strict');
const {MeetupEngine,distanceMeters}=require('../src/engine');
let current=Date.parse('2026-10-24T20:00:00Z');
const base={minutes:45,vibe:'social',activity:'coffee',interests:'music,coffee',area:'Palm Walk',consent:true};
function join(e,name,extra={}){return e.join({...base,name,...extra});}
test('explicit opt-in is required and private location is never returned',()=>{
  const e=new MeetupEngine(()=>current);
  assert.throws(()=>join(e,'A',{consent:false}),/Explicit opt-in/);
  const a=join(e,'A',{gpsConsent:true,coords:{lat:33.42,lon:-111.93}});
  assert.equal(a.oneTimeLocationShared,true);
  assert.equal(JSON.stringify(a).includes('33.42'),false);
});
test('two personal agents find compatible interests, time, activity, mood',()=>{
  const e=new MeetupEngine(()=>current);
  const a=join(e,'A');const b=join(e,'B',{interests:'music,books'});
  const as=e.status(a.token),bs=e.status(b.token);
  assert.equal(as.state,'pending');assert.equal(bs.state,'pending');
  assert.deepEqual(as.proposal.sharedInterests,['music']);
  assert.equal(JSON.stringify(as).includes('"B"'),false);
});
test('mutual yes is required before any identity or meeting details are shared',()=>{
  const e=new MeetupEngine(()=>current);const a=join(e,'A'),b=join(e,'B');
  const first=e.decide(a.token,true);assert.equal(first.state,'pending');
  assert.equal(JSON.stringify(first).includes('B'),false);
  const both=e.decide(b.token,true);assert.equal(both.state,'confirmed');
  assert.equal(both.match.name,'A');
  assert.equal(e.status(a.token).match.name,'B');
  assert.match(both.match.location.name,/Memorial Union/);
});
test('declining never introduces the students and blocks that pair',()=>{
  const e=new MeetupEngine(()=>current);const a=join(e,'A'),b=join(e,'B');
  assert.equal(e.decide(a.token,false).state,'declined');
  assert.equal(e.status(b.token).state,undefined);
  assert.equal(e.status(a.token).state,undefined);
});
test('conflicting preferences or unavailable overlap prevent matches',()=>{
  const e=new MeetupEngine(()=>current);const a=join(e,'A');
  const b=join(e,'B',{activity:'study',vibe:'productive'});
  assert.equal(e.status(a.token).state,undefined);
  assert.equal(e.status(b.token).state,undefined);
});
test('agents can negotiate an explicitly permitted fallback activity',()=>{
  const e=new MeetupEngine(()=>current);
  const a=join(e,'A',{activity:'coffee',alternatives:'walk'});
  const b=join(e,'B',{activity:'walk',vibe:'adventurous',alternatives:'coffee'});
  // Both agents have to agree on vibe; social vs adventurous is compatible for walking.
  assert.equal(e.status(a.token).proposal.activity,'walk');
  assert.equal(e.status(b.token).proposal.activity,'walk');
});
test('far apart GPS coordinates exclude matches; close ones work',()=>{
  const e=new MeetupEngine(()=>current);
  const a=join(e,'A',{coords:{lat:33.418,lon:-111.935},gpsConsent:true});
  const b=join(e,'B',{coords:{lat:33.450,lon:-111.950},gpsConsent:true});
  assert.equal(e.status(a.token).state,undefined);
  const c=join(e,'C',{coords:{lat:33.419,lon:-111.934},gpsConsent:true});
  assert.equal(e.status(a.token).state,'pending');
  assert.equal(e.status(c.token).state,'pending');
  assert.equal(distanceMeters({lat:33.418,lon:-111.935},{lat:33.419,lon:-111.934})<1200,true);
});
test('one-time GPS requires separate explicit consent',()=>{
  const e=new MeetupEngine(()=>current);const a=join(e,'A');
  assert.throws(()=>e.updateGPS(a.token,{lat:33.42,lon:-111.93},false),/explicitly approved/);
  const s=e.updateGPS(a.token,{lat:33.42,lon:-111.93},true);
  assert.equal(s.oneTimeLocationShared,true);
});
test('stop deletes profile and pending introduction; data expires',()=>{
  const e=new MeetupEngine(()=>current);const a=join(e,'A'),b=join(e,'B');
  e.stop(a.token);assert.throws(()=>e.status(a.token),/not found/);
  assert.equal(e.status(b.token).state,undefined);
  const t=join(e,'C',{minutes:15});current+=16*60000;
  assert.throws(()=>e.status(t.token),/not found/);
  current=Date.parse('2026-10-24T20:00:00Z');
});
