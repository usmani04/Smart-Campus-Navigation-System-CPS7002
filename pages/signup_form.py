from dash import html, dcc, Input, Output, State
import dash
import hashlib
import csv
import os

dash.register_page(__name__, path="/signup")


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
                    html.H3("Sign Up", style={"color": "#555", "marginBottom": "25px"}),

                    dcc.Input(
                        id="signup-username",
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

                    dcc.Input(
                        id="signup-email",
                        type="email",
                        placeholder="Email",
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
                        style={
                            "position": "relative",
                            "width": "100%",
                            "marginBottom": "15px"
                        },
                        children=[
                            dcc.Input(
                                id="signup-password",
                                type="password",
                                placeholder="Password",
                                style={
                                    "width": "100%",
                                    "padding": "12px",
                                    "border": "2px solid #1E90FF",
                                    "borderRadius": "6px",
                                    "boxSizing": "border-box"
                                }
                            ),

                            html.Span("👁️",
                                id="toggle-password",
                                style={
                                    "position": "absolute",
                                    "right": "12px",
                                    "top": "12px",
                                    "cursor": "pointer",
                                    "fontSize": "18px",
                                    "color": "#777"
                                }
                            )
                        ]
                    ),

                    dcc.Dropdown(
                        id="signup-role",
                        options=[
                            {"label": "Student", "value": "student"},
                            {"label": "Staff", "value": "staff"},
                            {"label": "Admin", "value": "admin"},
                            {"label": "Visitor", "value": "visitor"},
                        ],
                        placeholder="Select Role",
                        style={
                            "width": "100%",
                            "marginBottom": "20px",
                            "boxSizing": "border-box"
                        }
                    ),

                    dcc.Checklist(
    id="signup-consent",
    options=[
        {"label": " I agree to the collection and processing of my data (GDPR Consent)", "value": "yes"}
    ],
    style={"marginBottom": "20px", "fontSize": "14px", "textAlign": "left"}
),


                    html.Button(
                        "Sign Up",
                        id="signup-btn",
                        n_clicks=0,
                        style={
                            "width": "100%",
                            "padding": "12px",
                            "backgroundColor": "#1E90FF",
                            "color": "white",
                            "border": "none",
                            "borderRadius": "6px",
                            "fontSize": "16px",
                            "cursor": "pointer",
                            "boxSizing": "border-box"
                        }
                    ),

                    html.Div(id="signup-output", style={"marginTop": "15px", "color": "green"}),

                    html.Div(
                        [
                            html.Span("Already have an account? "),
                            html.A("Login", href="/", style={"color": "#1E90FF", "fontWeight": "bold"})
                        ],
                        style={"marginTop": "20px", "fontSize": "14px"}
                    )
                ]
            )
        ]
    )


@dash.callback(
    Output("signup-password", "type"),
    Input("toggle-password", "n_clicks"),
    prevent_initial_call=True
)

def toggle_password(n):
    if n % 2 == 1:
        return "text"
    return "password"


@dash.callback(
    Output("signup-output", "children"),
    Input("signup-btn", "n_clicks"),
    State("signup-username", "value"),
    State("signup-email", "value"),
    State("signup-password", "value"),
    State("signup-role", "value"),
    State("signup-consent", "value")
)
def signup(n, username, email, password, role, consent):

    if not n:
        return ""

    if not all([username, email, password]):
        return "Please fill all required fields!"

    if not role:
        role = "Regular User"

 
    if consent != ["yes"]:
        return "You must agree to GDPR data consent before signing up."

    hashed_pw = hash_password(password)
    file_path = "data/user_data.csv"

    file_exists = os.path.isfile(file_path)

    with open(file_path, "a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["username", "email", "role", "password", "consent"])

        writer.writerow([username, email, role, hashed_pw, "yes"])

    return "Account Created Successfully! Please Login."


def signup(n, username, email, password, role):
    if not n:
        return ""

    if not all([username, email, password, role]):
        return "Please fill all fields!"

    hashed_pw = hash_password(password)

    file_path = "data/user_data.csv"

    file_exists = os.path.isfile(file_path)

    with open(file_path, "a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["username", "email", "role", "password"])

        writer.writerow([username, email, role, hashed_pw])

    return "Account Created Successfully! Please Login."
