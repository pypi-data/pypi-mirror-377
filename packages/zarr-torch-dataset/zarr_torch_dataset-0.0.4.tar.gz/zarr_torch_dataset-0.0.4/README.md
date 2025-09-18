# Zarr Torch Dataset

## What is it?

Zarr Torch Dataset is an Pytorch Iterable Dataset implementation based on [Zarr](https://zarr.readthedocs.io/en/stable/) arrays.
This library addresses the problem of data distribution in the context of distributed data parallel PyTorch training.

During such training, several processes are executed at the same time. Ideally, each process holds a portion of the training data without it being duplicated in another process.
In addition, PyTorch offers parallel production of batches within a process: workers prepare batches that will be consumed one by one during training. Thus, workers within a training process must also share the data without duplication.

While distributed training (DDP), worker creation and management (DataLoader) mechanisms are implemented by PyTorch, loading data into RAM is left to the user, as the PyTorch makes no assumptions about the nature of the training data. To be precise: PyTorch does not distribute training data, but offers a data sampling mechanism based on data indexes (Samplers).

In general, when the training dataset is relatively small, users do not bother to optimize the memory footprint of training processes: each worker in the processes loads the entire dataset into RAM. This behavior poses a memory size problem when the dataset is large: it becomes impossible to load it multiple times. Furthermore, if the dataset does not fit into the memory of a single compute node, it must be distributed across a cluster of nodes.

This is where Zarr Torch Dataset comes in.

Like the Webdataset library, Zarr Torch Dataset will distribute pieces of the training dataset across all workers in all training process on all compute nodes, without duplication and with consistent data shuffling. This library is based on the Zarr data format, which implements the concept of data chunks with configurable dimensions. Zarr Torch Dataset enables the selection of a subset of chunks for training, which is useful for minimizing the time spent loading data into memory when developing the training script.

> [!important]
> There is only one constraint on chunk dimensions: chunking must be done only on the first dimension. For example, if the dataset has dimensions `(1400, 180, 360, 8)`, then the chunk dimensions must be `(n, 180, 360, 8)` where `n < 1400`.
> The greater the number of chunks (not `n`, but `1400 / n`), the greater the shuffling entropy, but the longer the read access time.



Why the Zarr format?

- It is mature and commonly used in geosciences.
- It allows decoupling between data storage (stores) and data indexing.
- It offers a set of compression codecs wrapped in the Blosc meta compressor.
- A selection of data from a Zarr array is of type Numpy NDArray.

> [!important]
> Zarr Torch Dataset only supports Zarr datasets and not Xarray datasets persisted in Zarr.
> The library doesn't support Zarr shards: it distributes chunks not shards.

## Notes

- reload_dataloaders_every_n_epochs in PyTorch Lightning trainer should always be zero unless you want to reload the entire dataset.
- use_distributed_sampler in PyTorch Lightning trainer is `False` for the best.
- You can provide samples and targets as Zarr groups.

## How to install?

### On IPSL GPU cluster HAL

#### Installation

```bash
module load pytorch-lightning/2.5.0.post0 # Or latest version.
mkdir -p "virtual_envs" # Create the environment parent dir, if it is not already done.
python -m venv --system-site-packages "virtual_envs/zarr_torch_dataset" # Create the virtual environment named zarr_torch_dataset.
source "virtual_envs/zarr_torch_dataset/bin/activate" # Activate the virtual environment.
pip install --no-cache-dir -U pip
pip install --no-cache-dir -U zarr-torch-dataset
```
#### Activation

```bash
module load pytorch-lightning/2.5.0.post0
source "virtual_envs/zarr_torch_dataset/bin/activate"
```
### On IDRIS super computer Jean Zay

#### Installation

```bash
module load pytorch-gpu/py3/2.8.0 # Or latest version
mkdir -p "virtual_envs" # Create the environment parent dir, if it is not already done.
python -m venv --system-site-packages "virtual_envs/zarr_torch_dataset" # Create the virtual environment named zarr_torch_dataset.
source "virtual_envs/zarr_torch_dataset/bin/activate" # Activate the virtual environment.
pip install --no-cache-dir-U pip
pip install --no-cache-dir -U lightning zarr-torch-dataset
```
#### Activation

```bash
module load pytorch-gpu/py3/2.8.0
source "virtual_envs/zarr_torch_dataset/bin/activate"
```

## How to use?

### Pytorch

TODO: to be documented.

### Pytorch lightning

#### On IDRIS super computer Jean Zay

##### Example of a distributed data parallel training:

```python
from zarrdataset import ZarrDataLoader, ZarrIterableDataset

# [...]

# Open your Zarr datasets.
train_samples = zarr.open('train_samples_zarr', mode='r')
train_targets = zarr.open('train_targets_zarr', mode='r')
validation_samples = zarr.open('validation_samples_zarr', mode='r')
validation_targets = zarr.open('validation_targets', mode='r')

# Instantiate the Zarr Iterable Datasets and Zarr Dataloaders.
# chunks_shuffle_seed can't be None, as all training process must have the same seed value.
train_ds = ZarrIterableDataset(samples=train_samples, targets=train_targets, shuffle_chunks=True,
                               chunks_shuffle_seed=42, shuffle_buffer=True, buffer_shuffle_seed=None)

val_ds = ZarrIterableDataset(samples=validation_samples, targets=validation_targets,
                             shuffle_chunks=False,
                             shuffle_buffer=False)

train_da = ZarrDataLoader(dataset=train_ds, num_workers=2, batch_size=32,
                          pin_memory=True, prefetch_factor=2, drop_last=False)

val_da = ZarrDataLoader(dataset=val_ds, num_workers=2, batch_size=32,
                        pin_memory=True, prefetch_factor=2, drop_last=False)

trainer = lightning.Trainer(devices=int(os.environ['SLURM_GPUS_ON_NODE']),
                            num_nodes=int(os.environ['SLURM_NNODES']),
                            strategy='ddp')

# Start training.
trainer.fit(model=model, train_dataloaders=train_da, val_dataloaders=val_da)
```

##### Example of a Slurm script submitting a 4 GPUs batch job (1 process per GPU), on partition gpu_p2:

```bash
#!/bin/bash

#SBATCH --account=YOUR_ACCOUNT
#SBATCH --partition=gpu_p2
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4  # Max 8 per gpu_p2 nodes
#SBATCH --gres=gpu:4         # Max 8 per gpu_p2 nodes
#SBATCH --cpus-per-task=3    # Specific for gpu_p2 nodes
#SBATCH --hint=nomultithread # Specific for Jean Zay
#SBATCH --time=2:00:00
#SBATCH --job-name=pl_test
#SBATCH --error=pl_test.log
#SBATCH --output=pl_test.log

# Enable the standard and error outputs of Python.
export PYTHONUNBUFFERED=1

# The latest pytorch module at this time.
module load pytorch-gpu/py3/2.8.0

# Activate Python virtual env.
source "/SOME/WHERE/TO/YOUR/virtual_envs/zarr_torch_dataset/bin/activate"

# Avoid no space left in device on Jean Zay.
export TMPDIR=$JOBSCRATCH

# You can give chunks_shuffle_seed value as a parameter to your script thank to $@.
# $RANDOM should be resourceful for generating the seed.
srun python YOUR_PYTHON_SCRIPT.py $@

returned_code=$?
echo "> script completed with exit code ${returned_code}"
exit ${returned_code}
```

> [!tip]
> Pytorch and Pytorch Lightning Slurm scripts differ only from the way to allocate GPUs and tasks.

## How to contribute?

Developing your patch in a forked repository then submitting a Merge Request in this repository.

* Pip

```bash
pip install -e .
pip install pre-commit
pre-commit install
```

* UV

```bash
uv sync
uv run pre-commit install
```
