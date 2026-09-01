const $=id=>document.getElementById(id);
function setMetric(name,val){$(name).textContent=val+'%';$(name+'bar').style.width=Math.max(0,Math.min(100,val))+'%'}
function render(d){
  $('signal').textContent=d.signal;
  $('confidence').textContent=d.confidence+'%';
  $('quality').textContent=d.quality;
  $('pairName').textContent=d.pair;
  $('price').textContent=d.price ? Number(d.price).toFixed(5) : '—';
  $('time').textContent=new Date().toLocaleTimeString();
  setMetric('trend',d.components.trend);
  setMetric('momentum',d.components.momentum);
  setMetric('structure',d.components.structure);
  setMetric('volatility',d.components.volatility);
}
function connect(){
  const proto=location.protocol==='https:'?'wss':'ws';
  const ws=new WebSocket(`${proto}://${location.host}/ws`);
  ws.onmessage=e=>render(JSON.parse(e.data));
  ws.onclose=()=>setTimeout(connect,1500);
}
connect();
