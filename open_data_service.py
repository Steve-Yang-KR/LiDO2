"""Open-data adapter for the LiDO2 location-based environmental twin."""

from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass
from datetime import date, timedelta
from threading import Lock
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen


OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
OPEN_METEO_MODEL = "era5_land"
OPEN_METEO_MODEL_LABEL = "ERA5-Land"
LIDO_LATITUDE = 46.3827
LIDO_LONGITUDE = 11.2881
MAX_RANGE_DAYS = 31
CACHE_TTL_SECONDS = 900
MAX_GRID_OFFSET_DEGREES = 0.15

HOURLY_VARIABLES = (
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "shortwave_radiation",
    "soil_temperature_0_to_7cm",
    "soil_moisture_0_to_7cm",
    "et0_fao_evapotranspiration",
    "wind_speed_10m",
)


class OpenDataError(RuntimeError):
    """Raised when the upstream open-data service cannot be used."""


@dataclass
class CacheEntry:
    expires_at: float
    payload: dict[str, Any]


_cache: dict[str, CacheEntry] = {}
_cache_lock = Lock()


def _mean(values: list[float | None]) -> float | None:
    valid = [float(value) for value in values if value is not None and math.isfinite(float(value))]
    return sum(valid) / len(valid) if valid else None


def _sum(values: list[float | None]) -> float:
    return sum(float(value) for value in values if value is not None and math.isfinite(float(value)))


def calculate_vpd(temperature_c: float, relative_humidity: float) -> float:
    """Calculate vapour-pressure deficit in kPa."""
    saturation = 0.6108 * math.exp((17.27 * temperature_c) / (temperature_c + 237.3))
    return max(0.0, saturation * (1 - relative_humidity / 100))


def _default_dates(days: int) -> tuple[date, date]:
    # ERA5-Land reanalysis normally trails real time; use a stable five-day lag.
    end = date.today() - timedelta(days=5)
    return end - timedelta(days=days - 1), end


def _validate_dates(start_date: date, end_date: date) -> None:
    if start_date > end_date:
        raise ValueError("start_date must be on or before end_date")
    if (end_date - start_date).days + 1 > MAX_RANGE_DAYS:
        raise ValueError(f"date range cannot exceed {MAX_RANGE_DAYS} days")
    if end_date > date.today() - timedelta(days=5):
        raise ValueError("ERA5-Land proxy data must end at least five days before today")


def _fetch_json(url: str, timeout: float = 15) -> dict[str, Any]:
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "LiDO2/2.4"})
    try:
        with urlopen(request, timeout=timeout) as response:  # noqa: S310 - fixed HTTPS endpoint
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:  # pragma: no cover - exercised through mocked failure
        raise OpenDataError(f"Open-Meteo request failed: {exc}") from exc


def _validate_response_metadata(raw: dict[str, Any]) -> dict[str, Any]:
    """Validate Open-Meteo metadata before treating the payload as ERA5-Land."""
    try:
        response_latitude = float(raw["latitude"])
        response_longitude = float(raw["longitude"])
    except (KeyError, TypeError, ValueError) as exc:
        raise OpenDataError("Open-Meteo response is missing valid latitude/longitude metadata") from exc

    if abs(response_latitude - LIDO_LATITUDE) > MAX_GRID_OFFSET_DEGREES:
        raise OpenDataError("Open-Meteo response latitude is outside the expected ERA5-Land grid area")
    if abs(response_longitude - LIDO_LONGITUDE) > MAX_GRID_OFFSET_DEGREES:
        raise OpenDataError("Open-Meteo response longitude is outside the expected ERA5-Land grid area")

    timezone = raw.get("timezone")
    if timezone != "Europe/Rome":
        raise OpenDataError(f"Unexpected Open-Meteo timezone: {timezone!r}")

    hourly = raw.get("hourly")
    hourly_units = raw.get("hourly_units")
    if not isinstance(hourly, dict) or not isinstance(hourly_units, dict):
        raise OpenDataError("Open-Meteo response is missing hourly data or unit metadata")

    required_columns = ("time", *HOURLY_VARIABLES)
    missing_columns = [name for name in required_columns if name not in hourly]
    missing_units = [name for name in required_columns if name not in hourly_units]
    if missing_columns or missing_units:
        details = []
        if missing_columns:
            details.append(f"columns={','.join(missing_columns)}")
        if missing_units:
            details.append(f"units={','.join(missing_units)}")
        raise OpenDataError("Open-Meteo response metadata validation failed: " + "; ".join(details))

    return {
        "provider": "Open-Meteo",
        "endpoint": OPEN_METEO_ARCHIVE_URL,
        "requestedModel": OPEN_METEO_MODEL,
        "modelLabel": OPEN_METEO_MODEL_LABEL,
        "modelPinned": True,
        "responseMetadataValidated": True,
        "responseGrid": {
            "latitude": response_latitude,
            "longitude": response_longitude,
            "elevation": raw.get("elevation"),
        },
        "timezone": timezone,
        "utcOffsetSeconds": raw.get("utc_offset_seconds"),
        "hourlyUnits": {name: hourly_units[name] for name in required_columns},
    }


