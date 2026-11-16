import {apiBase} from './api.js';

export function bindPlaceSearch({onSelect}) {
 const toggle=document.querySelector('#place-search-toggle');
 const form=document.querySelector('#place-search');
 const input=form.querySelector('input');
 const message=document.querySelector('#place-search-status');
 const results=document.querySelector('#place-search-results');
 let controller=null;
 function close(){controller?.abort();controller=null;form.hidden=true;toggle.setAttribute('aria-expanded','false');toggle.focus();}
 toggle.addEventListener('click',()=>{
  if(!form.hidden){close();return;}
  form.hidden=false;toggle.setAttribute('aria-expanded','true');input.focus();input.select();
 });
 form.addEventListener('keydown',event=>{if(event.key==='Escape'){event.preventDefault();close();}});
 input.addEventListener('input',()=>{controller?.abort();controller=null;results.replaceChildren();message.textContent='';});
 form.addEventListener('submit',async event=>{
  event.preventDefault();if(!form.reportValidity())return;
  const q=input.value.trim();if(q.length<2){message.textContent='Enter at least two characters.';return;}
  controller?.abort();const request=new AbortController();controller=request;
  results.replaceChildren();message.textContent='Searching places…';
  try{
   const response=await fetch(apiBase()+'/api/places/search?'+new URLSearchParams({q}),{signal:request.signal,headers:{Accept:'application/json'}});
   if(!response.ok||!(response.headers.get('content-type')||'').includes('application/json'))throw Error('Search is unavailable. Check that the Python app is running, then try again.');
   const data=await response.json();if(controller!==request)return;
   const places=(data.results||[]).filter(p=>typeof p.label==='string'&&Number.isFinite(p.lat)&&Number.isFinite(p.lon)&&Math.abs(p.lat)<=90&&Math.abs(p.lon)<=180);
   message.textContent=places.length?'Choose a result to move the map.':'No matching places. Try the city name with its country, or select a point on the map.';
   for(const place of places){
    const item=document.createElement('li'),button=document.createElement('button');
    button.type='button';button.textContent=place.label;
    button.addEventListener('click',()=>{close();onSelect(place);});
    item.append(button);results.append(item);
   }
  }catch(error){if(controller===request&&error.name!=='AbortError')message.textContent=error.message;}
 });
}
