const pending=new Map();
export function loadMapMetadata(url='https://gibs.earthdata.nasa.gov/wms/epsg3857/best/wms.cgi?SERVICE=WMS&REQUEST=GetCapabilities&VERSION=1.3.0'){
 if(!pending.has(url))pending.set(url,fetch(url,{signal:AbortSignal.timeout(15000)})
 .then(async response=>{if(!response.ok)throw Error('Map catalog unavailable');const xml=new DOMParser().parseFromString(await response.text(),'application/xml');if(xml.querySelector('parsererror'))throw Error('Invalid map catalog');const metadata={};for(const element of xml.getElementsByTagNameNS('*','Layer')){const direct=tag=>Array.from(element.children).find(c=>c.localName===tag);const name=direct('Name')?.textContent;if(!name)continue;const dimension=Array.from(element.children).find(c=>c.localName==='Dimension'&&c.getAttribute('name')==='time');metadata[name]={coverage:dimension?.textContent||''};}return metadata;}).catch(error=>{pending.delete(url);throw error;}));
 return pending.get(url);
}
