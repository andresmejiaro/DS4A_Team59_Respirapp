
#%%
import pandas as pd 
from dateutil.relativedelta import relativedelta
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
import os
import calendar
os.chdir("/home/andres/ds4a/Proyecto Omnivida/git-Omnivida")



# %%

adherencia=pd.read_excel("Bases limpias/AdherenciaNew_20_jun_AG.xlsx")

# %%
adherencia.columns

#%%

db=pd.read_csv("Bases limpias/DatosBasicosL_10_jul_GM.csv")
db=db.loc[:,['ID_PACIENTE','DEPARTMENT', 'CITY']]

# %%

#print(adherencia.shape)
adherencia=adherencia.merge(db)
#print(adherencia.shape)


#%%
adherencia.FE_ENTREVISTA=pd.to_datetime(adherencia.FE_ENTREVISTA)

#%%

adherencia.year=adherencia.FE_ENTREVISTA.apply(lambda x: x.year)
adherencia.month=adherencia.FE_ENTREVISTA.apply(lambda x: x.month)

#%%

pacientes=adherencia.ID_PACIENTE.drop_duplicates()
years=adherencia.year.drop_duplicates()
months=adherencia.month.drop_duplicates()

#%%
indice=pd.MultiIndex.from_product([pacientes,years,months],names=["ID_PACIENTE","years","months"])
cruce_g=pd.DataFrame(index=indice).reset_index()


#%%
abc=cruce_g.apply(lambda x: calendar.monthrange(x.years,x.months)[1],axis=1)

# %%
cruce_g["FE_BASE"]=pd.to_datetime(cruce_g.years.astype(str)+\
"-"+cruce_g.months.astype(str)+"-"+abc.astype(str))


# %%

cruce_g.sort_values("FE_BASE",inplace=True)
adherencia.sort_values("FE_ENTREVISTA",inplace=True)

# %%

base_total=pd.merge_asof(cruce_g,adherencia,by="ID_PACIENTE",left_on="FE_BASE",right_on="FE_ENTREVISTA")


# %%
filtro=~pd.isna(base_total.FE_ENTREVISTA)
filtro2=base_total.FE_BASE-base_total.FE_ENTREVISTA<365*timedelta(days=1)    
filtro2

# %%

base_total=base_total[filtro&filtro2]
#%%
base_total.columns
# %%

base_subir=base_total.groupby(["years","months",'DEPARTMENT',
       'CITY'])["CUALITATIVO_PONDERADO"].value_counts().unstack().reset_index()



# %%

base_subir.ADHERENTE[pd.isna(base_subir.ADHERENTE)]=0
base_subir["NO APLICA"][pd.isna(base_subir["NO APLICA"])]=0
base_subir['NO ADHERENTE'][pd.isna(base_subir['NO ADHERENTE'])]=0


# %%

base_subir.to_csv("Funciones Objetivo/conteos_adherencia.csv")