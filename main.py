import pandas as pd
from dash import Dash, html, dcc, callback, Output, Input, ALL, State, dash_table
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import frontpage as fp
import planner as pl
import history as hst
import db_management as dbm
import webbrowser as wb
from threading import Timer
import threading as th
import numpy as np
from db_utils import DbManagement
from datetime import date
from PyQt6.QtWidgets import QApplication, QFileDialog
import shutil


def open_file_dialog(openType="Folder"):
    app = QApplication([])

    if openType.lower() == "folder":
        directory = QFileDialog.getExistingDirectory(None, "Select backup location")
    else:
        directory = QFileDialog.getOpenFileName(None, "Select backup database to restore", filter = "Database (*.db)")
    app.quit()
    return directory

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Calorie Calculator and Optimizer"
app.layout = [
    dcc.Store(id="reqd_bmr", data=None),
    dcc.Store(id="diet-cal", data=None),
    dcc.Store(id="dummy-store",data=[]),
    dcc.Store(id="food-level-history"),
    dcc.Store(id="date-level-history"),
    dcc.Store(id="date-level-history-long"),
    dcc.Store(id="new-user-form-state", data=0),
    *fp.frontPageItems]


@callback(
    Output("planner-form-col-row-1", "children", allow_duplicate=True),
    Output("planner-output-col-row-1", "children", allow_duplicate=True),
    Output("new-plan", "n_clicks"),
    Output("reset", "n_clicks"),
    Output("planner-form-col-row-2", "children", allow_duplicate=True),
    Output("planner-form-col-row-3", "children"),
    Output("planner-output-col-row-2", "children", allow_duplicate=True),
    Output("planner-output-col-row-3", "children", allow_duplicate=True),
    Output("planner-output-col-row-4", "children", allow_duplicate=True),
    Output("submit", "style"),
    Input("new-plan", "n_clicks"),
    Input("reset", "n_clicks"),
    prevent_initial_call=True
)
def new_plan(n_clicks_plan,n_clicks_reset,):
    if n_clicks_plan == 1:
        return [pl.create_weight_input_widget()+[pl.create_form_row()], [], 2, 0, [], pl.create_add_item_button(), [], [], [], {}]

    elif n_clicks_reset == 1:
        return [[], [], 0, 0, [], [], [], [], [], dict(display='none')]
    else:
        raise PreventUpdate

@callback(
    Output("planner-form-col-row-2", "children", allow_duplicate=True),
    Input("add-item", "n_clicks"),
    State("planner-form-col-row-2", "children"),
prevent_initial_call=True
)
def on_add_item_click(n_clicks, children):
    if n_clicks == 1:
        raise PreventUpdate
    else:
        new_form_row = pl.create_form_row(n_clicks)

        children.append(new_form_row)

    return children

@callback(
    Output("planner-form-col-row-1", "children"),
    Output("planner-form-col-row-2", "children"),
    Output({"type": "form-delete-button", "index": ALL}, "n_clicks"),
    Input("planner-form-col-row-1", "children"),
    Input("planner-form-col-row-2", "children"),
    Input({"type": "form-delete-button", "index": ALL}, "n_clicks"),
)
def on_row_delete_click(row1_children, row2_children, n_clicks_dynamic):

    n_clicks_vector = np.array(n_clicks_dynamic)
    clickedButton = n_clicks_vector.argmax()+1
    if clickedButton == 1 and len(row1_children) == 8 and n_clicks_vector.max() != 0:
        row1_children.pop()
    elif len(row1_children) == 7 and n_clicks_vector.max() != 0:
        row2_children.pop(clickedButton-1)
    elif len(row1_children) == 8 and n_clicks_vector.max() != 0:
        row2_children.pop(clickedButton-2)
    else:
        raise PreventUpdate
    zero_vector = np.zeros(n_clicks_vector.shape[0])

    return [row1_children, row2_children, zero_vector.astype(int).tolist()]


@callback(
    Output("planner-output-col-row-1", "children"),
    Output("reqd_bmr", "data"),
    Input("weight-input", "value"),
    Input("age-input", "value"),
    Input("height-input", "value"),
    Input("gender-input", "value")
)
def calculate_requirements(weight, age, height, gender):
    reqd_row, bmr = pl.calculate_requirements(weight, age, height, gender)

    return [reqd_row, bmr]


