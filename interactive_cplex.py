import cplex

def solve_cplex(
    is_objective_maximized: bool, 
    var_names: list[str], 
    lower_bounds: list[float] = None, 
    upper_bounds: list[float] = None,
    objective_coefficients: list[float] = None,
    constraint_names: list[str] = None,
    constraint_coefficient_rows: list[list[float]] = None,
    constraint_senses: list[str] = None,
    constraint_rhs: list[float] = None,
    write_lp_file: bool = False,
):
    # 1. Inicializar CPLEX
    prob = cplex.Cplex()

    # 2. Definir el tipo de problema: maximización o minimización
    if is_objective_maximized:
        prob.objective.set_sense(prob.objective.sense.maximize)
    else:
        prob.objective.set_sense(prob.objective.sense.minimize)

    # 3. Definir las variables 
    prob.variables.add(obj=objective_coefficients, lb=lower_bounds, ub=upper_bounds, names=var_names)

    # 4. Definir las restricciones.
    constraint_rows = [[var_names, row] for row in constraint_coefficient_rows]  
    prob.linear_constraints.add(
        lin_expr=constraint_rows, 
        senses=constraint_senses, 
        rhs=constraint_rhs, 
        names=constraint_names
    )

    # Opcionalmente, escribir el modelo a un archivo LP.
    if write_lp_file:
        prob.write('problem.lp')

    # 5. Resolver el problema.
    prob.solve()

    # 6. Mostrar la solución.
    print('--------------------------------------------------')
    print("Estado de la solución:", prob.solution.get_status_string(status_code=prob.solution.get_status()))
    print("Valor objetivo:", prob.solution.get_objective_value())
    print("Valores de las variables:", prob.solution.get_values())


if __name__ == '__main__':
    print("Bienvenido al generador interactivo de modelos LP.")

    # Preguntar por el tipo de función objetivo.
    obj_input = input("¿Se maximiza la función objetivo? (True/False): ").strip()
    is_objective_maximized = obj_input.lower() in ["true", "t", "sí", "si", "yes", "1"]

    # Cantidad de variables.
    n_vars = int(input("Ingrese la cantidad de variables: "))
    # Crear automáticamente los nombres de las variables (x1, x2, ..., xn)
    var_names = [f"x{i+1}" for i in range(n_vars)]

    # Recopilar los límites inferiores/superiores y los coeficientes de la función objetivo.
    lower_bounds = []
    upper_bounds = []
    objective_coefficients = []
    for var in var_names:
        lb_input = input(f"Ingrese el límite inferior para {var} (presione Enter para usar el valor por defecto 0): ").strip()
        if lb_input == "":
            lower_bounds.append(0.0)
        else:
            lower_bounds.append(float(lb_input))
        
        ub_input = input(f"Ingrese el límite superior para {var} (presione Enter para dejar sin límite): ").strip()
        if ub_input == "":
            # Se utiliza cplex.infinity para representar sin límite superior.
            upper_bounds.append(cplex.infinity)
        else:
            upper_bounds.append(float(ub_input))
        
        coeff = float(input(f"Ingrese el coeficiente objetivo para {var}: "))
        objective_coefficients.append(coeff)

    # Recopilar datos de las restricciones.
    n_constraints = int(input("Ingrese la cantidad de restricciones: "))
    constraint_names = []
    constraint_coefficient_rows = []
    constraint_senses = []
    constraint_rhs = []
    
    for j in range(n_constraints):
        constraint_names.append(f"C{j+1}")
        print(f"\nIngrese los coeficientes para la restricción {j+1}:")
        coeffs = []
        for var in var_names:
            a_ij = float(input(f"  Coeficiente para {var}: "))
            coeffs.append(a_ij)
        constraint_coefficient_rows.append(coeffs)
        
        sense = input(f"Ingrese el sentido de la restricción {j+1} (L para <=, U para >=, E para =): ").strip().upper()
        if sense not in ["L", "U", "E", "l", "u", "e"]:
            print("  Sentido inválido. Se establece por defecto L (<=).")
            sense = "L"
        constraint_senses.append(sense.upper())
        
        rhs_val = float(input(f"Ingrese el valor del lado derecho para la restricción {j+1}: "))
        constraint_rhs.append(rhs_val)

    write_lp_flag = input("¿Desea escribir el archivo LP? (si/no): ").strip().lower()
    write_lp_file = write_lp_flag.startswith("s") or write_lp_flag.startswith("y")
    
    # Ejecutar el solver con los parámetros recopilados.
    solve_cplex(
        is_objective_maximized=is_objective_maximized,
        var_names=var_names,
        lower_bounds=lower_bounds,
        upper_bounds=upper_bounds,
        objective_coefficients=objective_coefficients,
        constraint_names=constraint_names,
        constraint_coefficient_rows=constraint_coefficient_rows,
        constraint_senses=constraint_senses,
        constraint_rhs=constraint_rhs,
        write_lp_file=write_lp_file
    )
