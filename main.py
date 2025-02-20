import pandas as pd
from dash import Dash, html, dcc, callback, Output, Input, ALL, State, dash_table
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import frontpage as fp
import planner as pl
import webbrowser as wb
from threading import Timer
import threading as th
import numpy as np
from db_utils import DbManagement
from datetime import date

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Calorie Calculator and Optimizer"
app.layout = [
    dcc.Store(id="reqd_bmr", data=0),
    dcc.Store(id="diet-cal", data=0),
    dcc.Store(id="dummy-store",data=[]),
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

    if diff < 0:
        diff_string = dbc.Row([html.H5("Calorie Deficit:", id="deficit-heading"), html.H6(f"{diff} Cal", id="deficit-value")])
    elif diff > 0:
        diff_string = dbc.Row([html.H5("Calorie Surplus:", id="surplus-heading"), html.H6(f"{diff} Cal", id="surplus-value")])
    else:
        diff_string = dbc.Row([html.H5("Calorie Balance:", id="balance-heading"), html.H6(f"{diff} Cal", id="balance-value")])

    return diff_string


@callback(
    Output("dummy-store", "data"),
    State("user-dropdown", "value"),
    State("plan-date-picker", "date"),
    State({"type": "form-dropdown", "index": ALL}, "value"),
    State({"type": "form-input", "index": ALL}, "value"),
    Input("submit", "n_clicks")
)
def on_submit_click(user, planDate, dropdowns, inputs, submit_button):
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

    gender, age, weight, height =dbManager.get_user_bio(user)
    dbManager.close_connection()

    return [gender, age, weight, height]


@callback(
Input("user-dropdown", "value"),
    Input("weight-input", "value"),
    Input("height-input", "value"),
    Input("update", "n_clicks")
)
def on_update_click(user, weight, height, n_click):
    dbManager = DbManagement()
    dbManager.update_user_weight_height(user, weight, height)
    dbManager.close_connection()


if __name__ == "__main__":
    port=33115
    debugMode = False
    open_browser = Timer(3, wb.open, [f"http://127.0.0.1:{port}"]).run
    openBrowserThread = th.Thread(target=open_browser)
    openBrowserThread.start()
    app.run(debug=debugMode, port=port, use_reloader=False)
