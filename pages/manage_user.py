import os
import hashlib
import dash
import pandas as pd
from dash import html, dcc, Input, Output, State, callback
from dash.dependencies import ALL

BLUE = "#0B63C5"
WHITE = "#FFFFFF"
LIGHT = "#F4F9FF"
CSV_PATH = "data/user_data.csv"


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def table_header_style():
    return {
        "padding": "12px",
        "borderBottom": "2px solid #ccc",
        "textAlign": "left",
        "backgroundColor": LIGHT
    }


def cell_style():
    return {
        "padding": "10px 14px",
        "borderBottom": "1px solid #eee"
    }


def edit_btn_style():
    return {
        "backgroundColor": "#FFA500",
        "color": "white",
        "border": "none",
        "padding": "4px 10px",
        "marginRight": "5px",
        "borderRadius": "5px",
        "cursor": "pointer"
    }


def delete_btn_style():
    return {
        "backgroundColor": "red",
        "color": "white",
        "border": "none",
        "padding": "4px 10px",
        "borderRadius": "5px",
        "cursor": "pointer"
    }


def generate_user_table(df):
    header = html.Tr(
        [html.Th(col, style=table_header_style()) for col in df.columns] +
        [html.Th("Actions", style=table_header_style())]
    )

    rows = []
    for i in range(len(df)):
        rows.append(
            html.Tr(
                [html.Td(df.iloc[i][col], style=cell_style()) for col in df.columns] +
                [
                    html.Td([
                        html.Button(
                            "Edit",
                            id={"type": "edit-btn", "index": i},
                            n_clicks=0,
                            style=edit_btn_style()
                        ),
                        html.Button(
                            "Delete",
                            id={"type": "delete-btn", "index": i},
                            n_clicks=0,
                            style=delete_btn_style()
                        )
                    ])
                ],
                style={"backgroundColor": "#FAFAFA" if i % 2 == 0 else WHITE}
            )
        )

    return html.Table(
        [header] + rows,
        style={
            "width": "100%",
            "borderCollapse": "collapse",
            "borderRadius": "10px",
            "overflow": "hidden",
            "boxShadow": "0 2px 8px rgba(0,0,0,0.1)"
        }
    )


def layout():
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(
            CSV_PATH,
            usecols=["username", "email", "role", "password"]
        )
    else:
        df = pd.DataFrame(columns=["username", "email", "role", "password"])

    df_display = df.drop(columns=["password"])

    input_style = {
        "flex": "1",
        "minWidth": "200px",
        "padding": "10px",
        "border": f"2px solid {BLUE}",
        "borderRadius": "6px"
    }

    return html.Div(
        style={"padding": "30px", "backgroundColor": LIGHT, "minHeight": "100vh"},
        children=[
            html.H2("👥 Manage Users", style={"color": BLUE, "marginBottom": "20px"}),

            html.Div(
                style={
                    "marginBottom": "30px",
                    "padding": "20px",
                    "backgroundColor": WHITE,
                    "borderRadius": "10px",
                    "boxShadow": "0 2px 8px rgba(0,0,0,0.1)"
                },
                children=[
                    html.H4("Add / Edit User"),
                    dcc.Store(id="edit-index"),

                    html.Div(
                        style={"display": "flex", "gap": "10px", "flexWrap": "wrap"},
                        children=[
                            dcc.Input(id="input-username", placeholder="Username", style=input_style),
                            dcc.Input(id="input-email", type="email", placeholder="Email", style=input_style),
                            dcc.Dropdown(
                                id="input-role",
                                options=[
                                    {"label": r, "value": r}
                                    for r in ["student", "staff", "admin", "visitor"]
                                ],
                                placeholder="Select role",
                                style={"flex": "1", "minWidth": "200px"}
                            ),
                            dcc.Input(id="input-password", type="password", placeholder="Password", style=input_style),

                            html.Button(
                                "Add",
                                id="btn-add-user",
                                n_clicks=0,
                                style={
                                    "backgroundColor": BLUE,
                                    "color": WHITE,
                                    "border": "none",
                                    "padding": "10px 15px",
                                    "borderRadius": "6px"
                                }
                            ),
                            html.Button(
                                "Reset",
                                id="btn-cancel-edit",
                                n_clicks=0,
                                style={
                                    "backgroundColor": "#777",
                                    "color": WHITE,
                                    "border": "none",
                                    "padding": "10px 15px",
                                    "borderRadius": "6px"
                                }
                            ),
                        ]
                    ),

                    html.Div(id="add-user-msg", style={"marginTop": "10px"})
                ]
            ),

            dcc.Input(
                id="search-input",
                placeholder="Search users...",
                style={
                    "padding": "10px",
                    "width": "300px",
                    "border": f"2px solid {BLUE}",
                    "borderRadius": "6px",
                    "marginBottom": "20px"
                }
            ),

            html.Div(id="user-table-div", children=generate_user_table(df_display))
        ]
    )


