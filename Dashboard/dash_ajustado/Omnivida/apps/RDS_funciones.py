# %%
import pandas as pd 
from dateutil.relativedelta import relativedelta
from datetime import timedelta
import sqlalchemy as sqla 
import json
import plotly.express as px

#%%
## necesita la base de medicamentos cargados
## Cambiar la ruta para la ubicacion correcta
engine=sqla.create_engine('postgresql://XXXXXXXX/proyecto_adherencia')

_connection_=engine.connect()
metadata=sqla.MetaData()

_db_=sqla.Table('datos_basicos',metadata,autoload=True,autoload_with=engine)
_com_=sqla.Table('comorbilidades',metadata,autoload=True,autoload_with=engine)
_creclama__=sqla.Table('consistencia_recl',metadata,autoload=True,autoload_with=engine)
_conteos_adherencia_=sqla.Table('conteos_adherencia2',metadata,autoload=True,autoload_with=engine)
tacometro_=sqla.Table('tacometro',metadata,autoload=True,autoload_with=engine)

df_conteos_adherencia2 = pd.read_sql('''select *
                                        from conteos_adherencia2
                                        ''', engine)

df_tacometro = pd.read_sql('''select *
                              from tacometro
                              ''', engine)
# %%
def find_tacometro(ID_PACIENTE):
    return df_tacometro[df_tacometro['id_paciente'] == ID_PACIENTE]['pred'].mean()
# %%
def informacion_basica(ID_PACIENTE):

    ## Edad y Genero
    _edad_y_genero_q_=sqla.select([_db_.columns.fe_nacimiento,_db_.columns.genero]).where(_db_.columns.id_paciente==ID_PACIENTE)
    _edad_y_genero_=_connection_.execute(_edad_y_genero_q_).fetchall()
    _edad_y_genero_df_=pd.DataFrame(_edad_y_genero_)
    _edad_y_genero_df_.columns=_edad_y_genero_[0].keys()

    _comorb_q_=sqla.select([_com_]).where(_com_.columns.id_paciente==ID_PACIENTE)
    _comorb_=_connection_.execute(_comorb_q_).fetchall()
    _comorb_df_=pd.DataFrame(_comorb_)
    _comorb_df_.columns=_comorb_[0].keys()

    _to_return_=pd.Series({"Edad":relativedelta(pd.to_datetime("today"),pd.to_datetime(_edad_y_genero_df_["fe_nacimiento"].values[0])).years,
                            "Genero":_edad_y_genero_df_["genero"].values[0],
                            "Rinitis":_comorb_df_["rinitisalergica"].values[0],
                            "Urticaria":_comorb_df_["urticaria"].values[0],
                            "Tumor":_comorb_df_["tumor"].values[0],
                            "Circulatorio":_comorb_df_["circulatorio"].values[0],
                            "Digestivo":_comorb_df_["digestivo"].values[0],
                            "Respiratorio No Asma No Rinitis":_comorb_df_["digestivo"].values[0],
                            "Otros":_comorb_df_["otros"].values[0],
                        })
    return _to_return_

# %%

def info_gra_consist_reclama(ID_PACIENTE):

    _consistencia_recl_q_=sqla.select([_creclama__]).where(_creclama__.columns.id_paciente==ID_PACIENTE)
    _consistencia_recl_=_connection_.execute(_consistencia_recl_q_).fetchall()
    
    _consistencia_recl_df_=pd.DataFrame(_consistencia_recl_)
    _consistencia_recl_df_.columns=_consistencia_recl_[0].keys()

    _consistencia_recl_df_.fecha_emision=pd.to_datetime(_consistencia_recl_df_.fecha_emision)
    _consistencia_recl_df_.fechasiguienterecla=pd.to_datetime(_consistencia_recl_df_.fechasiguienterecla)
    
    _consistencia_recl_df_.fechasiguienterecla[pd.isna(_consistencia_recl_df_.fechasiguienterecla)]=_consistencia_recl_df_.fecha_emision[pd.isna(_consistencia_recl_df_.fechasiguienterecla)]+timedelta(days=30)
    _consistencia_recl_df_.consistenciareclamacion[pd.isna(_consistencia_recl_df_.consistenciareclamacion)]=-1

    
    return _consistencia_recl_df_


