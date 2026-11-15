// Deterministic plain-language summary: no external AI service or invented results.
export function summarizeTrend(analysis, name) {
 const change=analysis.slopePerDecade;
 const amount=Math.abs(change).toLocaleString('en-US',{maximumSignificantDigits:3});
 if(change===0) return `${name} showed no estimated overall change during the selected period. This describes the observations available for this place and period.`;
 const direction=change>0?'increased':'decreased';
 if(analysis.series?.length>1 && Date.parse(analysis.series.at(-1).date)-Date.parse(analysis.series[0].date)<2*365.2425*86400000){
  return `${name} ${direction} over this short selection. Seasonal variation can dominate a period this brief; the displayed rate should not be interpreted as a long-term climate trend.`;
 }
 const evidence=analysis.pValue<.05
  ? 'The tests suggest a consistent change, although they do not explain what caused it.'
  : 'The evidence is not strong enough to tell whether this is a lasting trend or natural variation.';
 // Do not describe a result as consistent when residual correlation is substantial.
 const caution=Math.abs(analysis.lagOneResidualCorrelation??0)>.3
  ? 'Similar readings over time make this estimate less certain; it does not tell us what caused the change.'
  : evidence;
 return `${name} ${direction} by an estimated ${amount} ${analysis.unit} per decade during the selected period. ${caution}`;
}
export function bindTrendDetails(button, details) {
 button.addEventListener('click',()=>{
  const expanded=button.getAttribute('aria-expanded')==='true';
  button.setAttribute('aria-expanded',String(!expanded));
  button.textContent=expanded?'Show more':'Show less';
  details.hidden=expanded;
 });
}
