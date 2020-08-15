
# %%
import pandas as pd 
from sklearn.model_selection import train_test_split 
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
import os

os.chdir("/mnt/Storage/ds4a/Proyecto Omnivida/git-Omnivida")




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


class MedicamentosPipe:
    
    def __init__(self, base_nombre,bio=False):
        self.bio=bio
        self.base=pd.read_excel("Bases limpias/"+base_nombre)
        if self.bio==False:
            self.base=self.base[self.base.DadoPrinPara=="Asma"]

        if self.bio:
            self.base.rename(columns={"FECHA_DCTO":"FECHA_EMISION","CANTIDAD":"NUMERO_CANTIDAD_PRESTACIONES","NOM_GENERICO":"Categoria"},
                inplace=True)
            self.base["Tratamiento"]="Bio"
        self.base_nombre=base_nombre
        self.cargar_limpias=0
    
    

    def crea_medicamento(self,NOMBRE_MEDICAMENTO,columna,Frecuencia_Mensual=30,tolerancia_dias=5,doble_marca=False):
        setattr(self,NOMBRE_MEDICAMENTO,Medicamento(NOMBRE_MEDICAMENTO,columna,Frecuencia_Mensual,tolerancia_dias,doble_marca))
        return   

#%%
class Medicamento:
    def __init__(self,NOMBRE_MEDICAMENTO,columna,Frecuencia_Mensual=30,tolerancia_dias=5,doble_marca=False):
        self.NOMBRE_MEDICAMENTO=NOMBRE_MEDICAMENTO
        self.Frecuencia_Mensual=Frecuencia_Mensual
        self.columna=columna
        self.tolerancia_dias=tolerancia_dias
        self.doble_marca=doble_marca
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
                            "ConsistenciaReclamacion":_adherencia_,
                        "TiempoEntreFormulas":_tiempo_entre_form_,
                        "TiempoEsperadoEntreFormulas":_tiempo_esperado_,
                            "NUMERO_CANTIDAD_PRESTACIONES":NUMERO_CANTIDAD_PRESTACIONES})
        return _return_
        

    def procesa_medicamentos_df(self,base_med):
        _work_base_=base_med[base_med[self.columna]==self.NOMBRE_MEDICAMENTO]
        _work_base_=_work_base_.loc[:,[ 'ID_PACIENTE', 'FECHA_EMISION','Categoria',
                'NUMERO_CANTIDAD_PRESTACIONES','Tratamiento']].groupby([ 'ID_PACIENTE',
                     'FECHA_EMISION','Categoria','Tratamiento']).agg("sum").reset_index()
        if self.doble_marca:
            def me(x):
                if x>29:
                    x=x/30
                return x
            _work_base_['NUMERO_CANTIDAD_PRESTACIONES']=_work_base_['NUMERO_CANTIDAD_PRESTACIONES'].apply(me)
        
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
        self.marcacion=_adherencia_
        _adherencia_.to_csv("Funciones Objetivo/Consistencia_"+self.NOMBRE_MEDICAMENTO+".csv")
        return _adherencia_
          


#%%


base_prin_medicamentos=MedicamentosPipe("medicamentos_limpio_29_jun_AM.xlsx")

#%%
base_prin_medicamentos.crea_medicamento("Oral","Tratamiento",30)
base_prin_medicamentos.Oral.procesa_medicamentos_df(base_prin_medicamentos.base)

# %%

biologicos.crea_medicamento("Bio","Tratamiento",1)
biologicos.Bio.procesa_medicamentos_df(biologicos.base)


# %%

base_prin_medicamentos.crea_medicamento("Inhaladores Emergencia","Tratamiento",1)
getattr(base_prin_medicamentos,"Inhaladores Emergencia").procesa_medicamentos_df(base_prin_medicamentos.base)



# %%
base_prin_medicamentos.crea_medicamento("Inhaladores Mantenimiento","Tratamiento",1,doble_marca=True)
ab=getattr(base_prin_medicamentos,"Inhaladores Mantenimiento").procesa_medicamentos_df(base_prin_medicamentos.base)

# %%

