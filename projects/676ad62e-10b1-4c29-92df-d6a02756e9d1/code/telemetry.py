"""Учебен формат за телеметрия. Няма управление на радио или GPIO."""
import struct
import math

FORMAT = "<BBIhIiiiH"
SIZE = struct.calcsize(FORMAT)
GNSS_VALID = 1
PRESSURE_VALID = 2
TEMPERATURE_VALID = 4
BATTERY_VALID = 8


def _number(value, low, high, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(label)
    if not math.isfinite(value) or not low <= value <= high:
        raise ValueError(label)
    return value


def encode(sequence, temperature_c=None, pressure_pa=None,
           position=None, battery_mv=None):
    # Всеки флаг показва дали съответното поле носи валидно измерване.
    if not isinstance(sequence, int) or isinstance(sequence, bool):
        raise ValueError("sequence")
    _number(sequence, 0, 0xffffffff, "sequence")
    flags = temp = pressure = lat = lon = altitude = battery = 0
    if temperature_c is not None:
        temp = round(_number(temperature_c, -100, 100, "temperature") * 100)
        flags |= TEMPERATURE_VALID
    if pressure_pa is not None:
        _number(pressure_pa, 0, 200000, "pressure")
        # BMP581: извън 300...1250 hPa не заявяваме валидна точност.
        if 30000 <= pressure_pa <= 125000:
            pressure = round(pressure_pa)
            flags |= PRESSURE_VALID
    if position is not None:
        # position е (ширина, дължина, височина в метри), само при fix.
        latitude, longitude, height = position
        lat = round(_number(latitude, -90, 90, "latitude") * 10000000)
        lon = round(_number(longitude, -180, 180, "longitude") * 10000000)
        altitude = round(_number(height, -1000, 100000, "altitude") * 100)
        flags |= GNSS_VALID
    if battery_mv is not None:
        battery = round(_number(battery_mv, 1, 65535, "battery"))
        flags |= BATTERY_VALID
    return struct.pack(FORMAT, 1, flags, sequence, temp, pressure,
                       lat, lon, altitude, battery)


def decode(packet):
    if len(packet) != SIZE:
        raise ValueError("packet length")
    version, flags, seq, temp, pressure, lat, lon, height, battery = struct.unpack(FORMAT, packet)
    if version != 1 or flags & ~15:
        raise ValueError("packet version or flags")
    # None е липсващо измерване. То не е нула градуса или нула метра.
    result = {
        "sequence": seq,
        "temperature_c": temp / 100 if flags & TEMPERATURE_VALID else None,
        "pressure_pa": pressure if flags & PRESSURE_VALID else None,
        "position": (lat / 10000000, lon / 10000000, height / 100)
                    if flags & GNSS_VALID else None,
        "battery_mv": battery if flags & BATTERY_VALID else None,
    }
    # Използваме същите граници и за приетите данни, не само за изпратените.
    check = encode(**result)
    if check != packet:
        raise ValueError("inconsistent packet fields")
    return result
