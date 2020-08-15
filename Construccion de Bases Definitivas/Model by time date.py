
#%%
import pandas as pd 
from dateutil.relativedelta import relativedelta
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
import os
import calendar
os.chdir("/home/andres/ds4a/Proyecto Omnivida/git-Omnivida")



# %%

adherencia=pd.read_csv("Resultados Modelo/20200801_Res_Modelo_Adh_Mod_2.csv")

# %%

adherencia


#%%
adherencia.FE_ACTUALIZA=pd.to_datetime(adherencia.FE_ACTUALIZA)

#%%

adherencia.year=adherencia.FE_ACTUALIZA.apply(lambda x: x.year)
adherencia.month=adherencia.FE_ACTUALIZA.apply(lambda x: x.month)

#%%

departartment=adherencia.DEPARTMENT.drop_duplicates()
city=adherencia.CITY.drop_duplicates()
years=adherencia.year.drop_duplicates()
months=adherencia.month.drop_duplicates()

#%%
indice=pd.MultiIndex.from_product([departartment,city,years,months],names=["DEPARTMENT","CITY","years","months"])
cruce_g=pd.DataFrame(index=indice).reset_index()


#%%
abc=cruce_g.apply(lambda x: calendar.monthrange(x.years,x.months)[1],axis=1)

# %%
cruce_g["FE_BASE"]=pd.to_datetime(cruce_g.years.astype(str)+\
"-"+cruce_g.months.astype(str)+"-"+abc.astype(str))


# %%

cruce_g.sort_values("FE_BASE",inplace=True)
adherencia.sort_values("FE_ACTUALIZA",inplace=True)

# %%

base_total=pd.merge_asof(cruce_g,adherencia,by=["DEPARTMENT","CITY"],left_on="FE_BASE",right_on="FE_ACTUALIZA")


# %%
filtro=~pd.isna(base_total.FE_ACTUALIZA)
filtro2=base_total.FE_BASE-base_total.FE_ACTUALIZA<365*timedelta(days=1)    
filtro2

# %%

base_total=base_total[filtro&filtro2]

# %%

#%%

base_subir=base_total.loc[:,["years","months",'DEPARTMENT',
       'CITY','FACT_Alcohol_Abusive - No dependence',
       'FACT_Alcohol_Excepcional', 'FACT_Alcohol_Moderate', 'FACT_Alcohol_No',
       'FACT_Alcohol_Social drinker', 'FACT_Tobacco_16+ daily',
       'FACT_Tobacco_6-15 daily', 'FACT_Tobacco_<5 daily', 'FACT_Tobacco_No',
       'FACT_Tobacco_Pasive', 'FACT_Tobacco_Yes', 'FACT_Act_Bin_NoRecord',
       'FACT_Act_Bin_LT18', 'FACT_Act_Bin_LT22', 'FACT_Act_Bin_GT22',
       'FACT_Dias desde RAM', 'FACT_NumEntrevistas_1_anio',
       'FACT_NumNoAdherencias_1_anio', 'FACT_PropAdherencia_1_anio',
       'FACT_NumAdherencias_3_anio', 'FACT_NumEntrevistas_3_anio',
       'FACT_NumNoAdherencias_3_anio', 'FACT_PropAdherencia_3_anio',
       'FACT_NumAdherencias_5_anio', 'FACT_NumEntrevistas_5_anio',
       'FACT_NumNoAdherencias_5_anio', 'FACT_PropAdherencia_5_anio',
       'FACT_Ratio6m_Oral', 'FACT_NM_IMC']]

#base_subir.iloc[:,4:]=base_subir.iloc[:,4:].apply(lambda x:pd.to_numeric(x,errors="coerce"))      


#%%


base_subir=base_subir.groupby(["years","months",'DEPARTMENT',
       'CITY']).mean()
base_subir=base_subir.reset_index()

# %%

base_subir[(base_subir.years==2019)&(base_subir.CITY=="BOGOTA")&(base_subir.months==12)].iloc[0,:]

# %%

base_subir.to_csv("Funciones Objetivo/intensidad_region.csv")

# %%

