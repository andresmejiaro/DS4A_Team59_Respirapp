# %%
import pandas as pd 
from sklearn.model_selection import train_test_split 
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
import os
os.chdir("/home/andres/ds4a/Proyecto Omnivida/git-Omnivida")




# %%

def try_year(a): 
    try: 
        return relativedelta(a.FECHA_EMISION,a.BIRTHDATE).years 
    except: 
        return pd.NaT


def Antecedentes_cumu(Antecedentes,ID_PACIENTE,FE_ACTUALIZA):
     _Antecedentes_=Antecedentes[(Antecedentes.ID_PACIENTE==ID_PACIENTE) & (Antecedentes.FE_ACTUALIZA<=FE_ACTUALIZA)]
     _Antecedentes_=_Antecedentes_.iloc[:,23:31].agg("max")
     _Antecedentes_["ID_PACIENTE"]=ID_PACIENTE
     _Antecedentes_["FE_ACTUALIZA"]=FE_ACTUALIZA
     return _Antecedentes_   
def Cuenta_6_meses_12(adherencia,ID_PACIENTE,FECHA):
    meses6=adherencia.loc[(adherencia.ID_PACIENTE==ID_PACIENTE)&\
        (adherencia.FECHA_EMISION>FECHA-timedelta(days=182))&\
           (adherencia.FECHA_EMISION<FECHA) ,["TiempoEntreFormulas",
        "TiempoEsperadoEntreFormulas"]]
    meses12=adherencia.loc[(adherencia.ID_PACIENTE==ID_PACIENTE)&\
        (adherencia.FECHA_EMISION>FECHA-timedelta(days=365))&\
           (adherencia.FECHA_EMISION<FECHA),["TiempoEntreFormulas",
        "TiempoEsperadoEntreFormulas"]]

    meses6=meses6.agg("sum")
    meses12=meses12.agg("sum")
    _toreturn_=pd.Series({"TiempoEntreFormulas6m":meses6[0],
                        "TiempoEsperadoEntreFormulas6m":meses6[1],
                        "Ratio6m":meses6[1]/meses6[0],
                        "TiempoEntreFormulas12m":meses12[0],
                        "TiempoEsperadoEntreFormulas12m":meses12[1],
                        "Ratio12m":meses12[1]/meses12[0],})
    return _toreturn_


## Estructura: La clase MedicamentosPipe lee una base, ya sea medicamentos o biologicos, dentro de esa clase se cargan los split
## en train/test, las bases necesarias para la carga de cada medicamento, si hay una base de la frecuencia (es decir si las dosis son
# diaras o menuales)

## dentro de esta clase se crean elementos de la clase medicamentos, dentro de estos van las bases ya separadas de este medicamento
## tanto por test y train y juntas con la base grande.

# %%
#Cuenta_6_meses_1_a(base_prin_medicamentos.MONTELUKAST.train_grande,557377,pd.to_datetime("2017-5-29"))
# %%
#Antecedentes_cumu(base_prin_medicamentos.Antecedentes,653834,pd.to_datetime("2010-12-12"))
# %%
#base_prin_medicamentos.Antecedentes.apply(lambda x: Antecedentes_cumu(base_prin_medicamentos.Antecedentes,x.ID_PACIENTE,x.FE_ACTUALIZA),axis=1)
#%%

