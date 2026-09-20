"""Версия 2 добавя влажност; няма радио, GPIO или сензорен драйвер."""
import struct
import telemetry as v1

HUMIDITY_VALID = 16
SIZE = v1.SIZE + 2


def encode(sequence, temperature_c=None, pressure_pa=None, position=None,
           battery_mv=None, humidity_rh=None):
    # Запазваме полетата от v1, но сменяме версията за старите приемници.
    packet = bytearray(v1.encode(sequence, temperature_c, pressure_pa,
                               position, battery_mv))
    packet[0] = 2
    humidity = 0
    if humidity_rh is not None:
        humidity = round(v1._number(humidity_rh, 0, 100, "humidity") * 100)
        packet[1] |= HUMIDITY_VALID
    return bytes(packet) + struct.pack("<H", humidity)


def decode(packet):
    if len(packet) != SIZE or packet[0] != 2 or packet[1] & ~31:
        raise ValueError("packet length, version or flags")
    # Декодираме общата част чрез същите проверки като v1.
    base = bytearray(packet[:v1.SIZE])
    base[0] = 1
    base[1] &= ~HUMIDITY_VALID
    result = v1.decode(base)
    humidity = struct.unpack("<H", packet[v1.SIZE:])[0]
    result["humidity_rh"] = humidity / 100 if packet[1] & HUMIDITY_VALID else None
    if encode(**result) != packet:
        raise ValueError("inconsistent humidity field")
    return result
