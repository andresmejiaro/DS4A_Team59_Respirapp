
# %%
import pandas as pd 
from sklearn.model_selection import train_test_split 
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
import os
os.chdir("/mnt/Storage/ds4a/Proyecto Omnivida/git-Omnivida")




def try_year(a): 
    try: 
        return relativedelta(a.FE_ENTREVISTA,a.BIRTHDATE).years 
    except: 
        return pd.NaT


def Antecedentes_cumu(Antecedentes,ID_PACIENTE,FE_ACTUALIZA):
     _Antecedentes_=Antecedentes[(Antecedentes.ID_PACIENTE==ID_PACIENTE) & (Antecedentes.FE_ACTUALIZA<=FE_ACTUALIZA)]
     _Antecedentes_=_Antecedentes_.iloc[:,23:31].agg("max")
     _Antecedentes_["ID_PACIENTE"]=ID_PACIENTE
     _Antecedentes_["FE_ACTUALIZA"]=FE_ACTUALIZA
     return _Antecedentes_   
def Cuenta_6_meses_12(adherencia,ID_PACIENTE,FECHA,Marca=""):
    meses6=adherencia.loc[(adherencia.ID_PACIENTE==ID_PACIENTE)&\
        (adherencia.FECHA_EMISION>FECHA-timedelta(days=182))&\
           (adherencia.FechaSiguienteRecla<FECHA) ,["TiempoEntreFormulas",
        "TiempoEsperadoEntreFormulas"]]
    meses12=adherencia.loc[(adherencia.ID_PACIENTE==ID_PACIENTE)&\
        (adherencia.FECHA_EMISION>FECHA-timedelta(days=365))&\
           (adherencia.FECHA_EMISION<FECHA),["TiempoEntreFormulas",
        "TiempoEsperadoEntreFormulas"]]

    meses6=meses6.agg("sum")
    meses12=meses12.agg("sum")
    _toreturn_=pd.Series({"ID_PACIENTE":ID_PACIENTE,
                        "FE_ENTREVISTA":FECHA,
                        "TiempoEntreFormulas6m"+Marca:meses6[0],
                        "TiempoEsperadoEntreFormulas6m"+Marca:meses6[1],
                        "Ratio6m"+Marca:meses6[1]/meses6[0],
                        "TiempoEntreFormulas12m"+Marca:meses12[0],
                        "TiempoEsperadoEntreFormulas12m"+Marca:meses12[1],
                        "Ratio12m"+Marca:meses12[1]/meses12[0],})
    return _toreturn_


def Cuenta_Bio(adherencia,ID_PACIENTE,FECHA,Marca=""):
    meses6=adherencia.loc[(adherencia.ID_PACIENTE==ID_PACIENTE)&\
        (adherencia.FECHA_EMISION>FECHA-timedelta(days=182))&\
           (adherencia.FechaSiguienteRecla<FECHA) ,["TiempoEntreFormulas",
        "TiempoEsperadoEntreFormulas"]]
    meses12=adherencia.loc[(adherencia.ID_PACIENTE==ID_PACIENTE)&\
        (adherencia.FECHA_EMISION>FECHA-timedelta(days=365))&\
           (adherencia.FechaSiguienteRecla<FECHA),["TiempoEntreFormulas",
        "TiempoEsperadoEntreFormulas"]]

    meses6["Carga"]=meses6["TiempoEntreFormulas"]<20
    meses12["Carga"]=meses12["TiempoEntreFormulas"]<20
    meses6["Mantiene"]=(meses6["TiempoEntreFormulas"]<40)&(meses6["TiempoEntreFormulas"]>=20)
    meses12["Mantiene"]=(meses12["TiempoEntreFormulas"]<40)&(meses12["TiempoEntreFormulas"]>=20)
    meses6["cuenta"]=1
    meses12["cuenta"]=1
    meses6=meses6.agg("sum")
    meses12=meses12.agg("sum")
    _toreturn_=pd.Series({"ID_PACIENTE":ID_PACIENTE,
                        "FE_ENTREVISTA":FECHA,
                        "Total6m"+Marca:meses6["cuenta"],
                        "Carga6m"+Marca:meses6["Carga"],
                        "Mantiene6m"+Marca:meses6["Mantiene"],
                        "Total12m"+Marca:meses12["cuenta"],
                        "Carga12m"+Marca:meses12["Carga"],
                        "Mantiene12m"+Marca:meses12["Mantiene"],
                        #"TiempoEsperadoEntreFormulas6m"+Marca:meses6[1],
                        #"Ratio6m"+Marca:meses6[1]/meses6[0],
                        #"TiempoEntreFormulas12m"+Marca:meses12[0],
                        #"TiempoEsperadoEntreFormulas12m"+Marca:meses12[1],
                        #"Ratio12m"+Marca:meses12[1]/meses12[0]
                        })
    return _toreturn_


