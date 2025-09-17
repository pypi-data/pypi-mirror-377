# -*- coding: utf-8 -*-

"""
#Algoritmo Genético
```
Versión   : 1.2, Para uso educativo
Autor     : Luis Beltran Palma Ttito
Lugar     : Cusco, Perú, 2024.
Proposito : Implementación de algoritmos genético en python
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

    
class AlgoritmoGenetico:
    # Constructor
    def __init__(self, Generaciones, Poblacion, ProbMutacion, PobElite, funFitness=None):
        self.N = 0                              # Cantidad de ciudades
        self.Generaciones = Generaciones        # Cantidad de generaciones
        self.P = Poblacion                      # población
        self.ProbMutacion = ProbMutacion        # Probabilidad de mutación
        self.PoElite = PobElite                 # Cantidad de individuos de la élite
        self.Archivo = ''                       # Archivo TSP

        self.HistCosto = []         # Historial de costo
        self.HistFitness = []       # historial de fitness
        self.TSP = []               # TSP
        self.Ruta = []              # Ruta solución
        self.Distancia = []         # Matriz de distancias
        self.Costo = 0.0            # Costo de la ruta solucion
        self.Aptitu = 0.0           # Fitness de ruta solución
        self.Fitness = funFitness or self.Fitness_defecto # Función fitness definido por usuario

        
    # Muestra evolución de costo
    def GraficaCosto(self):
        plt.figure()
        plt.plot(self.HistCosto)
        plt.title('Evolución de costo')
        plt.grid(True)
        plt.show
      
    # Muestra evolución de aptitud
    def GraficaAptitud(self):
        plt.figure()
        plt.plot(self.HistFitness)
        plt.title('Evolución de aptitud')
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
      
    # Lee TSP excel (sin cabecera) y crea matriz de distancias
    def LeerExcel(self, Archivo, Hoja ):
        # Leer TSP
        df = pd.read_excel(Archivo, sheet_name=Hoja, header=None)
        self.TSP = np.array(df.values)
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

    # Calcula Costo entre 2 nodos adyacentes
    def CostoArco(self, inicio, fin):
        return self.Distancia[inicio - 1][fin - 1]

    # Calcula Costo de una ruta
    def DistaTotal(self, R):
        Costo = 0
        for k in range(0, self.N - 1):
            Costo = Costo + self.CostoArco(R[k], R[k+1])
        Costo = Costo + self.CostoArco(R[self.N - 1], 1)
        return Costo

    # Calcula aptitup o fitnnes de la ruta R = 1/sum(distancias)
    def Fitness_defecto(self, R):
        Costo = 0
        for k in range(0, self.N - 1):
            Costo = Costo + self.CostoArco(R[k], R[k+1])
        Costo = Costo + self.CostoArco(R[self.N - 1], 1)
        return 1/Costo

    # Genera población inicial con P individuos
    def GeneraPoblacionInicial(self, P):
        self.Poblacion = []
        self.P = P
        for i in range(1, P + 1):
            S = random.sample(list(range(2,self.N+1)), k=self.N-1)
            S.insert(0, 1)
            self.Poblacion.append([self.Fitnnes(S),S])
        return self.Poblacion

    # Seleccion de padre y madre por metodo de la ruleta
    def Seleccion(self):

        # ordenar población por el valor fitness
        self.Poblacion = sorted(self.Poblacion)

        # Hallar sumatoria de fitness para crear ruleta
        SumaF = 0
        for P in self.Poblacion:
            SumaF = SumaF + P[0]

        # Crea ruleta
        Ruleta = []
        SumaAcu = 0
        for P in self.Poblacion:
            SumaAcu = SumaAcu + P[0]/SumaF
            Ruleta.append([P[0], P[1], SumaAcu])

        # Seleccionar padre
        RandPadre = random.random()
        for k in Ruleta:
            if (k[2] >= RandPadre):
                break
        Padre = k

        # Selecciona madre
        RandMadre = random.random()
        for k in Ruleta:
            if (k[2] >= RandMadre):
                break
        Madre = k

        return Padre, Madre, Ruleta, RandPadre, RandMadre

    def Cruce(self, P, M):
        p = P[1]
        m = M[1]

        # Generar punto de cruce al azar
        r = random.randint(3, self.N - 2)

        # Crear hijo 1
        h1 = []
        for k in range(0, r):
            h1.append(p[k])
        for k in range(1, self.N):
            if (m[k] not in h1):
                h1.append(m[k])

        # Crear hijo 2
        h2 = []
        for k in range(0, r):
            h2.append(m[k])
        for k in range(1, self.N):
            if (p[k] not in h2):
                h2.append(p[k])

        return h1, h2,r

    # mutacion swap para el problema de TSP (permutación)
    def Mutacion(self, H, Prob):
        h = H.copy()
        r1 = 0
        r2 = 0
        if (random.random() <= Prob):
            r1 = random.randint(1, self.N - 1)
            r2 = random.randint(1, self.N - 1)
            Aux = h[r1]
            h[r1] = h[r2]
            h[r2] = Aux
        return h, r1, r2

    # Seleccionar N individuos de la elite
    def Elite(self, N):
        # ordenar población por el valor fitnnes
        self.Poblacion = sorted(self.Poblacion, reverse = True)
        PoblacionElite = []
        for k in range(N):
            PoblacionElite.append(self.Poblacion[k])
        return PoblacionElite

    def EjecutarTSP(self, Archivo):
        self.Archivo = Archivo
        # Leer datos del problema
        self.LeerTSP(self.Archivo)

        # Inicializar poblacion inicial con P individuos
        self.Poblacion = self.GeneraPoblacionInicial(self.P)

        # Repetir el proceso evolución por generaciones
        self.HistCosto = []
        self.HistFitness = []
        
        for k in range(self.Generaciones):
            Pe = self.Elite(self.PoElite)
            Po = []

            # obtener padre y madre por la mitad de la población y generar hijo1 e hijo2
            for i in range(self.P // 2):
                Padre, Madre, Ruleta, R1, R2 = self.Seleccion()
                Hijo1, Hijo2, PuntoCruce = self.Cruce(Padre, Madre)
                Hijo1, r1, r2 = self.Mutacion(Hijo1, self.ProbMutacion)
                Hijo2, r1, r2 = self.Mutacion(Hijo2, self.ProbMutacion)
                Po.append([self.Fitnnes(Hijo1), Hijo1])
                Po.append([self.Fitnnes(Hijo2), Hijo2])

            # Reemplazar a la población actual
            self.Poblacion = Po
            # adicionar los individuos de la elite
            for p in Pe:
                self.Poblacion.append(p)
            
            # Guardar costo histórico
            self.Poblacion = sorted(self.Poblacion, reverse=True)
            MejorGene = self.Poblacion[0]
            self.HistCosto.append(self.DistaTotal(MejorGene[1]))
            self.HistFitness.append(self.Fitnnes(MejorGene[1]))
            

        # Elegir el mejor individuo de la población
        self.Poblacion = sorted(self.Poblacion, reverse=True)
        Mejor = self.Poblacion[0]
        self.Ruta = Mejor[1]
        self.Costo = self.DistaTotal(Mejor[1])
        self.Aptitud = Mejor[0]
        return self.Ruta, self.Costo, self.Aptitud 


    def EjecutarDistancia(self, Archivo, Hoja):
        self.Archivo = Archivo
        # Leer datos del problema
        self.LeerDistanciaExcel(self.Archivo, Hoja)

        # Inicializar poblacion inicial con P individuos
        self.Poblacion = self.GeneraPoblacionInicial(self.P)

        # Repetir el proceso evolución por generaciones
        self.HistCosto = []
        self.HistFitness = []
        
        for k in range(self.Generaciones):
            Pe = self.Elite(self.PoElite)
            Po = []

            # obtener padre y madre por la mitad de la población y generar hijo1 e hijo2
            for i in range(self.P // 2):
                Padre, Madre, Ruleta, R1, R2 = self.Seleccion()
                Hijo1, Hijo2, PuntoCruce = self.Cruce(Padre, Madre)
                Hijo1, r1, r2 = self.Mutacion(Hijo1, self.ProbMutacion)
                Hijo2, r1, r2 = self.Mutacion(Hijo2, self.ProbMutacion)
                Po.append([self.Fitnnes(Hijo1), Hijo1])
                Po.append([self.Fitnnes(Hijo2), Hijo2])

            # Reemplazar a la población actual
            self.Poblacion = Po
            # adicionar los individuos de la elite
            for p in Pe:
                self.Poblacion.append(p)
            
            # Guardar costo histórico
            self.Poblacion = sorted(self.Poblacion, reverse=True)
            MejorGene = self.Poblacion[0]
            self.HistCosto.append(self.DistaTotal(MejorGene[1]))
            self.HistFitness.append(self.Fitnnes(MejorGene[1]))
            

        # Elegir el mejor individuo de la población
        self.Poblacion = sorted(self.Poblacion, reverse=True)
        Mejor = self.Poblacion[0]
        self.Ruta = Mejor[1]
        self.Costo = self.DistaTotal(Mejor[1])
        self.Aptitud = Mejor[0]
        return self.Ruta, self.Costo, self.Aptitud 

