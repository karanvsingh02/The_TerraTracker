import {getPlaceName} from './api.js';
// A separate request lifecycle prevents a slow old point from renaming a new one.
export function createPlaceLabeler(element, lookup=getPlaceName){
 const cache=new Map();let controller=null,pendingKey=null;
 function show(result){element.textContent=result.label;element.title=result.source+' · '+result.note;}
 return {
  async select(lat,lon){
   const key=lat.toFixed(4)+','+lon.toFixed(4);
   if(pendingKey===key)return;
   controller?.abort();controller=null;pendingKey=null;
   if(cache.has(key)){show(cache.get(key));return;}
   const request=new AbortController();controller=request;pendingKey=key;
   element.textContent='Finding place name…';element.title='';
   try{
    const result=await lookup(lat,lon,request.signal);
    if(controller!==request)return;
    if(cache.size>=256)cache.delete(cache.keys().next().value);
    cache.set(key,result);show(result);
   }catch(error){if(controller===request&&error.name!=='AbortError')element.textContent='Place name unavailable · select this point again to retry.';}
   finally{if(controller===request){controller=null;pendingKey=null;}}
  },
  clear(){controller?.abort();controller=null;pendingKey=null;element.textContent='Select anywhere on the map to investigate.';element.title='';}
 };
}
