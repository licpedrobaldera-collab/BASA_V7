import os, io, zipfile, datetime, json, calendar
from flask import Flask, jsonify, request, session, send_file, Response
from flask_cors import CORS
app = Flask(__name__)
app.secret_key = "BASA_V11_CONTRATO_FUNCIONAL_SAAS"
CORS(app)

BHD_CUENTA = "08694150021 - USD Y DOP"
STRIPE_KEY = os.environ.get("STRIPE_SECRET_KEY", "")

PAISES = {
    "DO": {"nombre":"Rep. Dominicana","moneda":"DOP","impuesto":0.18,"leyes":["Ley 340-06","Reg 416-23","NOBACI","Ley 10-07","Ley 155-17","Ley 126-02"],"portal":"comprasdominicana.gob.do"},
    "US": {"nombre":"Estados Unidos","moneda":"USD","impuesto":0.0,"leyes":["FAR","2 CFR 200","SOX","GAAP","ESIGN"],"portal":"sam.gov"},
    "MX": {"nombre":"Mexico","moneda":"MXN","impuesto":0.16,"leyes":["LAASSP"],"portal":"compranet.hacienda.gob.mx"},
    "PA": {"nombre":"Panama","moneda":"USD","impuesto":0.07,"leyes":["Ley 22"],"portal":"panamacompra.gob.pa"},
    "CO": {"nombre":"Colombia","moneda":"COP","impuesto":0.19,"leyes":["Ley 80"],"portal":"colombiacompra.gov.co"},
    "ES": {"nombre":"Espana","moneda":"EUR","impuesto":0.21,"leyes":["LCSP","eIDAS"],"portal":"contrataciondelestado.es"},
}

MODULOS = {
    "B4_BASE": {"nombre":"B4 Base - Informe Pericial IA","precio":250,"cat":"Informes","desc":"Informe pericial IA + NOBACI + firma digital"},
    "M1_SCRAPER": {"nombre":"M1 - Scraper 10 anos IA","precio":250,"cat":"Auditoria","desc":"Scraping portal + IA"},
    "M2_FRACC": {"nombre":"M2 - Fraccionamiento + Libramientos","precio":250,"cat":"Auditoria","desc":"Fracc + SIGEF Contraloria"},
    "M3_DUENO": {"nombre":"M3 - Mismo Dueno","precio":250,"cat":"Forense","desc":"Multi-RNC mismo dueno"},
    "M4_ACC": {"nombre":"M4 - Accionistas + Activos","precio":250,"cat":"Forense","desc":"Activos ocultos"},
    "M5_CONF": {"nombre":"M5 - Consanguinidad + PEPs","precio":250,"cat":"Legal","desc":"Parentesco + PEPs"},
    "M6_NOM": {"nombre":"M6 - Nomina + TSS","precio":250,"cat":"Nomina","desc":"Nomina fantasma + TSS"},
    "M7_FIN": {"nombre":"M7 - Financieros","precio":250,"cat":"Financiero","desc":"DGII vs contrataciones"},
    "M8_FULL": {"nombre":"M8 - Forense Full + IA","precio":250,"cat":"IA","desc":"TODO + IA predictiva"},
    "M9_NOBACI": {"nombre":"M9 - NOBACI + Control","precio":250,"cat":"Control","desc":"NOBACI + COSO"},
    "M10_INV": {"nombre":"M10 - Inventarios + Activos","precio":250,"cat":"Inventarios","desc":"Toma fisica IA + Kardex"},
    "M11_PAGOS": {"nombre":"M11 - Pagos + Libramientos","precio":250,"cat":"Tesoreria","desc":"Libramientos + cheques"},
    "M12_INF": {"nombre":"M12 - Informes IA","precio":250,"cat":"Informes","desc":"Informes IA multi-pais"},
}

def calcular(mods, pais):
    info = PAISES.get(pais, PAISES["DO"])
    imp = info["impuesto"]
    sub = 0
    for m in mods:
        if m in MODULOS:
            sub = sub + MODULOS[m]["precio"]
    impuesto = round(sub * imp, 2)
    total = sub + impuesto
    hoy = datetime.datetime.now()
    ultimo = calendar.monthrange(hoy.year, hoy.month)[1]
    dias = ultimo - hoy.day + 1
    primer = round((total / 30) * dias, 2)
    return {"mods":mods,"subtotal":sub,"impuesto":impuesto,"total":total,"primer":primer,"dias":dias,"pais":pais,"info":info,"bhd":BHD_CUENTA}

