import os
import pandas as pd
import numpy as np
import main_optimo

alpha = 0.1
beta = 1.0
k = 8
m = 2

workers_df = pd.read_csv("workers_df_225.csv")
co2_total_final = main_optimo.resolver(workers_df, alpha, beta, k, m)
