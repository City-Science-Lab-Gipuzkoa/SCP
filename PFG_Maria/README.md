# Route Optimization and CO₂ Prediction using mTSP

This project implements an evaluation framework for optimized public transport routes using the Multi-Traveling Salesman Problem (mTSP). It generates GTFS feeds, computes CO₂ emissions, and produces visual and tabular outputs to support sustainable mobility planning.

---

## 🚀 What the Code Does

- Clusters workers into groups based on a transport graph (from OSM data)
- Generates stop permutations and solves the mTSP using IBM CPLEX (`docplex`)
- Builds time and distance matrices for all permutations of stops
- Solves the mTSP problem, and calculates the CO₂ emissions from those routes
- Creates GTFS feeds from the resulting routes
- Runs a prediction model that predicts the transport mode of the input workers
- Estimates total CO₂ emissions from workers changing transport modes and stores outputs
- Visualizes results with `folium` (interactive HTML maps) with the routes and the stops

---

## 📂 Project Structure

```
.
├── evaluar_una_comb.py             # Run one route combination with a combination of number of workers, alpha, beta, k and m
├── MCM.py                          # Run the Mode Choice Model
├── SCP_files/
│   ├── run_MCM.py                 # Prediction model script
│   └── assets/data/input_data_MCM/
├── combinacion_unica/              # Folder with output for one combination run previously
├── workers_df_225.csv              # 225 Workers' locations
├── all_bus_stops.csv               # Potential stop locations in Gipuzkoa
├── requirements.txt                # Python pip dependencies
└── *.py                            # Supporting scripts (matrix generation, graphs, maps, etc.)
```

---

## ⚙️ Instructions

### 1. Set up the environment

Using conda:

```bash
conda create -n mtsp_env python=3.10
conda activate mtsp_env
pip install -r requirements.txt
```

### 2. How to Run one route combination

```bash
python evaluar_una_comb.py
```

This will:

- Perform clustering on workers and stops  
- Solve the mTSP with distance and time matrices  
- Generate the GTFS feed  
- Predict travel-related emissions  
- Visualize the result on an interactive HTML map  
- Print results including:
  - Total distance  
  - Passenger time balance  
  - Route emissions  
  - MCM model emissions  
  - Total CO₂ emissions

### 3. To run a variant without the β (passenger time balance) component:

```python
resolver_sin_beta(k=5, m=2)
```

---

### 4. There is a missing file that is too large to upload in this repository
The file `stop_times.txt` (256 MB) is not included due to size limitations. 

You can download it from: 
[Link to Google Drive](https://drive.google.com/drive/folders/1eNjwZo19QImVU2ufr3TTcW2HAL9wq0JD?usp=drive_link)

Once downloaded, place it in the folders: 
`PFG_Maria/SCP_files/assets/data/input_data_MCM/GTFS_feeds/Renfe_cercanias/`
`PFG_Maria/SCP_files/assets/data/input_data_MCM/GTFS_feeds_backup/Renfe_cercanias/`


##  Output Files

- `Data_after_prediction_id_*.csv`: prediction results  
- `rutas.csv`: solved vehicle routes  
- `rutas_coords.csv`: route coordinates  
- `df_stops.csv`, `time_mat.csv`, `dist_mat.csv`: input data for each scenario  
- `mapa_combinacion_unica.html`: interactive visualization

---

##  Main Dependencies

- `pandas`, `numpy`, `matplotlib`, `folium`  
- `osmnx`, `urbanaccess`, `networkx`  
- `docplex` (for mTSP modeling with IBM CPLEX)  
- `scikit-learn`, `dash`, `plotly`  
- `geopandas`, `pyproj`, `rasterio`, `SALib`  

Check `requirements.txt` for the complete list.

---

## Author

Developed by **María Peña**  
Final Year Project – Tecnun, University of Navarra
