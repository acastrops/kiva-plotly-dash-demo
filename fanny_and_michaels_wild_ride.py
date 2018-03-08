#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  8 11:39:09 2018

@author: Mike
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import numpy as np


df = pd.read_csv('data/kiva_loans.csv')

df_clean = df[['country','borrower_genders']]
df_clean.dropna()
df_clean[['borrower_genders']].astype(str)

mask = (df_clean['borrower_genders'].str.len() <= 6)

df_clean = df_clean.loc[mask]

