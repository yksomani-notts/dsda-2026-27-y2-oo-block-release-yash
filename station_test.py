from station import Station


def main():
    label = "Stanmore, Wolverton Road"
    station = Station(label)

    print(station)

    df = station.get_water_level()

    print(df)


if __name__ == "__main__":
    main()
