import numpy as np
from SALib.sample import morris
from SALib.analyze import morris as morris_analyze
import main_optimo
import pandas as pd
import os

# --- Definir el problema ---
problem = {
    'num_vars': 4,
    'names': ['alpha', 'beta', 'k', 'rel'],
    'bounds': [
        [0.1, 1.0],     # alpha
        [1.0, 10.0],    # beta
        [3, 8],         # k
        [0.25, 1.0]     # relación m/k
    ]
}

workers_df = pd.read_csv("workers_df_225.csv")
df_prev = pd.DataFrame(columns=['alpha', 'beta', 'k', 'm', 'co2_total'])

# --- Sampleo de Morris ---
N = 30
samples = morris.sample(problem, N, num_levels=4)

# --- Evaluar muestras ---
results = []
Y = []

for sample in samples:
    alpha = round(float(sample[0]), 4)
    beta = round(float(sample[1]), 4)
    k = int(np.round(sample[2]))
    rel = float(sample[3])
    m = int(np.floor(k * rel))
    m = max(1, m)

    try:
        co2 = main_optimo.resolver(workers_df, alpha, beta, k, m)
        print(f"Calculado: alpha={alpha}, beta={beta}, k={k}, m={m} -> CO2={co2}")
        # Guardar nuevo resultado
        new_row = pd.DataFrame([{
            'alpha': alpha,
            'beta': beta,
            'k': k,
            'm': m,
            'co2_total': co2
        }])
        df_prev = pd.concat([df_prev, new_row], ignore_index=True)
    except Exception as e:
        print(f"Error en alpha={alpha}, beta={beta}, k={k}, m={m}: {e}")
        continue

    results.append({'alpha': alpha, 'beta': beta, 'k': k, 'm': m, 'co2_total': co2})
    Y.append(co2)

# --- Guardar resultados actualizados ---
df_prev.to_csv("resultados_morris.csv", index=False)

# --- Análisis de sensibilidad Morris ---
Si = morris_analyze.analyze(
    problem,
    samples[:len(Y)],
    np.array(Y),
    num_levels=4,
    num_resamples=10,
    conf_level=0.95,
    print_to_console=False
)

print("\nMu* (mu_star) para cada variable:")
for name, mu_star in zip(problem['names'], Si['mu_star']):
    print(f"{name}: {mu_star:.4f}")
