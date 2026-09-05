const $=id=>document.getElementById(id);
let ws, pair="EURUSD-OTC", timeframe="1m", scanTimer;

function setMetric(name,val){
  const n=Number(val)||0;
  $(name).textContent=n.toFixed(1)+"%";
  $(name+"bar").style.width=Math.max(0,Math.min(100,n))+"%";
}
function setScan(on=true){
  document.body.classList.toggle("scanning",on);
  $("scanState").textContent=on?"NEURAL SCAN ACTIVE":"ENGINE READY";
  $("scanRing").classList.toggle("active",on);
}
function render(d){
  if(d.type==="scan_start"){ setScan(true); return; }
  setScan(false);
  $("pairName").textContent=d.pair||pair;
  $("tfName").textContent=d.timeframe||timeframe;
  $("time").textContent=d.timestamp?new Date(d.timestamp*1000).toLocaleTimeString():"—";
  if(d.price!=null) $("price").textContent=Number(d.price).toFixed(5);

  const offline=!d.ok || d.signal==="FEED OFFLINE";
  $("signal").textContent=offline?"NO DATA":d.signal;
  $("confidence").textContent=(Number(d.confidence)||0).toFixed(1)+"%";
  $("quality").textContent=d.quality||"WAIT";
  $("feedStatus").textContent=offline?"FEED OFFLINE":"LIVE FEED";
  $("feedDot").classList.toggle("bad",offline);
  $("errorText").textContent=offline?(d.error||"Authorized live feed is not configured."):"";

  const c=d.components||{};
  setMetric("trend",c.trend);
  setMetric("momentum",c.momentum);
  setMetric("structure",c.structure);
  setMetric("volatility",c.volatility);
  document.querySelectorAll(".core b").forEach(x=>x.textContent=offline?"STANDBY":"ONLINE");
}
function connect(){
  const proto=location.protocol==="https:"?"wss":"ws";
  ws=new WebSocket(`${proto}://${location.host}/ws`);
  ws.onopen=()=>{ $("feedStatus").textContent="CONNECTING"; };
  ws.onmessage=e=>render(JSON.parse(e.data));
  ws.onclose=()=>{ setScan(false); $("feedStatus").textContent="RECONNECTING"; setTimeout(connect,1500); };
  ws.onerror=()=>ws.close();
}
document.querySelectorAll(".tabs button").forEach(btn=>{
  btn.addEventListener("click",()=>{
    document.querySelectorAll(".tabs button").forEach(b=>b.classList.remove("active"));
    btn.classList.add("active");
    timeframe=btn.dataset.tf;
    if(ws && ws.readyState===1) ws.close();
    setTimeout(connect,100);
  });
});
$("pair").addEventListener("change",e=>{
  pair=e.target.value;
  if(ws && ws.readyState===1) ws.close();
  setTimeout(connect,100);
});
$("rescan").addEventListener("click",()=>{
  setScan(true);
  if(ws && ws.readyState===1) ws.send(JSON.stringify({pair,timeframe}));
});
connect();
