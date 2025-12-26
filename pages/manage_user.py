import os
import csv
import hashlib
import dash
from dash import html, dcc, Input, Output, State, callback
from dash.dependencies import ALL
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

BLUE = "#0B63C5"
WHITE = "#FFFFFF"
LIGHT = "#F4F9FF"
CSV_PATH = "data/user_data.csv"


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def read_users():
    users = []

    if not os.path.exists(CSV_PATH):
        return users

    with open(CSV_PATH, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            users.append({
                "username": row.get("username", ""),
                "email": row.get("email", ""),
                "role": row.get("role", ""),
                "password": row.get("password", "")
            })
    return users


def save_users(users):
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["username", "email", "role", "password"]
        )
        writer.writeheader()
        for u in users:
            row = {
                "username": u.get("username", ""),
                "email": u.get("email", ""),
                "role": u.get("role", ""),
                "password": u.get("password", "")
            }
            writer.writerow(row)



def generate_user_table(users):
    header = html.Tr(
        [html.Th(col, className="p-2 border-bottom") for col in ["username", "email", "role"]] +
        [html.Th("Actions", className="p-2 border-bottom")]
    )

    rows = []
    for i, user in enumerate(users):
        rows.append(
            html.Tr(
                [
                    html.Td(user["username"], className="p-2"),
                    html.Td(user["email"], className="p-2"),
                    html.Td(user["role"], className="p-2"),
                    html.Td([
                        dbc.Button(
                            "Edit",
                            id={"type": "edit-btn", "index": i},
                            color="warning",
                            size="sm",
                            className="me-1"
                        ),
                        dbc.Button(
                            "Delete",
                            id={"type": "delete-btn", "index": i},
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



def layout():
    users = read_users()

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
                            dbc.Col(dcc.Input(id="input-username", placeholder="Username", className="form-control"), md=2),
                            dbc.Col(dcc.Input(id="input-email", type="email", placeholder="Email", className="form-control"), md=2),
                            dbc.Col(
                                dcc.Dropdown(
                                    id="input-role",
                                    options=[{"label": r, "value": r} for r in ["student", "staff", "admin", "visitor"]],
                                    placeholder="Select role"
                                ),
                                md=2
                            ),
                            dbc.Col(dcc.Input(id="input-password", type="password", placeholder="Password", className="form-control"), md=2),
                            dbc.Col(dbc.Button("Add", id="btn-add-user", color="primary"), width="auto"),
                            dbc.Col(dbc.Button("Reset", id="btn-cancel-edit", color="secondary"), width="auto"),
                        ]
                    ),
                    html.Div(id="add-user-msg", className="mt-2")
                ]
            ),

            dbc.Row(
                className="mb-3",
                children=[
                    dbc.Col(
                        dcc.Input(id="search-input", placeholder="Search users...", className="form-control"),
                        md=3
                    )
                ]
            ),

            dbc.Card(
                className="p-3 shadow-sm",
                children=[
                    html.Div(id="user-table-div", children=generate_user_table(users))
                ]
            )
        ]
    )


@callback(
    Output("user-table-div", "children", allow_duplicate=True),
    Input({"type": "delete-btn", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def delete_user(clicks):
    if not any(clicks):
        raise PreventUpdate

    index = dash.callback_context.triggered_id["index"]
    users = read_users()
    users.pop(index)
    save_users(users)

    return generate_user_table(users)

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
        raise PreventUpdate

    index = dash.callback_context.triggered_id["index"]
    user = read_users()[index]

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
    if not all([username, email, role, password]):
        return dash.no_update, "Please fill all required fields."

    users = read_users()

    if edit_index is not None:
        users[edit_index]["username"] = username
        users[edit_index]["email"] = email
        users[edit_index]["role"] = role
        if password:
            users[edit_index]["password"] = hash_password(password)
        msg = "User updated."
    else:
        users.append({
            "username": username,
            "email": email,
            "role": role,
            "password": hash_password(password)
        })
        msg = f"User '{username}' added."

    save_users(users)
    return generate_user_table(users), msg



@callback(
    Output("user-table-div", "children", allow_duplicate=True),
    Input("search-input", "value"),
    prevent_initial_call=True
)
def search_users(text):
    users = read_users()

    if not text:
        return generate_user_table(users)

    t = text.lower()
    filtered = [
        u for u in users
        if t in str(u).lower()
    ]

    return generate_user_table(filtered)
