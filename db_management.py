from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime as dt, date
from db_utils import DbManagement


contents = [
    html.Div(id="db-manage-button-div",
             children=[
                 html.Button(children='New User', id='new-user', n_clicks=0, className="planner-btn"),
                 html.Button(children='Modify User', id='modify-user', n_clicks=0, className="planner-btn"),
                 html.Button(children='Backup DB', id='backup-db', n_clicks=0, className="planner-btn"),
                 html.Button(children='Restore DB', id='restore-db', n_clicks=0, className="planner-btn"),
                ]
             ),

    html.Div(id="backup-restore-message-div"),

    html.Div(id="db-manage-form-div",
             children=[
                 dbc.Row(id="db-manage-username", className="new-manage-form-class"),
                 html.Div(id="db-manage-name", className="new-manage-form-class"),
                 html.Div(id="db-manage-gender", className="new-manage-form-class"),
                 dbc.Row(id="db-manage-dob", className="new-manage-form-class"),
                 html.Div(id="db-manage-weight", className="new-manage-form-class"),
                 html.Div(id="db-manage-height", className="new-manage-form-class"),
                 html.Div(id="db-manage-save", className="new-manage-form-class"),
                 html.Div(id="db-manage-toast", className="new-manage-form-class")
                ]
             )
]

def create_new_or_modify_form(formType="new"):
    dbManager = DbManagement()
    userList = dbManager.get_user_list()
    dbManager.close_connection()

    usernameInput = dcc.Input(placeholder="username", type="text", id=f"username-manage-input")
    usernameAvailability = html.Label("", id="user-manage-availability")
    usernameSelect = dcc.Dropdown(userList, placeholder="Select User", value="guest_user", clearable=False,
                                  id="username-manage-dropdown", className="user-drop")
    nameInput = dcc.Input(placeholder="Name", type="text", id=f"name-manage-input")
    genderRadio = dcc.RadioItems(["Male", "Female"], "Male", inline=True, id="gender-manage-input")

    today = dt.today().date()
    dobLabel = html.Label("Date of birth", id="dob-manage-label")
    dateInput = dcc.DatePickerSingle(
        id='dob-manage-picker',
        min_date_allowed=date(1900, 1, 1),
        max_date_allowed=today,
        initial_visible_month=today,
        date=today
    )
    weightInput = dcc.Input(placeholder="Weight", type="text", id=f"weight-manage-input")
    heightInput = dcc.Input(placeholder="Height(in cm)", type="number", id=f"height-manage-input")

    if formType.lower() == "new":
        saveButton = html.Button(children='Save', id='save-new-user', n_clicks=0, className="planner-btn"),
        returnObj = [[usernameInput, usernameAvailability], nameInput, genderRadio, [dobLabel, dateInput], weightInput,
                     heightInput, saveButton]
    else:
        saveButton = html.Button(children='Save', id='save-modified-user', n_clicks=0, className="planner-btn"),
        returnObj = [usernameSelect, nameInput, genderRadio, [dobLabel, dateInput], weightInput,
                     heightInput, saveButton]

    return returnObj

def backup_restore_toast(filepath, toastType = "Backup"):
    toastMessage = dbc.Toast(
        [html.P(f"Database Restored from {filepath}")],
        id="auto-toast",
        header="Restored",
        icon="primary",
        duration=4000,
        is_open=True,
        )
    
    if toastType.lower() == "backup":
        toastMessage = dbc.Toast(
        [html.P(f"Database Backed up at {filepath}")],
        id="auto-toast",
        header="Backed up",
        icon="primary",
        duration=4000,
        is_open=True,
        )

    return toastMessage