"""Host проверки на модела; няма DFRobot хардуер в тези тестове."""
import unittest
import telemetry as v1
import telemetry_v2 as v2
from dfrobot_model import make_packet
from scan_dfrobot import check_bus


class DFRobotModelTests(unittest.TestCase):
    def setUp(self):
        self.barometer = dict(ok=True, age_ms=0, temperature_c=25, pressure_pa=101325)
        self.environment = dict(ok=True, age_ms=0, crc_ok=True,
                                temperature_c=20, humidity_rh=55.25)
        self.gnss = dict(ok=True, age_ms=0, fix_valid=True, altitude_valid=True,
                         latitude_deg=42, longitude_deg=23, altitude_m=550)

    def result(self):
        return v2.decode(make_packet(1, self.barometer, self.environment, self.gnss))

    def test_v2_roundtrip_and_old_receiver(self):
        packet = v2.encode(1, humidity_rh=55.25)
        self.assertEqual(len(packet), 28)
        self.assertEqual(v2.decode(packet)["humidity_rh"], 55.25)
        with self.assertRaises(ValueError):
            v1.decode(packet)
        with self.assertRaises(ValueError):
            v2.decode(v1.encode(1))

    def test_invalid_humidity(self):
        for value in (-1, 100.01, float("nan"), float("inf"), True):
            with self.assertRaises(ValueError):
                v2.encode(1, humidity_rh=value)
        corrupt = bytearray(v2.encode(1))
        corrupt[-1] = 1  # Скрито ненулево поле без флаг се отхвърля.
        with self.assertRaises(ValueError):
            v2.decode(corrupt)
        corrupt = bytearray(v2.encode(1, humidity_rh=100))
        corrupt[-2:] = b"\xff\xff"
        with self.assertRaises(ValueError):
            v2.decode(corrupt)

    def test_environment_source(self):
        self.assertEqual(self.result()["temperature_c"], 20)
        self.assertEqual(self.result()["humidity_rh"], 55.25)
        self.assertEqual(self.result()["position"], (42, 23, 550))

    def test_crc_and_stale_samples(self):
        self.environment["crc_ok"] = False
        self.assertIsNone(self.result()["temperature_c"])
        self.assertIsNone(self.result()["humidity_rh"])
        self.gnss["age_ms"] = 3001
        self.assertIsNone(self.result()["position"])
        self.barometer["age_ms"] = -1
        self.assertIsNone(self.result()["pressure_pa"])

    def test_out_of_range_and_missing_data(self):
        self.barometer["pressure_pa"] = 20000
        self.assertIsNone(self.result()["pressure_pa"])
        self.barometer["pressure_pa"] = 101325
        self.barometer["temperature_c"] = -10
        self.assertIsNone(self.result()["pressure_pa"])
        self.gnss["altitude_valid"] = False
        self.assertIsNone(self.result()["position"])
        self.environment["humidity_rh"] = float("nan")
        self.assertIsNone(self.result()["humidity_rh"])
        self.assertIsNone(v2.decode(make_packet(1))["humidity_rh"])

    def test_i2c_inventory(self):
        class FakeI2C:
            def scan(self):
                return [0x44, 0x47]
        self.assertTrue(all(check_bus(FakeI2C()).values()))
        self.assertFalse(check_bus(FakeI2C(), 0x46)["SEN0667_address_seen"])


if __name__ == "__main__":
    unittest.main()
