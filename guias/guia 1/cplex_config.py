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

    # 2. Definir el tipo de problema
    if is_objective_maximized:
        prob.objective.set_sense(prob.objective.sense.maximize)
    else:
        prob.objective.set_sense(prob.objective.sense.minimize)

    # 3. Definir las variables
    if lower_bounds:
      prob.variables.add(obj=objective_coefficients, lb=lower_bounds, names=var_names)
    if upper_bounds:
      prob.variables.add(obj=objective_coefficients, ub=upper_bounds, names=var_names)

    # 4. Definir las restricciones
    constraint_rows = [[var_names, row] for row in constraint_coefficient_rows]  
    prob.linear_constraints.add(lin_expr=constraint_rows, senses=constraint_senses, rhs=constraint_rhs, names=constraint_names)

    # Para depurar el codigo
    if write_lp_file:
      prob.write('problem.lp')

    # 5. Resolver el problema
    prob.solve()

    # 6. Mostrar la solucion
    print('--------------------------------------------------')
    print("Estado de la solución:", prob.solution.get_status_string(status_code = prob.solution.get_status()))
    print("Valor objetivo:", prob.solution.get_objective_value())
    print("Solución:", prob.solution.get_values())