# dmrc_logic.py
"""
Logic layer for DMRC project, adapted from original DMTC CS Project.py

- No input()/print()
- No MySQL / GUI / matplotlib
- Only: load CSV, compute route, compute fare
"""
import csv
import os
import math
import matplotlib.pyplot as plt   
# ---------------------------
# Load CSV once at import
# ---------------------------

BASE_DIR = os.path.dirname(__file__)
CSV_PATH = os.path.join(BASE_DIR, "DMTC Stations CS Database.csv")

with open(CSV_PATH, newline="", encoding="utf-8") as f:
    csvlist = list(csv.reader(f))


# ---------------------------
# Helper functions
# ---------------------------

x_co_extracter = lambda co: co[0]
y_co_extracter = lambda co: co[1]


def get_line(st: str):
    """
    Return set of line names that contain station st.
    """
    st = st.upper()
    linenames_set = set()
    for line in csvlist:
        if st in line:
            linenames_set.add(line[0])
    return linenames_set


def get_coordinates(st: str):
    """
    Return (x, y) coordinates for a station as floats.
    This is taken directly from your original code.
    """
    st = st.upper()
    line_name = get_line(st).pop()  # pick one line that contains the station
    line_index = int(line_name[0:2]) * 2
    # On next row (+1) same index holds coordinates as a string like "(x, y)"
    coord_str = csvlist[line_index + 1][csvlist[line_index].index(st)]
    # eval to tuple, then reverse order [::-1] like your original code
    return tuple(eval(coord_str))[::-1]


def get_avg_distance(route):
    """
    Average distance proxy used by your original code.
    (Actually total path length in 'coordinate distance', then scaled)
    """
    avg_distance = 0.0
    for i in route[1:]:
        prev = route[route.index(i) - 1]
        x1, y1 = get_coordinates(prev)
        x2, y2 = get_coordinates(i)
        avg_distance += math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return avg_distance


def short_route_generat(routes, linenames):
    """
    Choose route with minimum distance from list of candidate routes.
    """
    distances = list(map(get_avg_distance, routes))
    index = distances.index(min(distances))
    return routes[index], linenames[index]


def get_route(st1: str, st2: str):
    """
    Route when both stations lie on same line(s), based on your original logic.
    """
    st1 = st1.upper()
    st2 = st2.upper()
    setA = get_line(st1)
    setB = get_line(st2)

    if st1 == st2 and len(setA) != 0:
        # same station, just return it and one of its lines
        return [st1], setA.pop()

    common_line_name = setA.intersection(setB)
    routes = []
    linenames_func = []

    try:
        while True:
            linename = common_line_name.pop()
            lineinfo1 = csvlist[int(linename[0:2]) * 2]
            lineinfo2 = list(reversed(lineinfo1))
            # direct path in forward and reverse arrays (your original trick)
            routes.append(
                lineinfo1[lineinfo1.index(st1): lineinfo1.index(st2) + 1]
                + lineinfo2[lineinfo2.index(st1): lineinfo2.index(st2) + 1]
            )
            linenames_func.append(linename)
    except KeyError:
        # no more common lines
        pass
    except Exception:
        # just break on any pop() error
        pass

    return short_route_generat(routes, linenames_func)

def build_route_figure(route, init_st, dest_st):
    """
    Build a matplotlib Figure that looks like the original project:
    - full Delhi network (all lines, colored)
    - highlighted route between init_st and dest_st
    """
    fig = plt.figure(figsize=(7, 5), dpi=100)

    # ----- draw full network (your old plot_map logic) -----
    for row in csvlist:
        if not row:
            continue
        if row[0] in ("Line Info", ""):
            continue

        # your original code: skip rows whose first char IS 'C'
        if row[0][0] == "C":
            continue

        # station names on this line
        try:
            end_idx = row.index("")
            stations_on_line = row[1:end_idx]
        except ValueError:
            stations_on_line = row[1:]

        if not stations_on_line:
            continue

        xs = list(map(x_co_extracter, map(get_coordinates, stations_on_line)))
        ys = list(map(y_co_extracter, map(get_coordinates, stations_on_line)))

        # colour encoded in line header like "01 Red Line"
        try:
            color = row[0][3:row[0].index("L") - 1]
        except ValueError:
            color = "black"

        plt.plot(
            xs,
            ys,
            marker=".",
            ms=2,
            mfc="black",
            mec="black",
            c=color,
        )

    # ----- highlight the selected route (similar to your old code) -----
    init_st = init_st.upper()
    dest_st = dest_st.upper()

    try:
        prevst = route[0]
        plt.annotate(
            init_st,
            (get_coordinates(init_st)[0] + 0.005, get_coordinates(init_st)[1] + 0.005),
            size=5,
        )
        plt.annotate(
            dest_st,
            (get_coordinates(dest_st)[0] + 0.005, get_coordinates(dest_st)[1] + 0.005),
            size=5,
        )

        for stprnt in route:
            if prevst == stprnt != route[0]:
                # interchange
                x, y = get_coordinates(stprnt)
                plt.scatter(x, y, c="yellow", s=50)
                plt.annotate(stprnt, (x, y), size=5)
            else:
                x1, y1 = get_coordinates(prevst)
                x2, y2 = get_coordinates(stprnt)
                plt.arrow(
                    x1,
                    y1,
                    x2 - x1,
                    y2 - y1,
                    head_width=0.01,
                    ec="lime",
                    alpha=0.5,
                    width=0.01,
                )
            prevst = stprnt

        # start/end markers
        sx, sy = get_coordinates(init_st)
        dx, dy = get_coordinates(dest_st)
        plt.scatter(sx, sy, c="green", s=50)
        plt.scatter(dx, dy, c="red", s=50)

    except Exception:
        # if anything fails, we at least show base map
        pass

    plt.title("Delhi Transit route map", size=15, c="black")
    plt.xlabel("x coordinates (1 unit = 100Km)")
    plt.ylabel("y coordinates (1 unit = 100Km)")

    return fig

