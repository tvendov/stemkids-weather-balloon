"""Симулация на маса. Работи без сензор, платка, антена и предавател."""
from telemetry import encode, decode


def main():
    print("СИМУЛАЦИЯ: числата не идват от истински датчик.")
    for sequence in range(3):
        # Нямаме GNSS fix и изрично оставяме position=None.
        packet = encode(sequence, temperature_c=21.5 + sequence / 10,
                        pressure_pa=101325, battery_mv=3900)
        print("Дължина:", len(packet), "байта; данни:", decode(packet))
    # Налягане под обхвата не се представя като годно за измерване.
    print("Извън диапазон:", decode(encode(3, pressure_pa=20000)))


if __name__ == "__main__":
    main()
