/** CampusCue Connect: two opt-in student agents negotiating one safe public meetup.
 * Prototype only: ephemeral in-memory data, no identification, no persistent tracking.
 */
const crypto = require('node:crypto');

const VALID_VIBES = new Set(['social','chill','adventurous','productive','low-key']);
const VALID_ACTIVITIES = new Set(['coffee','study','walk','chat','event']);
const MAX_RADIUS_METERS = 1200;
const MIN_OVERLAP_MINUTES = 15;
const POINT = Object.freeze({
  name: 'Memorial Union main entrance (public meeting point)',
  address: '301 E Orange St, Tempe, AZ 85281',
  map: 'https://www.asu.edu/map/interactive/?psCode=MU',
  note: 'Meet outside in a visible public area. Check your walking route and return-to-class time.'
});
function error(message, status=400) { const e = new Error(message);e.status=status;return e; }
function cleanString(v, limit=60) {return String(v ?? '').trim().replace(/[<>\r\n]/g,'').slice(0, limit);}
function distanceMeters(a,b) {
  const rad=x=>x*Math.PI/180, R=6371000;
  const p1=rad(a.lat),p2=rad(b.lat),dp=rad(b.lat-a.lat),dl=rad(b.lon-a.lon);
  const z=Math.sin(dp/2)**2+Math.cos(p1)*Math.cos(p2)*Math.sin(dl/2)**2;
  return R*2*Math.atan2(Math.sqrt(z),Math.sqrt(1-z));
}
function validCoords(v) {return v && typeof v.lat==='number' && typeof v.lon==='number' && Number.isFinite(v.lat) && Number.isFinite(v.lon) && Math.abs(v.lat)<=90 && Math.abs(v.lon)<=180;}
function interestsOf(input) {return [...new Set((Array.isArray(input)? input : String(input??'').split(',')).map(x=>cleanString(x,24).toLowerCase()).filter(Boolean))].slice(0,6);}
function vibeCompatible(a,b,activity) {
  if (a===b) return true;
  const social=new Set(['social','low-key','chill']);
  if(['coffee','chat'].includes(activity)&&social.has(a)&&social.has(b))return true;
  if(activity==='study'&&[a,b].every(v=>['productive','low-key'].includes(v)))return true;
  if(['walk','event'].includes(activity)&&[a,b].every(v=>['social','adventurous'].includes(v)))return true;
  return false;
}
function overlapMinutes(a,b,now) {
  return Math.max(0,Math.floor((Math.min(a.until,b.until) - Math.max(now,a.since,b.since))/60000));
}
class PersonalAgent {
  constructor(privateProfile) {this.profile=privateProfile;}
  // The other agent receives only the fields explicitly authorized for matching.
  proposalPacket() {
    const p=this.profile;
    return {discoveryConsent:p.discoveryConsent,since:p.since,until:p.until,
      activities:[...p.activities],interests:[...p.interests]};
  }
  // No peer identity, private mood, raw coordinates or private calendar enters here.
  evaluate(packet,context,now){
    const a=this.profile,b=packet;
    if(!a.discoveryConsent || !b.discoveryConsent || a.until<=now || b.until<=now || !context.proximityOK)return null;
    const negotiatedActivity=a.activities.find(x=>b.activities.includes(x) && context.vibeOK(x));
    if(!negotiatedActivity)return null;
    const overlap=overlapMinutes(a,b,now);
    if(overlap < MIN_OVERLAP_MINUTES)return null;
    const shared=a.interests.filter(x=>b.interests.includes(x));
    if(shared.length===0)return null;
    return {overlap,shared,negotiatedActivity,
      score:shared.length*25+overlap-(context.meters===null?0:context.meters/30)};
  }
}
class MeetupEngine {
  constructor(now=()=>Date.now()) {this.now=now;this.people=new Map();this.proposals=new Map();this.blockedPairs=new Set();this.events=[];}
  _get(token){const p=this.people.get(token);if(!p)throw error('Student session not found.',401);return p;}
  _cleanup(){
    const now=this.now();
    for(const [id,p] of this.people) if(p.until<=now || p.stopped) this.people.delete(id);
    for(const [id,p] of this.proposals) if(p.expiresAt<=now || !this.people.has(p.a)||!this.people.has(p.b))this.proposals.delete(id);
    // Blocked pairs are only needed while both temporary sessions remain alive.
    for(const key of this.blockedPairs) if(key.split(':').some(id=>!this.people.has(id)))this.blockedPairs.delete(key);
  }
  _unpaired(token){return ![...this.proposals.values()].some(x=>(x.a===token||x.b===token) && ['pending','confirmed'].includes(x.state));}
  join(input){
    this._cleanup();
    if(input?.consent!==true)throw error('Explicit opt-in is required before searching for people.');
    const name=cleanString(input.name,30);if(!name) throw error('Enter a display name.');
    const minutes=Number(input.minutes);
    if(!Number.isInteger(minutes)||minutes<15||minutes>120)throw error('Free time must be 15–120 minutes.');
    const vibe=cleanString(input.vibe).toLowerCase();if(!VALID_VIBES.has(vibe))throw error('Choose a valid mood.');
    const activity=cleanString(input.activity).toLowerCase();if(!VALID_ACTIVITIES.has(activity))throw error('Choose a valid activity.');
    const area=cleanString(input.area,60);
    if(!area)throw error('Share a general campus area (not your precise location).');
    const acceptableActivities=(Array.isArray(input.alternatives)?input.alternatives:String(input.alternatives??'').split(','))
      .map(x=>cleanString(x).toLowerCase()).filter(x=>VALID_ACTIVITIES.has(x));
    const activities=[...new Set([activity,...acceptableActivities])];
    const interests=interestsOf(input.interests);
    if(interests.length===0)throw error('Enter at least one interest.');
    const coords=input.coords;
    if(coords && (!input.gpsConsent || !validCoords(coords)))throw error('GPS requires separate explicit one-time consent and valid coordinates.');
    // Distinct high-entropy token represents each student for this local demonstration.
    const token=crypto.randomBytes(24).toString('hex');
    const now=this.now();
    const p={id:token,name,minutes,vibe,activity,activities,area,interests,coords:coords?{lat:coords.lat,lon:coords.lon}:null,
      gpsConsent:!!(coords&&input.gpsConsent),discoveryConsent:true,since:now,until:now+minutes*60000,stopped:false};
    this.people.set(token,p);
    this.events.push({event:'student-opted-in',time:now,agent:token.slice(0,5)});
    this._findMatches();
    return {token,...this.status(token)};
  }
  updateGPS(token,coords,gpsConsent){
    this._cleanup();const p=this._get(token);
    if(gpsConsent!==true || !validCoords(coords))throw error('One-time location sharing must be explicitly approved.');
    if(p.until<=this.now())throw error('Your session expired.');
    p.coords={lat:coords.lat,lon:coords.lon};p.gpsConsent=true;
    this._findMatches();return this.status(token);
  }
  _findMatches(){
    const now=this.now();
    const options=[...this.people.values()].filter(x=>x.until>now && this._unpaired(x.id));
    let best=null;
    for(let i=0;i<options.length;i++)for(let j=i+1;j<options.length;j++){
      const a=options[i],b=options[j];
      const pairKey=[a.id,b.id].sort().join(':');
      if(this.blockedPairs.has(pairKey))continue;
      // The coordinator alone holds precise GPS and private moods. It computes two
      // coarse compatibility flags; agents never receive each other's raw profile.
      const meters=a.coords&&b.coords?distanceMeters(a.coords,b.coords):null;
      const proximityOK=meters===null?a.area.toLowerCase()===b.area.toLowerCase():meters<=MAX_RADIUS_METERS;
      const context={meters,proximityOK,vibeOK:activity=>vibeCompatible(a.vibe,b.vibe,activity)};
      const agentA=new PersonalAgent(a),agentB=new PersonalAgent(b);
      const packetA=agentA.proposalPacket(),packetB=agentB.proposalPacket();
      const ab=agentA.evaluate(packetB,context,now);
      const ba=agentB.evaluate(packetA,context,now);
      if(!ab||!ba || ab.negotiatedActivity!==ba.negotiatedActivity)continue;
      const score=Math.min(ab.score,ba.score);
      if(!best || score>best.score)best={a,b,shared:ab.shared,overlap:ab.overlap,meters,activity:ab.negotiatedActivity,score};
    }
    if(!best)return;
    const id=crypto.randomBytes(12).toString('hex');
    const p={id,a:best.a.id,b:best.b.id,state:'pending',accepts:new Set(),createdAt:now,
      expiresAt:Math.min(now+10*60000,best.a.until,best.b.until),shared:best.shared,activity:best.activity,overlap:best.overlap,meters:best.meters};
    this.proposals.set(id,p);
    this.events.push({event:'agent-a-requested',proposal:id,time:now,fields:['acceptable activities','opt-in interests','availability window']});
    this.events.push({event:'agent-b-checked-constraints',proposal:id,time:now,result:'compatible',privateChecks:['mood compatible','proximity compatible']});
    this.events.push({event:'both-agents-await-student-approval',proposal:id,time:now});
  }
  _proposalFor(token){return [...this.proposals.values()].find(p=>(p.a===token||p.b===token) && p.state!=='rejected')||null;}
  status(token){
    this._cleanup();const p=this._get(token);const pr=this._proposalFor(token);
    const base={name:p.name,active:true,minutesLeft:Math.max(0,Math.floor((p.until-this.now())/60000)),area:p.area,
      activity:p.activity,vibe:p.vibe,oneTimeLocationShared:p.gpsConsent,
      message:'Your agent is looking for someone who also opted in. Nothing is shared yet.'};
    if(!pr){this._findMatches();const nxt=this._proposalFor(token);if(!nxt)return base;return this._statusWithProposal(base,nxt,token);}
    return this._statusWithProposal(base,pr,token);
  }
  _statusWithProposal(base,pr,token){
    const accepted=pr.accepts.has(token);
    if(pr.state==='confirmed') {
      const other=this.people.get(pr.a===token?pr.b:pr.a);
      return {...base,state:'confirmed',match:{name:other.name,activity:pr.activity,sharedInterests:pr.shared,overlapMinutes:pr.overlap,location:POINT},message:'Both students said yes. Meet only if you still feel comfortable; you can leave anytime.'};
    }
    return {...base,state:'pending',proposalId:pr.id,accepted,
      proposal:{activity:pr.activity,sharedInterests:pr.shared,overlapMinutes:pr.overlap,proximity:pr.meters===null?'same stated campus area':`within ${MAX_RADIUS_METERS} meters (checked privately)`},
      message:accepted?'You said yes. Waiting for the other student to decide.':'Both agents found a compatible opt-in student. Do you approve this introduction?'};
  }
  decide(token,accept){
    this._cleanup();this._get(token);
    const p=this._proposalFor(token);if(!p||p.state!=='pending')throw error('No pending introduction.');
    if(typeof accept!=='boolean')throw error('Answer true or false.');
    if(!accept){p.state='rejected';this.blockedPairs.add([p.a,p.b].sort().join(':'));this.events.push({event:'student-declined',proposal:p.id});return {state:'declined',message:'No introduction made. Your decision stays private.'};}
    p.accepts.add(token);this.events.push({event:'student-approved',proposal:p.id,agent:token.slice(0,5)});
    if(p.accepts.size===2){p.state='confirmed';this.events.push({event:'mutual-consent-met',proposal:p.id});}
    return this.status(token);
  }
  stop(token){
    this._get(token);this.people.delete(token);
    for(const [id,p]of this.proposals)if(p.a===token||p.b===token)this.proposals.delete(id);
    this.events.push({event:'session-stopped-and-deleted',agent:token.slice(0,5)});
    return {state:'stopped',message:'Matching stopped. Your temporary profile and GPS data were cleared.'};
  }
  debugTrace(){return this.events.slice(-15);}
}
module.exports={MeetupEngine,PersonalAgent,distanceMeters,validCoords,MIN_OVERLAP_MINUTES,MAX_RADIUS_METERS};
