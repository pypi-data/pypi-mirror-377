# -*- coding: utf-8 -*-

"""
# Recocido simulado
```
Versión   : 1.2, Para uso educativo
Autor     : Luis Beltran Palma Ttito
Lugar     : Cusco, Perú, 2024.
Proposito : Implementación de recocido simulado en python
Problema  : TSP.
```

#Librerías
"""

import random
import math
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

"""# Clase Recocido Simulado """


class RecocidoSimulado:
    def __init__(self, TempInicial, TempFinal, ConstanteDecremento, TiempoEnfriamiento, Bolztman):
        self.Ti = TempInicial           # Temperatura inicial
        self.Tf = TempFinal             # Temperatura final
        self.c = ConstanteDecremento    # Constante de decremento
        self.n = TiempoEnfriamiento     # Duración de tiempo de enfriamiento
        self.k = Bolztman               # Constante de Bolztman
        self.TSP = []                   # TSP
        self.Distancia = []             # matriz de distancias
        self.N = 0                      # Cantidad de ciudades
        self.Archivo = ''               # Archivo TSP

        self.Ruta = []          # Ruta solucion
        self.Costo = 0.0        # costo de la ruta solucion
        self.HistCosto = []     # Historico de costo

    # Muestra evolución de costo
    def GraficaEnergia(self):
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
    # [1, 6, 8, 2, 10, 3, ..]
    def Energia(self, S):
        Cost = 0
        for k in range(self.N - 1):
            Cost = Cost + self.CostoArco(S[k],S[k+1])
        Cost = Cost + self.CostoArco(S[self.N - 1], 1)
        return Cost

    # Determina un solución aleatoria inicial
    def Muestrar(self):
        So = random.sample(list(range(2,self.N+1)), self.N-1)
        So.insert(0, 1)
        return So

    # Determina un vecino al azar
    def Mover(self, S):
        SS = S.copy()
        Pos1 = int(random.uniform(1, self.N))
        Pos2 = int(random.uniform(1, self.N))
        Aux = SS[Pos1]
        SS[Pos1] = SS[Pos2]
        SS[Pos2] = Aux
        return SS

    # Algoritmo de recocido simulado
    def EjecutarTSP(self, Archivo):
        self.Archivo = Archivo
        self.LeerTSP(self.Archivo)
        # variables que almacenan rutas y energías
        Rutas = []
        Energias = []
        # Inicializa T con temperatura inicial
        T = self.Ti
        # Generar la primera solución
        x = self.Muestrar()
        # calcula energía de la muestra inicial
        e = self.Energia(x)
        # alamacena en la lista
        Energias.append(e)
        Rutas.append(x)

        # Mientras la temperatura actual > a temperatura final
        while (T > self.Tf):
            # por n tiempos determina un mejor solución
            # n tiempos de emfriamiento
            for i in range(1, self.n + 1):
                # Genera vecino
                xp = self.Mover(x)
                ep = self.Energia(xp)
                # si energia de vecino < energia de dato actual, entonces reemplazar
                if (ep < e):
                    x = xp
                    e = ep
                    Energias.append(e)
                    Rutas.append(x)
                # Utilizar clave de funcionamiento de enfriamiento simulado
                # para escapar de minimos locales
                # self.k: constante de Boltzmann
                else:
                    r = random.random()
                    if (r < math.exp(-(ep-e)/(self.k * T))):
                        x = xp
                        e = ep
                        Energias.append(e)
                        Rutas.append(x)

            # Disminuir temperatura
            T = self.c * T
            self.Costo = self.Energia(x)
            self.Ruta = x
            self.HistCosto = Energias
        return self.Ruta, self.Costo
    
    # Algoritmo de recocido simulado
    def EjecutarDistancia(self, Archivo, Hoja):
        self.Archivo = Archivo
        self.LeerDistanciaExcel(self.Archivo, Hoja)
        # variables que almacenan rutas y energías
        Rutas = []
        Energias = []
        # Inicializa T con temperatura inicial
        T = self.Ti
        # Generar la primera solución
        x = self.Muestrar()
        # calcula energía de la muestra inicial
        e = self.Energia(x)
        # alamacena en la lista
        Energias.append(e)
        Rutas.append(x)

        # Mientras la temperatura actual > a temperatura final
        while (T > self.Tf):
            # por n tiempos determina un mejor solución
            # n tiempos de emfriamiento
            for i in range(1, self.n + 1):
                # Genera vecino
                xp = self.Mover(x)
                ep = self.Energia(xp)
                # si energia de vecino < energia de dato actual, entonces reemplazar
                if (ep < e):
                    x = xp
                    e = ep
                    Energias.append(e)
                    Rutas.append(x)
                # Utilizar clave de funcionamiento de enfriamiento simulado
                # para escapar de minimos locales
                # self.k: constante de Boltzmann
                else:
                    r = random.random()
                    if (r < math.exp(-(ep-e)/(self.k * T))):
                        x = xp
                        e = ep
                        Energias.append(e)
                        Rutas.append(x)

            # Disminuir temperatura
            T = self.c * T
            self.Costo = self.Energia(x)
            self.Ruta = x
            self.HistCosto = Energias
        return self.Ruta, self.Costo
    