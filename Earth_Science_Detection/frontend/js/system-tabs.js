// One shared highlight travels between window tabs in either direction.
export function bindSystemTabs(nav) {
 if(!nav)return ()=>{};
 let highlight=nav.querySelector('.system-tab-highlight');
 if(!highlight){highlight=document.createElement('span');highlight.className='system-tab-highlight';highlight.setAttribute('aria-hidden','true');nav.prepend(highlight);}
 let initialized=false;
 function update() {
  const active=nav.querySelector('[aria-current="page"]');
  if(!active)return;
  highlight.style.width=active.offsetWidth+'px';
  highlight.style.height=active.offsetHeight+'px';
  highlight.style.transform=`translate(${active.offsetLeft}px, ${active.offsetTop}px)`;
  if(!initialized){initialized=true;requestAnimationFrame(()=>nav.classList.add('tabs-ready'));}
 }
 if(typeof ResizeObserver!=='undefined'){const observer=new ResizeObserver(update);observer.observe(nav);}
 else window.addEventListener('resize',update);
 document.fonts?.ready.then(update);
 return update;
}
