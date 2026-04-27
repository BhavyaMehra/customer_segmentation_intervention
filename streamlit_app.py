import streamlit as st
import requests
import numpy as np

API_URL = "https://customer-segmentation-intervention.onrender.com/predict"

def simulate_roi(lift_mean, monetary, cost, n_sims=1000, seed=42):
    """
    Simulate lift over baseline but on smaller simulations(1000) for realistic approach than flat uplift.
    """
    np.random.seed(seed)
    samples = np.random.normal(lift_mean, 0.02, n_sims)
    samples = np.maximum(0, samples) # clip negative

    incremental_revenue = samples * monetary
    roi = ((incremental_revenue - cost) / cost * 100)

    return roi 


@st.cache_data(ttl=300) # cache for 5min
def call_api(recency, frequency, monetary_gbp):
    response = requests.post(
                    API_URL,
                    json={
                        "recency": recency,
                        "frequency": frequency,
                        "monetary": monetary_gbp
                    },
                    timeout=10
                )
    return response.json() 


st.set_page_config(
    page_title='Customer Segmentation and Intervention',
    layout='wide'
)

# Header
st.title("Customer Segmentation and Intervention Recommender", text_alignment='center')
st.markdown("Enter how recently a customer bought, how often they buy, and how much they spend. We will tell you which customer group they belong to and what marketing action is best suited for them.", text_alignment='center')

# Main two columns
left_col, right_col = st.columns(2)

with left_col:
    # Input sliders
    st.subheader("Customer Recency, Frequency, Monetary (RFM) Input")

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


    st.markdown(f"<p style='font-size: 16px; color: #aaaaaa;'>INR to GBP conversion uses approximate rate of ₹106 = £1</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 16px; color: #aaaaaa;'>Recency capped at 373 days, maximum the model saw during training.</p>", unsafe_allow_html=True)


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
                result = call_api(recency, frequency, monetary_gbp)

                segment = result["segment"]
                treatment = result["treatment"]
                baseline = result["baseline_conv_rate"]
                treatment_rate = result["treatment_conv_rate"]
                revenue = result["expected_incremental_revenue"]
                cost = result["campaign_cost_per_customer"]
                avg_order_value = result['avg_order_value']

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
                customer_incremental_revenue = (lift * avg_order_value if currency == "GBP (£)" else lift * monetary_gbp * 106)
                roi = ((customer_incremental_revenue - cost_display) / cost_display * 100)
                extra_converters = round(lift * 100)

                st.markdown(f"Without any campaign, roughly **{int(baseline*100)} in 100** customers like this make a repeat purchase. The **{treatment}** is expected to bring in **{extra_converters} additional customers per 100 contacted**, each spending approximately **{currency_symbol}{int(avg_order_value):,}** on average.")

                
                with st.container(border=True):
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Incremental Revenue (per 100 customers)", f"{currency_symbol}{customer_incremental_revenue * 100:,.0f}")
                    m2.metric("Campaign Cost (per 100 customers)", f"{currency_symbol}{cost_display * 100:.0f}")
                    m3.metric("Expected Incremental ROI", f"{roi:,.0f}%")
                    st.markdown(f"<p style='font-size: 16px; color: #aaaaaa;'>Estimated returns if this intervention is run across 100 similar customers.</p", unsafe_allow_html=True)

                if run_sim:
                    sim_results = simulate_roi(lift, avg_order_value, cost)
                    p5 = np.percentile(sim_results, 5)
                    p95 = np.percentile(sim_results, 95)
                    prob_positive = (sim_results > 0).mean() * 100

                    st.divider()
                    st.subheader('Campaign ROI: Best and Worst Case')

                    col1, col2, col3 = st.columns(3)
                    col1.metric("Worst Case ROI", f"{p5:.0f}%")
                    col2.metric("Most likely ROI range upto", f"{p95:.0f}%")
                    col3.metric("Likelihood of Positive ROI", f"{prob_positive:.1f}%")

                    st.markdown(f"<p style='font-size: 16px; color: #aaaaaa;'>In 90% of simulated scenarios, ROI falls between {p5:.0f}% and {p95:.0f}%. Worst case assumes lower than expected customer response.</p>", unsafe_allow_html=True)
                    st.markdown(f"<p style='font-size: 16px; color: #aaaaaa;'>Scenarios estimated by varying the expected response rate across 500 Monte Carlo simulations.</p>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"API call failed: {str(e)}")

st.markdown("For full source code, visit [GitHub](https://github.com/BhavyaMehra/customer_segmentation_intervention).", text_alignment='center')



