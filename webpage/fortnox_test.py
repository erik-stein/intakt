import os

import dash
import dash_bootstrap_components as dbc
import flask
from dash import html
from dash.dependencies import Input, Output

CLIENT_ID = os.environ.get("FORTNOX_CLIENT_ID")
REDIRECT_URI = "http://localhost:6060/auth"

app = dash.Dash(
    name="intakt",
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    server=flask.Flask(__name__),
)

app.layout = html.Div(
    [
        html.A(
            dbc.Button("Click me", id="btn"),
            href=f"https://apps.fortnox.se/oauth-v1/auth?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=bookkeeping&state=somestate123&access_type=offline&response_type=code",
        ),
        html.P(id="btn-clicked"),
    ]
)


@app.callback(
    Output("btn-clicked", "children"),
    Input("btn", "n_clicks"),
    prevent_initial_call=True,
)
def btn_clicked(n_clicks):
    return f"Clicked {n_clicks} time{'s' if n_clicks > 1 else ''}"


app.run(
    debug=True,
    host="localhost",
    port=6061,
)
