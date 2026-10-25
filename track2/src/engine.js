/** CampusCue Track 2: ONE independent matchmaking coordinator serving many Cubbie users.
 * Cubbie is the only chat interface. This service never messages students directly.
 * Hackathon prototype: temporary in-memory sessions, never for public production.
 */
'use strict';
const crypto = require('node:crypto');
const MAX_RADIUS_METERS = 1200;
const MIN_OVERLAP_MINUTES = 15;
const VIBES = new Set(['social', 'chill', 'adventurous', 'productive', 'low-key']);
const ACTIVITIES = new Set(['coffee', 'study', 'walk', 'chat', 'event']);
const MU = Object.freeze({name:'Memorial Union main entrance (public)', address:'301 E Orange St, Tempe, AZ', map:'https://www.asu.edu/map/interactive/?psCode=MU',note:'Meet outside in public. Check travel time to your next class.'});
const err=(message,status=400)=>Object.assign(new Error(message),{status});
function clean(v,max=60){return String(v??'').trim().replace(/[<>\r\n\u0000-\u001f]/g,'').slice(0,max);}
function list(v){return [...new Set((Array.isArray(v)?v:String(v??'').split(',')).map(s=>clean(s,25).toLowerCase()).filter(Boolean))].slice(0,6);}
function gpsValid(p){return p && Number.isFinite(p.lat)&&Number.isFinite(p.lon) && Math.abs(p.lat)<=90 && Math.abs(p.lon)<=180;}
function distanceMeters(a,b){const r=x=>x*Math.PI/180, dp=r(b.lat-a.lat),dl=r(b.lon-a.lon),p1=r(a.lat),p2=r(b.lat);const q=Math.sin(dp/2)**2+Math.cos(p1)*Math.cos(p2)*Math.sin(dl/2)**2;return 6371000*2*Math.atan2(Math.sqrt(q),Math.sqrt(1-q));}
function vibeOK(a,b,act){if(a===b)return true;const light=['social','chill','low-key'];if(['coffee','chat'].includes(act))return light.includes(a)&&light.includes(b);if(act==='study')return ['productive','low-key'].includes(a)&&['productive','low-key'].includes(b);if(['walk','event'].includes(act))return ['social','adventurous'].includes(a)&&['social','adventurous'].includes(b);return false;}
function meetingPoint(area){const a=area.toLowerCase();return /palm walk|hayden|tempe|memorial union|mu|tooker|noble/.test(a)?MU:{name:'Agree on a visible public meeting point on your campus',note:'Choose together only after both students approve. Never share your live location.'};}