def _normalize(raw: dict[str, Any], start_date: date, end_date: date) -> dict[str, Any]:
    provenance = _validate_response_metadata(raw)
    hourly = raw.get("hourly") or {}
    timestamps = hourly.get("time") or []
    if not timestamps:
        raise OpenDataError("Open-Meteo returned no hourly observations")

    size = len(timestamps)
    columns: dict[str, list[float | None]] = {}
    for variable in HOURLY_VARIABLES:
        values = list(hourly.get(variable) or [])
        if len(values) != size:
            values = (values + [None] * size)[:size]
        columns[variable] = values

    series: list[dict[str, Any]] = []
    vpds: list[float] = []
    for index, timestamp in enumerate(timestamps):
        temperature = columns["temperature_2m"][index]
        humidity = columns["relative_humidity_2m"][index]
        vpd = calculate_vpd(float(temperature), float(humidity)) if temperature is not None and humidity is not None else None
        if vpd is not None:
            vpds.append(vpd)
        series.append(
            {
                "time": timestamp,
                "temperature": temperature,
                "humidity": humidity,
                "precipitation": columns["precipitation"][index],
                "solarRadiation": columns["shortwave_radiation"][index],
                "soilTemperature": columns["soil_temperature_0_to_7cm"][index],
                "soilMoisture": columns["soil_moisture_0_to_7cm"][index],
                "et0": columns["et0_fao_evapotranspiration"][index],
                "windSpeed": columns["wind_speed_10m"][index],
                "vpd": round(vpd, 3) if vpd is not None else None,
            }
        )

    mean_temperature = _mean(columns["temperature_2m"])
    mean_soil_moisture = _mean(columns["soil_moisture_0_to_7cm"])
    mean_vpd = _mean(vpds)
    growing_degree_days = 0.0
    daily_temperatures: dict[str, list[float]] = {}
    for row in series:
        if row["temperature"] is not None:
            daily_temperatures.setdefault(row["time"][:10], []).append(float(row["temperature"]))
    for values in daily_temperatures.values():
        growing_degree_days += max(0.0, sum(values) / len(values) - 10.0)

    soil_percent = (mean_soil_moisture or 0) * 100
    stress_index = min(100.0, max(0.0, (25 - soil_percent) * 2.4 + max(0.0, (mean_vpd or 0) - 1.2) * 28))
    summary = {
        "temperature": round(mean_temperature, 2) if mean_temperature is not None else None,
        "humidity": round(_mean(columns["relative_humidity_2m"]) or 0, 2),
        "precipitation": round(_sum(columns["precipitation"]), 2),
        "solarRadiation": round(_mean(columns["shortwave_radiation"]) or 0, 2),
        "soilTemperature": round(_mean(columns["soil_temperature_0_to_7cm"]) or 0, 2),
        "soilMoisture": round(soil_percent, 2),
        "et0": round(_sum(columns["et0_fao_evapotranspiration"]), 2),
        "windSpeed": round(_mean(columns["wind_speed_10m"]) or 0, 2),
        "vpd": round(mean_vpd or 0, 3),
        "growingDegreeDays": round(growing_degree_days, 2),
        "waterStressIndex": round(stress_index, 1),
    }
    return {
        "source": "Open-Meteo / ERA5-Land",
        "provenance": provenance,
        "dataType": "Reanalysis / model estimate",
        "validationStatus": "Proxy data — not validated against LiDO sensors",
        "location": {
            "name": "LiDO field-lab area, Laimburg Research Centre",
            "latitude": LIDO_LATITUDE,
            "longitude": LIDO_LONGITUDE,
            "timezone": provenance["timezone"],
        },
        "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "summary": summary,
        "series": series,
        "model": "ERA5-Land via Open-Meteo Historical Weather API",
    }


def get_environmental_data(
    start_date: date | None = None,
    end_date: date | None = None,
    days: int = 7,
    fetcher: Any = _fetch_json,
) -> dict[str, Any]:
    """Fetch and normalize environmental proxy data for the LiDO field-lab area."""
    if not 1 <= days <= MAX_RANGE_DAYS:
        raise ValueError(f"days must be between 1 and {MAX_RANGE_DAYS}")
    if start_date is None and end_date is None:
        start_date, end_date = _default_dates(days)
    elif start_date is None or end_date is None:
        raise ValueError("start_date and end_date must be supplied together")
    assert start_date is not None and end_date is not None
    _validate_dates(start_date, end_date)

    key = f"{start_date}:{end_date}"
    now = time.monotonic()
    with _cache_lock:
        cached = _cache.get(key)
        if cached and cached.expires_at > now:
            result = dict(cached.payload)
            result["cacheStatus"] = "hit"
            return result

    query = urlencode(
        {
            "latitude": LIDO_LATITUDE,
            "longitude": LIDO_LONGITUDE,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "hourly": ",".join(HOURLY_VARIABLES),
            "timezone": "Europe/Rome",
            "models": OPEN_METEO_MODEL,
        }
    )
    result = _normalize(fetcher(f"{OPEN_METEO_ARCHIVE_URL}?{query}"), start_date, end_date)
    result["retrievedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    result["cacheStatus"] = "miss"
    with _cache_lock:
        _cache[key] = CacheEntry(now + CACHE_TTL_SECONDS, result)
    return result

