import json
import os
from datetime import datetime
from typing import Any

from fdq.ui_functions import iprint, wprint, getIntInput


def get_nb_exp_epochs(path: str) -> int:
    """Returns the number of epochs of the experiment stored at 'path'."""
    path = os.path.join(path, "history.json")

    try:
        with open(path, encoding="utf8") as f:
            data = json.load(f)
        return len(data["train"])
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return 0


def find_experiment_result_dirs(experiment: Any) -> tuple[str, list[str]]:
    """Finds and returns the experiment result directory and its subfolders for the given experiment."""
    if experiment.is_slurm and experiment.inargs.train_model:
        wprint("WARNING: This is a slurm TRAINING session - looking only for results in scratch_results_path!")
        outbasepath: str | None = experiment.exp_def.get("slurm_cluster", {}).get("scratch_results_path")

    elif experiment.is_slurm and not experiment.mode.op_mode.train:
        wprint("WARNING: This is a slurm INFERENCE session - looking for results in regular path!")
        outbasepath = experiment.exp_def.get("store", {}).get("results_path")

        if outbasepath[0] == "~":
            outbasepath = os.path.expanduser(outbasepath)

        elif outbasepath[0] != "/":
            raise ValueError("Error: The results path needs to be an absolute path!")

    else:
        # regular local use
        outbasepath = experiment.exp_def.get("store", {}).get("results_path")
        outbasepath = os.path.expanduser(outbasepath)

    if outbasepath is None:
        raise ValueError("Error: No store path specified in experiment file.")

    experiment_res_path: str = os.path.join(outbasepath, experiment.project, experiment.experimentName)
    subfolders: list[str] = [f.path.split("/")[-1] for f in os.scandir(experiment_res_path) if f.is_dir()]

    return experiment_res_path, subfolders


def manual_experiment_selection(subfolders_dict: dict[str, str], res_root_path: str) -> str:
    """UI to manually select experiment ."""
    subfolders_datetime = [datetime.strptime(s, "%Y%m%d_%H_%M_%S") for s in subfolders_dict.keys()]
    subfolders_datetime.sort()
    sorted_keys = [s.strftime("%Y%m%d_%H_%M_%S") for s in subfolders_datetime]

    print("\nSelect experiment:")
    for i, d in enumerate(sorted_keys):
        if subfolders_dict[d] == "":
            # old naming scheme, without funkyBob
            nb_epochs = get_nb_exp_epochs(os.path.join(res_root_path, d))
        else:
            nb_epochs = get_nb_exp_epochs(os.path.join(res_root_path, d + "__" + subfolders_dict[d]))
        print(f"{i:<3}: {d:<20} {subfolders_dict[d]:<25} {nb_epochs} epochs {'(!)' if nb_epochs == 0 else ''}")
    exp_idx: int = getIntInput("Enter index: ", [0, len(subfolders_datetime) - 1])
    return sorted_keys[exp_idx]


def find_model_path(experiment: Any) -> tuple[str, str]:
    """Returns the path to the model file of a previous experiment."""
    experiment_res_path, subfolders = find_experiment_result_dirs(experiment)

    subfolders_date_str: list[str] = []
    subfolders_dict: dict[str, str] = {}
    for s in subfolders:
        datestr = s.split("__")[0]
        subfolders_date_str.append(datestr)
        if len(s.split("__")) > 1:
            subfolders_dict[datestr] = s.replace(datestr + "__", "")
        else:
            subfolders_dict[datestr] = ""

    if (
        experiment.mode.test_mode.custom_last
        or experiment.mode.test_mode.custom_best_val
        or experiment.mode.test_mode.custom_best_train
    ):
        selected_exp_date_str = manual_experiment_selection(subfolders_dict, experiment_res_path)
    else:
        selected_exp_date_str = sorted(subfolders_date_str)[-1]

    res = [i for i in subfolders if selected_exp_date_str in i]
    if not len(res) == 1:
        raise ValueError(f"No corresponding result folder was found in '{experiment_res_path}'. Specify path manually!")

    if experiment.mode.test_mode.custom_last or experiment.mode.test_mode.last:
        search_string = "last_"
    elif experiment.mode.test_mode.custom_best_train or experiment.mode.test_mode.best_train:
        search_string = "best_train_"
    else:
        search_string = "best_val_"

    possible_files: list[str] = []
    for fn in os.listdir(os.path.join(experiment_res_path, res[0])):
        if search_string in fn and fn.endswith(".fdqm"):
            possible_files.append(fn)

    if len(possible_files) == 0:
        raise ValueError(f"No corresponding model file was found in '{experiment_res_path}'. Specify path manually!")

    if len(possible_files) > 1:
        wprint(f"Multiple corresponding models files were found in '{experiment_res_path}':")
        wprint(possible_files)
        wprint(f"Selecting automatically the first one for testing: '{possible_files[0]}'")

    return os.path.join(experiment_res_path, res[0]), possible_files[0]


