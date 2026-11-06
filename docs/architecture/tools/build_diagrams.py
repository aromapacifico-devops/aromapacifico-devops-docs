"""Builds docs/architecture/diagrams/platform-architecture.drawio with fixed coordinates."""
from pathlib import Path
from xml.sax.saxutils import quoteattr

OUT = Path(__file__).resolve().parent.parent / "diagrams" / "platform-architecture.drawio"

COMPUTE, DATA, STORAGE, NET, SEC, APP, ML, MGMT, IOT = (
    "#ED7100", "#C925D1", "#7AA116", "#8C4FFF", "#DD344C", "#E7157B", "#01A88D", "#E7157B", "#7AA116")
TEL, OBJ, BIZ, CTRL, FAIL = "#2E7D32", "#1565C0", "#6A1B9A", "#616161", "#C62828"
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

    def edge(self, src, dst, label="", color=INK, dashed=False, points=(), exit=None, entry=None, width=1.5):
        style = (f"edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor={color};strokeWidth={width};"
                 f"dashed={1 if dashed else 0};endArrow=block;endFill=1;fontSize=11;fontColor={INK};"
                 f"labelBackgroundColor=#FFFFFF;")
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

    def xml(self):
        return (f'<diagram name={quoteattr(self.name)}><mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" '
                f'guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
                f'pageWidth="{self.w}" pageHeight="{self.h}" background="#FFFFFF"><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
                + "".join(self.cells) + "".join(self.edges) + "</root></mxGraphModel></diagram>")


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
    p.edge("cf", "api", "public API behind WAF, read-only buyer view", BIZ, exit=(0, 0.5), entry=(0.5, 0), points=[(1560, 396), (1560, 310), (816, 310)])

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
    p = Page("02 Cloud deployment", 1860, 1020, "One AWS environment: what the infrastructure code builds, by box")
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
    p.group("Permanent firewall rules", 450, 480, 570, 66, stroke="#DD344C", color="#DD344C", fill="#FFFFFF")
    p.badge("C06", 972, 486)
    p.text("Endpoint security groups allow TCP 443 from 10.41.3.0/24 and 10.41.10.0/24 and deny all else. Visitors have no route.", 460, 504, 500, 38, size=11)
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
    p.group("Platform identities and encryption", 330, 600, 470, 150, stroke="#0B3D91", sw=2)
    p.badge("C05", 750, 606)
    p.aws("KMS keys", 360, 640, "key_management_service", SEC)
    p.aws("Function roles", 460, 640, "identity_and_access_management", SEC)
    p.aws("Pipeline OIDC roles", 570, 640, "identity_and_access_management", SEC)
    p.aws("Secrets Manager", 690, 640, "secrets_manager", SEC)

    p.group("Remote state", 820, 600, 230, 150, stroke="#0B3D91", sw=2)
    p.badge("C02", 1000, 606)
    p.aws("S3 state bucket<br>native lock file", 900, 640, "s3", STORAGE, "state")

    p.group("Reserved for later plans", 1070, 600, 720, 150, stroke="#AEB6BF", color="#5D6D7E", dashed=True)
    p.text("API Gateway, domain functions, Cognito, CloudFront, WAF and the three other inference triggers stay in the architecture and outside the first plan. The Huila and Tolima links reuse the C04 pattern.", 1090, 640, 680, 70, size=12)

    # Outside AWS: repo and pipeline
    p.group("Code and delivery, GitHub", 30, 764, 1790, 136, stroke=INK, sw=2)
    p.group("Infrastructure repository", 50, 796, 240, 96, stroke="#0B3D91", sw=2)
    p.group("Pipeline with approval", 310, 796, 900, 96, stroke="#0B3D91", sw=2)
    p.step("Root, environments<br>and tfvars with no secrets", 66, 824, 208, 58, cid="root")
    p.step("Pull request<br>fmt, validate, scan", 340, 824, 170, 58, cid="pr")
    p.step("Plan on the test<br>environment", 550, 824, 170, 58, cid="plan")
    p.step("Person approves<br>protected environment", 760, 824, 170, 58, cid="ok", stroke=FAIL)
    p.step("Apply<br>OIDC deployment role", 970, 824, 170, 58, cid="apply")
    p.badge("C01", 240, 800)
    p.badge("C09", 1160, 800)
    p.note("Validation evidence stays with each pull request. No production change between 05:00 and 18:00 in a harvest week, except during an incident.", 1240, 804, 560, 80)
    p.edge("root", "pr", "", CTRL)
    p.edge("pr", "plan", "", CTRL)
    p.edge("plan", "ok", "", CTRL)
    p.edge("ok", "apply", "", CTRL)
    p.legend(40, 916, 700, [(TEL, False, "Telemetry"), (OBJ, False, "Center and drone object traffic")])
    p.legend(760, 916, 500, [(FAIL, True, "Failure path"), (CTRL, False, "Delivery flow")])
    p.note("Blue badges C01 to C09 are the boxes the infrastructure code implements. Dashed subnets stay reserved. Each subnet has one /24 per zone inside a /20 block.", 1280, 916, 510, 74)
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
             "<tr><td>Transport</td><td>Internet</td><td>443</td><td>Allow</td></tr>"
             "<tr><td>Management</td><td>Internet</td><td>443</td><td>Allow</td></tr>"
             "<tr><td>Support</td><td>Internet</td><td>443</td><td>Allow</td></tr>"
             "<tr><td>Visitors</td><td>Internet</td><td>80, 443</td><td>Allow</td></tr>"
             "<tr><td>Visitors</td><td>10.X.0.0/16</td><td>Any</td><td>Deny</td></tr>"
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


def main():
    pages = [end_to_end(), cloud_deployment(), connectivity(), pest_flow(), landing_zone()]
    xml = '<mxfile host="app.diagrams.net">' + "".join(p.xml() for p in pages) + "</mxfile>"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(xml, encoding="utf-8")


if __name__ == "__main__":
    main()
