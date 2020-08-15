# %%
import pandas as pd 
from dateutil.relativedelta import relativedelta
from datetime import timedelta
import sqlalchemy as sqla 

#%%
## necesita la base de medicamentos cargados
## Cambiar la ruta para la ubicacion correcta
engine=sqla.create_engine('postgresql://biologicos:omalizumab@adherencia.cl57pi28yi4u.us-east-2.rds.amazonaws.com:5432/proyecto_adherencia')

#base_medicamentos=pd.read_csv("/mnt/Storage/ds4a/Proyecto Omnivida/git-Omnivida/Funciones Objetivo/medicamentos_limpio_29_jun_AM.xlsx_Oral_train_trabajo.csv")

# %%
def informacion_basica(ID_PACIENTE):
    _connection_=engine.connect()
    metadata=sqla.MetaData()
    _db_=sqla.Table('datos_basicos',metadata,autoload=True,autoload_with=engine)
    _com_=sqla.Table('comorbilidades',metadata,autoload=True,autoload_with=engine)

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
                            "RespiratorioNoAsmaRinitis":_comorb_df_["digestivo"].values[0],
                            "Otros":_comorb_df_["otros"].values[0],
                        })
    return _to_return_

# %%

def info_gra_consist_reclama(ID_PACIENTE):
    _connection_=engine.connect()
    metadata=sqla.MetaData()
    _creclama__=sqla.Table('consistencia_recl',metadata,autoload=True,autoload_with=engine)

    _consistencia_recl_q_=sqla.select([_creclama__]).where(_creclama__.columns.id_paciente==ID_PACIENTE)
    _consistencia_recl_=_connection_.execute(_consistencia_recl_q_).fetchall()
    
    _consistencia_recl_df_=pd.DataFrame(_consistencia_recl_)
    _consistencia_recl_df_.columns=_consistencia_recl_[0].keys()

    _consistencia_recl_df_.fecha_emision=pd.to_datetime(_consistencia_recl_df_.fecha_emision)
    _consistencia_recl_df_.fechasiguienterecla=pd.to_datetime(_consistencia_recl_df_.fecha_emision)
    
    _consistencia_recl_df_.fechasiguienterecla[pd.isna(_consistencia_recl_df_.fechasiguienterecla)]=_consistencia_recl_df_.fecha_emision[pd.isna(_consistencia_recl_df_.fechasiguienterecla)]+timedelta(days=30)
    _consistencia_recl_df_.consistenciareclamacion[pd.isna(_consistencia_recl_df_.consistenciareclamacion)]=-1

    
    return _consistencia_recl_df_

#%%
def info_conteo():
        
    _connection_=engine.connect()
    metadata=sqla.MetaData()
    _conteos_adherencia_=sqla.Table('conteos_adherencia',metadata,autoload=True,autoload_with=engine)

    _conteos_adherencia__q_=sqla.select([_conteos_adherencia_])
    _conteos_adherencia_2=_connection_.execute(_conteos_adherencia__q_).fetchall()
    
    _conteos_adherencia_df_=pd.DataFrame(_conteos_adherencia_2)
    _conteos_adherencia_df_.columns=_conteos_adherencia_2[0].keys()

    return _conteos_adherencia_df_
    

#%%
info_conteo()

# %%

informacion_basica(528384)
# %%
