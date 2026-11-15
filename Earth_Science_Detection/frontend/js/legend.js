// Keep provider labels upright. Vertical source keys are rendered as horizontal UI.
import {apiBase} from './api.js';
export function renderLegend(variable){
 const image=document.querySelector('#legend-image');
 const custom=document.querySelector('#legend-custom');
 image.onload=null;
 custom.replaceChildren();custom.hidden=true;
 image.hidden=!variable.legend;image.alt=variable.name+' color scale';
 if(variable.legendStops?.length){
  image.hidden=true;custom.hidden=false;
  const stops=variable.legendStops;
  const label=document.createElement('p');label.className='legend-unit';label.textContent=variable.legendUnit||variable.unit;custom.append(label);
  const ramp=document.createElement('div');ramp.className='legend-ramp';ramp.setAttribute('role','img');
  ramp.setAttribute('aria-label',(variable.legendTicks?variable.legendTicks.map(t=>t.label):stops.map(s=>s.label)).join(', ')+' '+variable.unit);
  if(variable.legendContinuous)ramp.style.background='linear-gradient(to right,'+stops.map(s=>s.color).join(',')+')';
  else for(const stop of stops){const swatch=document.createElement('span');swatch.style.backgroundColor=stop.color;swatch.title=stop.label+' '+variable.unit;ramp.append(swatch);}custom.append(ramp);
  const ticks=document.createElement('div');ticks.className='legend-ticks';
  if(variable.legendTicks){ticks.classList.add('legend-positioned-ticks');for(const entry of variable.legendTicks){const tick=document.createElement('span');tick.textContent=entry.label;tick.style.left=(entry.position*100)+'%';if(entry.position===0)tick.style.transform='none';ticks.append(tick);}}
  else for(const label of variable.legendTickLabels||[0,.25,.5,.75,1].map(fraction=>stops[Math.round(fraction*(stops.length-1))].label)){const tick=document.createElement('span');tick.textContent=label;ticks.append(tick);}custom.append(ticks);
 }else if(variable.legend){image.hidden=true;image.onload=()=>{if(custom.hidden)image.hidden=false;};image.src=variable.legend.startsWith('/api/')?apiBase()+variable.legend:variable.legend;}
}