class MatchmakingAgent {
  constructor(now=()=>Date.now()){this.now=now;this.sessions=new Map();this.proposals=new Map();this.declined=new Set();}
  get(token){const p=this.sessions.get(token);if(!p)throw err('Your matching session is missing or expired.',401);return p;}
  cleanup(){const n=this.now();for(const [id,p]of this.sessions)if(p.expires<=n)this.sessions.delete(id);for(const [id,p]of this.proposals)if(p.expires<=n||!this.sessions.has(p.a)||!this.sessions.has(p.b))this.proposals.delete(id);for(const k of this.declined)if(k.split(':').some(id=>!this.sessions.has(id)))this.declined.delete(k);}
  available(p){return ![...this.proposals.values()].some(x=>['pending','confirmed'].includes(x.state)&&(x.a===p.token||x.b===p.token));}
  register(input){
    this.cleanup();if(input?.consent!==true)throw err('Ask the student for permission before joining matchmaking.');
    const name=clean(input.name,30);if(!name)throw err('A display name is required.');
    const minutes=Number(input.minutes);if(!Number.isInteger(minutes)||minutes<15||minutes>120)throw err('Available time must be 15–120 minutes.');
    const vibe=clean(input.vibe).toLowerCase(),activity=clean(input.activity).toLowerCase();
    if(!VIBES.has(vibe)||!ACTIVITIES.has(activity))throw err('Invalid mood or activity.');
    const area=clean(input.area);if(!area)throw err('Ask the student for their general campus area.');
    const interests=list(input.interests);if(!interests.length)throw err('Ask for at least one interest.');
    // GPS is optional and separate: normal registration never accepts coordinates.
    if(input.coords || input.gpsConsent)throw err('Location needs separate one-time browser consent.');
    const n=this.now(),token=crypto.randomBytes(24).toString('hex');
    const alternatives=list(input.alternatives).filter(v=>ACTIVITIES.has(v));
    this.sessions.set(token,{token,name,vibe,activities:[...new Set([activity,...alternatives])],activity,area,interests,coords:null,gpsConsent:false,since:n,expires:n+minutes*60000});
    this.findMatches();return {token,...this.status(token)};
  }
  shareOneTimeLocation(token,coords,consent){this.cleanup();const p=this.get(token);if(consent!==true||!gpsValid(coords))throw err('One-time GPS sharing requires separate explicit permission.');p.coords={lat:coords.lat,lon:coords.lon};p.gpsConsent=true;this.findMatches();return this.status(token);}
  score(a,b,n){
    const key=[a.token,b.token].sort().join(':');if(this.declined.has(key))return null;
    const dist=a.coords&&b.coords?distanceMeters(a.coords,b.coords):null;
    const sameArea=a.area.toLowerCase()===b.area.toLowerCase();
    if(dist===null?!sameArea:dist>MAX_RADIUS_METERS)return null;
    const overlap=Math.floor((Math.min(a.expires,b.expires)-Math.max(n,a.since,b.since))/60000);
    if(overlap<MIN_OVERLAP_MINUTES)return null;
    const shared=a.interests.filter(x=>b.interests.includes(x));if(!shared.length)return null;
    const activity=a.activities.find(x=>b.activities.includes(x)&&vibeOK(a.vibe,b.vibe,x));if(!activity)return null;
    return {a:a.token,b:b.token,activity,overlap,shared,proximity:dist===null?'same opted-in campus area':`within ${MAX_RADIUS_METERS} m (checked privately)`,score:shared.length*25+overlap-(dist??0)/30,area:a.area};
  }
  findMatches(){
    this.cleanup();const n=this.now();const users=[...this.sessions.values()].filter(x=>this.available(x));
    while(true){let best=null;for(let i=0;i<users.length;i++)for(let j=i+1;j<users.length;j++){if(!this.available(users[i])||!this.available(users[j]))continue;const s=this.score(users[i],users[j],n);if(s&&(!best||s.score>best.score))best=s;}
      if(!best)break;const id=crypto.randomBytes(12).toString('hex');
      this.proposals.set(id,{...best,id,state:'pending',approved:new Set(),expires:Math.min(n+10*60000,this.get(best.a).expires,this.get(best.b).expires)});
    }
  }
  proposal(token){return [...this.proposals.values()].find(p=>p.state!=='declined'&&(p.a===token||p.b===token));}
  status(token){this.cleanup();const p=this.get(token);if(!this.proposal(token))this.findMatches();const match=this.proposal(token);
    const base={active:true,mood:p.vibe,activity:p.activity,area:p.area,minutesLeft:Math.max(0,Math.ceil((p.expires-this.now())/60000)),gpsSharedOnce:p.gpsConsent};
    if(!match)return {...base,state:'searching',message:'Looking for another student who also opted in. Check again shortly.'};
    if(match.state==='confirmed')return {...base,state:'confirmed',match:{name:this.get(match.a===token?match.b:match.a).name,activity:match.activity,sharedInterests:match.shared,overlapMinutes:match.overlap,location:meetingPoint(match.area)},message:'Both students approved. Agree on a public spot and leave for class on time.'};
    const yes=match.approved.has(token);return {...base,state:yes?'waiting':'pending',proposal:{activity:match.activity,sharedInterests:match.shared,overlapMinutes:match.overlap,proximity:match.proximity},message:yes?'You approved. Waiting for the other student.':'A compatible student opted in. Would you like to be introduced? (yes/no)'};
  }
  decide(token,yes){this.cleanup();this.get(token);const p=this.proposal(token);if(!p||p.state!=='pending')throw err('No pending introduction.');if(typeof yes!=='boolean')throw err('Approval must be yes or no.');
    if(!yes){p.state='declined';this.declined.add([p.a,p.b].sort().join(':'));this.proposals.delete(p.id);return {state:'declined',message:'No introduction happened. Your answer was not shared.'};}
    p.approved.add(token);if(p.approved.size===2)p.state='confirmed';return this.status(token);
  }
  stop(token){this.cleanup();this.get(token);this.sessions.delete(token);for(const [id,p]of this.proposals)if(p.a===token||p.b===token)this.proposals.delete(id);this.cleanup();return {state:'stopped',message:'Matchmaking stopped. Session and shared GPS deleted.'};}
}
module.exports={MatchmakingAgent,MeetupEngine:MatchmakingAgent,distanceMeters,MAX_RADIUS_METERS};
