"""Синтетични DFRobot показания; не комуникира с датчици или радио."""
from dfrobot_model import make_packet
from telemetry_v2 import decode


def main():
    print("СИМУЛАЦИЯ: SEN0667 + SEN0385 + TEL0157")
    # При реалния локален BMP581 драйвер: pressure_pa = bmp.pressure * 1000.
    barometer = {"ok": True, "age_ms": 100, "temperature_c": 24,
                 "pressure_pa": 101325}
    environment = {"ok": True, "age_ms": 150, "crc_ok": True,
                   "temperature_c": 21.5, "humidity_rh": 48.25}
    gnss = {"ok": True, "age_ms": 500, "fix_valid": True,
            "altitude_valid": True, "latitude_deg": 42.0,
            "longitude_deg": 23.0, "altitude_m": 550.0}
    for sequence in range(3):
        if sequence == 1:
            # Последната позиция е стара: тя няма да се изпрати като прясна.
            gnss["age_ms"] = 5000
        if sequence == 2:
            # Под диапазона на BMP581 и с лош CRC на SHT31: полетата липсват.
            barometer["pressure_pa"] = 20000
            environment["crc_ok"] = False
        packet = make_packet(sequence, barometer, environment, gnss, 3900)
        print(len(packet), "байта:", decode(packet))


if __name__ == "__main__":
    main()