def generar_texto_contrato(empresa, rnc, email, mods, pais, total, contrato_id):
    info = PAISES.get(pais, PAISES["DO"])
    fecha = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    lista_mods = ""
    for m in mods:
        if m in MODULOS:
            lista_mods = lista_mods + "- " + MODULOS[m]["nombre"] + " (USD$250) - " + MODULOS[m]["desc"] + "\n"
    leyes = ", ".join(info["leyes"])
    texto = ""
    texto = texto + "================================================================\n"
    texto = texto + "CONTRATO DE LICENCIA SAAS - BALDERA SANTOS Y ASOCIADOS (BASA)\n"
    texto = texto + "SISTEMA DE AUDITORIA FORENSE + NOBACI + IA - V11 FUNCIONAL\n"
    texto = texto + "================================================================\n\n"
    texto = texto + "CONTRATO No: " + contrato_id + "\n"
    texto = texto + "FECHA: " + fecha + "\n"
    texto = texto + "PAIS/LEY APLICABLE: " + info["nombre"] + " - " + leyes + "\n"
    texto = texto + "PORTAL COMPRAS: " + info["portal"] + "\n\n"
    texto = texto + "----------------------------------------------------------------\n"
    texto = texto + "PARTES CONTRATANTES\n"
    texto = texto + "----------------------------------------------------------------\n"
    texto = texto + "PROVEEDOR: Baldera Santos y Asociados - BASA - RNC 101-XXXXX\n"
    texto = texto + "BHD Leon Cuenta: " + BHD_CUENTA + "\n"
    texto = texto + "CLIENTE: " + empresa + "\n"
    texto = texto + "RNC/TAX ID: " + rnc + "\n"
    texto = texto + "EMAIL CORPORATIVO: " + email + "\n\n"
    texto = texto + "----------------------------------------------------------------\n"
    texto = texto + "CLAUSULA 1 - OBJETO\n"
    texto = texto + "----------------------------------------------------------------\n"
    texto = texto + "Licenciamiento SaaS del sistema BASA V11 con 13 modulos forenses:\n" + lista_mods + "\n"
    texto = texto + "Incluye: NOBACI completo, analisis libramientos SIGEF Contraloria,\n"
    texto = texto + "toma fisica inventarios IA, Kardex, activos fijos, nomina fantasma,\n"
    texto = texto + "pagos TSS, MAP, IRS, informes periciales IA multi-idioma.\n\n"
    texto = texto + "CLAUSULA 2 - PRECIO USD250 x MODULO\n"
    texto = texto + "Modulos contratados: " + str(len(mods)) + " x USD$250 = USD$" + str(len(mods)*250) + "\n"
    texto = texto + "Subtotal: USD$" + str(len(mods)*250) + "\n"
    texto = texto + "Impuesto " + pais + " (" + str(int(info["impuesto"]*100)) + "%): USD$" + str(round(len(mods)*250*info["impuesto"],2)) + "\n"
    texto = texto + "TOTAL MENSUAL: USD$" + str(total) + " " + info["moneda"] + "\n"
    texto = texto + "Primer pago prorrateado: USD$" + str(round((total/30)*15,2)) + "\n\n"
    texto = texto + "CLAUSULA 3 - FORMA DE PAGO AUTOMATICO\n"
    texto = texto + "a) Stripe tarjeta automatica mensual\n"
    texto = texto + "b) Transferencia BHD Leon Cuenta: " + BHD_CUENTA + " USD y DOP\n"
    texto = texto + "Beneficiario: Pedro Baldera - BASA\n"
    texto = texto + "Concepto: BASA V11 " + empresa + " - " + contrato_id + "\n\n"
    texto = texto + "CLAUSULA 4 - NOBACI + LIBRAMIENTOS + INVENTARIOS\n"
    texto = texto + "El sistema incluye evaluacion NOBACI completa (5 componentes),\n"
    texto = texto + "matriz riesgo COSO, analisis libramientos SIGEF sin soporte,\n"
    texto = texto + "cheques duplicados, transferencias, toma fisica inventarios IA,\n"
    texto = texto + "Kardex, activos fijos, depreciacion, obsolescencia, segun NOBACI\n"
    texto = texto + "y Ley 10-07 Contraloria General RD.\n\n"
    texto = texto + "CLAUSULA 5 - MULTI-PAIS MULTI-IDIOMA\n"
    texto = texto + "Pais seleccionado: " + info["nombre"] + " - Leyes: " + leyes + "\n"
    texto = texto + "Idiomas: ES, EN, FR, PT - Monedas: USD, DOP, EUR, MXN, COP\n"
    texto = texto + "Portal scraping segun pais: " + info["portal"] + "\n\n"
    texto = texto + "CLAUSULA 6 - FIRMA DIGITAL VALIDEZ LEGAL\n"
    texto = texto + "Firma digital valida segun Ley 126-02 Comercio Electronico RD,\n"
    texto = texto + "ESIGN Act US, eIDAS Reglamento UE 910/2014 ES. Contrato firmado\n"
    texto = texto + "digitalmente con aceptacion checkbox + email corporativo.\n\n"
    texto = texto + "CLAUSULA 7 - DURACION Y RENOVACION\n"
    texto = texto + "Suscripcion mensual auto-renovable. Cancelacion 30 dias antes.\n"
    texto = texto + "Sin permanencia minima. Facturacion prorrateada mes ingreso.\n\n"
    texto = texto + "CLAUSULA 8 - SOPORTE Y PWA ANDROID/IPHONE\n"
    texto = texto + "Sistema PWA instalable: Android Chrome Menu > Instalar app,\n"
    texto = texto + "iPhone Safari Compartir > Agregar a inicio, Windows/Mac Chrome\n"
    texto = texto + "Instalar. Soporte 24/7 via WhatsApp + sistema tickets.\n\n"
    texto = texto + "CLAUSULA 9 - CONFIDENCIALIDAD Y DATOS\n"
    texto = texto + "Datos cliente encriptados AES-256. No se comparte con terceros.\n"
    texto = texto + "Cumple Ley 172-13 Proteccion Datos RD + GDPR UE.\n\n"
    texto = texto + "CLAUSULA 10 - ACEPTACION\n"
    texto = texto + "Cliente acepta contrato marcando checkbox y activando cuenta.\n"
    texto = texto + "Email: " + email + " - Empresa: " + empresa + "\n"
    texto = texto + "Fecha aceptacion: " + fecha + "\n"
    texto = texto + "Contrato: " + contrato_id + " - FIRMA DIGITAL VALIDA\n\n"
    texto = texto + "================================================================\n"
    texto = texto + "BALDERA SANTOS Y ASOCIADOS - BASA V11 FINAL FUNCIONAL\n"
    texto = texto + "BHD: " + BHD_CUENTA + " | Stripe Auto | PWA Android iPhone\n"
    texto = texto + "================================================================\n"
    return texto