@callback(
    Output("planner-output-col-row-2", "children"),
    Output("planner-output-col-row-4", "children"),
    Output("diet-cal", "data"),
    Input({"type": "form-dropdown", "index": ALL}, "value"),
    Input({"type": "form-input", "index": ALL}, "value"),
    prevent_initial_call=True
)
def calculate_kpis(dropdowns, inputs):

    contents = {}

    for drop, inp in zip(dropdowns, inputs):
        if drop is not None and inp is not None:
            if contents.get(drop, "not found") == "not found":
                contents[drop] = [inp]
            else:
                contents[drop].append(inp)

    if len(contents)==0:
        return [[], 0]

    plan_Row, calories, nutrients_df = pl.calculate_diet_kpis(contents)

    nutrients_data_table = dash_table.DataTable(nutrients_df.to_dict("records"), [{"name": i, "id": i} for i in nutrients_df.columns], id="nutrients-table")

    return [plan_Row, nutrients_data_table, calories]


@callback(
    Output("planner-output-col-row-3", "children"),
    Input("reqd_bmr", "data"),
    Input("diet-cal", "data"),
    prevent_initial_call=True
)
def get_calorie_difference(bmr, planned_cal):
    diff = round(planned_cal-bmr,2)

    if bmr is None or planned_cal is None:
        return ""

    if diff < 0:
        diff_string = dbc.Row([html.H5("Calorie Deficit:", id="deficit-heading"), html.H6(f"{diff} Cal", id="deficit-value")])
    elif diff > 0:
        diff_string = dbc.Row([html.H5("Calorie Surplus:", id="surplus-heading"), html.H6(f"{diff} Cal", id="surplus-value")])
    else:
        diff_string = dbc.Row([html.H5("Calorie Balance:", id="balance-heading"), html.H6(f"{diff} Cal", id="balance-value")])

    return diff_string


@callback(
    Output("dummy-store", "data", allow_duplicate=True),
    State("user-dropdown", "value"),
    State("plan-date-picker", "date"),
    State({"type": "form-dropdown", "index": ALL}, "value"),
    State({"type": "form-input", "index": ALL}, "value"),
    State("reqd_bmr", "data"),
    State("weight-input", "value"),
    Input("submit", "n_clicks"),
    prevent_initial_call=True
)
def on_submit_click(user, planDate, dropdowns, inputs, bmr, weight, submit_button):
    contents = {}
    planDate = planDate[:planDate.find("T") if planDate.find("T") != -1 else len(planDate)].split("-")
    planDate = date(int(planDate[0]), int(planDate[1]), int(planDate[2]))
    for drop, inp in zip(dropdowns, inputs):
        if drop is not None and inp is not None:
            if contents.get(drop, "not found") == "not found":
                contents[drop] = [inp]
            else:
                contents[drop].append(inp)

    if len(contents) == 0:
        return [[], 0]

    nutrients_df = pl.calculate_diet_kpis(contents)[2]
    nutrients_df["bmr"] = bmr
    nutrients_df["weight"] = weight
    currentCols = list(nutrients_df.columns)
    nutrients_df["user"] = user
    nutrients_df["date"] = planDate

    nutrients_df = nutrients_df[["user", "date"]+currentCols]
    dbManager = DbManagement()
    dbManager.upload_dataframe(nutrients_df, "history")
    dbManager.close_connection()
    return ""


@callback(
    Output("gender-input", "value"),
    Output("age-input", "value"),
    Output("weight-input", "value"),
    Output("height-input", "value"),
    Input("user-dropdown", "value")
)
def on_user_selection_change(user):
    dbManager = DbManagement()

    name, gender, dob, age, weight, height =dbManager.get_user_bio(user)
    dbManager.close_connection()

    return [gender, age, weight, height]


@callback(
State("user-dropdown", "value"),
    State("weight-input", "value"),
    State("height-input", "value"),
    Input("update", "n_clicks")
)
def on_update_click(user, weight, height, n_click):
    dbManager = DbManagement()
    dbManager.update_user_weight_height(user, weight, height)
    dbManager.close_connection()


