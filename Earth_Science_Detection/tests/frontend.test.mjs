import test from 'node:test';
import assert from 'node:assert/strict';
import {apiBase, getObservations} from '../frontend/js/api.js';
import {systems} from '../frontend/js/catalog.js';
import {createMap} from '../frontend/js/map.js';

test('local previews use the Python API rather than their HTML server', async () => {
 assert.equal(apiBase({hostname:'127.0.0.1',port:'5500'}),'http://127.0.0.1:8000');
 assert.equal(apiBase({hostname:'localhost',port:'63342'}),'http://127.0.0.1:8000');
 assert.equal(apiBase({hostname:'127.0.0.1',port:'8000'}),'');
 assert.equal(apiBase({hostname:'example.com',port:''}),'');
 globalThis.location={hostname:'localhost',port:'5500'};
 let requested;
 globalThis.fetch=async url=>{requested=url;return Response.json({data:[{date:'2024-01-01',value:12}]});};
 await getObservations({variable:'T2M'});
 assert.match(requested,/^http:\/\/127\.0\.0\.1:8000\/api\/observations\/point\?/);
});

test('HTML errors and validation responses become readable errors', async () => {
 globalThis.fetch=async()=>new Response('<!DOCTYPE html>',{headers:{'content-type':'text/html'}});
 await assert.rejects(getObservations({}),/API returned a page/);
 globalThis.fetch=async()=>Response.json({detail:[{loc:['query','start'],msg:'Invalid date'}]},{status:422});
 await assert.rejects(getObservations({}),/start: Invalid date/);
});

test('dropdown catalogs contain exactly the requested variables', () => {
 const expected={
 atmosphere:['Air temperature','Atmospheric pressure','Precipitation','Water vapor','Total-column ozone','Carbon monoxide','Methane','Solar radiation'],
 geosphere:['Surface elevation','Surface soil moisture','Ground displacement','Soil composition','Surface albedo','Soil temperature','Root-zone soil moisture'],
 cryosphere:['Sea ice concentration','Snow water equivalent','Freeze/thaw state','Glacier mass anomaly','Glacier velocity','Snow cover','Ice surface temperature'],
 biosphere:['Land surface temperature','Vegetation index (NDVI)','Gross primary productivity','Biomass','Land cover','Fire intensity'],
 hydrosphere:['Sea surface temperature','Sea surface salinity','Sea-level anomaly','Eastward geostrophic current','Sea surface temperature anomaly','Land evaporation','Groundwater storage anomaly']};
 for(const [id,names] of Object.entries(expected)){
  assert.deepEqual(systems[id].variables.map(v=>v.name),names);
  assert.equal(new Set(systems[id].variables.map(v=>v.id)).size,names.length);
 }
});

test('switching variables replaces the science layer and clears unsupported layers', async () => {
 const message={textContent:''};
 globalThis.document={querySelector:()=>message};
 let instance;
 class Map {
  constructor(){instance=this;this.layers={};this.sources={};}
  on(event,callback){if(event==='load')queueMicrotask(callback);}
  once(){}
  getCanvas(){return {setAttribute(){}};}
  getLayer(id){return this.layers[id];} getSource(id){return this.sources[id];}
  addSource(id,source){this.sources[id]=source;} addLayer(layer){this.layers[layer.id]=layer;}
  removeLayer(id){delete this.layers[id];} removeSource(id){delete this.sources[id];}
 }
 globalThis.window={maplibregl:{Map}};
 const map=createMap(()=>{});
 await map.setSystem(systems.atmosphere.variables[0],'2024-07-01');
 assert.match(Object.values(instance.sources)[0].tiles[0],/MERRA2_2m_Air_Temperature/);
 const originalSource=Object.keys(instance.sources);
 await map.setSystem(systems.atmosphere.variables[0],'2024-07-01');
 assert.deepEqual(Object.keys(instance.sources),originalSource,'Unchanged availability must not rebuild the map');
 await map.setSystem(systems.atmosphere.variables[0],'2024-07-01',{force:true});
 assert.notDeepEqual(Object.keys(instance.sources),originalSource,'Explicit retry must still reload the source');
 await map.setSystem(systems.atmosphere.variables[2],'2024-07-01');
 assert.match(Object.values(instance.sources)[0].tiles[0],/IMERG_Precipitation_Rate/);
 await map.setSystem({id:'TEST_MISSING',name:'Unavailable test',layer:null},'2024-07-01');
 assert.equal(Object.keys(instance.sources).length,0);
 assert.match(message.textContent,/not available in this version/);
});

