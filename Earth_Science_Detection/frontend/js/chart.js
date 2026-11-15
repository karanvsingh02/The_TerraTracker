const escape=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function chart(series, fitted=[], unit='', range={}) {
 const day=86400000,w=960,h=300,p=55;
 const ordered=series.filter(r=>Number.isFinite(Date.parse(r.date))).sort((a,b)=>Date.parse(a.date)-Date.parse(b.date));
 const start=range.start||ordered[0]?.date,end=range.end||ordered.at(-1)?.date;
 const xmin=Date.parse(start),xmax=Date.parse(end)+(range.end?day-1:0);
 if(!Number.isFinite(xmin)||!Number.isFinite(xmax)||xmax<xmin)return '<div class="empty">Choose a valid date range.</div>';
 const within=r=>Date.parse(r.date)>=xmin&&Date.parse(r.date)<=xmax;
 const shown=ordered.filter(within),valid=shown.filter(r=>Number.isFinite(r.value));
 const header=`<svg id="timeseries" viewBox="0 0 ${w} ${h}" data-range-start="${escape(start)}" data-range-end="${escape(end)}" data-observation-count="${valid.length}" role="img" aria-label="Time series in ${escape(unit)}, ${escape(start)} to ${escape(end)}"><title>Observations within the requested dates</title>`;
 const labels=`<text class="range-start" x="${p}" y="${h-12}">${escape(start)}</text><text class="range-end" x="${w-p}" y="${h-12}" text-anchor="end">${escape(end)}</text><text x="${p}" y="20">${escape(unit)}</text>`;
 if(!valid.length)return header+`<text x="${w/2}" y="${h/2}" text-anchor="middle">No observations returned for this period</text>`+labels+'</svg>';
 let lo=Infinity,hi=-Infinity;for(const r of valid){lo=Math.min(lo,r.value);hi=Math.max(hi,r.value);}const pad=(hi-lo)*.12||1;lo-=pad;hi+=pad;
 const x=d=>p+(Date.parse(d)-xmin)/(xmax-xmin||1)*(w-p*2),y=v=>h-p-(v-lo)/(hi-lo)*(h-p*1.6);
 const path=rows=>{let pen=false;return rows.map(r=>{if(!Number.isFinite(r.value)){pen=false;return '';}const command=pen?'L':'M';pen=true;return `${command}${x(r.date).toFixed(2)},${y(r.value).toFixed(2)}`;}).join(' ');};
 const line=fitted.filter(within).sort((a,b)=>Date.parse(a.date)-Date.parse(b.date));
 return header+[0,1,2,3,4].map(i=>{const v=lo+(hi-lo)*i/4;return `<path d="M${p} ${y(v)}H${w-p}" class="gridline"/><text x="${p-10}" y="${y(v)+4}" text-anchor="end">${v.toFixed(1)}</text>`;}).join('')+`<path d="${path(shown)}" fill="none" stroke="#795b60" stroke-width="2"/>`+(valid.length===1?`<circle cx="${x(valid[0].date)}" cy="${y(valid[0].value)}" r="4" fill="#795b60"/>`:'')+(line.length?`<path d="${path(line)}" fill="none" stroke="#ba8b42" stroke-width="2" stroke-dasharray="7 5"/>`:'')+labels+'</svg>';
}
