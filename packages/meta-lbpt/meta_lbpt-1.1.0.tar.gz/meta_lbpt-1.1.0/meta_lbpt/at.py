# -*- coding: utf-8 -*-

"""
# Algoritmo tabú
```
Versión   : 1.2, Para uso educativo
Autor     : Luis Beltran Palma Ttito
Lugar     : Cusco, Perú, 2024.
Proposito : Implementación de algoritmo tabú en python
Problema  : TSP.
```

#Librerías
"""

import random
import math
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

"""# Clase Algoritmo Tabu """

class AlgoritmoTabu:
    def __init__(self, Ciclos):
        self.N = 0                  # Cantidad de ciudades
        self.Ciclos = Ciclos        # Ciclos del algoruitmo tabu
        self.Memoria = []           # Memoria de largo y corto plazo
        self.TSP = []               # TSP
        self.Distancia = []         # matriz de distancias
        self.Archivo = ''           # Archivo TSP

        self.Ruta = []              # Ruta solucion
        self.Costo = 0.0            # Costo de ruta solucion
        self.HistCosto = []         # Historico de costos

    def GraficaEnergia(self):
        plt.figure()
        plt.plot(self.HistCosto)
        plt.title('Evolución de costo')
        plt.grid(True)
        plt.show

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
        self.Memoria = np.zeros((self.N, self.N), dtype=int)
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
        
        self.Memoria = np.zeros((self.N, self.N), dtype=int)
        return self.N, self.TSP, self.Distancia


    # Determina la distancia entre 2 ciudad, usa la matriz Distancias
    def CostoArco(self, inicio, fin):
        return self.Distancia[inicio - 1][fin - 1]

    # Genera un estado inicial
    def Muestrar(self):
        So = random.sample(list(range(2,self.N+1)), k=self.N-1)
        So.insert(0, 1)
        return So

    # Determina la energía de S (heurístico), costo de la ruta S
    def Energia(self, S):
        Costo = 0
        for k in range(self.N - 1):
            Costo = Costo + self.CostoArco(S[k], S[k+1])
        Costo = Costo + self.CostoArco(S[self.N - 1], 1)
        return Costo

    # Determina los vecinos de una estado
    # S: estado del que se desea conocer los vecinos
    # Lista, cada elemento contiene:
    # 1. puntos que favorece al vecino en comparación al estado S
    # 2. estado 1 permutado
    # 3. estado 2 permutado
    # 4. Estado vecino
    def Candidatos(self, S):
        Lista = []
        for k in range(1, self.N):
            for j in range(k + 1, self.N):
                L = []
                SS = S.copy()
                Aux = SS[k]
                SS[k] = SS[j]
                SS[j] = Aux
                L.append(self.Energia(S) - self.Energia(SS))
                L.append(k+1)
                L.append(j+1)
                L.append(SS)
                Lista.append(L)
        Lista = sorted(Lista, reverse=True)
        return Lista

    def Tabu(self, S):
        Candi = self.Candidatos(S)
        k = 0

        # Verificar que estado no es tabú
        d = Candi[k]
        while (self.Memoria[d[1]-1][d[2]-1] > 0 or  k < self.N):
            k = k + 1
            d = Candi[k]

        # Elige el ultimo analizado o el primero
        if (k < self.N):
            d = Candi[k]
        else:
            d = Candi[0]

        # Actualizar situación de tabu (-1)
        for i in range(0, self.N - 1):
            for j in range(i + 1, self.N - 1):
                if (self.Memoria[i][j] > 0):
                    self.Memoria[i][j] = self.Memoria[i][j] - 1

        # Actualiza memoria a largo plazo
        if (self.Memoria[d[1]-1][d[2]-1] == 0):
            self.Memoria[d[1]-1][d[2]-1] = 3   # memoria a corto plazo
            self.Memoria[d[2]-1][d[1]-1] = self.Memoria[d[2]-1][d[1]-1]  + 1  # memoria a largo plazo
            S = (d[3]).copy()

        return S, Candi, self.Memoria

    def EjecutarTSP(self, Archivo):
        self.Archivo = Archivo
        self.LeerTSP(self.Archivo)
        S = self.Muestrar()
        self.HistCosto = []
        for k in range(self.Ciclos):
            S, Candi, self.Memoria = self.Tabu(S)
            self.HistCosto.append(self.Energia(S))
        self.Ruta = S
        self.Costo = self.Energia(S)
        return self.Ruta, self.Costo

    def EjecutarDistancia(self, Archivo, Hoja):
        self.Archivo = Archivo
        self.LeerDistanciaExcel(self.Archivo, Hoja)
        S = self.Muestrar()
        self.HistCosto = []
        for k in range(self.Ciclos):
            S, Candi, self.Memoria = self.Tabu(S)
            self.HistCosto.append(self.Energia(S))
        self.Ruta = S
        self.Costo = self.Energia(S)
        return self.Ruta, self.Costo