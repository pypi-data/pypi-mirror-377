# -*- coding: utf-8 -*-

"""
# Selección clonal
```
Versión   : 1.2, Para uso educativo
Autor     : Luis Beltran Palma Ttito
Lugar     : Cusco, Perú, 2024.
Proposito : Implementación de selección clonal en python
Problema  : TSP.
```

#Librerías
"""

import random
import math
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

"""# Clase Selección Clonal """

class SeleccionClonal:
    def __init__(self, Iteraciones, Poblacion, CantClones, AltaAfinidad, ProbMutacion, IncProbMutacion):
        self.Iteraciones = Iteraciones          # Iteraciones
        self.P = Poblacion                      # Población de anticuerpos
        self.CantClones = CantClones            # Cantidad de clones
        self.Q = AltaAfinidad                   # Cantidad de anticuerpos de alta afinidad
        self.ProbMutar = ProbMutacion           # Probabiliad de mutar para individuos más afines
        self.IncMutacion = IncProbMutacion      # Incremento del 150% de mutacion a perores individuos
        self.N = 0                              # Cantidad de ciudades
        self.Distancia = []                     # Matriz de distancias 
        self.Archivo = ''                       # Archivo TSP
        self.TSP = []                           # TSP

        self.MejorObjetivo = 0          # Mejor objetivo hallado
        self.Ruta = []                  # Ruta solucion
        self.Costo = 0.0                # Costo de ruta solucion 
        self.HistCosto = []             # Historico de costos

    # Muestra evolución de costo
    def GraficaAfinidad(self):
        plt.figure()
        plt.plot(self.HistCosto)
        plt.title('Evolución de costo')
        plt.grid(True)
        plt.show

    # Grafica la ruta solución 2D
    def GraficaRuta(self):
        plt.figure()
        X = []
        Y = []
        for i in range(len(self.Ruta)):
            X.append(self.TSP[self.Ruta[i]-1, 0])
            Y.append(self.TSP[self.Ruta[i]-1, 1])
        plt.plot(X,Y,'-o')
        for i in range(len(self.Ruta)):
            plt.annotate(str(self.Ruta[i]), (X[i],Y[i]))
        plt.title("Ruta solución")
        plt.show()

    # Lee Matriz desde excel (sin cabecera) y crea matriz de distancias
    def LeerDistanciaExcel(self, Archivo, Hoja ):
        # Leer TSP
        df = pd.read_excel(Archivo, sheet_name=Hoja, header=None)
        df_float = df.astype(float)
        self.Distancia = np.array(df_float.values)
        self.N = len(self.Distancia)
        return self.N, self.TSP, self.Distancia
    
    # Lee archivo TSP descargado de TSPLIB
    def Leer_TSP(self, Archivo):
        with open(Archivo) as archivo:
            ciudades = []
            while True:
                linea = archivo.readline()
                if linea.startswith("NODE_COORD_SECTION"):
                    break
            for linea in archivo:
                partes = linea.strip().split()
                if partes[0] == "EOF":
                    break
                _, x, y = partes
                ciudades.append([float(x), float(y)])
        return np.array(ciudades)

    # Lee Archivo TSP y crea matriz de distancias
    def LeerTSP(self, Archivo):
        # Leer TSP
        self.TSP = self.Leer_TSP(Archivo)
        self.N = len(self.TSP)
        # Convertir TSP a matriz de distancias
        self.Distancia = np.empty((self.N,self.N))
        for i in range(self.N):
            for j in range(self.N):
                if i == j:
                    self.Distancia[i, j] = 0
                else:
                    self.Distancia[i, j] = math.sqrt(math.pow(self.TSP[i, 0] - self.TSP[j, 0], 2)
                    + math.pow(self.TSP[i, 1] - self.TSP[j, 1], 2))
        return self.N, self.TSP, self.Distancia

    # Determina la distancia entre 2 ciudad, usa la matriz D
    def CostoArco(self, inicio, fin):
        return self.Distancia[inicio - 1][fin - 1]

    # Determina la energía de S (heurístico), costo de la ruta S
    def Objetivo(self, S):
        Costo = 0
        for k in range(self.N - 1):
            Costo = Costo + self.CostoArco(S[k],S[k+1])
        Costo = Costo + self.CostoArco(S[self.N - 1], 1)
        return Costo

    # Genera población inicial con P individuos
    def GeneraPoblacionInicial(self, P):
        self.Poblacion = []
        self.P = P
        for k in range(1, P + 1):
            S = random.sample(list(range(2,self.N+1)), self.N-1)
            S.insert(0, 1)
            self.Poblacion.append([self.Objetivo(S),S])
        self.Poblacion = sorted(self.Poblacion)
        Mejor = self.Poblacion[0]
        self.MejorObjetivo = Mejor[0]
        return self.Poblacion

    # Obtener los Q individuos de mas alta afinidad
    def AltaAfinidad(self, Q):
        self.PoblacionAltaAfinidad = []
        self.Poblacion = sorted(self.Poblacion)
        for k in range(Q):
            C = (self.Poblacion[k]).copy()
            self.PoblacionAltaAfinidad.append(C)
        return self.PoblacionAltaAfinidad

    # Mutar con probabiliad Prob el individuo I
    def Mutar(self, I, Prob):
        IM = I.copy()
        if (random.random() <= Prob):
            r1 = random.randint(1, self.N - 1)
            r2 = random.randint(1, self.N - 1)
            Aux = IM[r1]
            IM[r1] = IM[r2]
            IM[r2] = Aux
        return IM

    # Clonar y mutar M muestras de cada individuo de alta afinidad
    # fp: probabilidad de mutación
    # fi: incremento de prob de mutacion
    def ClonarMutar(self, M, fp, fi):
        self.ProbMutar = fp
        self.IncMutacion = fi
        self.C = []
        self.PoblacionAltaAfinidad = sorted(self.PoblacionAltaAfinidad)
        Prob = self.ProbMutar
        for IAA in self.PoblacionAltaAfinidad:
            for k in range(M):
                IA = self.Mutar(IAA[1], Prob)
                self.C.append([self.Objetivo(IA), IA])
                Prob = Prob * self.IncMutacion  # incrementa probabiliad de mutación
        return self.C

    # Elegir soluciones que optimizan soluciones anteriores
    def ElegirOptimizadores(self):
        self.Optimos = []
        self.C = sorted(self.C)
        for I in self.C:
            if (I[0] <= self.MejorObjetivo):
                self.Optimos.append(I)
            else:
                break
        return self.Optimos

    def ReemplazarOptimos(self):
        # Reemplazar los peores por  mejores
        self.Poblacion = sorted(self.Poblacion, reverse = True)

        k = 0
        for IO in self.Optimos:
            if k >= len(self.Poblacion):
                break
            self.Poblacion[k] = IO
            k = k + 1

        # Retornar la nueva población
        return self.Poblacion

    def EjecutarTSP(self, Archivo):
        self.Archivo = Archivo
        self.LeerTSP(self.Archivo)
        self.GeneraPoblacionInicial(self.P)
        self.HistCosto = []
        for k in range(self.Iteraciones):
            self.AltaAfinidad(self.Q)
            self.ClonarMutar(self.CantClones, self.ProbMutar, self.IncMutacion)
            self.ElegirOptimizadores()
            self.ReemplazarOptimos()
            # Calculo de historico de afinidad 
            self.Poblacion = sorted(self.Poblacion)
            Mejor = self.Poblacion[0]
            self.HistCosto.append(Mejor[0])

        self.Poblacion = sorted(self.Poblacion)
        Solucion = self.Poblacion[0]
        self.Ruta = Solucion[1]
        self.Costo =  Solucion[0]
        return self.Ruta, self.Costo


    def EjecutarDistancia(self, Archivo, Hoja):
        self.Archivo = Archivo
        self.LeerDistanciaExcel(self.Archivo, Hoja)
        self.GeneraPoblacionInicial(self.P)
        self.HistCosto = []
        for k in range(self.Iteraciones):
            self.AltaAfinidad(self.Q)
            self.ClonarMutar(self.CantClones, self.ProbMutar, self.IncMutacion)
            self.ElegirOptimizadores()
            self.ReemplazarOptimos()
            # Calculo de historico de afinidad 
            self.Poblacion = sorted(self.Poblacion)
            Mejor = self.Poblacion[0]
            self.HistCosto.append(Mejor[0])

        self.Poblacion = sorted(self.Poblacion)
        Solucion = self.Poblacion[0]
        self.Ruta = Solucion[1]
        self.Costo =  Solucion[0]
        return self.Ruta, self.Costo



