from dash import html
import dash_bootstrap_components as dbc
import planner

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
                                 dbc.Tab(label="History", id="tab-history", children=[]),
                                 dbc.Tab(label="DB Management", id="tab-db-management", children=[])
                             ],
                             id="tab-group", active_tab = "tab-0",
                             )
                ]
    )
    ]