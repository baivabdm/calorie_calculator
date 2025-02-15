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
                    dbc.Tabs(id="tab-group", active_tab="tab-planner",
                             children=[
                                 dbc.Tab(label="Planner", id="tab-planner"),
                                 dbc.Tab(label="History", id="tab-history"),
                                 dbc.Tab(label="DB Management", id="tab-db-management")
                             ]
                             )
                ]
    ),
    html.Div(
        id="content-div",
        children = planner.contents
    )
    ]