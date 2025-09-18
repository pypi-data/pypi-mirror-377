# iclearn

`iclearn` is a tool for standardizing distributed machine-learning workflows at ICHEC. It will allow us to develop a common set of performance benchmarking, profiling and optimization tools and apply them to ML workflows across scientific domains.

## Design ##

![Top-level library architecture](./docs/media/iclearn_toplevel_arch.png)

The top-level library architecture is shown above. A machine learning experiment is defined via a YAML file and launched via the CLI. Resources addressed in the YAML are loaded from a range of libraries, which are built out per-domain (e.g. Earth Observation) or per-framework (e.g. PyTorch). Libraries can include ML models and datasets, but also specialized metrics calculators, output handlers and profiling tools.

Once resources are loaded a machine learning experiment is executed in a `Session` using supported frameworks, primarily the PyTorch ecosystem at the moment, but others are planned.

![Library integration](./docs/media/iclearn_library_integration.png)

Practical integration of a third-party library is shown in the figure above. A config file is read through the CLI. Models, dataloaders and similar are loaded from third party libraries by 'provider' callbacks which take 'resource IDs' from the config and provide corresponding Python objects. The Python objects are derived from `iclearn` base classes and implement event handlers for different stages of a machine learning workflow, such as training steps, testing or inference.

A sample yaml file for a machine learning training session is shown below:

``` yaml
name: linear_train
dataloader:
  batch_size: 64
  dataset:
    name: linear
model:
  name: "torch.linear"
  framework: "pytorch"
  optimizer:
    name: "torch.SGD"
    learning_rate: 0.001
  loss_function: "torch.MSELoss"
outputs:
  - name: "logging"
  - name: "plotting"
    active: false
with_profiling: false
num_epochs: 10
num_batches: 0
```

This includes named PyTorch models or model elements, e.g. `torch.linear` and `torch.SGD` and their parameters, a named dataset `linear` and named output handlers `plotting` and `logging`.

A third party library may expose custom datasets `my_library.my_dataset` or output handlers `my_library.mlflow`, `my_library.my_grid_plotter`. 

with a simple implementation via inheritance from `iclearn` templates, as shown below.

```python
from iclearn.data import Dataloader, Splits
from iclearn.model import Model, Metrics

class MyModel(Model):

    def __init__(metrics: Metrics):
        super(metrics = metrics, MyOptimizer(MyLossFunc()))
        
    def predict(self, x):
        return ...
        
class MyDataloader(Dataloader):

    def load_dataset(root: Path, name: str, splits):
        return ...
        
    def load_dataloader(name: str):
        return...
```

As a real example of launching a CLI with a config you can train a simple built-in linear regression with:

``` shell
iclearn train --config test/data/experiments/linear_train.yaml
```

In practice you would launch your own program that includes functionality for providing your custom library resources via callbacks, giving something like:

``` shell
my_custom_pipeline train  --config my_experiment.yaml
```

## Installing ##

The package is available on PyPI, you can install the base package with:

``` shell
pip install iclearn
```

Most functionality so far uses PyTorch, you can install the PyTorch add-ons with:

``` shell
pip install 'iclearn[torch]'
```

## License ##

This software is Copyright ICHEC 2024 and can be re-used under the terms of the GPL v3+. See the included `LICENSE` file for details.
