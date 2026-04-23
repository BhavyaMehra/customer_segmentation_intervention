import pandas as pd

def run_simulation(rfm, intervention):
    """
    Takes labeled RFM df and intervention parameters dict.
    Return a df with incremental revenue and ROI per segment

    Parameters:
    rfm: df with Segment column
    intervention: dict of segment intervention parameters

    Returns:
    results_df: simulation results dataframe
    """

    results = []

    for segment, params in intervention.items():
        n_customers = len(rfm[rfm['Segment'] == segment])

        baseline_conversions = n_customers * params['baseline_rate']
        treatment_conversions = n_customers * (params['baseline_rate'] + params['lift_rate'])
        incremental_conversions = treatment_conversions - baseline_conversions

        baseline_revenue = baseline_conversions * params['avg_order_value']
        treatment_revenue = treatment_conversions * params['avg_order_value']
        incremental_revenue = treatment_revenue - baseline_revenue

        campaign_cost = n_customers * params['cost_per_customer']
        net_roi = (((incremental_revenue - campaign_cost) / campaign_cost) * 100).round(2)

        results.append({
            'Segment': segment,
            'Treatment': params['treatment'],
            'Customers': n_customers,
            'Baseline Conv %': params['baseline_rate'] * 100,
            'Treatment Conv %': (params['baseline_rate'] + params['ilft_rate']) * 100,
            'Incremental Conversions': round(incremental_conversions, 2),
            'Incremental Revenue': round(incremental_revenue, 2),
            'Campaign Cost': round(campaign_cost, 2),
            'Net ROI %': round(net_roi, 2)

        })

        return pd.DataFrame(results)