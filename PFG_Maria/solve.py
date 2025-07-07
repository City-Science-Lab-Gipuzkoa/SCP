def solve(paradas_df, dist_matrix, time_matrix, m, alpha, beta):
    import pandas as pd
    from docplex.mp.model import Model

    stops_coordinates = [(row['stop_lon'], row['stop_lat']) for _, row in paradas_df.iterrows()]

    n = len(stops_coordinates)

    model = Model("mTSP_balanceo_distancia_y_tiempo")
    model.context.cplex_parameters.randomseed = 42
    model.context.cplex_parameters.threads = 1

    # Variables de decisión
    x = {(i, j): model.binary_var(name=f"x_{i}_{j}") for i in range(n) for j in range(n) if i != j}

    # Variables MTZ para subtours
    u = [model.continuous_var(lb=0, ub=n - 1, name=f"u_{i}") for i in range(n)]

    r = [model.continuous_var(lb=0, ub=0, name="r_0")] + \
    [model.continuous_var(lb=0, name=f"r_{i}") for i in range(1, n)]

    r_max = model.continuous_var(name="r_max")
    r_min = model.continuous_var(name="r_min")

    # Restricciones

    # Cada nodo visitado una vez (salvo depósito)
    for j in range(1, n):
        model.add_constraint(model.sum(x[i, j] for i in range(n) if i != j) == 1)

    for i in range(1, n):
        model.add_constraint(model.sum(x[i, j] for j in range(n) if i != j) == 1)

    # m vehículos entran y salen del depósito
    model.add_constraint(model.sum(x[0, j] for j in range(1, n)) == m)
    model.add_constraint(model.sum(x[i, 0] for i in range(1, n)) == m)

    # Subtour elimination (MTZ)
    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                model.add_constraint(u[i] - u[j] + (n - 1) * x[i, j] <= n - 2)

    # Restricciones de tiempo hacia el depósito
    M = 1e5
    for i in range(n):
        for j in range(1, n):
            if i != j:
                model.add_constraint(r[j] >= r[i] + time_matrix[i][j] - M * (1 - x[i, j]))

    # Balanceo del tiempo
    for i in range(1, n):
        model.add_constraint(r_max >= r[i])
        model.add_constraint(r_min <= r[i])

    model.minimize(
        alpha * model.sum(dist_matrix[i][j] * x[i, j] for (i, j) in x) +
        beta * (r_max - r_min)
    )

    # Resolver
    solution = model.solve()
    if solution:
        total_distance = round(sum(dist_matrix[i][j] * solution.get_value(x[i, j]) for (i, j) in x), 4)

        print(f"Total Distance: {total_distance}")

        balanceo_tiempo = round(solution.get_value(r_max) - solution.get_value(r_min), 4)


        # Extraer rutas
        rutas = [[] for _ in range(m)]
        solution_arcs = {(i, j): solution.get_value(x[i, j]) > 0.5 for (i, j) in x}
        salidas_depot = [j for j in range(1, n) if solution_arcs.get((0, j), False)]

        for k in range(m):
            ruta = [0]
            actual = salidas_depot[k]
            while actual != 0:
                ruta.append(actual)
                siguientes = [j for j in range(n) if j != actual and solution_arcs.get((actual, j), False)]
                if siguientes:
                    actual = siguientes[0]
                else:
                    actual = 0
            ruta.append(0)
            rutas[k] = ruta

        print(f"Rutas: f{rutas}")
        
            
        return rutas, total_distance, balanceo_tiempo
        print("Resuelto sin problemas")
    else:
        print("No se encontró solución factible.")
        
def solve_sin_beta(paradas_df, dist_matrix, time_matrix, m):
    import pandas as pd
    from docplex.mp.model import Model
 
    stops_coordinates = [(row['stop_lon'], row['stop_lat']) for _, row in paradas_df.iterrows()]

    n = len(stops_coordinates)

    model = Model("mTSP_balanceo_distancia_y_tiempo")
    model.context.cplex_parameters.randomseed = 42
    model.context.cplex_parameters.threads = 1

    # Variables de decisión
    x = {(i, j): model.binary_var(name=f"x_{i}_{j}") for i in range(n) for j in range(n) if i != j}

    # Variables MTZ para subtours
    u = [model.continuous_var(lb=0, ub=n - 1, name=f"u_{i}") for i in range(n)]

    # Restricciones

    # Cada nodo visitado una vez (salvo depósito)
    for j in range(1, n):
        model.add_constraint(model.sum(x[i, j] for i in range(n) if i != j) == 1)

    for i in range(1, n):
        model.add_constraint(model.sum(x[i, j] for j in range(n) if i != j) == 1)

    # m vehículos entran y salen del depósito
    model.add_constraint(model.sum(x[0, j] for j in range(1, n)) == m)
    model.add_constraint(model.sum(x[i, 0] for i in range(1, n)) == m)

    # Subtour elimination (MTZ)
    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                model.add_constraint(u[i] - u[j] + (n - 1) * x[i, j] <= n - 2)

    model.minimize(
        model.sum(dist_matrix[i][j] * x[i, j] for (i, j) in x)
    )

    # Resolver
    solution = model.solve()
    if solution:
        total_distance = round(sum(dist_matrix[i][j] * solution.get_value(x[i, j]) for (i, j) in x), 4)

        print(f"Total Distance: {total_distance}")

        # Extraer rutas
        rutas = [[] for _ in range(m)]
        solution_arcs = {(i, j): solution.get_value(x[i, j]) > 0.5 for (i, j) in x}
        salidas_depot = [j for j in range(1, n) if solution_arcs.get((0, j), False)]

        for k in range(m):
            ruta = [0]
            actual = salidas_depot[k]
            while actual != 0:
                ruta.append(actual)
                siguientes = [j for j in range(n) if j != actual and solution_arcs.get((actual, j), False)]
                if siguientes:
                    actual = siguientes[0]
                else:
                    actual = 0
            ruta.append(0)
            rutas[k] = ruta

        print(f"Rutas: f{rutas}")
        
            
        return rutas, total_distance
        print("Resuelto sin problemas")
    else:
        print("No se encontró solución factible.")
        
