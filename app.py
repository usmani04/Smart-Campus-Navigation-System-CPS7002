from dash import Dash, page_container

app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True
)

app.layout = page_container

if __name__ == "__main__":
    app.run(debug=True, port=8050)
