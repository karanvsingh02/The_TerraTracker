const day=86400000;
const iso=value=>new Date(value).toISOString().slice(0,10);
// Select only published timestamps, including gaps and multi-day/month steps.
export function chooseMapDate(variable, requested) {
 if(variable.availableDates?.length){const target=Date.parse(requested);return variable.availableDates.reduce((best,candidate)=>Math.abs(Date.parse(candidate)-target)<Math.abs(Date.parse(best)-target)?candidate:best);}
 const parts=(variable.coverage||'').split(',').filter(Boolean);
 if(!parts.length)return variable.static?null:requested;
 const target=Date.parse(requested);let best=null,distance=Infinity;
 for(const part of parts){
  const [first,last=first,step='P1D']=part.split('/');
  const start=Date.parse(first),end=Date.parse(last);
  if(!Number.isFinite(start)||!Number.isFinite(end)||end<start)continue;
  const timed=/^PT(\d+)([MH])$/.exec(step);
  if(timed){
   const interval=Number(timed[1])*(timed[2]==='H'?3600000:60000);
   const n=Math.max(0,Math.min(Math.floor((end-start)/interval),Math.round((target-start)/interval)));
   const candidate=start+n*interval,d=Math.abs(candidate-target);
   if(d<distance){best=candidate;distance=d;}
   continue;
  }
  const match=/^P(\d+)([DMY])$/.exec(step);if(!match)continue;
  const stride=Number(match[1]),kind=match[2];let candidates=[];
  if(kind==='D'){
   const n=Math.max(0,Math.min(Math.floor((end-start)/(day*stride)),Math.round((target-start)/(day*stride))));
   candidates=[start+n*stride*day];
  }else{
   const from=new Date(start),to=new Date(target);
   const count=kind==='M'?(to.getUTCFullYear()-from.getUTCFullYear())*12+to.getUTCMonth()-from.getUTCMonth():to.getUTCFullYear()-from.getUTCFullYear();
   const index=Math.max(0,Math.floor(count/stride));
   for(const n of [Math.max(0,index-1),index,index+1]){
    const candidate=new Date(start);
    if(kind==='M')candidate.setUTCMonth(from.getUTCMonth()+n*stride);else candidate.setUTCFullYear(from.getUTCFullYear()+n*stride);
    if(candidate.getTime()<=end)candidates.push(candidate.getTime());
   }
   // When requested date is far beyond this interval, its last aligned period wins.
   const finish=new Date(end);const total=kind==='M'?(finish.getUTCFullYear()-from.getUTCFullYear())*12+finish.getUTCMonth()-from.getUTCMonth():finish.getUTCFullYear()-from.getUTCFullYear();
   const final=new Date(start);if(kind==='M')final.setUTCMonth(from.getUTCMonth()+Math.floor(total/stride)*stride);else final.setUTCFullYear(from.getUTCFullYear()+Math.floor(total/stride)*stride);candidates.push(final.getTime());
  }
  for(const candidate of candidates){const d=Math.abs(candidate-target);if(d<distance){best=candidate;distance=d;}}
 }
 return best===null?(variable.static?null:requested):(/\/PT/.test(variable.coverage)?new Date(best).toISOString().replace('.000Z','Z'):iso(best));
}