import {chooseMapDate} from '../frontend/js/map-dates.js';
import {localToday,pointFromURL} from '../frontend/js/view-state.js';
test('default imagery date uses the local calendar and URL points restore safely',()=>{
 assert.equal(localToday(new Date(2026,10,15,23,59)),'2026-11-15');
 assert.deepEqual(pointFromURL(new URLSearchParams('lat=0&lon=-95.37')),[0,-95.37]);
 assert.equal(pointFromURL(new URLSearchParams('lat=91&lon=0')),null);
 assert.equal(pointFromURL(new URLSearchParams('lat=NaN&lon=0')),null);
 assert.equal(pointFromURL(new URLSearchParams()),null);
});
import {summarizeTrend,bindTrendDetails} from '../frontend/js/trend-summary.js';

test('map dates respect retired products, gaps and native observation steps',()=>{
 const vars=Object.values(systems).flatMap(s=>s.variables);
 const get=id=>vars.find(v=>v.id===id);
 assert.equal(chooseMapDate(get('ALLSKY_SFC_SW_DWN'),'2024-07-01'),'2021-07-01');
 assert.equal(chooseMapDate(get('SEA_LEVEL'),'2024-07-01'),'2024-07-01');
 assert.equal(chooseMapDate({coverage:'2015-04-01/2023-12-01/P1M,2025-01-01/2026-09-01/P1M'},'2024-07-01'),'2025-01-01');
 assert.equal(chooseMapDate(get('CURRENTS'),'2024-07-01'),'2024-07-01');
 assert.equal(chooseMapDate(get('BIOMASS'),'2024-07-01'),'2019-04-18');
 assert.equal(chooseMapDate({coverage:'2020-01-01/2020-01-16/P5D'},'2020-01-08'),'2020-01-06');
});

test('trend summary distinguishes increases, decreases, weak evidence and correlated readings',()=>{
 const base={slopePerDecade:.556,pValue:.02,unit:'C',lagOneResidualCorrelation:.054};
 assert.match(summarizeTrend(base,'Air temperature'),/increased.*0.556 C per decade/);
 assert.match(summarizeTrend({...base,slopePerDecade:-.5},'Air temperature'),/decreased/);
 assert.match(summarizeTrend({...base,pValue:.4},'Air temperature'),/not strong enough/);
 assert.match(summarizeTrend({...base,lagOneResidualCorrelation:.7},'Air temperature'),/less certain/);
 assert.match(summarizeTrend({...base,slopePerDecade:0},'Air temperature'),/no estimated overall change/);
});

test('show more button exposes details and changes to show less, then collapses again',()=>{
 const attributes={'aria-expanded':'false'};
 let click;
 const button={textContent:'Show more',addEventListener:(event,fn)=>{click=fn;},getAttribute:key=>attributes[key],setAttribute:(key,value)=>{attributes[key]=value;}};
 const details={hidden:true};
 bindTrendDetails(button,details);
 click();assert.equal(details.hidden,false);assert.equal(button.textContent,'Show less');assert.equal(attributes['aria-expanded'],'true');
 click();assert.equal(details.hidden,true);assert.equal(button.textContent,'Show more');
});

test('tile errors remain visible after the map becomes idle',async()=>{
 const message={textContent:''};let instance;
 globalThis.document={querySelector:()=>message};
 class Map{
  constructor(){instance=this;this.callbacks={};this.layers={};this.sources={};}
  on(event,callback){this.callbacks[event]=callback;if(event==='load')queueMicrotask(callback);}
  getCanvas(){return{setAttribute(){}};}getLayer(id){return this.layers[id];}getSource(id){return this.sources[id];}
  addSource(id,source){this.sources[id]=source;}addLayer(layer){this.layers[layer.id]=layer;}
  removeLayer(id){delete this.layers[id];}removeSource(id){delete this.sources[id];}
 }
 globalThis.window={maplibregl:{Map}};
 const map=createMap(()=>{});await map.setSystem(systems.atmosphere.variables[0],'2024-07-01');
 instance.callbacks.error({sourceId:Object.keys(instance.sources)[0]});
 assert.match(message.textContent,/failed to load/);
 instance.callbacks.idle();await Promise.resolve();assert.match(message.textContent,/failed to load/);
});

import {inspectCoverage} from '../frontend/js/map.js';
test('transparent images are identified as empty observations, not successful data',async()=>{
 globalThis.createImageBitmap=async()=>({width:1,height:1,close(){}});
 globalThis.fetch=async()=>new Response(new Blob(['image']),{headers:{'content-type':'image/png'}});
 let alpha=0;
 globalThis.document={createElement:()=>({getContext:()=>({drawImage(){},getImageData:()=>({data:new Uint8ClampedArray([0,0,0,alpha])})})})};
 const bounds={getWest:()=>-180,getEast:()=>180,getSouth:()=>-80,getNorth:()=>80};
 assert.equal(await inspectCoverage(systems.atmosphere.variables[0],'2024-07-01',bounds),false);
 alpha=255;assert.equal(await inspectCoverage(systems.atmosphere.variables[0],'2024-07-01',bounds),true);
 delete globalThis.createImageBitmap;
});

