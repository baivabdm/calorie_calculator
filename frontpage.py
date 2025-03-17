from dash import html
import dash_bootstrap_components as dbc
import planner
import history
import db_management as dbm

frontPageItems = [
    html.Div(
        children=[
            html.H1(children='Calorie Calculator and Optimizer', id="app-name"),
            ],
        id="banner"
    ),
    html.Div(
        id="tab-div",
        children=[
                    dbc.Tabs(
                             children=[
                                 dbc.Tab(label="Planner", id="tab-planner", children=planner.contents),
                                 dbc.Tab(label="History", id="tab-history", children=history.contents),
                                 dbc.Tab(label="DB Management", id="tab-db-management", children=dbm.contents, disabled=False)
                             ],
                             id="tab-group", active_tab = "tab-0",
                             )
                ]
    )
    ]