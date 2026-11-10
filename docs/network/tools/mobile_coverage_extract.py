"""Summarizes the public Postdata mobile datasets for Cauca, Huila and Tolima.

Usage
    python mobile_coverage_extract.py INFRASTRUCTURE_CSV COVERAGE_CSV OUTPUT_CSV

INFRASTRUCTURE_CSV is F3_RES175_2.csv, the number of base station sites by municipality, operator and technology.
COVERAGE_CSV is Datos_Cobertura_Movil_1T_2023-4T_2025.csv, the area covered by operator, technology and signal level
inside each populated center (the municipal seat and the other centros poblados).
Both files are downloaded from https://www.postdata.gov.co and are read as delivered.
"""
import csv
import sys
from collections import defaultdict

DEPARTMENTS = {"19": "Cauca", "41": "Huila", "73": "Tolima"}
OPERATORS = {
    "COMUNICACION CELULAR S A COMCEL S A": "Claro",
    "COLOMBIA TELECOMUNICACIONES S.A. E.S.P.": "Movistar",
    "COLOMBIA MOVIL  S.A ESP": "Tigo",
    "PARTNERS TELECOM COLOMBIA SAS": "WOM",
}
COVERAGE_COLUMNS = {"Claro": "AREA_COB_CLARO", "Movistar": "AREA_COB_MOVISTAR", "Tigo": "AREA_COB_TIGO", "WOM": "AREA_COB_WOM"}
TECHS = ["2G", "3G", "4G", "5G"]


def number(text):
    return float(text.replace(",", ".")) if text else 0.0


def read(path):
    with open(path, encoding="utf-8-sig", newline="") as handle:
        yield from csv.DictReader(handle, delimiter=";")


def infrastructure(path, quarter):
    """Sites with each technology, by department and operator, for one quarter."""
    sites = defaultdict(lambda: defaultdict(int))
    municipalities = defaultdict(set)
    seen_quarters = set()
    for row in read(path):
        seen_quarters.add((row["ANNO"], row["TRIMESTRE"]))
        if (row["ANNO"], row["TRIMESTRE"]) != quarter:
            continue
        department = row["CODIGO_DANE_MUNICIPIO"].zfill(5)[:2]
        if department not in DEPARTMENTS or row["DESC_EMPRESA"] not in OPERATORS:
            continue
        key = (DEPARTMENTS[department], OPERATORS[row["DESC_EMPRESA"]])
        count = int(row["SITIOS"])
        sites[key]["total"] += count
        for tech in TECHS:
            if row[f"TECNOLOGIA_ESTACION_BASE_{tech}"] == "1":
                sites[key][tech] += count
                municipalities[(key, tech)].add(row["CODIGO_DANE_MUNICIPIO"])
        municipalities[(key, "total")].add(row["CODIGO_DANE_MUNICIPIO"])
    return sites, municipalities, sorted(seen_quarters)


def coverage(path, quarter):
    """Covered area by operator and technology inside populated centers, by department."""
    area = defaultdict(float)
    covered = defaultdict(float)
    centers = defaultdict(set)
    centers_covered = defaultdict(set)
    municipal_rows = defaultdict(lambda: defaultdict(float))
    seen_quarters = set()
    counted = set()
    for row in read(path):
        seen_quarters.add((row["ANNO"], row["TRIMESTRE"]))
        if (row["ANNO"], row["TRIMESTRE"]) != quarter or row["ID_DEPARTAMENTO"] not in DEPARTMENTS:
            continue
        tech = row["TECNOLOGIA"]
        if tech not in TECHS:
            continue
        department = DEPARTMENTS[row["ID_DEPARTAMENTO"]]
        center = row["ID_CPOB"]
        seat = "seat" if center.endswith("000") else "other"
        for operator, column in COVERAGE_COLUMNS.items():
            key = (department, operator, tech, seat)
            if (center, tech, operator) not in counted:
                counted.add((center, tech, operator))
                area[key] += number(row["AREA_CPOB"])
                centers[key].add(center)
            value = number(row[column])
            covered[key] += value
            if value > 0:
                centers_covered[key].add(center)
            municipal_rows[(department, row["MUNICIPIO"], row["ID_MUNICIPIO"], operator, tech, seat)]["covered"] += value
            if (center, tech, operator, "m") not in counted:
                counted.add((center, tech, operator, "m"))
                municipal_rows[(department, row["MUNICIPIO"], row["ID_MUNICIPIO"], operator, tech, seat)]["area"] += number(row["AREA_CPOB"])
    return area, covered, centers, centers_covered, municipal_rows, sorted(seen_quarters)


def main():
    infra_path, cover_path, out_path = sys.argv[1:4]
    _, _, infra_quarters = infrastructure(infra_path, ("0", "0"))
    infra_latest = infra_quarters[-1]
    cover_quarters = coverage(cover_path, ("0", "0"))[-1]
    cover_latest = cover_quarters[-1]
    print(f"infrastructure quarters {infra_quarters[0]} to {infra_latest}")
    print(f"coverage quarters {cover_quarters[0]} to {cover_latest}")

    compare = [(str(int(infra_latest[0]) - 1), infra_latest[1]), infra_latest]
    print("\n## Sites by department, operator and technology")
    print("| Department | Operator | Quarter | Sites | with 2G | with 3G | with 4G | with 5G | Municipalities with a site |")
    print("|---|---|---|---|---|---|---|---|---|")
    for quarter in compare:
        sites, municipalities, _ = infrastructure(infra_path, quarter)
        for department in DEPARTMENTS.values():
            for operator in OPERATORS.values():
                key = (department, operator)
                s = sites.get(key)
                if not s:
                    print(f"| {department} | {operator} | {quarter[0]} Q{quarter[1]} | 0 | 0 | 0 | 0 | 0 | 0 |")
                    continue
                print(f"| {department} | {operator} | {quarter[0]} Q{quarter[1]} | {s['total']} | {s['2G']} | {s['3G']} | {s['4G']} | {s['5G']} | {len(municipalities[(key, 'total')])} |")

    area, covered, centers, centers_covered, municipal_rows, _ = coverage(cover_path, cover_latest)
    print(f"\n## Coverage in populated centers, {cover_latest[0]} Q{cover_latest[1]}")
    print("| Department | Operator | Technology | Municipal seats with coverage | Other populated centers with coverage | Area covered in seats, percent | Area covered in other centers, percent |")
    print("|---|---|---|---|---|---|---|")
    for department in DEPARTMENTS.values():
        for operator in OPERATORS.values():
            for tech in TECHS:
                seat = (department, operator, tech, "seat")
                other = (department, operator, tech, "other")

                def share(key):
                    return f"{100 * covered[key] / area[key]:.1f}" if area[key] else "n/a"

                print(f"| {department} | {operator} | {tech} | {len(centers_covered[seat])} of {len(centers[seat])} | {len(centers_covered[other])} of {len(centers[other])} | {share(seat)} | {share(other)} |")

    with open(out_path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["department", "municipality", "dane_code", "operator", "technology", "center_type", "center_area", "covered_area", "period"])
        for (department, municipality, code, operator, tech, seat), values in sorted(municipal_rows.items()):
            writer.writerow([department, municipality, code, operator, tech, "municipal seat" if seat == "seat" else "other populated centers",
                             f"{values['area']:.4f}", f"{values['covered']:.4f}", f"{cover_latest[0]} Q{cover_latest[1]}"])


main()
