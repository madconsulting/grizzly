main_config = {
    "enable_mlflow_tracking": True,
    "dfs_kwargs": {
        "max_depth": 2,
        "max_features": 100,
    },
    "model_type": "lightgbm",
    "hyperparameter_tuning": {
        "n_trials": 100,
        # "is_run_trials_concurrently": False,
        # "concurrency_limit": None,
        "is_run_trials_concurrently": True,
        "concurrency_limit": 5,
        "param_dict": {
            # Static parameters
            "objective": "multiclass",  # Multi-class classification
            "num_class": 3,  # Number of classes in the target variable
            "metric": "multi_logloss",  # Log loss as the evaluation metric
            "n_jobs": -1,  # Use all available cores for parallelism
            "bagging_freq": 1,  # Bagging is performed at every iteration in the training process (prevent overfitting)
            # Hyperparameters (identified by is_hyperparam=True flag)
            # Limiting number of iterations to a relatively low number to prevent overfiting
            # and for faster training. Most likely a value close to the upper limit will be selected for better
            # accuracy, and we could even get higher accuracies if we increased that value (but at risk of
            # overfiting).
            "n_estimators": {
                "is_hyperparam": True,
                "name": "n_estimators",
                "type": "int",
                "values": {"low": 20, "high": 150},
            },
            "learning_rate": {
                "is_hyperparam": True,
                "name": "learning_rate",
                "type": "float",
                "values": {"low": 0.01, "high": 0.2},
            },
            # # IMPORTANT NOTE:
            # # Try to meet the following condition to prevent overfiting in optuna:
            # # num_leaves < 2 ^ max_depth
            "num_leaves": {
                "is_hyperparam": True,
                "name": "num_leaves",
                "type": "int",
                "values": {"low": 20, "high": 50, "step": 10},
            },
            "max_depth": {
                "is_hyperparam": True,
                "name": "max_depth",
                "type": "int",
                "values": {"low": 6, "high": 12},
            },
            "min_data_in_leaf": {
                "is_hyperparam": True,
                "name": "min_data_in_leaf",
                "type": "int",
                "values": {"low": 20, "high": 50, "step": 5},
            },
            "max_bin": {
                "is_hyperparam": True,
                "name": "max_bin",
                "type": "int",
                "values": {"low": 200, "high": 300},
            },
            "lambda_l1": {
                "is_hyperparam": True,
                "name": "lambda_l1",
                "type": "int",
                "values": {"low": 0, "high": 10},
            },
            "lambda_l2": {
                "is_hyperparam": True,
                "name": "lambda_l2",
                "type": "int",
                "values": {"low": 0, "high": 10},
            },
            "min_gain_to_split": {
                "is_hyperparam": True,
                "name": "min_gain_to_split",
                "type": "float",
                "values": {"low": 0, "high": 15},
            },
            "bagging_fraction": {
                "is_hyperparam": True,
                "name": "bagging_fraction",
                "type": "float",
                "values": {"low": 0.2, "high": 0.95, "step": 0.05},
            },
            "feature_fraction": {
                "is_hyperparam": True,
                "name": "feature_fraction",
                "type": "float",
                "values": {"low": 0.2, "high": 0.95, "step": 0.05},
            },
        },
    },
    "is_use_fastrree_shap": False,
    "eval_metrics": {
        "accuracy": {},
        "roc_auc": {},
        "f1_score": {},
        "precision": {},
        "recall": {},
        "confusion_matrix": {"normalize": "all"},
    },
}
