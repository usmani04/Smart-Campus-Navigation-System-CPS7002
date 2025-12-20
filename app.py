import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

app = dash.Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP]  
)

server = app.server

app.layout = dbc.Container(
    [
        dcc.Location(id="url"),
        dash.page_container
    ],
    fluid=True 
)

if __name__ == "__main__":
    app.run(debug=True)