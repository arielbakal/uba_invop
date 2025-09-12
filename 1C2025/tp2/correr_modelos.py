import asyncio
import sys
import cplex, pathlib, sys
from cplex.exceptions import CplexSolverError
from tsp_mtz import armar_lp_tsp_mtz, resolver_lp_tsp_mtz
from tsp_sol import armar_lp_tsp_sol, resolver_lp_tsp_sol
from tsp_sol_d1 import armar_lp_tsp_sol_d1, resolver_lp_tsp_sol_d1
from tsp_sol_d2 import armar_lp_tsp_sol_d2, resolver_lp_tsp_sol_d2

TOLERANCE =10e-6 

class InstanciaRecorridoMixto:
    def __init__(self):
        self.cant_clientes = 0
        self.costo_repartidor = 0
        self.d_max = 0
        self.refrigerados = []
        self.exclusivos = []
        self.distancias = []        
        self.costos = []        

    def leer_datos(self,filename):
        # abrimos el archivo de datos
        f = open(filename)

        # leemos la cantidad de clientes
        self.cant_clientes = int(f.readline())
        # leemos el costo por pedido del repartidor
        self.costo_repartidor = int(f.readline())
        # leemos la distamcia maxima del repartidor
        self.d_max = int(f.readline())
        
        # inicializamos distancias y costos con un valor muy grande (por si falta algun par en los datos)
        self.distancias = [[1000000 for _ in range(self.cant_clientes)] for _ in range(self.cant_clientes)]
        self.costos = [[1000000 for _ in range(self.cant_clientes)] for _ in range(self.cant_clientes)]
        
        # leemos la cantidad de refrigerados
        cantidad_refrigerados = int(f.readline())
        # leemos los clientes refrigerados
        for i in range(cantidad_refrigerados):
            self.refrigerados.append(int(f.readline()))
        
        # leemos la cantidad de exclusivos
        cantidad_exclusivos = int(f.readline())
        # leemos los clientes exclusivos
        for i in range(cantidad_exclusivos):
            self.exclusivos.append(int(f.readline()))
        
        # leemos las distancias y costos entre clientes
        lineas = f.readlines()
        for linea in lineas:
            row = list(map(int,linea.split(' ')))
            self.distancias[row[0]][row[1]] = row[2]
            self.distancias[row[1]][row[0]] = row[2]
            self.costos[row[0]][row[1]] = row[3]
            self.costos[row[1]][row[0]] = row[3]

        self.alcanzables = [[] for _ in range(self.cant_clientes)]

        # preprocesamos A_i
        for i in range(self.cant_clientes):
            for j in range(self.cant_clientes):
                if i != j and self.distancias[i][j] < self.d_max:
                    self.alcanzables[i].append(j)
        
        # cerramos el archivo
        f.close()

def cargar_instancia(instancia_numero):
    # El 1er parametro es el nombre del archivo de entrada
    instancias = [
        "instancias/instancia_unica_parada.txt",
        "instancias/instancia_todos_exclusivos.txt",
        "instancias/instancia_unico_cliente_aislado.txt",
        "instancias/instancia_clusters_refrigerados.txt",
        "instancias/instancia_clusters.txt",
        "instancias/instancia_solo_3_a_pie_1_exclusivo.txt",
    ]
    nombre_archivo = instancias[instancia_numero-1]
    # Crea la instancia vacia
    instancia = InstanciaRecorridoMixto()
    # Llena la instancia con los datos del archivo de entrada 
    instancia.leer_datos(nombre_archivo)
    return instancia

def mostrar_solucion(prob, instancia, instancia_numero, filename, time):
    # 1. Gather solution info
    status    = prob.solution.get_status_string(prob.solution.get_status())
    obj_value = prob.solution.get_objective_value()
    names     = prob.variables.get_names()
    values    = prob.solution.get_values()

    # 2. Open file and write
    with open(f"instancia_{instancia_numero}/{filename}", "w") as f:
        f.write(f"Funcion objetivo: {obj_value} ({status}) in {time:.4f}s\n\n")

        # 3. Arcos x_
        f.write("Variables x_ != 0:\n")
        for name, val in zip(names, values):
            if name.startswith("x_") and abs(val) > TOLERANCE:
                f.write(f"  {name} = {val}\n")

        # 4. Variables y_
        f.write("\nVariables y_ != 0:\n")
        for name, val in zip(names, values):
            if name.startswith("y_") and abs(val) > TOLERANCE:
                f.write(f"  {name} = {val}\n")

        # 5. u_ and p_
        f.write("\nOtras variables (u_, p_):\n")
        for name, val in zip(names, values):
            if name.startswith(("u_", "p_")):
                f.write(f"  {name} = {val}\n")
        
async def main():
    for k in range(1, 7):

        # Lectura de datos desde el archivo de entrada
        instancia_numero = k
        instancia = cargar_instancia(instancia_numero)

        # TSP MTZ Normal
        try:
            prob1 = cplex.Cplex()
            armar_lp_tsp_mtz(prob1,instancia)
            start = prob1.get_time()
            await resolver_lp_tsp_mtz(prob1)
            end = prob1.get_time()
            mostrar_solucion(prob1,instancia, k, f"sol_{instancia_numero}_tsp_mtz.txt", end - start)
        except CplexSolverError as e:
            print(e)

        for i in range(1):
            # if i == 0: 
            #     mip_start = True
            # else:
            #     mip_start = False

            for j in range(5):
                if j == 0: 
                    mip_start = True
                else:
                    mip_start = False

                # MODELO PROPUESTO
                try:
                    if mip_start:
                        nombre_archivo_solucion = f"sol_{instancia_numero}_config{j}_mipstart_tsp_sol.txt" 
                    else:
                        nombre_archivo_solucion = f"sol_{instancia_numero}_config{j}_tsp_sol.txt" 
                    prob2 = cplex.Cplex()
                    armar_lp_tsp_sol(prob2, instancia)
                    start = prob2.get_time()
                    resolver_lp_tsp_sol(prob2, prob1, j, mip_start)
                    end = prob2.get_time()
                    mostrar_solucion(prob2, instancia, k, nombre_archivo_solucion, end - start )
                except CplexSolverError as e:
                    print(e)

                # # MODELO PROPUESTO CON DESEABLE 1
                # if j == 0 and mip_start == False:
                #     try:
                #         prob2 = cplex.Cplex()
                #         armar_lp_tsp_sol_d1(prob2, instancia)
                #         start = prob2.get_time()
                #         resolver_lp_tsp_sol_d1(prob2, prob1, j, mip_start)
                #         end = prob2.get_time()
                #         mostrar_solucion(prob2, instancia, k, f"sol_{instancia_numero}_config{j}_tsp_sol_d1.txt", end - start)
                #     except CplexSolverError as e:
                #         print(e)

                # # MODELO PROPUESTO CON DESEABLE 2
                # if j == 0 and mip_start == False:
                #     try:
                #         prob2 = cplex.Cplex()
                #         armar_lp_tsp_sol_d2(prob2, instancia)
                #         start = prob2.get_time()
                #         resolver_lp_tsp_sol_d2(prob2, prob1, j, mip_start)
                #         end = prob2.get_time()
                #         mostrar_solucion(prob2, instancia, k, f"sol_{instancia_numero}_config{j}_tsp_sol_d2.txt", end - start )
                #     except CplexSolverError as e:
                #         print(e)

if __name__ == '__main__':
    asyncio.run(main())