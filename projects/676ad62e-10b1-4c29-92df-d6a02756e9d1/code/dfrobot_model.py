"""Модел на декодирани SEN0667/SEN0385/TEL0157 данни, не I2C/UART драйвер."""
import math
from telemetry_v2 import encode

# Наш праг за примерен цикъл 1 Hz, а не характеристика на сензорите.
MAX_AGE_MS = 3000


def _number(value, low, high):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and low <= value <= high)


def _fresh(reading):
    return (isinstance(reading, dict) and reading.get("ok") is True
            and _number(reading.get("age_ms"), 0, MAX_AGE_MS))


def _field(reading, key, low, high):
    value = reading.get(key)
    return value if _number(value, low, high) else None


def make_packet(sequence, barometer=None, environment=None, gnss=None,
                battery_mv=None):
    pressure = temperature = humidity = position = None
    if _fresh(barometer):
        # Консервативна начална температурна област от таблицата на модула.
        # Това е температурата на барометъра, не тази на околния въздух.
        if _field(barometer, "temperature_c", 0, 65) is not None:
            pressure = _field(barometer, "pressure_pa", 30000, 125000)
    if _fresh(environment) and environment.get("crc_ok") is True:
        temperature = _field(environment, "temperature_c", -40, 80)
        humidity = _field(environment, "humidity_rh", 0, 100)
    if (_fresh(gnss) and gnss.get("fix_valid") is True
            and gnss.get("altitude_valid") is True):
        latitude = _field(gnss, "latitude_deg", -90, 90)
        longitude = _field(gnss, "longitude_deg", -180, 180)
        height = _field(gnss, "altitude_m", -1000, 100000)
        # Числовите граници са на формата, не обещан диапазон на TEL0157.
        if latitude is not None and longitude is not None and height is not None:
            position = (latitude, longitude, height)
    battery = battery_mv if _number(battery_mv, 1, 65535) else None
    return encode(sequence, temperature, pressure, position, battery, humidity)