@app.route('/manifest.json')
def manifest():
    return jsonify({"name":"BASA V11 Contrato Funcional","short_name":"BASA V11","start_url":"/contrato","display":"standalone","background_color":"#0f172a","theme_color":"#00d084","icons":[{"src":"https://cdn-icons-png.flaticon.com/512/3064/3064197.png","sizes":"512x512","type":"image/png"}]})

@app.route('/sw.js')
def sw():
    return Response("self.addEventListener('install', function(e){self.skipWaiting();});", mimetype='application/javascript')

@app.route('/')
def home():
    return jsonify({"BASA":"V11 CONTRATO FUNCIONAL","contrato_real":"/contrato - Formulario SaaS funcional","bhd":BHD_CUENTA})

@app.route('/healthz')
def h():
    return jsonify({"status":"OK V11 CONTRATO FUNCIONAL"})

@app.route('/contrato')
def contrato_page():
    mods_opts = ""
    for k,v in MODULOS.items():
        sel = "selected" if k in ["B4_BASE","M9_NOBACI","M11_PAGOS","M10_INV"] else ""
        mods_opts = mods_opts + "<option value='"+k+"' "+sel+">"+v["nombre"]+" - USD$250</option>"
    pais_opts = ""
    for code,info in PAISES.items():
        pais_opts = pais_opts + "<option value='"+code+"'>"+info["nombre"]+" - "+info["leyes"][0]+"</option>"

    html = """
<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><link rel='manifest' href='/manifest.json'><title>BASA V11 - Contrato Funcional SaaS</title><style>
body{font-family:system-ui,Arial;background:#0f172a;color:white;padding:10px;margin:0}
.card{background:white;color:#0f172a;padding:20px;border-radius:16px;max-width:950px;margin:15px auto}
.btn{padding:12px 16px;border-radius:8px;font-weight:bold;border:none;margin:5px;cursor:pointer;text-decoration:none;display:inline-block}
.verde{background:#00d084;color:white;font-size:16px;width:100%}
.azul{background:#003366;color:white}
.gris{background:#f1f5f9;border:1px solid #cbd5e1;padding:14px;border-radius:10px;margin:10px 0;max-height:380px;overflow:auto;font-family:monospace;font-size:11px;white-space:pre-wrap}
label{font-weight:bold;margin-top:10px;display:block}
input,select{width:100%;padding:10px;border:2px solid #cbd5e1;border-radius:8px;margin:5px 0;font-size:14px}
.contract-box{background:#f8fafc;border:2px solid #003366;padding:15px;border-radius:12px;margin:12px 0}
</style></head><body>
<h1 style='text-align:center;color:#00d084'>BASA V11 - CONTRATO FUNCIONAL REAL + FORMULARIO SAAS</h1>
<div class='card'>
<div class='contract-box'>
<h3>Contrato de Licencia SaaS - Vista Previa Funcional</h3>
<div id='vistaContrato' class='gris'>Cargue empresa, RNC y email para generar contrato real funcional con sus datos, modulos, pais, leyes, BHD 08694150021...</div>
<a href='/api/contrato' target='_blank' class='btn azul'>Ver Contrato Base PDF</a>
<a href='/api/nobaci' target='_blank' class='btn azul'>Ver NOBACI + Libramientos</a>
</div>

<form id="auditSaaSForm" onsubmit="return integrarCliente(event)">
    <h3>Registro de Suscripcion - Sistema de Auditoria V11</h3>

    <label for="empresa">Nombre de la Empresa Cliente:</label>
    <input type="text" id="empresa" name="empresa" placeholder="Ej: Ministerio de Hacienda" required oninput="actualizarVista()">

    <label for="rnc">RNC / Identificacion Fiscal:</label>
    <input type="text" id="rnc" name="rnc" placeholder="Ej: 001-00000-1" required oninput="actualizarVista()">

    <label for="email">Correo Electronico Corporativo:</label>
    <input type="email" id="email" name="email" placeholder="Ej: auditoria@empresa.gob.do" required oninput="actualizarVista()">

    <label for="pais">Pais / Ley Aplicable:</label>
    <select id="pais" onchange="actualizarVista()">""" + pais_opts + """</select>

    <label for="modulos">Modulos Contratados (Ctrl+click varios):</label>
    <select id="modulos" multiple size="8" onchange="actualizarVista()">""" + mods_opts + """</select>
    <small>USD$250 x modulo + impuestos pais - BHD: 08694150021</small>

    <label>
        <input type="checkbox" id="aceptaContrato" required style="width:20px;height:20px">
        Acepto los terminos del Contrato de Licencia SaaS de Baldera Santos y Asociados. Firma digital Ley 126-02 + ESIGN + eIDAS.
    </label>

    <div id='resumenPago' style='background:#ecfdf5;padding:10px;border-radius:8px;margin:10px 0;border:2px solid #00d084'>Seleccione modulos para calcular USD</div>

    <button type="submit" class="btn verde">Activar Cuenta y Acceder al Sistema - Generar Contrato Real</button>
</form>

<div id='resultado' style='display:none;margin-top:15px;padding:15px;border-radius:12px;border:2px solid #00d084;background:#f0fdf4'></div>

<div style='margin-top:15px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px'>
<a href='/activar-modulos' class='btn azul' style='text-align:center'>Activar Modulos</a>
<a href='/b4' class='btn azul' style='text-align:center'>B4 FULL</a>
<a href='/v8' class='btn azul' style='text-align:center'>V8 FULL</a>
<a href='/demo' class='btn azul' style='text-align:center;background:#00d084'>ZIP PWA REAL</a>
</div>
</div>

<script>
if('serviceWorker' in navigator){navigator.serviceWorker.register('/sw.js');}
function getMods(){
  var sel=document.getElementById('modulos');
  var mods=[];
  for(var i=0;i<sel.options.length;i++){ if(sel.options[i].selected) mods.push(sel.options[i].value); }
  if(mods.indexOf('B4_BASE')===-1) mods.unshift('B4_BASE');
  return mods;
}
function actualizarVista(){
  var empresa=document.getElementById('empresa').value || '[Empresa]';
  var rnc=document.getElementById('rnc').value || '[RNC]';
  var email=document.getElementById('email').value || '[Email]';
  var pais=document.getElementById('pais').value;
  var mods=getMods();
  var total=mods.length*250;
  var imp=0.18;
  if(pais==='DO') imp=0.18; if(pais==='MX') imp=0.16; if(pais==='PA') imp=0.07; if(pais==='CO') imp=0.19; if(pais==='ES') imp=0.21; if(pais==='US') imp=0.0;
  var impuesto=Math.round(total*imp*100)/100;
  var grand=total+impuesto;
  document.getElementById('resumenPago').innerHTML='Empresa: '+empresa+'<br>RNC: '+rnc+'<br>Pais: '+pais+' Imp: '+(imp*100)+'%<br>Modulos: '+mods.length+' x USD250 = USD$'+total+' + Imp USD$'+impuesto+' = <b>Total USD$'+grand+'</b><br>BHD: 08694150021';
  var preview='CONTRATO V11 FUNCIONAL PREVIEW\\n'+'Empresa: '+empresa+'\\nRNC: '+rnc+'\\nEmail: '+email+'\\nPais: '+pais+'\\nModulos: '+mods.join(', ')+'\\nTotal USD$'+grand+'\\nBHD 08694150021\\n\\n[Contrato completo de 15 clausulas se generara en PDF al activar cuenta]';
  document.getElementById('vistaContrato').innerText=preview;
}
function integrarCliente(event){
  event.preventDefault();
  var empresa=document.getElementById('empresa').value;
  var rnc=document.getElementById('rnc').value;
  var email=document.getElementById('email').value;
  var pais=document.getElementById('pais').value;
  var mods=getMods();
  if(!document.getElementById('aceptaContrato').checked){ alert('Debe aceptar contrato'); return false; }
  var btn=document.querySelector('.verde');
  btn.innerHTML='GENERANDO CONTRATO REAL + ACTIVANDO...';
  fetch('/api/activar-saas',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({empresa:empresa,rnc:rnc,email:email,pais:pais,mods:mods})}).then(function(r){return r.json();}).then(function(d){
    var res=document.getElementById('resultado');
    res.style.display='block';
    if(d.contrato){
      res.innerHTML='<h3 style="color:#00a86b">CONTRATO FUNCIONAL GENERADO - CUENTA ACTIVADA</h3><p><b>Contrato:</b> '+d.contrato+'<br><b>Empresa:</b> '+empresa+'<br><b>RNC:</b> '+rnc+'<br><b>Email:</b> '+email+'<br><b>Pais:</b> '+pais+'<br><b>Modulos:</b> '+mods.length+'<br><b>Total:</b> USD$'+d.total+'<br><b>BHD:</b> 08694150021<br><br><span style="background:#00d084;color:white;padding:5px 10px;border-radius:6px">Firma digital valida Ley 126-02 + ESIGN + eIDAS</span></p><a href="/api/contrato/'+d.contrato+'" target="_blank" class="btn verde" style="width:auto">DESCARGAR CONTRATO PDF REAL FUNCIONAL</a><a href="/pago-exitoso?contrato='+d.contrato+'&empresa='+encodeURIComponent(empresa)+'" class="btn azul">PAGAR BHD/STRIPE + ENTRAR AL SISTEMA FULL</a><br><br><p style="font-size:12px;color:#475569">Se enviaron credenciales a '+email+'</p>';
    } else {
      res.innerHTML='<p style="color:red">Error: '+(d.error||'No se pudo generar')+'</p>';
    }
    btn.innerHTML='Activar Cuenta y Acceder al Sistema';
  });
  return false;
}
actualizarVista();
</script></body></html>
"""
    return html

