"""Host doubles only: no radio transmission and no UART hardware test."""
import types
import unittest
from unittest.mock import Mock, patch
import femto_radio as radio
import femto_bus


class RadioTest(unittest.TestCase):
    def setUp(self):
        self.spi, self.mac = Mock(), Mock()
        self.machine = types.SimpleNamespace(Pin=lambda name: name,
                                             SPI=Mock(return_value=self.spi),
                                             UART=Mock())
        self.lorawan = types.SimpleNamespace(EU868=5, Mac=Mock(return_value=self.mac))
        self.modules = patch.dict("sys.modules", machine=self.machine, lorawan=self.lorawan)
        self.modules.start()
        self.addCleanup(self.modules.stop)

    def test_exact_example_radio_pins_no_transmit(self):
        self.assertEqual(radio.open_radio(), (self.mac, self.spi))
        self.machine.SPI.assert_called_once_with(3, baudrate=8000000, polarity=0,
                                                phase=0, sck="P111", mosi="P109", miso="P110")
        self.lorawan.Mac.assert_called_once_with(region=5, spi=self.spi, cs="P206",
                                                rst="P001", gpio_busy="P002",
                                                irq="P015", rf_sw="P100")
        self.assertEqual(self.mac.mock_calls, [])

    def test_constructor_failure_releases_bus(self):
        self.lorawan.Mac.side_effect = RuntimeError("fixture")
        with self.assertRaises(RuntimeError):
            radio.open_radio()
        self.spi.deinit.assert_called_once()

    def test_cleanup_releases_bus_even_on_error(self):
        self.mac.deinit.side_effect = RuntimeError("fixture")
        with self.assertRaises(RuntimeError):
            radio.close_radio(self.mac, self.spi)
        self.spi.deinit.assert_called_once()

    def test_uart_needs_verified_mapping(self):
        with self.assertRaises(RuntimeError):
            radio.open_gnss_uart()
        self.machine.UART.assert_not_called()

    def test_uart3_not_uart9_no_tx_rx_override(self):
        radio.open_gnss_uart(board_mapping_verified=True)
        self.assertEqual(radio.GNSS_PADS, {"rx": "TP4/P408", "tx": "TP6/P409", "uart": 3})
        self.machine.UART.assert_called_once_with(3, baudrate=9600, bits=8, parity=None,
                                                 stop=1, rxbuf=512, timeout=0)

    def test_sensor_bus_avoids_radio_reset_busy(self):
        self.machine.SoftI2C = Mock()
        femto_bus.make_bus()
        self.machine.SoftI2C.assert_called_once_with(scl="P302", sda="P301", freq=100000)


if __name__ == "__main__":
    unittest.main()
