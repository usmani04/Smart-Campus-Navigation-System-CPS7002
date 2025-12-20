import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import io
import base64
from dash import html


def load_locations():
    return pd.read_csv("data/locations.csv")


def load_routes():
    return pd.read_csv("data/routes.csv")


def fig_to_base64():
    buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format="png")
    plt.close()
    buffer.seek(0)
    return "data:image/png;base64," + base64.b64encode(buffer.read()).decode()


def bar_visits_per_building(df):
    counts = df["building"].value_counts()
    plt.figure(figsize=(6, 4))
    plt.bar(counts.index, counts.values)
    plt.title("Visits per Building")
    plt.xlabel("Building")
    plt.ylabel("Visit Count")
    return fig_to_base64()


def pie_visits_per_building(df):
    counts = df["building"].value_counts()
    plt.figure(figsize=(6, 4))
    plt.pie(counts.values, labels=counts.index, autopct="%1.1f%%")
    plt.title("Visit Share by Building")
    return fig_to_base64()


def line_visits_over_floors(df):
    counts = df.groupby("floor").size()
    plt.figure(figsize=(6, 4))
    plt.plot(counts.index, counts.values, marker="o")
    plt.title("Visit Trend by Floor")
    plt.xlabel("Floor")
    plt.ylabel("Visits")
    return fig_to_base64()


def heatmap_routes(df):
    pivot = pd.pivot_table(
        df,
        index="start_location",
        columns="end_location",
        values="id",
        aggfunc="count",
        fill_value=0,
    )
    plt.figure(figsize=(6, 4))
    plt.imshow(pivot, cmap="Blues")
    plt.colorbar(label="Route Usage")
    plt.xticks(range(len(pivot.columns)), pivot.columns, rotation=45)
    plt.yticks(range(len(pivot.index)), pivot.index)
    plt.title("Route Crowdedness Heatmap")
    return fig_to_base64()


def scatter_distance_vs_route(df):
    plt.figure(figsize=(6, 4))
    plt.scatter(df["distance_m"], df.index)
    plt.title("Route Distance Distribution")
    plt.xlabel("Distance (meters)")
    plt.ylabel("Route Index")
    return fig_to_base64()


def histogram_distance(df):
    plt.figure(figsize=(6, 4))
    plt.hist(df["distance_m"], bins=5)
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
