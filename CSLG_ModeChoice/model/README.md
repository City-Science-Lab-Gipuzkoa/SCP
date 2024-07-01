- `pre_model.ipynb` adds noise to survey data, assigns origin and destination to each trip, and calculates the travel time for each mode of transportation.
- `training_model.ipynb` reads the output file from `pre_model.ipynb` and trains the supervised learning AI model.
- `predict_().ipynb` are different codes predicting the mobility mode choice in a number scenarios using the aforementioned AI model. This scenarios include:
    - Moving people closer to their workplace.
    - Moving people to a walkable distance from their workplace.
    - Changing the workplace location.
    - ...

Notes: 
- To run `pre_model.ipynb` you will need a GOOGLE API key to download data from the *distancematrix* API.
- If you are having trouble running `pre_model.ipynb`, download the [results](https://drive.google.com/drive/folders/13u5F34FRRHQqKfsz_SR6Hg-2XtPmNWdI?usp=sharing) folder and paste it on the \model directory.
