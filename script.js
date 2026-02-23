"use strict";
const TAU=Math.PI*2,DEG=Math.PI/180,AU_KM=149_597_870.7,SECONDS_PER_DAY=86400,MU_ROUTH=0.5*(1-Math.sqrt(23/27)),MOON_ORBIT_VISUAL_SCALE=60;
const AXIS={Sun:7.25,Mercury:.03,Venus:177.36,Earth:23.44,Mars:25.19,Jupiter:3.13,Saturn:26.73,Uranus:97.77,Neptune:28.32};
const SPIN_HOURS={Sun:609.12,Mercury:1407.6,Venus:-5832.5,Earth:23.9345,Mars:24.6229,Jupiter:9.925,Saturn:10.656,Uranus:-17.24,Neptune:16.11};
const BODIES=[
{name:"Sun",color:"#f5d142",radiusKm:695700,massKg:1.98847e30,a:0,periodDays:1,phaseDeg:0,incDeg:0},
{name:"Mercury",color:"#9ea2a8",radiusKm:2439.7,massKg:3.3011e23,a:.3871,periodDays:87.969,phaseDeg:60,incDeg:7},
{name:"Venus",color:"#d7b57d",radiusKm:6051.8,massKg:4.8675e24,a:.7233,periodDays:224.701,phaseDeg:140,incDeg:3.4},
{name:"Earth",color:"#4f83ff",radiusKm:6371,massKg:5.97219e24,a:1,periodDays:365.256,phaseDeg:220,incDeg:0},
{name:"Mars",color:"#b95b3c",radiusKm:3389.5,massKg:6.4171e23,a:1.5237,periodDays:686.98,phaseDeg:300,incDeg:1.85},
{name:"Jupiter",color:"#c9ae8b",radiusKm:69911,massKg:1.89813e27,a:5.2034,periodDays:4332.59,phaseDeg:15,incDeg:1.3},
{name:"Saturn",color:"#d7c48f",radiusKm:58232,massKg:5.6834e26,a:9.537,periodDays:10759.22,phaseDeg:80,incDeg:2.5},
{name:"Uranus",color:"#8dd8e9",radiusKm:25362,massKg:8.681e25,a:19.191,periodDays:30688.5,phaseDeg:180,incDeg:.77},
{name:"Neptune",color:"#4c6fd6",radiusKm:24622,massKg:1.02413e26,a:30.07,periodDays:60182,phaseDeg:240,incDeg:1.77},
];
const MOONS={
Earth:[{name:"Moon",color:"#c8c8c8",radiusKm:1737.4,massKg:7.342e22,orbitRadiusKm:384400,periodDays:27.3217,phaseDeg:0,incDeg:5.1}],
Mars:[{name:"Phobos",color:"#8e7f72",radiusKm:11.267,massKg:1.0659e16,orbitRadiusKm:9376,periodDays:.3189,phaseDeg:120,incDeg:1.1},{name:"Deimos",color:"#9a8d82",radiusKm:6.2,massKg:1.4762e15,orbitRadiusKm:23463,periodDays:1.262,phaseDeg:220,incDeg:1.8}],
Jupiter:[{name:"Io",color:"#e0cf78",radiusKm:1821.6,massKg:8.9319e22,orbitRadiusKm:421700,periodDays:1.769,phaseDeg:0,incDeg:.04},{name:"Europa",color:"#ddd5be",radiusKm:1560.8,massKg:4.7998e22,orbitRadiusKm:671034,periodDays:3.551,phaseDeg:90,incDeg:.47},{name:"Ganymede",color:"#bca890",radiusKm:2634.1,massKg:1.4819e23,orbitRadiusKm:1_070_412,periodDays:7.155,phaseDeg:170,incDeg:.2},{name:"Callisto",color:"#8f7e6c",radiusKm:2410.3,massKg:1.0759e23,orbitRadiusKm:1_882_709,periodDays:16.689,phaseDeg:270,incDeg:.2}],
Saturn:[{name:"Mimas",color:"#bdb8b2",radiusKm:198.2,massKg:3.7493e19,orbitRadiusKm:185539,periodDays:.942,phaseDeg:0,incDeg:1.5},{name:"Rhea",color:"#c7c1b8",radiusKm:763.8,massKg:2.3065e21,orbitRadiusKm:527108,periodDays:4.518,phaseDeg:110,incDeg:.35},{name:"Titan",color:"#d6a86e",radiusKm:2574.7,massKg:1.3452e23,orbitRadiusKm:1_221_870,periodDays:15.945,phaseDeg:210,incDeg:.33},{name:"Iapetus",color:"#a99b8b",radiusKm:734.5,massKg:1.8056e21,orbitRadiusKm:3_560_820,periodDays:79.321,phaseDeg:290,incDeg:15.5}],
Uranus:[{name:"Miranda",color:"#beb7ad",radiusKm:235.8,massKg:6.59e19,orbitRadiusKm:129390,periodDays:1.413,phaseDeg:30,incDeg:4.3},{name:"Ariel",color:"#c9c3b8",radiusKm:578.9,massKg:1.353e21,orbitRadiusKm:190900,periodDays:2.52,phaseDeg:120,incDeg:0},{name:"Umbriel",color:"#9f9a92",radiusKm:584.7,massKg:1.172e21,orbitRadiusKm:266000,periodDays:4.144,phaseDeg:200,incDeg:.1},{name:"Titania",color:"#b4aea4",radiusKm:788.9,massKg:3.527e21,orbitRadiusKm:436300,periodDays:8.706,phaseDeg:290,incDeg:.1},{name:"Oberon",color:"#9d978e",radiusKm:761.4,massKg:3.014e21,orbitRadiusKm:583500,periodDays:13.463,phaseDeg:350,incDeg:.1}],
Neptune:[{name:"Triton",color:"#c8cdd2",radiusKm:1353.4,massKg:2.139e22,orbitRadiusKm:354759,periodDays:5.877,phaseDeg:30,incDeg:157},{name:"Nereid",color:"#b2b9c0",radiusKm:170,massKg:3.1e19,orbitRadiusKm:5_513_818,periodDays:360.13,phaseDeg:180,incDeg:7.2}],
};
const BODY_MAP=Object.fromEntries(BODIES.map(b=>[b.name,b])),BODY_ORDER=BODIES.map(b=>b.name),SCENE_RADIUS=Math.max(...BODIES.map(b=>b.a));
const scene={showOrbits:true,showAllOrbits:false,showMoons:false,showBelts:true,showLagrange:false,selectedBody:"Sun",selectedMoon:null,selectedLagrange:null,lockBody:"Sun",lagrangePrimary:"Sun",lagrangeSecondary:"Earth",lastSelectedPlanet:"Earth",simDays:0,simSpeed:2,running:true,yaw:35*DEG,pitch:20*DEG,distance:SCENE_RADIUS*2.3,focus:{x:0,y:0,z:0},dragMode:null,dragStart:null,lastClickMs:0};
const canvas=document.getElementById("scene"),statusLine=document.getElementById("statusLine"),ctx=canvas.getContext("2d"),startEpochMs=Date.now();
const speedSlider=document.getElementById("speedSlider"),speedValue=document.getElementById("speedValue"),pauseBtn=document.getElementById("pauseBtn"),allOrbitsBtn=document.getElementById("allOrbitsBtn");
if(statusLine)statusLine.textContent="Simulation script loaded. Booting...";
window.addEventListener("error",e=>{if(statusLine)statusLine.textContent=`Runtime error: ${e.message}`;});
window.addEventListener("unhandledrejection",e=>{if(statusLine)statusLine.textContent=`Promise error: ${e.reason?.message||String(e.reason)}`;});
if(!canvas||!statusLine||!ctx){if(statusLine)statusLine.textContent="Startup error: Canvas initialization failed.";throw new Error("Canvas initialization failed");}
let width=1,height=1,projectedBodies=[],projectedMoons=[],projectedLagrange=[];

