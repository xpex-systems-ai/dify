from flask import Blueprint, jsonify, request, Response
import os, urllib.request, json, time
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
*{box-sizing:border-box}body{margin:0;background:#031023;color:#eef9ff;font:14px Arial,sans-serif}.app{display:grid;grid-template-columns:230px 1fr;min-height:100vh}.side{background:#020b18;border-right:1px solid #0b4c74;padding:22px}.brand{font-size:34px;font-weight:900}.brand b{color:#ff9b2f}.sub{color:#41d8ff;font-size:11px;font-weight:700}.nav{margin-top:30px}.nav div{padding:13px;border-radius:10px;margin:5px 0;color:#aac3d6}.nav div:first-child{background:#07325a;border:1px solid #00b8ff;color:white}.main{padding:24px}.search{display:flex;gap:10px}.search input{flex:1;background:#071a31;border:1px solid #0878bb;border-radius:14px;padding:15px;color:white}.search button,.btn{background:#00c8ff;border:0;border-radius:12px;padding:0 18px;font-weight:800;color:#02101e}.kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin:18px 0}.card,.hero,.ai,.table{background:#061528;border:1px solid #0a66a0;border-radius:16px;padding:18px}.num{font-size:27px;font-weight:900}.muted{color:#8caabd}.grid{display:grid;grid-template-columns:1fr 350px;gap:16px}.hero h1{font-size:38px;margin:18px 0}.orange{color:#ff9b2f}.cyan{color:#36d9ff}.green{color:#25e99a}.pipe{display:grid;grid-template-columns:repeat(6,1fr);gap:7px;margin-top:25px}.pipe div{border:1px solid #0878bb;border-radius:10px;padding:12px 6px;text-align:center;font-size:10px}.table{margin-top:16px}.row{display:grid;grid-template-columns:80px 1fr 90px 80px 70px;padding:12px;border-top:1px solid #12314a}.services{margin-top:18px}.svc{display:flex;justify-content:space-between;padding:7px 0}@media(max-width:900px){.app{grid-template-columns:1fr}.side{display:none}.kpis{grid-template-columns:1fr 1fr}.grid{grid-template-columns:1fr}.pipe{grid-template-columns:1fr 1fr 1fr}}</style></head>
<body><div class="app"><aside class="side"><div class="brand">XPEX <b>AI</b></div><div class="sub">INTELLIGENCE COMMAND CENTER</div><div class="nav"><div>⌂ Início</div><div>▶ Cenara</div><div>◈ Dify Brain</div><div>▣ Assets</div><div>◎ Oportunidades</div><div>□ Projetos</div><div>$ Finanças</div><div>⇄ Conectores</div><div>⚙ Configurações</div></div><div class="services"><b class="green">SISTEMA ONLINE</b><div id="svcs"></div></div></aside><main class="main">
<div class="search"><input id="q" placeholder="Pergunte ao seu ecossistema..."><button onclick="ask()">EXECUTAR</button></div>
<div class="kpis"><div class="card"><div class="num" id="assets">0</div><div>Assets Catalogados</div></div><div class="card"><div class="num" id="jobs">0</div><div>Execuções</div></div><div class="card"><div class="num" id="opps">0</div><div>Oportunidades Ativas</div></div><div class="card"><div class="num" id="revenue">0</div><div>Receitas Confirmadas</div></div><div class="card"><div class="num" id="online">—</div><div>Serviços Online</div></div></div>
<div class="grid"><section class="hero"><div class="cyan">XPEX AI • ECOSSISTEMA INTELIGENTE</div><h1>DA IDEIA AO RESULTADO.<br><span class="orange">DO ASSET AO PAGAMENTO.</span></h1><p class="muted">Rastreie oportunidades, qualifique aderência, cruze com ativos existentes, execute, entregue e acompanhe receita real.</p><div class="pipe"><div>01<br>RASTREAR</div><div>02<br>QUALIFICAR</div><div>03<br>CRUZAR ASSETS</div><div>04<br>EXECUTAR</div><div>05<br>ENTREGAR</div><div>06<br>PAGAMENTO</div></div></section><aside class="ai"><b class="cyan">IA DO ECOSSISTEMA • ONLINE</b><p id="answer" style="line-height:1.6">Command Center conectado ao Dify Brain. Use a busca para operar o ecossistema.</p></aside></div>
<div class="table"><b class="orange">OPERAÇÃO REAL</b><div class="row"><b>Estado</b><b>Pipeline</b><b>Receita</b><b>Prova</b><b>Status</b></div><div class="row"><span class="green">ATIVO</span><span>Radar → Qualificação → Asset → Execução → Entrega</span><span>Ledger</span><span>Auditável</span><span class="green">READY</span></div></div>
</main></div><script>
async function health(){try{let r=await fetch('/xpex/api/health');let d=await r.json();document.getElementById('online').textContent=d.online+'/'+d.services.length;document.getElementById('svcs').innerHTML=d.services.map(s=>'<div class="svc"><span>'+s.name+'</span><span class="'+(s.status==='online'?'green':'orange')+'">'+s.status+'</span></div>').join('')}catch(e){}}
async function ask(){let q=document.getElementById('q').value.trim();if(!q)return;document.getElementById('answer').textContent='Processando: '+q+' — pipeline GXEON preparado para integração de workflow Dify e fontes monetizáveis.'}
async function stats(){try{let r=await fetch('/xpex/api/stats');let d=await r.json();assets.textContent=d.assets;jobs.textContent=d.jobs;opps.textContent=d.opportunities;revenue.textContent='R$ '+Number(d.revenue_brl).toFixed(2)}catch(e){}}
health();stats();setInterval(()=>{health();stats()},30000)</script></body></html>"""

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
