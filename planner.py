from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
from numpy import array
from datetime import datetime as dt, date
from db_utils import DbManagement


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
                             dbc.Col(children=[
                                 dbc.Row(id="planner-output-col-row-1"),
                                 dbc.Row(id="planner-output-col-row-2"),
                                 dbc.Row(id="planner-output-col-row-3"),
                                 dbc.Row(id="planner-output-col-row-4"),
                             ], id="planner-output-col", align="left")
                         ])
             ]),
    html.Div(id="submit-div",
             children=[
                 html.Button(children="Submit", id='submit', n_clicks=0, className="planner-btn", style = dict(display='none'))
             ])
]

def create_weight_input_widget():
    dbManager = DbManagement()
    userList = dbManager.get_user_list()
    dbManager.close_connection()
    
    userLabel = html.Label("User", "user-label")
    userDropDowm = dcc.Dropdown(userList, placeholder="Select User", value="guest_user", clearable=False,
                                id="user-dropdown", className="user-drop")
    today = dt.today().date()
    dateLabel = html.Label("Plan Date", "date-label")
    dateInput =  dcc.DatePickerSingle(
        id='plan-date-picker',
        min_date_allowed=date(1900, 1, 1),
        max_date_allowed=today,
        initial_visible_month=today,
        date=today
    )
    ageLabel = html.Label("Age(Yrs)", "age-label")
    ageInput = dcc.Input(placeholder="Age", type="number", id=f"age-input", className="age-input")
    heightLabel = html.Label("Height(cm)", "height-label")
    heightInput = dcc.Input(placeholder="Height", type="number", id=f"height-input", className="height-input")
    genderLabel = html.Label("Gender", "gender-label")
    genderRadio = dcc.RadioItems(["Male", "Female"], "Male", inline=True, id="gender-input")
    weightLabel = html.Label("Current Weight(Kg)", "weight-label")
    weightInput = dcc.Input(placeholder="Weight", type="number", id=f"weight-input", className="weight-input")
    updateUserStatsButton = html.Button(children="Update", id='update', n_clicks=0, className="planner-btn")
    row0 = dbc.Row(children=[userLabel, userDropDowm], id=f"user-row-1", className="user-row")
    row1 = dbc.Row(children=[dateLabel, dateInput], id=f"date-row-1", className="date-row")
    row2 = dbc.Row(children=[weightLabel, weightInput], id=f"weight-row-1", className="weight-row")
    row3 = dbc.Row(children=[ageLabel, ageInput], id=f"age-row-1", className="age-row")
    row4 = dbc.Row(children=[heightLabel, heightInput], id=f"height-row-1", className="height-row")
    row5 = dbc.Row(children=[genderLabel, genderRadio], id=f"gender-row-1", className="gender-row")
    row6 = dbc.Row(children=[updateUserStatsButton], id="update-row-1", className="update-row")
    return [row0, row1, row2, row3, row4, row5, row6]


def create_form_row(id_count=1):
    dropDowm = dcc.Dropdown(food, placeholder="Select Food", id={"type": "form-dropdown", "index": f"form-dropdown-{id_count}"}, className="form-dropdown")
    input = dcc.Input(placeholder="Quantity", type="number",id={"type": "form-input", "index": f"form-input-{id_count}"}, className="form-input")
    deleteButton = html.Button(children='Delete', id={"type": "form-delete-button", "index": f'form-delete-{id_count}'}, n_clicks=0, className="form-delete")
    row = dbc.Row(children=[dropDowm, input, deleteButton], id=f"form-row-{id_count}", className="form-row")
    return row

def create_add_item_button():
    addItem = html.Button(children='Add Item', id=f'add-item', n_clicks=1, className="planner-btn")
    return addItem

def calculate_requirements(weight, age, height, gender):
    if gender.lower() == "male":
        bmr = round(10*weight + 6.25*height -5*age + 5, 2) #10W + 6.25H - 5A + 5
    else:
        bmr = round(10*weight + 6.25*height -5*age + 161, 2) #10W + 6.25H - 5A - 161

    carbs = round(0.55*bmr/4,2)
    protein = round(0.8*weight,2)
    fat = round(25,2)

    heading = dbc.Row(html.H3("Requirements:", id="requirements-heading"))
    bmrRow = dbc.Row(html.H5(f"BMR:\t{bmr} Cal"))
    carbsRow = dbc.Row(html.H5(f"Carbs:\t{carbs} gms"))
    proteinRow = dbc.Row(html.H5(f"Protein:\t{protein} gms"))
    fatRow = dbc.Row(html.H5(f"Fat:\t{fat} gms"))

    finalRow = dbc.Row([heading, bmrRow, carbsRow, proteinRow, fatRow])

    return finalRow, bmr


def calculate_diet_kpis(form_contents):
    carbs = 0
    protein = 0
    fat = 0
    calories = 0

    nutrients_df = pd.DataFrame()

    for k,v in form_contents.items():
        row = db[db["food"]==k].to_dict("records")[0]
        unit = row["unit"]
        divider = 100
        if unit.lower() == "qty":
            divider = 1

        v_sum = array(v).sum()
        carbs_temp = round(v_sum*row["carbs"]/divider,2)
        protein_temp = round(v_sum*row["protein"]/divider,2)
        fat_temp = round(v_sum*row["fat"]/divider,2)
        calories_temp = round(v_sum*row["calorie"]/divider,2)

        carbs = round(carbs + carbs_temp,2)
        protein = round(protein +protein_temp,2)
        fat = round(fat + fat_temp,2)
        calories = round(calories + calories_temp,2)

        temp_df = pd.DataFrame(
            {"food":[k],
             "qty":[v_sum],
             "unit":[unit],
             "calorie":[calories_temp],
             "carbs":[carbs_temp],
             "protein":[protein_temp],
             "fat":[fat_temp],

             }
        )
        nutrients_df = pd.concat([nutrients_df, temp_df])

    caloriesRow = dbc.Row(html.H5(f"Calories:\t{calories} Cal"))
    heading = dbc.Row(html.H3("Plan Provides:", id="plan-heading"))
    carbsRow = dbc.Row(html.H5(f"Carbs:\t{carbs} gms"))
    proteinRow = dbc.Row(html.H5(f"Protein:\t{protein} gms"))
    fatRow = dbc.Row(html.H5(f"Fat:\t{fat} gms"))
    nutrients_df.reset_index(drop=True)

    finalRow = dbc.Row([heading, caloriesRow, carbsRow, proteinRow, fatRow])

    return finalRow, calories, nutrients_df