const v=(x=0,y=0,z=0)=>({x,y,z}),add=(a,b)=>v(a.x+b.x,a.y+b.y,a.z+b.z),sub=(a,b)=>v(a.x-b.x,a.y-b.y,a.z-b.z),mul=(a,s)=>v(a.x*s,a.y*s,a.z*s),dot=(a,b)=>a.x*b.x+a.y*b.y+a.z*b.z,cross=(a,b)=>v(a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x),norm=a=>Math.hypot(a.x,a.y,a.z),unit=(a,f=v(1,0,0))=>{const n=norm(a);return n>1e-12?mul(a,1/n):f},clamp=(x,a,b)=>Math.min(b,Math.max(a,x));
const moonToken=(p,m)=>`moon::${p}::${m}`,parseMoonToken=t=>{if(!t?.startsWith("moon::"))return null;const p=t.split("::");return p.length===3?{parent:p[1],moon:p[2]}:null},targetLabel=t=>{const p=parseMoonToken(t);return p?`${p.moon} (${p.parent})`:t};
const belts={main:makeBelt(1600,2.1,3.3,.11,.06,7,42),kuiper:makeBelt(3200,30,50,.15,.09,10,84)};

function rng(seed){let s=seed>>>0;return()=>((s=(1664525*s+1013904223)>>>0)/0xffffffff);}
function makeBelt(count,aMin,aMax,eMean,eSigma,iSigmaDeg,seed){const rnd=rng(seed),pts=[];for(let i=0;i<count;i++){const a=aMin+(aMax-aMin)*rnd(),e=Math.max(0,eMean+eSigma*(rnd()*2-1)),f=TAU*rnd(),omega=TAU*rnd(),node=TAU*rnd(),inc=(rnd()*2-1)*iSigmaDeg*DEG,r=a*(1-e*e)/(1+e*Math.cos(f)),u=f+omega,cu=Math.cos(u),su=Math.sin(u),cn=Math.cos(node),sn=Math.sin(node),ci=Math.cos(inc),si=Math.sin(inc),x=r*(cn*cu-sn*su*ci),z=r*(sn*cu+cn*su*ci),y=r*su*si;pts.push(v(x,y,z));}return pts;}
function resize(){const dpr=Math.max(1,Math.min(2,window.devicePixelRatio||1)),r=canvas.getBoundingClientRect();width=Math.max(1,Math.floor(r.width));height=Math.max(1,Math.floor(r.height));canvas.width=Math.floor(width*dpr);canvas.height=Math.floor(height*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);}
function bodyPos(body,t){if(body.name==="Sun")return v();const th=((t/body.periodDays)*TAU+body.phaseDeg*DEG)%TAU,node=(body.phaseDeg*.37)*DEG,xb=body.a*Math.cos(th),zb=body.a*Math.sin(th),yb=Math.sin(body.incDeg*DEG)*body.a*Math.sin(th+node);return v(xb*Math.cos(node)-zb*Math.sin(node),yb,xb*Math.sin(node)+zb*Math.cos(node));}
function moonRel(m,t){const a=(m.orbitRadiusKm/AU_KM)*MOON_ORBIT_VISUAL_SCALE,th=((t/m.periodDays)*TAU+m.phaseDeg*DEG)%TAU,node=(m.phaseDeg*.73)*DEG,xb=a*Math.cos(th),zb=a*Math.sin(th),yb=Math.sin(m.incDeg*DEG)*a*Math.sin(th+node);return v(xb*Math.cos(node)-zb*Math.sin(node),yb,xb*Math.sin(node)+zb*Math.cos(node));}
function rotateToCam(p){const r=sub(p,scene.focus),cy=Math.cos(scene.yaw),sy=Math.sin(scene.yaw),cp=Math.cos(scene.pitch),sp=Math.sin(scene.pitch),x1=r.x*cy-r.z*sy,z1=r.x*sy+r.z*cy,y2=r.y*cp-z1*sp,z2=r.y*sp+z1*cp;return v(x1,y2,z2);}
function panBasis(){const cy=Math.cos(scene.yaw),sy=Math.sin(scene.yaw),cp=Math.cos(scene.pitch),sp=Math.sin(scene.pitch);return{right:v(cy,0,-sy),up:v(-sp*sy,cp,-sp*cy)};}
function project(p){const c=rotateToCam(p),z=c.z+scene.distance;if(z<=1e-7)return null;const f=Math.min(width,height)*.95;return{sx:width*.5+(c.x/z)*f,sy:height*.5-(c.y/z)*f,depth:z};}
function bodyRadiusPx(radiusKm,depth,name){const f=Math.min(width,height)*.95,px=((radiusKm/AU_KM)/depth)*f;return Math.max(name==="Sun"?1.6:1,px);}
function velocityInfo(vel){const au=norm(vel),km=(au*AU_KM)/SECONDS_PER_DAY,u=au>0?mul(vel,1/au):v(),lon=Math.atan2(u.y,u.x)/DEG,lat=Math.atan2(u.z,Math.hypot(u.x,u.y))/DEG;return{km,u,lon,lat};}
function targetRadiusKm(target){if(BODY_MAP[target])return BODY_MAP[target].radiusKm;const p=parseMoonToken(target);if(!p)return null;const moon=MOONS[p.parent]?.find(m=>m.name===p.moon);return moon?moon.radiusKm:null;}
function spinAngle(name,tDays){const h=SPIN_HOURS[name];if(!h)return 0;const rotDays=h/24;return((tDays/rotDays)*TAU)%TAU;}
function applyUnlockedLagrangeDefault(){const p=scene.lastSelectedPlanet;if(p&&p!=="Sun"&&BODY_MAP[p]){scene.lagrangePrimary="Sun";scene.lagrangeSecondary=p;}}

