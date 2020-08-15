import dash_html_components as html
import dash_bootstrap_components as dbc

# needed only if running this as a single page app
#external_stylesheets = [dbc.themes.LUX]

#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# change to app.layout if running as single page app instead
layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("RESPIRAPP COLOMBIA", className="text-center")
                    , className="mb-5 mt-5")
        ]),
        dbc.Row([
            dbc.Col(html.H5(children='''En los siguientes modulos encontrará información reelevente para la adherencia en el tratamiento del asma, 
                            donde podrá análizar indicadores tanto individuales por paciente como agregados para la toma oportuna de decisiones''')
                    , className="mb-4")
            ]),

        dbc.Row([
            dbc.Col(dbc.Card(children=[html.H3(children='Profesionales de la salud',
                                               className="text-center"),
                                       #dbc.Row([dbc.Col(
                                      dbc.Button("Se dirigirá a profesionales de la salud.",
                                                                   href="/profesional_salud",
                                                                   color="primary",
                                                        className="mt-6") #], justify="center")
                                       ],
                             body=True, color="dark", outline=True)
                    , width=6, className="mb-6"),
 
            dbc.Col(dbc.Card(children=[html.H3(children='Entidades de salud',
                                               className="text-center"),
                                       dbc.Button("Se dirigirá a entidades de salud",
                                                  href="/entidades_de_la_salud",
                                                  color="primary",
                                                  className="mt-6"),
                                       ],
                             body=True, color="dark", outline=True)
                    , width=6, className="mb-6"),

        ], className="mb-8"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col( html.Img(src="/assets/CONE.png", height="40px"),  className="mb-3"),
                dbc.Col(html.Img(src="/assets/Omnivida.png", height="60px"),  className="mb-3"),
                dbc.Col(html.Img(src="/assets/MinTIC_logo.png", height="60px"), className="mb-3")
            ]),
        dbc.Col( html.A("Colombia | Team #59 | DS4A | 2020")) ,
        dbc.Col( html.A("Copyright Team #59 DS4A © 2020"))


#        html.A("Colombia | Team #59 | DS4A | 2020")
# html.Img(src="/assets/Omnivida.png", height="60px")
    ])

])

# needed only if running this as a single page app
# if __name__ == '__main__':
#     app.run_server(host='127.0.0.1', debug=True)