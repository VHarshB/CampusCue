/** Optional Discord DM integration: two separate personal agents coordinated in one process.
 * Start with: npm install && node --env-file=.env src/discord.js
 */
const crypto=require('node:crypto');
const {MeetupEngine}=require('./engine');
const {createServer}=require('./server');
const {Client,Events,GatewayIntentBits,Partials,ChannelType}=require('discord.js');
const token=process.env.DISCORD_BOT_TOKEN;
if(!token){console.error('Set DISCORD_BOT_TOKEN in your local .env file.');process.exit(1);}
const engine=new MeetupEngine();const gpsLinks=new Map();
const users=new Map();const last=new Map();
const bot=new Client({intents:[GatewayIntentBits.Guilds,GatewayIntentBits.DirectMessages,GatewayIntentBits.MessageContent],partials:[Partials.Channel]});
const HELP=`**CampusCue Connect — Track 2**\nSend me a DM:\n\`!cue join 45 | social | coffee | music, books | Palm Walk | walk\`\nFields: minutes | mood | main activity | interests | general area | optional alternate activities.\n\`!cue status\`, \`!cue yes\`, \`!cue no\`, \`!cue stop\`, \`!cue gps\` (one-time optional GPS).\nBy sending join you explicitly opt in to short-lived agent matching. Your exact GPS and name are never shown to anyone before both people approve.`;
async function reply(message,s){return message.reply({content:String(s).slice(0,1800)});}
async function notify(id,text){try{const u=await bot.users.fetch(id);await u.send(text);}catch(e){console.error('Could not send DM notification',id,e.message);}}
function messageFor(s){
  if(s.state==='confirmed')return `✅ **Mutual YES!** You've matched with **${s.match.name}** for **${s.match.activity}**. Suggested public meeting point: **${s.match.location.name}** (${s.match.location.address}).\n${s.match.location.map}\n${s.match.location.note}`;
  if(s.state==='pending')return `💙 Your personal agent and another student's agent agree on **${s.proposal.activity}**! Shared interests: **${s.proposal.sharedInterests.join(', ')}**; common time: **${s.proposal.overlapMinutes} min**. ${s.proposal.proximity}.\n${s.accepted?'You approved. Waiting privately for the other student.':'Reply `!cue yes` to approve the introduction or `!cue no` to decline.'}\nYour name and exact GPS stay private until both say yes.`;
  return `Looking for another opted-in student. Your time window: ${s.minutesLeft} minutes. No identity or location has been shared with anyone.`;
}
async function broadcastChanges(){
  for(const [id,t] of users){
    let status;try{status=engine.status(t);}catch{users.delete(id);last.delete(id);continue;}
    const state=[status.state||'waiting',status.proposalId||'',status.accepted?'yes':'no',status.match?.name||''].join('|');
    if(last.get(id)!==state){last.set(id,state);if(status.state==='pending'||status.state==='confirmed')await notify(id,messageFor(status));}
  }
}
bot.on(Events.MessageCreate,async message=>{
  if(message.author.bot || message.channel.type!==ChannelType.DM)return;
  const s=message.content.trim();if(!s.toLowerCase().startsWith('!cue'))return;
  const id=message.author.id;
  const parts=s.split(/\s+/);const cmd=(parts[1]||'help').toLowerCase();
  try{
    if(cmd==='help')return reply(message,HELP);
    if(cmd==='join'){
      const fields=s.replace(/^!cue\s+join\s*/i,'').split('|').map(s=>s.trim());
      if(fields.length<5)return reply(message,`Use: \`!cue join 45 | social | coffee | music, books | Palm Walk | walk\`\nJoining explicitly opts you in for the selected time window.`);
      if(users.has(id)){try{engine.stop(users.get(id));}catch{}}
      const st=engine.join({name:message.author.globalName||message.author.username,minutes:Number(fields[0]),vibe:fields[1],activity:fields[2],interests:fields[3],area:fields[4],alternatives:fields[5]||'',consent:true});
      users.set(id,st.token);last.delete(id);
      await reply(message,`You're opted in for **${st.minutesLeft} minutes**. My agent will only look for students who opted in too. Use \`!cue stop\` anytime. No continuous GPS tracking.`);
      await broadcastChanges();return;
    }
    if(cmd==='stop'){if(users.has(id)){engine.stop(users.get(id));users.delete(id);last.delete(id);}return reply(message,'Matching stopped; temporary session and exact GPS data cleared.');}
    const t=users.get(id);if(!t)return reply(message,'Start with `!cue join 45 | social | coffee | music, books | Palm Walk`.');
    if(cmd==='status')return reply(message,messageFor(engine.status(t)));
    if(cmd==='yes'||cmd==='no'){
      const out=engine.decide(t,cmd==='yes');await reply(message,out.state==='declined'?'Declined privately. No introduction was made.':out.state==='confirmed'?'You both approved! 💙':'Your approval is saved. Waiting for their answer.');
      await broadcastChanges();return;
    }
    if(cmd==='gps'){
      const base=String(process.env.PUBLIC_BASE_URL||'').replace(/\/$/,'');
      if(!base.startsWith('https://'))return reply(message,'GPS sharing needs a temporary HTTPS URL to this demo server. You can still match using the stated campus area without GPS.');
      const linkToken=crypto.randomBytes(24).toString('hex');gpsLinks.set(linkToken,{studentToken:t,expires:Date.now()+5*60000});
      return reply(message,`Only if you choose: share a **one-time location** using this 5-minute consent link. Your exact coordinates never go to the other student.\n${base}/gps?t=${linkToken}`);
    }
    return reply(message,HELP);
  }catch(e){return reply(message,`Couldn't do that: ${e.message}`);}
});
bot.once(Events.ClientReady,client=>console.log(`CampusCue Connect Discord ready as ${client.user.tag}`));
bot.login(token);
const port=Number(process.env.PORT)||3000;
createServer(engine,gpsLinks).listen(port,'127.0.0.1',()=>console.log(`Consent web demo at http://127.0.0.1:${port}`));
setInterval(()=>{broadcastChanges().catch(console.error);for(const [id,link]of gpsLinks)if(link.expires<Date.now())gpsLinks.delete(id);},3000);
