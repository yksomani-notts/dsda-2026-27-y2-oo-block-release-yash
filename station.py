import pandas as pd
import requests

BASE_URL = "https://environment.data.gov.uk/flood-monitoring/id/stations"


class Station:
    """Represents a flood monitoring station."""

    def __init__(self, label):
        """Initialise a Station object with the given label.

        Args:
            label: The label of the station to retrieve."""
        # passing the label via params ensures it is correctly url-encoded
        response = requests.get(BASE_URL, params={"label": label}, timeout=30)
        response.raise_for_status()
        responsejson = response.json()

        # the json should contain one response in an array called 'items'
        try:
            station = responsejson["items"][0]
        except IndexError:
            raise ValueError("No station found with label: " + label) from None

        # extract values from the returned json and set them as attributes;
        self._id = station.get("@id")
        self._measures = station.get("measures")
        self.catchment = station.get("catchmentName")
        self.label = station.get("label")
        self.lat = station.get("lat")
        self.long = station.get("long")
        self.river = station.get("riverName")
        self.town = station.get("town")

    def __repr__(self):
        return f"Station({self.label!r})"

    def __str__(self):
        # only include the details the station actually has
        parts = [f"Station: {self.label}"]
        if self.lat is not None and self.long is not None:
            parts.append(f"at ({self.lat:.6f},{self.long:.6f})")
        if self.town is not None:
            parts.append(f"in town: {self.town}")
        if self.river is not None:
            parts.append(f"on river: {self.river}")
        if self.catchment is not None:
            parts.append(f"catchment area: {self.catchment}")
        return " ".join(parts) + "."

    def get_water_level(self):
        """Get the water level readings for the station."""
        # find the water level measure, as a station may have several measures
        measure = None
        for m in self._measures or []:
            if m.get("parameterName") == "Water Level":
                measure = m
                break
        if measure is None:
            raise ValueError(f"Station {self._id} does not have water level.")

        # read the water level readings straight into a DataFrame
        df = pd.read_csv(
            measure["@id"] + "/readings.csv",
            usecols=["dateTime", "value"],
            parse_dates=["dateTime"],
        )
        df.columns = ["date", "level"]
        return df
