"""Validated scenario models and deterministic LiDO2 evaluation logic."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


def to_camel(value: str) -> str:
    """Convert snake_case model fields to the camelCase used by the frontend."""
    first, *rest = value.split("_")
    return first + "".join(part.capitalize() for part in rest)


class ApiModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid",
    )


class ScenarioInput(ApiModel):
    """Field-to-market inputs accepted by the scenario engine."""

    crop: Literal["apple", "vineyard"] = "apple"

    temperature: float = Field(0, ge=-5, le=10)
    rain: float = Field(20, ge=0, le=100)
    humidity: float = Field(65, ge=30, le=100)
    vpd: float = Field(1.2, ge=0, le=4)
    solar: float = Field(100, ge=40, le=130)
    wind: float = Field(3, ge=0, le=15)

    soil: float = Field(28, ge=10, le=50)
    irrigation: float = Field(18, ge=0, le=40)
    ec: float = Field(0.8, ge=0, le=3)
    drainage: float = Field(75, ge=0, le=100)
    water_cost: float = Field(100, ge=50, le=150)

    phenology: float = Field(78, ge=0, le=100)
    stress: float = Field(20, ge=0, le=100)
    canopy: float = Field(72, ge=30, le=100)
    crop_load: float = Field(100, ge=50, le=140)
    maturity: float = Field(82, ge=40, le=110)
    disease: float = Field(18, ge=0, le=100)
    pollen_tube: float = Field(0, ge=0, le=100)

    labor: float = Field(90, ge=40, le=120)
    spray: float = Field(82, ge=20, le=100)
    harvest_delay: float = Field(6, ge=0, le=72)
    handling: float = Field(92, ge=40, le=100)
    cooling: float = Field(6, ge=0, le=48)

    cold: float = Field(94, ge=20, le=100)
    lead: float = Field(7, ge=1, le=30)
    shelf: float = Field(4, ge=1, le=20)
    pack: float = Field(88, ge=40, le=100)
    claims: float = Field(12, ge=0, le=100)

    price: float = Field(100, ge=60, le=140)
    energy: float = Field(100, ge=50, le=150)
    carbon: float = Field(100, ge=50, le=150)
    biodiversity: float = Field(68, ge=20, le=100)
    waste_target: float = Field(20, ge=0, le=50)


class ScenarioResult(ApiModel):
    """Decision outputs returned to the Scenario Lab."""

    quality: float
    yield_index: float
    water_efficiency: float
    waste_score: float
    waste_risk: Literal["Low", "Medium", "High"]
    value_index: float
    confidence: float
    dominant_drivers: list[str]
    engine_version: str = "python-rules-v1"
    data_source: str = "scenario"


def evaluate_scenario(scenario: ScenarioInput) -> ScenarioResult:
    """Evaluate one scenario using the prototype's transparent rule set."""
    climate = (
        abs(scenario.temperature) * 1.3
        + max(0, scenario.vpd - 1.2) * 7
        + max(0, scenario.humidity - 80) * 0.25
    )
    water = max(0, 28 - scenario.soil) * 1.1 + max(0, 18 - scenario.irrigation) * 0.7
    biology = (
        scenario.stress * 0.18
        + scenario.disease * 0.22
        + abs(scenario.crop_load - 100) * 0.08
    )
    operations = (
        scenario.harvest_delay * 0.18
        + scenario.cooling * 0.35
        + (100 - scenario.handling) * 0.22
        + (100 - scenario.cold) * 0.25
    )
    chain = scenario.lead * 0.28 + scenario.shelf * 0.35 + scenario.claims * 0.08

    quality = max(
        35,
        96 - climate - water - biology - operations - chain * 0.35 + scenario.pack * 0.04,
    )
    yield_index = max(
        40,
        104
        - climate * 0.45
        - water * 0.7
        - biology * 0.5
        - max(0, 100 - scenario.labor) * 0.2,
    )
    water_efficiency = max(
        30,
        96
        - abs(scenario.irrigation - 18) * 1.2
        - max(0, scenario.vpd - 1.5) * 5
        + (scenario.drainage - 75) * 0.08,
    )
    waste_score = max(2, 100 - quality + scenario.cooling * 0.25 + scenario.lead * 0.25)
    value_index = max(
        30,
        quality * 0.55
        + yield_index * 0.35
        + scenario.price * 0.1
        - max(0, scenario.energy - 100) * 0.08,
    )
    confidence = max(
        0.42,
        min(
            0.94,
            0.82
            - (scenario.disease + scenario.stress) * 0.0015
            - abs(scenario.temperature) * 0.006,
        ),
    )

    driver_scores = {
        "climate": climate,
        "water": water,
        "plant physiology": biology,
        "field operations": operations,
        "value chain": chain,
    }
    dominant_drivers = [
        name for name, score in sorted(driver_scores.items(), key=lambda item: item[1], reverse=True)[:3]
    ]
    waste_risk: Literal["Low", "Medium", "High"] = (
        "Low" if waste_score < 18 else "Medium" if waste_score < 35 else "High"
    )

    return ScenarioResult(
        quality=quality,
        yield_index=yield_index,
        water_efficiency=water_efficiency,
        waste_score=waste_score,
        waste_risk=waste_risk,
        value_index=value_index,
        confidence=confidence,
        dominant_drivers=dominant_drivers,
    )
