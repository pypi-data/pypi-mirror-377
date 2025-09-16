import os
import sys
import math
import shutil
import argparse
import importlib
import subprocess
from datetime import datetime, timedelta
from typing import Any
import git

import torch
import funkybob
from torchview import draw_graph
from torch.nn.parallel import DistributedDataParallel as DDP
import wandb
from fdq.ui_functions import (
    iprint,
    eprint,
    wprint,
    show_train_progress,
    startProgBar,
    set_global_rank,
)
from fdq.testing import find_model_path
from fdq.transformers import get_transformers
from fdq.misc import (
    remove_file,
    store_processing_infos,
    FCQmode,
    DictToObj,
    save_train_history,
    save_tensorboard,
    save_wandb,
    load_conf_file,
)
from fdq.dataset_caching import cache_datasets_ddp_handler


class fdqExperiment:
    """This class defines the fdqExperiment.

    It manages the setup, training, evaluation, and management of machine learning experiments.
    """

    def __init__(self, inargs: argparse.Namespace, rank: int) -> None:
        """Initialize the fdqExperiment class with the provided arguments.

        Args:
            inargs (argparse.Namespace): The input arguments containing experiment configurations.
            rank (int): The rank of the current process in distributed training.
        """
        self.inargs: argparse.Namespace = inargs
        self.experiment_file_path = self.inargs.experimentfile
        self.exp_def = load_conf_file(self.experiment_file_path)
        self.globals = self.exp_def.globals
        self.project: str = self.exp_def.globals.project.replace(" ", "_")
        self.experimentName: str = self.experiment_file_path.split("/")[-1].split(".json")[0]
        self.funky_name: str | None = None
        self.checkpoint_frequency: int = self.exp_def.store.checkpoint_frequency
        self.mode: FCQmode = FCQmode()
        self.creation_time: datetime = datetime.now()
        self.current_ep_start_time: datetime | None = None
        self.finish_time: datetime | None = None
        self.total_run_time: timedelta | None = None
        self.run_info: dict[str, Any] = {}
        self.gradacc_iter: int = self.exp_def.train.args.get("accumulate_grad_batches", default=1)
        self.useAMP: bool = bool(self.exp_def.train.args.use_AMP)
        self.nb_epochs: int = self.exp_def.train.args.epochs
        self.current_epoch: int = 0
        self.start_epoch: int = 0
        self.data: dict[str, Any] = {}
        self.models: dict[str, torch.nn.Module] = {}
        self.models_no_ddp: dict[str, torch.nn.Module] = {}
        self.transformers: dict[str, Any] = {}
        self.scaler: torch.cuda.amp.GradScaler | None = None
        self.trainer: Any | None = None
        self.trained_model_paths: dict[str, str] = {}
        self.optimizers: dict[str, torch.optim.Optimizer | None] = {}
        self.lr_schedulers: dict[str, Any | None] = {}
        self.losses: dict[str, Any] = {}
        self.last_model_path: dict[str, str | None] = {}
        self.best_val_model_path: dict[str, str | None] = {}
        self.best_train_model_path: dict[str, str | None] = {}
        self.checkpoint_path: str | None = None
        self._results_dir: str | None = None
        self._results_output_dir: str | None = None
        self.file_store_cnt: int = 0
        self._test_dir: str | None = None
        self._valLoss: float = float("inf")
        self._trainLoss: float = float("inf")
        self.bestValLoss: float = float("inf")
        self.bestTrainLoss: float = float("inf")
        self.valLoss_per_ep: list[float] = []
        self.trainLoss_per_ep: list[float] = []
        self.new_best_train_loss: bool = False
        self.new_best_train_loss_ep_id: int | None = None
        self.new_best_val_loss: bool = False
        self.new_best_val_loss_ep_id: int | None = None
        self.early_stop_detected: bool = False
        self.early_stop_reason: str = ""
        self.processing_log_dict: dict[str, Any] = {}
        self.useTensorboard: bool = self.exp_def.store.use_tensorboard
        self.tb_writer: Any | None = None
        self.useWandb: bool = self.exp_def.store.use_wandb
        self.wandb_initialized: bool = False
        slurm_job_id: str | None = os.getenv("SLURM_JOB_ID")
        if isinstance(slurm_job_id, str) and slurm_job_id.isdigit():
            self.is_slurm: bool = True
            self.slurm_job_id: str = slurm_job_id
            self.scratch_data_path: str | None = self.exp_def.get("slurm_cluster", {}).get("scratch_data_path")
        else:
            self.is_slurm = False
            self.slurm_job_id = None
            self.scratch_data_path = None
        # distributed training
        set_global_rank(rank)
        self.rank: int = rank
        if not self.inargs.train_model:
            self.world_size = 1
        else:
            self.world_size: int = self.exp_def.get("slurm_cluster", {}).get("world_size", 1)
        self.master_port: int = self.exp_def.get("slurm_cluster", {}).get("master_port")
        self.ddp_rdvz_path: int = self.exp_def.get("slurm_cluster", {}).get("ddp_rdvz_path", "/scratch/")
        self.init_distributed_mode()

        self.previous_slurm_job_id: str | None = None
        if torch.cuda.is_available() and bool(self.exp_def.train.args.use_GPU):
            torch.cuda.empty_cache()
            self.device: torch.device = torch.device("cuda", self.rank)
            self.is_cuda: bool = True
            iprint(f"CUDA available: {torch.cuda.is_available()}. NB devices: {torch.cuda.device_count()}")
        else:
            wprint("NO CUDA available - CPU mode")
            self.device = torch.device("cpu")
            self.is_cuda = False
        self.prepare_transformers()
        self.store_experiment_git_hash()

    @property
    def results_dir(self) -> str:
        if not self.is_main_process():
            return None

        if self._results_dir is None:
            dt_string = self.creation_time.strftime("%Y%m%d_%H_%M_%S")
            if self.funky_name is None:
                self.funky_name = next(iter(funkybob.RandomNameGenerator()))

            folder_name = f"{dt_string}__{self.funky_name}"

            if self.is_slurm:
                folder_name += f"__{self.slurm_job_id}"
                res_base_path = self.exp_def.get("slurm_cluster", {}).get("scratch_results_path")
                if res_base_path is None:
                    raise ValueError("Error, scratch_results_path was not defined.")

            else:
                res_base_path = self.exp_def.get("store", {}).get("results_path", None)
                if res_base_path is None:
                    raise ValueError("Error, result path was not defined.")

            self._results_dir = os.path.join(res_base_path, self.project, self.experimentName, folder_name)

            if not os.path.exists(self._results_dir):
                os.makedirs(self._results_dir)

        return self._results_dir

    @property
    def results_output_dir(self) -> str:
        if not self.is_main_process():
            return None

        if self._results_output_dir is None:
            self._results_output_dir = os.path.join(self.results_dir, "training_outputs")
            if not os.path.exists(self._results_output_dir):
                os.makedirs(self._results_output_dir)
        return self._results_output_dir

    @property
    def test_dir(self) -> str:
        if not self.is_main_process():
            return None

        if self._test_dir is None:
            folder_name = self.creation_time.strftime("%Y%m%d_%H_%M_%S")
            if self.is_slurm:
                folder_name += f"__{self.slurm_job_id}"
            self._test_dir = os.path.join(self.results_dir, "test", folder_name)
            if not os.path.exists(self._test_dir):
                os.makedirs(self._test_dir)
        return self._test_dir

    @property
    def valLoss(self) -> float:
        return self._valLoss

    @valLoss.setter
    def valLoss(self, value: float) -> None:
        self._valLoss = value
        self.valLoss_per_ep.append(value)
        if not math.isnan(value):
            self.bestValLoss = min(self.bestValLoss, self._valLoss)
            if self.bestValLoss == value:
                self.new_best_val_loss = True
                self.new_best_val_loss_ep_id = self.current_epoch

    @property
    def trainLoss(self) -> float:
        return self._trainLoss

    @trainLoss.setter
    def trainLoss(self, value: float) -> None:
        self._trainLoss = value
        self.trainLoss_per_ep.append(value)
        if not math.isnan(value):
            self.bestTrainLoss = min(self.bestTrainLoss, self._trainLoss)
            if self.bestTrainLoss == value:
                self.new_best_train_loss = True
                self.new_best_train_loss_ep_id = self.current_epoch

    def is_main_process(self) -> bool:
        """Check if the current process is the main process in a distributed setup."""
        if not self.is_distributed():
            return True
        return self.rank == 0

    def is_child_process(self) -> bool:
        """Check if the current process is a child process in a distributed setup."""
        if not self.is_distributed():
            return False
        return self.rank > 0

    def is_distributed(self) -> bool:
        """Check if the current setup is distributed."""
        return self.world_size > 1

    def dist_barrier(self) -> None:
        """Barrier for distributed training."""
        if self.is_distributed():
            torch.distributed.barrier()

    def init_distributed_mode(self):
        # if "SLURM_PROCID" not in os.environ or os.environ["SLURM_JOB_NAME"] == "bash":
        #     return

        if not self.is_distributed():
            return

        os.environ["MASTER_ADDR"] = "localhost"
        # os.environ["MASTER_PORT"] = str(self.master_port)
        torch.cuda.set_device(self.rank)

        dist_backend = "nccl"
        # dist_url = "env://"
        rdvz_location = f"file://{self.ddp_rdvz_path}ddp_rendezvous_{self.experimentName}"

        iprint("Initializing distributed mode.")
        iprint(f"world size {self.world_size}, rank: {self.rank}")

        torch.distributed.init_process_group(
            backend=dist_backend,
            init_method=rdvz_location,
            world_size=self.world_size,
            rank=self.rank,
            # timeout=timedelta(minutes=15),
            # device_id=torch.device("cuda", self.rank),
        )

        print(f"Distributed mode initialized on rank {self.rank}.")
        self.dist_barrier()

    def store_experiment_git_hash(self):
        """Check if the experiment directory is a git repository and store the current git hash."""
        exp_path = os.path.abspath(self.experiment_file_path)
        try:
            exp_git = git.Repo(exp_path, search_parent_directories=True)
            if exp_git.is_dirty():
                dirty_files = [f.b_path for f in exp_git.index.diff(None)]
            else:
                dirty_files = None
            self.processing_log_dict["experiment_git"] = {
                "hash": exp_git.head.object.hexsha,
                "dirty_files": dirty_files,
            }
        except Exception:
            self.processing_log_dict["experiment_git"] = "UNABLE TO LOCALIZE GIT REPO!"

    def add_module_to_syspath(self, path: str) -> None:
        if not os.path.exists(path):
            raise FileNotFoundError(f"File {path} not found.")

        parent_dir = os.path.dirname(path)
        if parent_dir not in sys.path:
            sys.path.append(parent_dir)

    def import_class(self, file_path: str | None = None, module_name: str | None = None) -> Any:
        if module_name is None:
            if file_path is None or not file_path.endswith(".py"):
                raise ValueError(
                    f"Error, path must be a string with the module name and class name separated by a dot. Got: {file_path}"
                )
            self.add_module_to_syspath(file_path)
            module_name = os.path.splitext(os.path.basename(file_path))[0]
        return importlib.import_module(module_name)

    def instantiate_class(
        self,
        class_path: str | None = None,
        file_path: str | None = None,
        class_name: str | None = None,
    ) -> Any:
        if class_path is None and file_path is None:
            raise ValueError(f"Error, class_path or file_path must be defined. Got: {class_path}, {file_path}")

        if class_path is not None:
            if "." not in class_path:
                raise ValueError(
                    f"Error, class_path must be a string with the module name and class name separated by a dot. Got: {class_path}"
                )
            module_path, class_name = class_path.rsplit(".", 1)
            module = self.import_class(module_name=module_path)

        elif file_path is not None:
            if not file_path.endswith(".py"):
                raise ValueError(
                    f"Error, path must be a string with the module name and class name separated by a dot. Got: {file_path}"
                )
            if class_name is None:
                raise ValueError(f"Error, class_name must be defined if file_path is used. Got: {class_name}")
            self.add_module_to_syspath(file_path)
            module_name = os.path.basename(file_path).split(".")[0]
            module = importlib.import_module(module_name)
        else:
            raise ValueError(f"Error, class_path or file_path must be defined. Got: {class_path}, {file_path}")

        return getattr(module, class_name)

    def load_model_from_path(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Error, trained model path {path} does not exist.")
        return torch.load(path, weights_only=False).to(self.device).eval()

    def init_models(self, instantiate: bool = True) -> None:
        if self.models:
            return

        for model_name, model_def in self.exp_def.models:
            if model_def.path is not None:
                if os.path.exists(model_def.path):
                    cls = self.instantiate_class(file_path=model_def.path, class_name=model_def.class_name)
                else:
                    # if path does not exist, it might be a a fdq model specified by the file name only.
                    current_file_path = os.path.abspath(__file__)
                    networks_dir = os.path.abspath(os.path.join(os.path.dirname(current_file_path), "../networks/"))
                    model_path = os.path.join(networks_dir, model_def.path)
                    cls = self.instantiate_class(file_path=model_path, class_name=model_def.class_name)

            elif model_def.class_name is not None:
                # model is an installed pip package
                cls = self.instantiate_class(class_path=model_def.class_name)
            else:
                raise ValueError(f"Error, model {model_name} must have a path or module defined.")

            # load trained model from automatically detected path
            # -> only used for testing or dumping - highest priority
            if self.trained_model_paths.get(model_name) is not None:
                self.models[model_name] = self.load_model_from_path(self.trained_model_paths[model_name])

            # load trained model from path defined in exp file
            elif model_def.trained_model_path is not None:
                self.models[model_name] = self.load_model_from_path(model_def.trained_model_path)

            # or instantiate new model with random weights
            elif instantiate:
                self.models[model_name] = cls(**model_def.args.to_dict()).to(self.device)
                iprint(
                    f"Model {model_name} instantiated on rank {self.rank}.",
                    dist_print=True,
                )

            if model_name in self.models:
                if self.is_distributed():
                    self.dist_barrier()

                    self.models[model_name] = DDP(
                        self.models[model_name].cuda(self.rank),
                        device_ids=[self.rank],
                        # find_unused_parameters=True,
                    )
                    iprint(
                        f"Model {model_name} wrapped in DDP on rank {self.rank}. ",
                        dist_print=True,
                    )
                    self.models_no_ddp[model_name] = self.models[model_name].module
                else:
                    self.models_no_ddp[model_name] = self.models[model_name]

                # frozen model? disable gradient tracking
                if model_def.freeze:
                    iprint(f"Freezing model {model_name} parameters.")
                    for param in self.models[model_name].parameters():
                        param.requires_grad = False

    def load_trained_models(self) -> None:
        """Load trained models, defined by user path or previous trainings.

        This function is only used in model dumping or testing mode, therefore world_size != 1,
        and map_location is not required.
        """
        if not self.is_main_process():
            return
        for model_name, _ in self.exp_def.models:
            if self.mode.test_mode.custom_path:
                while True:
                    model_path = input(f"Enter path to model for '{model_name}' (or 'q' to quit).")
                    if model_path == "q":
                        sys.exit()
                    elif os.path.exists(model_path):
                        break
                    else:
                        eprint(f"Error: File {model_path} not found.")
            else:
                self._results_dir, net_name = find_model_path(self)
                model_path = os.path.join(self._results_dir, net_name)
            self.trained_model_paths[model_name] = model_path

        self.init_models(instantiate=False)
        [self.models[model_name].eval() for model_name, _ in self.exp_def.models]

    def setupData(self) -> None:
        if self.exp_def.data is None:
            wprint(
                "No data section found in the experiment file. Data setup must be handled manually in the training loop."
            )
            return
        if self.data:
            # data already loaded, skip setup
            return

        self.copy_data_to_scratch()

        for data_name, data_source in self.exp_def.data.items():
            processor = self.import_class(file_path=data_source.processor)

            if data_source.caching is None:
                self.data[data_name] = DictToObj(processor.create_datasets(self, self.exp_def.data.get(data_name).args))
            else:
                self.data[data_name] = DictToObj(cache_datasets_ddp_handler(self, processor, data_name, data_source))

        self.print_dataset_infos()

    def save_current_model(self) -> None:
        """Store model including weights.

        This is run at the end of every epoch.
        """
        if not self.is_main_process():
            # only the main process saves the checkpoint
            return

        for model_name, model_def in self.exp_def.models:
            if model_def.freeze:
                # skip frozen models
                continue

            model = self.models_no_ddp[model_name]

            if self.exp_def.store.get("save_last_model", False):
                remove_file(self.last_model_path.get(model_name))
                self.last_model_path[model_name] = os.path.join(
                    self.results_dir,
                    f"last_{model_name}_e{self.current_epoch}.fdqm",
                )
                torch.save(model, self.last_model_path[model_name])

            # new best val loss (default!)
            if self.exp_def.store.get("save_best_val_model", False) and self.new_best_val_loss:
                best_model_path = os.path.join(
                    self.results_dir,
                    f"best_val_{model_name}_e{self.current_epoch}.fdqm",
                )
                remove_file(self.best_val_model_path.get(model_name))
                self.best_val_model_path[model_name] = best_model_path
                torch.save(model, best_model_path)

            # save best model according to train loss
            if (
                self.current_epoch == self.start_epoch
                or self.exp_def.store.get("save_best_train_model", False)
                and self.new_best_train_loss
            ):
                best_train_model_path = os.path.join(
                    self.results_dir,
                    f"best_train_{model_name}_e{self.current_epoch}.fdqm",
                )
                remove_file(self.best_train_model_path.get(model_name))
                self.best_train_model_path[model_name] = best_train_model_path
                torch.save(model, best_train_model_path)

    def print_nb_weights(self) -> None:
        """Print the number of parameters for each model in the experiment."""
        for model_name, model in self.models.items():
            iprint("-----------------------------------------------------------")
            iprint(f"Model: {model_name}")
            nbp = sum(p.numel() for p in model.parameters())
            iprint(f"nb parameters: {nbp / 1e6:.2f}M")
            iprint(f"Using Float32, This will require {nbp * 4 / 1e9:.3f} GB of memory.")
            iprint("-----------------------------------------------------------")
            self.processing_log_dict[model_name] = {
                "nb_parameters": f"{nbp / 1e6:.2f}M",
                "memory_usage_GB": f"{nbp * 4 / 1e9:.3f} GB",
            }

    def prepareTraining(self) -> None:
        self.mode.train()
        self.setupData()
        self.trainer = self.import_class(file_path=self.exp_def.train.path)
        self.createLosses()
        if self.exp_def.models is not None:
            self.init_models()
            self.print_nb_weights()
            self.createOptimizer()
            self.set_lr_schedule()
        else:
            wprint(
                "Warning: No models defined in experiment file -> Model has to be manually defined in the training/testing loop."
            )

        if self.useAMP:
            self.scaler = torch.amp.GradScaler(device=self.device, enabled=True)

        if self.inargs.resume_path is not None:
            iprint("-----------------------------------------------------------")
            iprint(f"Loading checkpoint: {self.inargs.resume_path}")

            self.load_checkpoint(self.inargs.resume_path)

        self.cp_to_res_dir(file_path=self.experiment_file_path)
        for p in self.exp_def.globals.parent_hierarchy:
            self.cp_to_res_dir(file_path=p)

        store_processing_infos(self)
        self.dist_barrier()

    def createOptimizer(self) -> None:
        for model_name, margs in self.exp_def.models:
            if margs.optimizer is None:
                iprint(f"No optimizer defined for model {model_name}")
                # -> either its frozen, or manually defined within train loop
                self.optimizers[model_name] = None
                continue

            cls = self.instantiate_class(margs.optimizer.class_name)

            optimizer = cls(
                self.models[model_name].parameters(),
                **margs.optimizer.args.to_dict(),
            )

            if optimizer is not None:
                optimizer.zero_grad()

            self.optimizers[model_name] = optimizer

    def set_lr_schedule(self) -> None:
        # https://pytorch.org/docs/stable/optim.html#how-to-adjust-learning-rate
        # https://towardsdatascience.com/a-visual-guide-to-learning-rate-schedulers-in-pytorch-24bbb262c863

        for model_name, margs in self.exp_def.models:
            if self.optimizers[model_name] is None:
                # no optimizer defined for this model
                self.lr_schedulers[model_name] = None
                continue
            if margs.lr_scheduler is None:
                self.lr_schedulers[model_name] = None
                continue

            lr_scheduler_module = margs.lr_scheduler.class_name

            if lr_scheduler_module is None:
                self.lr_schedulers[model_name] = None
                continue

            cls = self.instantiate_class(lr_scheduler_module)

            self.lr_schedulers[model_name] = cls(self.optimizers[model_name], **margs.lr_scheduler.args.to_dict())

    def createLosses(self) -> None:
        if self.exp_def.losses is None:
            wprint("No losses defined in the experiment file. Losses must be defined in the training loop.")
            return
        for loss_name, largs in self.exp_def.losses:
            if largs.path is not None:
                cls = self.instantiate_class(file_path=largs.path, class_name=largs.class_name)
            elif largs.class_name is not None:
                cls = self.instantiate_class(class_path=largs.class_name)
            else:
                raise ValueError(f"Error, loss {loss_name} must have a path or class name defined.")
            if largs.args is not None:
                self.losses[loss_name] = cls(**largs.args.to_dict())
            else:
                self.losses[loss_name] = cls()

    def load_checkpoint(self, path: str) -> None:
        """Load checkpoint to resume training."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Error, checkpoint file {path} not found.")

        try:
            # checkpoint was saved on rank 0
            # so we need to map to the current rank
            map_location = {f"cuda:{0}": f"cuda:{self.rank}"} if self.is_distributed() else None
            checkpoint = torch.load(path, map_location=map_location)
            self.start_epoch = checkpoint["epoch"]
            self.trainLoss = checkpoint["train_loss"]
            self.valLoss = checkpoint["val_loss"]
            self.funky_name = checkpoint["funky_name"]
            self.previous_slurm_job_id = checkpoint.get("slurm_job_id")
        except Exception as exc:
            raise ValueError(f"Error loading checkpoint {path}.") from exc

        iprint(f"Loaded checkpoint {self.start_epoch}. Train loss: {self.trainLoss:.4f}, val loss: {self.valLoss:.4f}")

        if self.start_epoch >= self.nb_epochs - 1:
            raise ValueError(
                f"Error, checkpoint epoch {self.start_epoch + 1} already reached defined nb epochs ({self.nb_epochs})."
            )

        for model_name, model_def in self.exp_def.models:
            if model_def.freeze:
                iprint(f"Skipping loading of frozen model {model_name}.")
                continue
            self.models_no_ddp[model_name].load_state_dict(checkpoint["model_state_dict"][model_name])

            if checkpoint["optimizer"] is None:
                self.optimizers[model_name] = None
            else:
                self.optimizers[model_name].load_state_dict(checkpoint["optimizer"][model_name])

    def save_checkpoint(self) -> None:
        if not self.is_main_process():
            # only the main process saves the checkpoint
            return

        if self.checkpoint_frequency is None or self.checkpoint_frequency == 0:
            return

        if self.current_epoch % self.checkpoint_frequency != 0:
            return

        remove_file(self.checkpoint_path)
        self.checkpoint_path = os.path.join(self.results_dir, f"checkpoint_e{self.current_epoch}.fdqcpt")

        iprint(f"Saving checkpoint to {self.checkpoint_path}")

        if not self.optimizers:
            optimizer_state = None
        else:
            optimizer_state = {}
            for optim_name, optim in self.optimizers.items():
                if optim is None:
                    optimizer_state[optim_name] = None
                else:
                    optimizer_state[optim_name] = optim.state_dict()

        model_state = {}
        for model_name, model_def in self.exp_def.models:
            if model_def.freeze:
                model_state[model_name] = "FROZEN"
            else:
                # we save only the non-ddp wrapped model in the rank 0 process
                model_state[model_name] = self.models_no_ddp[model_name].state_dict()

        checkpoint = {
            "epoch": self.current_epoch,
            "model_state_dict": model_state,
            "optimizer": optimizer_state,
            "train_loss": self.trainLoss_per_ep[-1],
            "val_loss": self.valLoss_per_ep[-1],
            "funky_name": self.funky_name,
            "slurm_job_id": self.slurm_job_id,
        }

        torch.save(checkpoint, self.checkpoint_path)

    def get_next_export_fn(self, name: str | None = None, file_ending: str = "jpg") -> str:
        if not self.is_main_process():
            return None

        if self.mode.op_mode.test:
            start_str = "test_image"
            dest_dir = self.test_dir
        else:
            start_str = f"train_out_e{self.current_epoch:02}"
            dest_dir = self.results_output_dir

        name_str = "" if name is None else f"__{name}"
        path = os.path.join(dest_dir, f"{start_str}_{self.file_store_cnt:02}{name_str}.{file_ending}")

        self.file_store_cnt += 1

        return path

    def print_dataset_infos(self) -> None:
        iprint("-----------------------------------------------------------")
        for data_name, data_source in self.exp_def.data.items():
            iprint(f"Dataset: {data_name}")
            iprint(f"Train batch size: {data_source.args.train_batch_size}")
            iprint(f"Validation batch size: {data_source.args.val_batch_size}")
            iprint(f"Test batch size: {data_source.args.test_batch_size}")
            iprint(f"Nb samples train: {self.data[data_name].n_train_samples}")
            iprint(f"Nb samples val: {self.data[data_name].n_val_samples}")
            iprint(f"Nb samples test: {self.data[data_name].n_test_samples}")
        iprint("-----------------------------------------------------------")

    def clean_up_train(self) -> None:
        iprint("-----------------------------------------------------------")
        iprint("Training done!\nCleaning up..")
        iprint("-----------------------------------------------------------")
        if self.is_main_process():
            if self.useTensorboard:
                self.tb_writer.close()

            if self.wandb_initialized:
                wandb.finish()

            store_processing_infos(self)

    def clean_up_distributed(self) -> None:
        if self.is_distributed():
            torch.distributed.destroy_process_group()

    def check_early_stop(self) -> bool:
        """Check if training should be stopped.

        1) Stop training if the validation los over last last N epochs did not further decrease.
        We want at least N epochs in each training start, also if its a resume from checkpoint training.
        (--> Therefore, (cur_epoch - self.start_epoch) > self.early_stop_val_loss)

        2) Stop training if the loss is NaN for N epochs.
        """
        e_stop_nan = self.exp_def.train.args.early_stop_nan
        e_stop_val = self.exp_def.train.args.early_stop_val_loss
        e_stop_train = self.exp_def.train.args.early_stop_train_loss

        # early stop NaN ?
        if e_stop_nan is not None:
            if all(math.isnan(x) for x in self.trainLoss_per_ep[-e_stop_nan:]):
                self.early_stop_detected = True
                self.early_stop_reason = "NaN_train_Loss"
                wprint(
                    "\n###############################\n"
                    f"!! Early Stop NaN EP {self.current_epoch} !!\n"
                    "###############################\n"
                )
                return True

        # early stop val loss?
        # did we have a new best val loss within the last N epochs?
        # we want at least N losses
        if e_stop_val is not None and len(self.valLoss_per_ep) >= e_stop_val:
            # was there a new best val loss within the last N epochs?
            if min(self.valLoss_per_ep[-e_stop_val:]) != self.bestValLoss:
                self.early_stop_detected = True
                self.early_stop_reason = "ValLoss_stagnated"
                wprint(
                    "\n###############################\n"
                    f"!! Early Stop Val Loss EP {self.current_epoch} !!\n"
                    "###############################\n"
                )
                return True

        # early stop train loss?
        elif e_stop_train is not None and len(self.trainLoss_per_ep) >= e_stop_train:
            if min(self.trainLoss_per_ep[-e_stop_train:]) != self.bestTrainLoss:
                wprint(
                    "\n###############################\n"
                    f"!! Early Stop Train Loss EP {self.current_epoch} !!\n"
                    "###############################\n"
                )
                self.early_stop_detected = True
                self.early_stop_reason = "TrainLoss_stagnated"
                return True

        return False

    def update_gradients(self, b_idx: int, loader_name: str, model_name: str) -> None:
        length_loader = self.data[loader_name].n_train_batches

        if ((b_idx + 1) % self.gradacc_iter == 0) or (b_idx + 1 == length_loader):
            optimizer = self.optimizers[model_name]
            if optimizer is not None:
                if self.useAMP:
                    # self.scaler.unscale_(optimizer) # TODO
                    self.scaler.step(optimizer)
                    self.scaler.update()
                else:
                    optimizer.step()
                optimizer.zero_grad()

    def on_epoch_start(self, epoch: int) -> None:
        if epoch is None:
            self.current_epoch += 1
        else:
            self.current_epoch = epoch

        self.current_ep_start_time = datetime.now()

        iprint(f"\nEpoch: {self.current_epoch + 1} / {self.nb_epochs}")

        if self.is_distributed():
            # necessary to make shuffling work properly
            for data_name, _ in self.exp_def.data.items():
                if self.data[data_name] is not None:
                    if self.data[data_name].train_sampler is not None:
                        self.data[data_name].train_sampler.set_epoch(epoch)
                    if self.data[data_name].val_sampler is not None:
                        self.data[data_name].val_sampler.set_epoch(epoch)

    def on_epoch_end(
        self,
        log_scalars: dict[str, float] | None = None,
        log_images_wandb: Any | None = None,
        log_images_tensorboard: Any | None = None,
        log_text_tensorboard: Any | None = None,
    ) -> None:
        # update learning rate
        for model_name in self.models:
            scheduler = self.lr_schedulers[model_name]
            if scheduler is not None:
                current_LR = scheduler.get_last_lr()
                scheduler.step()
                new_LR = scheduler.get_last_lr()
                if current_LR != new_LR:
                    iprint(f"Updating LR of {model_name} from {current_LR} to {new_LR}")

        if not self.is_main_process():
            return

        show_train_progress(self)
        save_tensorboard(
            experiment=self,
            images=log_images_tensorboard,
            scalars=log_scalars,
            text=log_text_tensorboard,
        )
        save_wandb(
            experiment=self,
            images=log_images_wandb,
            scalars=log_scalars,
        )

        try:
            current_ep_time = datetime.now() - self.current_ep_start_time
            self.total_run_time = datetime.now() - self.creation_time

            iprint(
                f"Total run time: {self.total_run_time.days} days, "
                f"{self.total_run_time.seconds // 3600} hours, "
                f"{self.total_run_time.seconds % 3600 / 60.0:.0f} minutes | "
                f"current epoch: {int(current_ep_time.total_seconds() // 60)} minutes {int(current_ep_time.total_seconds() % 60)} seconds"
            )
        except (AttributeError, ValueError, TypeError):
            iprint("Error calculating epoch time - skipping.")

        store_processing_infos(self)

        if self.current_epoch == self.nb_epochs - 1:
            self.finish_time = datetime.now()

        save_train_history(self)
        self.save_checkpoint()
        self.save_current_model()

    def cp_to_res_dir(self, file_path: str) -> None:
        if not self.is_main_process():
            return
        fn = file_path.split("/")[-1]
        iprint(f"Saving {fn} to {self.results_dir}...")
        shutil.copyfile(file_path, f"{self.results_dir}/{fn}")

    def copy_files_to_test_dir(self, file_path: str) -> None:
        fn = file_path.split("/")[-1]
        iprint(f"Saving {fn} to {self.test_dir}...")
        shutil.copyfile(file_path, f"{self.test_dir}/{fn}")

    def runEvaluator(self) -> Any:
        evaluator_path = self.exp_def.test.processor

        if not os.path.exists(evaluator_path):
            raise FileNotFoundError(f"Evaluator file not found: {evaluator_path}")

        parent_dir = os.path.dirname(evaluator_path)
        if parent_dir not in sys.path:
            sys.path.append(parent_dir)

        module_name = os.path.splitext(os.path.basename(evaluator_path))[0]
        currentEvaluator = importlib.import_module(module_name)

        return currentEvaluator.fdq_test(self)

    def copy_data_to_scratch(self) -> None:
        """Copy all datasets to scratch dir, and update the paths."""
        if self.scratch_data_path is None:
            return

        if self.is_main_process():
            os.makedirs(self.scratch_data_path, exist_ok=True)

        iprint("-----------------------------------------------------------")
        iprint("Copy datasets to temporary scratch location...")
        iprint("-----------------------------------------------------------")

        for data_name, data_source in self.exp_def.data.items():
            dargs = data_source.args

            if dargs.base_path is not None:
                dst_path = os.path.join(self.scratch_data_path, data_name)

                # actual actions only on rank 0
                if self.is_main_process():
                    # cleanup old data first -> in case this is a debug run with dirty data
                    if os.path.exists(dst_path):
                        shutil.rmtree(dst_path)

                    if not os.path.exists(dargs.base_path):
                        wprint(
                            f"Warning: Base path {dargs.base_path} for dataset {data_name} does not exist - nothing to copy!"
                        )
                    else:
                        try:
                            subprocess.run(
                                ["rsync", "-au", dargs.base_path, dst_path],
                                capture_output=True,
                                text=True,
                                check=True,
                            )
                            iprint(f"Successfully copied {dargs.base_path} to {dst_path}")

                        except Exception as exc:
                            raise ValueError(
                                f"Unable to copy {dargs.base_path} to scratch location at {self.scratch_data_path}!"
                                f"Return code: {exc.returncode}, Error: {exc.stderr}"
                            ) from exc

                dargs.base_path = dst_path

            else:
                for file_cat in [
                    "train_files_path",
                    "test_files_path",
                    "val_files_path",
                ]:
                    fps = dargs.get(file_cat)
                    if not fps:
                        continue
                    if not isinstance(fps, list):
                        raise ValueError(f"Error, {data_name} dataset files must be a list of file paths. Got: {fps}")
                    new_paths = []
                    pbar = startProgBar(len(fps), f"Copy {file_cat} files to scratch")
                    for i, src_file in enumerate(fps):
                        pbar.update(i)
                        rel_path = os.path.relpath(src_file, "/")
                        dst_file = os.path.join(self.scratch_data_path, rel_path)
                        if self.is_main_process():
                            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                            shutil.copy(src_file, dst_file)
                        new_paths.append(dst_file)
                    dargs.set(file_cat, new_paths)
                    pbar.finish()

        iprint("-----------------------------------------------------------")
        iprint("Copy datasets to temporary scratch location... Done!")
        iprint("-----------------------------------------------------------")

        self.dist_barrier()

    def prepare_transformers(self) -> None:
        """Prepare transformers for the experiment."""
        if self.exp_def.transforms is None:
            return
        if not isinstance(self.exp_def.to_dict().get("transforms"), dict):
            raise ValueError("Error, transforms must be a dictionary with transform names as keys.")

        for transformer_name, transformer_def in self.exp_def.transforms.items():
            self.transformers[transformer_name] = get_transformers(t_defs=transformer_def)

    def print_model(self) -> None:
        if not self.is_main_process():
            return
        self.setupData()
        self.init_models()
        iprint("\n-----------------------------------------------------------")
        iprint("Print model definition")
        iprint("-----------------------------------------------------------\n")

        for model_name, model in self.models.items():
            iprint("\n-----------------------------------------------------------")
            iprint(model_name)
            iprint("\n-----------------------------------------------------------")
            iprint(model)
            iprint("-----------------------------------------------------------\n")

            try:
                iprint(f"Saving model graph to: {self.results_dir}/{model_name}_graph.png")

                sample = next(iter(self.data[next(iter(self.data))].train_data_loader))
                if isinstance(sample, tuple):
                    sample = sample[0]
                if isinstance(sample, list):
                    sample = sample[0]
                if isinstance(sample, dict):
                    sample = next(iter(sample.values()))

                draw_graph(
                    model,
                    input_size=sample.shape,
                    device=self.device,
                    save_graph=True,
                    filename=model_name + "_graph",
                    directory=self.results_dir,
                    expand_nested=False,
                )
            except (
                StopIteration,
                AttributeError,
                KeyError,
                TypeError,
                RuntimeError,
            ) as e:
                wprint("Failed to draw graph!")
                print(e)
