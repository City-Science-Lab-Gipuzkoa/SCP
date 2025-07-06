import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import os
import generar_grafos
from geopy.distance import geodesic  

def buscar_nombre_mas_cercano(lat, lon, df_stops, tolerancia_m=20):
    coord_punto = (lat, lon)
    for _, row in df_stops.iterrows():
        coord_stop = (row["stop_lat"], row["stop_lon"])
        if geodesic(coord_punto, coord_stop).meters <= tolerancia_m:
            return row["stop_name"]
    return f"({lat:.5f}, {lon:.5f})"


# Cargar datos
df = pd.read_csv("resultados_225.csv")

filtro = (df['alpha'] == 0.1) & \
         (df['beta'] == 1.0)

df = df[filtro].copy()

print(f"Longitud: {df.shape}")

# Agrupar por co2_total y aplicar moda a las columnas deseadas
agrupado = (
    df.groupby('CO2 total')
      .agg({
          #'alpha': lambda x: x.mode().iloc[0] if not x.mode().empty else None,
          #'beta': lambda x: x.mode().iloc[0] if not x.mode().empty else None,
          'k': lambda x: x.mode().iloc[0] if not x.mode().empty else None,
          'm': lambda x: x.mode().iloc[0] if not x.mode().empty else None
      })
      .reset_index()
)

# Ranking para ver en consola
ranking = agrupado.sort_values(by='CO2 total', ascending=True)

# Mover 'co2_total' al final
cols = [col for col in ranking.columns if col != 'CO2 total'] + ['CO2 total']
ranking = ranking[cols]

print(ranking.to_string(index=False))

# Variables
x = df['k']
y = df['m']
z = df['CO2 total']

# Crear grilla regular
xi = np.linspace(x.min(), x.max(), 100)
yi = np.linspace(y.min(), y.max(), 100)
xi, yi = np.meshgrid(xi, yi)

# Interpolación
zi = griddata((x, y), z, (xi, yi), method='cubic')

# Crear gráfico
fig, ax = plt.subplots(figsize=(10, 6))
contour = ax.contourf(xi, yi, zi, levels=100, cmap='viridis')

# Colorbar con etiqueta movida y en negrita
cbar = plt.colorbar(contour, ax=ax)
cbar.set_label('CO2 Emitted (kg)', fontsize=12, fontweight='bold', labelpad=15)  # ← mueve etiqueta a la derecha

# Puntos reales
ax.scatter(x, y, c='white', edgecolors='black')

# Títulos
ax.set_title('CO2 Emissions vs k and m', fontsize=14, fontweight='bold')
ax.set_xlabel('k (Number of Stops)', fontsize=12, fontweight='bold')
ax.set_ylabel('m (Number of Routes)', fontsize=12, fontweight='bold')

# Ticks en negrita
ax.tick_params(axis='both', labelsize=10)
for label in ax.get_xticklabels() + ax.get_yticklabels():
    label.set_fontweight('bold')

# Ticks del colorbar en negrita
cbar.ax.tick_params(labelsize=10)  # Tamaño opcional
for label in cbar.ax.get_yticklabels():
    label.set_fontweight('bold')

# Guardar antes de mostrar
plt.tight_layout()
plt.savefig("Grafico_CO2_paradas_225.png", dpi=300)
plt.show()