@callback(
    Output("food-level-history", "data"),
    Output("date-level-history", "data"),
    Output("date-level-history-long", "data"),
    Output("history-user-dropdown", "options"),
    Input("hist-refresh", "n_clicks"),
    Input("history-user-dropdown", "value"),
    Input("hist-date-picker-range", "start_date"),
    Input("hist-date-picker-range", "end_date")
)
def fetch_history(n_clicks, user, start_date, end_date):
    dbManager = DbManagement()
    userList = dbManager.get_user_list()
    datefoodlevel, datelevel, datelevelmelt = dbManager.get_user_history(user, start_date, end_date)
    dbManager.close_connection()
    return datefoodlevel, datelevel, datelevelmelt, userList

@callback(
    Output("hist-graph-row", "children"),
    Output("hist-table-row", "children"),
    Input("food-level-history", "data"),
    Input("date-level-history", "data"),
    Input("date-level-history-long", "data"),
    Input("hist-bmr-switch","on"),
    Input("hist-cal-switch","on"),
    Input("hist-carb-switch","on"),
    Input("hist-prot-switch","on"),
    Input("hist-fat-switch","on"),
    Input("hist-weight-switch","on"),
    Input("hist-calDelta-switch","on"),
)
def populate_history(datefoodlevel, datelevel, datelevelmelt, bmr, cal, carb, prot, fat, weight, delta):
    try:
        userHistory = (datefoodlevel, datelevel, datelevelmelt)
        filter_dict = {
            "bmr": bmr, "calorie": cal, "carbs": carb, "protein": prot, "fat": fat, "weight": weight, "delta": delta
        }
        fig, datelevelTable = hst.generate_chart(userHistory, filter=filter_dict)

        graph = dcc.Graph(figure=fig)
        graphTable = dash_table.DataTable(datelevelTable.to_dict("records"), [{"name": i, "id": i} for i in datelevelTable.columns], id="history-table")
        return [graph, graphTable]
    except:
        return ["", ""]


@callback(
    Output("hist-bmr-switch","on", allow_duplicate=True),
    Output("hist-cal-switch","on", allow_duplicate=True),
    Output("hist-carb-switch","on", allow_duplicate=True),
    Output("hist-prot-switch","on", allow_duplicate=True),
    Output("hist-fat-switch","on", allow_duplicate=True),
    Output("hist-weight-switch","on", allow_duplicate=True),
    Output("hist-calDelta-switch","on", allow_duplicate=True),
    Input("hist-sel-all", "n_clicks"),
    prevent_initial_call=True
)
def select_all_history(n_clicks):
    return [True]*7

@callback(
    Output("hist-bmr-switch","on"),
    Output("hist-cal-switch","on"),
    Output("hist-carb-switch","on"),
    Output("hist-prot-switch","on"),
    Output("hist-fat-switch","on"),
    Output("hist-weight-switch","on"),
    Output("hist-calDelta-switch","on"),
    Input("hist-sel-none", "n_clicks"),
    prevent_initial_call=True
)
def select_none_history(n_clicks):
    return [False]*7


@callback(
    Output("db-manage-username", "children", allow_duplicate=True),
    Output("db-manage-name", "children", allow_duplicate=True),
    Output("db-manage-gender", "children", allow_duplicate=True),
    Output("db-manage-dob", "children", allow_duplicate=True),
    Output("db-manage-weight", "children", allow_duplicate=True),
    Output("db-manage-height", "children", allow_duplicate=True),
    Output("db-manage-save", "children", allow_duplicate=True),
    Output("new-user-form-state", "data", allow_duplicate=True),
    Output("new-user", "children", allow_duplicate=True),
    Output("modify-user", "children", allow_duplicate=True),
    Input("new-user", "n_clicks"),
    State("modify-user", "children"),
    State("new-user-form-state", "data"),
    prevent_initial_call = True
)
def add_new_user_form(n_clicks, modify_user_text, new_user_form_state):

    new_user_form = ["", "", "", "", "", "", "", 0, "New User", "Modify User"]

    if new_user_form_state == 0 or modify_user_text.lower() == "cancel":
        new_user_form = dbm.create_new_or_modify_form()
        new_user_form.extend([1, "Cancel", "Modify User"])

    return new_user_form