#base_prin_medicamentos.Antecedentes.apply(lambda x: Antecedentes_cumu(base_prin_medicamentos.Antecedentes,x.ID_PACIENTE,x.FE_ACTUALIZA),axis=1)
#%%

class AdherenciaPipe:
    
    def __init__(self, base_nombre):
        self.base=pd.read_excel("Bases limpias/"+base_nombre)
        self.base_nombre=base_nombre
        self.cargar_limpias=0
        self.juntar_con_limpias()
        self.crea_split()
        self.crea_base()
    
    def crea_split(self,random_state=0,test_size=0.23):
             
        
        ## divide base
        self.base_train, self.base_test=train_test_split(self.base["ID_PACIENTE"].drop_duplicates(),
                                                        test_size=test_size,random_state=random_state)
        
        #escribe resultados a disco
        #self.base_test.to_csv("Funciones Objetivo/"+self.base_nombre.split(".")[0]+"_test_sample.csv")
        #self.base_train.to_csv("Funciones Objetivo/"+self.base_nombre.split(".")[0]+"_train_sample.csv")
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

        self.Med_Oral=pd.read_csv("Funciones Objetivo/Consistencia_Oral.csv")
        self.Med_Oral.FECHA_EMISION=pd.to_datetime(self.Med_Oral.FECHA_EMISION)
        self.Med_Oral.FechaSiguienteRecla=pd.to_datetime(self.Med_Oral.FechaSiguienteRecla)

        self.Med_Bio=pd.read_csv("Funciones Objetivo/Consistencia_Bio.csv")
        self.Med_Bio.FECHA_EMISION=pd.to_datetime(self.Med_Bio.FECHA_EMISION)
        self.Med_Bio.FechaSiguienteRecla=pd.to_datetime(self.Med_Bio.FechaSiguienteRecla)
        
        self.Med_I_Eme=pd.read_csv("Funciones Objetivo/Consistencia_Inhaladores Emergencia.csv")
        self.Med_I_Eme.FECHA_EMISION=pd.to_datetime(self.Med_I_Eme.FECHA_EMISION)
        self.Med_I_Eme.FechaSiguienteRecla=pd.to_datetime(self.Med_I_Eme.FechaSiguienteRecla)

        self.Med_I_Mant=pd.read_csv("Funciones Objetivo/Consistencia_Inhaladores Mantenimiento.csv")
        self.Med_I_Mant.FECHA_EMISION=pd.to_datetime(self.Med_I_Mant.FECHA_EMISION)
        self.Med_I_Mant.FechaSiguienteRecla=pd.to_datetime(self.Med_I_Mant.FechaSiguienteRecla)

        self.cargar_limpias=1
        pass
     

    def crea_base(self):
        _base_=self.base
        _base_train_=_base_[_base_.ID_PACIENTE.isin(self.base_train.ID_PACIENTE)]
        _base_test_=_base_[~_base_.ID_PACIENTE.isin(self.base_test.ID_PACIENTE)]
        _base_train_.to_csv("Funciones Objetivo/Train_"+self.base_nombre+".csv",index=False)
        _base_test_.to_csv("Funciones Objetivo/Test_"+self.base_nombre+".csv",index=False)
        self.train=_base_train_
        self.test=_base_test_
        return  

    def juntar_con_limpias(self):
        if self.cargar_limpias==0:
            self.cargar_bases_limpias()
            pass
        
        _base_entrenamiento_=self.base
        
        print(_base_entrenamiento_.shape,"Inicio")
        
        _base_entrenamiento_.FE_ENTREVISTA=pd.to_datetime(_base_entrenamiento_.FE_ENTREVISTA)
        
        #_Tiempos_=_base_entrenamiento_.apply(lambda x: Cuenta_6_meses_12(_base_entrenamiento_,x.ID_PACIENTE,x.FECHA_EMISION),axis=1)
        #_base_entrenamiento_=pd.concat([_base_entrenamiento_,_Tiempos_],axis=1,sort=None)
        
        #print(_base_entrenamiento_.shape,"Tiempos")

        _db_=self.datos_basicos.loc[:,['ID_PACIENTE', 'SEX','DEPARTMENT',
                                                     'CITY', 'STRATUM', 'SOCIOECONOMIC_LEVEL',
                                                     'AFFILIATION_TYPE', 'BIRTHDATE', 'Education',
                                                     'MaritalStatus', 'LifeCyle', 'WorkingStatus',
                                                      'Zone', 'Ocupation']]
        _base_entrenamiento_=_base_entrenamiento_.merge(_db_,how="left")
        _base_entrenamiento_["Edad"]=_base_entrenamiento_.apply(try_year,axis=1)
        
        
        print(_base_entrenamiento_.shape,"Datos Basicos")

        _habitos_=self.habitos.loc[self.habitos.Types.isin(["Pets",
            "Alcohol","Tobacco","Exercise","Mood"]),
                                ["ID_PACIENTE","FE_REGISTRO","Types","Habits"]]
        _habitos_=_habitos_.pivot_table(index=["ID_PACIENTE","FE_REGISTRO"],columns="Types",
                                values="Habits",aggfunc='first').reset_index()
        _habitos_=_habitos_.sort_values("FE_REGISTRO")
        _base_entrenamiento_=_base_entrenamiento_.sort_values("FE_ENTREVISTA")
        _base_entrenamiento_=pd.merge_asof(_base_entrenamiento_,_habitos_,by="ID_PACIENTE",
                                right_on="FE_REGISTRO",left_on="FE_ENTREVISTA")
        
        
        print(_base_entrenamiento_.shape,"Habitos")

        _RAM_=self.RAM[~self.RAM["FECHA_INICIO_REACCION"].isnull()]
        _RAM_=_RAM_.sort_values("FECHA_INICIO_REACCION").loc[:,["ID_PACIENTE",'MEDICAMENTO_SOSPECHOSO','FECHA_INICIO_REACCION']]
        _base_entrenamiento_=pd.merge_asof(_base_entrenamiento_,_RAM_,by="ID_PACIENTE",right_on="FECHA_INICIO_REACCION",left_on="FE_ENTREVISTA",direction="forward")
        _base_entrenamiento_["Ram"]=_base_entrenamiento_["FE_ENTREVISTA"] > _base_entrenamiento_["FECHA_INICIO_REACCION"]
        _base_entrenamiento_["FECHA_INICIO_REACCION"][~_base_entrenamiento_["Ram"]]=pd.NaT
        _base_entrenamiento_["MEDICAMENTO_SOSPECHOSO"][~_base_entrenamiento_["Ram"]]=pd.NaT
             
        
        
        print(_base_entrenamiento_.shape,"RAM")

        _RAM2_=_RAM_.sort_values("FECHA_INICIO_REACCION").loc[:,["ID_PACIENTE",'MEDICAMENTO_SOSPECHOSO','FECHA_INICIO_REACCION']]
        _base_entrenamiento_=pd.merge_asof(_base_entrenamiento_,_RAM_,by="ID_PACIENTE",right_on="FECHA_INICIO_REACCION",left_on="FE_ENTREVISTA",suffixes=['_Actual', '_Anterior'])
        _base_entrenamiento_["Dias desde RAM"]=(pd.to_datetime(_base_entrenamiento_["FE_ENTREVISTA"]) - pd.to_datetime(_base_entrenamiento_["FECHA_INICIO_REACCION_Anterior"])).apply(lambda x: x.days)
        
        print(_base_entrenamiento_.shape,"RAM2")


        _base_entrenamiento_=pd.merge_asof(_base_entrenamiento_,self.Calidad_Vida,
                        by="ID_PACIENTE",right_on="FE_ALTA",left_on="FE_ENTREVISTA")
        print(_base_entrenamiento_.shape,"Calidad_Vida")

        
        _base_entrenamiento_=pd.merge_asof(_base_entrenamiento_,self.ACT,by="ID_PACIENTE",
                                            right_on="FE_RESULTADO",left_on="FE_ENTREVISTA")
        print(_base_entrenamiento_.shape,"ACT")

        _base_entrenamiento_=pd.merge_asof(_base_entrenamiento_,self.BMI,by="ID_PACIENTE",
                                            right_on="FE_BMI",left_on="FE_ENTREVISTA")
        print(_base_entrenamiento_.shape,"BMI")
        
        _Hospitalizacion_= _base_entrenamiento_.loc[:,["ID_PACIENTE",
             "FE_ENTREVISTA"]].drop_duplicates().apply(lambda x: self.marca_fila_hospitalizacion(self,x.ID_PACIENTE,x.FE_ENTREVISTA),axis=1)
        _base_entrenamiento_=pd.merge(_base_entrenamiento_,_Hospitalizacion_,on=["ID_PACIENTE","FE_ENTREVISTA"])

        print(_base_entrenamiento_.shape,"Hospitalizacion")
                                            
        
        _Adherencia_p_1_= _base_entrenamiento_.loc[:,["ID_PACIENTE",
             "FE_ENTREVISTA"]].drop_duplicates().apply(lambda x: self.marca_fila_adherencia_pasada(x.ID_PACIENTE,x.FE_ENTREVISTA,1),axis=1)
        _base_entrenamiento_=pd.merge(_base_entrenamiento_,_Adherencia_p_1_,on=["ID_PACIENTE","FE_ENTREVISTA"])

        print(_base_entrenamiento_.shape,"Adherencia 1 año")

        _Adherencia_p_3_= _base_entrenamiento_.loc[:,["ID_PACIENTE",
             "FE_ENTREVISTA"]].drop_duplicates().apply(lambda x: self.marca_fila_adherencia_pasada(x.ID_PACIENTE,x.FE_ENTREVISTA,3),axis=1)
        _base_entrenamiento_=pd.merge(_base_entrenamiento_,_Adherencia_p_3_,on=["ID_PACIENTE","FE_ENTREVISTA"])

        print(_base_entrenamiento_.shape,"Adherencia 3 años")

        _Adherencia_p_5_= _base_entrenamiento_.loc[:,["ID_PACIENTE",
             "FE_ENTREVISTA"]].drop_duplicates().apply(lambda x: self.marca_fila_adherencia_pasada(x.ID_PACIENTE,x.FE_ENTREVISTA,5),axis=1)
        _base_entrenamiento_=pd.merge(_base_entrenamiento_,_Adherencia_p_5_,on=["ID_PACIENTE","FE_ENTREVISTA"])

        print(_base_entrenamiento_.shape,"Adherencia 5 años")
        

        _base_entrenamiento_=pd.merge_asof(_base_entrenamiento_,self.Antecedentes2,by="ID_PACIENTE",
                                            right_on="FE_ACTUALIZA",left_on="FE_ENTREVISTA")
        
        print(_base_entrenamiento_.shape,"Antecedentes")
        
        _Orales_= _base_entrenamiento_.loc[:,["ID_PACIENTE",
             "FE_ENTREVISTA"]].drop_duplicates().apply(lambda x: Cuenta_6_meses_12(self.Med_Oral,x.ID_PACIENTE,x.FE_ENTREVISTA,"_Oral"),axis=1)
        _base_entrenamiento_=pd.merge(_base_entrenamiento_,_Orales_,on=["ID_PACIENTE","FE_ENTREVISTA"])

        print(_base_entrenamiento_.shape,"Med Orales")

        _Bio_= _base_entrenamiento_.loc[:,["ID_PACIENTE",
             "FE_ENTREVISTA"]].drop_duplicates().apply(lambda x: Cuenta_Bio(self.Med_Bio,x.ID_PACIENTE,x.FE_ENTREVISTA,"_Bio"),axis=1)
        _base_entrenamiento_=pd.merge(_base_entrenamiento_,_Bio_,on=["ID_PACIENTE","FE_ENTREVISTA"])

        print(_base_entrenamiento_.shape,"Med Bio")

        _I_Eme_= _base_entrenamiento_.loc[:,["ID_PACIENTE",
             "FE_ENTREVISTA"]].drop_duplicates().apply(lambda x: Cuenta_6_meses_12(self.Med_I_Eme,x.ID_PACIENTE,x.FE_ENTREVISTA,"_I_Eme"),axis=1)
        _base_entrenamiento_=pd.merge(_base_entrenamiento_,_I_Eme_,on=["ID_PACIENTE","FE_ENTREVISTA"])

        print(_base_entrenamiento_.shape,"Inaladores Emergencia")

        _I_Mant_= _base_entrenamiento_.loc[:,["ID_PACIENTE",
             "FE_ENTREVISTA"]].drop_duplicates().apply(lambda x: Cuenta_6_meses_12(self.Med_I_Mant,x.ID_PACIENTE,x.FE_ENTREVISTA,"_I_Mant"),axis=1)
        _base_entrenamiento_=pd.merge(_base_entrenamiento_,_I_Mant_,on=["ID_PACIENTE","FE_ENTREVISTA"])

        print(_base_entrenamiento_.shape,"Inhaladores Mantenimiento")


        self.base=_base_entrenamiento_
        
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
                        "FE_ENTREVISTA":FECHA_EMISION,
                        #"DiagnosticoUltimaHospitalizacion":_ultima_hosp_[0],
                        "DiasUCIUltimoAnio":_dias_[0],
                        "DiasUCEUltimoAnio":_dias_[1],
                        "NumHospUltimoAnio":_conteo_,
                        "DiasUCIRespUltimoAnio":_dias_resp_[0],
                        "DiasUCERespUltimoAnio":_dias_resp_[1],
                        "NumHospRespUltimoAnio":_conteo_resp_})
        

    def marca_fila_adherencia_pasada(self,ID_PACIENTE,FE_ENTREVISTA,tiempo=1):
        
        _Adherencia_=self.base.iloc[:,0:10].copy()
        _filtro_=(_Adherencia_.ID_PACIENTE==ID_PACIENTE)
        _filtro_=_filtro_&(_Adherencia_.FE_ENTREVISTA<FE_ENTREVISTA)
        _filtro_=_filtro_&(_Adherencia_.FE_ENTREVISTA>FE_ENTREVISTA-tiempo*timedelta(days=365))
        _Adherencia_=_Adherencia_[_filtro_]
        
        
        _num_adherencias_=(_Adherencia_.CUALITATIVO_PONDERADO=="ADHERENTE").sum()
        _num_entrevistas_=_Adherencia_.CUALITATIVO_PONDERADO.count()
        _num_no_aplica_=(_Adherencia_.CUALITATIVO_PONDERADO=="NO APLICA").sum()
        _num_no_adherente_=(_Adherencia_.CUALITATIVO_PONDERADO=="NO ADHERENTE").sum()
              

        
        return pd.Series({"ID_PACIENTE":ID_PACIENTE,
                        "FE_ENTREVISTA":FE_ENTREVISTA,
                        "NumAdherencias_"+str(tiempo)+"_anio":_num_adherencias_,
                        "NumEntrevistas_"+str(tiempo)+"_anio":_num_entrevistas_,
                        "NumNA_"+str(tiempo)+"_anio":_num_no_aplica_,
                        "NumNoAdherencias_"+str(tiempo)+"_anio":_num_no_adherente_,
                        "PropAdherencia_"+str(tiempo)+"_anio":_num_adherencias_/_num_entrevistas_}
                        )
    def marca_fila_consistencia_med(self,ID_PACIENTE,FE_ENTREVISTA,tiempo=1):
        
        _Adherencia_=self.base.iloc[:,0:10].copy()
        _filtro_=(_Adherencia_.ID_PACIENTE==ID_PACIENTE)
        _filtro_=_filtro_&(_Adherencia_.FE_ENTREVISTA<FE_ENTREVISTA)
        _filtro_=_filtro_&(_Adherencia_.FE_ENTREVISTA>FE_ENTREVISTA-tiempo*timedelta(days=365))
        _Adherencia_=_Adherencia_[_filtro_]
        
        
        _num_adherencias_=(_Adherencia_.CUALITATIVO_PONDERADO=="ADHERENTE").sum()
        _num_entrevistas_=_Adherencia_.CUALITATIVO_PONDERADO.count()
        _num_no_aplica_=(_Adherencia_.CUALITATIVO_PONDERADO=="NO APLICA").sum()
        _num_no_adherente_=(_Adherencia_.CUALITATIVO_PONDERADO=="NO ADHERENTE").sum()
              

        
        return pd.Series({"ID_PACIENTE":ID_PACIENTE,
                        "FE_ENTREVISTA":FE_ENTREVISTA,
                        "NumAdherencias_"+str(tiempo)+"_anio":_num_adherencias_,
                        "NumEntrevistas_"+str(tiempo)+"_anio":_num_entrevistas_,
                        "NumNA_"+str(tiempo)+"_anio":_num_no_aplica_,
                        "NumNoAdherencias_"+str(tiempo)+"_anio":_num_no_adherente_,
                        "PropAdherencia_"+str(tiempo)+"_anio":_num_adherencias_/_num_entrevistas_}
                        )
        


#%%

base_prin_adherencia=AdherenciaPipe("AdherenciaNew_20_jun_AG.xlsx")
# %%

base_prin_adherencia.marca_fila_adherencia_pasada(725344,pd.to_datetime("2014-05-08 00:00:00"))

# %%
