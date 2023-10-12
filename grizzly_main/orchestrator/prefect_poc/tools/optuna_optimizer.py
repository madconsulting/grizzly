import logging
from datetime import datetime
from typing import Any, Optional

import mlflow
import optuna
import pandas as pd

from grizzly_main.orchestrator.prefect_poc.tools.custom_logger import redirect_logger_to_root_logger
from grizzly_main.orchestrator.prefect_poc.tools.mlflow_tools import log_and_create_model_version_in_mlflow
from grizzly_main.orchestrator.prefect_poc.tools.models.abstract_model import BaseModel
from grizzly_main.path_interations import get_base_dir

optuna_vis_dict = {
    "optimization_story": optuna.visualization.plot_optimization_history,
    "parallel_coordinate": optuna.visualization.plot_parallel_coordinate,
    "contour": optuna.visualization.plot_contour,
    "slice": optuna.visualization.plot_slice,
    "param_importances": optuna.visualization.plot_param_importances,
    "edf": optuna.visualization.plot_edf,
}


class OptunaOptimizer:
    """
    Optuna hyperparameter tuning optimization functionality
    """

    def __init__(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        model: type[BaseModel],
        param_dict: dict[str, Any],
        direction: str,
        study_name: Optional[str] = None,
        storage: Optional[str] = None,
        is_run_in_prefect: bool = False,
        model_verbose: int = -1,
        cv_nfold: int = 5,
    ):
        """
        Initialize OptunaOptimizer class

        :param X: Feature DataFrame
        :param y: Target Series
        :param model: Model
        :param param_dict: Parameter dictionary
        :param direction: Direction of optimization ('minimize' or 'maximize')
        :param study_name: Optuna study name
        :param storage: Storage for the Optuna study
        :param is_run_in_prefect: True if running in a Prefect pipeline, False otherwise
        :param model_verbose: Model verbosity level
        :param cv_nfold: Number of folds in Cross Validation
        """
        self.is_run_in_prefect = is_run_in_prefect
        if self.is_run_in_prefect:
            redirect_logger_to_root_logger(
                logger_name="optuna",
                is_enable_in_prefect=True,
            )
        self.X = X
        self.y = y
        self.model = model
        self.model_verbose = model_verbose
        if study_name:
            self.study_name = study_name
        else:
            self.study_name = f"example_optuna_lightgbm_{datetime.utcnow().strftime('%Y%m%d%H%M%S_%f')}"
        # Specifying sample with a fixed random seed to make the Optuna result parameters reproducible across runs
        # (when running trials sequentially, reproducibility is not guaranteed in distributed computing mode)
        sampler = optuna.samplers.TPESampler(seed=42)
        self.study = optuna.create_study(
            study_name=self.study_name,
            direction=direction,
            storage=storage,
            sampler=sampler,
        )
        logging.info(f"Optuna study {self.study_name} created")
        (
            self.static_params,
            self.dynamic_params,
        ) = self._divide_into_static_and_dynamic_params(param_dict=param_dict)
        self.cv_nfold = cv_nfold

    @staticmethod
    def _divide_into_static_and_dynamic_params(param_dict: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        """
        Divide the parameter dictionary into static and dynamic parameters. The latter are the hyperparameters to be
        tuned, whose value is chosen in every Optuna trial.

        :param param_dict: Parameter dictionary
        :return: Static and dynamic parameter dictionaries
        """
        static_params = {}
        dynamic_params = {}
        for param, param_val in param_dict.items():
            if isinstance(param_val, dict):
                if "is_hyperparam" in param_val.keys():
                    dynamic_params.update(
                        {
                            param: {
                                "type": param_val["type"],
                                "values": param_val["values"],
                            }
                        }
                    )
            if param not in dynamic_params:
                static_params.update({param: param_val})
        return static_params, dynamic_params

    def _get_dynamic_params_trial_val(
        self,
        trial: optuna.Trial,
    ) -> dict[str, Any]:
        """
        Get dynamic hyperparameter values for a given Trial

        :param trial: Optuna trial
        :return: Dictionary with the dynamic hyperparameter values for the Optuna trial
        """
        dynamic_param_vals = {}
        for param, param_val_dict in self.dynamic_params.items():
            if param_val_dict["type"] == "float":
                dynamic_param_vals[param] = trial.suggest_float(param, **param_val_dict["values"])
            elif param_val_dict["type"] == "categorical":
                # Note: In Optuna we need to use suggest_categorical in order to pick amongst a list of possible values,
                # even though these values might not necessarily be strings.
                # In optuna/distributions.py, there is a list of possible dtypes:
                # CategoricalChoiceType = Union[None, bool, int, float, str]
                dynamic_param_vals[param] = trial.suggest_categorical(param, param_val_dict["values"])
            elif param_val_dict["type"] == "int":
                dynamic_param_vals[param] = trial.suggest_int(param, **param_val_dict["values"])
            else:
                raise NotImplementedError(f"The hyperparameter type: {param_val_dict['type']} not implemented yet")
        return dynamic_param_vals

    def objective(self, trial: optuna.Trial) -> Any:
        """
        Generic objective function for any BaseModel, where we are training with cross validation

        :param trial: Optuna Trial
        :return: Objective value, which is the cross validation metric
        """
        dynamic_param_vals = self._get_dynamic_params_trial_val(trial=trial)
        instantiated_model = self.model(
            params={**self.static_params, **dynamic_param_vals},
            verbose=self.model_verbose,
        )
        metrics_res = instantiated_model.train_with_cv(X=self.X, y=self.y, nfold=self.cv_nfold)
        if len(instantiated_model.metric_list) > 1:  # type: ignore
            # https://optuna.readthedocs.io/en/stable/tutorial/20_recipes/002_multi_objective.html to extend to
            # multiple metrics to be optimized
            raise NotImplementedError("Multi-objective in Optuna for multiple model metrics not implemented yet")
        return metrics_res[instantiated_model.metric_list[0]]  # type: ignore

    def optimize(self, n_trials: int) -> None:
        """
        Run the optimization process for the study

        :param n_trials: Number of trials to be performed
        :return: None
        """
        self.study.optimize(self.objective, n_trials=n_trials)

    def train_best_model(
        self,
        is_store_model: bool = False,
        enable_mlflow_tracking: bool = False,
        model_tags: Optional[dict[str, str]] = None,
    ) -> BaseModel:
        """
        Train a model with the best parameters from the Optuna study

        :param is_store_model: True if storing the model, False otherwise
        :param enable_mlflow_tracking: True if saving plots to MLflow is enabled, False otherwise
        :param model_tags: Model tags to associate with the model version
        :return: Trained model (BaseModel class)
        """
        best_dynamic_params = self.study.best_params
        logging.info(f"Best parameters: {best_dynamic_params}")

        best_model = self.model(
            params={**self.static_params, **best_dynamic_params},
            verbose=self.model_verbose,
        )
        best_model.train(X_train=self.X, y_train=self.y)
        if is_store_model:
            log_and_create_model_version_in_mlflow(
                model=best_model.model,
                model_name="adventure_works_model",
                local_file_path="adventure_works_model.joblib",
                model_directory="best_trained_model",
                model_tags=model_tags,
                include_poetry_files=True,
                enable_mlflow_tracking=enable_mlflow_tracking,
            )
        return best_model

    @staticmethod
    def _save_optuna_figure(
        fig: Any,
        figure_path: str,
        enable_mlflow_tracking: bool = False,
        mlflow_artifact_path: Optional[str] = None,
    ) -> None:
        """
        Save an Optuna figure as an image.

        :param fig: Optuna figure object to save.
        :param figure_path: Path to save the figure image.
        :param enable_mlflow_tracking: True if MLflow tracking is enabled, False otherwise.
        :param mlflow_artifact_path: Path within MLflow artifacts to store the figure.
        :return: None
        """
        fig.write_image(figure_path)
        if enable_mlflow_tracking:
            if mlflow_artifact_path is None:
                raise ValueError("mlflow_artifact_path must be defined when MLflow tracking is enabled.")
            mlflow.log_artifact(figure_path, artifact_path=mlflow_artifact_path)

    def generate_optuna_plots(
        self,
        plot_names: Optional[list[str]] = None,
        plot_arguments: Optional[dict[str, dict[str, Any]]] = None,
        enable_mlflow_tracking: bool = False,
        mlflow_artifact_path: Optional[str] = None,
        figure_name_prefix: str = "",
        target_name: Optional[str] = None,
    ) -> None:
        """
        Generate plots using the Optuna library and save them.

        :param plot_names: List of plot names to generate using the Optuna library. If None, using all the available
                           ones in the optuna_vis_dict
        :param plot_arguments: Dictionary of plot names to their corresponding arguments.
        :param enable_mlflow_tracking: True if saving plots to MLflow is enabled, False otherwise.
        :param mlflow_artifact_path: Path within MLflow artifacts to store the generated plots.
        :param figure_name_prefix: Prefix for the generated figure names.
        :param target_name: Name of the target for which the plots are generated.
        :return: None
        """
        base_dir = get_base_dir()
        if plot_arguments is None:
            plot_arguments = {}
        for plot_name, plot_function in optuna_vis_dict.items():
            if plot_names is None or plot_name in plot_names:
                plot_args = plot_arguments.get(plot_name, {})
                try:
                    fig = plot_function(
                        self.study,
                        target_name=target_name,
                        **plot_args,
                    )
                    figure_filename = f"{base_dir}/{figure_name_prefix}_optuna_{plot_name}.png"
                    self._save_optuna_figure(
                        fig=fig,
                        figure_path=figure_filename,
                        enable_mlflow_tracking=enable_mlflow_tracking,
                        mlflow_artifact_path=mlflow_artifact_path,
                    )
                except RuntimeError as e:
                    logging.warning(f"Failed to generate plot '{plot_name}' for target '{target_name}': {e}")
            logging.info(f"Optuna plot {plot_name} generated")


if __name__ in "__main__":
    from sklearn.datasets import load_iris
    from sklearn.model_selection import train_test_split

    # pylint: disable=C0412
    from grizzly_main.orchestrator.prefect_poc.tools.custom_logger import add_stdout_logger_as_root
    from grizzly_main.orchestrator.prefect_poc.tools.models.lightgbm_model import LightGBMModel

    add_stdout_logger_as_root()

    # Load the Iris dataset
    data = load_iris()
    X_ = pd.DataFrame(data.data, columns=data.feature_names)
    y_ = pd.Series(data.target, name="target")

    # Split the dataset into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X_, y_, test_size=0.2, random_state=42)

    # Define LightGBM params
    # https://lightgbm.readthedocs.io/en/latest/Parameters.html
    # https://lightgbm.readthedocs.io/en/latest/Parameters-Tuning.html
    params = {
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
        # Iris has very small dataset - using lower values than by default (at risk of overfitting)
        "min_data_in_leaf": {
            "is_hyperparam": True,
            "name": "min_data_in_leaf",
            "type": "int",
            "values": {"low": 10, "high": 20, "step": 5},
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
    }

    # Hyperparameter tuning
    optimizer = OptunaOptimizer(
        X=X_train,
        y=y_train,
        model=LightGBMModel,
        direction="minimize",
        param_dict=params,
    )
    optimizer.optimize(n_trials=100)

    # Optuna results visualization
    optimizer.generate_optuna_plots(figure_name_prefix="iris_")

    # Train the best model
    best_model_ = optimizer.train_best_model()
