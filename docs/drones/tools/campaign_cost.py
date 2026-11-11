"""Reproducible economic model for the AromaPacifico drone pilot.

All operating and logistics rates are explicit hypothetical planning inputs, not
supplier quotes. AWS rates are public list prices for us-east-1, before tax.
Inference and agrochemical product are deliberately excluded from totals.
"""

from dataclasses import dataclass
from math import ceil

from flight_frequency import (
    BRIGADES,
    CAMPAIGNS_IN_HARVEST,
    DEPARTMENTS,
    FARMS,
    HARVEST_MONTHS,
    HARVEST_MONTH,
    IMAGES_HARVEST_MONTH,
    IMAGES_PER_ESTIMATION,
    OUTSIDE_MONTHS,
    OUTSIDE_SHARE,
    SERVICES,
    outside_campaigns,
    yearly,
)

SERVICE_HOURS = {
    "Delimit the lot": 3.0,
    "Confirm the alert": 1.0,
    "Fumigate": 1.5,
    "Verify": 1.0,
    "Estimate the harvest": 3.5,
}

# The harvest total is fixed at 9,000. Estimation uses 50 * 100 images, so the
# remaining 4,000 images are spread across the 90 precision missions.
PRECISION_IMAGES_PER_MISSION = (
    IMAGES_HARVEST_MONTH
    - FARMS / HARVEST_MONTHS * IMAGES_PER_ESTIMATION
) / sum(HARVEST_MONTH.values())

# Public AWS on-demand rates, us-east-1, before tax. Retrieval: 2026-11-10.
S3_STANDARD_GB_MONTH = 0.023
S3_GLACIER_IR_GB_MONTH = 0.004
S3_PUT_PER_1000 = 0.005
S3_GET_PER_1000 = 0.0004
S3_GLACIER_TRANSITION_PER_1000 = 0.02
LAMBDA_REQUEST_PER_MILLION = 0.20
LAMBDA_GB_SECOND = 0.0000166667
IMAGE_GB = 3 / 1024
STANDARD_MONTHS = 3
RETENTION_MONTHS = 60


@dataclass(frozen=True)
class Scenario:
    name: str
    operator_overhead_year: float
    pilot_hour: float
    brigade_support_hour: float
    equipment_flight_hour: float
    maintenance_mission: float
    insurance_permits_year: float
    vehicle_km: float
    distance_mission_km: float
    per_diem_person_day: float
    people: int
    equipment_transport_mission: float
    campaign_mobilization: float
    extra_visit_share: float
    extra_visit_cost: float
    consumables: dict[str, float]


def _scenario(name, values):
    consumables = dict(zip(SERVICES, values.pop("consumables")))
    return Scenario(name=name, consumables=consumables, **values)


SCENARIOS = {
    "conservative": _scenario("Conservador", {
        "operator_overhead_year": 6000, "pilot_hour": 18,
        "brigade_support_hour": 12, "equipment_flight_hour": 18,
        "maintenance_mission": 8, "insurance_permits_year": 3000,
        "vehicle_km": 0.18, "distance_mission_km": 30,
        "per_diem_person_day": 15, "people": 2,
        "equipment_transport_mission": 5, "campaign_mobilization": 35,
        "extra_visit_share": 0.05, "extra_visit_cost": 35,
        "consumables": [2, 1, 5, 1, 3],
    }),
    "base": _scenario("Base", {
        "operator_overhead_year": 9000, "pilot_hour": 25,
        "brigade_support_hour": 18, "equipment_flight_hour": 28,
        "maintenance_mission": 15, "insurance_permits_year": 4500,
        "vehicle_km": 0.25, "distance_mission_km": 45,
        "per_diem_person_day": 25, "people": 2,
        "equipment_transport_mission": 10, "campaign_mobilization": 60,
        "extra_visit_share": 0.10, "extra_visit_cost": 60,
        "consumables": [3, 2, 8, 2, 4],
    }),
    "high": _scenario("Alto", {
        "operator_overhead_year": 13500, "pilot_hour": 35,
        "brigade_support_hour": 26, "equipment_flight_hour": 42,
        "maintenance_mission": 25, "insurance_permits_year": 7000,
        "vehicle_km": 0.35, "distance_mission_km": 70,
        "per_diem_person_day": 40, "people": 2,
        "equipment_transport_mission": 18, "campaign_mobilization": 100,
        "extra_visit_share": 0.20, "extra_visit_cost": 110,
        "consumables": [5, 3, 12, 3, 6],
    }),
}


