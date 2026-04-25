import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pickle
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.config import INTERVENTIONS

app = FastAPI(
    title='Customer Segmentation API',
    description='Predicts customer segment and returns intervention recommendation based on RFM values.',
    version='1.0.0'
)


# Load models at startup
with open('data/processed/xgb.pkl', 'rb') as f:
    xgb_model = pickle.load(f)

with open('data/processed/label_encoder.pkl', 'rb') as f:
    le = pickle.load(f)


# Input schemas
class CustomerRFM(BaseModel):
    recency: int
    frequency: int
    monetary: int

    class Config:
        json_schema_extra = {
            'example': {
                'recency': 45,
                'frequency': 3,
                'monetary': 850
            }
        }


@app.api_route("/", methods=["GET", "HEAD"])
def health():
    return {"status": "ok"}


# Prediction endpoint
@app.post("/predict")
def predict_customer(data: CustomerRFM):
    try:
        # Convert to array
        input_data = np.array([[data.recency, data.frequency, data.monetary]],
                              dtype=float)

        # Predict
        pred = xgb_model.predict(input_data)

        # Decode label
        segment = le.inverse_transform(pred)[0]

        # Map intervention
        intervention = INTERVENTIONS.get(segment)
        if not intervention:
            raise ValueError(f'No intervention defined for {segment}')
        
        expected_revenue = intervention["lift_rate"] * intervention["avg_order_value"]

        return {
            "segment": segment,
            "treatment": intervention["treatment"],
            "baseline_conv_rate": intervention["baseline_rate"],
            "treatment_conv_rate": intervention["baseline_rate"] + intervention["lift_rate"],
            "expected_incremental_revenue": round(expected_revenue, 2),
            "campaign_cost_per_customer": intervention["cost_per_customer"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

    


