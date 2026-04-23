import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import pickle
import os


def compute_rfm(df, snapshot_date='2011-12-10', scaler_path=None):
    """
    Takes a raw transactions df and returns a scaled RFM dataframe.
    
    Parameters:
        df: raw transactions df
        snapshot_date: reference date for recency calculation
        scaler_path: path to saved scaler pickle. If None fits a new scaler

    Returns:
        rfm: df with Customer ID, Recency, Frequency, Monetary
        rfm_scaled: scaled and log transformed RFM features
    """

    snapshot = pd.Timestamp(snapshot_date)

    df = df.copy()
    df['Customer ID'] = df['Customer ID'].astype(str)
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['Revenue'] = df['Price'] * df['Quantity']

    rfm = df.groupby('Customer ID').agg(
        Recency = ('InvoiceDate', lambda x: (snapshot - x.max()).days),
        Frequency = ('Invoice', 'nunique'),
        Monetary = ('Revenue', 'sum')
    ).reset_index()

    rfm_log = rfm.copy()
    rfm_log['Recency'] = np.log1p(rfm['Recency'])
    rfm_log['Frequency'] = np.log1p(rfm['Frequency'])
    rfm_log['Monetary'] = np.log1p(rfm['Monetary'])

    if scaler_path and os.path.exists(scaler_path):
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
            rfm_scaled = scaler.transform(rfm_log[['Recency', 'Frequency', 'Monetary']])
    else:
        scaler = StandardScaler()
        rfm_scaled = scaler.fit_transform(rfm_log[['Recency', 'Frequency', 'Monetary']])

    rfm_scaled = pd.DataFrame(rfm_scaled, columns=['Recency', 'Frequency', 'Monetary'])

    return rfm, rfm_scaled