# %%

def prepara_info_mapa():

    with open('apps/municipios.geojson', encoding='utf8') as file1:
        data=json.load(file1)


    div_Municipio=[]
    nom_Municipio=[]
    nom_Dpto=[]
    for x in data["features"]:
        x["id"]=x["properties"]["ID_ESPACIA"]
        div_Municipio.append(x["properties"]["ID_ESPACIA"])
        nom_Municipio.append(x["properties"]["NOM_MUNICI"])
        nom_Dpto.append(x["properties"]["NOM_DEPART"])



    
    conteos_adherencia_q_=sqla.select([_conteos_adherencia_])
    conteos_adherencia_f=_connection_.execute(conteos_adherencia_q_).fetchall()
    conteos_adherencia=pd.DataFrame(conteos_adherencia_f)
    conteos_adherencia.columns=conteos_adherencia_f[0].keys()
 
    divipola=pd.DataFrame({"cod_divipola":div_Municipio,"city":nom_Municipio,"department":nom_Dpto})


    dept_replace={"VALLE":"VALLE DEL CAUCA","BOLIVAR":"BOLÍVAR"}
    conteos_adherencia.department.replace(dept_replace,inplace=True)



    mun_replace={"BOGOTA":"BOGOTÁ, D.C.","MEDELLIN":"MEDELLÍN","CHIA":"CHÍA",
             "ITAGUI":"ITAGÜÍ","DON MATIAS":"DON MATÍAS",
             "BARRANQUILLA":"BARRANQUILLA (Distrito Especial, Industrial y Portuario)",
             "PUERTO BERRIO":"PUERTO BERRÍO","EL SANTUARIO":"SANTUARIO",
             "PENOL":"PEÑOL",
             "SOPO":"SOPÓ","GUATAPE":"GUATAPÉ","VILLAMARIA":"VILLAMARÍA",
             "SONSON":"SONSÓN","SANTA MARTA":"SANTA MARTA (Distrito Turístico Cultural e Histórico)",
             "CARTAGENA":"CARTAGENA DE INDIAS (Distrito Turístico y Cultural)"}
    conteos_adherencia.city.replace(mun_replace,inplace=True)

    divipola.department.replace({"SATA FE DE BOGOTÁ D.C.":"CUNDINAMARCA"},inplace=True)



    conteos_adherencia=conteos_adherencia.merge(divipola,how="left")

    conteos_adherencia["PORCENTAJE ADHERENCIA"]=100*conteos_adherencia['adherente']/(conteos_adherencia['adherente']+
    conteos_adherencia["no adherente"]+
    conteos_adherencia['no aplica'])
    conteos_adherencia["day"]=1
    conteos_adherencia["FECHA"]=pd.to_datetime(conteos_adherencia.loc[:,['day','months','years']])
    conteos_adherencia["FECHAK"]=conteos_adherencia["years"]*100+conteos_adherencia["months"]

    new_features=[feature for feature in data['features'] if feature["id"] in conteos_adherencia["cod_divipola"].values]
    new_features
    data["features"]=new_features
    return (data, conteos_adherencia)

# %%
def region_agrupada_values():
    return df_conteos_adherencia2['department'].unique(), df_conteos_adherencia2['city'].unique()