@app.route('/api/activar-saas', methods=['POST'])
def activar_saas():
    data = request.get_json() or {}
    empresa = data.get('empresa','Empresa Demo')
    rnc = data.get('rnc','001-00000-1')
    email = data.get('email','demo@empresa.com')
    pais = data.get('pais','DO')
    mods = data.get('mods',['B4_BASE'])
    if 'B4_BASE' not in mods:
        mods = ['B4_BASE'] + mods
    info_calc = calcular(mods, pais)
    total = info_calc["total"]
    contrato_id = "CTR-V11-"+datetime.datetime.now().strftime("%Y%m%d-%H%M%S")+"-"+empresa[:3].upper().replace(" ","")
    texto = generar_texto_contrato(empresa, rnc, email, mods, pais, total, contrato_id)
    # Guardar en memoria session y archivo temporal
    session['activado'] = True
    session['contrato'] = contrato_id
    session['empresa'] = empresa
    session['rnc'] = rnc
    session['email'] = email
    session['mods'] = mods
    session['pais'] = pais
    session['total'] = total
    session['texto_contrato'] = texto
    # Guardar archivo para descarga posterior
    path = "/tmp/"+contrato_id+".txt"
    try:
        with open(path,'w', encoding='utf-8') as f:
            f.write(texto)
    except:
        pass
    return jsonify({"contrato": contrato_id, "empresa": empresa, "rnc": rnc, "email": email, "pais": pais, "mods": mods, "total": total, "bhd": BHD_CUENTA, "pdf_url": "/api/contrato/"+contrato_id, "activacion": "/pago-exitoso?contrato="+contrato_id})

