from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_daq as daq
import pandas as pd
from numpy import array
from datetime import datetime as dt, date
from db_utils import DbManagement
import plotly.express as px

dbManager = DbManagement()
userList = dbManager.get_user_list()
dbManager.close_connection()
today = dt.today().date()

histBmrLabel = html.Label("BMR:", "hist-bmr-label", className="hist-control-label")
histBmrToggle = daq.BooleanSwitch(id='hist-bmr-switch', on=True, className="hist-toggle")

histCalLabel = html.Label("Calories:", "hist-cal-label", className="hist-control-label")
histCalToggle = daq.BooleanSwitch(id='hist-cal-switch', on=True, className="hist-toggle")

histCarbLabel = html.Label("Carbs:", "hist-carb-label", className="hist-control-label")
histCarbToggle = daq.BooleanSwitch(id='hist-carb-switch', on=True, className="hist-toggle")

histProtLabel = html.Label("Protein:", "hist-prot-label", className="hist-control-label")
histProtToggle = daq.BooleanSwitch(id='hist-prot-switch', on=True, className="hist-toggle")

histFatLabel = html.Label("Fat:", "hist-fat-label", className="hist-control-label")
histFatToggle = daq.BooleanSwitch(id='hist-fat-switch', on=True, className="hist-toggle")

histWeightLabel = html.Label("Weight:", "hist-weight-label", className="hist-control-label")
histWeightToggle = daq.BooleanSwitch(id='hist-weight-switch', on=True, className="hist-toggle")

calDeltaLabel = html.Label("Calorie Delta:", "hist-calDelta-label", className="hist-control-label")
calDeltaToggle = daq.BooleanSwitch(id='hist-calDelta-switch', on=True, className="hist-toggle")

refreshBtn = html.Button(children="Refresh", id='hist-refresh', n_clicks=0, className="planner-btn")
selAllBtn = html.Button(children="Select All", id='hist-sel-all', n_clicks=0, className="planner-btn")
selNoneBtn = html.Button(children="Select None", id='hist-sel-none', n_clicks=0, className="planner-btn")


contents = [
    dbc.Row(id="history-row", className="history-master-row",
            children=[
                dbc.Col(id="history-input", className="history-input-col",
                        children=[
                            dcc.Dropdown(userList, placeholder="Select User", value="guest_user", clearable=False,
                                id="history-user-dropdown", className="user-drop"),
                            dcc.DatePickerRange(
                                    id='hist-date-picker-range',
                                    min_date_allowed=date(1900, 1, 1),
                                    max_date_allowed=today,
                                    initial_visible_month=today,
                                    clearable=True
                                ),
                            dbc.Row(children=[refreshBtn, selAllBtn,selNoneBtn ], id="hist-button-row", className="history-control-row"),
                            html.Div(id="control-panel",
                                    children=[
                                        dbc.Row(children=[histBmrLabel, histBmrToggle], id="hist-brm-row", className="history-control-row"),
                                        dbc.Row(children=[histCalLabel, histCalToggle], id="hist-cal-row", className="history-control-row"),
                                        dbc.Row(children=[histCarbLabel, histCarbToggle], id="hist-carb-row", className="history-control-row"),
                                        dbc.Row(children=[histProtLabel, histProtToggle], id="hist-prot-row", className="history-control-row"),
                                        dbc.Row(children=[histFatLabel, histFatToggle], id="hist-fat-row", className="history-control-row"),
                                        dbc.Row(children=[histWeightLabel, histWeightToggle], id="hist-weight-row", className="history-control-row"),
                                        dbc.Row(children=[calDeltaLabel, calDeltaToggle], id="hist-delta-row", className="history-control-row")
                                    ])
                        ]),
                dbc.Col(id="history-output", className="history-output-col",
                        children=[
                            dbc.Row(children=[], id="hist-graph-row", className="history-graph-row"),
                            dbc.Row(children=[], id="hist-table-row", className="history-table-row")
                        ])
            ])
]


def generate_chart(userHistory, chartType = "overall", filter = {}):
    datefoodlevel, datelevel, datelevelmelt = userHistory
    datefoodlevel = pd.DataFrame(datefoodlevel)
    datelevel = pd.DataFrame(datelevel)
    datelevelmelt = pd.DataFrame(datelevelmelt)

    for k,v in filter.items():
        if not v:
            datelevelmelt = datelevelmelt[datelevelmelt["kpi"] !=k]

    if chartType.lower() == "overall":
        fig = px.line(datelevelmelt, x="date", y="value", color='kpi')
        return fig, datelevel