function buildState(t){
  const e=.001,bodyStates={},moonStates={};
  for(const b of BODIES){const p=bodyPos(b,t),vel=mul(sub(bodyPos(b,t+e),bodyPos(b,t-e)),1/(2*e));bodyStates[b.name]={pos:p,vel,massKg:b.massKg,radiusKm:b.radiusKm,color:b.color};}
  for(const parent of Object.keys(MOONS)){moonStates[parent]={};const ps=bodyStates[parent];for(const m of MOONS[parent]){const rNow=moonRel(m,t),rPrev=moonRel(m,t-e),rNext=moonRel(m,t+e),pos=add(ps.pos,rNow),vel=add(ps.vel,mul(sub(rNext,rPrev),1/(2*e)));moonStates[parent][m.name]={pos,vel,massKg:m.massKg,radiusKm:m.radiusKm,moon:m};}}
  return{bodyStates,moonStates};
}
function resolveTargetState(target,state){if(state.bodyStates[target])return state.bodyStates[target];const p=parseMoonToken(target);return p?state.moonStates[p.parent]?.[p.moon]||null:null;}
function secondaryCandidates(){const out=BODY_ORDER.filter(b=>b!==scene.lagrangePrimary);if(scene.showLagrange&&scene.lockBody&&MOONS[scene.lockBody])for(const m of MOONS[scene.lockBody])out.push(moonToken(scene.lockBody,m.name));return out;}
function syncLagrangeWithLock(state){
  if(!scene.lockBody)return;
  const moonLock=parseMoonToken(scene.lockBody);
  if(moonLock){scene.lagrangePrimary=moonLock.parent;scene.lagrangeSecondary=scene.lockBody;return;}
  if(!MOONS[scene.lockBody]?.length)return;
  const parent=scene.lockBody,selectedTok=scene.selectedMoon&&scene.selectedBody===parent?moonToken(parent,scene.selectedMoon):null;
  const validMoon=selectedTok&&resolveTargetState(selectedTok,state)?selectedTok:null;
  scene.lagrangePrimary=parent;
  scene.lagrangeSecondary=validMoon||moonToken(parent,MOONS[parent][0].name);
}
function computeLagrange(state){
  if(scene.lagrangePrimary===scene.lagrangeSecondary)return[];const p1=resolveTargetState(scene.lagrangePrimary,state),p2=resolveTargetState(scene.lagrangeSecondary,state);if(!p1||!p2)return[];
  const rVec=sub(p2.pos,p1.pos),r=norm(rVec);if(r<=1e-12)return[];const u=unit(rVec),mu=p2.massKg/(p1.massKg+p2.massKg),h=unit(cross(rVec,sub(p2.vel,p1.vel)),v(0,0,1)),vDir=unit(cross(h,u),v(0,1,0)),d=r*Math.pow(mu/3,1/3);
  return[{label:"L1",pos:add(p1.pos,sub(rVec,mul(u,d)))},{label:"L2",pos:add(p1.pos,add(rVec,mul(u,d)))},{label:"L3",pos:add(p1.pos,mul(u,-r*(1+(5*mu)/12)))},{label:"L4",pos:add(p1.pos,add(mul(u,.5*r),mul(vDir,Math.sqrt(3)*.5*r)))},{label:"L5",pos:add(p1.pos,sub(mul(u,.5*r),mul(vDir,Math.sqrt(3)*.5*r)))}];
}
function lagrangeStability(label,state){const p=resolveTargetState(scene.lagrangePrimary,state),s=resolveTargetState(scene.lagrangeSecondary,state);if(!p||!s)return{text:"Unknown",score:0,mu:0};const mu=s.massKg/(p.massKg+s.massKg);if(["L1","L2","L3"].includes(label))return{text:"Unstable (saddle equilibrium)",score:0,mu};if(["L4","L5"].includes(label)){if(mu<MU_ROUTH)return{text:"Conditionally stable (small perturbations)",score:clamp(1-(mu/MU_ROUTH),0,1),mu};const ex=(mu/MU_ROUTH)-1;return{text:"Unstable (mass ratio above Routh limit)",score:clamp(1-ex,0,1),mu};}return{text:"Unknown",score:0,mu};}
function drawOrbit(center,rVec,vVec,color){const r=norm(rVec);if(r<=1e-12)return;const u=unit(rVec),h=norm(cross(rVec,vVec));if(h<=1e-12)return;const hHat=unit(cross(rVec,vVec)),w=unit(cross(hHat,u));let open=false,segments=0;ctx.beginPath();for(let i=0;i<=240;i++){const t=(TAU*i)/240,p=add(center,add(mul(u,r*Math.cos(t)),mul(w,r*Math.sin(t)))),pr=project(p);if(!pr){open=false;continue;}if(!open){ctx.moveTo(pr.sx,pr.sy);open=true;segments++;}else ctx.lineTo(pr.sx,pr.sy);}if(segments>0){ctx.strokeStyle=color;ctx.lineWidth=.9;ctx.stroke();}}
function drawAxisEquator(name,state,tDays){const st=state.bodyStates[name],item=projectedBodies.find(b=>b.name===name);if(!st||!item||item.drawRadius<18)return;const tilt=(AXIS[name]||0)*DEG,axis=unit(v(0,Math.sin(tilt),Math.cos(tilt)),v(0,0,1)),ra=st.radiusKm/AU_KM,p1=sub(st.pos,mul(axis,ra*1.4)),p2=add(st.pos,mul(axis,ra*1.4)),s1=project(p1),s2=project(p2);if(s1&&s2){ctx.strokeStyle="#6fd3ff";ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(s1.sx,s1.sy);ctx.lineTo(s2.sx,s2.sy);ctx.stroke();}let ref=v(1,0,0);if(Math.abs(dot(ref,axis))>.95)ref=v(0,1,0);const e1Base=unit(cross(axis,ref)),e2Base=unit(cross(axis,e1Base)),a=spinAngle(name,tDays),ca=Math.cos(a),sa=Math.sin(a),e1=unit(add(mul(e1Base,ca),mul(e2Base,sa))),e2=unit(add(mul(e2Base,ca),mul(e1Base,-sa)));let stt=false;ctx.beginPath();for(let i=0;i<=64;i++){const t=(TAU*i)/64,p=add(st.pos,add(mul(e1,ra*Math.cos(t)),mul(e2,ra*Math.sin(t)))),pr=project(p);if(!pr)continue;if(!stt){ctx.moveTo(pr.sx,pr.sy);stt=true;}else ctx.lineTo(pr.sx,pr.sy);}if(stt){ctx.strokeStyle="#8ce99a";ctx.lineWidth=2;ctx.stroke();}let mer=false;ctx.beginPath();for(let i=0;i<=64;i++){const t=(TAU*i)/64,p=add(st.pos,add(mul(axis,ra*Math.cos(t)),mul(e1,ra*Math.sin(t)))),pr=project(p);if(!pr)continue;if(!mer){ctx.moveTo(pr.sx,pr.sy);mer=true;}else ctx.lineTo(pr.sx,pr.sy);}if(mer){ctx.strokeStyle="#ffd166";ctx.lineWidth=1.5;ctx.stroke();}}
function drawSelection(item,color,extra=4){ctx.strokeStyle=color;ctx.lineWidth=2;ctx.beginPath();ctx.arc(item.sx,item.sy,Math.max(item.drawRadius+extra,7),0,TAU);ctx.stroke();}
function drawBackground(){const g=ctx.createRadialGradient(width*.3,height*.2,20,width*.4,height*.4,width*.8);g.addColorStop(0,"#0d1830");g.addColorStop(1,"#04070f");ctx.fillStyle=g;ctx.fillRect(0,0,width,height);}
function drawBelts(){for(const p of belts.main){const pr=project(p);if(!pr)continue;ctx.fillStyle="rgba(143,143,143,0.62)";ctx.fillRect(pr.sx,pr.sy,1.4,1.4);}for(const p of belts.kuiper){const pr=project(p);if(!pr)continue;ctx.fillStyle="rgba(95,122,166,0.62)";ctx.fillRect(pr.sx,pr.sy,1.2,1.2);}}
function drawBody(b){if(b.drawRadius<2){ctx.fillStyle=b.color;ctx.beginPath();ctx.arc(b.sx,b.sy,1.2,0,TAU);ctx.fill();return;}ctx.beginPath();ctx.arc(b.sx,b.sy,b.drawRadius,0,TAU);ctx.fillStyle=b.color;ctx.fill();const g=ctx.createRadialGradient(b.sx-b.drawRadius*.25,b.sy-b.drawRadius*.35,1,b.sx,b.sy,b.drawRadius*1.7);g.addColorStop(0,"rgba(255,255,255,0.45)");g.addColorStop(1,"rgba(255,255,255,0)");ctx.fillStyle=g;ctx.beginPath();ctx.arc(b.sx,b.sy,b.drawRadius*1.6,0,TAU);ctx.fill();if(b.name==="Saturn"){ctx.save();ctx.translate(b.sx,b.sy);ctx.rotate(-.3+scene.yaw*.1);ctx.strokeStyle="rgba(220,210,160,.8)";ctx.lineWidth=1.3;ctx.beginPath();ctx.ellipse(0,0,b.drawRadius*2.6,b.drawRadius*1.1,0,0,TAU);ctx.stroke();ctx.restore();}}
function fillRoundRect(x,y,w,h,r){const rr=Math.max(0,Math.min(r,Math.min(w,h)*.5));ctx.beginPath();ctx.moveTo(x+rr,y);ctx.lineTo(x+w-rr,y);ctx.quadraticCurveTo(x+w,y,x+w,y+rr);ctx.lineTo(x+w,y+h-rr);ctx.quadraticCurveTo(x+w,y+h,x+w-rr,y+h);ctx.lineTo(x+rr,y+h);ctx.quadraticCurveTo(x,y+h,x,y+h-rr);ctx.lineTo(x,y+rr);ctx.quadraticCurveTo(x,y,x+rr,y);ctx.closePath();ctx.fill();}
function strokeRoundRect(x,y,w,h,r){const rr=Math.max(0,Math.min(r,Math.min(w,h)*.5));ctx.beginPath();ctx.moveTo(x+rr,y);ctx.lineTo(x+w-rr,y);ctx.quadraticCurveTo(x+w,y,x+w,y+rr);ctx.lineTo(x+w,y+h-rr);ctx.quadraticCurveTo(x+w,y+h,x+w-rr,y+h);ctx.lineTo(x+rr,y+h);ctx.quadraticCurveTo(x,y+h,x,y+h-rr);ctx.lineTo(x,y+rr);ctx.quadraticCurveTo(x,y,x+rr,y);ctx.closePath();ctx.stroke();}