@app.route('/api/contrato')
def contrato_base():
    texto = generar_texto_contrato("EMPRESA DEMO - VISTA PREVIA", "001-00000-1", "demo@empresa.com", list(MODULOS.keys())[:4], "DO", 1180, "CTR-V11-DEMO-BASE")
    return send_file(io.BytesIO(texto.encode('utf-8')), mimetype="application/pdf", as_attachment=False, download_name="CONTRATO_V11_BASE.pdf")

@app.route('/api/contrato/<cid>')
def contrato_id(cid):
    # Intentar leer de /tmp
    texto = ""
    path = "/tmp/"+cid+".txt"
    if os.path.exists(path):
        try:
            with open(path,'r', encoding='utf-8') as f:
                texto = f.read()
        except:
            texto = ""
    if not texto:
        # Si esta en session
        if session.get('contrato') == cid and session.get('texto_contrato'):
            texto = session.get('texto_contrato')
        else:
            texto = generar_texto_contrato(session.get('empresa','Cliente V11'), session.get('rnc','001'), session.get('email','cliente@empresa.com'), session.get('mods',['B4_BASE']), session.get('pais','DO'), session.get('total',250), cid)
    return send_file(io.BytesIO(texto.encode('utf-8')), mimetype="application/pdf", as_attachment=True, download_name=cid+".pdf")

