import test from 'node:test';
import assert from 'node:assert/strict';
import {timelapseDates,createTimelapse} from '../frontend/js/timelapse.js';
const variable={layer:'test',dataResolution:'daily'};

test('daily playback includes both exact endpoints',()=>{
 assert.deepEqual(timelapseDates('2024-02-28','2024-03-01','daily',variable),['2024-02-28','2024-02-29','2024-03-01']);
});
test('monthly and annual steps preserve the start day across leap years and include the end',()=>{
 assert.deepEqual(timelapseDates('2024-01-31','2024-04-10','monthly',variable),['2024-01-31','2024-02-29','2024-03-31','2024-04-10']);
 assert.deepEqual(timelapseDates('2024-02-29','2026-03-01','annual',variable),['2024-02-29','2025-02-28','2026-02-28','2026-03-01']);
});
test('published coverage gaps never cause frames outside the user window or duplicate frames',()=>{
 const v={...variable,coverage:'2024-01-02/2024-01-04/P2D'};
 assert.deepEqual(timelapseDates('2024-01-01','2024-01-05','daily',v),['2024-01-02','2024-01-04']);
 assert.deepEqual(timelapseDates('2023-01-01','2023-01-05','daily',v),[]);
 assert.deepEqual(timelapseDates('2024-01-01','2024-01-05','daily',{...v,static:true}),[]);
 assert.deepEqual(timelapseDates('2024-01-01','2024-01-31','native',{...variable,dataResolution:'8-day'}),['2024-01-01','2024-01-09','2024-01-17','2024-01-25','2024-01-31']);
});
function setup(overrides={}){
 const button={attributes:{},addEventListener(_,fn){this.click=fn;},setAttribute(k,v){this.attributes[k]=v;}};
 const frames=[],messages=[],delays=[];
 const player=createTimelapse({button,settings:()=>({start:'2024-01-01',end:'2024-01-03',resolution:'daily',variable}),showFrame:async date=>{frames.push(date);return true;},notify:m=>messages.push(m),wait:async ms=>delays.push(ms),...overrides});
 return {button,frames,messages,delays,player};
}
test('playback loads frames sequentially at a readable speed and stops on the end date',async()=>{
 const {button,frames,messages,delays}=setup();await button.click();
 assert.deepEqual(frames,['2024-01-01','2024-01-02','2024-01-03']);
 assert.deepEqual(delays,[1500,1500]);assert.match(messages.at(-1),/finished.*2024-01-03/);
 assert.equal(button.attributes['aria-pressed'],'false');assert.equal(button.textContent,'Play timelapse ▷');
});
test('stopping during a pending frame prevents every subsequent date from loading',async()=>{
 let finish;const pending=new Promise(resolve=>{finish=resolve;});const frames=[];
 const {button,player}=setup({showFrame:async date=>{frames.push(date);await pending;return true;}});
 const playing=button.click();player.stop();finish();await playing;
 assert.deepEqual(frames,['2024-01-01']);assert.equal(button.attributes['aria-pressed'],'false');
});
test('a failed map frame stops playback instead of silently skipping imagery',async()=>{
 const {button,messages}=setup({showFrame:async()=>false});await button.click();
 assert.match(messages.at(-1),/could not load/);assert.equal(button.attributes['aria-pressed'],'false');
});
