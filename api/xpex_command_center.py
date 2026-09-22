from flask import Blueprint, jsonify, request, Response
import os, urllib.request, json, time, re, threading
from pathlib import Path

bp = Blueprint("xpex_command_center", __name__)
DATA_FILE = Path(os.getenv("XPEX_DATA_FILE", "/tmp/xpex_command_center.json"))
SUPABASE_URL = os.getenv("XPEX_SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("XPEX_SUPABASE_PUBLISHABLE_KEY", "")

def _supabase(path, method="GET", payload=None):
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    url = SUPABASE_URL + "/functions/v1/xpex-core/" + path.lstrip("/")
    headers = {"apikey": SUPABASE_KEY, "Authorization": "Bearer " + SUPABASE_KEY, "Content-Type": "application/json"}
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=12) as r:
        return json.loads(r.read().decode() or "{}")

def _load_data():
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"assets":[],"opportunities":[],"jobs":[],"deliveries":[],"payments":[]}

def _save_data(data):
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def _id(prefix):
    return prefix + "-" + str(int(time.time()*1000))

PAGE = r"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>XPEX AI — Intelligence Command Center</title><style>
*{box-sizing:border-box}body{margin:0;background:#031023;color:#eef9ff;font:14px Arial,sans-serif}.app{display:grid;grid-template-columns:230px 1fr;min-height:100vh}.side{background:#020b18;border-right:1px solid #0b4c74;padding:22px}.brand{font-size:34px;font-weight:900}.brand b{color:#ff9b2f}.sub{color:#41d8ff;font-size:11px;font-weight:700}.nav{margin-top:30px}.nav a{display:block;padding:13px;border-radius:10px;margin:5px 0;color:#c9e8f7;text-decoration:none;border:1px solid transparent}.nav a:hover,.nav a.active{background:#07325a;border-color:#00b8ff;color:white}.main{padding:24px}.search{display:flex;gap:10px}.search input{flex:1;background:#071a31;border:1px solid #0878bb;border-radius:14px;padding:15px;color:white}.search button,.btn{background:#00c8ff;border:0;border-radius:12px;padding:12px 18px;font-weight:800;color:#02101e;cursor:pointer}.kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin:18px 0}.card,.hero,.ai,.panel{background:#061528;border:1px solid #0a66a0;border-radius:16px;padding:18px}.num{font-size:27px;font-weight:900}.muted{color:#8caabd}.grid{display:grid;grid-template-columns:1fr 350px;gap:16px}.hero h1{font-size:38px;margin:18px 0}.orange{color:#ff9b2f}.cyan{color:#36d9ff}.green{color:#25e99a}.red{color:#ff6b6b}.pipe{display:grid;grid-template-columns:repeat(6,1fr);gap:7px;margin-top:25px}.pipe button{border:1px solid #0878bb;background:#061528;color:white;border-radius:10px;padding:12px 6px;text-align:center;font-size:10px;cursor:pointer}.panel{margin-top:16px}.row{display:grid;grid-template-columns:120px 1fr 130px 100px;padding:12px;border-top:1px solid #12314a;gap:10px}.services{margin-top:18px}.svc{display:flex;justify-content:space-between;padding:7px 0}.hidden{display:none}.form{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}.form input,.form select{background:#071a31;border:1px solid #0878bb;border-radius:9px;padding:10px;color:white;min-width:180px}@media(max-width:900px){.app{grid-template-columns:1fr}.side{display:none}.kpis{grid-template-columns:1fr 1fr}.grid{grid-template-columns:1fr}.pipe{grid-template-columns:1fr 1fr 1fr}}</style></head>
<body><div class="app"><aside class="side"><div class="brand">XPEX <b>AI</b></div><div class="sub">INTELLIGENCE COMMAND CENTER</div><nav class="nav">
<a href="#inicio" data-view="inicio" class="active">⌂ Início</a><a href="#cenara" data-view="cenara">▶ Cenara</a><a href="#dify" data-view="dify">◈ Dify Brain</a><a href="#assets" data-view="assets">▣ Assets</a><a href="#opportunities" data-view="opportunities">◎ Oportunidades</a><a href="#jobs" data-view="jobs">□ Projetos / Execuções</a><a href="#finance" data-view="finance">$ Finanças</a><a href="#connectors" data-view="connectors">⇄ Conectores</a><a href="#settings" data-view="settings">⚙ Configurações</a></nav><div class="services"><b class="green">SISTEMA ONLINE</b><div id="svcs"></div></div></aside><main class="main">
<div class="search"><input id="q" placeholder="Cole URL, asset ou comando..."><button onclick="runInput()">EXECUTAR</button></div>
<div class="kpis"><div class="card"><div class="num" id="assetsK">0</div><div>Assets Catalogados</div></div><div class="card"><div class="num" id="jobsK">0</div><div>Execuções</div></div><div class="card"><div class="num" id="oppsK">0</div><div>Oportunidades Ativas</div></div><div class="card"><div class="num" id="revenueK">R$ 0.00</div><div>Receitas Confirmadas</div></div><div class="card"><div class="num" id="online">—</div><div>Serviços Online</div></div></div>
<section id="inicio" class="view"><div class="grid"><section class="hero"><div class="cyan">XPEX AI • ECOSSISTEMA INTELIGENTE</div><h1>DA IDEIA AO RESULTADO.<br><span class="orange">DO ASSET AO PAGAMENTO.</span></h1><p class="muted">Rastreie oportunidades, qualifique aderência, cruze com ativos existentes, execute, entregue e acompanhe receita real.</p><div class="pipe"><button onclick="show('opportunities')">01<br>RASTREAR</button><button onclick="show('opportunities')">02<br>QUALIFICAR</button><button onclick="show('assets')">03<br>CRUZAR ASSETS</button><button onclick="show('jobs')">04<br>EXECUTAR</button><button onclick="show('jobs')">05<br>ENTREGAR</button><button onclick="show('finance')">06<br>PAGAMENTO</button></div></section><aside class="ai"><b class="cyan">IA DO ECOSSISTEMA • ONLINE</b><p id="answer" style="line-height:1.6">Command Center conectado ao núcleo XPEX.</p></aside></div></section>
<section id="cenara" class="view hidden"><div class="panel"><h2>Cenara</h2><p>Motor de geração de mídia.</p><button class="btn" onclick="window.open('https://cenara-xpex-systems-production.up.railway.app','_blank')">ABRIR CENARA</button></div></section>
<section id="dify" class="view hidden"><div class="panel"><h2>Dify Brain</h2><p>Brain e API do Command Center estão operando neste serviço.</p><button class="btn" onclick="fetch('/xpex/api/health').then(r=>r.json()).then(x=>answer.textContent=JSON.stringify(x,null,2))">TESTAR BRAIN</button></div></section>
<section id="assets" class="view hidden"><div class="panel"><h2>Assets</h2><div class="form"><input id="assetName" placeholder="Nome do asset"><input id="assetUri" placeholder="URL/URI"><select id="assetType"><option>video</option><option>image</option><option>audio</option><option>document</option><option>code</option></select><button class="btn" onclick="addAsset()">CATALOGAR</button></div><div id="assetsList"></div></div></section>
<section id="opportunities" class="view hidden"><div class="panel"><h2>Oportunidades</h2><div class="form"><button class="btn" onclick="scanRadar()">⚡ ATIVAR RADAR REAL</button><span id="radarStatus" class="muted">Radar pronto para varredura.</span></div><div class="form"><input id="oppTitle" placeholder="Título"><input id="oppSource" placeholder="Fonte/URL"><input id="oppReward" placeholder="Recompensa"><button class="btn" onclick="addOpp()">REGISTRAR</button></div><div id="oppsList"></div></div></section>
<section id="jobs" class="view hidden"><div class="panel"><h2>Projetos / Execuções</h2><p class="muted">Execuções registradas no pipeline.</p><div id="jobsList"></div></div></section>
<section id="finance" class="view hidden"><div class="panel"><h2>Finanças</h2><p>Pagamentos confirmados alimentam Receita Confirmada.</p><div id="paymentsList"></div></div></section>
<section id="connectors" class="view hidden"><div class="panel"><h2>Conectores</h2><div id="connectorsList"></div></div></section>
<section id="settings" class="view hidden"><div class="panel"><h2>Configurações</h2><p>Persistência: <b>Supabase</b></p><p>Backend: <b>Dify Brain / Railway</b></p><p>Modo: <b class="green">MONETIZAÇÃO REAL</b></p></div></section>
</main></div><script>
const $=id=>document.getElementById(id);function show(id){document.querySelectorAll('.view').forEach(x=>x.classList.add('hidden'));$(id).classList.remove('hidden');document.querySelectorAll('.nav a').forEach(a=>a.classList.toggle('active',a.dataset.view===id));location.hash=id;loadView(id)}document.querySelectorAll('.nav a').forEach(a=>a.onclick=e=>{e.preventDefault();show(a.dataset.view)});
async function api(path,opt){let r=await fetch('/xpex/api/'+path,opt);let t=await r.text();let d;try{d=JSON.parse(t)}catch{d={error:t}}if(!r.ok)throw new Error(d.error||r.statusText);return d}
async function health(){try{let d=await api('health');$('online').textContent=d.online+'/'+d.services.length;$('svcs').innerHTML=d.services.map(s=>'<div class="svc"><span>'+s.name+'</span><span class="'+(s.status==='online'?'green':'red')+'">'+s.status+'</span></div>').join('');$('connectorsList').innerHTML=$('svcs').innerHTML}catch(e){}}
async function stats(){try{let d=await api('stats');$('assetsK').textContent=d.assets;$('jobsK').textContent=d.jobs;$('oppsK').textContent=d.opportunities;$('revenueK').textContent='R$ '+Number(d.revenue_brl||0).toFixed(2)}catch(e){}}
function rows(a,fields){return !a.length?'<p class="muted">Nenhum registro ainda.</p>':a.map(x=>'<div class="row">'+fields.map(f=>'<span>'+String(x[f]??'—')+'</span>').join('')+'</div>').join('')}
async function loadView(id){try{if(id==='assets')$('assetsList').innerHTML=rows(await api('assets'),['name','asset_type','source','created_at']);if(id==='opportunities')$('oppsList').innerHTML=rows(await api('opportunities'),['title','reward_text','status','source']);if(id==='jobs')$('jobsList').innerHTML=rows(await api('jobs'),['id','state','opportunity_id','created_at']);if(id==='finance')$('paymentsList').innerHTML=rows(await api('payments'),['amount','currency','status','tx_ref'])}catch(e){let el=$(id==='assets'?'assetsList':id==='opportunities'?'oppsList':id==='jobs'?'jobsList':'paymentsList');if(el)el.innerHTML='<p class="red">'+e.message+'</p>'}}
async function addAsset(){let x={name:$('assetName').value||'Asset',uri:$('assetUri').value,asset_type:$('assetType').value,source:'command-center'};await api('assets',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(x)});await stats();loadView('assets')}
async function scanRadar(){let s=$('radarStatus');s.textContent='Rastreando fontes públicas reais...';try{let d=await api('radar/scan',{method:'POST'});s.textContent='Radar: '+d.discovered+' encontradas • '+d.inserted+' novas registradas';await stats();await loadView('opportunities')}catch(e){s.textContent='Radar: '+e.message}}
async function addOpp(){let x={title:$('oppTitle').value||'Oportunidade',source:$('oppSource').value,reward_text:$('oppReward').value,status:'open'};await api('opportunities',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(x)});await stats();loadView('opportunities')}
async function runInput(){let q=$('q').value.trim();if(!q)return;$('answer').textContent='Processando '+q;try{if(/^https?:\/\//i.test(q)){await api('assets',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:q.split('/').filter(Boolean).pop()||'URL Asset',uri:q,asset_type:'link',source:new URL(q).hostname})});$('answer').textContent='Asset registrado no núcleo persistente. Abra Assets para visualizar.';await stats()}else{let d=await api('pipeline',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({command:q})});$('answer').textContent='Pipeline aceito: '+d.state}}catch(e){$('answer').textContent='Erro: '+e.message}}
health();stats();let initial=location.hash.slice(1);if(initial&&$(initial))show(initial);setInterval(()=>{health();stats()},30000)</script></body></html>"""

def _ping(name, url):
    try:
        with urllib.request.urlopen(url, timeout=4) as r:
            return {"name": name, "status": "online" if r.status < 500 else "degraded", "code": r.status}
    except Exception:
        return {"name": name, "status": "offline"}

@bp.get("/")
@bp.get("/xpex")
@bp.get("/xpex/")
def command_center():
    return Response(PAGE, mimetype="text/html")

@bp.get("/xpex/api/health")
def health():
    cenara=os.getenv("XPEX_CENARA_PUBLIC_URL","https://cenara-xpex-systems-production.up.railway.app/_stcore/health")
    services=[{"name":"Dify Brain","status":"online"},_ping("Cenara",cenara)]
    return jsonify({"ok":True,"online":sum(1 for s in services if s["status"]=="online"),"services":services,"timestamp":int(time.time())})

@bp.post("/xpex/api/pipeline")
def pipeline():
    data=request.get_json(silent=True) or {}
    return jsonify({"accepted":True,"pipeline":"rastreamento->qualificacao->assets->execucao->entrega->pagamento","input":data,"state":"QUALIFYING"})

# deployment trigger: GXEON Command Center root route 2026-09-22


@bp.get("/xpex/api/stats")
def stats():
    try:
        s=_supabase("stats")
        if s is not None:
            revenue=sum(float(p.get("amount",0) or 0) for p in s.get("revenue_confirmed",[]) if p.get("currency")=="BRL")
            return jsonify({"assets":s.get("assets",0),"opportunities":s.get("opportunities",0),"jobs":s.get("jobs",0),"deliveries":s.get("deliveries",0),"payments":s.get("payments",0),"revenue_brl":revenue,"storage":"supabase"})
    except Exception:
        pass
    d=_load_data()
    revenue=sum(float(p.get("amount_brl",0) or 0) for p in d["payments"] if p.get("status")=="confirmed")
    return jsonify({"assets":len(d["assets"]),"opportunities":len([o for o in d["opportunities"] if o.get("status","open")=="open"]),"jobs":len(d["jobs"]),"deliveries":len(d["deliveries"]),"payments":len(d["payments"]),"revenue_brl":revenue,"storage":"fallback"})

@bp.get("/xpex/api/assets")
def list_assets():
    try:
        x=_supabase("assets")
        if x is not None: return jsonify(x)
    except Exception: pass
    return jsonify(_load_data()["assets"])

@bp.get("/xpex/api/opportunities")
def list_opportunities():
    try:
        x=_supabase("opportunities")
        if x is not None: return jsonify(x)
    except Exception: pass
    return jsonify(_load_data()["opportunities"])

@bp.get("/xpex/api/jobs")
def list_jobs():
    try:
        x=_supabase("jobs")
        if x is not None: return jsonify(x)
    except Exception: pass
    return jsonify(_load_data()["jobs"])

@bp.get("/xpex/api/payments")
def list_payments():
    try:
        x=_supabase("payments")
        if x is not None: return jsonify(x)
    except Exception: pass
    return jsonify(_load_data()["payments"])

@bp.post("/xpex/api/assets")
def add_asset():
    item=request.get_json(silent=True) or {}
    try:
        x=_supabase("assets","POST",item)
        if x is not None: return jsonify(x),201
    except Exception: pass
    d=_load_data(); item["id"]=_id("AST"); item["created_at"]=int(time.time()); d["assets"].append(item); _save_data(d); return jsonify(item),201

@bp.post("/xpex/api/opportunities")
def add_opportunity():
    item=request.get_json(silent=True) or {}; item.setdefault("status","open")
    try:
        x=_supabase("opportunities","POST",item)
        if x is not None: return jsonify(x),201
    except Exception: pass
    d=_load_data(); item["id"]=_id("OPP"); item["created_at"]=int(time.time()); d["opportunities"].append(item); _save_data(d); return jsonify(item),201

@bp.post("/xpex/api/execute")
def execute_job():
    d=_load_data(); item=request.get_json(silent=True) or {}; job={"id":_id("JOB"),"opportunity_id":item.get("opportunity_id"),"asset_ids":item.get("asset_ids",[]),"state":"EXECUTING","created_at":int(time.time())}; d["jobs"].append(job); _save_data(d); return jsonify(job),202

@bp.post("/xpex/api/deliveries")
def add_delivery():
    d=_load_data(); item=request.get_json(silent=True) or {}; item["id"]=_id("DEL"); item["created_at"]=int(time.time()); d["deliveries"].append(item); _save_data(d); return jsonify(item),201

@bp.post("/xpex/api/payments")
def add_payment():
    d=_load_data(); item=request.get_json(silent=True) or {}; item["id"]=_id("PAY"); item.setdefault("status","pending"); item["created_at"]=int(time.time()); d["payments"].append(item); _save_data(d); return jsonify(item),201


# XPEX RADAR V1 — credential-free public-source discovery, no fabricated opportunities
RADAR_SOURCES=[{"name":"RustChain Bounties","url":"https://api.github.com/repos/Scottcjn/rustchain-bounties/issues?state=open&per_page=100&sort=updated&direction=desc"}]

def _radar_fetch(url):
    req=urllib.request.Request(url,headers={"Accept":"application/vnd.github+json","User-Agent":"XPEX-GXEON-Radar/1.0"})
    with urllib.request.urlopen(req,timeout=15) as r: return json.loads(r.read().decode())

def _reward_from_text(title, body=""):
    text=(title+"\n"+(body or ""))[:5000]
    m=re.search(r"(?:BOUNTY|REWARD)[^\n]{0,40}?(\d+(?:\.\d+)?(?:\s*[-–]\s*\d+(?:\.\d+)?)?)\s*(RTC|USD|USDC|USDT|ETH|BTC|BRL|R\$)",text,re.I)
    if not m: m=re.search(r"(\d+(?:\.\d+)?(?:\s*[-–]\s*\d+(?:\.\d+)?)?)\s*(RTC|USD|USDC|USDT|ETH|BTC|BRL|R\$)",text,re.I)
    return (m.group(1)+" "+m.group(2).upper()) if m else "ver fonte"

def _existing_opportunity_urls():
    try:
        x=_supabase("opportunities")
        if isinstance(x,list): return {str(i.get("source","")) for i in x}
    except Exception: pass
    return {str(i.get("source","")) for i in _load_data().get("opportunities",[])}

def _persist_radar_opportunity(item):
    try:
        x=_supabase("opportunities","POST",item)
        if x is not None: return True
    except Exception: pass
    d=_load_data(); item=dict(item); item["id"]=_id("OPP"); item["created_at"]=int(time.time()); d["opportunities"].append(item); _save_data(d); return True

@bp.get("/xpex/api/radar/status")
def radar_status():
    return jsonify({"enabled":os.getenv("XPEX_OPPORTUNITY_RADAR_ENABLED","false").lower()=="true","sources":[s["name"] for s in RADAR_SOURCES],"mode":"real-public-sources"})

def _radar_scan_data():
    if os.getenv("XPEX_OPPORTUNITY_RADAR_ENABLED","false").lower()!="true":
        return {"ok":False,"error":"radar_disabled","discovered":0,"inserted":0,"sources":len(RADAR_SOURCES),"errors":[],"mode":"DISABLED"}
    existing=_existing_opportunity_urls(); found=[]; errors=[]
    for source in RADAR_SOURCES:
        try:
            for issue in _radar_fetch(source["url"]):
                if issue.get("pull_request"): continue
                title=str(issue.get("title",""))
                title_l=title.strip().lower()
                if title_l.startswith(("claim:", "[bounty claim]", "[wallet]", "[tracking]", "📌 faq")):
                    continue
                body=str(issue.get("body") or "")
                hay=(title+" "+body[:1200]).lower()
                if "bounty" not in hay and "reward" not in hay and "payout" not in hay: continue
                url=str(issue.get("html_url") or "")
                if not url: continue
                reward=_reward_from_text(title,body)
                fit=95 if any(k in hay for k in ["video","youtube","short","bottube","content","distribution"]) else (85 if any(k in hay for k in ["agent","api","integration","mcp"]) else 70)
                found.append({
                    "external_id":str(issue.get("number","")),
                    "title":title,
                    "source":url,
                    "reward_text":reward,
                    "status":"open",
                    "fit_score":fit,
                    "metadata":{
                        "provider":source["name"],
                        "discovered_at":int(time.time()),
                        "html_url":url,
                        "labels":[str(x.get("name","")) for x in (issue.get("labels") or [])],
                        "updated_at":issue.get("updated_at"),
                    },
                })
        except Exception as ex:
            errors.append({"source":source["name"],"error":str(ex)[:180]})
    inserted=0
    for item in found:
        if item["source"] in existing: continue
        if _persist_radar_opportunity(item):
            inserted+=1
            existing.add(item["source"])
    return {"ok":True,"discovered":len(found),"inserted":inserted,"sources":len(RADAR_SOURCES),"errors":errors,"mode":"REAL"}

@bp.post("/xpex/api/radar/scan")
def radar_scan():
    data=_radar_scan_data()
    return jsonify(data), (200 if data.get("ok") else 503)

def _radar_startup_worker():
    time.sleep(4)
    try:
        data=_radar_scan_data()
        print("XPEX_RADAR_STARTUP "+json.dumps(data,ensure_ascii=False))
    except Exception as ex:
        print("XPEX_RADAR_STARTUP "+json.dumps({"ok":False,"error":str(ex)[:220]}))

if os.getenv("XPEX_RADAR_SCAN_ON_START","false").lower()=="true":
    threading.Thread(target=_radar_startup_worker,daemon=True,name="xpex-radar-startup").start()
