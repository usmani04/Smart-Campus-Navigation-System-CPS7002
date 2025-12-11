import dash
from dash import html, dcc, Input, Output, State
import csv, os, hashlib

dash.register_page(__name__, path="/")

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def layout():
    return html.Div(
        style={
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center",
            "height": "100vh",
            "backgroundColor": "#f4f6f8",
            "fontFamily": "Arial"
        },
        children=[
            html.Div(
                style={
                    "width": "380px",
                    "padding": "40px",
                    "backgroundColor": "white",
                    "borderRadius": "12px",
                    "boxShadow": "0 4px 15px rgba(0,0,0,0.15)",
                    "textAlign": "center"
                },
                children=[

                    html.Img(
                        src="https://upload.wikimedia.org/wikipedia/en/f/f5/St_Mary%27s_University_Twickenham_coat_of_arms.png",
                        style={"width": "90px", "marginBottom": "20px"}
                    ),

                    html.H2("Smart Campus Navigation System", style={"color": "#333"}),
                    html.H3("Login", style={"color": "#555", "marginBottom": "25px"}),

                    dcc.Input(
                        id="login-username",
                        type="text",
                        placeholder="Username",
                        style={
                            "width": "100%",
                            "padding": "12px",
                            "marginBottom": "15px",
                            "border": "2px solid #1E90FF",
                            "borderRadius": "6px",
                            "boxSizing": "border-box"
                        }
                    ),

                    html.Div(
                        style={"position": "relative", "width": "100%"},
                        children=[
                            dcc.Input(
                                id="login-password",
                                type="password",
                                placeholder="Password",
                                style={
                                    "width": "100%",
                                    "padding": "12px 40px 12px 12px",
                                    "marginBottom": "20px",
                                    "border": "2px solid #1E90FF",
                                    "borderRadius": "6px",
                                    "boxSizing": "border-box"
                                }
                            ),

                            html.Button(
                                "👁️",
                                id="toggle-pass",
                                n_clicks=0,
                                style={
                                    "position": "absolute",
                                    "right": "10px",
                                    "top": "8px",
                                    "border": "none",
                                    "background": "transparent",
                                    "cursor": "pointer",
                                    "fontSize": "18px"
                                }
                            )
                        ]
                    ),

                    html.Button(
                        "Login",
                        id="login-btn",
                        n_clicks=0,
                        style={
                            "width": "100%",
                            "padding": "12px",
                            "backgroundColor": "#1E90FF",
                            "border": "none",
                            "color": "white",
                            "borderRadius": "6px",
                            "fontSize": "16px",
                            "cursor": "pointer"
                        }
                    ),

                    html.Div(id="login-output", style={"marginTop": "15px", "color": "red"}),

                    html.Div(
                        [
                            html.Span("Don't have an account? "),
                            html.A("Sign Up", href="/signup", style={"color": "#1E90FF", "fontWeight": "bold"})
                        ],
                        style={"marginTop": "20px", "fontSize": "14px"}
                    )
                ]
            )
        ]
    )


@dash.callback(
    Output("login-output", "children"),
    Input("login-btn", "n_clicks"),
    State("login-username", "value"),
    State("login-password", "value"),
)
def login_user(n, username, password):
    if not n:
        return ""

    if not username or not password:
        return "Please enter both username and password."

    filepath = "data/user_data.csv"

    if not os.path.exists(filepath):
        return "User database not found."

    hashed_pw = hash_password(password)

    with open(filepath, "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            if row["username"] == username and row["password"] == hashed_pw:
                return html.Div("Login Successful!", style={"color": "green"})

    return "Invalid username or password."

@dash.callback(
    Output("login-password", "type"),
    Input("toggle-pass", "n_clicks"),
    State("login-password", "type")
)
def toggle_password(n, current_type):
    if n:
        return "text" if current_type == "password" else "password"
    return current_type