function drawPanels(state){
  const epoch=new Date(startEpochMs+scene.simDays*86400000).toISOString(),liveUtc=new Date().toISOString(),selBody=state.bodyStates[scene.selectedBody],selMoon=scene.selectedMoon?state.moonStates[scene.selectedBody]?.[scene.selectedMoon]:null,bv=velocityInfo(selBody.vel),lines=[`Selected: ${scene.selectedBody}`,`Lock: ${scene.lockBody?targetLabel(scene.lockBody):"None"}`,`Lagrange Pair: ${targetLabel(scene.lagrangePrimary)} -> ${targetLabel(scene.lagrangeSecondary)} (${scene.showLagrange?"ON":"OFF"})`,`Belts: ${scene.showBelts?"ON":"OFF"} | Orbits: ${scene.showOrbits?"ON":"OFF"} | All Orbits: ${scene.showAllOrbits?"ON":"OFF"} | Moons: ${scene.showMoons?"ON":"OFF"}`];
  if(selMoon){const relPos=sub(selMoon.pos,selBody.pos),relVel=sub(selMoon.vel,selBody.vel),rel=velocityInfo(relVel),sun=velocityInfo(selMoon.vel);lines.push(`Moon Selected: ${scene.selectedMoon} (parent: ${scene.selectedBody})`,`Mass: ${selMoon.massKg.toExponential(6)} kg`,`Position rel ${scene.selectedBody} (AU): x=${relPos.x.toFixed(9)} y=${relPos.y.toFixed(9)} z=${relPos.z.toFixed(9)}`,`Velocity rel ${scene.selectedBody} (AU/day): vx=${relVel.x.toFixed(9)} vy=${relVel.y.toFixed(9)} vz=${relVel.z.toFixed(9)}`,`Speed rel ${scene.selectedBody}: ${rel.km.toFixed(4)} km/s`,`Speed rel Sun: ${sun.km.toFixed(4)} km/s`);}
  else lines.push(`Mass: ${selBody.massKg.toExponential(6)} kg`,`Position rel Sun (AU): x=${selBody.pos.x.toFixed(9)} y=${selBody.pos.y.toFixed(9)} z=${selBody.pos.z.toFixed(9)}`,`Velocity rel Sun (AU/day): vx=${selBody.vel.x.toFixed(9)} vy=${selBody.vel.y.toFixed(9)} vz=${selBody.vel.z.toFixed(9)}`,`Speed: ${bv.km.toFixed(4)} km/s`,`Direction unit vector: x=${bv.u.x.toFixed(5)} y=${bv.u.y.toFixed(5)} z=${bv.u.z.toFixed(5)}`,`Direction angles (ecliptic): lon=${bv.lon.toFixed(2)} deg lat=${bv.lat.toFixed(2)} deg`);
  if(scene.selectedLagrange){const st=lagrangeStability(scene.selectedLagrange,state);lines.push(`Lagrange Selected: ${scene.selectedLagrange} (${targetLabel(scene.lagrangePrimary)}-${targetLabel(scene.lagrangeSecondary)})`,`Stability: ${st.text} | Score=${(st.score*100).toFixed(1)}/100 | mu=${st.mu.toFixed(6)} (mu_crit=${MU_ROUTH.toFixed(6)})`);}
  lines.push(`Model Epoch (UTC): ${epoch}`,`Live UTC: ${liveUtc}`);
  const pw=Math.max(380,Math.min(760,width*.44)),ph=Math.max(220,Math.min(height-24,16+lines.length*16+16)),x=width-pw-14,y=height-ph-8;
  ctx.fillStyle="rgba(13,21,38,0.88)";
  fillRoundRect(x,y,pw,ph,10);
  ctx.strokeStyle="rgba(119,160,231,0.4)";
  ctx.lineWidth=1;
  strokeRoundRect(x,y,pw,ph,10);
  ctx.fillStyle="#9ab0d9";
  ctx.font='13px "Segoe UI", Tahoma, Geneva, Verdana, sans-serif';
  for(let i=0;i<lines.length;i++){
    const yy=y+20+i*16;
    if(yy>y+ph-8)break;
    ctx.fillText(lines[i],x+12,yy,pw-24);
  }
}
function findHit(mx,my){
  if(scene.showMoons)for(const m of projectedMoons){const d2=(mx-m.sx)**2+(my-m.sy)**2;if(d2<=36)return{type:"moon",item:m};}
  if(scene.showLagrange)for(const l of projectedLagrange){const d2=(mx-l.sx)**2+(my-l.sy)**2;if(d2<=64)return{type:"lagrange",item:l};}
  let hit=null,best=Infinity;for(const b of projectedBodies){const r=Math.max(b.drawRadius,6),d2=(mx-b.sx)**2+(my-b.sy)**2;if(d2<=r*r&&d2<best){best=d2;hit=b;}}return hit?{type:"body",item:hit}:null;
}
function applySingleClick(hit){
  if(hit?.type==="moon"){scene.selectedMoon=hit.item.name;scene.selectedBody=hit.item.parent;scene.lastSelectedPlanet=hit.item.parent;scene.selectedLagrange=null;if(scene.showLagrange){scene.lagrangePrimary=hit.item.parent;scene.lagrangeSecondary=moonToken(hit.item.parent,hit.item.name);}return;}
  if(hit?.type==="lagrange"){scene.selectedLagrange=hit.item.label;scene.selectedMoon=null;return;}
  if(hit?.type==="body"){scene.selectedBody=hit.item.name;if(hit.item.name!=="Sun")scene.lastSelectedPlanet=hit.item.name;scene.selectedMoon=null;scene.selectedLagrange=null;if(scene.showLagrange&&hit.item.name!==scene.lagrangePrimary)scene.lagrangeSecondary=hit.item.name;}else{scene.selectedMoon=null;scene.selectedLagrange=null;}
}
function syncSpeedUi(){
  const v1=scene.simSpeed.toFixed(2);
  if(speedSlider&&speedSlider.value!==v1)speedSlider.value=v1;
  if(speedValue)speedValue.textContent=scene.simSpeed.toFixed(2);
}
function syncPauseUi(){if(pauseBtn)pauseBtn.textContent=scene.running?"Pause":"Resume";}
function syncAllOrbitsUi(){if(allOrbitsBtn)allOrbitsBtn.textContent=`All Orbits: ${scene.showAllOrbits?"On":"Off"}`;}

