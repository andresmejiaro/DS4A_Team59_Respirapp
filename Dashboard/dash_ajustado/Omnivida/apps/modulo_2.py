import plotly.graph_objects as go
import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import dash_bootstrap_components as dbc

from app import app

###################################################################
from apps.RDS_funciones import prepara_info_mapa, region_agrupada, region_agrupada_values, region_agrupada_barra

data, conteos_adherencia = prepara_info_mapa()

def mapa_adherencia(year=2019,month=1):
    cont=conteos_adherencia[(conteos_adherencia.years==year) &(conteos_adherencia.months==month)]
    fig=px.choropleth(cont,geojson=data,locations="cod_divipola",color='PORCENTAJE ADHERENCIA',scope="south america",hover_name="city")
    fig.update_geos(fitbounds="locations",visible=True)
    return fig

year = 2019
month = 1
departmento = 'CUNDINAMARCA'
ciudad = 'BOGOTA'

departments, cities = region_agrupada_values()

def region_agrupada_table(departmento,ciudad):
    df = region_agrupada(departmento,ciudad).reset_index()
    df = df.rename(columns = {'index':'_'})
    return df.to_dict('rows')

def adherencia_barra(departmento, ciudad):
    df_group = region_agrupada_barra(departmento, ciudad)
    fig = px.bar(df_group, x="fecha", y=['adherente','no adherente'])
    return fig

# change to app.layout if running as single page app instead
layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("Entidades de salud"), className="mb-2")
        ]),
        dbc.Row([
            dbc.Col(html.H6(children=''), className="mb-4")
        ]),

        dbc.Row([
            dbc.Col(dbc.Card(html.H3(children='Adherencia por municipio',
                                     className="text-center text-light bg-dark"), body=True, color="dark")
                    , className="mb-4")
        ]),
        dbc.Row([
            dbc.Col(dcc.Dropdown(
                    id='fig_mapa_adherencia_year',
                    options=[
                        {'label': '2012', 'value': 2012},
                        {'label': '2013', 'value': 2013},
                        {'label': '2014', 'value': 2014},
                        {'label': '2015', 'value': 2015},
                        {'label': '2016', 'value': 2016},
                        {'label': '2017', 'value': 2017},
                        {'label': '2018', 'value': 2018},
                        {'label': '2019', 'value': 2019},
                        {'label': '2020', 'value': 2020},
                    ],
                    value=2020,
                    style={'width': '65%', 'margin-left':'5px'}
                    )),
            dbc.Col(dcc.Dropdown(
                    id='fig_mapa_adherencia_month',
                    options=[
                        {'label': '1', 'value': 1},
                        {'label': '2', 'value': 2},
                        {'label': '3', 'value': 3},
                        {'label': '4', 'value': 4},
                        {'label': '5', 'value': 5},
                        {'label': '6', 'value': 6},
                        {'label': '7', 'value': 7},
                        {'label': '8', 'value': 8},
                        {'label': '9', 'value': 9},
                        {'label': '10', 'value': 10},
                        {'label': '11', 'value': 11},
                        {'label': '12', 'value': 12},
                    ],
                    value=1,
                    style={'width': '65%', 'margin-left':'5px'}
                    )),
                ]),
    dcc.Graph(figure=mapa_adherencia(year=year,month=month),id='fig_mapa_adherencia'),
        dbc.Row([
            dbc.Col(dbc.Card(html.H3(children='Detalle adherencia por región',
                                     className="text-center text-light bg-dark"), body=True, color="dark")
                    , className="mt-4")
        ]),
    dbc.Row([
                dbc.Col(dcc.Dropdown(
                        id='datatable_region_agrupada_departments',
                        options=[{'label': key, 'value': key} for key in departments],
                        value='CUNDINAMARCA',
                        style={'width': '65%', 'margin-left':'5px'}
                        )),
                dbc.Col(dcc.Dropdown(
                        id='datatable_region_agrupada_cities',
                        options=[{'label': key, 'value': key} for key in cities],
                        value='BOGOTA',
                        style={'width': '65%', 'margin-left':'5px'}
                        )),
                    ]),        
    dash_table.DataTable(# Tabla
        id='datatable_region_agrupada',
        columns=[{"name": i, "id": i} for i in ['_', 'pacientes', 'adherente', 'no adherente', 'no aplica']],
        data=region_agrupada_table(departmento, ciudad)
        ),#Valor inicial
    dbc.Row([
        dbc.Col(dbc.Card(html.H3(children='Adherencia en el tiempo' ,
                                 className="text-center text-light bg-dark"), body=True, color="dark")
                , className="mt-4")
    ]),
    dcc.Graph(figure=adherencia_barra('ANTIOQUIA','MEDELLIN'),id='fig_adherencia_barra'),
    ]),
])

# page callbacks
@app.callback(
    Output(component_id='fig_mapa_adherencia', component_property='figure'),
    [Input(component_id='fig_mapa_adherencia_year', component_property='value'),
     Input(component_id='fig_mapa_adherencia_month', component_property='value')]
    )
def update_grafica_adherencia(x,y):
    return mapa_adherencia(x,y)

@app.callback(Output(component_id='datatable_region_agrupada', component_property='data'), # Callback tabla
    [Input(component_id='datatable_region_agrupada_departments', component_property='value'),
     Input(component_id='datatable_region_agrupada_cities', component_property='value')]
    )
def update_table_adherencia(x,y):
    return region_agrupada_table(x,y)

@app.callback(
    Output(component_id='fig_adherencia_barra', component_property='figure'),
    [Input(component_id='datatable_region_agrupada_departments', component_property='value'),
     Input(component_id='datatable_region_agrupada_cities', component_property='value')]
    )

def update_grafica_barra(x,y):
    return adherencia_barra(x,y)