class MedicamentosPipe:
    
    def __init__(self, base_nombre):
        self.base=pd.read_excel("Bases limpias/"+base_nombre)
        self.base=self.base[self.base.DadoPrinPara=="Asma"]
        self.base_nombre=base_nombre
        self.cargar_limpias=0
    
    def crea_split(self,random_state=None,test_size=0.33):
             
        
        ## divide base
        self.base_train, self.base_test=train_test_split(self.base["ID_PACIENTE"].drop_duplicates(),
                                                        test_size=test_size,random_state=random_state)
        
        #escribe resultados a disco
        self.base_test.to_csv("Funciones Objetivo/"+self.base_nombre.split(".")[0]+"_test_sample.csv")
        self.base_train.to_csv("Funciones Objetivo/"+self.base_nombre.split(".")[0]+"_train_sample.csv")
        self.base_train=self.base_train.reset_index()
        self.base_test=self.base_test.reset_index()
        return

    def cargar_bases_limpias(self):
        if self.cargar_limpias==1:
            print("Bases ya cargadas. se esperaba esto?")
            return 
        self.datos_basicos=pd.read_csv("Bases limpias/DatosBasicosL_10_jul_GM.csv")
        #self.datos_basicos.rename(columns={"ID":"ID_PACIENTE"},inplace=True)
        self.datos_basicos["BIRTHDATE"]=pd.to_datetime(self.datos_basicos["BIRTHDATE"])

        self.habitos=pd.read_csv("Bases limpias/HabitosL_29_jun_GM.csv")
        #self.habitos.rename(columns={"DS_IDENTIFICACION":"ID_PACIENTE"},inplace=True)
        self.habitos.FE_REGISTRO=pd.to_datetime(self.habitos.FE_REGISTRO)
        
        self.RAM=pd.read_excel("Bases limpias/Farmaco_RAM_limpia_18_jun_AM.xlsx")
        self.RAM.sort_values("FECHA_INICIO_REACCION")
        
        self.Calidad_Vida=pd.read_excel("Bases limpias/Calidad de vidaNew_20_jun_AG.xlsx")#
        self.Calidad_Vida=self.Calidad_Vida.loc[:,"ID_PACIENTE":"0_100"].pivot_table(
            index=["ID_PACIENTE","FE_ALTA"],columns="DIMENSIONES",
            values="0_100").reset_index().sort_values("FE_ALTA")


        self.ACT=pd.read_csv("Bases limpias/ACT_consolidada_26_junio_Ariel.csv")
        self.ACT=self.ACT.loc[:,
                    ['FE_RESULTADO', 'ID', 'NM_PUNTAJE']].sort_values('FE_RESULTADO')
        self.ACT.FE_RESULTADO=pd.to_datetime(self.ACT.FE_RESULTADO)
        self.ACT.rename(columns={ 'ID':"ID_PACIENTE",
             'NM_PUNTAJE':'ACT_NM_PUNTAJE'},inplace=True)


        self.BMI=pd.read_excel("Bases limpias/med_peso_y_talla_3_jul_Cata.xlsx")
        self.BMI=self.BMI.loc[:,['ID_PACIENTE',"FE_ALTA","NM_IMC","NM_PESO","NM_TALLA",
            "NM_TALLA","ClasificacionImcIngles"]]
        self.BMI=self.BMI.sort_values("FE_ALTA")
        self.BMI.rename(columns={"FE_ALTA":"FE_BMI"},inplace=True)
        
        self.Hospitalizacion=pd.read_csv("Bases limpias/HospitalizacionesL_29_jun_GM.csv")
        #self.Hospitalizacion.rename(columns={"ID":"ID_PACIENTE"},inplace=True)
        self.Hospitalizacion.FECHA_INGRESO=pd.to_datetime(self.Hospitalizacion.FECHA_INGRESO)
        self.Hospitalizacion.FECHA_EGRESO=pd.to_datetime(self.Hospitalizacion.FECHA_EGRESO)
        self.Hospitalizacion.FechaIngresoDT=pd.to_datetime(self.Hospitalizacion.FechaIngresoDT)
        self.Hospitalizacion.FechaEgresoDT=pd.to_datetime(self.Hospitalizacion.FechaEgresoDT)

        self.Antecedentes=pd.read_excel("Bases limpias/antecedentes_patologicos_3_jul.xlsx")
        self.Antecedentes.FE_ACTUALIZA=pd.to_datetime(self.Antecedentes.FE_ACTUALIZA)
        self.Antecedentes2=self.Antecedentes.apply(
            lambda x: Antecedentes_cumu(self.Antecedentes,x.ID_PACIENTE,x.FE_ACTUALIZA),axis=1)
        
        self.Antecedentes2=self.Antecedentes2.sort_values("FE_ACTUALIZA")



        self.cargar_limpias=1
        pass

    def crea_medicamento(self,NOMBRE_MEDICAMENTO,columna,Frecuencia_Mensual=30,tolerancia_dias=5):
        setattr(self,NOMBRE_MEDICAMENTO,Medicamento(NOMBRE_MEDICAMENTO,columna,Frecuencia_Mensual,tolerancia_dias))
        return   

