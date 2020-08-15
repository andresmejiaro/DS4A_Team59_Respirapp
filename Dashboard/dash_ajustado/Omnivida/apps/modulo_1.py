import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

########## Importante inportar app para ejecutar en multi #########
from app import app

###################################################################
from apps.RDS_funciones import informacion_basica, info_gra_consist_reclama, find_tacometro, barras_paciente

def informacion_grafico_adherencia(id_paciente_ini):
    df = info_gra_consist_reclama(id_paciente_ini)
    return df.loc[df['id_paciente']==id_paciente_ini,["fecha_emision","consistenciareclamacion","fechasiguienterecla","categoria"]]

def graph_fig_adherencia_tiempo(id_paciente_ini):
    df_grafico = informacion_grafico_adherencia(id_paciente_ini)
    df_grafico["consistenciareclamacion"].replace(
        {0: "No Reclama", -1:"No Aplica" ,1: "Reclama"}, inplace=True) 
    # los números 1 y 0 ahora son STR   
    df_grafico.rename(columns={"categoria": "Task"}, inplace=True)
    df_grafico.rename(columns={"fecha_emision": "Start"}, inplace=True)
    df_grafico.rename(columns={"fechasiguienterecla": "Finish"}, inplace=True)
    df_grafico.rename(columns={"consistenciareclamacion": "Resource"}, inplace=True) 
    
    
    colors = {'No Aplica': 'rgb(255,255,0)',
              'Reclama': 'rgb(0,255,0)',
              'No Reclama': 'rgb(255,0,0)'}
    
    fig_adherencia_tiempo = ff.create_gantt(df_grafico, index_col="Resource",
                          title='reclamación de medicamentos en el tiempo',
                          colors=colors, show_colorbar=True, group_tasks=True)

    
    return fig_adherencia_tiempo

def tacometro_adherencia(prob_adherencia):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = prob_adherencia,
        domain = {'x': [0, 0.5], 'y': [0, 0.5]},
       # title = {'text': "Adherence probability"},
        gauge = {'axis': {'range': [0, 1]},
                'bar': {'color': "black"},
                 'steps' : [
                     {'range': [0, 0.3], 'color': "red"},
                     {'range': [0.300001, 0.6], 'color': "yellow"},
                     {'range': [0.600001, 1], 'color': "green"}]}))
    return fig


# Id default pacient
id_paciente_ini = 528384

# title
h_title = html.H2("Resumen paciente", id='title')

# Input
h_input = html.Div(["Identificación del paciente: ",
                    dcc.Input(id='input_cedula', value=id_paciente_ini, type='number', debounce=True)])

# gráficas
d_graph = dcc.Graph(figure=graph_fig_adherencia_tiempo(id_paciente_ini),id='fig_adherencia_tiempo')
d_taco = dcc.Graph(figure=tacometro_adherencia(find_tacometro(id_paciente_ini)),id='fig_tacometro')
d_barras = dcc.Graph(figure=barras_paciente(id_paciente_ini),id='fig_barras')
# # gráficas Div
h_graph = html.Div(d_graph,
    className="six columns",
    style={'display': 'block', "width":'auto','height': 'auto'} #"width":500, , 'height': '10em', "margin": 0,
    )

h_taco = html.Div(d_taco,
    className="six columns",
    style={'display': 'block', "width":'50em','height': '15em', "margin": '7.5em' }
        )
h_barras = html.Div(d_barras,
    className="six columns",
    style={'display': 'block', "width":'50em','height': '15em', "margin": '7.5em' }
        )

layout = dbc.Container( 
    [
        html.Hr(),
        dbc.Row([
            dbc.Col(html.H1("profesionales de la salud"), className="mb-2")
        ]),
######################        
        dbc.Row([   
            dbc.Col(dbc.Card(html.H3(children='Resumen del paciente',
                    className="text-center text-light bg-dark"), body=True, color="dark")
                    ,className="mb-4")
######################
        ]),
        html.Div([
            dbc.Row([
               dbc.Col(h_input),
            ]),           
        ],),#align="right"
        html.Hr(),  
######################    
        dash_table.DataTable(
            id='datatableOV',
           style_table={'overflowX': 'scroll',
                            'padding': 10},
            style_header={'backgroundColor': '#25597f', 'color': 'white'},
            style_cell={
                'backgroundColor': 'white',
                'color': 'black',
                'fontSize': 13,
                'font-family': 'Nunito Sans'}),
######################
        html.Hr(), 
        dbc.Row([
        dbc.Col(html.H5(children='reclamación de medicamentos en el tiempo', className="text-center"),
                width=6, className="mt-4"),
        dbc.Col(html.H5(children='Probabilidad de adherencia', className="text-center"), width=6,
                className="mt-4"),
        ]),
        html.Hr(),
        html.Div([
            dbc.Row([
                
                dbc.Col(html.Div(h_graph)), #md , width=6
                dbc.Col(html.Div(h_taco))   #, width=6
                
            ]), 
        ],),#align="right"

        html.Hr(),
#align="center" 
        dbc.Row([
        dbc.Col(html.H5(children='factores de riesgo', className="text-center"),
                width=6, className="mt-4")
        ]),    
            dbc.Row([              
                html.Div(h_barras)             
            ]),#align="center"
    ],
    fluid=True,
)    


@app.callback([Output('datatableOV', 'data'),
               Output('datatableOV', 'columns')],
             [Input('input_cedula', 'value')])
def update_table(value):
    df = informacion_basica(value)
    col= ["Rinitis","Urticaria","Tumor","Circulatorio","Digestivo",
    "Respiratorio No Asma No Rinitis","Otros"]
    full_col = ["Edad","Genero","Rinitis","Urticaria","Tumor","Circulatorio","Digestivo",
        "Respiratorio No Asma No Rinitis","Otros"]
    for i in col:
        if df.loc[i]== 0:
            df.loc[i] = None 
        else: 
            df.loc[i] = 'Presente' 
    columns = [{"name": i, "id": i} for i in full_col]
    data= [df.to_dict()]

    return data, columns 
    
@app.callback(
    Output(component_id='fig_adherencia_tiempo', component_property='figure'),
    [Input(component_id='input_cedula', component_property='value')])
def update_grafica(x):
    return graph_fig_adherencia_tiempo(x)
    
@app.callback(
    Output(component_id='fig_tacometro', component_property='figure'),
    [Input(component_id='input_cedula', component_property='value')])
def update_taco(value):
    taco = find_tacometro(value)
    return tacometro_adherencia(taco)

@app.callback(
    Output(component_id='fig_barras', component_property='figure'),
    [Input(component_id='input_cedula', component_property='value')])
def update_barras_paciente(id_paciente_ini):
#TODO mientras tenemos el modelo se usa random
    return barras_paciente(id_paciente_ini)


