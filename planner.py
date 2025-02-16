from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd

db = pd.read_excel("./assets/food_calorie_db.xlsx")
food = list(db["food"])

contents = [
    html.Div(id="button-div",
             children=[
                 html.Button(children='New Plan', id='new-plan', n_clicks=0, className="planner-btn"),
                 html.Button(children='Reset', id='reset', n_clicks=0, className="planner-btn"),
             ]
             ),
    html.Div(id="planner-area",
             children=[
                 dbc.Row(id="planner-row",
                         children=[
                             dbc.Col(children=[
                                 dbc.Row(id="planner-form-col-row-1"),
                                 dbc.Row(id="planner-form-col-row-2", children=[]),
                                 dbc.Row(id="planner-form-col-row-3")
                             ],id="planner-form-col", align="left"),
                             dbc.Col(id="planner-output-col")
                         ])
             ]),
    html.Div(id="submit-div",
             children=[
                 html.Button(children="Submit", id='submit', n_clicks=0, className="planner-btn", style = dict(display='none'))
             ])
]

def create_weight_input_widget():
    label = html.Label("Current Weight(Kg)", "weight-label")
    input = dcc.Input(placeholder="Weight", type="number", id=f"weight-input", className="weight-input")
    row = dbc.Row(children=[label, input], id=f"weight-row-1", className="weight-row")
    return row


def create_form_row(id_count=1):
    dropDowm = dcc.Dropdown(food, placeholder="Select Food", id=f"form-dropdown-{id_count}", className="form-dropdown")
    input = dcc.Input(placeholder="Quantity", type="number",id=f"form-input-{id_count}", className="form-input")
    deleteButton = html.Button(children='Delete', id={"type": "form-delete-button", "index": f'form-delete-{id_count}'}, n_clicks=0, className="form-delete")
    row = dbc.Row(children=[dropDowm, input, deleteButton], id=f"form-row-{id_count}", className="form-row")
    return row

def create_add_item_button():
    addItem = html.Button(children='Add Item', id=f'add-item', n_clicks=1, className="planner-btn")
    return addItem
