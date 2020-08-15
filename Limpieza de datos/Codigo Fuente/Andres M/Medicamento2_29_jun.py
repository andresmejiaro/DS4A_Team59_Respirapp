# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'

# %%
### Limpieza del Archivo de Medicamentos, incluye calculos de variables necesarias para 
### calcular la adherencia


# %%
import pandas as pd
from datetime import timedelta
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer,MissingIndicator 

medicamentos=pd.read_excel("/mnt/Storage/ds4a/Proyecto Omnivida/git-Omnivida/datos originales/Medicamentos.xlsx")


# %%
### Renombramiento de columnas segun el estilo acordado


# %%
medicamentos.columns=[x.upper() for x in medicamentos.columns ]
medicamentos.rename(columns={"ID":"ID_PACIENTE"},inplace=True)
medicamentos.rename(columns={"DESCRIPCION_PRESTACION":"NOMBRE_MEDICAMENTO"},inplace=True)


# %%
medicamentos.columns


# %%
### Revision Columnas

## ID Paciente
print(medicamentos.ID_PACIENTE.drop_duplicates().count())
print(medicamentos.ID_PACIENTE.isna().sum())
print(medicamentos.ID_PACIENTE.isnull().sum())


# %%
### Fecha Emision

medicamentos.FECHA_EMISION=pd.to_datetime(medicamentos.FECHA_EMISION)
print(medicamentos.FECHA_EMISION.min())
print(medicamentos.FECHA_EMISION.max())
print(medicamentos.FECHA_EMISION.isna().sum())
print(medicamentos.FECHA_EMISION.isnull().sum())


# %%
### Regional Eps Descr

medicamentos.REGIONAL_EPS_DESC.drop_duplicates()


# %%
### Codigo de presptacion OP

medicamentos.CODIGO_PRESTACION_OP.drop_duplicates().count()
medicamentos.CODIGO_PRESTACION_OP.isna().sum()
medicamentos.CODIGO_PRESTACION_OP.isnull().sum()
## 1491


# %%
### Descricion prestacion/Nombre del Medicamento 

##'CODIGO_DIAGNOSTICO_EPS_OP', 'DIAGNOSTICO_EPS_DESC',
##       'NUMERO_CANTIDAD_PRESTACIONES']

print(medicamentos.NOMBRE_MEDICAMENTO.drop_duplicates().count())
print(medicamentos.NOMBRE_MEDICAMENTO.isna().sum())
print(medicamentos.NOMBRE_MEDICAMENTO.isnull().sum())


# %%
### CODIGO_DIAGNOSTICO EPS

print(medicamentos.CODIGO_DIAGNOSTICO_EPS_OP.drop_duplicates().count())
print(medicamentos.CODIGO_DIAGNOSTICO_EPS_OP.isna().sum())
print(medicamentos.CODIGO_DIAGNOSTICO_EPS_OP.isnull().sum())
medicamentos.CODIGO_DIAGNOSTICO_EPS_OP.head()


# %%
## Diagnostico Hipertension parece ser Rinitis Alergica y Urticaria

print(medicamentos.DIAGNOSTICO_EPS_DESC.drop_duplicates().count())
print(medicamentos.DIAGNOSTICO_EPS_DESC.isna().sum())
print(medicamentos.DIAGNOSTICO_EPS_DESC.isnull().sum())
medicamentos.DIAGNOSTICO_EPS_DESC.value_counts().head(10)


# %%
print(medicamentos.NUMERO_CANTIDAD_PRESTACIONES.isna().sum())
print(medicamentos.NUMERO_CANTIDAD_PRESTACIONES.isnull().sum())

medicamentos[medicamentos.NUMERO_CANTIDAD_PRESTACIONES.isna()].FECHA_EMISION.agg(["min","max"])
### Numerp de cantidad de prestaciones debe ser imputado para esta columna, poner comentario de imputación 


# %%
medicamentos[(medicamentos.FECHA_EMISION>=pd.to_datetime("2020-01-20"))&(medicamentos.FECHA_EMISION<=pd.to_datetime("2020-01-27"))].REGIONAL_EPS_DESC.value_counts()