#%%
class Medicamento:
    def __init__(self,NOMBRE_MEDICAMENTO,columna,Frecuencia_Mensual=30,tolerancia_dias=5):
        self.NOMBRE_MEDICAMENTO=NOMBRE_MEDICAMENTO
        self.Frecuencia_Mensual=Frecuencia_Mensual
        self.columna=columna
        self.tolerancia_dias=tolerancia_dias
        return

    def marca_fila(self,base_med,ID_PACIENTE,FECHA_EMISION,
            NUMERO_CANTIDAD_PRESTACIONES,Tratamiento,Categoria):
        NombreAdherencia=self.NOMBRE_MEDICAMENTO
        columna=self.columna
        tolerancia_dias=self.tolerancia_dias
        Frecuencia_Mensual=self.Frecuencia_Mensual
        #los input corresponden a campos de la tabla Medicamentos, Frecuencia_Diaria es la cantidad 
        #de ese medicamento si la aplicacion fuera diaria, ej si es un inhalador al mes usar 1, si es un
        # si es una aplicacion diaria usar 30
        # base med es la base donde se realiza la busqueda
        # Fecha Emision formato datetime de pandas
        _tiempo_esperado_=30*NUMERO_CANTIDAD_PRESTACIONES/Frecuencia_Mensual
        #_Fecha_Fin_inf_=_Fecha_Fin_-timedelta(days=tolerancia_dias)
        #_Fecha_Fin_sup_=_Fecha_Fin_+timedelta(days=tolerancia_dias)
        _filtro_fin_med_=(base_med.ID_PACIENTE==ID_PACIENTE) &(base_med["FECHA_EMISION"]>FECHA_EMISION)
        _filtro_fin_med_=_filtro_fin_med_ &(base_med[columna]==NombreAdherencia)
        _medicamentos_local_=base_med[_filtro_fin_med_]
        _fecha_prox_formula_=_medicamentos_local_.loc[base_med.ID_PACIENTE==ID_PACIENTE,"FECHA_EMISION"].min()
        _tiempo_entre_form_=(_fecha_prox_formula_-FECHA_EMISION).days
        _fecha_esperada_reclamacion_=FECHA_EMISION+_tiempo_esperado_*timedelta(days=1)
        if _medicamentos_local_.shape[0]==0:
            ## marca como no adherente 
            _adherencia_=float("NaN")
            _comentario_="ultimo registro"
            #print("No adherente")
            pass
        elif _tiempo_entre_form_<=_tiempo_esperado_+tolerancia_dias:
            ## marca como adherente marca continuidad medicamento
            #print("Adherente, Continuidad")
            _adherencia_=1
            _comentario_="adherente"
            pass
        elif _tiempo_entre_form_<2*_tiempo_esperado_:
            ## marca como aderente no continuidad del medicamento
            #print("Adherente, No Continuidad")
            _adherencia_=0
            _comentario_="no adherente"
            pass
        else:
            _adherencia_=0
            _comentario_="abandono/ciclo corto"
        #print(_medicamentos_local_)
        _return_=pd.Series({"ID_PACIENTE":ID_PACIENTE,
                            "FECHA_EMISION":FECHA_EMISION,
                            "Tratameinto":Tratamiento,
                            "Categoria":Categoria,
                            "FechaSiguienteRecla":_fecha_prox_formula_,
                            columna:NombreAdherencia,
                            "FechaEsperadaReclamacion":_fecha_esperada_reclamacion_,
                            "AdherenciaMed":_adherencia_,
                            "Comentario":_comentario_,
                        "TiempoEntreFormulas":_tiempo_entre_form_,
                        "TiempoEsperadoEntreFormulas":_tiempo_esperado_,
                            "NUMERO_CANTIDAD_PRESTACIONES":NUMERO_CANTIDAD_PRESTACIONES})
        return _return_
        

    def crea_base(self,MedicamentosPipe):
        base_med=MedicamentosPipe.base
        IDtrain=MedicamentosPipe.base_train
        _base_=self.procesa_medicamentos_df(base_med)
        _base_train_=_base_[_base_.ID_PACIENTE.isin(IDtrain.ID_PACIENTE)]
        _base_test_=_base_[~_base_.ID_PACIENTE.isin(IDtrain.ID_PACIENTE)]
        _base_train_.to_csv("Funciones Objetivo/Train_"+self.NOMBRE_MEDICAMENTO+".csv",index=False)
        _base_test_.to_csv("Funciones Objetivo/Test_"+self.NOMBRE_MEDICAMENTO+".csv",index=False)
        self.train=_base_train_
        self.test=_base_test_
        return  

    def procesa_medicamentos_df(self,base_med):
        _work_base_=base_med[base_med[self.columna]==self.NOMBRE_MEDICAMENTO]
        
        _work_base_=_work_base_.loc[:,[ 'ID_PACIENTE', 'FECHA_EMISION','Categoria',
                'NUMERO_CANTIDAD_PRESTACIONES','Tratamiento']].groupby([ 'ID_PACIENTE',
                     'FECHA_EMISION','Categoria','Tratamiento']).agg("sum").reset_index()
        _adherencia_=_work_base_.apply(lambda x:self.marca_fila(_work_base_,x.ID_PACIENTE,
                                    x.FECHA_EMISION,
                                    x.NUMERO_CANTIDAD_PRESTACIONES,
                                    x.Tratamiento,
                                    x.Categoria
                                    ) ,axis=1)
         
                                                
        _adherencia2_=_adherencia_.sort_values("FECHA_EMISION").loc[:,["ID_PACIENTE",
            "TiempoEntreFormulas","TiempoEsperadoEntreFormulas",
                "FECHA_EMISION"]].groupby(["ID_PACIENTE",
                    "FECHA_EMISION"]).sum().groupby(level=0).cumsum().reset_index(
                        ).rename(columns={"TiempoEntreFormulas":"TiempoEntreFormulasAcum",
                    "TiempoEsperadoEntreFormulas":"TiempoEsperadoEntreFormulasAcum"})

        _adherencia_=_adherencia_.merge(_adherencia2_,on=["FECHA_EMISION","ID_PACIENTE"])
        
        _adherencia_=_adherencia_.sort_values(["ID_PACIENTE","FECHA_EMISION"])
        zz=~_adherencia_.groupby("ID_PACIENTE")["Categoria"].apply(lambda x: x.eq(x.shift(1)))
        zz.rename("Cambio_med",inplace=True)
        _adherencia_=pd.concat([_adherencia_,zz],axis=1)
        return _adherencia_
    

    def juntar_con_limpias(self,MedicamentosPipe,train="Train"):
        if MedicamentosPipe.cargar_limpias==0:
            MedicamentosPipe.cargar_bases_limpias()
            pass
        
        if train=="Train":
            _base_entrenamiento_=self.train
        elif train=="Test":
            _base_entrenamiento_=self.test
        elif train=="SQL":
            ### hacer base total con train y test
            pass
        else:
            ## devolver un error
            pass

        print(_base_entrenamiento_.shape,"Inicio")
        
        _base_entrenamiento_.FECHA_EMISION=pd.to_datetime(_base_entrenamiento_.FECHA_EMISION)
        
        _Tiempos_=_base_entrenamiento_.apply(lambda x: Cuenta_6_meses_12(_base_entrenamiento_,x.ID_PACIENTE,x.FECHA_EMISION),axis=1)
        _base_entrenamiento_=pd.concat([_base_entrenamiento_,_Tiempos_],axis=1,sort=None)
        
        print(_base_entrenamiento_.shape,"Tiempos")

        _db_=MedicamentosPipe.datos_basicos.loc[:,['ID_PACIENTE', 'SEX','DEPARTMENT',
                                                     'CITY', 'STRATUM', 'SOCIOECONOMIC_LEVEL',
                                                     'AFFILIATION_TYPE', 'BIRTHDATE', 'Education',
                                                     'MaritalStatus', 'LifeCyle', 'WorkingStatus',
                                                      'Zone', 'Ocupation']]
        _base_entrenamiento_=_base_entrenamiento_.merge(_db_,how="left")
        _base_entrenamiento_["Edad"]=_base_entrenamiento_.apply(try_year,axis=1)
        
        
        print(_base_entrenamiento_.shape,"Datos Basicos")

        _habitos_=MedicamentosPipe.habitos.loc[MedicamentosPipe.habitos.Types.isin(["Pets",
            "Alcohol","Tobacco","Exercise","Mood"]),
                                ["ID_PACIENTE","FE_REGISTRO","Types","Habits"]]
        _habitos_=_habitos_.pivot_table(index=["ID_PACIENTE","FE_REGISTRO"],columns="Types",
                                values="Habits",aggfunc='first').reset_index()
        _habitos_=_habitos_.sort_values("FE_REGISTRO")
        _base_entrenamiento_=_base_entrenamiento_.sort_values("FECHA_EMISION")
        _base_entrenamiento_=pd.merge_asof(_base_entrenamiento_,_habitos_,by="ID_PACIENTE",
                                right_on="FE_REGISTRO",left_on="FECHA_EMISION")
        
        
        print(_base_entrenamiento_.shape,"Habitos")

        _RAM_=MedicamentosPipe.RAM[~MedicamentosPipe.RAM["FECHA_INICIO_REACCION"].isnull()]
        _RAM_=_RAM_.sort_values("FECHA_INICIO_REACCION").loc[:,["ID_PACIENTE",'MEDICAMENTO_SOSPECHOSO','FECHA_INICIO_REACCION']]
        _base_entrenamiento_=pd.merge_asof(_base_entrenamiento_,_RAM_,by="ID_PACIENTE",right_on="FECHA_INICIO_REACCION",left_on="FECHA_EMISION",direction="forward")
        _base_entrenamiento_["Ram"]=_base_entrenamiento_["FechaSiguienteRecla"] > _base_entrenamiento_["FECHA_INICIO_REACCION"]
        _base_entrenamiento_["FECHA_INICIO_REACCION"][~_base_entrenamiento_["Ram"]]=pd.NaT
        _base_entrenamiento_["MEDICAMENTO_SOSPECHOSO"][~_base_entrenamiento_["Ram"]]=pd.NaT
             
        
        
        print(_base_entrenamiento_.shape,"RAM")

        _RAM2_=_RAM_.sort_values("FECHA_INICIO_REACCION").loc[:,["ID_PACIENTE",'MEDICAMENTO_SOSPECHOSO','FECHA_INICIO_REACCION']]
        _base_entrenamiento_=pd.merge_asof(_base_entrenamiento_,_RAM_,by="ID_PACIENTE",right_on="FECHA_INICIO_REACCION",left_on="FECHA_EMISION",suffixes=['_Actual', '_Anterior'])
        _base_entrenamiento_["Dias desde RAM"]=(pd.to_datetime(_base_entrenamiento_["FECHA_EMISION"]) - pd.to_datetime(_base_entrenamiento_["FECHA_INICIO_REACCION_Anterior"])).apply(lambda x: x.days)
        
        print(_base_entrenamiento_.shape,"RAM2")


        _base_entrenamiento_=pd.merge_asof(_base_entrenamiento_,MedicamentosPipe.Calidad_Vida,
                        by="ID_PACIENTE",right_on="FE_ALTA",left_on="FECHA_EMISION")
        print(_base_entrenamiento_.shape,"Calidad_Vida")

        
        _base_entrenamiento_=pd.merge_asof(_base_entrenamiento_,MedicamentosPipe.ACT,by="ID_PACIENTE",
                                            right_on="FE_RESULTADO",left_on="FECHA_EMISION")
        print(_base_entrenamiento_.shape,"ACT")

        _base_entrenamiento_=pd.merge_asof(_base_entrenamiento_,MedicamentosPipe.BMI,by="ID_PACIENTE",
                                            right_on="FE_BMI",left_on="FECHA_EMISION")
        print(_base_entrenamiento_.shape,"BMI")
        
        _Hospitalizacion_= _base_entrenamiento_.loc[:,["ID_PACIENTE","FECHA_EMISION"]].drop_duplicates().apply(lambda x: self.marca_fila_hospitalizacion(MedicamentosPipe,x.ID_PACIENTE,x.FECHA_EMISION),axis=1)
        _base_entrenamiento_=pd.merge(_base_entrenamiento_,_Hospitalizacion_,on=["ID_PACIENTE","FECHA_EMISION"])

        print(_base_entrenamiento_.shape,"Hospitalizacion")
                                            
        
        _base_entrenamiento_=pd.merge_asof(_base_entrenamiento_,MedicamentosPipe.Antecedentes2,by="ID_PACIENTE",
                                            right_on="FE_ACTUALIZA",left_on="FECHA_EMISION")
        
        print(_base_entrenamiento_.shape,"Antecedentes")
        if train=="Train":
            texto="train"
        elif train=="Test":
            texto="test"
        elif train=="SQL":
            texto="total"
        else:
            ## devolver un error
            pass
        
        _base_entrenamiento_.to_csv("Funciones Objetivo/"+MedicamentosPipe.base_nombre+"_"+self.NOMBRE_MEDICAMENTO+"_"+texto+"_trabajo.csv")
        

        if train=="SQL":
            _base_entrenamiento_.to_sql(self.NOMBRE_MEDICAMENTO,engine) ## ojo solo usar minusculas para subir



        if train=="Train":
            self.train_grande=_base_entrenamiento_
        elif train=="Test":
            self.test_grande=_base_entrenamiento_
        elif train=="SQL":
            self.total_grande=_base_entrenamiento_
            pass
        else:
            ## devolver un error
            pass

        
        
            

        print(_base_entrenamiento_.shape)
        return 
    
    
        
    
    
    def marca_fila_hospitalizacion(self,MedicamentosPipe,ID_PACIENTE,FECHA_EMISION):
        
        _Hospitalizacion_=MedicamentosPipe.Hospitalizacion.copy()
        _filtro_=(_Hospitalizacion_.ID_PACIENTE==ID_PACIENTE)
        _filtro_=_filtro_&(_Hospitalizacion_.FechaIngresoDT<FECHA_EMISION)
        _filtro_=_filtro_&(_Hospitalizacion_.FechaEgresoDT>FECHA_EMISION-timedelta(days=365))
        _Hospitalizacion_=_Hospitalizacion_[_filtro_]
        
        _dias_=_Hospitalizacion_.loc[:,['DIAS_UCI', 'DIAS_UCE']].sum()
        _conteo_=_Hospitalizacion_.shape[0]

        _dias_resp_=_Hospitalizacion_.loc[_Hospitalizacion_.CAPITULO=="C10 - ENFERMEDADES DEL SISTEMA RESPIRATORIO",
                    ['DIAS_UCI', 'DIAS_UCE']].sum()
        
        _conteo_resp_=_Hospitalizacion_.loc[_Hospitalizacion_.CAPITULO=="C10 - ENFERMEDADES DEL SISTEMA RESPIRATORIO"].shape[0]
        if _Hospitalizacion_.shape[0]>0:
            _ultima_hosp_= _Hospitalizacion_.NOM_DIAG.tail(1)
            
        else:
            _ultima_hosp_= pd.NaT

        
        return pd.Series({"ID_PACIENTE":ID_PACIENTE,
                        "FECHA_EMISION":FECHA_EMISION,
                        #"DiagnosticoUltimaHospitalizacion":_ultima_hosp_[0],
                        "DiasUCIUltimoAnio":_dias_[0],
                        "DiasUCEUltimoAnio":_dias_[1],
                        "NumHospUltimoAnio":_conteo_,
                        "DiasUCIRespUltimoAnio":_dias_resp_[0],
                        "DiasUCERespUltimoAnio":_dias_resp_[1],
                        "NumHospRespUltimoAnio":_conteo_resp_})
    

   
        
 

