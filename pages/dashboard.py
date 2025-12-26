import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
from pages import (
    manage_user,
    analytics_report,
    access_control,
    manage_route,
    manage_location,
    notifications,
    view_notifications,
    view_locations,
    view_routes,
)
import json


BLUE = "#0B63C5"
LIGHT = "#F4F9FF"
WHITE = "#FFFFFF"

dash.register_page(__name__, path="/dashboard")


def menu_btn_class():
    return "p-3 mb-2 bg-light rounded border fs-6 cursor-pointer"


def dashboard_welcome():
    return html.Div(
        className="d-flex flex-column align-items-center justify-content-center text-center",
        style={"height": "80vh"},
        children=[
            html.Img(
                src="https://upload.wikimedia.org/wikipedia/en/f/f5/St_Mary%27s_University_Twickenham_coat_of_arms.png",
                style={"maxWidth": "300px", "marginBottom": "30px"},
            ),
            html.H3(
                "Welcome to Smart Campus Navigation System",
                className="fw-bold",
                style={"color": BLUE},
            ),
            html.P(
                "Please select an option from the menu on the left to continue",
                className="fs-5 text-muted mt-2",
            ),
        ],
    )


def layout():
    return html.Div(
        className="bg-light min-vh-100",
        children=[
            dcc.Location(id="dash-url"),
            dcc.Store(id="current-user", storage_type="session"),

            
            dbc.Navbar(
                dbc.Container(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Img(
                                        src="https://upload.wikimedia.org/wikipedia/en/f/f5/St_Mary%27s_University_Twickenham_coat_of_arms.png",
                                        height="40px",
                                        className="me-2",
                                    ),
                                    width="auto",
                                ),
                                dbc.Col(
                                    html.Span(
                                        "Smart Campus Dashboard",
                                        className="fs-4 fw-bold text-white",
                                    ),
                                    width="auto",
                                ),
                            ],
                            align="center",
                            className="g-0",
                        ),
                        dbc.Button(
                            "Logout",
                            id="logout-btn",
                            n_clicks=0,
                            color="danger",
                            className="px-3 py-2",
                        ),
                    ],
                    fluid=True,
                ),
                color=BLUE,
                dark=True,
                className="py-3",
            ),

            
            dbc.Row(
                className="g-0",
                children=[
                  
                    dbc.Col(
                        width="auto",
                        className="bg-white p-3 shadow-sm min-vh-100",
                        style={"width": "240px"},
                        children=[
                            html.H5(
                                "Menu",
                                className="fw-bold mb-4",
                                style={"color": BLUE},
                            ),

                            html.Div("👥 Manage Users", id="menu-users", n_clicks=0,
                                     className=menu_btn_class(), role="button"),

                            html.Div("📊 Analytics & Reports", id="menu-analytics", n_clicks=0,
                                     className=menu_btn_class(), role="button"),

                            html.Div("📍 Route Finder", id="menu-access-control", n_clicks=0,
                                     className=menu_btn_class(), role="button"),

                            html.Div("🛣️ Routes", id="menu-routes", n_clicks=0,
                                     className=menu_btn_class(), role="button"),

                            html.Div("📍 Locations", id="menu-locations", n_clicks=0,
                                     className=menu_btn_class(), role="button"),

                            html.Div("🔔 Notifications", id="menu-notification", n_clicks=0,
                                     className=menu_btn_class(), role="button"),
                        ],
                    ),

                
                    dbc.Col(
                        id="dashboard-content",
                        className="p-4 flex-grow-1",
                        children=dashboard_welcome(), 
                    ),
                ],
            ),
        ],
    )

@callback(
    Output("menu-notification", "style"),
    Output("menu-locations", "style"),
    Output("menu-routes", "style"),
    Output("menu-users", "style"),
    Output("menu-analytics", "style"),
    Input("current-user", "data"),
)
def toggle_sidebar_items(current_user_data):
    if not current_user_data:
        hide = {"display": "none"}
        return hide, hide, hide, hide, hide

    user = json.loads(current_user_data)
    role = user.get("role")

    return (
        {"display": "block"},  
        {"display": "block"},
        {"display": "block"},  
        {"display": "block"} if role == "admin" else {"display": "none"},
        {"display": "block"} if role == "admin" else {"display": "none"},
    )


@callback(
    Output("dashboard-content", "children"),
    [
        Input("menu-users", "n_clicks"),
        Input("menu-analytics", "n_clicks"),
        Input("menu-access-control", "n_clicks"),
        Input("menu-routes", "n_clicks"),
        Input("menu-locations", "n_clicks"),
        Input("menu-notification", "n_clicks"),
        Input("current-user", "data"),
    ],
)
def update_page(u, a, ac, r, l, n, current_user_data):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    role = json.loads(current_user_data).get("role") if current_user_data else None

    if button_id == "menu-users":
        return manage_user.layout() if role == "admin" else html.Div("⛔ Access Denied", className="text-danger fw-bold")

    if button_id == "menu-analytics":
        return analytics_report.layout() if role == "admin" else html.Div("⛔ Access Denied", className="text-danger fw-bold")

    if button_id == "menu-access-control":
        return access_control.layout()

    if button_id == "menu-routes":
        return manage_route.layout() if role == "admin" else view_routes.view_routes_layout()

    if button_id == "menu-locations":
        return manage_location.locations_layout() if role == "admin" else view_locations.view_locations_layout()

    if button_id == "menu-notification":
        return notifications.notifications_layout() if role == "admin" else view_notifications.layout()

    return dash.no_update


@callback(
    Output("dash-url", "href"),
    Input("logout-btn", "n_clicks"),
)
def logout(n_clicks):
    if n_clicks:
        return "/"
    return dash.no_update
