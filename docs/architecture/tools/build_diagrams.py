"""Builds docs/architecture/diagrams/platform-architecture.drawio with fixed coordinates."""
from pathlib import Path
from xml.sax.saxutils import quoteattr

OUT = Path(__file__).resolve().parent.parent / "diagrams" / "platform-architecture.drawio"

COMPUTE, DATA, STORAGE, NET, SEC, APP, ML, MGMT, IOT = (
    "#ED7100", "#C925D1", "#7AA116", "#8C4FFF", "#DD344C", "#E7157B", "#01A88D", "#E7157B", "#7AA116")
TEL, OBJ, BIZ, CTRL, FAIL, ALERT = "#2E7D32", "#1565C0", "#6A1B9A", "#616161", "#C62828", "#E65100"
INK = "#232F3E"


class Page:
    def __init__(self, name, width, height, title):
        self.name, self.w, self.h = name, width, height
        self.cells, self.edges, self.seq = [], [], 0
        self.geo = {}
        self.text(title, 40, 16, width - 80, 34, size=20, bold=True)

    def nid(self):
        self.seq += 1
        return f"{self.name[:2]}{self.seq}"

    def _v(self, value, style, x, y, w, h, cid=None):
        cid = cid or self.nid()
        self.geo[cid] = (x, y, w, h)
        self.cells.append(
            f'<mxCell id={quoteattr(cid)} value={quoteattr(value)} style={quoteattr(style)} vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        return cid

    def text(self, value, x, y, w, h, size=12, bold=False, align="left", color=INK):
        style = (f"text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align={align};verticalAlign=middle;"
                 f"fontSize={size};fontColor={color};fontStyle={1 if bold else 0};")
        return self._v(value, style, x, y, w, h)

    def group(self, label, x, y, w, h, stroke="#879196", fill="none", dashed=False, sw=1, color=None, cid=None, align="left"):
        style = (f"rounded=0;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};strokeWidth={sw};"
                 f"dashed={1 if dashed else 0};verticalAlign=top;align={align};spacingLeft=10;spacingRight=10;spacingTop=6;"
                 f"fontSize=13;fontStyle=1;fontColor={color or stroke};")
        return self._v(label, style, x, y, w, h, cid)

    def note(self, value, x, y, w, h, fill="#FFF8E1", stroke="#D6B656", size=11):
        style = (f"rounded=0;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};align=left;"
                 f"verticalAlign=middle;spacingLeft=6;spacingRight=6;fontSize={size};fontColor={INK};")
        return self._v(value, style, x, y, w, h)

    def step(self, value, x, y, w=150, h=62, fill="#FFFFFF", stroke=INK, cid=None, size=12):
        style = (f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};align=center;"
                 f"verticalAlign=middle;fontSize={size};fontColor={INK};")
        return self._v(value, style, x, y, w, h, cid)

    def aws(self, label, x, y, icon, color, cid=None, size=52):
        style = (f"sketch=0;outlineConnect=0;fontColor={INK};fillColor={color};strokeColor=#ffffff;dashed=0;"
                 f"verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=11;aspect=fixed;"
                 f"shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.{icon};")
        return self._v(label, style, x, y, size, size, cid)

    def net(self, label, x, y, shape, cid=None, w=52, h=52):
        style = (f"sketch=0;html=1;shape=mxgraph.networks.{shape};fillColor=#29AAE1;strokeColor=#ffffff;"
                 f"verticalLabelPosition=bottom;verticalAlign=top;align=center;fontSize=11;fontColor={INK};")
        return self._v(label, style, x, y, w, h, cid)

    def azure(self, label, x, y, image, size=44):
        style = (f"sketch=0;html=1;aspect=fixed;image;image=img/lib/azure2/{image};verticalLabelPosition=bottom;"
                 f"verticalAlign=top;align=center;fontSize=11;fontColor={INK};")
        return self._v(label, style, x, y, size, size)

    def badge(self, code, x, y):
        style = ("rounded=1;whiteSpace=wrap;html=1;fillColor=#0B3D91;strokeColor=#0B3D91;fontColor=#FFFFFF;"
                 "fontSize=12;fontStyle=1;align=center;verticalAlign=middle;")
        return self._v(code, style, x, y, 42, 22, f"box-{code}")

    def zone(self, label, x, y, w, h, fill, stroke, cid=None, dashed=False, size=15, align="left"):
        style = (f"rounded=0;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};strokeWidth=1.5;"
                 f"dashed={1 if dashed else 0};verticalAlign=top;align={align};spacingLeft=10;spacingTop=6;"
                 f"fontSize={size};fontStyle=1;fontColor={INK};")
        return self._v(label, style, x, y, w, h, cid)

    def card(self, title, sub, x, y, w=170, h=64, cid=None, stroke="#7F8C8D", dashed=False, icon=None, color=None, net=None, azure=None, impl=False):
        pad = 44 if (icon or net or azure) else 6
        fill, sw = ("#D6E6FA", 3) if impl else ("#FFFFFF", 1.2)
        stroke = "#0B3D91" if impl else stroke
        value = f"<b>{title}</b><br><font style='font-size:10px'>{sub}</font>" if sub else f"<b>{title}</b>"
        style = (f"rounded=1;arcSize=8;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};strokeWidth={sw};"
                 f"dashed={1 if dashed else 0};align=left;verticalAlign=middle;spacingLeft={pad};spacingRight=3;"
                 f"fontSize=12;fontColor={INK};")
        cid = self._v(value, style, x, y, w, h, cid)
        ih = 32
        iy = y + (h - ih) // 2
        if icon:
            self.aws("", x + 7, iy, icon, color, size=ih)
        if net:
            self.net("", x + 7, iy, net, w=ih, h=ih)
        if azure:
            self.azure("", x + 7, iy, azure, size=ih)
        return cid

    def chip(self, text, x, y, w=120, h=26, fill="#FFFFFF", stroke="#7F8C8D", dashed=False, impl=False):
        if impl:
            fill, stroke = "#D6E6FA", "#0B3D91"
        style = (f"rounded=1;arcSize=30;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};"
                 f"strokeWidth={3 if impl else 1};dashed={1 if dashed else 0};align=center;verticalAlign=middle;fontSize=11;fontColor={INK};")
        return self._v(text, style, x, y, w, h)

    def code(self, code, x, y):
        style = ("rounded=1;arcSize=40;whiteSpace=wrap;html=1;fillColor=#0B3D91;strokeColor=#0B3D91;fontColor=#FFFFFF;"
                 "fontSize=10;fontStyle=1;align=center;verticalAlign=middle;")
        return self._v(code, style, x, y, 32, 17)

    def edge(self, src, dst, label="", color=INK, dashed=False, points=(), exit=None, entry=None, width=1.5):
        style = (f"edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor={color};strokeWidth={width};"
                 f"dashed={1 if dashed else 0};endArrow=block;endFill=1;fontSize=11;fontColor={INK};"
                 f"labelBackgroundColor=#FFFFFF;jumpStyle=arc;jumpSize=10;")
        if exit:
            style += f"exitX={exit[0]};exitY={exit[1]};exitDx=0;exitDy=0;"
        if entry:
            style += f"entryX={entry[0]};entryY={entry[1]};entryDx=0;entryDy=0;"
        pts = "".join(f'<mxPoint x="{x}" y="{y}"/>' for x, y in points)
        arr = f'<Array as="points">{pts}</Array>' if pts else ""
        self.edges.append(
            f'<mxCell id={quoteattr(self.nid())} value={quoteattr(label)} style={quoteattr(style)} edge="1" parent="1" '
            f'source={quoteattr(src)} target={quoteattr(dst)}><mxGeometry relative="1" as="geometry">{arr}</mxGeometry></mxCell>')

    def legend(self, x, y, w, rows):
        h = 30 + 22 * len(rows)
        self.group("Legend", x, y, w, h, stroke=INK, fill="#FFFFFF")
        yy = y + 28
        for color, dashed, text in rows:
            style = (f"endArrow=block;endFill=1;html=1;strokeColor={color};strokeWidth=2;dashed={1 if dashed else 0};")
            cid = self.nid()
            self.edges.append(
                f'<mxCell id={quoteattr(cid)} value="" style={quoteattr(style)} edge="1" parent="1">'
                f'<mxGeometry relative="1" as="geometry"><mxPoint x="{x + 12}" y="{yy + 10}" as="sourcePoint"/>'
                f'<mxPoint x="{x + 58}" y="{yy + 10}" as="targetPoint"/></mxGeometry></mxCell>')
            self.text(text, x + 66, yy, w - 74, 20, size=11)
            yy += 22

    def lifeline(self, title, sub, x, top, bottom, icon=None, color=None, net=None):
        self._v("", f"rounded=0;html=1;fillColor=#AAB7B8;strokeColor=none;", x - 1, top + 60, 2, bottom - top - 60)
        self.card(title, sub, x - 95, top, 190, 60, icon=icon, color=color, net=net)

    def message(self, x1, x2, y, label, color=INK, dashed=False):
        style = (f"endArrow=block;endFill=1;html=1;strokeColor={color};strokeWidth=1.5;dashed={1 if dashed else 0};"
                 f"fontSize=11;fontColor={INK};labelBackgroundColor=#FFFFFF;")
        self.edges.append(
            f'<mxCell id={quoteattr(self.nid())} value={quoteattr(label)} style={quoteattr(style)} edge="1" parent="1">'
            f'<mxGeometry relative="1" as="geometry"><mxPoint x="{x1}" y="{y}" as="sourcePoint"/>'
            f'<mxPoint x="{x2}" y="{y}" as="targetPoint"/></mxGeometry></mxCell>')

    def xml(self):
        return (f'<diagram name={quoteattr(self.name)}><mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" '
                f'guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
                f'pageWidth="{self.w}" pageHeight="{self.h}" background="#FFFFFF"><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
                + "".join(self.cells) + "".join(self.edges) + "</root></mxGraphModel></diagram>")