import {createPlaceLabeler} from '../frontend/js/place-label.js';
test('place labels cache repeated points and clear when a point is removed',async()=>{
 const element={textContent:'',title:''};let requests=0;
 const labeler=createPlaceLabeler(element,async()=>{requests++;return {label:'Atlantic Ocean',source:'Natural Earth',note:'Approximate reference'};});
 await labeler.select(26.76,-17.56);assert.equal(element.textContent,'Atlantic Ocean');
 await labeler.select(26.76,-17.56);assert.equal(requests,1);
 labeler.clear();assert.match(element.textContent,/Select anywhere/);
});

test('a slow old place lookup cannot overwrite a newly selected point',async()=>{
 const element={textContent:'',title:''};const pending=[];
 const labeler=createPlaceLabeler(element,()=>new Promise(resolve=>pending.push(resolve)));
 const first=labeler.select(26.76,-17.56),second=labeler.select(54,3);
 pending[1]({label:'North Sea',source:'Natural Earth',note:''});await second;
 pending[0]({label:'Atlantic Ocean',source:'Natural Earth',note:''});await first;
 assert.equal(element.textContent,'North Sea');
});

test('shorelines remain above scientific rasters without adding country boundaries',async()=>{
 const message={textContent:''};let instance,style;
 globalThis.document={querySelector:()=>message};
 class Map{
  constructor(options){instance=this;style=options.style;this.layers=Object.fromEntries(style.layers.map(l=>[l.id,l]));this.sources={...style.sources};}
  on(event,callback){if(event==='load')queueMicrotask(callback);}
  getCanvas(){return{setAttribute(){}};}getLayer(id){return this.layers[id];}getSource(id){return this.sources[id];}
  addSource(id,source){this.sources[id]=source;}addLayer(layer,before){this.layers[layer.id]=layer;this.insertBefore=before;}
  removeLayer(id){delete this.layers[id];}removeSource(id){delete this.sources[id];}
 }
 globalThis.window={maplibregl:{Map}};
 const map=createMap(()=>{});await map.setSystem(systems.atmosphere.variables[0],'2024-07-01');
 assert.equal(instance.insertBefore,'coastline-outline');
 assert.equal(style.layers.find(l=>l.id==='coastline-outline').type,'line');
 assert.match(style.sources.coastlines.data,/coastlines.geojson$/);
 assert.equal(style.layers.some(l=>/countr|political|admin/i.test(l.id)),false);
 await map.setSystem(systems.atmosphere.variables[1],'2024-07-01');
 assert.ok(instance.layers['coastline-outline']);assert.ok(instance.layers['lake-shore-outline']);
 await map.setSystem({id:'TEST_MISSING',name:'Unavailable test',layer:null},'2024-07-01');
});


test('fire maps use actual selectable detections rather than raster color values',()=>{
 const fire=systems.biosphere.variables.find(v=>v.id==='FIRE');
 assert.match(fire.points,/\/api\/maps\/fire\/\{date\}\.geojson$/);
 assert.equal(fire.point,true);
 assert.equal(fire.unit,'MW');
 assert.match(fire.description,/rolling seven days/);
});

test('every offered variable has a connected source and GFZ uses explicit published dates',()=>{
 for(const system of Object.values(systems))for(const v of system.variables)assert.ok(v.layer||v.tiles||v.image,v.name);
 const groundwater=systems.hydrosphere.variables.find(v=>v.id==='GROUNDWATER');
 assert.match(groundwater.image,/gravis/);
 assert.ok(groundwater.availableDates.length>200);
 assert.equal(groundwater.availableDates.some(d=>d.startsWith('2005-06')),false);
 assert.ok(groundwater.availableDates.includes(chooseMapDate(groundwater,'2024-07-01')));
 const mass=systems.cryosphere.variables.find(v=>v.id==='ICE_MASS');assert.equal(mass.gravisField,'glac');
});

import {chart} from '../frontend/js/chart.js';
test('timeline axes retain exact requested dates and never plot outside observations',()=>{
 const svg=chart([{date:'2023-12-01',value:9999},{date:'2024-01-15',value:10},{date:'2024-02-29',value:20},{date:'2024-03-01',value:-9999}],[],'°C',{start:'2024-01-10',end:'2024-02-29'});
 assert.match(svg,/data-range-start="2024-01-10"/);
 assert.match(svg,/data-range-end="2024-02-29"/);
 assert.match(svg,/data-observation-count="2"/);
 assert.doesNotMatch(svg,/>-?9999(?:\.0)?</);
 assert.match(svg,/class="range-start"[^>]*>2024-01-10</);
 assert.match(svg,/class="range-end"[^>]*>2024-02-29</);
});
test('an empty selected period still shows its requested dates without invented values',()=>{
 const svg=chart([],[],'m',{start:'2024-01-01',end:'2024-01-31'});
 assert.match(svg,/No observations returned/);assert.match(svg,/data-observation-count="0"/);
 assert.match(svg,/>2024-01-31</);
});