@callback(
    Output("user-table-div", "children", allow_duplicate=True),
    Input({"type": "delete-btn", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def delete_user(clicks):
    if not any(clicks):
        raise dash.exceptions.PreventUpdate

    index = clicks.index(max(clicks))
    df = pd.read_csv(CSV_PATH, usecols=["username", "email", "role", "password"])
    df = df.drop(index).reset_index(drop=True)
    df.to_csv(CSV_PATH, index=False)

    return generate_user_table(df.drop(columns=["password"]))


@callback(
    Output("input-username", "value", allow_duplicate=True),
    Output("input-email", "value", allow_duplicate=True),
    Output("input-role", "value", allow_duplicate=True),
    Output("input-password", "value", allow_duplicate=True),
    Output("btn-add-user", "children", allow_duplicate=True),
    Output("edit-index", "data", allow_duplicate=True),
    Input({"type": "edit-btn", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def load_user(clicks):
    if not any(clicks):
        raise dash.exceptions.PreventUpdate

    index = clicks.index(max(clicks))
    df = pd.read_csv(CSV_PATH, usecols=["username", "email", "role", "password"])
    user = df.iloc[index]

    return user["username"], user["email"], user["role"], "", "Update", index


@callback(
    Output("input-username", "value", allow_duplicate=True),
    Output("input-email", "value", allow_duplicate=True),
    Output("input-role", "value", allow_duplicate=True),
    Output("input-password", "value", allow_duplicate=True),
    Output("btn-add-user", "children", allow_duplicate=True),
    Output("edit-index", "data", allow_duplicate=True),
    Output("add-user-msg", "children", allow_duplicate=True),
    Input("btn-cancel-edit", "n_clicks"),
    prevent_initial_call=True
)
def cancel_edit(_):
    return "", "", None, "", "Add", None, ""


@callback(
    Output("user-table-div", "children", allow_duplicate=True),
    Output("add-user-msg", "children"),
    Input("btn-add-user", "n_clicks"),
    State("input-username", "value"),
    State("input-email", "value"),
    State("input-role", "value"),
    State("input-password", "value"),
    State("edit-index", "data"),
    prevent_initial_call=True
)
def save_user(_, username, email, role, password, edit_index):
    if not all([username, email, role]):
        return dash.no_update, "Please fill all required fields."

    df = pd.read_csv(CSV_PATH, usecols=["username", "email", "role", "password"])

    if edit_index is not None:
        df.loc[edit_index, ["username", "email", "role"]] = [username, email, role]
        if password:
            df.loc[edit_index, "password"] = hash_password(password)
        message = "User updated."
    else:
        df = pd.concat([
            df,
            pd.DataFrame([{
                "username": username,
                "email": email,
                "role": role,
                "password": hash_password(password)
            }])
        ], ignore_index=True)
        message = f"User '{username}' added."

    df.to_csv(CSV_PATH, index=False)
    return generate_user_table(df.drop(columns=["password"])), message


@callback(
    Output("user-table-div", "children", allow_duplicate=True),
    Input("search-input", "value"),
    prevent_initial_call=True
)
def search_users(text):
    df = pd.read_csv(CSV_PATH, usecols=["username", "email", "role", "password"])
    df_display = df.drop(columns=["password"])

    if not text:
        return generate_user_table(df_display)

    text = text.lower()
    filtered = df_display[
        df_display.apply(lambda r: r.astype(str).str.lower().str.contains(text).any(), axis=1)
    ]

    return generate_user_table(filtered)


if __name__ == "__main__":
    app = dash.Dash(__name__)
    app.layout = layout()
    app.run_server(debug=True)
