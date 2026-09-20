"""Начална FEMTO шина за SEN0667/SEN0385. Не отваря UART или радио."""


def make_bus():
    from machine import Pin, SoftI2C
    # H1.7 = P302 (SCL); H2.7 = P301 (SDA). Pull-up само към 3.3 V.
    # P001/P002 са RESET/BUSY на Wio-SX1262 и не се използват за I2C.
    return SoftI2C(scl=Pin("P302"), sda=Pin("P301"), freq=100000)


if __name__ == "__main__":
    from scan_dfrobot import check_bus
    print(check_bus(make_bus()))
    # ACK проверява адреси, не точност. TEL0157 е на UART(3), не на тази шина.
