import os
import hashlib
import dash
import pandas as pd
from dash import html, dcc, Input, Output, State, callback
from dash.dependencies import ALL
import dash_bootstrap_components as dbc

BLUE = "#0B63C5"
WHITE = "#FFFFFF"
LIGHT = "#F4F9FF"
CSV_PATH = "data/user_data.csv"


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# -------------------
# Table Buttons Classes
# -------------------
def btn_class(color="primary"):
    return f"btn btn-sm btn-{color} me-1 cursor-pointer"


# -------------------
# Generate User Table
# -------------------
def generate_user_table(df):
    header = html.Tr(
        [html.Th(col, className="p-2 border-bottom") for col in df.columns] +
        [html.Th("Actions", className="p-2 border-bottom")]
    )

    rows = []
    for i in range(len(df)):
        rows.append(
            html.Tr(
                [html.Td(df.iloc[i][col], className="p-2") for col in df.columns] +
                [
                    html.Td([
                        dbc.Button(
                            "Edit",
                            id={"type": "edit-btn", "index": i},
                            n_clicks=0,
                            color="warning",
                            size="sm",
                            className="me-1"
                        ),
                        dbc.Button(
                            "Delete",
                            id={"type": "delete-btn", "index": i},
                            n_clicks=0,
                            color="danger",
                            size="sm"
                        )
                    ])
                ],
                className="bg-light" if i % 2 == 0 else ""
            )
        )

    return dbc.Table(
        [header] + rows,
        bordered=False,
        hover=True,
        responsive=True,
        striped=False,
        className="shadow-sm rounded"
    )


# -------------------
# Layout
# -------------------
def layout():
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH, usecols=["username", "email", "role", "password"])
    else:
        df = pd.DataFrame(columns=["username", "email", "role", "password"])

    df_display = df.drop(columns=["password"])

    return dbc.Container(
        fluid=True,
        className="p-4",
        style={"backgroundColor": LIGHT, "minHeight": "100vh"},
        children=[
            html.H2("👥 Manage Users", className="text-primary mb-4"),

            dbc.Card(
                className="p-3 mb-4 shadow-sm",
                children=[
                    html.H4("Add / Edit User"),
                    dcc.Store(id="edit-index"),

                    dbc.Row(
                        className="g-2",
                        children=[
                            dbc.Col(dcc.Input(id="input-username", placeholder="Username", className="form-control"), className="col-md-2"),
                            dbc.Col(dcc.Input(id="input-email", type="email", placeholder="Email", className="form-control"), className="col-md-2"),
                            dbc.Col(dcc.Dropdown(
                                id="input-role",
                                options=[{"label": r, "value": r} for r in ["student", "staff", "admin", "visitor"]],
                                placeholder="Select role",
                                className=""
                            ), className="col-md-2"),
                            dbc.Col(dcc.Input(id="input-password", type="password", placeholder="Password", className="form-control"), className="col-md-2"),
                            dbc.Col(dbc.Button("Add", id="btn-add-user", color="primary", className="me-1"), width="auto"),
                            dbc.Col(dbc.Button("Reset", id="btn-cancel-edit", color="secondary"), width="auto"),
                        ]
                    ),
                    html.Div(id="add-user-msg", className="mt-2")
                ]
            ),

            dbc.Row(
                className="mb-3 g-2",
                children=[
                    dbc.Col(dcc.Input(id="search-input", placeholder="Search users...", className="form-control", type="text"), width="auto")
                ]
            ),

            dbc.Card(
                className="p-3 mb-4 shadow-sm",
                children=[
                    html.Div(id="user-table-div", children=generate_user_table(df_display))
                ]
            ),

        ]
    )


# -------------------
# Callbacks
# -------------------
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
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.layout = layout()
    app.run_server(debug=True)
