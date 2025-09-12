import asyncio
import sys
import cplex, pathlib, sys

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
            self.distancias[row[0]-1][row[1]-1] = row[2]
            self.distancias[row[1]-1][row[0]-1] = row[2]
            self.costos[row[0]-1][row[1]-1] = row[3]
            self.costos[row[1]-1][row[0]-1] = row[3]
        
        # cerramos el archivo
        f.close()

def cargar_instancia():
    # El 1er parametro es el nombre del archivo de entrada
    nombre_archivo = sys.argv[1].strip()
    # Crea la instancia vacia
    instancia = InstanciaRecorridoMixto()
    # Llena la instancia con los datos del archivo de entrada 
    instancia.leer_datos(nombre_archivo)
    return instancia

def agregar_variables(prob, instancia):

    n = instancia.cant_clientes

    x = []
    coef_fo = []
    for i in range(n):
        for j in range(i+1, n): # defino x_ij, x_ji con mismo costo en una pasada y evito definir x_ii
            x += [f"x_{i}_{j}", f"x_{j}_{i}"]
            coef_fo += [instancia.costos[i][j]]*2 # c_ij = c_ji

    # agrego x_ij
    prob.variables.add(
        obj = coef_fo, 
        types=[prob.variables.type.binary]*len(x), 
        names=x
    ) 

    u = [f"u_{i}" for i in range(n)]

    # agrego u_i
    prob.variables.add(
        names=u,
        lb=[0] + [1]*(n-1),
        ub=[0] + [n-1]*(n-1),
        types=[prob.variables.type.continuous]*n
    )

def agregar_restricciones(prob, instancia):

    n = instancia.cant_clientes

    # suma_j x_ij = 1
    for i in range(n):
        inds = [f"x_{i}_{j}" for j in range(n) if j != i]
        prob.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=inds, val=[1]*len(inds))],
            senses=["E"],
            rhs=[1]
        )

    # suma_i x_ij = 1
    for j in range(n):
        inds = [f"x_{i}_{j}" for i in range(n) if i != j]
        prob.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=inds, val=[1]*len(inds))],
            senses=["E"],
            rhs=[1]
        )

    # continuidad
    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                prob.linear_constraints.add(
                    lin_expr=[cplex.SparsePair(
                        ind=[f"u_{i}", f"u_{j}", f"x_{i}_{j}"],
                        val=[1, -1, (n-1)]
                    )],
                    senses=["L"],
                    rhs=[n-2]
                )
    
    # u_0 = 0   
    prob.linear_constraints.add(
        lin_expr=[cplex.SparsePair(ind=["u_0"], val=[1])],
        senses=["E"],
        rhs=[0]
    )

def armar_lp_tsp_mtz(prob, instancia):

    # Agregar las variables
    agregar_variables(prob, instancia)
   
    # Agregar las restricciones 
    agregar_restricciones(prob, instancia)

    # Setear el sentido del problema
    prob.objective.set_sense(prob.objective.sense.minimize)

    # Escribir el lp a archivo
    prob.write('modelo_tsp_mtz.lp')

async def resolver_lp_tsp_mtz(prob):
    
    # Definir los parametros del solver
    prob.parameters.timelimit.set(900.0)
    prob.parameters.mip.tolerances.mipgap.set(TOLERANCE)
       
    # Resolver el lp
    prob.solve()

def mostrar_solucion(prob,instancia):
    
    # Obtener informacion de la solucion a traves de 'solution'
    
    # Tomar el estado de la resolucion
    status = prob.solution.get_status_string(status_code = prob.solution.get_status())
    
    # Tomar el valor del funcional
    valor_obj = prob.solution.get_objective_value()
    
    print('Funcion objetivo: ',valor_obj,'(' + str(status) + ')')
    
    # Tomar los valores de las variables
    names  = prob.variables.get_names()
    values = prob.solution.get_values()

    x_nz = [(n, v) for n, v in zip(names, values) 
                if n.startswith('x_') and abs(v) > TOLERANCE]

    for n, v in x_nz:
        print(f"  {n} = {v}")

    other_vars = [(n, v) for n, v in zip(names, values)
                    if not n.startswith('x_')]

    for n, v in other_vars:
        print(f"  {n} = {v}")

async def main():
    
    # Lectura de datos desde el archivo de entrada
    instancia = cargar_instancia()
    
    # Definicion del problema de Cplex
    prob = cplex.Cplex()
    
    # Definicion del modelo
    armar_lp_tsp_mtz(prob,instancia)

    # Resolucion del modelo
    await resolver_lp_tsp_mtz(prob)

    # Obtencion de la solucion
    mostrar_solucion(prob,instancia)

if __name__ == '__main__':
    asyncio.run(main())