In case you want to run these codes, you should run them on the following order:

- `surveys.ipynb` cleans, treats and postprocesses the survey data, adding salary data to each trip-taker.
- `landuse&section_aggregation.ipynb` generates a building database, including land use and neighborhood-wealth characteristics.
- `edificios.ipynb` takes the previous buildings and clusters them to reduce computing time.
- `intermunicipal_travel_cost.ipynb` calculates travel fares between towns and regions for different public transport companies.
- `create_road_network.ipynb` creates the pandana road and walk networks from OpenStreetMaps to calculate driving and walking travel times.
- `GTFS_24.ipynb` creates the pandana transit networks (24, one for each hour) to calculate transit travel times. This is done using [UrbanAccess](https://github.com/UDST/urbanaccess) library.

Additional code, not necessary to create the model.

- `population_generation.ipynb` generates a placeholder of ~2500 workers commuting to a same place (industrial park) to create different scenarios once the model is created.