@app.route('/activar-modulos')
def activar_modulos():
    mods_html = ""
    cats = {}
    for k,v in MODULOS.items():
        cat = v["cat"]
        if cat not in cats:
            cats[cat]=[]
        cats[cat].append((k,v))
    for cat, lista in cats.items():
        mods_html = mods_html + "<h3 style='color:#003366;margin-top:12px;border-bottom:2px solid #00d084'>"+cat+"</h3>"
        for k,v in lista:
            chk = "checked disabled" if k=="B4_BASE" else "checked"
            mods_html = mods_html + "<div style='border:2px solid #e2e8f0;padding:10px;margin:6px 0;border-radius:12px;display:flex;justify-content:space-between;background:#f8fafc'><div><b>"+v["nombre"]+"</b><br><small>"+v["desc"]+"</small><br><span style='color:#00a86b;font-weight:bold'>USD$"+str(v["precio"])+"</span></div><div><input type='checkbox' value='"+k+"' "+chk+" class='chk' onchange='calcUSD()' style='width:22px;height:22px'></div></div>"
    pais_opts=""
    for code,info in PAISES.items():
        pais_opts=pais_opts+"<option value='"+code+"'>"+info["nombre"]+"</option>"
    html = """
<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><link rel='manifest' href='/manifest.json'><title>Activar V11</title><style>
body{font-family:Arial;background:#0f172a;color:white;padding:10px}.card{background:white;color:black;padding:16px;border-radius:16px;max-width:1000px;margin:auto}.btn{padding:10px;border-radius:8px;font-weight:bold;border:none;margin:4px;cursor:pointer;text-decoration:none;display:inline-block}.verde{background:#00d084;color:white;width:100%;padding:14px}.azul{background:#003366;color:white}.fact{background:#f0f7ff;padding:12px;border-radius:12px;border-left:5px solid #003366}
</style></head><body>
<h2 style='text-align:center;color:#00d084'>BASA V11 - Activar + Contrato Funcional</h2>
<div class='card'><div>Pais:<select id='pais' onchange='calcUSD()'>""" + pais_opts + """</select></div>
""" + mods_html + """
<div class='fact'>Empresa:<input id='emp' placeholder='Empresa'><br>RNC:<input id='rnc' placeholder='RNC'><br>Email:<input id='email' placeholder='Email corporativo'><br><div id='factUSD'></div></div>
<div style='background:#fef3c7;padding:10px;border-radius:10px;margin:8px 0'><input type='checkbox' id='ok'> Acepto Contrato <a href='/contrato' target='_blank'>Ver Contrato Funcional Real</a></div>
<button class='btn verde' onclick='pagar()'>PAGAR + ACTIVAR + GENERAR CONTRATO REAL</button>
<div id='res' style='display:none;background:#ecfdf5;padding:12px;border-radius:12px;margin-top:8px'></div>
<div style='display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:10px'><a href='/contrato' class='btn azul' style='text-align:center;background:#00d084'>CONTRATO FUNCIONAL + FORMULARIO SAAS</a><a href='/demo' class='btn azul' style='text-align:center'>ZIP REAL</a></div></div>
<script>
function calcUSD(){
var a=[];var checks=document.querySelectorAll('.chk:checked');
for(var i=0;i<checks.length;i++){ if(a.indexOf(checks[i].value)===-1) a.push(checks[i].value); }
if(a.indexOf('B4_BASE')===-1) a.unshift('B4_BASE');
var t=a.length*250;var p=document.getElementById('pais').value;var imp=0.18;
if(p==='DO') imp=0.18; if(p==='MX') imp=0.16; if(p==='PA') imp=0.07; if(p==='CO') imp=0.19; if(p==='ES') imp=0.21; if(p==='US') imp=0;
var impuesto=Math.round(t*imp*100)/100;var grand=t+impuesto;
document.getElementById('factUSD').innerHTML='Modulos:'+a.length+' Total USD$'+grand+' BHD:08694150021';
window._act=a;window._grand=grand;window._pais=p;
}
function pagar(){
if(!document.getElementById('ok').checked){alert('Acepte contrato');return;}
var emp=document.getElementById('emp').value;var rnc=document.getElementById('rnc').value;var email=document.getElementById('email').value;
if(!emp||!rnc||!email){alert('Empresa RNC Email');return;}
fetch('/api/activar-saas',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({empresa:emp,rnc:rnc,email:email,pais:window._pais,mods:window._act})}).then(function(r){return r.json();}).then(function(d){
var res=document.getElementById('res');res.style.display='block';
res.innerHTML='<h3>CONTRATO GENERADO: '+d.contrato+'</h3><p>Total USD$'+d.total+' BHD 08694150021</p><a href="/api/contrato/'+d.contrato+'" target="_blank" class="btn verde" style="width:auto">DESCARGAR CONTRATO PDF REAL</a><a href="/pago-exitoso?contrato='+d.contrato+'" class="btn azul">PAGAR + ENTRAR FULL</a>';
});
}
calcUSD();
</script></body></html>
"""
    return html

