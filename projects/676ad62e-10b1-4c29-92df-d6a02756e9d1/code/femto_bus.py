"""Начална FEMTO шина за SEN0667/SEN0385. Не отваря UART или радио."""


def make_bus():
    from machine import Pin, SoftI2C
    # H1.3 = P001 (SCL); H1.4 = P002 (SDA). Pull-up само към 3.3 V.
    return SoftI2C(scl=Pin("P001"), sda=Pin("P002"), freq=100000)


if __name__ == "__main__":
    from scan_dfrobot import check_bus
    print(check_bus(make_bus()))
    # ACK проверява адреси, не точност. TEL0157 е на UART(2), не на тази шина.