# %%
### Las siguientes columnas de procesamiento y limpieza se deben añadir: Imputacion del campo NUMERO_CANTIDAD_PRESTACIONES
### Una Dummy que indique si hay imputacion en el anterior
### una columna de agrupamiento de los medicamentos que nos interesan

## Dejar listo para los script que crean las bases a discutir


# %%
medicamentos.columns
medicamentos=medicamentos.groupby(["ID_PACIENTE",'FECHA_EMISION','CODIGO_PRESTACION_OP']).agg("max").reset_index()


# %%
def dum_sign(dummy_col, threshold=0.1):

    # removes the bind
    dummy_col = dummy_col.copy()

    # what is the ratio of a dummy in whole column
    count = pd.value_counts(dummy_col) / len(dummy_col)

    # cond whether the ratios is higher than the threshold
    mask = dummy_col.isin(count[count > threshold].index)

    # replace the ones which ratio is lower than the threshold by a special name
    dummy_col[~mask] = "others"

    return pd.get_dummies(dummy_col, prefix=dummy_col.name)



#medicamentos2=pd.get_dummies(medicamentos)
#medicamentos2.FECHA_EMISION=medicamentos2.FECHA_EMISION.apply(lambda x: x.timestamp())

#medicamentos2.sum(axis=1)

#medicamentos_imputed=IterativeImputer(random_state=141854)
#medicamentos_imputed.fit_transform(medicamentos2)


# %%
medicamentos.columns

dum_reg=pd.get_dummies(medicamentos.REGIONAL_EPS_DESC)
dum_medicamento=dum_sign(medicamentos.NOMBRE_MEDICAMENTO,0.01)
dum_diag=dum_sign(medicamentos.DIAGNOSTICO_EPS_DESC,0.01)

aver=pd.concat([dum_reg,dum_medicamento,dum_diag,
                medicamentos.FECHA_EMISION.apply(lambda x: x.timestamp()),
                medicamentos.NUMERO_CANTIDAD_PRESTACIONES],axis=1)

medicamentos_imputed=IterativeImputer(random_state=141854)
sal=medicamentos_imputed.fit_transform(aver)


# %%
medicamentos["NumeroCantidadPrestacionesImputado"]=sal[:,-1]


# %%
medicamentos["NumeroCantidadPrestacionesImputadoInd"]=pd.isna(medicamentos.NUMERO_CANTIDAD_PRESTACIONES).astype(int)


# %%
medicamentos[medicamentos.NumeroCantidadPrestacionesImputadoInd==1]


# %%
## El objetivo de estos script es crear los casos de observación de adherencia. 
## La metodologia consiste en ver si existe otra entrega de medicación cercana al dia final 
## para las entregas de medicacion (un delta de 5 dias es posible)
## Existen casos y lecturas que complican la situación se puede añadir una lectura de "seguridad"
## que es 1 si el medicamento es el mismo o 0 si solo existe otro medicamento.


# %%
diagnosticos=pd.read_excel("/mnt/Storage/ds4a/Proyecto Omnivida/git-Omnivida/Bases limpias/Codigo Fuente/Andres M/Diagnostico.xlsx")
diagnosticos.drop(columns="Unnamed: 0",inplace=True)


# %%
medicamentos=medicamentos.merge(diagnosticos,how="left")


# %%
tipo_med=pd.read_excel("/mnt/Storage/ds4a/Proyecto Omnivida/git-Omnivida/Bases limpias/Codigo Fuente/Andres M/Unico_Medicamento.xlsx")


# %%
tipo_med.columns


# %%
medicamentos=medicamentos.merge(tipo_med,how="left")


# %%
print(medicamentos.shape)
print(medicamentos.columns)


# %%
medicamentos.to_excel("medicamentos_limpio_29jun.xlsx")


# %%


px.histogram(medicamentos[
    medicamentos["NOMBRE_MEDICAMENTO"]=="FORMOTEROL FUMARATO/BUDESONIDA"],
    x='DIAGNOSTICO_EPS_DESC')

# %%
