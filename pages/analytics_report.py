import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import csv
import collections
import io
import base64
from dash import html


def load_locations():
    locations = []
    with open("data/locations.csv", 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            locations.append({
                'id': int(row['id']),
                'name': row['name'],
                'building': row['building'],
                'floor': int(row['floor']),
                'accessible': row['accessible'].lower() == 'true'
            })
    return locations


def load_routes():
    routes = []
    with open("data/routes.csv", 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            routes.append({
                'id': int(row['id']),
                'start_location': row['start_location'],
                'end_location': row['end_location'],
                'distance_m': float(row['distance_m']),
                'accessible': row['accessible'].lower() == 'true'
            })
    return routes


def fig_to_base64():
    buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format="png")
    plt.close()
    buffer.seek(0)
    return "data:image/png;base64," + base64.b64encode(buffer.read()).decode()


def bar_visits_per_building(locations):
    counts = collections.Counter([loc['building'] for loc in locations])
    plt.figure(figsize=(6, 4))
    plt.bar(counts.keys(), counts.values())
    plt.title("Visits per Building")
    plt.xlabel("Building")
    plt.ylabel("Count")
    return fig_to_base64()


def pie_visits_per_building(locations):
    counts = collections.Counter([loc['building'] for loc in locations])
    plt.figure(figsize=(6, 4))
    plt.pie(counts.values(), labels=counts.keys(), autopct="%1.1f%%")
    plt.title("Visit Share by Building")
    return fig_to_base64()


def line_visits_over_floors(locations):
    counts = collections.Counter([loc['floor'] for loc in locations])
    floors = sorted(counts.keys())
    values = [counts[f] for f in floors]
    plt.figure(figsize=(6, 4))
    plt.plot(floors, values, marker="o")
    plt.title("Visit Trend by Floor")
    plt.xlabel("Floor")
    plt.ylabel("Visits")
    return fig_to_base64()


def heatmap_routes(routes):
    locations = sorted(set([r['start_location'] for r in routes] + [r['end_location'] for r in routes]))
    matrix = [[0 for _ in locations] for _ in locations]
    for r in routes:
        i = locations.index(r['start_location'])
        j = locations.index(r['end_location'])
        matrix[i][j] += 1
    plt.figure(figsize=(6, 4))
    plt.imshow(matrix, cmap="Blues")
    plt.colorbar(label="Route Usage")
    plt.xticks(range(len(locations)), locations, rotation=45)
    plt.yticks(range(len(locations)), locations)
    plt.title("Route Crowdedness Heatmap")
    return fig_to_base64()


def scatter_distance_vs_route(routes):
    plt.figure(figsize=(6, 4))
    plt.scatter([r['distance_m'] for r in routes], list(range(len(routes))))
    plt.title("Route Distance Distribution")
    plt.xlabel("Distance (meters)")
    plt.ylabel("Route Index")
    return fig_to_base64()


def histogram_distance(routes):
    plt.figure(figsize=(6, 4))
    plt.hist([r['distance_m'] for r in routes], bins=5)
    plt.title("Route Distance Histogram")
    plt.xlabel("Distance (meters)")
    plt.ylabel("Frequency")
    return fig_to_base64()


def layout():
    locations = load_locations()
    routes = load_routes()

    return html.Div(
        style={"maxWidth": "1100px", "margin": "0 auto"},
        children=[
            html.H2("Analytics Report"),

            html.H3("Location Analytics"),
            html.Img(src=bar_visits_per_building(locations)),
            html.Img(src=pie_visits_per_building(locations)),
            html.Img(src=line_visits_over_floors(locations)),

            html.Hr(),

            html.H3("Route Analytics"),
            html.P("Dark color indicates more crowded routes"),
            html.Img(src=heatmap_routes(routes)),

            html.P("Distance vs route index"),
            html.Img(src=scatter_distance_vs_route(routes)),

            html.P("Route distance distribution"),
            html.Img(src=histogram_distance(routes)),
        ],
    )