def mission_variable_cost(scenario: Scenario, service: str) -> dict[str, float]:
    """Variable cost of one successful mission, including expected revisits."""
    hours = SERVICE_HOURS[service]
    operation = (
        hours * (scenario.pilot_hour + scenario.brigade_support_hour)
        + hours * scenario.equipment_flight_hour
        + scenario.maintenance_mission
        + scenario.consumables[service]
    )
    logistics = (
        scenario.distance_mission_km * scenario.vehicle_km
        + scenario.per_diem_person_day * scenario.people * hours / 8
        + scenario.equipment_transport_mission
        + scenario.extra_visit_share * scenario.extra_visit_cost
    )
    return {"operation": operation, "logistics": logistics,
            "total": operation + logistics}


def image_count_by_service(volumes: dict[str, float]) -> float:
    return (
        (volumes["Delimit the lot"] + volumes["Estimate the harvest"])
        * IMAGES_PER_ESTIMATION
        + (volumes["Confirm the alert"] + volumes["Fumigate"] + volumes["Verify"])
        * PRECISION_IMAGES_PER_MISSION
    )


def monthly_image_volumes(year: int) -> list[float]:
    """Twelve monthly cohorts; year one includes the two-month start-up round."""
    outside_alerts = sum(round(n * OUTSIDE_SHARE) for n in HARVEST_MONTH.values())
    outside_alert_images = outside_alerts * PRECISION_IMAGES_PER_MISSION
    if year == 1:
        start = outside_alert_images + FARMS / 2 * IMAGES_PER_ESTIMATION
        return [start, start] + [IMAGES_HARVEST_MONTH] * HARVEST_MONTHS + [outside_alert_images] * 6
    redelim_images = FARMS * 0.10 * IMAGES_PER_ESTIMATION / OUTSIDE_MONTHS
    return [IMAGES_HARVEST_MONTH] * HARVEST_MONTHS + [outside_alert_images + redelim_images] * OUTSIDE_MONTHS


def technology_cost_for_calendar_year(year: int) -> dict[str, float]:
    """Gross cloud cost in calendar year 1..5, with cohorts and lifecycle."""
    if not 1 <= year <= 5:
        raise ValueError("year must be from 1 to 5")
    cohorts: list[tuple[int, float]] = []
    storage = requests = processing = orthomosaic = 0.0
    month_number = 0
    for y in range(1, year + 1):
        for images in monthly_image_volumes(y):
            month_number += 1
            cohorts.append((month_number, images))
            if y == year:
                requests += images / 1000 * (S3_PUT_PER_1000 + S3_GET_PER_1000)
                # One 1-second, 512-MB verification invocation per image.
                processing += images * (
                    0.5 * LAMBDA_GB_SECOND + LAMBDA_REQUEST_PER_MILLION / 1_000_000
                )
            for born, cohort_images in cohorts:
                if y != year:
                    continue
                age = month_number - born
                if age >= RETENTION_MONTHS:
                    continue
                gb = cohort_images * IMAGE_GB
                storage += gb * (
                    S3_STANDARD_GB_MONTH if age < STANDARD_MONTHS
                    else S3_GLACIER_IR_GB_MONTH
                )
                if age == STANDARD_MONTHS:
                    requests += cohort_images / 1000 * S3_GLACIER_TRANSITION_PER_1000
        if y == year:
            # Orthomosaic: 5 minutes at 4 GB for each estimation mission.
            orthomosaic = yearly(y)["Estimate the harvest"] * 1200 * LAMBDA_GB_SECOND
    return {
        "storage": storage,
        "requests": requests,
        "evidence_processing": processing + orthomosaic,
        "total": storage + requests + processing + orthomosaic,
    }