def overview():
    p = Page("00 Platform overview", 2640, 1730, "Aroma Pacifico: target platform on AWS, from the farm to the port of Buenaventura")
    p.text("Pilot of 200 farms, 3 collection centers and 60 carriers in Cauca, Huila and Tolima. AWS us-east-1 is primary and Azure East US stays prepared. The same pattern grows to 1,000 farms. <b>Blue boxes are what the infrastructure code implements, everything else is designed and documented.</b>", 40, 46, 2200, 22, size=13, color="#5D6D7E")
    G = dict(ext=("#F4F6F7", "#AEB6BF"), field=("#EEF7EE", "#6AA84F"), site=("#FDF2E9", "#D68910"), org=("#F7FAFC", "#34495E"), gov=("#FEF9E7", "#B7950B"),
             prod=("#EBF5FB", "#2E86C1"), net=("#F4ECF7", "#8E44AD"), sec=("#FDEDEC", "#CB4335"), obs=("#E8F8F5", "#17A589"), dlv=("#F2F3F4", "#566573"), app=("#EAF2F8", "#2471A3"), az=("#EBF5FB", "#0078D4"), des=("#FDF2E9", "#CA6F1E"))

    # A external
    p.zone("A. External parties", 30, 76, 2580, 128, *G["ext"])
    ext = [("Federation", "Sets alert ranges, reads reports, approves changes"), ("Platform operators", "Console with SSO and MFA"), ("GitHub", "Code, pull requests and Actions"),
           ("Mobile operators", "LTE in municipal seats and main roads"), ("Apple and Google push", "Deliver alerts to phones"), ("Shipping company", "Keeps its own telemetry, no integration"),
           ("Coffee buyers", "Read one sack by code"), ("Data regulator", "Colombian rules on personal data")]
    for i, (t, sub) in enumerate(ext):
        p.card(t, sub, 50 + i * 318, 112, 300, 74, cid=f"ext{i}")

    # B field and sites
    p.zone("B. Field and sites", 30, 220, 520, 1200, *G["field"])
    p.zone("Farm with signal, repeated for each covered farm", 46, 252, 488, 182, "#FFFFFF", G["field"][1], size=12)
    p.card("Local buffer", "FIFO, retains 24 h at most, then drops and counts", 60, 282, 230, 64, net="server")
    p.card("Autonomous node", "ESP32-S3, IP67, LTE modem, encrypted flash", 300, 282, 220, 64, "node", net="wireless_modem")
    p.card("Probes", "NPK, pH, soil, air and grain", 60, 354, 230, 64, net="wireless_hub")
    p.card("Solar kit", "20 W panel, LiFePO4, 5 days of autonomy", 300, 354, 220, 64, net="server")
    p.zone("Out-of-coverage vereda", 46, 444, 488, 118, "#FFFFFF", G["field"][1], size=12)
    p.chip("Data mule<br>for objects", 60, 480, 84, 60)
    p.card("LoRa node", "Same node, LoRa radio", 154, 474, 170, 72, "lnode", net="wireless_modem")
    p.card("Shared gateway", "High point, LTE backhaul", 350, 474, 170, 72, "lgw", net="wireless_hub")
    p.edge("lnode", "lgw", "", TEL)
    p.zone("Carriers: 60 phones", 46, 572, 488, 102, "#FFFFFF", G["field"][1], size=12)
    p.card("Carrier application", "Position every 5 min, queues offline, custody events always kept", 60, 600, 460, 62, "carrier", net="mobile")
    p.zone("Drone service: 3 brigades", 46, 684, 488, 174, "#FFFFFF", G["field"][1], size=12)
    p.card("Drone", "Mission preloaded, flight log held in its buffer", 60, 712, 460, 62, net="wireless_modem")
    p.card("Ground station", "Loads missions at the municipal seat or center, uploads objects and logs", 60, 782, 460, 62, "ground", net="pc")
    p.zone("C. Collection centers: one pattern, X = 41 Cauca, 42 Huila, 43 Tolima", 46, 870, 488, 424, *G["site"], size=12)
    zones = [("Management", "10.X.1.0/24"), ("Support", "10.X.2.0/24"), ("Logistics", "10.X.3.0/24"), ("Transport", "10.X.4.0/24"), ("Visitors, isolated", "10.X.5.0/24"), ("Local servers", "10.X.10.0/24")]
    for i, (z, c) in enumerate(zones):
        p.chip(f"<b>{z}</b><br>{c}", 60 + (i % 2) * 150, 902 + (i // 2) * 56, 142, 48)
    p.card("WLAN and VLANs", "One SSID per zone, QoS", 360, 902, 164, 64, net="wireless_hub")
    p.card("Code printer", "Sheets for sacks with no code", 360, 974, 164, 64, net="printer")
    p.card("Perimeter firewall", "10.X.20.0/24, default deny, one per center", 60, 1078, 464, 64, "fw", net="firewall")
    p.card("WAN 100 Mbps", "Symmetric, shared with operations", 60, 1150, 464, 60, net="router")
    p.note("Visitors reach the internet only. Logistics and local servers reach the cloud through the tunnel.", 60, 1218, 464, 62)
    p.zone("Port of Buenaventura", 46, 1304, 488, 102, "#FFFFFF", G["field"][1], size=12)
    p.note("No Federation equipment. The platform records only the sack delivery event, from the carrier application.", 60, 1334, 460, 60)

    # AWS organization
    p.zone("D. AWS Organization", 570, 220, 1620, 1200, *G["org"], cid="org")
    p.zone("D1. Governance from the root", 586, 252, 1588, 118, *G["gov"], size=13)
    for i, (t, c) in enumerate([("Management", "Billing, SSO"), ("Log archive", "Audit, 5 years"), ("Security tooling", "Findings, keys"), ("Network", "VPCs, VPN"), ("Production", "10.70.0.0/16"), ("Test", "10.60.0.0/16"), ("Development", "10.50.0.0/16")]):
        p.chip(f"<b>{t}</b><br>{c}", 600 + i * 140, 284, 132, 44)
    p.card("Service control policies", "Region limit, audit protection", 1590, 280, 280, 40, icon="organizations", color=MGMT)
    p.card("Tags, budgets, trail", "Cost by farms, drones, collection, trips", 1880, 280, 280, 40, icon="budgets", color=MGMT)
    p.text("Tags and budgets are inherited by every account, and the cost dashboard splits by them.", 600, 336, 1500, 24, size=11)

    p.zone("D2. Production account: serverless workload, nothing runs while no event arrives", 586, 382, 1588, 586, *G["prod"], size=13)
    c = [600, 800, 1000, 1200, 1400, 1600, 1800, 2000]
    W = 164
    for label, x in (("Entry", c[0]), ("Queue and route", c[1]), ("Functions", c[2]), ("Data", c[3]), ("Analysis", c[4])):
        p.text(label, x, 408, W, 20, size=12, bold=True, color="#2E86C1")
    p.card("IoT Core", "MQTT over TLS, LoRaWAN, X.509", c[0], 436, W, 66, "iot", icon="iot_core", color=IOT, impl=True)
    p.card("SQS", "Burst buffer, 3 retries", c[1], 436, W, 66, "sqs", icon="sqs", color=APP, impl=True)
    p.card("Ingestion", "Validates, dedupes, checks ranges", c[2], 436, W, 66, "fn", icon="lambda", color=COMPUTE, impl=True)
    p.code("C07", c[2] + W - 34, 430)
    p.card("DynamoDB readings", "90 days, ranges, alerts", c[3], 436, W, 66, "ddb", icon="dynamodb", color=DATA, impl=True)
    p.card("SNS", "Push under 5 min", c[6], 436, W, 66, "sns", icon="sns", color=APP)
    p.card("Firehose", "Parquet batches", c[1], 516, W, 66, "fh", icon="kinesis_data_firehose", color=NET, impl=True)
    p.card("S3 archive", "Readings, 5 years", c[3], 516, W, 66, "arc", icon="s3", color=STORAGE, impl=True)
    p.card("Athena", "Pilot reports", c[4], 516, W, 66, "ath", icon="athena", color=NET)
    p.card("API Gateway", "HTTP API, Cognito JWT", c[0], 626, W, 66, "api", icon="api_gateway", color=NET)
    p.card("Cognito", "Four user groups, MFA for three", c[1], 626, W, 66, icon="cognito", color=SEC)
    p.card("Domain functions", "Sacks, trips, orders, query", c[2], 626, W, 66, "dom", icon="lambda", color=COMPUTE)
    p.card("DynamoDB records", "Sacks, trips, orders, PITR", c[3], 626, W, 66, "rec", icon="dynamodb", color=DATA)
    p.card("DynamoDB cases", "Case table, function results", c[4], 626, W, 66, "cases", icon="dynamodb", color=DATA, impl=True)
    p.card("S3 web assets", "Reports and query pages", c[6], 516, W, 66, "wa", icon="s3", color=STORAGE)
    p.card("CloudFront", "Web, static assets", c[6], 626, W, 66, "cf", icon="cloudfront", color=NET)
    p.note("<b>Event-driven inference.</b> A function starts on an event, reads the stored object, calls the managed service and writes the result with time, confidence and source object. Then it ends. If it fails, the object stays and the case does not change. Only a person authorizes a fumigation. In code, only focus confirmation is built, with its case table, and Rekognition and Bedrock are called, not created.", 1600, 756, 564, 130, fill="#FFFFFF", stroke=G["prod"][1])
    p.card("WAF", "Rate limit on sack reads", c[7], 626, W, 66, "waf", icon="waf", color=SEC)
    p.card("S3 flight objects", "Photos, maps, logs, 5 years", c[0], 756, W, 66, "obj", icon="s3", color=STORAGE, impl=True)
    p.card("EventBridge", "Object created rules", c[1], 756, W, 66, "eb", icon="eventbridge", color=APP, impl=True)
    p.card("Inference functions", "Focus in code, two more designed", c[2], 756, W, 66, "inf", icon="lambda", color=COMPUTE, impl=True)
    p.code("C08", c[2] + W - 34, 750)
    p.card("Rekognition", "DetectLabels, person filter", c[3], 756, W, 66, "rek", icon="rekognition", color=ML)
    p.card("Bedrock", "Multimodal model, no training", c[4], 756, W, 66, "bed", icon="bedrock", color=ML)
    p.card("Farm module", "Thing, CSR certificate, policy", c[0], 516, W, 66, "farmmod", icon="iot_core", color=IOT, impl=True)
    p.code("C10", c[0] + W - 34, 510)
    p.card("S3 restricted", "Objects with a person, 30 days", c[3], 856, W, 66, "quar", icon="s3", color=STORAGE)
    p.card("SQS dead letter", "Keeps failures, state unchanged", c[1], 856, W, 66, "dlq", icon="sqs", color=APP, impl=True)
    p.card("CloudWatch alarm", "Reports failed invocations", c[2], 856, W, 66, "alm", icon="cloudwatch_2", color=MGMT, impl=True)

    p.zone("D3. Network account: VPC shared with each environment, no internet or NAT gateway", 586, 980, 1588, 212, *G["net"], size=13, align="center")
    p.card("Virtual private gateway", "VPN to one center in code, 3 in the design", c[0], 1020, 190, 76, "vgw", icon="site_to_site_vpn", color=NET, impl=True)
    p.code("C04", c[0] + 156, 1078)
    subs = [("Telemetry ingress", "10.70.0.0/20", "IoT endpoint"), ("Drone object ingress", "10.70.16.0/20", "S3 endpoint"), ("Application", "10.70.32.0/20", "API endpoint"), ("Data", "10.70.48.0/20", "reserved"),
            ("Object storage", "10.70.64.0/20", "reserved"), ("Administration", "10.70.80.0/20", "reserved"), ("Public query", "10.70.96.0/20", "reserved")]
    for i, (n, cidr, use) in enumerate(subs):
        p.chip(f"<b>{n}</b><br>{cidr}<br>{use}", 806 + i * 196, 1020, 188, 76, dashed=use == "reserved", impl=True)
    p.code("C03", 2130, 986)
    p.card("Gateway endpoints", "S3 and DynamoDB, no charge", c[0], 1110, 190, 66, icon="endpoints", color=NET, impl=True)
    p.card("Permanent firewall rules", "Endpoint security groups allow TCP 443 from logistics and local servers only, and deny all else", 806, 1110, 1184, 66, impl=True)
    p.code("C06", 1952, 1104)

    p.zone("D4. Security and audit", 586, 1204, 620, 202, *G["sec"], size=13)
    p.card("KMS", "Keys for data, objects, platform", 600, 1236, 190, 66, icon="key_management_service", color=SEC, impl=True)
    p.card("Secrets Manager", "VPN keys from AWS, API keys", 800, 1236, 190, 66, icon="secrets_manager", color=SEC)
    p.card("IAM roles", "Per function, OIDC for pipeline", 1000, 1236, 192, 66, icon="identity_and_access_management", color=SEC, impl=True)
    p.code("C05", 1158, 1230)
    p.card("CloudTrail", "Organization trail, 5 years", 600, 1316, 190, 66, icon="cloudtrail", color=MGMT)
    p.card("GuardDuty", "Threat detection", 800, 1316, 190, 66, icon="guardduty", color=SEC)
    p.card("Security Hub", "Findings in one place", 1000, 1316, 192, 66, icon="security_hub", color=SEC)
    p.zone("D5. Observability", 1218, 1204, 560, 202, *G["obs"], size=13)
    p.card("CloudWatch", "Metrics, logs, traces", 1232, 1236, 170, 66, icon="cloudwatch_2", color=MGMT)
    p.card("Operations dashboard", "WAN, objects, silent nodes", 1412, 1236, 170, 66, icon="cloudwatch_2", color=MGMT)
    p.card("Cost dashboard", "Split by tags", 1592, 1236, 170, 66, icon="budgets", color=MGMT)
    p.note("<b>Two SLOs.</b> Crop alert delivery and sack query availability. Alarms cover silent nodes over 24 h, unclosed flights and failed invocations.", 1232, 1316, 530, 66, fill="#FFFFFF", stroke=G["obs"][1])
    p.zone("D6. Environments and promotion", 1790, 1204, 384, 202, *G["dlv"], size=13)
    p.step("<b>Development</b><br>10.50.0.0/16", 1804, 1240, 106, 66, cid="e1", size=11, fill="#D6E6FA", stroke="#0B3D91")
    p.step("<b>Test</b><br>10.60.0.0/16", 1926, 1240, 106, 66, cid="e2", size=11, fill="#D6E6FA", stroke="#0B3D91")
    p.step("<b>Production</b><br>10.70.0.0/16", 2048, 1240, 112, 66, cid="e3", size=11, fill="#D6E6FA", stroke="#0B3D91")
    p.edge("e1", "e2", "", CTRL, width=2)
    p.edge("e2", "e3", "", CTRL, width=2)
    p.note("Same code, separate accounts, ranges and data. Production needs a person's approval. Detail on the environments page.", 1804, 1316, 356, 72, fill="#FFFFFF", stroke=G["dlv"][1])

    # Delivery
    p.zone("E. Infrastructure delivery", 570, 1436, 1620, 150, *G["dlv"])
    p.card("Terraform modules", "One repository per module", 590, 1474, 190, 66, "rep", net="server", impl=True)
    p.card("Infrastructure repository", "Root, environments, no secrets", 800, 1474, 200, 66, "root", net="server", impl=True)
    p.code("C01", 966, 1468)
    p.card("Pull request", "fmt, validate, security scan", 1020, 1474, 180, 66, "pr", icon="organizations", color=CTRL, impl=True)
    p.card("Plan", "Output kept as evidence", 1220, 1474, 160, 66, "plan", icon="organizations", color=CTRL, impl=True)
    p.code("C09", 1346, 1468)
    p.card("Person approves", "Protected environment", 1400, 1474, 170, 66, "ok", icon="identity_and_access_management", color=SEC, impl=True)
    p.card("Apply", "OIDC role, no static keys", 1590, 1474, 170, 66, "app", icon="organizations", color=CTRL, impl=True)
    p.card("Remote state", "S3, KMS, native lock file", 1780, 1474, 190, 66, "st", icon="s3", color=STORAGE, impl=True)
    p.code("C02", 1936, 1468)
    p.card("Destroy", "On demand and each night", 1990, 1474, 180, 66, "des", icon="organizations", color=CTRL, impl=True)
    p.text("No production change between 05:00 and 18:00 in harvest week, except during an incident. The pipeline can bring an environment up and down, so credits are spent only while it is in use.", 590, 1546, 1580, 30, size=11)
    for a, b in (("rep", "root"), ("root", "pr"), ("pr", "plan"), ("plan", "ok"), ("ok", "app"), ("app", "st"), ("st", "des")):
        p.edge(a, b, "", CTRL)

    # Right column
    p.zone("F. Applications, built outside this project", 2206, 220, 404, 470, *G["app"])
    p.note("The platform hosts three planned applications. They are built outside this project, and the carrier application appears with the carriers in zone B.", 2224, 256, 368, 96, fill="#FFFFFF", stroke=G["app"][1])
    p.card("Farmer application", "Few screens, alerts and history", 2224, 436, 368, 66, "farmer", net="mobile")
    p.card("Reports web", "Federation and collection centers", 2224, 560, 368, 56, "web", net="pc")
    p.card("Sack query", "Public, by code, buyer view only", 2224, 624, 368, 56, "buyer", net="pc")
    p.zone("G. Azure East US: prepared, idle", 2206, 706, 404, 330, *G["az"], dashed=True)
    p.card("IoT Hub", "Replaces IoT Core", 2224, 744, 178, 66, azure="iot/IoT_Hub.svg", dashed=True, stroke="#0078D4")
    p.card("Functions", "Replaces Lambda", 2414, 744, 178, 66, azure="compute/Function_Apps.svg", dashed=True, stroke="#0078D4")
    p.card("Blob Storage", "Replaces S3", 2224, 820, 178, 66, azure="storage/Storage_Accounts.svg", dashed=True, stroke="#0078D4")
    p.card("Cosmos DB", "Replaces DynamoDB", 2414, 820, 178, 66, azure="databases/Azure_Cosmos_DB.svg", dashed=True, stroke="#0078D4")
    p.note("No resources run here. Portable contracts, the equivalence table and the five-year archive keep the exit available with no idle cost.", 2224, 900, 368, 118, fill="#FFFFFF", stroke="#0078D4")
    p.zone("H. Design system", 2206, 1052, 404, 150, *G["des"])
    p.note("Logo, palette with sack states and crop alert, type for phone and web, spacing, base components and rules of use for the three applications.", 2224, 1088, 368, 98, fill="#FFFFFF", stroke=G["des"][1])

    # Flows
    p.edge("node", "iot", "①", TEL, exit=(1, 0.5), entry=(0, 0.3), points=[(556, 314), (556, 456)], width=2)
    p.edge("lgw", "iot", "①", TEL, exit=(1, 0.5), entry=(0, 0.7), points=[(544, 510), (544, 482)], width=2)
    p.edge("iot", "sqs", "", TEL, width=2)
    p.edge("sqs", "fn", "", TEL, width=2)
    p.edge("fn", "ddb", "", TEL, width=2)
    p.edge("ddb", "sns", "② out of range", ALERT, width=2)
    p.edge("sns", "farmer", "② push", ALERT, width=2)
    p.edge("iot", "fh", "", TEL, exit=(1, 0.75), entry=(0, 0.5), points=[(782, 486), (782, 549)], width=2)
    p.edge("fh", "arc", "objects", TEL, width=2)
    p.edge("arc", "ath", "", TEL, width=2)
    p.edge("carrier", "api", "③", BIZ, exit=(1, 0.5), entry=(0, 0.5), width=2)
    p.edge("api", "dom", "", BIZ, exit=(1, 0.75), entry=(0, 0.75), points=[(780, 676), (780, 702), (985, 702), (985, 676)], width=2)
    p.edge("dom", "rec", "", BIZ, width=2)
    p.edge("ground", "obj", "④", OBJ, exit=(1, 0.5), entry=(0, 0.5), points=[(562, 813), (562, 789)], width=2)
    p.edge("obj", "eb", "", OBJ, width=2)
    p.edge("eb", "inf", "", OBJ, width=2)
    p.edge("inf", "rek", "", OBJ, width=2)
    p.edge("rek", "bed", "", OBJ, width=2)
    p.edge("rek", "quar", "person", FAIL, dashed=True, width=2)
    p.edge("inf", "cases", "result", OBJ, exit=(0.85, 0), entry=(0.5, 1), points=[(1139, 726), (1482, 726)], width=2)
    p.edge("dom", "cases", "", BIZ, exit=(0.85, 1), entry=(0.2, 1), points=[(1139, 706), (1433, 706)], width=2)
    p.edge("eb", "dlq", "fails", FAIL, dashed=True, width=2)
    p.edge("dlq", "alm", "", FAIL, dashed=True, width=2)
    p.edge("buyer", "waf", "⑤", BIZ, exit=(0, 0.5), entry=(1, 0.39), width=2)
    p.edge("web", "waf", "", BIZ, exit=(0, 0.5), entry=(1, 0.15), points=[(2195, 588), (2195, 636)], width=2)
    p.edge("cf", "wa", "", BIZ, exit=(0.5, 0), entry=(0.5, 1), width=2)
    p.edge("waf", "cf", "", BIZ, width=2)
    p.edge("cf", "dom", "⑤ signed lookup", BIZ, exit=(0, 0.25), entry=(0.5, 0), points=[(1700, 642), (1700, 606), (1082, 606)], width=2)
    p.edge("fw", "vgw", "③ ④", OBJ, exit=(1, 0.5), entry=(0, 0.5), points=[(562, 1110), (562, 1058)], width=2)
    p.edge("vgw", "obj", "④", OBJ, exit=(0.3, 0), entry=(0.3, 1), width=2)
    p.edge("vgw", "api", "③", BIZ, exit=(0.6, 0), entry=(0.85, 1), points=[(714, 1000), (782, 1000), (782, 730), (739, 730)], width=2)
    p.edge("app", "org", "⑥ OIDC role", CTRL, exit=(0.5, 0), entry=(0.682, 1), width=2)

    # Legend
    p.zone("Legend", 30, 1436, 520, 276, "#FFFFFF", INK, size=13)
    rows = [(TEL, False, "① Telemetry: MQTT over TLS, X.509 per device"), (ALERT, False, "② Crop alert: mobile push in under 5 minutes"), (BIZ, False, "③ Events: HTTPS, user token. ⑤ Queries: public, read-only"), (OBJ, False, "④ Drone objects: HTTPS, presigned URL, or IPsec at centers"), (FAIL, True, "Failure path: the state stays unchanged"), (CTRL, False, "⑥ Infrastructure delivery: pipeline with approval")]
    yy = 1466
    for color, dashed, text in rows:
        style = f"endArrow=block;endFill=1;html=1;strokeColor={color};strokeWidth=2;dashed={1 if dashed else 0};"
        p.edges.append(f'<mxCell id={quoteattr(p.nid())} value="" style={quoteattr(style)} edge="1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="44" y="{yy + 11}" as="sourcePoint"/><mxPoint x="92" y="{yy + 11}" as="targetPoint"/></mxGeometry></mxCell>')
        p.text(text, 100, yy, 440, 22, size=12)
        yy += 24
    p.chip("Blue box", 44, yy + 4, 76, 22, impl=True)
    p.text("Implemented in code, C01 to C10", 130, yy + 2, 400, 26, size=12, bold=True)
    p.chip("White box", 44, yy + 32, 76, 22)
    p.text("Designed and documented, not coded", 130, yy + 30, 400, 26, size=12)
    p.text("Dashed outline: reserved or prepared, nothing runs there.", 44, yy + 58, 490, 22, size=12)
    p.text("Detail by subject continues on the following pages.", 590, 1600, 1500, 24, size=12, color="#5D6D7E")
    return p


def end_to_end():
    p = Page("01 End to end", 1860, 1000, "Aroma Pacifico platform, farm to port: data paths, trust boundaries and identities")
    p.group("Field: untrusted networks", 40, 70, 330, 800, stroke=FAIL, dashed=True, sw=2)
    p.group("Centers: Federation LAN", 410, 612, 280, 258, stroke=FAIL, dashed=True, sw=2)
    p.group("AWS us-east-1: platform boundary", 740, 70, 790, 800, stroke=FAIL, dashed=True, sw=2)
    p.group("Public internet: consumers", 1580, 70, 240, 540, stroke=FAIL, dashed=True, sw=2)

    p.group("Farm with signal", 60, 104, 290, 130)
    p.note("Solar node with cultivation and drying probes. Buffer retains 24 h at most, then drops and counts.", 72, 136, 170, 88)
    p.net("Autonomous<br>node", 268, 136, "wireless_modem", "node")
    p.group("Farm out of coverage", 60, 246, 290, 130)
    p.net("Node with LoRa", 84, 276, "wireless_modem", "lnode")
    p.net("Shared gateway", 268, 276, "wireless_hub", "lgw")
    p.edge("lnode", "lgw", "LoRaWAN", TEL)
    p.group("Carrier in transit", 60, 390, 290, 130)
    p.note("Position every 5 min. With no data the app queues positions and always keeps custody events.", 72, 422, 170, 88)
    p.net("Carrier<br>phone", 278, 424, "mobile", "phone", w=36, h=52)
    p.group("Drone brigade", 60, 534, 290, 150)
    p.note("Mission loaded at the municipal seat or center before takeoff. Flight log stays in the drone buffer until the link returns.", 72, 566, 170, 108)
    p.net("Drone, ground<br>station", 268, 574, "wireless_modem", "ground")
    p.group("Port of Buenaventura", 60, 698, 290, 150)
    p.note("No Federation equipment here. The shipping company keeps its telemetry. The carrier application records the sack delivery event.", 80, 730, 250, 100)

    p.net("Logistics<br>stations", 450, 650, "pc", "stations")
    p.net("Code printer", 450, 770, "printer", "printer")
    p.net("Perimeter<br>firewall", 590, 710, "firewall", "fw")
    p.edge("stations", "printer", "", CTRL, exit=(0, 0.5), entry=(0, 0.5), points=[(432, 676), (432, 796)])
    p.edge("stations", "fw", "10.X.3.0/24", OBJ, exit=(1, 0.5), entry=(0, 0.5), points=[(530, 676), (530, 736)])

    for label, y, h in (("Telemetry", 104, 200), ("Sacks, trips and orders", 316, 130), ("Flight objects and inference", 458, 240)):
        p.group(label, 760, y, 750, h, stroke="#AEB6BF", color="#5D6D7E", align="right")
    p.aws("IoT Core<br>MQTT, LoRaWAN", 790, 136, "iot_core", IOT, "iot")
    p.aws("SQS queue", 950, 136, "sqs", APP, "sqs")
    p.aws("Ingestion<br>function", 1110, 136, "lambda", COMPUTE, "ingfn")
    p.aws("DynamoDB readings", 1270, 136, "dynamodb", DATA, "ddbr")
    p.aws("SNS alert", 1420, 136, "sns", APP, "sns")
    p.aws("Firehose", 950, 226, "kinesis_data_firehose", NET, "fh")
    p.aws("S3 archive, 5 years", 1270, 226, "s3", STORAGE, "arch")
    p.badge("C07", 1110, 110)
    p.aws("API Gateway<br>with Cognito", 790, 356, "api_gateway", NET, "api")
    p.aws("Domain<br>functions", 1110, 356, "lambda", COMPUTE, "domfn")
    p.aws("DynamoDB<br>sacks, cases", 1270, 356, "dynamodb", DATA, "ddbs")
    p.aws("S3 flight<br>objects", 790, 500, "s3", STORAGE, "objs")
    p.aws("EventBridge", 950, 500, "eventbridge", APP, "eb")
    p.aws("Inference<br>function", 1110, 500, "lambda", COMPUTE, "inffn")
    p.badge("C08", 1110, 474)
    p.aws("Rekognition<br>person filter", 1270, 500, "rekognition", ML, "rek")
    p.aws("Bedrock<br>image analysis", 1420, 500, "bedrock", ML, "bed")
    p.aws("SQS dead letter", 1090, 620, "sqs", APP, "dlq")
    p.aws("CloudWatch alarm", 1270, 620, "cloudwatch_2", MGMT, "cw")

    p.group("Applied to every flow", 760, 712, 750, 140, stroke="#AEB6BF", color="#5D6D7E")
    p.aws("KMS keys", 800, 746, "key_management_service", SEC)
    p.aws("Cognito", 930, 746, "cognito", SEC)
    p.aws("IAM roles", 1060, 746, "identity_and_access_management", SEC)
    p.aws("CloudTrail audit", 1190, 746, "cloudtrail", MGMT)
    p.aws("WAF", 1320, 746, "waf", SEC)
    p.aws("Budgets", 1430, 746, "budgets", MGMT)

    p.net("Farmer application", 1660, 120, "mobile", "farmer", w=36, h=52)
    p.net("Reports web", 1650, 250, "pc", "web")
    p.aws("CloudFront", 1650, 370, "cloudfront", NET, "cf")
    p.net("Buyer browser<br>sack code, no sign-in", 1650, 500, "pc", "buyer")

    p.edge("node", "iot", "MQTT over TLS, X.509", TEL, exit=(1, 0.5), entry=(0, 0.3))
    p.edge("lgw", "iot", "TLS over LTE, gateway certificate", TEL, exit=(1, 0.5), entry=(0, 0.75), points=[(640, 302), (640, 175)])
    p.edge("iot", "sqs", "rule", TEL)
    p.edge("sqs", "ingfn", "batch", TEL)
    p.edge("ingfn", "ddbr", "write once", TEL)
    p.edge("ddbr", "sns", "out of range", TEL)
    p.edge("sns", "farmer", "push under 5 min", TEL, exit=(1, 0.5), entry=(0, 0.5), points=[(1550, 162), (1550, 146)])
    p.edge("iot", "fh", "rule", TEL, exit=(1, 0.8), entry=(0, 0.5), points=[(880, 178), (880, 252)])
    p.edge("fh", "arch", "Parquet", TEL)
    p.edge("phone", "api", "HTTPS, Cognito token", BIZ, exit=(1, 0.5), entry=(0, 0.35), points=[(640, 450), (640, 374)])
    p.edge("api", "domfn", "invoke", BIZ)
    p.edge("domfn", "ddbs", "transaction", BIZ)
    p.edge("ground", "fw", "HTTPS at center Wi-Fi", OBJ, exit=(1, 0.5), entry=(0.5, 0), points=[(616, 600)])
    p.edge("fw", "api", "IPsec VPN, MFA user", BIZ, exit=(1, 0.3), entry=(0, 0.75), points=[(660, 726), (660, 395)])
    p.edge("fw", "objs", "IPsec VPN, presigned URL", OBJ, exit=(1, 0.7), entry=(0, 0.5), points=[(720, 746), (720, 526)])
    p.edge("objs", "eb", "object created", OBJ)
    p.edge("eb", "inffn", "trigger", OBJ)
    p.edge("inffn", "rek", "person?", OBJ)
    p.edge("rek", "bed", "no person", OBJ)
    p.edge("inffn", "ddbs", "result with confidence", OBJ, exit=(0.75, 0), entry=(1, 0.7), points=[(1149, 450), (1350, 450), (1350, 392)])
    p.edge("eb", "dlq", "after 3 retries", FAIL, dashed=True, exit=(1, 0.8), entry=(0, 0.5), points=[(1030, 542), (1030, 646)])
    p.edge("dlq", "cw", "alarm", FAIL, dashed=True)
    p.edge("web", "cf", "reports", BIZ, exit=(1, 0.5), entry=(1, 0.25), points=[(1760, 276), (1760, 383)])
    p.edge("farmer", "cf", "history", BIZ, exit=(1, 0.5), entry=(1, 0.75), points=[(1795, 146), (1795, 409)])
    p.edge("buyer", "cf", "HTTPS", BIZ, exit=(0.5, 0), entry=(0.5, 1))
    p.edge("cf", "domfn", "function URL behind WAF, read-only buyer view", BIZ, exit=(0, 0.5), entry=(0.5, 0), points=[(1560, 396), (1560, 310), (1136, 310)])

    p.group("Azure East US: prepared, idle", 1580, 630, 240, 240, stroke="#0078D4", dashed=True, sw=2)
    p.azure("IoT Hub", 1604, 664, "iot/IoT_Hub.svg")
    p.azure("Functions", 1720, 664, "compute/Function_Apps.svg")
    p.azure("Blob Storage", 1604, 744, "storage/Storage_Accounts.svg")
    p.azure("Azure OpenAI", 1720, 744, "ai_machine_learning/Azure_OpenAI.svg")
    p.text("No resources run here. Contracts and the equivalence table keep the exit open.", 1596, 812, 210, 50, size=11)
    p.legend(40, 884, 700, [(TEL, False, "Telemetry and alerts"), (BIZ, False, "Sack, trip and order events, and queries")])
    p.legend(760, 884, 480, [(OBJ, False, "Drone objects"), (FAIL, True, "Failure path, state stays unchanged")])
    p.note("C07 and C08 mark boxes built in the first infrastructure plan. Red dashed outlines are trust boundaries. 10.X is 41 Cauca, 42 Huila or 43 Tolima.", 1280, 884, 540, 74)
    return p


def cloud_deployment():
    p = Page("02 Implementation scope", 1860, 1100, "Everything the infrastructure code implements: one environment, boxes C01 to C10, within 100 hours")
    p.group("AWS us-east-1", 300, 70, 1520, 690, stroke=INK, sw=2)

    # Center
    p.group("Center, Cauca pattern", 30, 250, 250, 300, stroke=FAIL, dashed=True, sw=2)
    p.net("Logistics<br>10.41.3.0/24", 60, 290, "pc", "st")
    p.net("Local servers<br>10.41.10.0/24", 60, 420, "server", "sv")
    p.net("Perimeter firewall<br>10.41.20.0/24", 190, 360, "firewall", "cfw")
    p.edge("st", "cfw", "", OBJ, exit=(1, 0.5), entry=(0.5, 0), points=[(216, 316)])
    p.edge("sv", "cfw", "", OBJ, exit=(1, 0.5), entry=(0, 0.5), points=[(150, 446), (150, 386)])

    # VPC
    p.group("VPC, network account. Production 10.70.0.0/16, test 10.60.0.0/16, development 10.50.0.0/16", 330, 240, 1460, 340, stroke=NET, sw=2)
    p.badge("C03", 1740, 246)
    tiers = [("Telemetry ingress", 0, True), ("Drone object ingress", 16, True), ("Application", 32, True), ("Data", 48, False),
             ("Object storage", 64, False), ("Administration", 80, False), ("Public query", 96, False)]
    x = 450
    for name, base, used in tiers:
        p.group(name, x, 280, 186, 280, stroke="#147EBA", fill="#F2F8FC" if used else "#FFFFFF", dashed=not used)
        p.text(f"a 10.70.{base}.0/24<br>b 10.70.{base + 1}.0/24", x + 8, 306, 170, 36, size=11)
        x += 192
    p.aws("IoT data endpoint", 516, 370, "endpoints", NET, "ep1")
    p.aws("S3 endpoint", 708, 370, "endpoints", NET, "ep2")
    p.aws("Private API endpoint", 900, 370, "endpoints", NET, "ep3")
    p.text("Reserved. DynamoDB by gateway endpoint", 1034, 370, 170, 60, size=11, align="center")
    p.text("Reserved. S3 gateway endpoint route", 1226, 370, 170, 60, size=11, align="center")
    p.text("Reserved for administrative endpoints", 1418, 370, 170, 60, size=11, align="center")
    p.text("Reserved. CloudFront and API Gateway run outside the VPC", 1610, 370, 170, 60, size=11, align="center")
    p.aws("Virtual private<br>gateway", 354, 370, "site_to_site_vpn", NET, "vgw")
    p.badge("C04", 352, 346)
    p.edge("cfw", "vgw", "IPsec", OBJ, exit=(1, 0.5), entry=(0, 0.5), points=[(310, 386), (310, 396)])
    p.group("Permanent firewall rules, coded", 450, 480, 570, 66, stroke="#DD344C", color="#DD344C", fill="#FFFFFF")
    p.badge("C06", 972, 486)
    p.text("<b>SG-01 to SG-05</b> one group per endpoint, TCP 443 from logistics and local servers of each linked center, no outbound. "
           "<b>NACL-01 to NACL-04</b> 443 in and return ports out on endpoint subnets, deny on reserved ones.", 460, 502, 505, 42, size=10)
    p.edge("vgw", "ep1", "", OBJ)
    p.edge("vgw", "ep2", "", OBJ, exit=(1, 0.25), entry=(0, 0.25), points=[(424, 383), (424, 358), (700, 358), (700, 383)])
    p.edge("vgw", "ep3", "", OBJ, exit=(1, 0.25), entry=(0, 0.25), points=[(424, 383), (424, 350), (892, 350), (892, 383)])

    # Managed services above the VPC
    p.group("Telemetry ingestion pattern", 450, 104, 650, 124, stroke="#0B3D91", sw=2)
    p.badge("C07", 1050, 110)
    p.aws("S3 archive", 480, 134, "s3", STORAGE, "arc")
    p.aws("Firehose", 590, 134, "kinesis_data_firehose", NET, "fh")
    p.aws("IoT Core rule", 700, 134, "iot_core", IOT, "iot")
    p.aws("SQS with DLQ", 810, 134, "sqs", APP, "q")
    p.aws("Ingestion function", 920, 134, "lambda", COMPUTE, "fn")
    p.aws("DynamoDB, PITR", 1020, 134, "dynamodb", DATA, "ddb")
    p.edge("iot", "q", "", TEL)
    p.edge("q", "fn", "", TEL)
    p.edge("fn", "ddb", "", TEL)
    p.edge("fh", "arc", "", TEL)
    p.edge("iot", "fh", "", TEL)

    p.group("Inference function pattern", 1120, 104, 670, 124, stroke="#0B3D91", sw=2)
    p.badge("C08", 1740, 110)
    p.aws("S3 flight objects", 1150, 134, "s3", STORAGE, "obj")
    p.aws("EventBridge rule", 1260, 134, "eventbridge", APP, "eb")
    p.aws("Focus confirmation", 1370, 134, "lambda", COMPUTE, "cf")
    p.aws("Rekognition, Bedrock", 1480, 134, "bedrock", ML, "br")
    p.aws("Case table", 1590, 134, "dynamodb", DATA, "cs")
    p.aws("SQS DLQ", 1690, 134, "sqs", APP, "dl")
    p.edge("obj", "eb", "", OBJ)
    p.edge("eb", "cf", "", OBJ)
    p.edge("cf", "br", "", OBJ)
    p.edge("br", "cs", "", OBJ)
    p.edge("cf", "dl", "", FAIL, dashed=True, exit=(0.5, 0), entry=(0.5, 0), points=[(1396, 124), (1716, 124)])

    # Lower row
    p.group("Platform identities and encryption", 330, 600, 340, 150, stroke="#0B3D91", sw=2)
    p.badge("C05", 620, 606)
    p.aws("KMS keys", 360, 640, "key_management_service", SEC)
    p.aws("Function roles", 460, 640, "identity_and_access_management", SEC)
    p.aws("Pipeline OIDC roles", 570, 640, "identity_and_access_management", SEC)
    p.group("VPN keys", 680, 600, 130, 150, stroke="#AEB6BF", color="#5D6D7E", dashed=True)
    p.aws("Secrets Manager<br>created by AWS<br>for the C04 link", 719, 636, "secrets_manager", SEC)

    p.group("Remote state", 820, 600, 230, 150, stroke="#0B3D91", sw=2)
    p.badge("C02", 1000, 606)
    p.aws("S3 state bucket<br>native lock file", 900, 640, "s3", STORAGE, "state")

    p.group("Reserved for later plans", 1070, 600, 720, 150, stroke="#AEB6BF", color="#5D6D7E", dashed=True)
    p.text("API Gateway, domain functions, Cognito, CloudFront, WAF, the sack query and the three other inference triggers stay in the architecture and outside the code. So do the 200 farms, the three centers and the landing zone. The Huila and Tolima links reuse the C04 pattern, and each farm reuses C10.", 1090, 640, 680, 70, size=12)

    # Outside AWS: repo and pipeline
    p.group("Farm module", 30, 566, 250, 186, stroke="#0B3D91", sw=2)
    p.badge("C10", 232, 572)
    p.text("Reusable module, called for one sample farm. The 200 farms are not instantiated.", 42, 596, 228, 54, size=11)
    p.card("IoT thing and group", "Farm, department", 42, 650, 226, 44, impl=True)
    p.card("Certificate from CSR", "Key stays on the device", 42, 700, 226, 44, impl=True)
    p.group("Code and delivery, GitHub", 30, 764, 1790, 136, stroke=INK, sw=2)
    p.group("Infrastructure repository", 50, 796, 240, 96, stroke="#0B3D91", sw=2)
    p.group("Pipeline with approval", 310, 796, 900, 96, stroke="#0B3D91", sw=2)
    p.step("Root, environments<br>and tfvars with no secrets", 66, 824, 208, 58, cid="root")
    p.step("Pull request<br>fmt, validate, scan", 340, 824, 170, 58, cid="pr")
    p.step("Plan on the test<br>environment", 550, 824, 170, 58, cid="plan")
    p.step("Person approves<br>protected environment", 760, 824, 170, 58, cid="ok", stroke=FAIL)
    p.step("Apply<br>OIDC deployment role", 970, 824, 170, 58, cid="apply")
    p.group("Bring down", 1230, 796, 210, 96, stroke="#0B3D91", sw=2)
    p.step("Destroy, on demand<br>and each night", 1244, 824, 182, 58, cid="dst")
    p.badge("C01", 240, 800)
    p.badge("C09", 1160, 800)
    p.note("Validation evidence stays with each pull request. No production change between 05:00 and 18:00 in a harvest week, except during an incident.", 1460, 804, 344, 80)
    p.edge("root", "pr", "", CTRL)
    p.edge("pr", "plan", "", CTRL)
    p.edge("plan", "ok", "", CTRL)
    p.edge("ok", "apply", "", CTRL)
    p.legend(40, 916, 700, [(TEL, False, "Telemetry"), (OBJ, False, "Center and drone object traffic")])
    p.legend(760, 916, 500, [(FAIL, True, "Failure path"), (CTRL, False, "Delivery flow")])
    p.note("Blue badges C01 to C10 are the boxes the infrastructure code implements. Dashed subnets stay reserved. Each subnet has one /24 per zone inside a /20 block.", 1280, 916, 510, 74)
    return p


def connectivity():
    p = Page("03 Connectivity and centers", 1860, 1000, "How each site connects: protocol, buffer and behavior with no signal")
    p.group("Sites with no Federation LAN", 40, 70, 500, 636, stroke=FAIL, dashed=True, sw=2)
    rows = [("Farm with signal", "wireless_modem", 110, "n1"), ("Farm out of coverage", "wireless_modem", 230, "n2"),
            ("Drone at the lot", "wireless_modem", 350, "n3"), ("Carrier in transit", "mobile", 470, "n4"), ("Port of Buenaventura", "mobile", 590, "n5")]
    notes = ["Publishes on schedule. Buffer retains 24 h at most, and the alert goes out when it drains.",
             "LoRa reaches the shared gateway. Objects travel by data mule on daily routes.",
             "Mission preloaded. Flight log stays in the buffer. Fumigation stays unauthorized until the log closes.",
             "Position every 5 min. Queues positions, and custody events are always kept.",
             "No Federation equipment. Only the sack delivery event is recorded."]
    for (label, shape, y, cid), text in zip(rows, notes):
        p.group(label, 60, y, 460, 104)
        p.note(text, 72, y + 28, 350, 64)
        p.net("", 450, y + 32, shape, cid, w=36 if shape == "mobile" else 52, h=52)
    p.group("Cloud endpoints, us-east-1", 650, 70, 220, 620, stroke=INK, sw=2)
    p.aws("IoT Core", 734, 130, "iot_core", IOT, "iot")
    p.aws("API Gateway", 734, 480, "api_gateway", NET, "api")
    p.net("Shared LoRaWAN<br>gateway", 570, 256, "wireless_hub", "gw", w=44, h=44)
    p.edge("n1", "iot", "MQTT TLS, LTE", TEL, exit=(1, 0.5), entry=(0, 0.35), points=[(560, 168), (560, 148)])
    p.edge("n2", "gw", "LoRa", TEL, exit=(1, 0.5), entry=(0, 0.5), points=[(530, 288), (530, 278)])
    p.edge("gw", "iot", "TLS, LTE", TEL, exit=(1, 0.5), entry=(0, 0.75), points=[(690, 278), (690, 169)])
    p.edge("n4", "api", "HTTPS, LTE", BIZ, exit=(1, 0.5), entry=(0, 0.35), points=[(560, 528), (560, 498)])
    p.edge("n5", "api", "HTTPS, carrier app", BIZ, exit=(1, 0.5), entry=(0, 0.75), points=[(610, 648), (610, 519)])

    p.group("Collection center pattern, repeated three times. X is 41 Cauca, 42 Huila or 43 Tolima", 900, 70, 920, 620, stroke=FAIL, dashed=True, sw=2)
    zones = [("Management", "10.X.1.0/24", "2 desktops, 5 phones"), ("Support", "10.X.2.0/24", "2 desktops, 5 phones"),
             ("Logistics", "10.X.3.0/24", "2 desktops, 20 phones"), ("Transport", "10.X.4.0/24", "20 phones in the yard"),
             ("Visitors", "10.X.5.0/24", "10 phones"), ("Local servers", "10.X.10.0/24", "Printing, network control")]
    p.step("<b>LAN and WLAN</b><br>one VLAN and one SSID per zone", 1180, 110, 120, 548, fill="#EAF2F8", stroke="#147EBA", cid="bus")
    y = 110
    for i, (name, cidr, clients) in enumerate(zones):
        fill = "#FDEDEC" if name == "Visitors" else "#F2F8FC"
        p.step(f"<b>{name}</b><br>{cidr}<br>{clients}", 930, y, 200, 84, fill=fill, stroke="#147EBA", cid=f"z{i}")
        p.edge(f"z{i}", "bus", "", CTRL, exit=(1, 0.5), entry=(0, (y + 42 - 110) / 548))
        y += 94
    p.net("Perimeter firewall<br>10.X.20.0/24", 1385, 356, "firewall", "fw")
    p.edge("bus", "fw", "trunk", CTRL, exit=(1, 0.5), entry=(0, 0.5), points=[(1340, 384), (1340, 382)])
    p.note("<b>Isolation.</b> Visitors route to the internet only, with no path to logistics or management.", 1320, 110, 160, 110)
    p.note("<b>Tunnel routes.</b> Only 10.X.3.0/24 and 10.X.10.0/24 reach the cloud. Other zones use the internet.", 1320, 232, 160, 104)
    p.note("<b>Capacity.</b> 100 Mbps symmetric WAN. Up to 40 active clients at 2 Mbps down and 0.5 Mbps up. Logistics and drone sync first, visitors capped at 10 percent.", 1500, 570, 300, 100)

    p.group("Firewall policy, permanent rules", 1500, 110, 300, 448, stroke="#DD344C", color="#DD344C")
    table = ("<table style='font-size:11px' cellpadding='4'><tr><td><b>Source</b></td><td><b>Destination</b></td><td><b>Port</b></td><td><b>Action</b></td></tr>"
             "<tr><td>Logistics</td><td>Cloud API</td><td>443</td><td>Allow</td></tr>"
             "<tr><td>Local servers</td><td>Cloud API</td><td>443</td><td>Allow</td></tr>"
             "<tr><td>Logistics</td><td>Label printer</td><td>To confirm</td><td>Pending</td></tr>"
             "<tr><td>Transport</td><td>Internet</td><td>443</td><td>Allow</td></tr>"
             "<tr><td>Management</td><td>Internet</td><td>443</td><td>Allow</td></tr>"
             "<tr><td>Support</td><td>Internet</td><td>443</td><td>Allow</td></tr>"
             "<tr><td>Visitors</td><td>Internet</td><td>80, 443</td><td>Allow</td></tr>"
             "<tr><td>Every zone</td><td>Own gateway</td><td>DHCP, DNS</td><td>Allow</td></tr>"
             "<tr><td>Visitors</td><td>Private ranges</td><td>Any</td><td>Deny</td></tr>"
             "<tr><td>Any</td><td>Any</td><td>Any</td><td>Deny</td></tr></table>")
    p._v(table, "text;html=1;align=left;verticalAlign=top;whiteSpace=wrap;fontSize=11;strokeColor=none;fillColor=none;", 1510, 142, 280, 340)
    p.text("These rules stay for the whole pilot. The same set repeats at each center.", 1516, 490, 268, 50, size=11)

    p.group("Cloud", 900, 720, 920, 170, stroke=INK, sw=2)
    p.aws("Virtual private<br>gateway", 1385, 756, "site_to_site_vpn", NET, "vgw")
    p.badge("C04", 1444, 756)
    p.aws("Private endpoints<br>API and S3", 1240, 756, "endpoints", NET, "eps")
    p.text("VPC: production 10.70.0.0/16, test 10.60.0.0/16, development 10.50.0.0/16. No overlap with 10.41 to 10.43, and 10.44 to 10.49 stay reserved for future centers.", 920, 756, 280, 100, size=12)
    p.note("<b>Drone objects.</b> The ground station uploads at the center through the logistics zone, or at the municipal seat over LTE, with a presigned URL.", 1500, 750, 300, 100)
    p.edge("fw", "vgw", "IPsec VPN", OBJ, exit=(1, 0.5), entry=(0.5, 0), points=[(1465, 382), (1465, 712), (1411, 712)])
    p.edge("vgw", "eps", "", OBJ)
    p.edge("n3", "z2", "HTTPS when back in range", OBJ, exit=(1, 0.5), entry=(0, 0.5), points=[(885, 408), (885, 340)])
    p.legend(40, 720, 500, [(TEL, False, "Telemetry"), (BIZ, False, "Events and queries"), (OBJ, False, "Center and drone traffic"), (CTRL, False, "Local network")])
    p.note("<b>Mobile network.</b> Nodes, gateways and phones use LTE, which depends on no network generation being retired during the pilot. Coverage per site needs a survey before installation.", 40, 860, 830, 60)
    return p


def pest_flow():
    p = Page("04 Pest to fumigation", 1860, 1000, "From a sensor alert to a closed case: who acts, what each function does, and what stops the flow")
    lanes = [("Platform", 90, "#F4F6F7"), ("Inference functions", 230, "#E8F8F5"), ("Human decision, MFA", 370, "#FEF9E7"), ("Drone brigade", 510, "#EBF5FB")]
    for name, y, fill in lanes:
        p.group(name, 40, y, 1780, 130, stroke="#AEB6BF", fill=fill, color=INK)
    s = p.step
    s("Lot polygon and<br>no-fly zones published", 200, 124, 150, cid="a1", fill="#FFFFFF")
    s("Reading out of range<br>raises an alert", 370, 124, cid="a2")
    s("Confirmation<br>mission issued", 540, 124, cid="a3")
    s("Focus confirmed,<br>case open", 1020, 124, cid="a4")
    s("Fumigation order: farm, lot,<br>reason, window, operator", 1190, 124, 170, cid="a5")
    s("Log stored,<br>awaiting verification", 1420, 124, cid="a6")
    s("Case closed", 1640, 124, 130, cid="a7", fill="#E8F5E9", stroke=TEL)
    s("Person filter, then<br>Bedrock on the focus object", 760, 264, 190, cid="f1", fill="#FFFFFF", stroke=ML)
    s("Verification object<br>can close the case", 1620, 264, 170, cid="f2", stroke=ML)
    s("Supervisor authorizes<br>the order, named person", 1190, 404, 170, cid="h1", stroke=FAIL)
    s("Flies to the focus,<br>uploads object and log", 540, 544, 170, cid="d1")
    s("Fumigates in the window,<br>records product lot", 1190, 544, 170, cid="d2")
    s("Closes the fumigation<br>flight log", 1420, 544, 150, cid="d3")
    s("Verification photo<br>or short path", 1640, 544, 150, cid="d4")
    e = p.edge
    e("a1", "a2", "", BIZ); e("a2", "a3", "", BIZ)
    e("a3", "d1", "mission", BIZ, exit=(0.3, 1), entry=(0.3, 0))
    e("d1", "f1", "object in S3", OBJ, exit=(1, 0.5), entry=(0.5, 1), points=[(855, 575)])
    e("f1", "a4", "confirmed, with confidence", OBJ, exit=(1, 0.5), entry=(0.5, 1), points=[(1095, 295)])
    e("a4", "a5", "", BIZ)
    e("a5", "h1", "needs polygon and closed log", FAIL, exit=(0.5, 1), entry=(0.5, 0))
    e("h1", "d2", "authorized", BIZ, exit=(0.5, 1), entry=(0.5, 0))
    e("d2", "d3", "", OBJ)
    e("d3", "a6", "log persisted", OBJ, exit=(0.5, 0), entry=(0.5, 1))
    e("a6", "d4", "verification mission", BIZ, exit=(1, 0.75), entry=(0.12, 0), points=[(1600, 170), (1600, 520), (1658, 520)])
    e("d4", "f2", "object in S3", OBJ, exit=(0.5, 0), entry=(0.559, 1))
    e("f2", "a7", "closes", OBJ, exit=(0.5, 0), entry=(0.5, 1))

    p.group("Failure and stop conditions", 40, 650, 880, 230, stroke=FAIL, dashed=True, sw=2)
    p.note("<b>Person in the object.</b> The object moves to a restricted prefix, never reaches inference, and the operator repeats the capture.", 60, 684, 410, 84, fill="#FDEDEC", stroke=FAIL)
    p.note("<b>Inference fails.</b> The object stays, the state does not change. Three retries, then the dead letter queue and an alarm.", 490, 684, 410, 84, fill="#FDEDEC", stroke=FAIL)
    p.note("<b>No polygon or no closed log.</b> The order does not go out.", 60, 780, 410, 84, fill="#FDEDEC", stroke=FAIL)
    p.note("<b>Verification object missing.</b> The fumigation stays open, and the dashboard reports it.", 490, 780, 410, 84, fill="#FDEDEC", stroke=FAIL)

    p.group("The four event triggers", 940, 650, 880, 230, stroke=ML, color=ML)
    table = ("<table style='font-size:12px' cellpadding='4'><tr><td><b>Trigger</b></td><td><b>Function persists</b></td><td><b>Never does</b></td></tr>"
             "<tr><td>Focus confirmation object <b>(C08)</b></td><td>Whether the focus is confirmed</td><td>Authorize fumigation</td></tr>"
             "<tr><td>Verification object</td><td>Whether the case can close</td><td>Change state if the object is missing</td></tr>"
             "<tr><td>Estimation flight object</td><td>Estimated sacks for the center</td><td>Create a packing order</td></tr>"
             "<tr><td>Telemetry batch</td><td>Reading out of threshold</td><td>Fix thresholds in code</td></tr></table>"
             "<br>Each result stores time, confidence and source object in the same case file.")
    p._v(table, "text;html=1;align=left;verticalAlign=top;whiteSpace=wrap;fontSize=12;strokeColor=none;fillColor=none;", 960, 684, 840, 190)
    p.legend(40, 896, 880, [(BIZ, False, "State and order flow"), (OBJ, False, "Object and result flow"), ])
    p.note("Only a person authorizes fumigation. No trigger can do it. C08 marks the function pattern in the first infrastructure plan.", 940, 896, 880, 74)
    return p


def landing_zone():
    p = Page("05 Landing zone", 1860, 700, "AWS Organization: accounts, boundaries and controls applied from the root")
    p.group("AWS Organization root", 40, 70, 1780, 500, stroke=INK, sw=2)
    p.aws("Organizations", 90, 110, "organizations", MGMT, "org")
    p.group("Controls from the root", 200, 96, 1600, 110, stroke="#DD344C", color="#DD344C")
    for i, (label, icon, col) in enumerate([("Service control policies", "organizations", MGMT), ("IAM Identity Center, MFA", "identity_and_access_management", SEC),
                                             ("Cost tag policies", "organizations", MGMT), ("AWS Budgets", "budgets", MGMT), ("Organization trail", "cloudtrail", MGMT), ("Security Hub, GuardDuty", "security_hub", SEC)]):
        p.aws(label, 260 + i * 260, 130, icon, col, size=44)
    groups = [("Management", 70, 200, [("Management account", "Billing, organization, sign-in", "organizations", MGMT, "m")], None),
              ("Security OU", 290, 420, [("Log archive", "Audit logs for 5 years", "cloudtrail", MGMT, "s1"), ("Security tooling", "Findings, key admin", "security_hub", SEC, "s2")], None),
              ("Infrastructure OU", 730, 280, [("Network", "VPCs, VPN, DNS", "virtual_private_cloud", NET, "n")], None),
              ("Workloads OU", 1030, 760, [("Production", "10.70.0.0/16", None, None, "w1"), ("Test", "10.60.0.0/16, first plan", None, None, "w2"), ("Development", "10.50.0.0/16", None, None, "w3")], "wl")]
    for name, x, w, accounts, gid in groups:
        p.group(name, x, 230, w, 240, stroke="#5D6D7E", cid=gid)
        step = w // len(accounts)
        for i, (acc, role, icon, col, cid) in enumerate(accounts):
            ax = x + i * step + 10
            p.group(acc, ax, 266, step - 20, 190, stroke="#AEB6BF", color=INK)
            if icon:
                p.aws("", ax + (step - 20) // 2 - 26, 306, icon, col, cid)
                p.text(role, ax + 6, 376, step - 32, 60, size=12, align="center")
            else:
                p.text(role + "<br>Functions, tables and buckets of this environment", ax + 6, 306, step - 32, 120, size=12, align="center")
    p.note("The network account owns the VPCs and shares subnets with the workload accounts through AWS Resource Access Manager, so workload teams consume the network and cannot change it.", 730, 486, 1060, 60)
    p.edge("n", "wl", "shared subnets", NET, exit=(1, 0.5), entry=(0, 0.42), width=2)
    p.legend(40, 586, 700, [(NET, False, "Subnets shared through Resource Access Manager")])
    p.note("Red outline marks controls every account inherits. The Azure subscription of the second cloud stays empty and sits outside this organization.", 760, 586, 1060, 60)
    return p


def environments():
    p = Page("06 Environments", 1860, 1040, "Environments and controlled promotion: same code, separate ranges, state and data")
    envs = [("Development", 40, "#F2F3F4", [("Purpose", "Try changes"), ("Target account", "Development"), ("Lab account", "Shared credit account, optional"), ("Range", "10.50.0.0/16"), ("Zones", "One"), ("Data", "Simulated nodes"), ("In code", "Designed, variables can follow"), ("Stays up", "Only while in use")]),
            ("Test", 640, "#EBF5FB", [("Purpose", "Validate before production, first plan"), ("Target account", "Test"), ("Lab account", "Shared credit account"), ("Range", "10.60.0.0/16"), ("Zones", "One"), ("Data", "Synthetic readings, one sample farm"), ("In code", "Variables and plan, applied in the lab"), ("Stays up", "Hours, destroyed every night")]),
            ("Production", 1240, "#FDEDEC", [("Purpose", "The pilot"), ("Target account", "Production"), ("Lab account", "Shared credit account"), ("Range", "10.70.0.0/16"), ("Zones", "Two"), ("Data", "Real, after the pilot starts"), ("In code", "Variables and plan, apply needs approval"), ("Stays up", "Hours in the lab, always in the pilot")])]
    for name, x, fill, rows in envs:
        p.zone(name, x, 70, 580, 330, fill, "#566573")
        y = 104
        for k, v in rows:
            p.text(f"<b>{k}</b>", x + 16, y, 150, 30, size=12)
            p.text(v, x + 170, y, 400, 30, size=12)
            y += 35
    p.zone("Controlled promotion: a change moves through the same pipeline", 40, 416, 1780, 200, "#FFFFFF", "#0B3D91")
    steps = [("Pull request", "fmt, validate, security scan, cross review", "s1"), ("Merge to main", "Version tag on the module", "s2"), ("Plan and apply test", "Tag updated in envs/test", "s3"), ("Validation", "Smoke test on test", "s4"), ("Plan production", "Tag updated in envs/prod", "s5"), ("Person approves", "Protected environment", "s6"), ("Apply production", "OIDC role, outside the freeze", "s7")]
    for i, (t, sub, cid) in enumerate(steps):
        p.card(t, sub, 60 + i * 250, 462, 218, 84, cid, stroke=FAIL if cid == "s6" else "#7F8C8D")
    for a, b in zip(steps, steps[1:]):
        p.edge(a[2], b[2], "", CTRL, width=2)
    p.text("Rollback: point the root of the environment to the previous module tag and run the same pipeline. The state and the Git history keep what was deployed. No production change between 05:00 and 18:00 in a harvest week, except during an incident.", 60, 560, 1740, 40, size=12)
    p.zone("Bring up and down: credits are spent only while an environment is in use", 40, 632, 1780, 230, "#FFFFFF", "#0B3D91")
    ups = [("Bootstrap, once", "State buckets and OIDC roles, never destroyed", "u1"), ("Deploy workflow", "Manual, choose the environment", "u2"), ("Environment up", "About USD 0.09 an hour with VPN and endpoints", "u3"), ("Destroy workflow", "Manual, or each night", "u4"), ("Environment down", "Only bootstrap remains, near zero", "u5")]
    for i, (t, sub, cid) in enumerate(ups):
        p.card(t, sub, 60 + i * 352, 676, 310, 84, cid)
    for a, b in zip(ups, ups[1:]):
        p.edge(a[2], b[2], "", CTRL, width=2)
    p.edge("u5", "u2", "next session", CTRL, dashed=True, exit=(0.5, 1), entry=(0.5, 1), points=[(1604, 790), (567, 790)], width=2)
    p.text("Switches turn off the VPN and the interface endpoints when a session does not need them. Forgotten for a month, a full environment would burn about USD 60, which is why the nightly destroy exists.", 60, 806, 1740, 44, size=12)
    p.legend(40, 878, 700, [(CTRL, False, "Pipeline step"), (CTRL, True, "Next session starts again")])
    p.note("The lab uses one credit account for every environment, with no AWS Organization, because joining one moves a free account to the paid plan. The target design keeps the seven accounts. Azure stays undeployed.", 760, 878, 1060, 74)
    return p


def farm_sequence():
    p = Page("07 Farm connection sequence", 1560, 1280, "How a farm node connects, loses its link and recovers, with no reading lost silently")
    node, net, iot, ing, db = 250, 610, 860, 1120, 1390
    top, bottom = 70, 1100
    bands = [("Connection, each hour at the minute fixed for the node", 140, 372, "#EAF6EC", "#2E7D32"),
             ("Disconnection, a failure at any step ends the same way", 524, 276, "#FDEDEC", "#C62828"),
             ("Recovery, the signal returns", 812, 288, "#EAF2F8", "#147EBA")]
    for _, y, h, fill, stroke in bands:
        p.zone("", 40, y, 1480, h, fill, stroke)
    p.lifeline("Farm node", "Controller, flash buffer, LTE modem", node, top, bottom, net="wireless_modem")
    p.lifeline("Mobile network", "Attach and network time", net, top, bottom, net="radio_tower")
    p.lifeline("AWS IoT Core", "Broker, rule and shadow", iot, top, bottom, icon="iot_core", color=IOT)
    p.lifeline("Queue and function", "SQS, ingestion function", ing, top, bottom, icon="sqs", color=APP)
    p.lifeline("DynamoDB", "Readings and alert state", db, top, bottom, icon="dynamodb", color=DATA)
    for label, y, _, fill, _ in bands:
        p._v(label, f"text;html=1;align=left;verticalAlign=middle;fontSize=14;fontStyle=1;fontColor={INK};fillColor={fill};strokeColor=none;spacingLeft=6;", 50, y + 6, 470, 24)

    p.note("<b>Wake.</b> Read if due, append record with seq and measured_at, delete records of 24 h or more", 70, 176, 360, 44)
    p.message(node, net, 240, "Attach, network time", CTRL)
    p.message(node, iot, 274, "TLS, CONNECT clean session", CTRL)
    p.message(iot, node, 308, "CONNACK", CTRL, dashed=True)
    p.message(node, iot, 342, "PUBLISH QoS 1, oldest first, 10 unconfirmed at most", TEL)
    p.message(iot, ing, 342, "Rule adds received_at", TEL)
    p.message(ing, db, 342, "Conditional write", TEL)
    p.message(iot, node, 376, "PUBACK, record leaves the buffer", TEL, dashed=True)
    p.message(node, iot, 410, "Get shadow", BIZ)
    p.message(iot, node, 444, "Desired state, drying on or off", BIZ, dashed=True)
    p.message(node, iot, 478, "DISCONNECT, then modem off and sleep", CTRL)

    p.message(node, net, 572, "Attach fails, window of 120 s ends", FAIL)
    p.note("<b>No path.</b> Records stay. The next hour is the retry", 70, 590, 360, 34)
    p.message(node, iot, 640, "PUBLISH seq n", TEL)
    p.message(iot, ing, 640, "Copy to queue", TEL)
    p.message(ing, db, 640, "Stored", TEL)
    p.message(iot, 540, 674, "PUBACK lost", FAIL, dashed=True)
    p.note("<b>No PUBACK in 10 s.</b> Record stays, modem off, sleep until the next hour", 70, 700, 360, 34)
    p.note("<b>At 24 h.</b> A record still waiting is deleted, and dropped_total grows", 70, 746, 360, 34)

    p.message(node, net, 850, "Attach, signal is back", CTRL)
    p.message(node, iot, 886, "PUBLISH seq n, repeat, buffered true", TEL)
    p.message(iot, ing, 886, "Copy to queue", TEL)
    p.message(ing, db, 886, "Conditional write", TEL)
    p.message(db, ing, 920, "Rejected, already stored", FAIL, dashed=True)
    p.message(iot, node, 954, "PUBACK, record leaves the buffer", TEL, dashed=True)
    p.message(node, iot, 988, "PUBLISH seq n+1 and newer, buffered true", TEL)
    p.message(iot, ing, 988, "Copy to queue", TEL)
    p.message(ing, db, 988, "Stored, state if newer", TEL)
    p.note("<b>Alerts.</b> Only a newer measured_at changes the alert state. An alert from an old reading carries the time of that reading", 960, 1020, 540, 44)
    p.message(node, iot, 1064, "Get shadow, DISCONNECT, sleep", CTRL)

    p.legend(40, 1116, 560, [(TEL, False, "Reading and its confirmation"), (BIZ, False, "Configuration through the shadow"),
                             (CTRL, False, "Connection control"), (FAIL, False, "Failure or rejection"), (CTRL, True, "Dashed line, an answer to a request")])
    return p


def sack_states():
    p = Page("08 Sack state model", 1560, 830, "Sack states and transitions: from the farm to the port, and what a rejection does")
    zones = [("Farm", 40, 260, "#EAF6EC", "#2E7D32"), ("Road to the center", 310, 280, "#F2F3F4", "#566573"), ("Collection center", 600, 310, "#EAF2F8", "#147EBA"),
             ("Road to the port", 920, 280, "#F2F3F4", "#566573"), ("Port of Buenaventura", 1210, 310, "#FDF2E9", "#E65100")]
    for name, x, w, fill, stroke in zones:
        p.zone(name, x, 70, w, 480, fill, stroke, size=13)
    state = dict(w=190, h=70, size=12)
    p.step("<b>in_preparation</b><br>Farmer holds the sack", 55, 280, cid="prep", **state)
    p.step("<b>in_transit_to_center</b><br>Carrier holds the sack", 385, 280, cid="toc", **state)
    p.step("<b>at_center_accepted</b><br>Center holds the sack", 650, 170, fill="#E8F5E9", stroke="#2E7D32", cid="acc", **state)
    p.step("<b>at_center_rejected</b><br>Resting state", 650, 400, fill="#FDEDEC", stroke="#C62828", cid="rej", **state)
    p.step("<b>in_transit_to_port</b><br>Carrier holds the sack", 985, 170, cid="top", **state)
    p.step("<b>delivered_accepted</b><br>End of the record", 1285, 110, fill="#E8F5E9", stroke="#2E7D32", cid="ok", **state)
    p.step("<b>delivered_rejected</b><br>End of the record", 1285, 240, fill="#FDEDEC", stroke="#C62828", cid="no", **state)
    p.step("Start at the farm", 52, 120, w=105, h=56, fill="#FFFFFF", cid="s1", size=11)
    p.step("Start at the center, no code", 175, 120, w=115, h=56, fill="#FFFFFF", cid="s2", size=11)
    p.edge("s1", "prep", "registered", TEL, exit=(0.5, 1), entry=(0.2, 0))
    p.edge("s2", "prep", "registered_at_center", OBJ, dashed=True, exit=(0.5, 1), entry=(0.8, 0))
    p.edge("prep", "toc", "handed_to_carrier", TEL)
    p.edge("toc", "acc", "received_accepted", TEL, exit=(1, 0.3), entry=(0, 0.5), points=[(615, 301), (615, 205)])
    p.edge("toc", "rej", "received_rejected", FAIL, exit=(1, 0.7), entry=(0, 0.5), points=[(615, 329), (615, 435)])
    p.edge("prep", "acc", "reception, sack with no code", OBJ, dashed=True, exit=(1, 0.15), entry=(0.5, 0), points=[(305, 290), (305, 145), (745, 145)])
    p.edge("prep", "rej", "reception, sack with no code", OBJ, dashed=True, exit=(1, 0.85), entry=(0.2, 1), points=[(305, 340), (305, 490), (688, 490)])
    p.edge("acc", "rej", "", CTRL, exit=(0.3, 1), entry=(0.3, 0))
    p.edge("rej", "acc", "", CTRL, exit=(0.7, 0), entry=(0.7, 1))
    p.text("Correct to rejected, with reason", 620, 290, 84, 60, size=11, align="right")
    p.text("Correct to accepted, with reason", 792, 290, 100, 60, size=11)
    p.edge("acc", "top", "dispatched_to_port", TEL)
    p.edge("top", "ok", "", TEL, exit=(1, 0.3), entry=(0, 0.5), points=[(1235, 191), (1235, 145)])
    p.text("delivered_accepted", 1090, 150, 130, 22, size=11, align="right")
    p.edge("top", "no", "", FAIL, exit=(1, 0.7), entry=(0, 0.5), points=[(1235, 219), (1235, 275)])
    p.text("delivered_rejected", 1090, 250, 130, 22, size=11, align="right")
    p.edge("rej", "prep", "returned_to_farm, same code and same history", FAIL, exit=(0.5, 1), entry=(0.5, 1), points=[(745, 520), (150, 520)])
    p.note("<b>The history keeps every event.</b> Arrival, pickup, reweighing, label reprint and a missing report change no state.", 1225, 400, 280, 66)
    p.legend(40, 566, 560, [(TEL, False, "Normal path"), (FAIL, False, "Rejection and return"), (CTRL, False, "Correction, before the sack leaves the center"),
                             (OBJ, True, "Only a sack registered at the center")])
    p.note("<b>Applied.</b> The event fits the history, and the state moves.", 620, 566, 280, 66)
    p.note("<b>Gap.</b> An earlier event is missing. The state moves, and the late event closes the gap.", 920, 566, 280, 66)
    p.note("<b>Anomaly.</b> The event contradicts the history. It is kept for review, and the state stays.", 1220, 566, 280, 66)
    p.note("<b>Order.</b> The state comes from replaying the history by time of capture, so any arrival order gives the same result.", 620, 646, 880, 44)
    return p


def center_wlan():
    p = Page("09 Center WLAN", 1700, 940, "How the WLAN of a center is segmented: SSID, VLAN and what each zone may reach")
    p.group("Wi-Fi clients and their SSID", 40, 70, 400, 640, stroke=FAIL, dashed=True, sw=2)
    zones = [("Management", "AP-GER, VLAN 101", "10.X.1.0/24, WPA3-Personal"), ("Support", "AP-SOP, VLAN 2", "10.X.2.0/24, WPA3-Personal"),
             ("Logistics", "AP-LOG, VLAN 3", "10.X.3.0/24, WPA3-Personal"), ("Transport", "AP-TRA, VLAN 4", "10.X.4.0/24, WPA3-Personal"),
             ("Visitors", "AP-VIS, VLAN 5", "10.X.5.0/24, isolated clients")]
    p.step("<b>Access points</b><br>2 to 3, powered by the switch<br>five SSIDs<br>one VLAN per SSID", 520, 110, 150, 548, fill="#EAF2F8", stroke="#147EBA", cid="ap")
    for i, (name, ssid, net_) in enumerate(zones):
        y = 110 + i * 110
        fill = "#FDEDEC" if name == "Visitors" else "#F2F8FC"
        p.step(f"<b>{name}</b><br>{ssid}<br>{net_}", 60, y, 360, 92, fill=fill, stroke="#147EBA", cid=f"z{i}")
        p.edge(f"z{i}", "ap", ssid.split(",")[0], BIZ, exit=(1, 0.5), entry=(0, (i * 110 + 46) / 548))
    p.step("<b>Managed switch</b><br>trunks carry only the listed VLANs<br>no routing", 750, 339, 140, 90, fill="#EAF2F8", stroke="#147EBA", cid="sw")
    p.net("Perimeter firewall<br>gateway of every zone", 1040, 358, "firewall", "fw")
    p.edge("ap", "sw", "trunk, tagged", CTRL, exit=(1, 0.5), entry=(0, 0.5))
    p.edge("sw", "fw", "trunk, all zone VLANs", CTRL, exit=(1, 0.5), entry=(0, 0.5))

    p.group("Local servers, VLAN 10, wired only, 10.X.10.0/24", 1160, 70, 500, 270, stroke="#147EBA", color="#147EBA")
    p.step("<b>Label printer</b><br>10.X.10.6", 1180, 130, 140, 70, fill="#F2F8FC", stroke="#147EBA", cid="prt")
    p.step("<b>Switch</b><br>10.X.10.2", 1340, 130, 140, 70, fill="#F2F8FC", stroke="#147EBA", cid="swm")
    p.step("<b>Access points</b><br>10.X.10.3 to .5", 1500, 130, 140, 70, fill="#F2F8FC", stroke="#147EBA", cid="apm")
    p.step("<b>Administration host</b><br>10.X.10.11 to .20", 1340, 250, 140, 70, fill="#FFF8E1", stroke="#D6B656", cid="adm")
    p.note("Each device accepts administration only from the administration host.", 1180, 250, 140, 70)
    p.edge("adm", "swm", "admin only", CTRL, exit=(0.5, 0), entry=(0.5, 1))
    p.edge("adm", "apm", "admin only", CTRL, exit=(1, 0.5), entry=(0.5, 1), points=[(1570, 285)])
    p.net("Internet", 1290, 358, "cloud", "net", w=80, h=52)
    p.edge("fw", "prt", "Printing rule, pending", OBJ, dashed=True, exit=(1, 0.1), entry=(0, 0.5), points=[(1125, 363), (1125, 165)])
    p.edge("fw", "net", "HTTPS 443, visitors 80 and 443", OBJ, exit=(1, 0.5), entry=(0, 0.5))

    p.group("Cloud, us-east-1", 1160, 480, 500, 210, stroke=INK, sw=2)
    p.aws("Virtual private<br>gateway", 1260, 540, "site_to_site_vpn", NET, "vgw")
    p.aws("Private endpoints<br>API and S3", 1500, 540, "endpoints", NET, "eps")
    p.edge("fw", "vgw", "IPsec VPN, logistics and local servers only", OBJ, exit=(1, 0.9), entry=(0, 0.5), points=[(1125, 405), (1125, 566)])
    p.edge("vgw", "eps", "", OBJ)

    p.group("Four layers keep visitors apart, and each one stops them on its own", 460, 730, 1200, 180, stroke=FAIL, color=FAIL)
    layers = [("<b>1. Access point.</b> Client isolation on AP-VIS stops one visitor phone from reaching another."),
              ("<b>2. VLAN and trunk.</b> VLAN 5 exists only on the access point trunks and the firewall uplink, with no wired port."),
              ("<b>3. Firewall.</b> Deny toward every private range and toward the firewall itself, ahead of the internet allow. Only DHCP and DNS reach the gateway."),
              ("<b>4. Tunnel and cloud.</b> No route for 10.X.5.0/24, and endpoint security groups accept only logistics and local servers.")]
    for i, text in enumerate(layers):
        p.note(text, 480 + i * 290, 770, 270, 110, fill="#FDEDEC", stroke="#DD344C")
    p.legend(40, 730, 400, [(BIZ, False, "Wi-Fi association, named by SSID"), (CTRL, False, "Wired trunk or administration"), (OBJ, False, "Path the firewall allows"), (OBJ, True, "Rule defined, not enabled")])
    p.note("<b>X is 41 Cauca, 42 Huila or 43 Tolima.</b> Only logistics and local servers reach the cloud. No zone reaches another. The printing rule from logistics stays pending until address, protocol and port are confirmed.", 40, 858, 400, 70)
    return p


def drone_link():
    p = Page("10 Drone mission link", 1700, 1460, "How a drone mission is preloaded, flown with no signal and published, with no evidence lost or counted twice")
    drone, gs, api, kms, s3, case = 230, 520, 820, 1060, 1300, 1530
    top, bottom = 70, 1270
    bands = [("Preload at the municipal seat or collection center, online", 140, 404, "#EAF2F8", "#147EBA"),
             ("At the lot, no signal needed", 560, 262, "#FEF9E7", "#B7950B"),
             ("Synchronization on return, municipal seat or collection center", 838, 432, "#EAF6EC", "#2E7D32")]
    for _, y, h, fill, stroke in bands:
        p.zone("", 40, y, 1620, h, fill, stroke)
    p.lifeline("Drone and controller", "Native log and evidence storage", drone, top, bottom, net="wireless_modem")
    p.lifeline("Ground station", "Brigade laptop, encrypted store, journal", gs, top, bottom, net="pc")
    p.lifeline("Mission API", "API Gateway and mission functions", api, top, bottom, icon="api_gateway", color=APP)
    p.lifeline("AWS KMS", "Asymmetric signing key", kms, top, bottom, icon="key_management_service", color=SEC)
    p.lifeline("Amazon S3", "Encrypted, versioned objects", s3, top, bottom, icon="s3", color=STORAGE)
    p.lifeline("Case table", "DynamoDB, records and keys", case, top, bottom, icon="dynamodb", color=DATA)
    for label, y, _, fill, _ in bands:
        p._v(label, f"text;html=1;align=left;verticalAlign=middle;fontSize=14;fontStyle=1;fontColor={INK};fillColor={fill};strokeColor=none;spacingLeft=6;", 50, y + 6, 560, 24)

    p.message(gs, api, 190, "Sign in, Cognito with second factor", BIZ)
    p.message(api, kms, 224, "Sign manifest digest", CTRL)
    p.message(kms, api, 258, "ECDSA signature", CTRL, dashed=True)
    p.message(api, gs, 292, "Signed manifest, download links", BIZ, dashed=True)
    p.message(gs, s3, 326, "Download package files", OBJ)
    p.message(s3, gs, 360, "Polygon, exclusions, route", OBJ, dashed=True)
    p.note("<b>Check and store.</b> Signature with the pinned public key, every SHA-256, then one atomic move into the mission store", 70, 378, 400, 44)
    p.message(gs, api, 444, "Station acknowledgement, package digest", BIZ)
    p.message(gs, drone, 478, "Load mission, local link", BIZ)
    p.message(drone, gs, 512, "Loaded digest read back", BIZ, dashed=True)

    p.note("<b>Preflight.</b> Inside the window, highest revision, not suspended, same polygon and exclusion versions, free storage, and for a fumigation a human authorization for this revision", 70, 596, 400, 58)
    p.note("<b>Flight.</b> The drone flies the loaded mission and writes its log, photos and evidence to its own storage", 70, 664, 400, 40)
    p.message(drone, gs, 726, "Log and evidence, file by file", OBJ)
    p.note("<b>Journal.</b> Each file copied, hashed and journaled. The drone copy stays until the station copy matches", 70, 744, 400, 44)
    p.message(gs, 780, 804, "No path, upload waits", FAIL, dashed=True)

    p.message(gs, api, 888, "Sign in again, object list with sizes and SHA-256", BIZ)
    p.message(api, gs, 922, "Missing objects, fresh presigned URLs", BIZ, dashed=True)
    p.message(gs, s3, 956, "PUT with SHA-256 checksum, one URL per object", OBJ)
    p.message(s3, gs, 990, "Version ID, or rejected and retried", OBJ, dashed=True)
    p.message(gs, api, 1024, "Completion, manifest signed by the station key", BIZ)
    p.note("<b>Station identity.</b> Signature checked against the station certificate in the IoT registry. A revoked station cannot publish", 860, 1042, 400, 44)
    p.message(api, s3, 1108, "Read checksum and version", CTRL)
    p.message(s3, api, 1142, "Stored checksum, version ID", CTRL, dashed=True)
    p.message(api, case, 1176, "Conditional write, flight record", BIZ)
    p.message(api, gs, 1210, "Publication receipt", BIZ, dashed=True)
    p.note("<b>Delete.</b> The station deletes its copy only after the receipt. A repeated request returns the same receipt", 70, 1226, 400, 36)

    p.legend(40, 1286, 560, [(BIZ, False, "Mission, acknowledgement and record"), (OBJ, False, "Package files and flight evidence"),
                             (CTRL, False, "Signing and verification"), (FAIL, False, "Failure, data stays local"), (CTRL, True, "Dashed line, an answer to a request")])
    p.note("<b>Fumigation.</b> A fumigation package exists only after the prerequisite flight is published and a supervisor, distinct from the pilot, authorizes it. Inference never authorizes.", 620, 1286, 1040, 50)
    p.note("<b>Large files.</b> Above 100 MB the station uses a multipart upload with a full-object CRC checksum, keeps its upload ID, and resends only missing parts. Verification then computes the SHA-256.", 620, 1350, 1040, 50)
    return p


def audit_path():
    p = Page("11 Audit evidence path", 1860, 990, "How evidence of the four sensitive events reaches a store that no account can alter")
    p.group("People and devices", 40, 80, 260, 640, stroke="#5D6D7E")
    p.card("Buyer or app user", "Reads a sack", 60, 140, 220, 64, cid="src_app", net="mobile")
    p.card("Platform operator", "Changes a threshold", 60, 280, 220, 64, cid="src_op", net="pc")
    p.card("Farm node", "Publishes telemetry", 60, 420, 220, 64, cid="src_node", net="wireless_modem")
    p.card("Ground station", "Delivers flight objects", 60, 560, 220, 64, cid="src_gs", net="pc")

    p.group("Workload account, one per environment", 340, 80, 720, 640, stroke=INK, sw=2)
    p.card("API Gateway", "Request ID, access log", 370, 140, 190, 64, cid="api", icon="api_gateway", color=APP)
    p.card("Platform functions", "Query, domain, upload", 610, 140, 200, 64, cid="fn", icon="lambda", color=COMPUTE)
    p.card("Audit log group", "Events, 90 days", 850, 140, 190, 64, cid="lg_app", icon="cloudwatch_2", color=MGMT)
    p.card("Ranges table", "Alert thresholds", 610, 280, 200, 64, cid="ranges", icon="dynamodb", color=DATA)
    p.card("IoT Core", "Broker", 370, 420, 190, 64, cid="iot", icon="iot_core", color=IOT)
    p.card("IoT log group", "Publish-In, farm groups", 850, 420, 190, 64, cid="lg_iot", icon="cloudwatch_2", color=MGMT)
    p.card("Flight object bucket", "Presigned uploads", 610, 560, 200, 64, cid="flights", icon="s3", color=STORAGE)

    p.group("Log archive account", 1100, 80, 720, 640, stroke=SEC, sw=2, color=SEC)
    p.card("Logs destination", "Receives subscriptions", 1130, 280, 200, 64, cid="dest", icon="cloudwatch_2", color=MGMT)
    p.card("Firehose", "Decompress, one event per line", 1130, 420, 200, 64, cid="fh", icon="kinesis_data_firehose", color="#8C4FFF")
    p.card("Organization trail", "Data events, digests", 1130, 560, 200, 64, cid="trail", icon="cloudtrail", color=MGMT)
    p.card("Audit bucket", "Object Lock compliance, 5 years, audit key", 1380, 410, 230, 84, cid="bucket", icon="s3", color=STORAGE, impl=False, stroke=SEC)
    p.card("Athena", "Evidence queries", 1650, 280, 150, 64, cid="athena", icon="athena", color="#8C4FFF")
    p.card("Security role", "Read only", 1650, 560, 150, 64, cid="sec", icon="identity_and_access_management", color=SEC)

    p.edge("src_app", "api", "1 Read a sack", BIZ, exit=(1, 0.5), entry=(0, 0.3))
    p.edge("src_op", "api", "2 Change a threshold", BIZ, exit=(1, 0.5), entry=(0, 0.75), points=[(330, 312), (330, 188)])
    p.edge("api", "fn", "", BIZ)
    p.edge("fn", "lg_app", "Audit event", BIZ)
    p.edge("fn", "ranges", "Write", BIZ, exit=(0.5, 1), entry=(0.5, 0))
    p.edge("src_node", "iot", "3 Publish", TEL, exit=(1, 0.5), entry=(0, 0.5))
    p.edge("iot", "lg_iot", "Publish-In entry", TEL)
    p.edge("src_gs", "api", "4 Ask for a URL", OBJ, exit=(1, 0.25), entry=(0.1, 1), points=[(352, 576), (352, 240), (389, 240)])
    p.edge("src_gs", "flights", "4 PUT with the URL", OBJ, exit=(1, 0.5), entry=(0, 0.5))
    p.edge("lg_app", "dest", "Subscription", BIZ, exit=(1, 0.5), entry=(0, 0.3), points=[(1070, 172), (1070, 299)])
    p.edge("lg_iot", "dest", "Subscription", TEL, exit=(1, 0.3), entry=(0, 0.75), points=[(1070, 439), (1070, 328)])
    p.edge("dest", "fh", "", BIZ)
    p.edge("fh", "bucket", "app/ and iot/", BIZ)
    p.edge("ranges", "trail", "Table writes", CTRL, exit=(0.9, 1), entry=(0, 0.25), points=[(790, 530), (1090, 530), (1090, 576)])
    p.edge("flights", "trail", "PutObject", CTRL, exit=(1, 0.5), entry=(0, 0.6))
    p.edge("trail", "bucket", "AWSLogs/", CTRL, exit=(1, 0.5), entry=(0.5, 1), points=[(1495, 592)])
    p.edge("sec", "athena", "Runs queries", CTRL, dashed=True, exit=(0.5, 0), entry=(0.5, 1))
    p.edge("athena", "bucket", "Reads", CTRL, dashed=True, exit=(0.5, 1), entry=(1, 0.3), points=[(1725, 435)])

    p.legend(40, 740, 560, [(BIZ, False, "Platform events, sack reads, thresholds, URL grants"), (TEL, False, "Telemetry publications"),
                             (OBJ, False, "Flight object delivery"), (CTRL, False, "CloudTrail data events"), (CTRL, True, "Reading the evidence")])
    p.note("<b>Immutable.</b> No user, root included, can delete or overwrite a locked version for five years. Only CloudTrail and the Firehose role of the log archive account write to the bucket.", 620, 740, 600, 64)
    p.note("<b>Two records for objects.</b> The upload function names the drone operator when it grants the URL. CloudTrail names the signing role and proves the arrival. They join on the object key.", 1240, 740, 580, 64)
    p.note("<b>Direct writes.</b> A write on the ranges table that did not come from a platform function appears in the trail and is flagged by the threshold query.", 620, 820, 600, 50)
    p.note("<b>Workload accounts.</b> Each one sends its own events. Its roles hold no write access to the archive.", 1240, 820, 580, 50)
    return p


def lot_geometry():
    p = Page("12 Lot geometry lifecycle", 1780, 760, "Lot polygon states: from no-fly zones to a published version that missions can use")
    zones = [("Before the first flight", 40, 560, "#EAF2F8", "#147EBA"), ("Delimitation flight and review", 615, 565, "#FEF9E7", "#B7950B"),
             ("In use by missions", 1195, 545, "#EAF6EC", "#2E7D32")]
    for name, x, w, fill, stroke in zones:
        p.zone(name, x, 70, w, 380, fill, stroke, size=13)
    state = dict(w=180, h=84, size=12)
    p.step("<b>DRAFT</b><br>Zones or polygon<br>in preparation", 70, 130, cid="draft", **state)
    p.step("<b>EXCLUSIONS_READY</b><br>Only the delimitation flight<br><i>lot.exclusions.ready</i>", 360, 130, cid="excl", **state)
    p.step("<b>SURVEYED</b><br>Candidate polygon<br>from the flight", 650, 130, cid="surv", **state)
    p.step("<b>VALIDATED</b><br>Polygon and no-spray<br>strips accepted", 940, 130, cid="val", **state)
    p.step("<b>PUBLISHED</b><br>Precision and estimation<br><i>lot.geometry.published</i>", 1230, 130, fill="#E8F5E9", stroke=TEL, cid="pub", **state)
    p.step("<b>SUSPENDED</b><br>No new mission<br><i>lot.geometry.suspended</i>", 1520, 130, fill="#FDEDEC", stroke=FAIL, cid="susp", **state)
    p.edge("draft", "excl", "zones reviewed", TEL)
    p.edge("excl", "surv", "log stored", TEL)
    p.edge("surv", "val", "checks pass", TEL)
    p.edge("val", "pub", "published", TEL)
    p.edge("pub", "susp", "safety reason", FAIL)
    p.edge("excl", "draft", "", FAIL, exit=(0.5, 1), entry=(0.75, 1), points=[(450, 254), (205, 254)])
    p.edge("surv", "draft", "", FAIL, exit=(0.5, 1), entry=(0.5, 1), points=[(740, 279), (160, 279)])
    p.edge("val", "draft", "", FAIL, exit=(0.5, 1), entry=(0.25, 1), points=[(1030, 304), (115, 304)])
    p.text("Correction or failed check returns the candidate to draft", 260, 256, 380, 20, size=11, color=FAIL)
    p.edge("susp", "draft", "", OBJ, dashed=True, exit=(0.5, 1), entry=(0.11, 1), points=[(1610, 334), (90, 334)])
    p.text("A replacement starts as a new draft, and the published version stays in use until it is replaced", 700, 336, 620, 20, size=11, color=OBJ)
    p.note("<b>Supervisor.</b> Maps houses, the processing facility, roads and water as no-fly zones, or records that there are none.", 60, 372, 520, 60)
    p.note("<b>Checks.</b> Flight log and map stored, valid GeoJSON, ring direction, no self-intersection, strips computed in metres in EPSG 9377.", 635, 372, 525, 60)
    p.note("<b>Missions.</b> Each package carries this exact version. A fumigation also needs a closed prior log and a named supervisor.", 1215, 372, 505, 60)

    p.group("No-spray strips for the drone, stored as versioned parameters", 580, 480, 1160, 250, stroke=FAIL, color=FAIL)
    table = ("<table style='font-size:12px' cellpadding='4'><tr><td><b>Place</b></td><td><b>Drone</b></td><td><b>Ground</b></td><td><b>Basis</b></td></tr>"
             "<tr><td>Rivers, streams, lakes</td><td>100 m</td><td>10 m</td><td>Decree 1843 of 1991, article 87</td></tr>"
             "<tr><td>Springs</td><td>100 m</td><td>100 m</td><td>Decree 1076 of 2015, protective forest area</td></tr>"
             "<tr><td>Houses and processing facility</td><td>100 m</td><td>10 m</td><td>Decree 1843, articles 87 and 102</td></tr>"
             "<tr><td>Main roads</td><td>100 m</td><td>10 m</td><td>Decree 1843, article 87</td></tr>"
             "<tr><td>People outside the operation</td><td>30 m, no flight</td><td></td><td>RAC 100, sections 100.310 and 100.410</td></tr></table>")
    p._v(table, "text;html=1;align=left;verticalAlign=top;whiteSpace=wrap;fontSize=12;strokeColor=none;fillColor=none;", 600, 514, 700, 200)
    p.note("<b>Ground fallback.</b> A focus inside the drone strip and outside the ground strip becomes a ground application by the brigade, with the same authorization. Inside the ground strip no product is applied.", 1320, 520, 400, 100, fill="#FDEDEC", stroke=FAIL)
    p.note("<b>Pending.</b> Strips for minor roads and narrower water strips with barriers wait for a legal review.", 1320, 634, 400, 70)
    p.legend(40, 480, 520, [(TEL, False, "Normal path, conditional write"), (FAIL, False, "Correction, failure or suspension"), (OBJ, True, "Replacement by a new version")])
    p.note("No state can be skipped, and a published version is never edited.", 40, 596, 520, 44)
    return p


def center_operation():
    p = Page("13 Center operation", 1700, 1050, "How a collection center receives, labels and dispatches sacks, and what limits it at 400 sacks a day")
    p.group("Reception: arrival is one action for the load, the decision is one event for each sack", 30, 60, 1640, 250, stroke=FAIL, dashed=True, sw=2)
    top = [("<b>1. Load arrives</b><br>carrier, once<br>arrived_at_center", "t1"), ("<b>2. Waiting area</b><br>sacks stay in transit<br>no event", "t2"),
           ("<b>3. Scan the label</b><br>15 s, assumed", "t3"), ("<b>4. Weigh</b><br>20 s, assumed<br>farm weight is kept", "t4"),
           ("<b>5. Inspect</b><br>90 s, assumed<br>no criteria invented", "t5"), ("<b>6. Decide and record</b><br>20 s, assumed<br>reception weight, reason code", "t6"),
           ("<b>7. Move the sack</b><br>20 s, assumed<br>stack or return area", "t7")]
    for i, (v, cid) in enumerate(top):
        p.step(v, 50 + i * 230, 110, 190, 80, fill="#F2F8FC", stroke="#147EBA", cid=cid)
        if i:
            p.edge(top[i - 1][1], cid, "", TEL, exit=(1, 0.5), entry=(0, 0.5))
    p.step("<b>Accepted</b><br>received_accepted<br>then dispatched_to_port, groups of 30, 15 s a sack", 1050, 215, 300, 70, fill="#EEF7EE", stroke=TEL, cid="acc")
    p.step("<b>Rejected</b><br>received_rejected<br>then returned_to_farm, same code", 1400, 215, 250, 70, fill="#FDEDEC", stroke=FAIL, cid="rej")
    p.edge("t6", "acc", "accept", TEL, exit=(0.3, 1), entry=(0.5, 0))
    p.edge("t6", "rej", "reject", FAIL, exit=(0.8, 1), entry=(0.5, 0))
    p.note("The five reception steps add up to 165 s for each sack. The dispatch scan of 15 s makes 180 s and belongs to the dispatch station.", 50, 215, 480, 70)
    p.note("A correction before dispatch is an event with a reason code and an observation. The codes stay provisional until the Federation confirms its criteria.", 560, 215, 450, 70)

    p.group("Sack that arrives with no code: four steps, each one can fail alone and none creates a second sack or code", 30, 340, 1640, 270, stroke=OBJ, dashed=True, sw=2)
    nc = [("<b>A. Assign a code</b><br>from the issued block of this device<br>20 s with B", "n1"), ("<b>B. Register</b><br>registered_at_center<br>farm, weight, event_id", "n2"),
          ("<b>C. Print one label</b><br>30 s on the printer<br>never two identical labels", "n3"), ("<b>D. Attach and scan</b><br>40 s<br>scan must match the registered code", "n4")]
    for i, (v, cid) in enumerate(nc):
        p.step(v, 50 + i * 300, 390, 250, 80, fill="#F2F8FC", stroke="#147EBA" if cid != "n3" else OBJ, cid=cid)
        if i:
            p.edge(nc[i - 1][1], cid, "", OBJ, dashed=cid == "n3", exit=(1, 0.5), entry=(0, 0.5))
    p.step("<b>Reception</b><br>steps 3 to 7", 1300, 390, 150, 80, fill="#EEF7EE", stroke=TEL, cid="rcv")
    p.edge("n4", "rcv", "", TEL, exit=(1, 0.5), entry=(0, 0.5))
    fails = ["No code left in the block. Stop, use another device or wait. No code is invented.",
             "Event waits on the device and repeats with the same event_id. A second registration of the code is an anomaly.",
             "No label came out. Print again for the same code, a retry that makes no sack, no code and no reprint record.",
             "Mismatch. Stop the sack, void the label and print again as a reprint with the same code."]
    for i, t in enumerate(fails):
        p.note("<b>If it fails.</b> " + t, 50 + i * 300, 490, 250, 100, fill="#FDEDEC", stroke="#DD344C")
    p.note("<b>Printing rule pending.</b> Address, protocol and port of the printer are not confirmed, so no permission is opened. A receipt, if any, is a separate non-adhesive slip with no QR.", 1300, 490, 350, 100, fill="#FFF8E1", stroke="#D6B656")

    p.group("Work with no internet and reprints", 30, 640, 810, 330, stroke=ALERT, dashed=True, sw=2)
    p.step("<b>Reserve of the center</b><br>10 percent of 400 sacks for 2 days = 80 codes, assumed<br>sized first, issued in advance", 50, 690, 300, 80, fill="#FFF3E0", stroke=ALERT, cid="res")
    p.step("<b>Exclusive blocks</b><br>no overlap, one per device<br>40 + 40, or 27 + 27 + 26", 400, 690, 250, 80, fill="#FFF3E0", stroke=ALERT, cid="blk")
    p.edge("res", "blk", "split", ALERT, exit=(1, 0.5), entry=(0, 0.5))
    p.note("<b>Exhausted.</b> Stop. <b>Lost device.</b> Freeze its codes and never reuse them. <b>Link back.</b> Events arrive, gaps close, a new block is issued, and the 48 h review list fills.", 50, 800, 600, 70, fill="#FFFFFF", stroke=ALERT)
    p.note("<b>Reprint.</b> Same code, reason code, label_reprinted, old label withdrawn or voided when possible. Review from the third reprint is an operating assumption.", 50, 885, 600, 70, fill="#FFFFFF", stroke=ALERT)

    p.group("Capacity at 400 sacks a day, with assumed times to measure in the first harvest", 870, 640, 800, 370, stroke=INK, sw=2)
    p.step("<b>Busiest hour</b><br>150 sacks, 3 times the average of 50<br>9 people cover the hour at 85 percent, in the model<br>4 people complete the day, 63 sacks queue", 890, 690, 360, 90, fill="#F7FAFC", stroke=INK, cid="cap")
    p.step("<b>Bottleneck: inspection</b><br>48 percent of the person time of a sack<br>5 people inspecting in the busiest hour", 1280, 690, 370, 90, fill="#FDEDEC", stroke=FAIL, cid="bot")
    p.note("<b>People set the pace.</b> 2 desktops and 20 phones say nothing about people, scales or inspection pace. With 4 people the backlog is 63 sacks after the busiest hour.", 890, 800, 360, 80)
    p.note("<b>One scale</b> runs at 83 percent in the busiest hour. <b>One printer</b> is busy 19 percent with 10 percent of sacks with no code and 5 percent reprints.", 1280, 800, 370, 80)
    p.legend(890, 895, 360, [(TEL, False, "Normal path"), (FAIL, False, "Rejection or failure"), (OBJ, True, "Step that depends on the pending printing rule")])
    return p


def crop_case():
    p = Page("14 Crop case states", 1800, 800, "Crop case states: from a cultivation alert to a focus confirmed or discarded by a person")
    zones = [("Case opens and the focus is built", 40, 520, "#EAF2F8", "#147EBA"), ("Drone flight, with no connection", 580, 520, "#FEF9E7", "#B7950B"),
             ("Decision of a person", 1120, 640, "#EAF6EC", "#2E7D32")]
    for name, x, w, fill, stroke in zones:
        p.zone(name, x, 70, w, 500, fill, stroke, size=13)
    st = dict(w=170, h=76, size=12)
    p.step("<b>open</b><br>alert or reported<br>symptom", 60, 260, cid="open", **st)
    p.step("<b>focus_ready</b><br>50 m around the node,<br>cut to the lot", 330, 260, cid="focus", **st)
    p.step("<b>location_pending</b><br>no position, lot<br>or flyable area", 60, 110, fill="#FDEDEC", stroke=FAIL, cid="loc", **st)
    p.step("<b>geometry_blocked</b><br>polygon missing<br>or suspended", 60, 420, fill="#FDEDEC", stroke=FAIL, cid="geo", **st)
    p.step("<b>mission_requested</b><br>exact polygon and<br>zone versions", 600, 260, cid="mreq", **st)
    p.step("<b>flight_published</b><br>log and evidence<br>verified", 870, 260, cid="fpub", **st)
    p.step("<b>mission_stale</b><br>package can no longer<br>fly, rebuilt as a new attempt", 600, 420, fill="#FDEDEC", stroke=FAIL, cid="stale", **st)
    p.step("<b>pending_review</b><br>evidence and<br>inference ready", 1140, 260, cid="rev", **st)
    p.step("<b>retry</b><br>inconclusive,<br>evidence kept", 1140, 420, fill="#FDEDEC", stroke=FAIL, cid="retry", **st)
    p.step("<b>confirmed</b><br>a fumigation order<br>may follow", 1440, 190, fill="#E8F5E9", stroke=TEL, cid="conf", **st)
    p.step("<b>discarded</b><br>a later alert<br>opens a new case", 1440, 330, fill="#F2F3F4", stroke=CTRL, cid="disc", **st)
    p.edge("open", "focus", "focus built", TEL)
    p.edge("focus", "mreq", "requested", TEL)
    p.edge("mreq", "fpub", "flight published", TEL)
    p.edge("fpub", "rev", "inference done", TEL)
    p.edge("rev", "conf", "confirmed", TEL, exit=(1, 0.3), entry=(0, 0.5), points=[(1380, 283), (1380, 228)])
    p.edge("rev", "disc", "discarded", CTRL, exit=(1, 0.7), entry=(0, 0.5), points=[(1380, 313), (1380, 368)])
    p.edge("open", "loc", "", FAIL, exit=(0.5, 0), entry=(0.5, 1))
    p.edge("open", "geo", "", FAIL, exit=(0.5, 1), entry=(0.5, 0))
    p.edge("loc", "focus", "supervisor records it", BIZ, exit=(1, 0.5), entry=(0.5, 0), points=[(415, 148)])
    p.edge("geo", "focus", "polygon published", BIZ, exit=(1, 0.5), entry=(0.5, 1), points=[(415, 458)])
    p.edge("mreq", "stale", "", FAIL, exit=(0.5, 1), entry=(0.5, 0))
    p.edge("stale", "focus", "", BIZ, exit=(0, 0.3), entry=(0.735, 1), points=[(455, 443)])
    p.edge("rev", "retry", "", FAIL, exit=(0.5, 1), entry=(0.5, 0))
    p.edge("retry", "focus", "new attempt", BIZ, exit=(0.5, 1), entry=(0.618, 1), points=[(1225, 540), (435, 540)])
    p.text("polygon, focus or window changed", 690, 350, 200, 40, size=11, color=FAIL)
    p.text("reviewer finds it inconclusive", 1230, 350, 150, 40, size=11, color=FAIL)
    p.legend(40, 600, 520, [(TEL, False, "Normal path, conditional write"), (FAIL, False, "Blocked or failed"), (BIZ, False, "Recovery by a person or an event"), (CTRL, False, "Discarded by the reviewer")])
    p.note("<b>Drying alerts</b> only notify the farmer. Guidance ranges and references open no case. One node keeps one open case, and new alerts attach to it.", 580, 600, 560, 70)
    p.note("<b>No fumigation here.</b> A confirmed focus lets a supervisor create an order, which needs its own authorization by a named person.", 1160, 600, 600, 70, fill="#FDEDEC", stroke=FAIL)
    p.note("<b>Events.</b> alert.raised, case.opened, focus.versioned, confirmation.requested, flight.record.published, inference.completed, confirmation.completed.", 580, 686, 1180, 50)
    return p


def alert_delivery():
    p = Page("15 Alert delivery sequence", 1900, 1060, "How an alert reaches the farmer and how each step of its delivery is recorded")
    fn, db, sns, push, phone, api, logs, check = 160, 390, 620, 850, 1080, 1310, 1540, 1770
    top, bottom = 70, 900
    bands = [("Platform side, from the reading to the handoff", 140, 330, "#EAF6EC", "#2E7D32"),
             ("Phone side, when the phone has data", 482, 196, "#EAF2F8", "#147EBA"),
             ("Five minutes after the publish", 690, 210, "#FEF9E7", "#B7950B")]
    for _, y, h, fill, stroke in bands:
        p.zone("", 40, y, 1820, h, fill, stroke)
    p.lifeline("Ingestion function", "Evaluates and raises", fn, top, bottom, icon="lambda", color=COMPUTE)
    p.lifeline("Alerts table", "DynamoDB, delivery record", db, top, bottom, icon="dynamodb", color=DATA)
    p.lifeline("Amazon SNS", "Mobile push", sns, top, bottom, icon="sns", color=APP)
    p.lifeline("Push service", "FCM or Apple, outside AWS", push, top, bottom, net="server")
    p.lifeline("Farmer phone", "Farmer application", phone, top, bottom, net="mobile")
    p.lifeline("Platform API", "Receipt function", api, top, bottom, icon="api_gateway", color=APP)
    p.lifeline("Status logs", "CloudWatch Logs, status function", logs, top, bottom, icon="cloudwatch_2", color=MGMT)
    p.lifeline("Delay queue", "SQS, delivery check function", check, top, bottom, icon="sqs", color=APP)
    for label, y, _, fill, _ in bands:
        p._v(label, f"text;html=1;align=left;verticalAlign=middle;fontSize=14;fontStyle=1;fontColor={INK};fillColor={fill};strokeColor=none;spacingLeft=6;", 50, y + 6, 470, 24)

    p.message(fn, db, 196, "Alert, live or drained", BIZ)
    p.message(fn, sns, 230, "Publish data message, TTL 24 h", ALERT)
    p.message(sns, fn, 264, "Message ID", CTRL, dashed=True)
    p.message(fn, db, 298, "Push ID, publish time", BIZ)
    p.message(fn, check, 332, "Check message, delay 300 s", CTRL)
    p.message(sns, push, 366, "Handoff after the dwell time", ALERT)
    p.message(sns, logs, 400, "Delivery status, dwellTimeMs", CTRL)
    p.message(logs, db, 434, "push_handoff_at, push_status", BIZ)

    p.message(push, phone, 530, "Data message, high priority", ALERT)
    p.note("<b>On the phone.</b> The application shows the notification", 980, 552, 200, 44)
    p.message(phone, api, 616, "POST receipt, time on the phone", CTRL)
    p.message(api, db, 650, "receipt_at, device_received_at", BIZ)

    p.message(check, db, 738, "Read the alert", CTRL)
    p.note("<b>No handoff.</b> Undelivered metric and alarm", 1520, 756, 300, 34)
    p.message(check, phone, 812, "SMS when urgent, active and with no receipt", FAIL)
    p.note("<b>SMS events.</b> End User Messaging writes them to the status logs", 1400, 830, 300, 34)
    p.message(logs, db, 884, "sms_status, sms_status_at", BIZ)

    p.note("<b>No data on the phone.</b> The push waits up to 24 hours at the push service, and the receipt goes with the next call. The objective stops at the handoff", 60, 916, 560, 44)
    p.legend(660, 916, 560, [(ALERT, False, "Alert on its way to the phone"), (BIZ, False, "Write to the delivery record"),
                             (CTRL, False, "Control and confirmation"), (FAIL, False, "SMS fallback for urgent alerts"), (CTRL, True, "Dashed line, an answer to a request")])
    return p


def fumigation_order():
    p = Page("16 Fumigation order states", 2740, 900, "Fumigation order states: from a confirmed focus to a closure that only a person can sign")
    zones = [("Before authorization", 40, 490, "#EAF2F8", "#147EBA", "z1"), ("Authorized, no product applied", 580, 490, "#EAF6EC", "#2E7D32", "z2"),
             ("Application in the field, with no connection", 1120, 490, "#FEF9E7", "#B7950B", "z3"), ("Record, verification and closure", 1660, 1040, "#F4ECF7", "#6A1B9A", "z4")]
    for name, x, w, fill, stroke, cid in zones:
        p.zone(name, x, 190, w, 520, fill, stroke, cid=cid, size=13)
    st = dict(w=170, h=76, size=12)
    red, grey, green = dict(fill="#FDEDEC", stroke=FAIL), dict(fill="#F2F3F4", stroke=CTRL), dict(fill="#E8F5E9", stroke=TEL)
    p.step("<b><font style=\"font-size:10px\">PREREQUISITE_PENDING</font></b><br>order created<br>by a supervisor", 60, 260, cid="pre", **st)
    p.step("<b><font style=\"font-size:10px\">READY_FOR_HUMAN_REVIEW</font></b><br>polygon, log, farmer<br>and permits checked", 320, 260, cid="ready", **st)
    p.step("<b><font style=\"font-size:10px\">AUTHORIZED</font></b><br>named supervisor,<br>second factor", 600, 260, cid="auth", **st)
    p.step("<b><font style=\"font-size:10px\">PACKAGE_PRELOADED</font></b><br>station and drone,<br>or brigade phone", 860, 260, cid="pkg", **st)
    p.step("<b><font style=\"font-size:10px\">EXECUTING</font></b><br>inside the package<br>window", 1140, 260, cid="exec", **st)
    p.step("<b><font style=\"font-size:10px\">EXECUTED_PENDING_SYNC</font></b><br>log closed<br>in the field", 1400, 260, cid="eps", **st)
    p.step("<b><font style=\"font-size:10px\">FLIGHT_RECORD_PERSISTED</font></b><br>record verified,<br>planned product lot", 1720, 260, cid="frp", **st)
    p.step("<b><font style=\"font-size:10px\">VERIFICATION_PENDING</font></b><br>stays open with<br>no verification file", 1980, 260, cid="vp", **st)
    p.step("<b><font style=\"font-size:10px\">VERIFIED</font></b><br>photos evaluated,<br>record written", 2240, 260, cid="ver", **st)
    p.step("<b><font style=\"font-size:10px\">CLOSED</font></b><br>outcome and any<br>follow-up order", 2500, 260, cid="closed", **green, **st)
    p.step("<b><font style=\"font-size:10px\">REJECTED</font></b><br>supervisor or<br>farmer refused", 320, 80, cid="rej", **grey, **st)
    p.step("<b><font style=\"font-size:10px\">CANCELLED</font></b><br>withdrawn<br>before takeoff", 660, 80, cid="can", **grey, **st)
    p.step("<b><font style=\"font-size:10px\">EXPIRED</font></b><br>window ended,<br>no product applied", 900, 80, cid="exp", **grey, **st)
    p.step("<b><font style=\"font-size:10px\">BLOCKED</font></b><br>safety condition<br>failed", 320, 480, cid="blk", **red, **st)
    p.step("<b><font style=\"font-size:10px\">ABORTED</font></b><br>applicator stopped<br>the application", 1140, 480, cid="abo", **red, **st)
    p.step("<b><font style=\"font-size:10px\">PARTIAL</font></b><br>part of the area<br>treated", 1400, 480, cid="par", **red, **st)
    p.step("<b><font style=\"font-size:10px\">SYNC_REVIEW_REQUIRED</font></b><br>failed check or<br>other product lot", 1720, 480, cid="syn", **red, **st)

    p.edge("pre", "ready", "checks pass", TEL)
    p.edge("ready", "auth", "authorizes", BIZ, width=2)
    p.edge("auth", "pkg", "both acks", TEL)
    p.edge("pkg", "exec", "takeoff", BIZ)
    p.edge("exec", "eps", "log closed", BIZ)
    p.edge("eps", "frp", "record published", TEL)
    p.edge("frp", "vp", "planned", TEL)
    p.edge("vp", "ver", "closable result", TEL)
    p.edge("vp", "ver", "reviews after dead letter", BIZ, exit=(0.7, 1), entry=(0.3, 1), points=[(2099, 420), (2291, 420)])
    p.edge("ver", "closed", "closes", BIZ, width=2)

    p.edge("ready", "rej", "refuses", BIZ, exit=(0.5, 0), entry=(0.5, 1))
    p.edge("pre", "rej", "farmer refuses", BIZ, exit=(0.5, 0), entry=(0, 0.5), points=[(145, 118)])
    p.edge("z1", "can", "", BIZ, exit=(0.97, 0), entry=(0, 0.5), points=[(515, 118)])
    p.edge("z2", "can", "cancels", BIZ, exit=(0.3, 0), entry=(0.394, 1))
    p.edge("z2", "exp", "window ends", CTRL, exit=(0.8, 0), entry=(0.424, 1))
    p.edge("ready", "blk", "", FAIL, exit=(0.5, 1), entry=(0.5, 0))
    p.edge("pre", "blk", "", FAIL, exit=(0.7, 1), entry=(0, 0.263), points=[(179, 500)])
    p.edge("auth", "blk", "", FAIL, exit=(0.5, 1), entry=(1, 0.5), points=[(685, 518)])
    p.edge("pkg", "blk", "polygon, permit or package fails", FAIL, exit=(0.5, 1), entry=(1, 0.5), points=[(945, 518)])
    p.edge("blk", "pre", "", BIZ, exit=(0, 0.75), entry=(0.3, 1), points=[(111, 537)])
    p.edge("exec", "abo", "aborts", FAIL, exit=(0.3, 1), entry=(0.3, 0))
    p.edge("abo", "exec", "", BIZ, exit=(0.7, 0), entry=(0.7, 1))
    p.edge("eps", "par", "", FAIL, exit=(0.5, 1), entry=(0.5, 0))
    p.edge("abo", "par", "product applied", FAIL, exit=(1, 0.5), entry=(0, 0.5))
    p.edge("eps", "syn", "", FAIL, exit=(1, 0.8), entry=(0, 0.5), points=[(1650, 321), (1650, 518)])
    p.edge("syn", "frp", "accepted", BIZ, exit=(0.5, 0), entry=(0.5, 1))
    p.edge("syn", "par", "incomplete", BIZ, exit=(0.3, 1), entry=(0.8, 1), points=[(1771, 600), (1536, 600)])
    p.edge("par", "vp", "requests verification", BIZ, exit=(0.3, 1), entry=(0.5, 1), points=[(1451, 660), (2065, 660)])
    p.text("revise", 130, 514, 60, 20, size=11, color=BIZ)
    p.text("retry", 1268, 420, 60, 20, size=11, color=BIZ)

    p.legend(40, 740, 560, [(TEL, False, "Platform function, conditional write"), (BIZ, False, "Person, with the group and second factor checked"),
                            (FAIL, False, "Safety stop or failure"), (CTRL, False, "Scheduler at the end of the window")])
    p.note("<b>Only a supervisor</b> moves an order to AUTHORIZED or CLOSED, and only the supervisor or the farmer to REJECTED. No model, function, event or upload can authorize.", 640, 740, 640, 60, fill="#FDEDEC", stroke=FAIL)
    p.note("<b>Not drawn.</b> READY_FOR_HUMAN_REVIEW expires when its proposed window ends. ABORTED expires when no product left the tank. BLOCKED and EXPIRED can be revised or cancelled, and READY, AUTHORIZED and PACKAGE_PRELOADED can be revised. All 41 moves are in fumigation-order-transitions.json.", 1320, 740, 860, 76)
    p.note("<b>Audit.</b> Every move, allowed or denied, writes one fumigation.transition event to the log archive.", 2220, 740, 480, 60)
    return p


def public_query():
    p = Page("17 Public query", 2000, 860, "How a buyer reads one sack by code, and what limits bulk reads of the public query")
    p.zone("Public internet", 40, 80, 260, 600, "#FDEDEC", FAIL, dashed=True)
    p.card("Buyer phone", "Scans the QR, no sign-in", 60, 150, 220, 64, cid="buyer", net="mobile")
    p.card("Direct caller", "Calls the function URL address", 60, 560, 220, 64, cid="direct", net="pc", stroke=FAIL, dashed=True)

    p.zone("CloudFront edge", 360, 80, 490, 600, "#F4ECF7", NET)
    p.card("AWS WAF web ACL", "300 per address in 5 min, managed rules", 440, 140, 180, 84, cid="waf", icon="waf", color=SEC)
    p.card("Distribution", "Page cached, lookup path not cached", 670, 140, 160, 84, cid="cf", icon="cloudfront", color=NET)

    p.zone("AWS us-east-1, production account", 890, 80, 830, 600, "#EBF5FB", INK)
    p.card("Query page bucket", "S3, read by the distribution only", 950, 140, 210, 84, cid="page", icon="s3", color=STORAGE)
    p.card("Lookup function", "Function URL, IAM auth, 5 reserved copies", 950, 320, 210, 84, cid="fn", icon="lambda", color=COMPUTE)
    p.card("Buyer view table", "buyer_views, GetItem only", 1240, 330, 200, 64, cid="table", icon="dynamodb", color=DATA)
    p.card("Audit log group", "One event per lookup", 1500, 330, 200, 64, cid="audit", icon="cloudwatch_2", color=MGMT)
    p.card("CloudWatch alarms", "Over 1,500 in 5 min, any throttle", 1240, 500, 210, 64, cid="alarm", icon="cloudwatch_2", color=MGMT)

    p.zone("Operations", 1760, 80, 200, 600, "#F2F3F4", CTRL)
    p.card("Platform operator", "Blocks addresses or sets 0 copies", 1775, 500, 170, 64, cid="op", net="pc")

    p.edge("buyer", "waf", "HTTPS, page and lookup", BIZ, exit=(1, 0.5), entry=(0, 0.5), points=[(400, 182)])
    p.edge("waf", "cf", "allowed", BIZ)
    p.edge("cf", "page", "page, signed", OBJ)
    p.edge("cf", "fn", "lookup, signed", BIZ, exit=(0.5, 1), entry=(0, 0.5), points=[(750, 362)])
    p.edge("fn", "table", "GetItem", BIZ, exit=(1, 0.5), entry=(0, 0.5))
    p.edge("fn", "audit", "audit event", BIZ, exit=(0.5, 0), entry=(0.5, 0), points=[(1055, 290), (1600, 290)])
    p.edge("fn", "alarm", "invocations, throttles", CTRL, dashed=True, exit=(0.5, 1), entry=(0, 0.5), points=[(1055, 532)])
    p.edge("alarm", "op", "notify", CTRL, dashed=True)
    p.edge("direct", "fn", "unsigned, refused with 403", FAIL, dashed=True, exit=(1, 0.5), entry=(0.2, 1), points=[(992, 592)])

    p.legend(40, 710, 420, [(BIZ, False, "Lookup of one sack"), (OBJ, False, "Query page, cached at the edge"),
                            (FAIL, True, "Request that never reaches the function"), (CTRL, True, "Alarm and response")])
    p.note("<b>Peak.</b> 30 lookups a minute, 0.5 a second, 0.1 copies running on average. With 5 reserved copies a buyer meets a refusal about once in ten million lookups. The ceiling is 25 a second, about 50 times the peak", 500, 710, 470, 64)
    p.note("<b>Bulk reads.</b> Codes of 60 random bits. A month of guesses at the ceiling finds about 0.0002 valid codes, and each hit shows one buyer view with no personal data", 1000, 710, 460, 64)
    p.note("<b>Response.</b> First a temporary rule blocks the addresses. If they are too many, reserved copies go to 0 and every lookup gets 429. Then back to 5", 1490, 710, 470, 64)
    return p


def center_cloud_link():
    p = Page("18 Center cloud link", 1700, 1080, "How a collection center reaches the cloud: tunnels, routes, names and what happens when the link fails")
    p.group("Collection center", 30, 60, 560, 560, stroke=FAIL, dashed=True, sw=2)
    p.step("<b>Logistics</b><br>10.X.3.0/24<br>stations", 60, 110, 250, 70, fill="#F2F8FC", stroke="#147EBA", cid="log")
    p.step("<b>Local servers</b><br>10.X.10.0/24<br>label printer", 330, 110, 230, 70, fill="#F2F8FC", stroke="#147EBA", cid="srv")
    p.step("<b>Firewall of the center</b><br>IKEv2, static public address, two tunnels<br>routes only to the endpoint subnets of each environment<br>no forwarding between tunnels", 60, 220, 500, 100, fill="#EAF2F8", stroke="#147EBA", cid="fw")
    p.edge("log", "fw", "", CTRL, exit=(0.5, 1), entry=(0.25, 0))
    p.edge("srv", "fw", "", CTRL, exit=(0.5, 1), entry=(0.75, 0))
    p.step("<b>One WAN link</b><br>100 Mbps, shared by both tunnels", 60, 340, 500, 60, fill="#FFF3E0", stroke=ALERT, cid="wan")
    p.edge("fw", "wan", "", CTRL, exit=(0.5, 1), entry=(0.5, 0))
    p.note("Management, Support, Transport, Visitors and the firewall range have no route to the cloud.", 60, 420, 500, 50, fill="#FDEDEC", stroke="#DD344C")
    p.note("<b>DNS.</b> The firewall answers every zone and forwards to two public resolvers. It also holds a local record for the IoT Core data name, with the addresses of the endpoint interfaces.", 60, 490, 500, 80)

    p.step("<b>Tunnel 1</b><br>IPsec, started by AWS", 660, 270, 200, 60, fill="#EEF7EE", stroke=TEL, cid="t1")
    p.step("<b>Tunnel 2</b><br>IPsec, started by AWS", 660, 350, 200, 60, fill="#EEF7EE", stroke=TEL, cid="t2")
    p.edge("fw", "t1", "", TEL, exit=(1, 0.3), entry=(0, 0.5))
    p.edge("fw", "t2", "", TEL, exit=(1, 0.7), entry=(0, 0.5))
    p.note("Both tunnels end on the same firewall and the same WAN. They cover a failure of an AWS tunnel endpoint, and a failure of the WAN or the firewall takes both.", 630, 440, 260, 100, fill="#FFF8E1", stroke="#D6B656")

    p.group("Cloud, one environment, production shown", 920, 60, 750, 560, stroke=INK, sw=2)
    p.step("<b>Virtual private gateway</b><br>one for each environment<br>one connection for each center<br>static routes", 950, 290, 230, 100, fill="#EAF2F8", stroke="#147EBA", cid="vgw")
    p.edge("t1", "vgw", "", TEL, exit=(1, 0.5), entry=(0, 0.3))
    p.edge("t2", "vgw", "", TEL, exit=(1, 0.5), entry=(0, 0.7))
    p.step("<b>rt-private-center</b><br>explicit routes to 10.41.3.0/24, 10.41.10.0/24, 10.42.3.0/24, 10.42.10.0/24, 10.43.3.0/24, 10.43.10.0/24", 1230, 110, 410, 80, fill="#F2F8FC", stroke="#147EBA", cid="rtc")
    p.step("<b>IoT Core data endpoint</b><br>10.70.0.0/24 and 10.70.1.0/24", 1230, 220, 410, 60, fill="#F2F8FC", stroke="#147EBA", cid="iot")
    p.step("<b>S3 interface endpoint</b><br>10.70.16.0/24 and 10.70.17.0/24", 1230, 300, 410, 60, fill="#F2F8FC", stroke="#147EBA", cid="s3")
    p.step("<b>Private REST API endpoint</b><br>10.70.32.0/24 and 10.70.33.0/24", 1230, 380, 410, 60, fill="#F2F8FC", stroke="#147EBA", cid="api")
    p.edge("vgw", "rtc", "routes and return", OBJ, exit=(0.5, 0), entry=(0, 0.5), points=[(1065, 150)])
    p.edge("vgw", "iot", "", OBJ, exit=(1, 0.2), entry=(0, 0.5))
    p.edge("vgw", "s3", "", OBJ, exit=(1, 0.5), entry=(0, 0.5))
    p.edge("vgw", "api", "", OBJ, exit=(1, 0.8), entry=(0, 0.5))
    p.note("<b>rt-private</b> serves data, object storage, administration and public query, and holds no route to a center. Security groups and network ACLs still decide what may pass on the routes above.", 1230, 470, 410, 100, fill="#FDEDEC", stroke="#DD344C")

    p.group("Names from a center, each one read in documentation and not tested", 30, 650, 1640, 190, stroke=OBJ, dashed=True, sw=2)
    p.note("<b>Private REST API.</b> Endpoint-specific name vpce.execute-api, header x-apigw-api-id. Public DNS returns the private addresses. TLS 1.2 or later, security policy TLS_1_2 or access mode BASIC.", 50, 700, 520, 120, fill="#F2F8FC", stroke="#147EBA")
    p.note("<b>S3.</b> Endpoint-specific name bucket.vpce, resolvable from the public S3 domain. TLS 1.2 only. Presigned URLs against that name are not verified. The gateway endpoint cannot be reached from a center.", 590, 700, 520, 120, fill="#F2F8FC", stroke="#147EBA")
    p.note("<b>IoT Core data.</b> No private DNS and no regional or zonal public name, so the firewall holds a local record. Server name required, ATS certificates, port 443 with ALPN or 8883 to be shown. A Resolver costs USD 182.50 a month and is not adopted.", 1130, 700, 520, 120, fill="#FFF8E1", stroke="#D6B656")

    p.group("When the link fails", 30, 870, 1100, 180, stroke=ALERT, dashed=True, sw=2)
    p.note("<b>One tunnel down.</b> Traffic moves to the other. The firewall must stop using the failed one. No recovery time is promised.", 50, 920, 340, 110, fill="#FFFFFF", stroke=ALERT)
    p.note("<b>Both down, WAN or firewall down.</b> Reception goes on, events queue on the devices, calls to the cloud time out. Alarm on TunnelState below 1.", 410, 920, 340, 110, fill="#FFFFFF", stroke=ALERT)
    p.note("<b>Tunnels up, traffic dropped.</b> TunnelState stays at 1. Flow logs and application errors show it.", 770, 920, 340, 110, fill="#FFFFFF", stroke=ALERT)
    p.legend(1160, 870, 510, [(TEL, False, "Tunnel"), (OBJ, False, "Route in the cloud"), (CTRL, False, "Inside the center")])
    p.note("<b>Static routing.</b> BGP is a future alternative with conditions, not a backup of the static routes.", 1160, 990, 510, 50, fill="#FFF8E1", stroke="#D6B656")
    return p


def main():
    pages = [overview(), end_to_end(), cloud_deployment(), connectivity(), pest_flow(), landing_zone(), environments(), farm_sequence(), sack_states(), center_wlan(), drone_link(), audit_path(), lot_geometry(), center_operation(), crop_case(), alert_delivery(), fumigation_order(), public_query(), center_cloud_link()]
    xml = '<mxfile host="app.diagrams.net">' + "".join(p.xml() for p in pages) + "</mxfile>"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(xml, encoding="utf-8")


if __name__ == "__main__":
    main()
