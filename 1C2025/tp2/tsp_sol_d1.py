import sys
import cplex

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
    coef_fo_x = []
    for i in range(n):
        for j in range(i+1, n): # defino x_ij, x_ji con mismo costo en una pasada y evito definir x_ii
            x += [f"x_{i}_{j}", f"x_{j}_{i}"]
            coef_fo_x += [instancia.costos[i][j]]*2 # c_ij = c_ji

    y = []
    coef_fo_y = []
    for k in range(n):
        for i in instancia.alcanzables[k]: 
            y += [f"y_{k}_{i}"]
            coef_fo_y += [instancia.costo_repartidor] 

    # agrego x_ij, y_ki
    prob.variables.add(
        obj = coef_fo_x + coef_fo_y, 
        types= [prob.variables.type.binary]*len(x+y), 
        names= x + y
    ) 

    u = [f"u_{i}" for i in range(n)]

    # agrego u_i
    prob.variables.add(
        names=u,
        lb=[0] + [1]*(n-1),
        ub=[0] + [n-1]*(n-1),
        types=[prob.variables.type.integer]*n
    )

    p = [f"p_{i}" for i in range(n)]

    # agrego p_i
    prob.variables.add(
        names=p,
        types=[prob.variables.type.binary]*n
    )

    r = [f"r_{i}" for i in range(1, n)]

    # agrego r_i
    prob.variables.add(
        names=r,
        types=[prob.variables.type.binary]*(n-1)
    )

def agregar_restricciones(prob, instancia):

    n = instancia.cant_clientes

    # sum_k y_ki + sum_j x_ji = 1
    for k in range(n):
        inds_y = [ f"y_{k}_{i}" 
           for i in range(n) 
           if k in instancia.alcanzables[i] ]
        inds_x = [f"x_{j}_{k}" for j in range(n) if j != k] 
        prob.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=inds_y + inds_x, val=[1]*len(inds_y) + [1]*len(inds_x))],
            senses=["E"],
            rhs=[1]
        )

    # y_ki <= p_i o bien y_ki - p_i <= 0  
    for i in range(n):
        for k in instancia.alcanzables[i]:
            prob.linear_constraints.add(
                lin_expr=[cplex.SparsePair(ind=[f"y_{k}_{i}", f"p_{i}"], val=[1, -1])],
                senses=["L"],
                rhs=[0]
            )

    # suma_j x_ij = p_i o bien suma_j x_ij - p_i = 0
    for i in range(n):
        inds = [f"x_{i}_{j}" for j in range(n) if j != i] + [f"p_{i}"]
        prob.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=inds, val=[1]*(len(inds)-1) + [-1])],
            senses=["E"],
            rhs=[0]
        )

    # suma_j x_ji = p_i o bien suma_j x_ji - p_i = 0 
    for i in range(n):
        inds = [f"x_{j}_{i}" for j in range(n) if i != j] + [f"p_{i}"]
        prob.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=inds, val=[1]*(len(inds)-1) + [-1])],
            senses=["E"],
            rhs=[0]
        )

    # continuidad
    # u_i + u_j + (n-1)x_i_j - (n-1)p_i <= 0
    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                prob.linear_constraints.add(
                    lin_expr=[cplex.SparsePair(
                        ind=[f"u_{i}", f"u_{j}", f"x_{i}_{j}", f"p_{i}"],
                        val=[1, -1, (n-1), (-n+2)]
                    )],
                    senses=["L"],
                    rhs=[0]
                )

    # y_{k,i} + p_k ≤ 1 "no reparte a si mismo"
    for i in range(n):
        for k in instancia.alcanzables[i]:
            prob.linear_constraints.add(
                lin_expr=[cplex.SparsePair(ind=[f"y_{k}_{i}", f"p_{k}"], val=[1, 1])],
                senses=["L"],
                rhs=[1]
            )
    
    # u_0 = 0   
    prob.linear_constraints.add(
        lin_expr=[cplex.SparsePair(ind=["u_0"], val=[1])],
        senses=["E"],
        rhs=[0]
    )

    # p_0 = 1
    prob.linear_constraints.add(
        lin_expr=[cplex.SparsePair(ind=["p_0"], val=[1])],
        senses=["E"],
        rhs=[1]
    )

    # sum_k y_ki <= 1
    for i in range(n):
        inds = [f"y_{k}_{i}"
            for k in instancia.refrigerados          
            if i in instancia.alcanzables[k]          
            and k != i] 
        if inds:
            prob.linear_constraints.add(
                lin_expr=[cplex.SparsePair(ind=inds, val=[1]*len(inds))],
                senses=["L"],
                rhs=[1]
            )

    # restriccion deseable 1: (n-1)*r_i >= sum_k y_ki >= 4*r_i 
    # (n-1)*p_i - sum_k y_ki >= 0
    for i in range(n):
        inds_y = [f"y_{k}_{i}" for k in instancia.alcanzables[i]] 
        if inds_y:
            inds = [f"r_{i}"] + inds_y
            prob.linear_constraints.add(
                lin_expr=[cplex.SparsePair(ind=inds, val=[n-1] + [-1]*(len(inds)-1))],
                senses=["G"],
                rhs=[0]
            )

    # sum_k y_ki - 4*r_i >= 0 
    for i in range(n):
        inds = [f"y_{k}_{i}" for k in instancia.alcanzables[i]] 
        if inds:
            inds += [f"r_{i}"]
            prob.linear_constraints.add(
                lin_expr=[cplex.SparsePair(ind=inds, val=[1]*(len(inds)-1) + [-4])],
                senses=["G"],
                rhs=[0]
            )

    # r_i - p_i <= 0
    for i in range(1, n):
        prob.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=[f"r_{i}", f"p_{i}"], val=[1, -1])],
            senses=["L"],
            rhs=[0]
        )