@callback(
    Output("db-manage-username", "children"),
    Output("db-manage-name", "children"),
    Output("db-manage-gender", "children"),
    Output("db-manage-dob", "children"),
    Output("db-manage-weight", "children"),
    Output("db-manage-height", "children"),
    Output("db-manage-save", "children"),
    Output("new-user-form-state", "data"),
    Output("modify-user", "children"),
    Output("new-user", "children"),
    Input("modify-user", "n_clicks"),
    State("new-user", "children"),
    State("new-user-form-state", "data"),
    prevent_initial_call=True
)
def add_modify_user_form(n_clicks, new_user_text, new_user_form_state):
    modify_user_form = ["", "", "", "", "", "", "", 0, "Modify User", "New User"]

    if new_user_form_state == 0 or new_user_text.lower() == "cancel":
        modify_user_form = dbm.create_new_or_modify_form("modify")
        modify_user_form.extend([1, "Cancel", "New User"])

    return modify_user_form


@callback(
    Output("user-manage-availability", "children"),
    Input("username-manage-input", "value"),
)
def check_username_avaialbilty(username):

    if len(username) > 0:
        dbManager = DbManagement()
        usernameExists = dbManager.check_username_exists(username)
        dbManager.close_connection()

        if usernameExists:
            return "this username is not avaialble"
        else:
            return "this username is available"
    else:
        return ""


@callback(
    State("username-manage-input", "value"),
    State("user-manage-availability", "children"),
    State("name-manage-input", "value"),
    State("gender-manage-input", "value"),
    State("dob-manage-picker", "date"),
    State("weight-manage-input", "value"),
    State("height-manage-input", "value"),
    Input("save-new-user", "n_clicks")
)
def add_user_data(username, availability, name, gender, dob, weight, height, n_click):

    if "not" not in availability.lower():
        if gender == "Male":
            gender = "M"
        else:
            gender = "F"

        if n_click > 0:
            dbManager = DbManagement()
            dbManager.add_user(username, name, gender, dob, weight, height)
            dbManager.close_connection()


@callback(
    Output("name-manage-input", "value"),
    Output("gender-manage-input", "value"),
    Output("dob-manage-picker", "date"),
    Output("weight-manage-input", "value"),
    Output("height-manage-input", "value"),
    Input("username-manage-dropdown", "value"),
)
def fetch_user_data_for_modify_form(username):
    dbManager = DbManagement()
    name, gender, dob, age, weight, height = dbManager.get_user_bio(username)
    dbManager.close_connection()

    return name, gender, dob, weight, height


@callback(
    Output("dummy-store", "data", allow_duplicate=True),
    State("username-manage-dropdown", "value"),
    State("name-manage-input", "value"),
    State("gender-manage-input", "value"),
    State("dob-manage-picker", "date"),
    State("weight-manage-input", "value"),
    State("height-manage-input", "value"),
    Input("save-modified-user", "n_clicks"),
    prevent_initial_call=True
)
def modify_user_data(username, name, gender, dob, weight, height, n_click):
    if gender == "Male":
        gender = "M"
    else:
        gender = "F"

    if n_click > 0:
        dbManager = DbManagement()
        dbManager.modify_user(username, name, gender, dob, weight, height)
        dbManager.close_connection()

    return []


@callback(
    Output("db-manage-toast", "children", allow_duplicate=True),
    Input("backup-db", "n_clicks"),
    prevent_initial_call=True
)
def backup_db(n_click):
    destination = open_file_dialog()
    source = "./planner.db"

    if destination != "":
        shutil.copy(source, destination)

    return dbm.backup_restore_toast(destination, "backup")


@callback(
    Output("db-manage-toast", "children", allow_duplicate=True),
    Input("restore-db", "n_clicks"),
    prevent_initial_call=True
)
def restore_db(n_clicks):
    source = open_file_dialog("file")[0]
    destination = "./"

    if source != "":
        shutil.copy(source, destination)

    return dbm.backup_restore_toast(source, "restore")


if __name__ == "__main__":
    port=33115
    debugMode = False
    open_browser = Timer(3, wb.open, [f"http://127.0.0.1:{port}"]).run
    useReloader=True
    if not debugMode:
        openBrowserThread = th.Thread(target=open_browser)
        openBrowserThread.start()
        useReloader = False
    app.run(debug=debugMode, port=port, use_reloader=useReloader)
