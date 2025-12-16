import dash
from dash import html, dcc

app = dash.Dash(__name__, use_pages=True, suppress_callback_exceptions=True)

server = app.server

app.layout = html.Div(
    [
        dcc.Location(id="url"),
        dash.page_container
    ]
)

if __name__ == "__main__":
    app.run(debug=True)  
