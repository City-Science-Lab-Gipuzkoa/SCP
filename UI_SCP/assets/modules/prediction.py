import pickle
import os
import numpy as np
# Plot
import matplotlib.pyplot as plt
import pandas as pd

def categorize(code):
    if code ==0:
        return 'walk'
    elif code ==1:
        return 'PT'
    else:
        return 'car'

def predict(df, model_dir):
    model_name = "rf"  # El nombre del modelo que guardaste anteriormente
    #file_path = os.path.join("models", f'{model_name}.pkl')
    #with open(file_path, 'rb') as file:
    with open(model_dir+f'{model_name}.pkl', 'rb') as file:
        model = pickle.load(file)
    x = np.array(df.drop(columns = ['Mun_Des', 'Mun_Ori', 'O_long', 'O_lat', 'D_long', 'D_lat']))
    y_pred = model.predict(x)
    unique_labels, counts = np.unique(y_pred, return_counts=True)
    d = {'mode_code': y_pred}
    df = pd.DataFrame(data=d)
    df['Mode'] = df['mode_code'].apply(categorize)
    labels = ['walk', 'PT', 'car']
    colors = ['#99ff66','#00ffff','#ff3300']
    print('Prediction')
    print(y_pred)
    print('Counts')
    print(counts)
    print(df.head(20))
    #plt.figure(figsize=(8, 8))
    ##plt.pie(counts, labels=unique_labels, autopct='%1.1f%%', startangle=140)
    #plt.pie(counts, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
    #plt.title('Mode choice for commuters to Eskuzaitzeta')
    #plt.show()
    return y_pred