## esta función toma un registro de medicamento y regresa la marcación con respecto a 
## adherencia, si es una continuación del mismo medicamento retorna un dataframe de pandas 
## de una sola fila

#%%


### prueba ciclo de trabajo de principio a fin con Medicamentos -> Categoria -> Montelukast

base_prin_medicamentos=MedicamentosPipe("medicamentos_limpio_29_jun_AM.xlsx")
base_prin_medicamentos.crea_split()

# %%
base_prin_medicamentos.crea_medicamento("Oral","Tratamiento",30)
base_prin_medicamentos.Oral.crea_base(base_prin_medicamentos)
base_prin_medicamentos.Oral.juntar_con_limpias(base_prin_medicamentos)
#base_prin_medicamentos.Oral.juntar_con_limpias(base_prin_medicamentos,train="Test")

# %%
base_prin_medicamentos.crea_medicamento("Inhaladores Mantenimiento","Tratamiento",1)
getattr(base_prin_medicamentos,"Inhaladores Mantenimiento").crea_base(base_prin_medicamentos)
getattr(base_prin_medicamentos,"Inhaladores Mantenimiento").juntar_con_limpias(base_prin_medicamentos)
# %%
base_prin_medicamentos.crea_medicamento("Inhaladores Emergencia","Tratamiento",1)
getattr(base_prin_medicamentos,"Inhaladores Emergencia").crea_base(base_prin_medicamentos)
getattr(base_prin_medicamentos,"Inhaladores Emergencia").juntar_con_limpias(base_prin_medicamentos)

