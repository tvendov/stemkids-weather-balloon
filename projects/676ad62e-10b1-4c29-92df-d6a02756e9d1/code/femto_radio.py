"""FEMTO + Wio-SX1262: същите радио пинове като LoRaWAN примерите."""

RADIO_PINS = {
    "sck": "P111", "mosi": "P109", "miso": "P110",
    "cs": "P206", "rst": "P001", "gpio_busy": "P002",
    "irq": "P015", "rf_sw": "P100",
}
GNSS_PADS = {"rx": "TP4/P408", "tx": "TP6/P409", "uart": 3}


def open_radio():
    # SPI(3) използва SCI9. Не изпълняваме join/send и не изтриваме NVM.
    from machine import Pin, SPI
    import lorawan
    spi = SPI(3, baudrate=8000000, polarity=0, phase=0,
              sck=Pin(RADIO_PINS["sck"]), mosi=Pin(RADIO_PINS["mosi"]),
              miso=Pin(RADIO_PINS["miso"]))
    try:
        mac = lorawan.Mac(region=lorawan.EU868, spi=spi,
                          cs=RADIO_PINS["cs"], rst=RADIO_PINS["rst"],
                          gpio_busy=RADIO_PINS["gpio_busy"],
                          irq=RADIO_PINS["irq"], rf_sw=RADIO_PINS["rf_sw"])
    except BaseException:
        spi.deinit()
        raise
    # Собственикът извиква първо mac.deinit(), после spi.deinit().
    return mac, spi


def open_gnss_uart(board_mapping_verified=False):
    # RA4M2 Table 19.9: TP4=P408 RXD3, TP6=P409 TXD3, отделно от SCI9.
    # Текущият порт се нуждае от UART3 board/IRQ/pin-table корекция.
    # Няма tx/rx keyword аргументи в проверения machine.UART конструктор.
    if not board_mapping_verified:
        raise RuntimeError("Първо провери коригиран UART3 build за TP4/TP6.")
    from machine import UART
    return UART(3, baudrate=9600, bits=8, parity=None, stop=1,
                rxbuf=512, timeout=0)


def close_radio(mac, spi):
    # Освобождаваме SPI дори ако mac.deinit() върне грешка.
    try:
        mac.deinit()
    finally:
        spi.deinit()
