"""Проверки на формата на компютър. Не са радио или полетни тестове."""
import unittest
from telemetry import encode, decode, SIZE


class TelemetryTests(unittest.TestCase):
    def test_round_trip(self):
        value = decode(encode(7, 21.5, 101325, (42.0, 23.0, 550.0), 3900))
        self.assertEqual(SIZE, 26)
        self.assertEqual(value["sequence"], 7)
        self.assertEqual(value["position"], (42.0, 23.0, 550.0))
        self.assertEqual(value["temperature_c"], 21.5)

    def test_missing_values(self):
        self.assertIsNone(decode(encode(1))["position"])
        self.assertIsNone(decode(encode(1, pressure_pa=20000))["pressure_pa"])

    def test_bad_data(self):
        for payload in (b"", bytes(SIZE), encode(1) + b"x"):
            with self.assertRaises(ValueError):
                decode(payload)
        for value in (float("nan"), float("inf"), -101):
            with self.assertRaises(ValueError):
                encode(1, temperature_c=value)
        with self.assertRaises(ValueError):
            encode(1, position=(91, 0, 0))


if __name__ == "__main__":
    unittest.main()