def save_test_results(test_results: Any, experiment: Any) -> None:
    """Save the test results of an experiment to a JSON file."""
    if test_results is not None:
        now: datetime = datetime.now()
        dt_string: str = now.strftime("%Y%m%d_%H_%M")

        results_fp: str = os.path.join(experiment.test_dir, f"00_test_results_{dt_string}.json")

        with open(results_fp, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "experiment_name": experiment.experimentName,
                    "test results": test_results,
                },
                f,
                ensure_ascii=False,
                indent=4,
            )


def save_test_info(experiment: Any, model_path: Any | None = None, weights: Any | None = None) -> None:
    """Save test configuration information to a JSON file."""
    now: datetime = datetime.now()
    dt_string: str = now.strftime("%Y%m%d_%H_%M")
    results_fp: str = os.path.join(experiment.test_dir, f"test_config_{dt_string}.json")

    with open(results_fp, "w", encoding="utf-8") as f:
        json.dump(
            {"model": model_path, "weights": weights},
            f,
            ensure_ascii=False,
            indent=4,
        )


def ui_ask_test_mode(experiment: Any) -> None:
    """UI to select test mode."""
    exp_mode: int = getIntInput("\nExperiment Selection:\n1: Last, 2: From List, 3: Path to model\n", [1, 3])
    model_mode: int = 1  # Default value
    if exp_mode in [1, 2]:
        model_mode = getIntInput(
            "\nModel Selection:\n1: Last Model, 2: Best Model (val loss), 3: Best Model (train loss)\n",
            [1, 3],
        )
        if exp_mode == 1:
            if model_mode == 1:
                experiment.mode.last()
            elif model_mode == 2:
                experiment.mode.best_val()
            else:
                experiment.mode.best_train()
        elif exp_mode == 2:
            if model_mode == 1:
                experiment.mode.custom_last()
            elif model_mode == 2:
                experiment.mode.custom_best_val()
            else:
                experiment.mode.custom_best_train()
    else:
        if model_mode == 1:
            experiment.mode.custom_path()


def _set_test_mode(experiment: Any) -> None:
    experiment.mode.test()

    if experiment.mode.op_mode.unittest:
        experiment.mode.last()

    elif experiment.inargs.test_model_auto:
        if experiment.exp_def.test.test_model == "best_val":
            iprint("Auto test: Loading best validation model.")
            experiment.mode.best_val()
        elif experiment.exp_def.test.test_model == "best_train":
            iprint("Auto test: Loading best train model.")
            experiment.mode.best_train()
        else:
            iprint("Auto test: Loading last trained model.")
            experiment.mode.last()

    else:
        ui_ask_test_mode(experiment)


def run_test(experiment: Any) -> None:
    """Runs the test procedure for the given experiment."""
    iprint("-----------------------------------------------------------")
    iprint("Starting Test...")
    iprint("-----------------------------------------------------------")

    if experiment.is_distributed():
        raise ValueError("ERROR: Cannot run test in distributed mode! Please run in single process mode.")

    experiment.file_store_cnt = 0

    _set_test_mode(experiment)

    if experiment.exp_def.models is not None:
        experiment.load_trained_models()

    experiment.copy_files_to_test_dir(experiment.experiment_file_path)
    for p in experiment.exp_def.globals.parent_hierarchy:
        experiment.copy_files_to_test_dir(file_path=p)

    save_test_info(
        experiment,
        model_path=experiment.trained_model_paths,
    )
    experiment.setupData()
    experiment.createLosses()
    test_results = experiment.runEvaluator()
    save_test_results(test_results, experiment)