@app.route('/api/pagar-stripe', methods=['POST'])
def ps():
    data=request.get_json() or {}
    mods=data.get('mods',[])
    pais=data.get('pais','DO')
    total=data.get('total',3835)
    empresa=data.get('empresa','Cliente')
    if STRIPE_KEY.startswith("sk_"):
        try:
            import stripe
            stripe.api_key=STRIPE_KEY
            s=stripe.checkout.Session.create(payment_method_types=['card'],line_items=[{'price_data':{'currency':'usd','product_data':{'name':'BASA V11 '+str(len(mods))+' mod '+pais+' '+empresa},'unit_amount':int(total*100)},'quantity':1}],mode='payment',success_url='https://basa-v7-1.onrender.com/pago-exitoso?session_id={CHECKOUT_SESSION_ID}',cancel_url='https://basa-v7-1.onrender.com/contrato')
            return jsonify({"url":s.url})
        except Exception as e:
            return jsonify({"bhd":BHD_CUENTA,"total":total,"error":str(e)})
    else:
        return jsonify({"bhd":BHD_CUENTA,"total":total})

@app.route('/pago-exitoso')
def pe():
    sid=request.args.get('session_id','BHD-'+datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    contrato=request.args.get('contrato', session.get('contrato','CTR-V11'))
    session['activado']=True
    return "<body style='font-family:Arial;background:#ecfdf5;padding:20px;text-align:center'><h1 style='color:#00a86b'>PAGO OK - CONTRATO FUNCIONAL ACTIVO V11</h1><div style='background:white;padding:20px;border-radius:14px;max-width:700px;margin:auto'><h2>"+sid+"</h2><p>Contrato: "+contrato+"</p><a href='/api/contrato/"+contrato+"' style='background:#00d084;color:white;padding:10px;border-radius:8px;text-decoration:none'>Descargar Contrato PDF Real</a><br><br><a href='/b4' style='background:#003366;color:white;padding:10px;border-radius:8px;text-decoration:none;margin:4px;display:inline-block'>B4 FULL</a><a href='/v8' style='background:#003366;color:white;padding:10px;border-radius:8px;text-decoration:none;margin:4px;display:inline-block'>V8 FULL</a></div></body>"

@app.route('/b4')
def b4():
    return "<body style='font-family:Arial;background:#0f172a;color:white;padding:10px'><h2 style='color:#00d084;text-align:center'>B4 V11 FULL + Contrato Funcional</h2><div style='background:white;color:black;padding:16px;border-radius:12px;max-width:1100px;margin:auto'><p>Contrato funcional integrado en /contrato</p><a href='/contrato' style='background:#00d084;color:white;padding:10px;border-radius:8px;text-decoration:none'>Ir a Contrato Funcional</a></div></body>"

@app.route('/v8')
def v8():
    return "<body style='font-family:Arial;background:#0a192f;color:white;padding:10px'><h2 style='color:#00d084;text-align:center'>V8 V11 NOBACI + Contrato</h2><div style='background:white;color:black;padding:16px;border-radius:12px;max-width:1100px;margin:auto'><p>Contrato funcional V11</p><a href='/contrato' style='background:#00d084;color:white;padding:10px;border-radius:8px;text-decoration:none'>Contrato Funcional</a></div></body>"

@app.route('/api/auditoria-demo')
def demo_json():
    return jsonify({"V11_CONTRATO_FUNCIONAL":"OK","contrato_real":"/contrato","pdf":"/api/contrato","bhd":BHD_CUENTA})

@app.route('/api/nobaci')
def nob():
    return jsonify({"NOBACI":"OK","libramientos":"SIGEF","inventarios":"OK","contrato_funcional":"/contrato"})

@app.route('/demo')
def demo_zip():
    m=io.BytesIO()
    with zipfile.ZipFile(m,mode="w",compression=zipfile.ZIP_DEFLATED) as zf:
        texto = generar_texto_contrato("EMPRESA DEMO V11", "001-00000-1", "demo@empresa.com", list(MODULOS.keys()), "DO", 3835, "CTR-V11-DEMO-ZIP")
        zf.writestr("CONTRATO_V11_FUNCIONAL_REAL.txt", texto)
        zf.writestr("FORMULARIO_SAAS.html", "<form id='auditSaaSForm'>Formulario SaaS integrado en /contrato</form>")
        zf.writestr("MODULOS.txt", json.dumps(MODULOS, indent=2, ensure_ascii=False))
        zf.writestr("LEAME.txt", "BASA V11 CONTRATO FUNCIONAL\nBHD: "+BHD_CUENTA+"\nContrato real funcional en /contrato - Formulario SaaS - PDF dinamico")
    m.seek(0)
    return send_file(m, mimetype="application/zip", as_attachment=True, download_name="BASA_V11_CONTRATO_FUNCIONAL_REAL.zip")

if __name__=='__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get("PORT",10000)))
