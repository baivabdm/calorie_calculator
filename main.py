from dash import Dash, html, dcc, callback, Output, Input, ALL, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import frontpage as fp
import planner as pl
import webbrowser as wb
from threading import Timer
import threading as th
import numpy as np

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = [
    dcc.Store(id="n_clicks_vector", data=[]),
    *fp.frontPageItems]


@callback(
    Output("planner-form-col-row-1", "children", allow_duplicate=True),
    Output("new-plan", "n_clicks"),
    Output("reset", "n_clicks"),
    Output("planner-form-col-row-2", "children", allow_duplicate=True),
    Output("planner-form-col-row-3", "children"),
    Output("submit", "style"),
    Input("new-plan", "n_clicks"),
    Input("reset", "n_clicks"),
    prevent_initial_call=True
)
def new_plan(n_clicks_plan,n_clicks_reset,):
    if n_clicks_plan == 1:
        return [[pl.create_weight_input_widget(), pl.create_form_row()], 2, 0, [], pl.create_add_item_button(), {}]

    elif n_clicks_reset == 1:
        return [[], 0, 0, [], [], dict(display='none')]
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
    print(clickedButton)
    if clickedButton == 1 and len(row1_children) == 2 and n_clicks_vector.max() != 0:
        row1_children.pop()
    elif len(row1_children) == 1 and n_clicks_vector.max() != 0:
        row2_children.pop(clickedButton-1)
    elif len(row1_children) == 2 and n_clicks_vector.max() != 0:
        row2_children.pop(clickedButton-2)
    else:
        raise PreventUpdate
    zero_vector = np.zeros(n_clicks_vector.shape[0])

    return [row1_children, row2_children, zero_vector.astype(int).tolist()]


if __name__ == "__main__":
    port=33115
    debugMode = False
    open_browser = Timer(3, wb.open, [f"http://127.0.0.1:{port}"]).run
    openBrowserThread = th.Thread(target=open_browser)
    openBrowserThread.start()
    app.run(debug=debugMode, port=port, use_reloader=False)
