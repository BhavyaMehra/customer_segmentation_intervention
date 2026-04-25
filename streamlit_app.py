import streamlit as st
import requests
import numpy as np

API_URL = "https://customer-segmentation-intervention.onrender.com/predict"

def simulate_roi(lift_mean, monetary, cost, n_sims=500):
    """
    Simulate lift over baseline but on smaller simulations(500) for realistic approach than flat uplift.
    """
    results = []
    for _ in range(n_sims):
        sampled_lift = max(0, np.random.normal(lift_mean, 0.02))
        incremental_revenue = sampled_lift * monetary
        roi = ((incremental_revenue - cost) / cost * 100)
        results.append(roi)

    return np.array(results)  


st.set_page_config(
    page_title='Customer Segmentation and Intervention',
    layout='wide'
)

# Header
st.title("Customer Segmentation and Intervention Recommender")
st.markdown("Enter how recently a customer bought, how often they buy, and how much they spend. We will tell you which customer group they belong to and what marketing action is most likely to bring them back.")

# Main two columns
left_col, right_col = st.columns([4, 6])

with left_col:
    # Input sliders
    st.subheader("Customer RFM Input")

    col1, col2, col3 = st.columns(3)

    with col1:
        recency = st.number_input("Recency (days since last purchase)", min_value=0, max_value=373, value=50)
        
    with col2:
        frequency = st.number_input("Frequency (number of invoices)", min_value=1, max_value=210, value=10)

    with col3:
        currency = st.selectbox("Currency", ["GBP (£)", "INR (₹)"])
        if currency == "INR (₹)":
            monetary = st.number_input("Monetary (total spend ₹)", min_value=0, max_value=30000000, value=53000, step=1000)
            monetary_gbp = monetary / 106
        else:
            monetary = st.number_input("Monetary (total spend £)", min_value=0, max_value=300000, value=500, step=10)
            monetary_gbp = monetary


    st.caption("INR to GBP conversion uses approximate rate of ₹106 = £1")
    st.caption('Recency capped at 373 days, maximum the model saw during training.')


    run_sim = st.checkbox('Show best and worst case ROI scenarios for this campaign')

    predict_clicked = st.button('Predict Segment', type='primary')

    st.subheader('How to interpret results')
    st.markdown("""
                - **Customer Segment** tells you which customer group this person belongs to based on their purchase history.
                - **Recommended Treatment** is the marketing action most likely to drive a repeated purchase.
                - **Converstion Impact** shows how many extra customers respond when you run the campaign versus doing nothing.
                - **Financial Impact** estimates the addtional revenue the campaign generates for this specific customer's spend level.
                """)
    st.divider()

with right_col:

    # Predict button and response
    if predict_clicked:
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

                st.subheader("Prediction Result")
                segment_colors = {
                    "Champions": "#2ecc71",
                    "Promising": "#3498db",
                    "At-Risk": "#e67e22",
                    "Lost": "#e74c3c"
                }
                color = segment_colors.get(segment, "#ffffff")

                st.markdown(f"""
                    <div style='border-left: 5px solid {color}; 
                                padding: 16px; 
                                background-color: #161B22; 
                                border-radius: 6px;
                                margin-bottom: 16px;'>
                        <h3 style='color: {color}; margin: 0 0 8px 0;'>Customer Segment: {segment}</h3>
                        <p style='margin: 0; font-size: 16px;'><strong>Recommended Treatment:</strong> {treatment}</p>
                    </div>
                """, unsafe_allow_html=True)

                lift = treatment_rate - baseline
                incremental_conversions = round(lift * 100)
                customer_incremental_revenue = lift * monetary if currency == "GBP (£)" else lift * monetary_gbp * 106
                roi = ((customer_incremental_revenue - cost_display) / cost_display * 100)

                col1, col2 = st.columns(2)
                with col1:
                    with st.container(border=True):
                        st.markdown("**Conversion Impact**")
                        st.markdown(f"**Without intervention**: **{int(baseline*100)} in 100** customers convert")
                        st.markdown(f"**With treatment**: **{int(treatment_rate*100)} in 100** customers convert")
                        st.markdown(f"**Additional conversions**: **{round(lift*100)} per 100** customers contacted")

                with col2:
                    with st.container(border=True):
                        st.markdown("**Financial Impact**")
                        st.metric("Expected Incremental Revenue", f"{currency_symbol}{customer_incremental_revenue:,.2f}")
                        st.metric("Estimated Campaign Cost Per Customer", f"{currency_symbol}{cost_display}")
                        st.metric("Expected ROI (mean estimate)", f"{roi:,.0f}%")

                if run_sim:
                    avg_order_value = result['avg_order_value']
                    sim_results = simulate_roi(lift, avg_order_value, cost)
                    p5 = np.percentile(sim_results, 5)
                    p95 = np.percentile(sim_results, 95)
                    prob_positive = (sim_results > 0).mean() * 100

                    st.divider()
                    st.subheader('Campaign ROI: Best and Worst Case')

                    col1, col2, col3 = st.columns(3)
                    col1.metric("Worst Case ROI (5% chance of falling below)", f"{p5:.0f}%")
                    col2.metric("Best Case ROI (95% chance of staying below)", f"{p95:.0f}%")
                    col3.metric("Likelihood of Positive ROI", f"{prob_positive:.1f}%")

                    st.caption("Scenarios estimated by varying the expected response rate across 500 Monte Carlo simulations.")

                st.caption("Per campaign cycle, typically 30 to 90 days. Based on customer's actual spend value.")
            except Exception as e:
                st.error(f"API call failed: {str(e)}")



