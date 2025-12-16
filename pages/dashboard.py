import dash
from dash import html, dcc, Input, Output, callback
from pages import manage_user, analytics_report, access_control  

BLUE = "#0B63C5"
LIGHT = "#F4F9FF"
WHITE = "#FFFFFF"

dash.register_page(__name__, path="/dashboard")

def menu_btn_style():
    return {
        "padding": "12px",
        "marginBottom": "10px",
        "backgroundColor": LIGHT,
        "borderRadius": "6px",
        "cursor": "pointer",
        "fontSize": "18px",
        "border": "1px solid #ddd",
    }


def layout():
    return html.Div(
        style={
            "backgroundColor": LIGHT,
            "minHeight": "100vh",
            "fontFamily": "Arial"
        },
        children=[
            dcc.Location(id="dash-url"),

            html.Div(
                style={
                    "backgroundColor": BLUE,
                    "padding": "18px",
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "color": "white",
                },
                children=[
                    html.Div(
                        [
                            html.Img(
                                src="https://upload.wikimedia.org/wikipedia/en/f/f5/St_Mary%27s_University_Twickenham_coat_of_arms.png",
                                style={"height": "40px", "marginRight": "10px"},
                            ),
                            html.Span(
                                "Smart Campus Dashboard",
                                style={"fontSize": "24px", "fontWeight": "bold"},
                            ),
                        ],
                        style={"display": "flex", "alignItems": "center"},
                    ),
                    html.Button(
                        "Logout",
                        id="logout-btn",
                        n_clicks=0,
                        style={
                            "padding": "10px 15px",
                            "backgroundColor": "red",
                            "color": "white",
                            "border": "none",
                            "borderRadius": "6px",
                            "cursor": "pointer",
                        },
                    ),
                ],
            ),

            html.Div(
                style={"display": "flex"},
                children=[
                    html.Div(
                        style={
                            "width": "220px",
                            "backgroundColor": WHITE,
                            "minHeight": "100vh",
                            "padding": "20px",
                            "boxShadow": "2px 0 8px rgba(0,0,0,0.1)",
                        },
                        children=[
                            html.H3("Menu", style={"color": BLUE}),

                            html.Div(
                                "👥 Manage Users",
                                id="menu-users",
                                n_clicks=0,
                                style=menu_btn_style(),
                            ),

                            html.Div(
                                "📊 Analytics & Reports",
                                id="menu-analytics",
                                n_clicks=0,
                                style=menu_btn_style(),
                            ),
                        
                            html.Div(
                                "📍 Route Finder",
                                id="menu-access-control",
                                n_clicks=0,
                                style=menu_btn_style(),
                            ),
                        ],
                    ),

                    html.Div(
                        id="dashboard-content",
                        style={"flex": "1", "padding": "30px"}
                    ),
                ],
            ),
        ],
    )

@callback(
    Output("dashboard-content", "children"),
    [
        Input("menu-users", "n_clicks"),
        Input("menu-analytics", "n_clicks"),
        Input("menu-access-control", "n_clicks"), 
    ],
)
def update_page(users_clicks, analytics_clicks, access_control_clicks):
    ctx = dash.callback_context

    if not ctx.triggered:
        return dash.no_update

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "menu-users":
        return manage_user.layout()

    if button_id == "menu-analytics":
        return analytics_report.layout()

    if button_id == "menu-access-control":
        return access_control.layout()

    return dash.no_update


@callback(
    Output("dash-url", "href"),
    Input("logout-btn", "n_clicks"),
)
def logout(n_clicks):
    if n_clicks:
        return "/"
    return dash.no_update