# %%
base_prin_medicamentos.crea_medicamento("Biologico","Tratamiento",30)
base_prin_medicamentos.Biologico.crea_base(base_prin_medicamentos)
base_prin_medicamentos.Biologico.juntar_con_limpias(base_prin_medicamentos)

# %%
base_prin_medicamentos.crea_medicamento("OMALIZUMAB","Categoria",1)
base_prin_medicamentos.OMALIZUMAB.crea_base(base_prin_medicamentos)
base_prin_medicamentos.OMALIZUMAB.juntar_con_limpias(base_prin_medicamentos)




# %%
baseacomp=base_prin_medicamentos.Oral.train_grande


# %%

baseacomp=baseacomp.sort_values(["ID_PACIENTE","FECHA_EMISION"])
#print(baseacomp.loc[:,["ID_PACIENTE","FECHA_EMISION","Categoria"]].head())
zz=baseacomp.groupby("ID_PACIENTE")["Categoria"].apply(lambda x:(x==x.shift()) )
zz.rename("Cambio_med",inplace=True)
#print(baseacomp.loc[:,["ID_PACIENTE","FECHA_EMISION","Categoria","res"]].head())


baseacomp=pd.concat([baseacomp,zz],axis=1)


# %%
mm=baseacomp.loc[:,["ID_PACIENTE","FECHA_EMISION","Categoria","Cambio_med"]]
# %%