def armar_lp_tsp_sol_d1(prob, instancia):

    # Agregar las variables
    agregar_variables(prob, instancia)
   
    # Agregar las restricciones 
    agregar_restricciones(prob, instancia)

    # Setear el sentido del problema
    prob.objective.set_sense(prob.objective.sense.minimize)

    # Escribir el lp a archivo
    prob.write('modelo_tsp_sol.lp')

def resolver_lp_tsp_sol_d1(prob, prob_tsp_mtz = None, config_number = 0, mip_start = False):
    
    # Definir los parametros del solver
    prob.parameters.timelimit.set(900.0)
    prob.parameters.mip.tolerances.mipgap.set(TOLERANCE)
    if (mip_start):
        prob.MIP_starts.add(
            cplex.SparsePair(ind=prob_tsp_mtz.variables.get_names(), val=prob_tsp_mtz.solution.get_values()),
            prob.MIP_starts.effort_level.repair,
        )
    if config_number == 1:
        prob.parameters.tune_problem()
    if config_number == 2:
        # FACTIBILIDAD
        prob.parameters.emphasis.mip.set(1)
        prob.parameters.mip.strategy.heuristiceffort.set(2.0)
    if config_number == 3:
        # CORTES AGRESIVOS
        prob.parameters.mip.cuts.cliques.set(2)   
        prob.parameters.mip.cuts.covers.set(2)  
        prob.parameters.mip.cuts.flowcovers.set(2)  
    if config_number == 4:
        # OPTIMALIDAD
        prob.parameters.emphasis.mip.set(2)
        prob.parameters.mip.cuts.cliques.set(2)   
        prob.parameters.mip.cuts.covers.set(2)  
        prob.parameters.mip.cuts.flowcovers.set(2) 
       
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

    y_nz = [(n, v) for n, v in zip(names, values) 
                if n.startswith('y_') and abs(v) > TOLERANCE]

    for n, v in y_nz:
        print(f"  {n} = {v}")

    other_vars = [(n, v) for n, v in zip(names, values)
                    if n.startswith('u_') or n.startswith('p_')]

    for n, v in other_vars:
        print(f"  {n} = {v}")

def main():
    
    # Lectura de datos desde el archivo de entrada
    instancia = cargar_instancia()
    
    # Definicion del problema de Cplex
    prob = cplex.Cplex()
    
    # Definicion del modelo
    armar_lp_tsp_sol_d1(prob,instancia)

    # Resolucion del modelo
    resolver_lp_tsp_sol_d1(prob, )

    # Obtencion de la solucion
    mostrar_solucion(prob,instancia)

if __name__ == '__main__':
    main()