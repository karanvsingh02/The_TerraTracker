import {chooseMapDate} from './map-dates.js';

// Calendar steps stay anchored to the start day (Jan 31 → Feb 29 → Mar 31).
export function timelapseDates(start,end,resolution,variable) {
 const first=new Date(start+'T00:00:00Z'),last=new Date(end+'T00:00:00Z');
 if(!Number.isFinite(+first)||!Number.isFinite(+last)||first>last)throw Error('Choose a valid investigation date range.');
 if(variable.static||(!variable.layer&&!variable.tiles))return [];
 const native=variable.dataResolution||'daily';
 const interval=resolution==='native'?native:resolution;
 const monthly=interval==='monthly',annual=interval==='annual';
 const stride=/^(\d+)-day$/.exec(interval);
 const dates=[],seen=new Set();
 function add(day){
  const frame=chooseMapDate(variable,day);
  if(!frame)return;
  const calendar=frame.slice(0,10);
  // Never substitute imagery outside the user's investigation window.
  if(calendar<start||calendar>end||seen.has(frame))return;
  seen.add(frame);dates.push(frame);
 }
 for(let index=0;index<20000;index++){
  let date;
  if(monthly||annual){
   date=new Date(Date.UTC(first.getUTCFullYear()+(annual?index:0),first.getUTCMonth()+(monthly?index:0),1));
   const days=new Date(Date.UTC(date.getUTCFullYear(),date.getUTCMonth()+1,0)).getUTCDate();
   date.setUTCDate(Math.min(first.getUTCDate(),days));
  }else date=new Date(+first+index*(stride?Number(stride[1]):1)*86400000);
  if(date>last)break;
  add(date.toISOString().slice(0,10));
  if(index===19999)throw Error('This timelapse is too long. Choose a shorter investigation period.');
 }
 add(end); // Include the final partial period, then hold the final available frame.
 return dates.sort((a,b)=>Date.parse(a)-Date.parse(b));
}

export function playbackDelay(milliseconds,signal){
 return new Promise(resolve=>{
  if(signal.aborted){resolve();return;}
  const finish=()=>{clearTimeout(timer);signal.removeEventListener('abort',finish);resolve();};
  const timer=setTimeout(finish,milliseconds);signal.addEventListener('abort',finish,{once:true});
 });
}

export function createTimelapse({button,settings,showFrame,notify,wait=playbackDelay,delay=1500}){
 let current=null;
 function refresh(){
  const {start,end,variable}=settings();
  button.disabled=!start||!end||start>end||variable.static||(!variable.layer&&!variable.tiles);
  button.title=button.disabled?'Timelapse requires dated map imagery and a valid investigation period.':'Play the investigation period at the selected interval; each frame stays visible for at least 1.5 seconds.';
 }
 function stop(){current?.abort();current=null;button.textContent='Play timelapse ▷';button.setAttribute('aria-pressed','false');refresh();}
 async function play(){
  if(current){stop();notify('Timelapse stopped at the displayed map date.');return;}
  let dates;
  try{const query=settings();dates=timelapseDates(query.start,query.end,query.resolution,query.variable);}
  catch(error){notify(error.message,true);return;}
  if(!dates.length){notify('No published map dates fall within this investigation period. Choose another period.',true);return;}
  const run=new AbortController();current=run;
  button.textContent='Stop timelapse ■';button.setAttribute('aria-pressed','true');
  try{
   for(let index=0;index<dates.length;index++){
    if(run.signal.aborted)return;
    notify('Timelapse · '+dates[index].slice(0,10)+' · '+(index+1)+' / '+dates.length);
    const loaded=await showFrame(dates[index],run.signal);
    if(run.signal.aborted)return;
    if(loaded===false)throw Error('Timelapse stopped because this map frame could not load. Retry playback or choose another period.');
    if(index<dates.length-1)await wait(delay,run.signal);
   }
   if(!run.signal.aborted)notify('Timelapse finished · '+dates.at(-1).slice(0,10)+'. The map will stay on this date.');
  }catch(error){if(!run.signal.aborted)notify(error.message,true);}
  finally{if(current===run)stop();}
 }
 button.addEventListener('click',play);refresh();
 return {stop,refresh};
}
