export function localToday(now=new Date()) {
 return [now.getFullYear(),String(now.getMonth()+1).padStart(2,'0'),String(now.getDate()).padStart(2,'0')].join('-');
}
export function pointFromURL(params) {
 if(!params.has('lat')||!params.has('lon'))return null;
 if(!params.get('lat').trim()||!params.get('lon').trim())return null;
 const lat=Number(params.get('lat')),lon=Number(params.get('lon'));
 return Number.isFinite(lat)&&Number.isFinite(lon)&&Math.abs(lat)<=90&&Math.abs(lon)<=180?[lat,lon]:null;
}
