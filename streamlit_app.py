import streamlit as st
import requests

API_URL = "https://customer-segmentation-interventions.onrender.com/predict"

st.set_page_config(
    page_title='Customer Segmentation and Intervention',
    layout='centered'
)

# Header
st.title("Customer Segmentation and Intervention Recommender")
st.markdown("Enter a customer's RFM values to predict their segment and get a targeted intervention recommendation.")
st.divider()


# Input sliders
st.subheader("Customer RFM Input")

col1, col2, col3 = st.columns(3)

with col1:
    recency = st.number_input("Recency (days since last purchase)", min_value=0, max_value=400, value=30)

with col2:
    frequency = st.number_input("Frequency (number of invoices)", min_value=1, max_value=210, value=3)

with col3:
    monetary = st.number_input("Monetary (total spend INR)", min_value=0.0, max_value=300000.0, value=500.0)

st.divider()


# Predict button and response
if st.button("Predict Segment", type="primary"):
    with st.spinner("Calling model..."):
        try:
            response = requests.post(
                API_URL,
                json={
                    "recency": recency,
                    "frequency": frequency,
                    "monetary": monetary
                },
                timeout=60
            )

            st.write(f"Status code: {response.status_code}")
            st.write(f"Raw response: {response.text}")
            
            result = response.json()

            segment = result["segment"]
            treatment = result["treatment"]
            baseline = result["baseline_conv_rate"]
            treatment_rate = result["treatment_conv_rate"]
            revenue = result["expected_incremental_revenue"]
            cost = result["campaign_cost_per_customer"]

            segment_colors = {
                "Champions": "🟢",
                "Promising": "🔵",
                "At-Risk": "🟠",
                "Lost": "🔴"
            }

            st.subheader("Prediction Result")
            st.markdown(f"## {segment_colors.get(segment, '')} {segment}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Recommended Treatment", treatment)
                st.metric("Baseline Conversion Rate", f"{baseline*100:.0f}%")
                st.metric("Treatment Conversion Rate", f"{treatment_rate*100:.0f}%")

            with col2:
                st.metric("Expected Incremental Revenue", f"£{revenue:,.2f}")
                st.metric("Campaign Cost per Customer", f"£{cost}")
                st.metric("Lift", f"+{(treatment_rate - baseline)*100:.0f}pp")

        except Exception as e:
            st.error(f"API call failed: {str(e)}")



