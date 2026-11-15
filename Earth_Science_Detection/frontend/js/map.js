import {apiBase} from './api.js';
// Provider imagery is visual context, never a numerical point measurement.
const shorelineURL=new URL('../data/coastlines.geojson',import.meta.url).href;
const lakeShoreURL=new URL('../data/lake-shores.geojson',import.meta.url).href;
const endpoint='https://gibs.earthdata.nasa.gov/wms/epsg3857/best/wms.cgi';
export function tileURL(variable,date){
 if(variable.tiles)return variable.tiles;
 return (variable.endpoint||endpoint)+((variable.endpoint||endpoint).includes('?')?'&':'?')+'SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&LAYERS='+encodeURIComponent(variable.layer)+'&STYLES='+encodeURIComponent(variable.style||'')+'&FORMAT=image/png&TRANSPARENT=TRUE&SRS=EPSG:3857&WIDTH=256&HEIGHT=256&BBOX={bbox-epsg-3857}'+(date?'&TIME='+date:'');
}
export async function inspectCoverage(variable,date,bounds,signal){
 if(variable.tiles||variable.image||variable.points||!globalThis.createImageBitmap)return null;
 let west=Math.max(-180,bounds.getWest()),east=Math.min(180,bounds.getEast());
 if(west>=east){west=-180;east=180;}
 const mercator=lat=>6378137*Math.log(Math.tan(Math.PI/4+lat*Math.PI/360));
 const bbox=[west*20037508.342789244/180,mercator(Math.max(-85,bounds.getSouth())),east*20037508.342789244/180,mercator(Math.min(85,bounds.getNorth()))].join(',');
 const url=(variable.endpoint||endpoint)+((variable.endpoint||endpoint).includes('?')?'&':'?')+new URLSearchParams({SERVICE:'WMS',VERSION:'1.1.1',REQUEST:'GetMap',LAYERS:variable.layer,STYLES:variable.style||'',FORMAT:'image/png',TRANSPARENT:'TRUE',SRS:'EPSG:3857',WIDTH:'400',HEIGHT:'240',BBOX:bbox,...(date?{TIME:date}:{})});
 const response=await fetch(url,{signal});
 if(!response.ok)throw Error('Map provider returned HTTP '+response.status);
 if(!(response.headers.get('content-type')||'').startsWith('image/'))throw Error('Map provider did not return an image');
 const bitmap=await createImageBitmap(await response.blob());
 try{
  const canvas=document.createElement('canvas');canvas.width=bitmap.width;canvas.height=bitmap.height;
  const context=canvas.getContext('2d',{willReadFrequently:true});if(!context)return null;
  context.drawImage(bitmap,0,0);const pixels=context.getImageData(0,0,canvas.width,canvas.height).data;
  for(let i=3;i<pixels.length;i+=4)if(pixels[i]>0)return true;
  return false;
 }finally{bitmap.close();}
}
export function createMap(onSelect){
 const message=document.querySelector('#map-message');
 let descriptionTimer=null;
 function showMessage(text, autoHide=false){
  clearTimeout(descriptionTimer);
  message.textContent=text;
  if(autoHide){descriptionTimer=setTimeout(()=>{message.textContent='';},6000);descriptionTimer.unref?.();}
 }

 if(!window.maplibregl){showMessage('Map library could not load. Coordinate entry is still available.');return null;}
 let map,marker,state=null,generation=0,probe=null,selectedPoint=null,firePopup=null;
 const ready=new Promise(resolve=>{
  const deadline=setTimeout(()=>{showMessage('The world map is taking too long to load. Check your connection and use Reload map.');resolve(false);},15000);deadline.unref?.();
  try{
   map=new window.maplibregl.Map({container:'earth-map',center:[0,15],zoom:1.1,minZoom:0,maxZoom:8,renderWorldCopies:false,style:{version:8,sources:{earth:{type:'raster',tiles:[tileURL({layer:'BlueMarble_ShadedRelief_Bathymetry'})],tileSize:256,attribution:'NASA GIBS / Earthdata'},coastlines:{type:'geojson',data:shorelineURL,attribution:'Coastlines: Natural Earth (public domain)'},'lake-shores':{type:'geojson',data:lakeShoreURL}},layers:[{id:'background',type:'background',paint:{'background-color':'#a8c0d1'}},{id:'earth',type:'raster',source:'earth'},{id:'coastline-outline',type:'line',source:'coastlines',paint:{'line-color':'#111111','line-opacity':.43,'line-width':['interpolate',['linear'],['zoom'],0,.45,4,.75,8,1.1]}},{id:'lake-shore-outline',type:'line',source:'lake-shores',paint:{'line-color':'#111111','line-opacity':.35,'line-width':['interpolate',['linear'],['zoom'],0,.3,4,.6,8,.9]}}]}});
   map.on('load',()=>{clearTimeout(deadline);resolve(true);});
   map.on('error',event=>{
    if(['coastlines','lake-shores'].includes(event.sourceId)){showMessage('Shoreline outlines could not load. Reload the map to retry.');return;}
    if(event.sourceId==='earth'){showMessage('The Earth basemap could not load. Check your connection and reload the map.');return;}
    if(state&&(!event.sourceId||event.sourceId===state.key)){state.failed=true;clearTimeout(state.deadline);showMessage(state.variable.name+' imagery failed to load. Try Reload map or another date.');}
   });
   map.on('click',e=>{
    if(state?.variable.points){const feature=map.queryRenderedFeatures(e.point,{layers:[state.key]})[0];if(!feature){showMessage('Choose a displayed fire detection to see its values and local detection history.',true);return;}const [lon,lat]=feature.geometry.coordinates;onSelect(lat,lon,{detectionId:feature.properties.detectionId});}
    else onSelect(e.lngLat.lat,((e.lngLat.lng+180)%360+360)%360-180);
   });
   map.on('mousemove',e=>{
    if(!state?.variable.points||!map.getLayer(state.key)){firePopup?.remove();return;}
    const feature=map.queryRenderedFeatures(e.point,{layers:[state.key]})[0];map.getCanvas().style.cursor=feature?'pointer':'crosshair';
    if(!feature){firePopup?.remove();return;}
    if(!firePopup)firePopup=new window.maplibregl.Popup({closeButton:false,closeOnClick:false});
    firePopup.setLngLat(feature.geometry.coordinates).setText(`${Number(feature.properties.frp).toFixed(2)} MW · ${feature.properties.timestamp} · click for detection history`).addTo(map);
   });
   map.on('idle',()=>checkView());
   map.on('moveend',()=>{if(state)state.checked=false;});
   map.getCanvas().setAttribute('aria-label','Interactive world map. Click to select a point, or enter coordinates in investigation settings.');
  }catch(error){clearTimeout(deadline);showMessage('Interactive map unavailable on this browser. Use coordinate entry to investigate.');resolve(false);}
 });
 async function checkView(){
  const current=state;
  if(!current||current.failed||current.checking||current.checked)return;
  current.checking=true;clearTimeout(current.deadline);probe?.abort();probe=new AbortController();
  const activeProbe=probe;const timeout=setTimeout(()=>activeProbe.abort(),15000);timeout.unref?.();
  try{
   const coverage=map.getBounds?await inspectCoverage(current.variable,current.date,map.getBounds(),activeProbe.signal):null;
   if(state!==current||current.failed)return;
   current.checked=true;
   showMessage(coverage===false?'No '+current.variable.name.toLowerCase()+' observations in this view for '+(current.date||'this composite')+'. Zoom out, pan to the product’s coverage area, or choose another date.':(current.variable.coverageNote||'Imagery loaded. Blank areas indicate no observations; they do not mean zero.'),coverage!==false);
  }catch(error){current.checked=true;if(state===current&&!current.failed)showMessage('Unable to verify map coverage. Some imagery may be missing. Try Reload map or another date.');}
  finally{clearTimeout(timeout);current.checking=false;}
 }
 return {
  async setSystem(variable,date,{force=false}={}){
   const signature=JSON.stringify([variable.id,variable.layer,variable.endpoint,variable.tiles,variable.image,variable.points,date]);
   if(!force&&state?.signature===signature)return;
   const id=++generation;probe?.abort();firePopup?.remove();if(state)clearTimeout(state.deadline);
   if(!await ready||id!==generation)return;
   const previous=state;state=null;
   if(variable.view&&!selectedPoint&&previous?.variable.id!==variable.id)map.flyTo?.({...variable.view,duration:600});
   if(previous){if(map.getLayer(previous.key))map.removeLayer(previous.key);if(map.getSource(previous.key))map.removeSource(previous.key);}
   if(!variable.layer&&!variable.tiles){showMessage(variable.name+' imagery is not available in this version. Showing shorelines and geographic context only.');return;}
   const key='science-'+id;state={key,signature,variable,date,failed:false,checked:false,checking:false};const current=state;
   showMessage('Loading '+variable.name.toLowerCase()+' imagery…');
   current.deadline=setTimeout(()=>{if(state===current&&!current.failed&&!current.checked){current.failed=true;showMessage('Map loading timed out. Check your connection, then use Reload map.');}},20000);current.deadline.unref?.();
   try{
    if(variable.points){
     map.addSource(key,{type:'geojson',data:apiBase()+variable.points.replace('{date}',date)});
     map.addLayer({id:key,type:'circle',source:key,paint:{'circle-color':['interpolate',['linear'],['get','frp'],0,'#ffed8a',10,'#fec44f',50,'#fe9929',100,'#ec7014',150,'#cc4c02'],'circle-radius':['interpolate',['linear'],['zoom'],0,2.5,4,4,8,7],'circle-stroke-color':'#7d2f15','circle-stroke-width':.4,'circle-opacity':.9}},'coastline-outline');
     return;
    }
    if(variable.image)map.addSource(key,{type:'image',url:apiBase()+variable.image.replace('{date}',date),coordinates:[[-180,85.0511287798],[180,85.0511287798],[180,-85.0511287798],[-180,-85.0511287798]]});
    else map.addSource(key,{type:'raster',tiles:[tileURL(variable,date)],tileSize:256,minzoom:variable.minzoom??0,maxzoom:variable.maxzoom??8,attribution:variable.provider});
    map.addLayer({id:key,type:'raster',source:key,paint:{'raster-opacity':.9,'raster-fade-duration':250}},'coastline-outline');
   }catch(error){clearTimeout(current.deadline);current.failed=true;showMessage('Unable to open '+variable.name.toLowerCase()+' imagery. Use Reload map to try again.');}
  },
  select(lat,lon){selectedPoint=[lat,lon];if(!map)return;map.stop?.();if(!marker){const el=document.createElement('div');el.innerHTML='<svg class="point-marker" viewBox="0 0 24 32"><path d="M22 11C22 20 12 30 12 30S2 20 2 11a10 10 0 1 1 20 0Z"/><circle cx="12" cy="11" r="3" fill="#f7ecd9" stroke="none"/></svg>';marker=new window.maplibregl.Marker({element:el,anchor:'bottom'});}marker.setLngLat([lon,lat]).addTo(map);map.flyTo({center:[lon,lat],zoom:Math.max(map.getZoom(),2),duration:window.matchMedia('(prefers-reduced-motion: reduce)').matches?0:900});},
  clear(){selectedPoint=null;marker?.remove();marker=null;},
  zoom(delta){if(map)map.zoomTo(map.getZoom()+delta,{duration:250});},
  home(){if(map)map.flyTo({center:[0,15],zoom:1.1,duration:600});}
 };
}
