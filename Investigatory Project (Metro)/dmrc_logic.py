# dmrc_logic.py

def get_all_stations():
    """
    Return a list of all metro stations.
    Replace this with your real station list later.
    """
    stations = [
        "Noida City Centre",
        "Botanical Garden",
        "Rajiv Chowk",
        "Kashmere Gate",
        "Huda City Centre",
    ]
    return stations


def get_route_and_fare(source, destination):
    """
    Given source and destination station names, return:
      - route: list of station names in order
      - fare: integer or float value in rupees
    Right now this is dummy logic, just to test UI.
    """
    if source == destination:
        return [source], 0

    # Dummy example route, replace with your actual logic
    route = [source, "Rajiv Chowk", destination]
    fare = 40

    return route, fare
