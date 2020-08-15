
# %%
import pandas as pd
import sqlalchemy as sqla 
import os
os.chdir("/home/andres/ds4a/Proyecto Omnivida/git-Omnivida")
# %%

engine = sqla.create_engine('postgresql://biologicos:omalizumab@adherencia.cl57pi28yi4u.us-east-2.rds.amazonaws.com:5432/proyecto_adherencia')

# %%
## Datos basicos

db=pd.read_excel("datos originales/Datos basicos.xlsx")
db.rename(columns={"ID":"ID_PACIENTE"},inplace=True)
db.columns=map(str.lower,db.columns)
db.to_sql("datos_basicos",engine)
# %%

## Comorbilidades
com=pd.read_excel("Bases limpias/antecedentes_patologicos_3_jul.xlsx")
com.columns
com=com.loc[:,['ID_PACIENTE','DiagnosticoAsma',
       'RinitisAlergica', 'Urticaria', 'Tumor', 'Circulatorio', 'Digestivo',
       'RespiratorioNoAsmaRinitis', 'Otros']]
com.columns=map(str.lower,com.columns)
com=com.groupby("id_paciente").max()
com.to_sql("comorbilidades",engine)

# %%

## Grafico

biologicos=pd.read_csv("Funciones Objetivo/Consistencia_Bio.csv")
oral=pd.read_csv("Funciones Objetivo/Consistencia_Oral.csv")
mantenimiento=pd.read_csv("Funciones Objetivo/Consistencia_Inhaladores Mantenimiento.csv")
emergencia=pd.read_csv("Funciones Objetivo/Consistencia_Inhaladores Emergencia.csv")

oral=oral.loc[:,["ID_PACIENTE","FECHA_EMISION","FechaSiguienteRecla","ConsistenciaReclamacion","Tratamiento","Categoria"]]

biologicos.ConsistenciaReclamacion=(biologicos.TiempoEntreFormulas<40).astype(float)
biologicos=biologicos.loc[:,["ID_PACIENTE","FECHA_EMISION","FechaSiguienteRecla","ConsistenciaReclamacion","Tratamiento","Categoria"]]

mantenimiento=mantenimiento.loc[:,["ID_PACIENTE","FECHA_EMISION","FechaSiguienteRecla","ConsistenciaReclamacion","Tratamiento","Categoria"]]

emergencia=emergencia.loc[:,["ID_PACIENTE","FECHA_EMISION","FechaSiguienteRecla","ConsistenciaReclamacion","Tratamiento","Categoria"]]



consistencia_recl=pd.concat([oral,biologicos,mantenimiento,emergencia],axis=0)
consistencia_recl.columns=map(str.lower,consistencia_recl.columns)

consistencia_recl.to_sql("consistencia_recl",engine)


# %%

tacometro=pd.read_csv("Resultados Modelo/20200801_Res_Modelo_Adh_Prob.csv")
tacometro.columns=map(str.lower,tacometro.columns)

tacometro.to_sql("tacometro",engine)



# %%

conteos_adherencia=pd.read_csv("Funciones Objetivo/conteos_adherencia.csv")
conteos_adherencia.columns=map(str.lower,conteos_adherencia.columns)

conteos_adherencia.to_sql("conteos_adherencia2",engine)

# %%


intensidad_region=pd.read_csv("Funciones Objetivo/intensidad_region.csv")
intensidad_region.columns=map(str.lower,intensidad_region.columns)

intensidad_region.to_sql("intensidad_region",engine)

# %%