def annual_cost(scenario: Scenario, year: int, mission_multiplier: float = 1.0) -> dict:
    volumes = {k: v * mission_multiplier for k, v in yearly(year).items()}
    variable_by_service = {
        service: mission_variable_cost(scenario, service)["total"] * volumes[service]
        for service in SERVICES
    }
    campaigns = (CAMPAIGNS_IN_HARVEST + outside_campaigns()) * DEPARTMENTS
    if year == 1:
        campaigns += DEPARTMENTS  # one start-up round per department
    campaign_logistics = campaigns * scenario.campaign_mobilization
    fixed = scenario.operator_overhead_year + scenario.insurance_permits_year
    technology = technology_cost_for_calendar_year(min(year, 5))
    subtotal = sum(variable_by_service.values()) + campaign_logistics + fixed + technology["total"]
    return {
        "year": year, "volumes": volumes, "missions": sum(volumes.values()),
        "variable_by_service": variable_by_service,
        "campaigns": campaigns, "campaign_logistics": campaign_logistics,
        "fixed": fixed, "technology": technology, "total": subtotal,
        "per_farm": subtotal / FARMS, "per_department": subtotal / DEPARTMENTS,
    }


def period_cost(scenario: Scenario, period: str, year: int = 2) -> dict:
    """Average whole-pilot month; campaign fixed cost is frequency-weighted."""
    if period == "startup":
        if year != 1:
            raise ValueError("startup exists only in year 1")
        volumes = {s: round(n * OUTSIDE_SHARE) for s, n in HARVEST_MONTH.items()}
        volumes["Estimate the harvest"] = 0
        volumes["Delimit the lot"] = FARMS / 2
        # The three two-month start-up rounds add 1.5 equivalents per month;
        # ordinary outside-harvest campaigns still average 0.75 per month.
        campaign_equivalents = (
            DEPARTMENTS / 2 + DEPARTMENTS * outside_campaigns() / OUTSIDE_MONTHS
        )
    elif period == "harvest":
        volumes = {"Delimit the lot": 0, "Estimate the harvest": FARMS / HARVEST_MONTHS,
                   **HARVEST_MONTH}
        campaign_equivalents = DEPARTMENTS
    elif period == "outside":
        volumes = {s: round(n * OUTSIDE_SHARE) for s, n in HARVEST_MONTH.items()}
        volumes["Estimate the harvest"] = 0
        volumes["Delimit the lot"] = 0 if year == 1 else FARMS * 0.10 / OUTSIDE_MONTHS
        campaign_equivalents = DEPARTMENTS * outside_campaigns() / OUTSIDE_MONTHS
    else:
        raise ValueError("period must be startup, harvest or outside")
    variable = sum(mission_variable_cost(scenario, s)["total"] * volumes[s] for s in SERVICES)
    annual = annual_cost(scenario, year)
    fixed_month = annual["fixed"] / 12
    tech_month = annual["technology"]["total"] / 12
    total = variable + campaign_equivalents * scenario.campaign_mobilization + fixed_month + tech_month
    return {"volumes": volumes, "missions": sum(volumes.values()), "total": total,
            "per_farm": total / FARMS}


def fully_loaded_mission_cost(scenario: Scenario, service: str, year: int = 2) -> float:
    annual = annual_cost(scenario, year)
    shared = (annual["fixed"] + annual["campaign_logistics"] + annual["technology"]["total"]) / annual["missions"]
    return mission_variable_cost(scenario, service)["total"] + shared


def main():
    print("Scenario totals (USD before tax; inference and agrochemical excluded)")
    print("| Scenario | First year | Following year | Per farm, first year |")
    print("|---|---:|---:|---:|")
    for scenario in SCENARIOS.values():
        y1, y2 = annual_cost(scenario, 1), annual_cost(scenario, 2)
        print(f"| {scenario.name} | {y1['total']:.2f} | {y2['total']:.2f} | {y1['per_farm']:.2f} |")
    print("\nBase fully loaded mission cost, following year")
    for service in SERVICES:
        variable = mission_variable_cost(SCENARIOS["base"], service)["total"]
        loaded = fully_loaded_mission_cost(SCENARIOS["base"], service)
        print(f"| {service} | {variable:.2f} | {loaded:.2f} |")
    print("\nBase periods")
    for period, year in (("startup", 1), ("harvest", 2), ("outside", 2)):
        result = period_cost(SCENARIOS["base"], period, year)
        print(f"| {period} | {result['missions']:.1f} | {result['total']:.2f} | {result['per_farm']:.2f} |")
    print("\nBase sensitivity, following year")
    for multiplier in (0.75, 1.0, 1.25, 1.5):
        result = annual_cost(SCENARIOS["base"], 2, multiplier)
        print(f"| {multiplier:.2f} | {result['missions']:.0f} | {result['total']:.2f} |")


if __name__ == "__main__":
    main()
