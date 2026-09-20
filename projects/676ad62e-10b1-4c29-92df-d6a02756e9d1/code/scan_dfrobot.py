"""Проверка на адреси; подава се вече проверена machine.I2C конфигурация."""


def check_bus(i2c, bmp_address=0x47):
    # SEN0667 може да бъде 0x46 или 0x47. SEN0385 използва 0x44.
    if bmp_address not in (0x46, 0x47):
        raise ValueError("SEN0667 address")
    found = set(i2c.scan())
    return {"SEN0667_address_seen": bmp_address in found,
            "SEN0385_address_seen": 0x44 in found}


# Пример след проверката на пиновете: print(check_bus(i2c))
# Адресният ACK не доказва chip ID, правилно измерване или хардуерна безопасност.
# TEL0157 е на UART в този проект и не се очаква в I2C scan.
