# -*- coding: utf-8 -*-

"""
# Colonia de hormigas
```
Versión   : 1.2, Para uso educativo
Autor     : Luis Beltran Palma Ttito
Lugar     : Cusco, Perú, 2024.
Proposito : Implementación de colonia de hormigas en python
Problema  : TSP.
```

#Librerías
"""

import random
import math
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

"""# Clase Algorítmo Genético"""

    
class ColoniaHormiga:
    # Constructor
    def __init__(self, Iteraciones, CantHormigas, Ro, Q):
        self.Iteraciones = Iteraciones          # Cantidad de iteraciones
        self.CantHormigas = CantHormigas        # Cantidad de hormigas
        self.Ro = Ro                            # Coeficiente de evaporación
        self.Q = Q                              # Coeficiente de disipación
        self.Archivo = ''                       # Archivo TSP
        self.TSP = []                           # TSP
        self.Distancia = []                     # Matriz de distancias
        self.Visibilidad = []                   # matriz de visibilidad de aristas por parte de las hormigas
        self.Feromona = []                      # matriz de feromona
        self.N = 0                              # Tamaño de la matriz, N x N

        self.Mejor = []                         # Aqui almacena la mejor solución en cada iteracion
        self.HistCosto = []                     # Historico de solucion
        self.Ruta = []                          # Ruta solucion
        self.Costo = 0.0                        # Costo de la mejor solución

    # Muestra evolución de costo
    def GraficaCosto(self):
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
        df = pd.read_excel(Archivo, sheet_name=Hoja, header=None)
        df_float = df.astype(float)
        self.Distancia = np.array(df_float.values)
        # Reemplazar valores iguales a cero por 0.000001, para evitar división por cero
        self.Distancia[self.Distancia == 0] = 0.000001
        self.N = len(self.Distancia)
        self.Mejor = list(range(1,self.N+1))
        self.Visibilidad = 1/self.Distancia
        self.Feromona = self.Distancia * 0.0 + 0.1
        return self.N, self.TSP, self.Distancia, self.Visibilidad, self.Feromona
    
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
        self.Mejor = list(range(1,self.N+1))
        # Convertir TSP a matriz de distancias
        self.Distancia = np.empty((self.N,self.N))
        for i in range(self.N):
            for j in range(self.N):
                if i == j:
                    self.Distancia[i, j] = 0.000001 # debiera ser 0, pero 1/0 genera división por cero, pero no sera utilizado 
                else:
                    self.Distancia[i, j] = math.sqrt(math.pow(self.TSP[i, 0] - self.TSP[j, 0], 2)
                    + math.pow(self.TSP[i, 1] - self.TSP[j, 1], 2))
        # Cálculo de visibilidad y feromona
        self.Visibilidad = 1/self.Distancia
        self.Feromona = self.Distancia * 0.0 + 0.1
        return self.N, self.TSP, self.Distancia, self.Visibilidad, self.Feromona

    # Calcula costo entre 2 nodos adyacentes
    def CostoArco(self, inicio, fin):
        return self.Distancia[inicio-1][fin-1]

    # Calcula el costo del camino C
    def CostoRuta(self,C):
        Cost = 0
        for k in range(self.N-1):
            Cost = Cost + self.CostoArco(C[k],C[k+1])
        Cost = Cost + self.CostoArco(C[self.N-1], 1)
        return Cost

    # Una hormina busca un camino a la comida aleatoriamente usando ruleta
    # Genera ruleta para cada adyacente desde un Nodo en  base a visibilidad, feromona
    # Solo crear caminos desde el Nodo actual a los faltantes (ADAPTACIÓN VIAJERO COMERCIO)
    def Hormiga(self):
        R = []  # R almacena la ruta que determinara la hormiga
        S = list(range(2,self.N+1))  # siempre inicia en el nodo 1,--> elegira los otros nodos al azar, usando ruleta por feromona
        Nodo = 1
        R.append(Nodo)

        # los elementos de S van eliminandose al azar, hasta que quede vacio
        while (len(S) > 0):
            L = [] # L contiene la matriz de la ruleta

            # Calcula el sumatoria de visibilidad * feromona
            Total = 0.0
            for k in S:
                Total = Total + self.Visibilidad[Nodo-1][k-1] * self.Feromona[Nodo-1][k-1]

            # calcula la función de probabilidad y función de distribución (genera ruleta)
            FD = 0.0
            for k in S:
                FD = FD + self.Visibilidad[Nodo-1][k-1] * self.Feromona[Nodo-1][k-1]/Total
                Fila = [Nodo, k, self.Visibilidad[Nodo-1][k-1] * self.Feromona[Nodo-1][k-1],
                        self.Visibilidad[Nodo-1][k-1] * self.Feromona[Nodo-1][k-1]/Total, FD]
                L.append(Fila)

            # Genera un valor aleatorio r y determina el siguiente nodo a elegir
            k = 0
            r = random.random()
            while (L[k][4] < r):
                k = k + 1
            Nodo = L[k][1]
            S.remove(Nodo)  # elimina nodo a elegir de las lista de nodos pendientes
            R.append(Nodo)  # almacena el nodo siguiente en la ruta

        # calcula costo de la ruta R
        C = self.CostoRuta(R)
        return R, C

    # N hormigas buscan ruta hacia la comida
    # y se va registrando la mejor solución
    def BuscanComida(self, N):
        Soluciones = []
        for k in range(N):
            Sol, _ = self.Hormiga()
            if self.CostoRuta(Sol) < self.CostoRuta(self.Mejor):
                self.Mejor = Sol
            Soluciones.append(Sol)
        return Soluciones, self.Mejor

    # Verifica si hay camino de p a q en el camino C
    # util para recalcular feromonas
    def HayCamino(self, C, p, q):
        for i in range(self.N - 1):
            if ((C[i] == p) and (C[i + 1] == q)):
                return True
        return False

    # Recalcula valor de feromona despues que N hormigas generaron caminos
    # nuevo valor feromona = f(valor evaporacion de feromona, suma deltas de cada hormiga)
    def RecalculaFeromona(self, Soluciones,Ro,Q):

        # disipación feromona
        for i in range(0, self.N):
            for j in range(0, self.N):
                self.Feromona[i][j] = (1 - Ro) * self.Feromona[i][j]

        # incremento feromona
        for i in range(0, self.N - 1):
            for j in range(i + 1, self.N):
                SumDelta = 0
                # print('(', i + 1, ',', j + 1, ')', end=' ')
                for R in Soluciones:
                    Cost = self.CostoRuta(R)
                    if (self.HayCamino(R, i + 1, j + 1)):
                        SumDelta = SumDelta + Q/Cost
                self.Feromona[i][j] = self.Feromona[i][j] + SumDelta
        return self.Feromona

    # Ejecuta el algoritmo de colonia de hormigas
    # Iteraciones : cantidad de iteraciones a realizar, es decir cantidad de veces que las hormigas salen en busca de alimentos
    # CantHormigas: cantidad de hormigas que salen a buscar alimentos en cada iteración
    # Ro: porcentaje de evaporación de feromoma
    # Q: Coef. de aprendizaje
    def EjecutarTSP(self, Archivo):
        self.Archivo = Archivo
        self.LeerTSP(self.Archivo)
        self.HistCosto = []
        for k in range(self.Iteraciones):
            Soluciones, self.Mejor = self.BuscanComida(self.CantHormigas)
            self.RecalculaFeromona(Soluciones,self.Ro,self.Q)
            self.HistCosto.append(self.CostoRuta(self.Mejor))
        self.Ruta = self.Mejor
        self.Costo = self.CostoRuta(self.Mejor)
        return self.Ruta, self.Costo

    def EjecutarDistancia(self, Archivo, Hoja):
        self.Archivo = Archivo
        self.LeerDistanciaExcel(self.Archivo, Hoja)
        self.HistCosto = []
        for k in range(self.Iteraciones):
            Soluciones, self.Mejor = self.BuscanComida(self.CantHormigas)
            self.RecalculaFeromona(Soluciones,self.Ro,self.Q)
            self.HistCosto.append(self.CostoRuta(self.Mejor))
        self.Ruta = self.Mejor
        self.Costo = self.CostoRuta(self.Mejor)
        return self.Ruta, self.Costo