# %%
zz

# %%

abc=pd.Series([1,1,1,0,1,1,1,0])


# %%
~(abc.shift()==abc)

# %%

def informacion_basica(ID_PACIENTE):
    _interna_=base_prin_medicamentos.Oral.train_grande[base_prin_medicamentos.Oral.train_grande.ID_PACIENTE==ID_PACIENTE]
    _last_=_interna_[_interna_.FECHA_EMISION==max(_interna_.FECHA_EMISION)]
    _bd_=_interna_["BIRTHDATE"].max()
    _to_return_=pd.Series({"Edad":relativedelta(pd.to_datetime("today"),_bd_).years,
                            "Genero":_interna_.loc[_interna_.FECHA_EMISION==max(_interna_.FECHA_EMISION),"SEX"].to_list()[0],
                            "Rinitis":_interna_.loc[_interna_.FECHA_EMISION==max(_interna_.FECHA_EMISION),"RinitisAlergica"].to_list()[0],
                            "Urticaria":_interna_.loc[_interna_.FECHA_EMISION==max(_interna_.FECHA_EMISION),"Urticaria"].to_list()[0],
                            "Tumor":_interna_.loc[_interna_.FECHA_EMISION==max(_interna_.FECHA_EMISION),"Tumor"].to_list()[0],
                            "Circulatorio":_interna_.loc[_interna_.FECHA_EMISION==max(_interna_.FECHA_EMISION),"Circulatorio"].to_list()[0],
                            "Digestivo":_interna_.loc[_interna_.FECHA_EMISION==max(_interna_.FECHA_EMISION),"Digestivo"].to_list()[0],
                            "RespiratorioNoAsmaRinitis":_interna_.loc[_interna_.FECHA_EMISION==max(_interna_.FECHA_EMISION),"RespiratorioNoAsmaRinitis"].to_list()[0],
                            "Otros":_interna_.loc[_interna_.FECHA_EMISION==max(_interna_.FECHA_EMISION),"Otros"].to_list()[0],
                        })
    return _to_return_

# %%
informacion_basica(500588)

# %%
relativedelta(informacion_basica(500588),pd.to_datetime("today"))
# %%
# %%

base_prin_medicamentos.Oral.train.to_sql("oral",engine) ## ojo solo usar minusculas para subir

# %%