function render(ts){
  if(!render.last)render.last=ts;const dt=Math.min(.05,(ts-render.last)/1000);render.last=ts;if(scene.running)scene.simDays+=dt*scene.simSpeed;
  drawBackground();const st=buildState(scene.simDays);projectedBodies=[];projectedMoons=[];projectedLagrange=[];
  if(scene.lockBody){const lockState=resolveTargetState(scene.lockBody,st);if(lockState)scene.focus={...lockState.pos};}
  syncLagrangeWithLock(st);
  for(const b of BODIES){const bs=st.bodyStates[b.name],pr=project(bs.pos);if(!pr)continue;projectedBodies.push({name:b.name,pos:bs.pos,vel:bs.vel,massKg:bs.massKg,radiusKm:bs.radiusKm,color:bs.color,sx:pr.sx,sy:pr.sy,depth:pr.depth,drawRadius:bodyRadiusPx(bs.radiusKm,pr.depth,b.name)});}
  if(scene.showBelts)drawBelts();
  if(scene.showOrbits){
    const sun=st.bodyStates.Sun;
    if(scene.showAllOrbits){
      for(const b of BODIES){
        if(b.name==="Sun")continue;
        const bs=st.bodyStates[b.name];
        if(sun&&bs)drawOrbit(sun.pos,sub(bs.pos,sun.pos),sub(bs.vel,sun.vel),b.color);
      }
    }else if(scene.selectedBody!=="Sun"){
      const sb=st.bodyStates[scene.selectedBody];
      if(sun&&sb)drawOrbit(sun.pos,sub(sb.pos,sun.pos),sub(sb.vel,sun.vel),BODY_MAP[scene.selectedBody].color);
    }
  }
  if(scene.selectedMoon){const m=st.moonStates[scene.selectedBody]?.[scene.selectedMoon],p=st.bodyStates[scene.selectedBody];if(m&&p)drawOrbit(p.pos,sub(m.pos,p.pos),sub(m.vel,p.vel),"#cfd3da");}
  if(scene.showMoons&&MOONS[scene.selectedBody]){for(const m of MOONS[scene.selectedBody]){const ms=st.moonStates[scene.selectedBody]?.[m.name];if(!ms)continue;const pr=project(ms.pos);if(!pr)continue;const r=bodyRadiusPx(ms.radiusKm,pr.depth,m.name),row={name:m.name,parent:scene.selectedBody,sx:pr.sx,sy:pr.sy,depth:pr.depth,drawRadius:r,label:m.name};projectedMoons.push(row);ctx.fillStyle=m.color;ctx.beginPath();ctx.arc(pr.sx,pr.sy,r,0,TAU);ctx.fill();ctx.fillStyle="#cfd3da";ctx.font="10px Consolas, monospace";ctx.fillText(m.name,pr.sx+6,pr.sy-6);}}
  for(const b of [...projectedBodies].sort((a,b)=>b.depth-a.depth)){drawBody(b);if(b.name==="Sun"){ctx.fillStyle="#000";ctx.font="bold 12px Consolas, monospace";ctx.fillText("SUN",b.sx+15,b.sy-13);ctx.fillStyle="#ffe88a";ctx.fillText("SUN",b.sx+14,b.sy-14);}else{ctx.fillStyle="#fff";ctx.font="12px Consolas, monospace";ctx.fillText(b.name,b.sx+8,b.sy-8);}}
  if(scene.showLagrange){for(const lp of computeLagrange(st)){const pr=project(lp.pos);if(!pr)continue;projectedLagrange.push({label:lp.label,sx:pr.sx,sy:pr.sy,depth:pr.depth});ctx.fillStyle="#ff66ff";ctx.beginPath();ctx.arc(pr.sx,pr.sy,4,0,TAU);ctx.fill();ctx.fillStyle="#ff99ff";ctx.font="11px Consolas, monospace";ctx.fillText(lp.label,pr.sx+8,pr.sy-8);}if(scene.selectedLagrange){const s=projectedLagrange.find(x=>x.label===scene.selectedLagrange);if(s){ctx.strokeStyle="#ff3333";ctx.lineWidth=2;ctx.beginPath();ctx.arc(s.sx,s.sy,8,0,TAU);ctx.stroke();}}}
  const sb=projectedBodies.find(b=>b.name===scene.selectedBody);if(sb)drawSelection(sb,scene.lockBody===scene.selectedBody?"#ff4040":"#00ffff");if(scene.selectedMoon){const sm=projectedMoons.find(m=>m.name===scene.selectedMoon);if(sm)drawSelection(sm,"#00ffff");}
  drawAxisEquator(scene.selectedBody,st,scene.simDays);drawPanels(st);
  statusLine.textContent=`${scene.running?"Running":"Paused"} | Selected ${scene.selectedBody}${scene.selectedMoon?` / ${scene.selectedMoon}`:""} | Lock ${scene.lockBody?targetLabel(scene.lockBody):"None"} | Pair ${targetLabel(scene.lagrangePrimary)} -> ${targetLabel(scene.lagrangeSecondary)} | Speed ${scene.simSpeed.toFixed(2)} days/s`;
  requestAnimationFrame(safeRender);
}
function safeRender(ts){try{render(ts);}catch(err){if(statusLine)statusLine.textContent=`Runtime error: ${err?.message||String(err)}`;}}
function onDown(e){canvas.setPointerCapture(e.pointerId);scene.dragStart={x:e.clientX,y:e.clientY,yaw:scene.yaw,pitch:scene.pitch,focus:{...scene.focus}};scene.dragMode=e.button===2?"orbit":(e.button===1?"pan":"left");}
function onMove(e){if(!scene.dragStart||!scene.dragMode)return;const dx=e.clientX-scene.dragStart.x,dy=e.clientY-scene.dragStart.y;if(scene.dragMode==="orbit"){scene.yaw=scene.dragStart.yaw+dx*.005;scene.pitch=clamp(scene.dragStart.pitch-dy*.005,-85*DEG,85*DEG);}else if(scene.dragMode==="pan"){if(scene.lockBody){scene.lockBody=null;applyUnlockedLagrangeDefault();}const s=(scene.distance/(Math.min(width,height)*.95))*2,{right,up}=panBasis(),worldDelta=add(mul(right,-dx*s),mul(up,dy*s));scene.focus=add(scene.dragStart.focus,worldDelta);}}
function onUp(e){const r=canvas.getBoundingClientRect(),mx=e.clientX-r.left,my=e.clientY-r.top;if(scene.dragMode==="left"&&scene.dragStart){const moved=Math.hypot(e.clientX-scene.dragStart.x,e.clientY-scene.dragStart.y);if(moved<4){const hit=findHit(mx,my),now=performance.now(),dbl=now-scene.lastClickMs<=300;if(dbl){if(!hit){if(scene.lockBody){scene.lockBody=null;applyUnlockedLagrangeDefault();}scene.selectedMoon=null;}else if(hit.type==="body"){if(scene.lockBody===hit.item.name){scene.lockBody=null;applyUnlockedLagrangeDefault();}else{scene.selectedBody=hit.item.name;if(hit.item.name!=="Sun")scene.lastSelectedPlanet=hit.item.name;scene.selectedMoon=null;scene.selectedLagrange=null;scene.lockBody=hit.item.name;if(hit.item.name!==scene.lagrangePrimary)scene.lagrangeSecondary=hit.item.name;}}else if(hit.type==="moon"){const tok=moonToken(hit.item.parent,hit.item.name);if(scene.lockBody===tok){scene.lockBody=null;applyUnlockedLagrangeDefault();}else{scene.selectedBody=hit.item.parent;scene.lastSelectedPlanet=hit.item.parent;scene.selectedMoon=hit.item.name;scene.selectedLagrange=null;scene.lockBody=tok;if(scene.showLagrange){scene.lagrangePrimary=hit.item.parent;scene.lagrangeSecondary=tok;}}}scene.lastClickMs=0;}else{applySingleClick(hit);scene.lastClickMs=now;}}}scene.dragMode=null;scene.dragStart=null;canvas.releasePointerCapture(e.pointerId);}
function onWheel(e){e.preventDefault();scene.distance*=e.deltaY>0?1.08:.92;let min=SCENE_RADIUS*.02;if(scene.lockBody){const rKm=targetRadiusKm(scene.lockBody);if(rKm)min=Math.max((rKm/AU_KM)*1.01,SCENE_RADIUS*1e-7);}scene.distance=clamp(scene.distance,min,SCENE_RADIUS*10);}
function nextBody(current,exclude){const idx=BODY_ORDER.includes(current)?BODY_ORDER.indexOf(current):-1;for(let i=1;i<=BODY_ORDER.length;i++){const c=BODY_ORDER[(idx+i+BODY_ORDER.length)%BODY_ORDER.length];if(c!==exclude)return c;}return current;}
function cyclePrimary(){scene.lagrangePrimary=nextBody(scene.lagrangePrimary,scene.lagrangeSecondary);scene.selectedLagrange=null;}
function cycleSecondary(){const c=secondaryCandidates();if(!c.length)return;const i=c.indexOf(scene.lagrangeSecondary);scene.lagrangeSecondary=i<0?c[0]:c[(i+1)%c.length];scene.selectedLagrange=null;}
function onKey(e){const k=e.key.toLowerCase();if(k==="e"){scene.selectedBody="Earth";scene.lastSelectedPlanet="Earth";scene.selectedMoon=null;scene.selectedLagrange=null;scene.lockBody="Earth";if(scene.lagrangePrimary!=="Earth")scene.lagrangeSecondary="Earth";}else if(k==="s"){scene.selectedBody="Sun";scene.selectedMoon=null;scene.selectedLagrange=null;scene.lockBody="Sun";if(scene.lagrangePrimary!=="Sun")scene.lagrangeSecondary="Sun";}else if(k==="escape"){scene.lockBody=null;applyUnlockedLagrangeDefault();scene.selectedMoon=null;scene.selectedLagrange=null;}else if(k==="l"){scene.showLagrange=!scene.showLagrange;if(!scene.showLagrange)scene.selectedLagrange=null;}else if(k==="b")scene.showBelts=!scene.showBelts;else if(k==="r")scene.showOrbits=!scene.showOrbits;else if(k==="a"){scene.showAllOrbits=!scene.showAllOrbits;syncAllOrbitsUi();}else if(k==="m")scene.showMoons=!scene.showMoons;else if(k==="o")cyclePrimary();else if(k==="p")cycleSecondary();else if(k==="="||k==="+"){scene.simSpeed=clamp(scene.simSpeed*1.2,0,30);syncSpeedUi();}else if(k==="-"||k==="_"){scene.simSpeed=clamp(scene.simSpeed/1.2,0,30);syncSpeedUi();}else if(k===" "){scene.running=!scene.running;syncPauseUi();}}
canvas.addEventListener("contextmenu",e=>e.preventDefault());canvas.addEventListener("pointerdown",onDown);canvas.addEventListener("pointermove",onMove);canvas.addEventListener("pointerup",onUp);canvas.addEventListener("wheel",onWheel,{passive:false});window.addEventListener("resize",resize);window.addEventListener("keydown",onKey);
if(speedSlider){
  speedSlider.value=scene.simSpeed.toFixed(2);
  speedSlider.addEventListener("input",()=>{scene.simSpeed=clamp(Number(speedSlider.value),0,30);syncSpeedUi();});
}
if(pauseBtn)pauseBtn.addEventListener("click",()=>{scene.running=!scene.running;syncPauseUi();});
if(allOrbitsBtn)allOrbitsBtn.addEventListener("click",()=>{scene.showAllOrbits=!scene.showAllOrbits;syncAllOrbitsUi();});
syncSpeedUi();syncPauseUi();syncAllOrbitsUi();
resize();requestAnimationFrame(safeRender);
