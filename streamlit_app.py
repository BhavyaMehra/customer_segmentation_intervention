import streamlit as st
import requests

API_URL = "https://customer-segmentation-intervention.onrender.com/predict"

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
    recency = st.number_input("Recency (days since last purchase)", min_value=0, max_value=750, value=50)

with col2:
    frequency = st.number_input("Frequency (number of invoices)", min_value=1, max_value=210, value=10)

with col3:
    currency = st.selectbox("Currency", ["GBP (£)", "INR (₹)"])
    if currency == "INR (₹)":
        monetary = st.number_input("Monetary (total spend ₹)", min_value=0.0, max_value=30000000.0, value=53000.0)
        monetary_gbp = monetary / 106
    else:
        monetary = st.number_input("Monetary (total spend £)", min_value=0.0, max_value=300000.0, value=500.0)
        monetary_gbp = monetary

st.caption("INR to GBP conversion uses approximate rate of ₹106 = £1")

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
                    "monetary": monetary_gbp
                },
                timeout=60
            )

            result = response.json()

            segment = result["segment"]
            treatment = result["treatment"]
            baseline = result["baseline_conv_rate"]
            treatment_rate = result["treatment_conv_rate"]
            revenue = result["expected_incremental_revenue"]
            cost = result["campaign_cost_per_customer"]

            rate = 106

            if currency == "INR (₹)":
                revenue_display = revenue * rate
                cost_display = cost * rate
                currency_symbol = "₹"
            else:
                revenue_display = revenue
                cost_display = cost
                currency_symbol = "£"
            

            segment_colors = {
                "Champions": "🟢",
                "Promising": "🔵",
                "At-Risk": "🟠",
                "Lost": "🔴"
            }

            st.subheader("Prediction Result")
            st.markdown(f"## {segment_colors.get(segment, '')} {segment}")
            
            st.info(f"Recommended Treatment: **{treatment}**")

            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Baseline Conversion Rate", f"{baseline*100:.0f}%")
                st.metric("Treatment Conversion Rate", f"{treatment_rate*100:.0f}%")

            with col2:
                st.metric("Expected Incremental Revenue", f"{currency_symbol}{revenue_display:,.2f}")
                st.metric("Campaign Cost per Customer", f"{currency_symbol}{cost_display}")
                st.metric("Lift", f"+{(treatment_rate - baseline)*100:.0f}pp")

        except Exception as e:
            st.error(f"API call failed: {str(e)}")



