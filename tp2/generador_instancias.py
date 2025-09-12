import math
import random

def escribir_instancia_con_deposito_fantasma(n, costo_repartidor, d_max, refrigerados, exclusivos, coords, factor_costo_camion=1.0, nombre_archivo="instancia.txt", costos_especiales=None):
    n_total = n + 1  # sumamos nodo 0
    coords[0] = (-1, -1)  # ubicación arbitraria, no importa porque distancia fija enorme
   
    pares = []
    for i in range(n_total):
        for j in range(i+1, n_total):
            if i == 0 or j == 0:
                distancia = 1_000_000
                costo = 0
            else:
                xi, yi = coords[i]
                xj, yj = coords[j]
                distancia = int(round(math.hypot(xi - xj, yi - yj)))
                if costos_especiales:
                    costo = costos_especiales(i, j, distancia)
                else:
                    costo = int(round(distancia * factor_costo_camion))
            pares.append((i, j, distancia, costo))
   
    with open(nombre_archivo, "w") as f:
        f.write(f"{n_total}\n{costo_repartidor}\n{d_max}\n")
        f.write(f"{len(refrigerados)}\n")
        for r in refrigerados:
            f.write(f"{r}\n")
        f.write(f"{len(exclusivos)}\n")
        for e in exclusivos:
            f.write(f"{e}\n")
        for i, j, dij, cij in pares:
            f.write(f"{i} {j} {dij} {cij}\n")
    print(f"✅ Instancia con depósito fantasma guardada en: {nombre_archivo}")


# Instancia 1: Única parada, todo a pie (aumentada a 45 nodos en línea)
def instancia_unica_parada():
    n = 100
    costo_repartidor = 5
    d_max = 4
    refrigerados = []
    exclusivos = [1]
    coords = {i: (0, i-1) for i in range(1, n+1)}  # nodos en línea vertical
    def costo_especial(i, j, dist):
        if 0 in (i, j):
            return 0
        if 1 in (i, j):
            return dist
        else:
            return 1000
    escribir_instancia_con_deposito_fantasma(n, costo_repartidor, d_max, refrigerados, exclusivos, coords, nombre_archivo="instancia_unica_parada_fantasma.txt", costos_especiales=costo_especial)


# Instancia 2: Un único cliente aislado en camión, resto a pie (50 nodos con cluster y uno aislado)
def instancia_unico_camion_por_conveniencia():
    n = 100
    costo_repartidor = 5
    d_max = 2
    refrigerados = []
    exclusivos = []
    coords = {}
    # Cluster grande de 49 nodos juntos
    for i in range(1, n):
        coords[i] = (i // 7, i % 7)
    # Nodo aislado lejos
    coords[n] = (100, 100)
    def costo_especial(i, j, dist):
        if 0 in (i, j):
            return 0
        if n in (i, j):
            return dist
        else:
            return dist * 10
    escribir_instancia_con_deposito_fantasma(n, costo_repartidor, d_max, refrigerados, exclusivos, coords, nombre_archivo="instancia_unico_cliente_en_camion_por_conveniencia_fantasma.txt", costos_especiales=costo_especial)


# Instancia 3: 4 clientes a pie y resto en camión (50 nodos, 4 exclusivos)
def instancia_4_a_pie_y_resto_camion():
    n = 100
    costo_repartidor = 5
    d_max = 2
    refrigerados = []
    exclusivos = [1, 6, 7, 8]
    coords = {}
    for i in range(1, n+1):
        coords[i] = (i // 10, i % 10)
    def costo_especial(i, j, dist):
        if 0 in (i, j):
            return 0
        else:
            return dist
    escribir_instancia_con_deposito_fantasma(n, costo_repartidor, d_max, refrigerados, exclusivos, coords, nombre_archivo="instancia_4_a_pie_resto_camion_fantasma.txt", costos_especiales=costo_especial)


# Instancia 4: Refrigerados dispersos (7x7 = 49 nodos)
def instancia_refrigerados_dispersos():
    lado_grilla = 7
    n = lado_grilla * lado_grilla
    costo_repartidor = 5
    d_max = 2
    refrigerados = [1, 5, 10, 16, 20, 30, 40, 49]
    exclusivos = []
    coords = {}
    for i in range(n):
        cliente_id = i + 1
        x = i % lado_grilla
        y = i // lado_grilla
        coords[cliente_id] = (x, y)
    def costo_especial(i, j, dist):
        if 0 in (i, j):
            return 0
        else:
            return int(round(dist * 5))
    escribir_instancia_con_deposito_fantasma(n, costo_repartidor, d_max, refrigerados, exclusivos, coords, nombre_archivo="instancia_refrigerados_dispersos_fantasma.txt", costos_especiales=costo_especial)


# Instancia 5: Clústeres separados (3 clusters, ~45 nodos)
def instancia_clusters_separados():
    coords = {}
    cluster1 = [(x, y) for x in range(0, 5) for y in range(0, 3)]  
    cluster2 = [(x+15, y) for x in range(0, 5) for y in range(0, 3)]  
    cluster3 = [(x+30, y) for x in range(0, 5) for y in range(0, 3)]  
    all_coords = cluster1 + cluster2 + cluster3
    for idx, (x, y) in enumerate(all_coords):
        coords[idx+1] = (x, y)
    n = len(coords)
    costo_repartidor = 5
    d_max = 2
    refrigerados = []
    exclusivos = []
    def costo_especial(i, j, dist):
        if 0 in (i, j):
            return 0
        else:
            return dist
    escribir_instancia_con_deposito_fantasma(n, costo_repartidor, d_max, refrigerados, exclusivos, coords, nombre_archivo="instancia_clusters_fantasma.txt", costos_especiales=costo_especial)

def instancia_random_50_nodos(
    seed: int | None = None,
    nombre_archivo: str = "instancia_random_50_nodos.txt"
):
    if seed is not None:
        random.seed(seed)

    n = 50                                       
    costo_repartidor = random.randint(3, 15)    
    d_max = random.randint(2, 8)                  

    coords = {
        i: (random.randint(0, 100), random.randint(0, 100))
        for i in range(1, n + 1)
    }

    cant_refrig = random.randint(0, 10)
    refrigerados = random.sample(range(1, n + 1), k=cant_refrig)

    candidatos_excl = [c for c in range(1, n + 1) if c not in refrigerados]
    cant_excl = random.randint(0, min(10, len(candidatos_excl)))
    exclusivos = random.sample(candidatos_excl, k=cant_excl)

    def costo_especial(i, j, dist):
        return int(round(dist))                  

    escribir_instancia_con_deposito_fantasma(
        n=n,
        costo_repartidor=costo_repartidor,
        d_max=d_max,
        refrigerados=refrigerados,
        exclusivos=exclusivos,
        coords=coords,
        factor_costo_camion=1.0,                 
        nombre_archivo=nombre_archivo,
        costos_especiales=costo_especial
    )


if __name__ == "__main__":
    instancia_unica_parada()
    instancia_unico_camion_por_conveniencia()
    instancia_4_a_pie_y_resto_camion()
    instancia_refrigerados_dispersos()
    instancia_clusters_separados()
    instancia_random_50_nodos(seed=42) 