# ---------------------------
# Public functions for Streamlit
# ---------------------------

def _compute_all_stations():
    """
    Extract all station names from CSV once.
    """
    stations_set = set()
    for row in csvlist:
        if not row:
            continue
        # From your plot_map: skip 'Line Info', '' and 'C...'
        if row[0] in ("Line Info", ""):
            continue
        if row[0][0] == "C":
            continue

        # stations are from col 1 until first empty string
        for s in row[1:]:
            if s == "":
                break
            stations_set.add(s.upper())

    return sorted(stations_set)


_STATIONS = _compute_all_stations()


def get_all_stations():
    """
    Return list of all station names (uppercased), for dropdowns.
    """
    return _STATIONS


def get_route_and_fare(source: str, destination: str):
    """
    Main function used by Streamlit app.

    Given source and destination station names,
    return (route_list, fare_amount)
    using your original routing + fare logic (without MySQL/GUI).
    """
    init_st = source.upper()
    dest_st = destination.upper()

    set_init = get_line(init_st)
    set_dest = get_line(dest_st)

    # -------------- route selection (based on your original code) --------------
    if len(set_init.intersection(set_dest)) in (1, 2):
        route, linename = get_route(init_st, dest_st)
        linename = linename[3:]  # strip initial 'xx ' part as in original

    elif len(set_init.intersection(set_dest)) == 0:
        routes = []
        linenames = []

        # First: one interchange
        for i1 in get_line(init_st):
            line1_index = int(i1[0:2]) * 2
            for i2 in csvlist[line1_index]:
                if i2 == "":
                    break
                if len(get_line(i2).intersection(get_line(dest_st))) != 0:
                    phase1, linename1 = get_route(init_st, i2)
                    phase2, linename2 = get_route(i2, dest_st)
                    routes.append(phase1 + phase2)
                    linenames.append(linename1[3:] + " and " + linename2[3:])
                    route, linename = short_route_generat(routes, linenames)

        # Second: two interchanges (if first did not find any)
        if not routes:
            for i1 in get_line(init_st):
                for i2 in get_line(dest_st):
                    line1_index = int(i1[0:2]) * 2
                    line2_index = int(i2[0:2]) * 2
                    for i3 in csvlist[line1_index]:
                        if i3 == "":
                            break
                        for i4 in csvlist[line2_index]:
                            if i4 == "":
                                break
                            if len(get_line(i3).intersection(get_line(i4))) != 0:
                                phase1, linename1 = get_route(init_st, i3)
                                phase2, linename2 = get_route(i3, i4)
                                phase3, linename3 = get_route(i4, dest_st)
                                routes.append(phase1 + phase2 + phase3)
                                linenames.append(
                                    linename1[3:] + ", " + linename2[3:] + " and " + linename3[3:]
                                )
                                route, linename = short_route_generat(routes, linenames)
    else:
        # fallback – should rarely happen
        route = [init_st, dest_st]
        linename = ""

    # -------------- fare calculation (ported from your code) --------------
    avg_distance = get_avg_distance(route) * 100  # same scale factor

    if avg_distance == 0:
        fare = 0
    elif 0 < avg_distance <= 2:
        fare = 10
    elif 2 < avg_distance <= 5:
        fare = 20
    elif 5 < avg_distance <= 12:
        fare = 30
    elif 12 < avg_distance <= 21:
        fare = 40
    elif 21 < avg_distance <= 32:
        fare = 50
    else:  # > 32
        fare = 60

    # NOTE: I skipped the Sunday/holiday discount and MySQL logging,
    # because they don't make sense in a stateless Streamlit cloud app.

    return route, fare
