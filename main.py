from dash import Dash, html, dcc, callback, Output, Input
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import frontpage as fp
import planner as pl
import webbrowser as wb
from threading import Timer
import threading as th

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = [
    dcc.Store(id="new-plan-click-store", data=[0]),
    dcc.Store(id="reset-click-store", data=[0]),
    *fp.frontPageItems]


@callback(
    Output("planner-form-col-row-1", "children"),
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
    Output("planner-form-col-row-2", "children"),
    Input("add-item", "n_clicks"),
    Input("planner-form-col-row-2", "children")
)
def on_add_item_click(n_clicks, children):
    if n_clicks == 1:
        raise PreventUpdate
    else:
        children.append(pl.create_form_row(n_clicks))
    return children








if __name__ == "__main__":
    port=33115
    debugMode = False
    open_browser = Timer(3, wb.open, [f"http://127.0.0.1:{port}"]).run
    openBrowserThread = th.Thread(target=open_browser)
    openBrowserThread.start()
    app.run(debug=debugMode, port=port, use_reloader=False)



