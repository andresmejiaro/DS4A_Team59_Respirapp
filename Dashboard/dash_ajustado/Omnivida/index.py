import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

# must add this line in order for the app to be deployed successfully on Heroku
from app import app
# import all pages in the app TODO
from apps import modulo_1, modulo_2, home
 
# building the navigation bar
# https://github.com/facultyai/dash-bootstrap-components/blob/master/examples/advanced-component-usage/Navbars.py
dropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Home", href="/home"),
        dbc.DropdownMenuItem("Profesionales de la salud", href="/profesional_salud"),
        dbc.DropdownMenuItem("Entidades de la salud", href="/entidades_de_la_salud"),
    ],
    nav = True,
    in_navbar = True,
    label = "Explore",
)

navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src="/assets/respirapp.jfif", height="60px")),
                        #dbc.Col(dbc.NavbarBrand("OMNIVIDA DASH", className="ml-2")),
                    ],
                    align="center",
                    no_gutters=True,
                ),
                href="/home",
            ),
            dbc.NavbarToggler(id="navbar-toggler2"),
            dbc.Collapse( 
                dbc.Nav(
                    # right align dropdown menu with ml-auto className
                    [dropdown], className="ml-auto", navbar=True
                ),
                id="navbar-collapse2",
                navbar=True,
            ),
        ]
    ),
    color="white",
    light =True,
    className="mb-4",
)

def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

for i in [2]:
    app.callback(
        Output(f"navbar-collapse{i}", "is_open"),
        [Input(f"navbar-toggler{i}", "n_clicks")],
        [State(f"navbar-collapse{i}", "is_open")],
    )(toggle_navbar_collapse)

# embedding the navigation bar
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content')
])

 
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/profesional_salud':
        return modulo_1.layout
    elif pathname == '/entidades_de_la_salud':
        return modulo_2.layout
    else:
        return home.layout

if __name__ == '__main__':
    app.run_server(debug=False, port=8080, host='0.0.0.0')