# %%
def region_agrupada(departmento='ANTIOQUIA', ciudad='MEDELLIN'):
    df = df_conteos_adherencia2.copy()
    df['pacientes'] = df['adherente']+ df['no adherente'] + df['no aplica']
    
    df_region_agrupada = df.groupby(['department','city'])['pacientes','adherente','no adherente','no aplica'].sum().reset_index()
    idx = ((df_region_agrupada['department']==departmento)&(df_region_agrupada['city']==ciudad))
    
    df_region_agrupada = df_region_agrupada[idx]
    df_region_agrupada = df_region_agrupada.append(df_region_agrupada)
    df_region_agrupada.index = ['Total','Porcentaje']

    df_region_agrupada.iloc[[1],[2,3,4,5]] = (df_region_agrupada.iloc[[1],[2,3,4,5]]/df_region_agrupada.iloc[0,2]).applymap(lambda x: '{:.1f}%'.format(x*100))
    df_region_agrupada.iloc[:,[2,3,4,5]]

    return df_region_agrupada.iloc[:,2:]
# %%
def region_agrupada_barra(departmento='ANTIOQUIA', ciudad='MEDELLIN'):
    df = df_conteos_adherencia2.copy()
    idx = (df['department']==departmento) & (df['city']==ciudad)
    df_group = df[idx].groupby(['years','months'])['adherente','no adherente'].sum().reset_index()
    df_group['fecha'] = df_group.apply(lambda x: pd.to_datetime('{:.0f}-{:02.0f}-01'.format(x['years'],x['months'])),axis=1)
    return df_group
# %%
factors_dic = {
     'Act_Bin_2' : 'Puntaje ACT < 22',
     'Act_Bin_3' : 'Puntaje ACT > 22',
     'ACT_GT22' : 'Puntaje ACT > 22',
     'ACT_LT18' : 'Puntaje ACT < 18',
     'ACT_NotRecord' : 'Sin registro ACT',
     'Alcohol_Excepcional' : 'Alcohol: Consumo Ocasional',
     'Alcohol_No' : 'Alcohol: No',
     'Alcohol_Social drinker' : 'Alcohol: Eventos Sociales',
     'Dias desde RAM' : 'Dias desde RAM',
     'NM_IMC' : 'IMC',
     'NumAdherencias_3_anio' : 'N° Adhs ult. 3 años',
     'NumEntrevistas_1_anio' : 'N° Test Adhs ult. año',
     'NumEntrevistas_3_anio' : 'N° Test Adhs ult. 3 años',
     'NumEntrevistas_5_anio' : 'N° Test Adhs ult. 5 años',
     'NumEntrevistas_5_anio' : 'N° Test Adhs ult. 5 años',
     'NumNoAdherencias_1_anio' : 'N° No Adh ult. año',
     'NumNoAdherencias_1_anio' : 'N° No Adh ult. año',
     'NumNoAdherencias_3_anio' : 'N° No Adh ult. 3 años',
     'PropAdherencia_3_anio' : 'Porporcion Adh ult. 3 años',
     'Ratio6m_Oral' : 'Ratio Oral ult. 6 meses',
     'Tobacco_<5 daily' : 'Tabaco: 5 diarios.',
     'Tobacco_No' : 'Tabaco: No'}


def barras_paciente(ID_PACIENTE):
    tacometro_q_=sqla.select([tacometro_]).where(tacometro_.columns.id_paciente==ID_PACIENTE)
    tacometro_data=_connection_.execute(tacometro_q_).fetchall()
    tacometro_df_=pd.DataFrame(tacometro_data)
    tacometro_df_.columns=tacometro_data[0].keys()
    datos=pd.DataFrame({"Factores":[tacometro_df_.c1[0],tacometro_df_.c2[0],tacometro_df_.c3[0]],"Riesgo":[tacometro_df_.x1[0],tacometro_df_.x2[0],tacometro_df_.x3[0]]})
    datos.Riesgo=datos.Riesgo.apply(abs)
    datos.Factores.replace(factors_dic, inplace=True)
    fig=px.bar(datos,x="Riesgo",y="Factores",color="Factores", color_discrete_sequence=["red","orange","green"],orientation="h")
    return fig
