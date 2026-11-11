"""Writes the HTML of the design system sheet from the tokens and the checks of design_system.py."""
import html
import re
from pathlib import Path


def icon(design, name, size=20, color="currentColor"):
    svg = (design / "icons" / f"{name}.svg").read_text(encoding="utf-8")
    inner = re.search(r">\s*(<(?:path|circle|rect|line|polyline|polygon|ellipse).*)</svg>", svg, re.S).group(1)
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{inner}</svg>'


def write(out, ds, fonts):
    T = ds.tok
    D = ds.DESIGN
    face = ""
    if fonts:
        f = Path(fonts).resolve().as_posix()
        face = f'@font-face{{font-family:Outfit;src:url("file:///{f}/Outfit.ttf");font-weight:100 900}}@font-face{{font-family:"Roboto Mono";src:url("file:///{f}/RobotoMono.ttf");font-weight:100 700}}'
    ic = lambda n, s=20, c="currentColor": icon(D, n, s, c)
    var = {
        "canvas": T("surface/canvas"), "card": T("surface/card"), "muted": T("surface/muted"), "border": T("surface/border"),
        "t1": T("text/primary"), "t2": T("text/secondary"), "t3": T("text/muted"), "inv": T("text/inverse"),
        "act": T("action/primary"), "red": T("brand/red"), "sun": T("brand/sun"),
    }
    for g in ("in-preparation", "in-transit", "accepted", "rejected"):
        for p in ("bg", "border", "text"):
            var[f"s-{g}-{p}"] = T(f"status/{g}/{p}")
    for g in ("normal", "warning", "urgent"):
        for p in ("bg", "border", "text"):
            var[f"a-{g}-{p}"] = T(f"alert/{g}/{p}")
    v = [row for row in ds.VARIANT_ROWS][0]
    var["t3s"] = v[3]
    root = ";".join(f"--{k}:{val}" for k, val in var.items())

    css = face + """
:root{%s}
*{box-sizing:border-box}
body{margin:0;background:var(--canvas);color:var(--t1);font-family:Outfit,system-ui,"Segoe UI",sans-serif;width:1800px}
.mono{font-family:"Roboto Mono",ui-monospace,Consolas,monospace;font-weight:700;letter-spacing:.04em}
h1{font-size:34px;font-weight:700;margin:0}h2{font-size:22px;font-weight:600;margin:0 0 14px}
.top{padding:28px 40px 12px;display:flex;justify-content:space-between;align-items:flex-end;border-bottom:4px solid var(--act)}
.top small{color:var(--t2);font-size:15px}
.band{padding:22px 40px;border-bottom:1px solid var(--border)}
.row{display:flex;gap:28px;align-items:flex-start;flex-wrap:wrap}
.sw{width:132px}.sw i{display:block;height:44px;border-radius:10px;border:1px solid var(--border)}.sw b{font-size:13px;display:block;margin-top:5px}.sw span{font-size:12px;color:var(--t2)}
table{border-collapse:collapse;font-size:13px}td,th{border-bottom:1px solid var(--border);padding:4px 10px;text-align:left}th{color:var(--t2);font-weight:600}
.AAA{color:#166534;font-weight:700}.AA{color:#92400E;font-weight:700}.fail{color:#991B1B;font-weight:700}
.cap{font-size:13px;color:var(--t2);font-weight:500;letter-spacing:.02em;margin:6px 0 4px}
.btn{height:48px;border-radius:14px;display:inline-flex;align-items:center;justify-content:center;gap:8px;padding:0 16px;font-weight:600;font-size:16px;min-width:150px}
.p{background:var(--act);color:var(--inv)}.s{background:var(--card);color:var(--act);border:1.5px solid var(--act)}.d{background:var(--card);color:var(--a-urgent-text);border:1.5px solid var(--a-urgent-text)}
.off{background:var(--muted);color:var(--t3);border:1.5px solid var(--border)}.foc{outline:2px solid var(--act);outline-offset:2px}
.field{width:250px}.field label{display:block;font-size:14px;font-weight:500;color:var(--t2);margin-bottom:4px}
.field .in{height:48px;border-radius:10px;background:var(--card);border:1.5px solid var(--t3);padding:0 12px;display:flex;align-items:center;font-size:16px}
.field .h{font-size:13px;color:var(--t3);margin-top:4px}.field .e{font-size:13px;color:var(--a-urgent-text);margin-top:4px;display:flex;gap:4px;align-items:center}
.al{border-radius:14px;padding:12px 16px;width:290px}.al b{display:block;font-size:16px;font-weight:600}.al span{font-size:14px}
.card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:12px 16px;width:340px;display:flex;justify-content:space-between;align-items:center;gap:10px}
.card small{display:block;color:var(--t2);font-size:13px;margin-top:2px}
.bd{white-space:nowrap;display:inline-block;border-radius:9999px;padding:2px 10px;font-size:13px;font-weight:500;letter-spacing:.02em;border:1px solid}
.ph{zoom:.8;width:390px;height:700px;border:1px solid var(--border);border-radius:28px;overflow:hidden;background:var(--canvas);display:flex;flex-direction:column;position:relative;box-shadow:0 2px 8px #0002}
.ph .st{padding:10px 20px 0;font-size:13px;font-weight:600}.ph h3{font-size:24px;font-weight:600;margin:6px 16px 8px;letter-spacing:-.02em}
.bar{background:var(--muted);color:var(--t2);font-size:13px;padding:8px 16px;font-weight:500}
.tabs{margin-top:auto;border-top:1px solid var(--border);background:var(--card);display:flex;justify-content:space-around;padding:8px 0 14px;font-size:12px;font-weight:500;color:var(--t2)}
.tabs div{display:flex;flex-direction:column;align-items:center;gap:2px}.tabs .on{color:var(--act);font-weight:600}
.pad{padding:0 16px;display:flex;flex-direction:column;gap:12px}
.note{font-size:13px;color:var(--t2);max-width:312px;margin-top:8px}
.big{font-size:38px;font-weight:900;letter-spacing:-.02em;line-height:44px}
.kv b{font-size:15px}.kv span{display:block;font-size:13px;color:var(--t2)}
""" % root

    def badge(g, text):
        return f'<span class="bd" style="background:var(--s-{g}-bg);border-color:var(--s-{g}-border);color:var(--s-{g}-text)">{text}</span>'

    def alert(g, title, body=""):
        bw = "2px" if g == "urgent" else "1px"
        return f'<div class="al" style="background:var(--a-{g}-bg);border:{bw} solid var(--a-{g}-border);color:var(--a-{g}-text)"><b>{title}</b><span>{body}</span></div>'

    def tabs(on):
        items = [("house", "Finca"), ("sun", "Secado"), ("bell", "Alertas"), ("package", "Sacos")]
        return '<div class="tabs">' + "".join(f'<div class="{"on" if n == on else ""}">{ic(i, 24)}{n}</div>' for i, n in items) + "</div>"

    sw = ""
    for name, path in (("canvas", "surface/canvas"), ("card", "surface/card"), ("muted", "surface/muted"), ("border", "surface/border"), ("text primary", "text/primary"), ("text secondary", "text/secondary"), ("text muted", "text/muted"), ("action", "action/primary"), ("brand red", "brand/red"), ("brand sun", "brand/sun"), ("muted strong (proposed, unused)", "")):
        val = var["t3s"] if not path else T(path)
        sw += f'<div class="sw"><i style="background:{val}"></i><b>{name}</b><span>{val}</span></div>'

    rows = ""
    for name, fg, bg, where, r, lv in ds.MATRIX:
        rows += f"<tr><td>{html.escape(name)}</td><td>{r:.2f}</td><td class='{lv}'>{lv}</td></tr>"
    half = (len(ds.MATRIX) + 1) // 2
    ct = lambda a: "<table><tr><th>Combination</th><th>Ratio</th><th>Level</th></tr>" + "".join(f"<tr><td>{html.escape(m[0])}</td><td>{m[4]:.2f}</td><td class='{m[5]}'>{'graphic only' if m[0] in ds.NOT_TEXT else ('not for text' if m[5]=='fail' else m[5])}</td></tr>" for m in a) + "</table>"

    comp = f"""
<div class="row">
<div><div class="cap">Button</div><div class="row" style="gap:12px"><span class="btn p">{ic('scan-line')}Escanear saco</span><span class="btn s">Llegué al centro</span><span class="btn d">Terminar secado</span></div>
<div class="row" style="gap:12px;margin-top:10px"><span class="btn p foc">Focus</span><span class="btn off">Disabled</span></div></div>
<div><div class="cap">Field</div><div class="row" style="gap:16px"><div class="field"><label>Peso (kg)</label><div class="in">60</div><div class="h">Un número entre 1 y 100</div></div>
<div class="field"><label>Código del saco</label><div class="in mono" style="border-color:var(--a-urgent-border);border-width:2px">AP-7K3M-Q29X-TDHB</div><div class="e">{ic('triangle-alert',16,var['a-urgent-text'])} Falta el dígito de control</div></div></div></div>
</div>
<div class="row" style="margin-top:16px">
<div><div class="cap">Alert, three levels</div><div class="row" style="gap:12px">{alert('normal','Tu cultivo está dentro del rango','El nodo reportó hace 40 min.')}{alert('warning','La humedad del suelo está por debajo del rango','Revisa en tu próxima visita.')}{alert('urgent','La temperatura del grano pasó de 40 °C','Actúa ahora.')}</div></div>
</div>
<div class="row" style="margin-top:16px">
<div><div class="cap">Sack card, default and rejected</div><div class="row" style="gap:12px"><div class="card"><div><span class="mono">AP-7K3M-Q29X-TDHB-6</span><small>Escaneado hace 5 min</small></div>{badge('in-transit','En tránsito')}</div>
<div class="card" style="background:var(--a-urgent-bg)"><div><span class="mono">AP-2D8F-W41P-KLMN-3</span><small>Rechazado por el receptor</small></div>{badge('rejected','Rechazado')}</div></div></div>
<div><div class="cap">Status badge, four groups</div><div class="row" style="gap:10px">{badge('in-preparation','En preparación')}{badge('in-transit','En tránsito')}{badge('accepted','Aceptado')}{badge('rejected','Rechazado')}</div>
<div class="cap" style="margin-top:14px">Icons, Lucide, 2 px stroke</div><div class="row" style="gap:12px;color:var(--t2)">{''.join(ic(n, 24) for n in ds.ICONS)}</div></div>
</div>"""

    farmer1 = f"""<div class="ph"><div class="st">9:41</div><h3>Finca La Esperanza</h3><div class="bar">Actualizado el martes a las 6:10</div><div class="pad" style="margin-top:12px">
{alert('normal','Tu cultivo está dentro del rango','El nodo reportó hace 40 min.').replace('width:290px','')}
<div class="card" style="width:auto"><div><b style="font-size:18px;font-weight:600">Secando desde el lunes</b><small>Toca para ver el secado</small></div>{ic('chevron-right',22,var['act'])}</div>
<span class="btn s" style="width:100%">Ver los números</span><div style="text-align:center;color:var(--act);font-weight:600;padding:6px">Registrar pH a mano</div></div>{tabs('Finca')}</div>"""
    farmer5 = f"""<div class="ph"><div class="st">9:41</div><h3>Secado</h3><div class="pad">
<div class="al" style="width:auto;background:var(--a-urgent-bg);border:2px solid var(--a-urgent-border);color:var(--a-urgent-text);display:flex;gap:10px;align-items:flex-start">{ic('triangle-alert',26,var['a-urgent-text'])}<div><b style="font-size:19px">La temperatura del grano pasó de 40 °C</b><b style="font-size:19px">Actúa ahora.</b></div></div>
<div style="font-size:16px">Secando hace 3 días y 4 horas</div>
<div class="row" style="gap:12px;flex-wrap:nowrap"><div class="card" style="width:50%;display:block"><div class="kv"><span>Grano</span><div class="mono" style="font-size:24px;color:var(--a-urgent-text)">41,6 °C</div><span>Sobre el límite de 40 °C</span></div></div><div class="card" style="width:50%;display:block"><div class="kv"><span>Humedad</span><div class="mono" style="font-size:24px">18,2 %</div><span>Meta: 12 %</span></div></div></div>
<div style="font-size:13px;color:var(--t3)">Última lectura hace 12 min</div><span class="btn d" style="width:100%;margin-top:30px">Terminar secado</span></div>{tabs('Secado')}</div>"""
    carrier1 = f"""<div class="ph"><div class="st">9:41</div><h3>Hacia el centro de acopio</h3><div class="bar" style="display:flex;gap:6px;align-items:center">{ic('wifi-off',16)}Sin conexión. 12 eventos esperan envío</div><div class="pad" style="margin-top:12px">
<div class="card" style="width:auto;background:var(--s-in-transit-bg);border-color:var(--s-in-transit-border);color:var(--s-in-transit-text)"><div style="display:flex;gap:8px;align-items:center">{ic('map-pin',22)}<span style="font-size:15px;font-weight:500">Ubicación activa · cada 5 min</span></div><span class="btn s" style="height:40px;min-width:0">{ic('pause',16)}Pausar</span></div>
<div class="card" style="width:auto;display:block;text-align:center"><div style="font-size:14px;color:var(--t2)">Sacos escaneados</div><div class="mono" style="font-size:40px">18 / 30</div></div>
<div class="cap">Últimos escaneos</div><div class="card" style="width:auto"><span class="mono" style="font-size:14px">AP-7K3M-Q29X-TDHB-6</span>{badge('in-transit','En tránsito')}</div><div class="card" style="width:auto"><span class="mono" style="font-size:14px">AP-2D8F-W41P-KLMN-3</span>{badge('in-transit','En tránsito')}</div></div>
<div class="pad" style="margin-top:auto;padding-bottom:20px"><span class="btn p" style="width:100%">{ic('scan-line')}Escanear saco</span><span class="btn s" style="width:100%">Llegué al centro</span></div></div>"""
    carrier4 = f"""<div class="ph"><div class="st">9:41</div><h3>Entrega en puerto</h3><div class="pad"><div style="display:flex;gap:6px"><i style="height:5px;flex:1;background:var(--act);border-radius:3px"></i><i style="height:5px;flex:1;background:var(--border);border-radius:3px"></i><i style="height:5px;flex:1;background:var(--border);border-radius:3px"></i></div>
<div style="font-size:14px;color:var(--t2)">Paso 1 de 3 · Marca los rechazados</div><div class="card" style="width:auto"><b>27 aceptados · 3 rechazados</b></div>
<div class="card" style="width:auto"><span class="mono" style="font-size:14px">AP-7K3M-Q29X-TDHB-6</span><i style="width:52px;height:30px;border-radius:15px;background:var(--card);border:2px solid var(--t3)"></i></div>
<div class="card" style="width:auto;background:var(--a-urgent-bg)"><span class="mono" style="font-size:14px">AP-2D8F-W41P-KLMN-3</span><i style="width:52px;height:30px;border-radius:15px;background:var(--a-urgent-text)"></i></div>
<div class="card" style="width:auto"><span class="mono" style="font-size:14px">AP-9H4C-R62V-ZQXA-1</span><i style="width:52px;height:30px;border-radius:15px;background:var(--card);border:2px solid var(--t3)"></i></div></div>
<div class="pad" style="margin-top:auto;padding-bottom:20px"><span class="btn p" style="width:100%">Continuar</span></div></div>"""
    buyer1 = f"""<div class="ph"><div style="display:flex;justify-content:space-between;align-items:center;padding:14px 16px;background:var(--card);border-bottom:3px solid var(--red)"><b style="font-size:20px;font-weight:900">AromaPacífico</b><span class="bd" style="background:var(--act);color:var(--inv);border-color:var(--act)">{ic('languages',14)} ES</span></div>
<div class="pad" style="margin-top:14px"><div class="card" style="width:auto;display:block"><span class="mono" style="font-size:16px">AP-7K3M-Q29X-TDHB-6</span><div style="margin:8px 0">{badge('in-transit','En tránsito')}</div><small>Rumbo al puerto</small></div>
<div><div style="font-size:13px;color:var(--t2)">Origen</div><div class="big">Cauca, Colombia</div></div>
<div class="card" style="width:auto;display:block"><b style="font-size:18px;font-weight:600">Recorrido del café</b><div style="font-size:14px;line-height:22px;margin-top:6px;color:var(--t2)">Secado del lote · 2 al 9 de mayo de 2026<br>Saco registrado · 14 de mayo de 2026<br>Recibido en el centro · 15 de mayo de 2026<br>Despachado al puerto · 18 de mayo de 2026</div></div>
<div class="card" style="width:auto;display:block"><b style="font-size:18px;font-weight:600">Secado del lote</b><div class="row" style="gap:30px;margin-top:6px"><div class="kv"><div class="mono" style="font-size:22px">175 h</div><span>Horas monitoreadas</span></div><div class="kv"><div class="mono" style="font-size:22px">41,6 °C</div><span>Temp. máx. del grano</span></div></div></div></div></div>"""

    body = f"""<div class="top"><div><h1>AromaPacífico design system applied to three views</h1><small>Tokens of the visual identity, components, accessibility rules and the farmer, carrier and buyer views. Proposed variants are marked and are not applied to the tokens.</small></div><small>Contrast computed with the WCAG 2.2 formula by design_system.py</small></div>
<div class="band"><h2>Tokens and contrast</h2><div class="row">{''.join([sw])}</div><div class="row" style="margin-top:16px;gap:40px">{ct(ds.MATRIX[:half])}{ct(ds.MATRIX[half:])}</div></div>
<div class="band"><h2>Components</h2>{comp}</div>
<div class="band"><h2>The three views</h2><div class="row" style="gap:24px;flex-wrap:nowrap">
<div>{farmer1}<div class="note">Farmer, farm screen with a normal reading</div></div>
<div>{farmer5}<div class="note">Farmer, drying with the urgent alert, a 2 px border, an icon and words</div></div>
<div>{carrier1}<div class="note">Carrier, open trip with the offline bar</div></div>
<div>{carrier4}<div class="note">Carrier, first of three delivery steps, off toggles keep a 3:1 outline</div></div>
<div>{buyer1}<div class="note">Buyer lookup. Only fields of the public view appear. Weight, centers, hours and minutes, people, trips and places stay out</div></div></div></div>"""
    for rule in re.findall(r"\.([\w-]+)\{([^}]*)\}", css):
        sel, decl = rule
        if "background:var(--muted)" in decl and "color:var(--t3)" in decl and sel != "off":
            raise SystemExit(f"the sheet puts text/muted on surface/muted in .{sel}")
    for frag in re.findall(r'style="([^"]*)"', body):
        if "background:var(--muted)" in frag and "color:var(--t3)" in frag:
            raise SystemExit("the sheet puts text/muted on surface/muted in an inline style")
    Path(out).write_text(f"<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'><style>{css}</style></head><body>{body}</body></html>", encoding="utf-8")
