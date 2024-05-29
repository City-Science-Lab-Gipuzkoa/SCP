**Mobility mode choice model using Gipuzkoa (Spain) as a use case**

# Folders
- [model](https://github.com/Inigo-Azcarate/Mobility_Choice/tree/main/model) contains the code to create the supervised learning AI model that predicts the mobility choices. 
- [input_data](https://github.com/Inigo-Azcarate/Mobility_Choice/tree/main/input_data) contains all the data necessary to run the AI model in the \model folder. Some of the containing data is raw and the rest is a result of the codes in the \preprocessing folder.
- [preprocessing](https://github.com/Inigo-Azcarate/Mobility_Choice/tree/main/preprocessing) contains the codes and the raw data to create the files in input files in \input_data.


# Code files
- `surveys.ipynb` cleans, treats and postprocessesof the survey data, adding salary data to each trip-taker
- `analysis_graphics.ipynb` generates graphs related to mode of transportation from survey data
- `population_generation.ipynb` generates a placeholder of ~2500 workers commuting to Eskuzaitzeta.
- `landuse&section_aggregation.ipynb` generates a building database, including land use and neighborhood-wealth characteristics
- `intermunicipal_travel_cost.ipynb` calculates travel fares between towns and regions for different public transport companies
- `create_road_network.ipynb` creates the pandana road network from OpenStreetMaps to calculate driving times from origin to destination
- `GTFS_transit_24.ipynb` creates the pandana transit networks (24, one for each hour) to calculate bus times from origin to destination
- `GTFS_train_24.ipynb` creates the pandana train networks (24, one for each hour) to calculate bus times from origin to destination

- `model.ipynb` adds noise to survey data, assigns origin and destination to each trip, and calculates the mode of transportation’s travel time and travel cost. Then, it trains the supervised learning AI model.
- `predict.ipynb` uses the aforementioned AI model (Random Forest Classifier) and predicts the mode of transportation for an specific population

![Preprocessing files](images/preprocessing_pic.png)