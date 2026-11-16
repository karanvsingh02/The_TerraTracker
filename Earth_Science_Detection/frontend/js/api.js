export function apiBase(location = globalThis.location) {
 const local = ['localhost', '127.0.0.1', '[::1]'].includes(location?.hostname);
 return local && location.port !== '8000' ? 'http://127.0.0.1:8000' : '';
}
export async function getObservations(selection, signal, onProgress=()=>{}) {
 let response;
 try {
  response = await fetch(apiBase() + '/api/observations/point?' + new URLSearchParams(selection), {
   signal, headers: {Accept: 'application/json'}
  });
 } catch (error) {
  if (error.name === 'AbortError') throw error;
  throw new Error('Cannot reach the analysis server. Start the Python app and open http://127.0.0.1:8000/atmosphere.');
 }
 const contentType = response.headers.get('content-type') || '';
 if (!contentType.includes('application/json')) {
  throw new Error('The analysis API returned a page instead of data. Check that the Python app is running on port 8000 and reload this page.');
 }
 let result;
 try { result = await response.json(); }
 catch { throw new Error('The analysis server returned invalid JSON. Please retry the request.'); }
 if (!response.ok) {
  const detail = Array.isArray(result.detail)
   ? result.detail.map(issue => `${issue.loc?.at(-1) || 'Input'}: ${issue.msg}`).join('; ')
   : result.detail;
  throw new Error(detail || 'Unable to retrieve observations.');
 }
 if (response.status===202) {
  const jobId=result.jobId;
  if(!/^[a-f0-9]{64}$/.test(jobId||''))throw Error('The extraction server returned an invalid task identifier.');
  while(result.status!=='done') {
   if(result.status==='error')throw Error(result.error||'The scientific provider could not complete this extraction.');
   const percentage=typeof result.progress==='number'?' '+Math.round(result.progress*100)+'%':'';
   const sstMessage=result.status==='processing'?'NASA is preparing your SST history'+percentage+(result.inputFiles?' ('+Number(result.inputFiles).toLocaleString()+' daily files)':'')+'. Available measurements appear while the full history loads.':result.status==='downloading'?'Downloading your SST history'+percentage+'. Available measurements are shown below.':'Retrieving SST observations…'+percentage;
   onProgress(selection.variable==='SST'?sstMessage:result.providerStatus==='pending'?'NASA has queued this extraction; processing has not started yet. Your point is saved. Retrying reconnects to the same request.':result.status==='processing'?'NASA is processing your observations. Your point is saved; no need to click Retrieve again.':('Retrieving scientific observations…'+(typeof result.progress==='number'?' '+Math.round(result.progress*100)+'%':'')),result.preview);
   await new Promise((resolve,reject)=>{
    const cancelled=()=>{clearTimeout(timer);reject(new DOMException('Aborted','AbortError'));};
    const timer=setTimeout(()=>{signal?.removeEventListener('abort',cancelled);resolve();},2000);
    if(signal?.aborted)cancelled();else signal?.addEventListener('abort',cancelled,{once:true});
   });
   const poll=await fetch(apiBase()+'/api/observations/jobs/'+jobId,{signal,headers:{Accept:'application/json'}});
   if(!poll.ok||!(poll.headers.get('content-type')||'').includes('application/json'))throw Error('Cannot check extraction progress. Retry to reconnect to the saved task.');
   result=await poll.json();
  }
  result=result.result;
 }
 if (!result || !Array.isArray(result.data) || !result.data.length) {
  throw new Error('The analysis server returned no observations for this selection.');
 }
 if(result.variable && result.variable!==selection.variable)throw new Error('The provider returned a different variable. These values were not displayed; retry your selected variable.');
 return result;
}
export function download(filename, content, type) {
 const url=URL.createObjectURL(new Blob([content],{type}));
 const a=Object.assign(document.createElement('a'),{href:url,download:filename});a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
export function csv(result) {
 const meta = ['# '+result.source, '# source: '+result.sourceUrl, '# fetched: '+result.fetchedAt, '# coordinates: '+result.latitude+', '+result.longitude];
 return [...meta,'date,value,unit,variable',...result.data.map(r=>[r.date,r.value ?? '',result.unit,result.variable].join(','))].join('\n');
}
export async function getPlaceName(latitude, longitude, signal) {
 const response=await fetch(apiBase()+'/api/places/reverse?'+new URLSearchParams({lat:latitude,lon:longitude}),{signal,headers:{Accept:'application/json'}});
 if(!response.ok||!(response.headers.get('content-type')||'').includes('application/json'))throw Error('Place lookup unavailable');
 const result=await response.json();if(!result.label)throw Error('No place name returned');return result;
}

export async function getGravisMetadata(field){
 const response=await fetch(apiBase()+'/api/maps/gravis/'+encodeURIComponent(field)+'/metadata');
 if(!response.ok)throw Error('Alternate provider metadata unavailable');
 return response.json();
}
