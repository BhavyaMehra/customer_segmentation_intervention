# src/config.py

# Snapshot date for RFM calculation
SNAPSHOT_DATE = "2011-12-10"

# KMeans parameters
KMEANS_K = 4
KMEANS_RANDOM_STATE = 42
KMEANS_N_INIT = 10


# PyTorch model architecture
MODEL_CONFIG = {
    "input_dim": 3,
    "hidden_dim1": 32,
    "hidden_dim2": 16,
    "output_dim": 4,
    "dropout1": 0.4,
    "dropout2": 0.3,
    "learning_rate": 0.0005,
    "batch_size": 32,
    "epochs": 100,
    "patience": 10,
    "random_seed": 42
}

# Intervention parameters
INTERVENTIONS = {
    "Champions": {
        "treatment": "Loyalty Program Upsell",
        "baseline_rate": 0.25,                  # Probability a customer converts with no intervention (From study)
        "lift_rate": 0.10,                          # Additional conversion probability the treatment adds on top of baseline (From study)
        "avg_order_value": 8086,                    # Derived from our own clustering in notebook 03 (From our analysis)
        "cost_per_customer": 15                     # Cost of delivering the intervention (From study)
    },
    "Promising": {
        "treatment": "Cross-sell Campaign",
        "baseline_rate": 0.10,
        "lift_rate": 0.08,
        "avg_order_value": 548,
        "cost_per_customer": 8
    },
    "At-Risk": {
        "treatment": "Reactivation Discount Voucher",
        "baseline_rate": 0.05,
        "lift_rate": 0.12,
        "avg_order_value": 1801,
        "cost_per_customer": 10
    },
    "Lost": {
        "treatment": "Win-back Deep Discount",
        "baseline_rate": 0.02,
        "lift_rate": 0.05,
        "avg_order_value": 342,
        "cost_per_customer": 5
    }
}

# Monte Carlo simulation parameters
MONTE_CARLO_SIMULATIONS = 10000
LIFT_STD_DEV = 0.03

# Budget constraint
TOTAL_BUDGET = 25000