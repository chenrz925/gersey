# task.torch

## common

### DataLoaderProvider

```
geyser_lava.task.torch.common.DataLoaderProvider
```

**构建数据加载器**

|参数类型|定义|
|---|---|
|provides|`('loader',)`|
|requires|`('dataset_params', 'loader_params')`|
|revert_requires|`()`|

=== "输入"
    `dataset_params`定义构建PyTorch风格数据集对象的参数，其中`reference`为数据集类的路径，数据集类必须为[Dataset][torch.utils.data.Dataset]或[IterableDataset][torch.utils.data.IterableDataset]的子类，其他参数会直接输入数据集类的构造函数中。

    `loader_params`定义输入PyTorch风格数据加载器，即[DataLoader][torch.utils.data.DataLoader]的参数。

=== "输出"
    `loader`为任务构建的数据加载器，即[DataLoader][torch.utils.data.DataLoader]对象。

=== "类型"
    `task`

### ModelProvider

```
geyser_lava.task.torch.common.ModelProvider
```

**构建模型**

|参数类型|定义|
|---|---|
|provides|`('model',)`|
|requires|`('model_params',)`|
|revert_requires|`()`|

=== "输入"
    `model_params`定义构建PyTorch模型对象的参数，其中`reference`为模型类或构建模型函数的路径，模型类必须为[Module][torch.nn.Module]的子类，其他参数会直接输入模型类的构造函数中。

=== "输出"
    `model`为任务构建的模型，即[Module][torch.nn.Module]对象。

=== "类型"
    `task`

### LossProvider

```
geyser_lava.task.torch.common.LossProvider
```

**构建损失函数**

|参数类型|定义|
|---|---|
|provides|`('loss',)`|
|requires|`('loss_params',)`|
|revert_requires|`()`|

=== "输入"
    `loss_params`定义构建PyTorch损失函数对象的参数，其中`reference`为损失函数类或损失函数的构建函数的路径，损失函数类必须为[Module][torch.nn.Module]的子类，其他参数会直接输入损失函数类的构造函数中。

=== "输出"
    `loss`为任务构建的损失函数，即[Module][torch.nn.Module]对象。

=== "类型"
    `task`

### OptimizerProvider

```
geyser_lava.task.torch.common.OptimizerProvider
```

**构建优化器**

|参数类型|定义|
|---|---|
|provides|`('optimizer',)`|
|requires|`('optimizer_params', 'model')`|
|revert_requires|`()`|

=== "输入"
    `optimizer_params`定义构建PyTorch优化器对象的参数，其中`reference`为优化器类的路径，优化器类必须为[Optimizer][torch.optim.Optimizer]的子类，其他参数会直接输入优化器类的构造函数中。

    `model`定义该优化器优化的模型对象。

=== "输出"
    `optimizer`为任务构建的损失函数，即[Optimizer][torch.optim.Optimizer]对象。

=== "类型"
    `task`

## trainer

### SupervisedTrainer

```
geyser_lava.task.torch.trainer.SupervisedTrainer
```

**有监督训练模型**

|参数类型|定义|
|---|---|
|provides|`('model',)`|
|requires|`('model', 'train_loader', 'validate_loader', 'optimizer', 'device', 'loss', 'metrics_params', 'max_epochs', 'non_blocking')`|
|revert_requires|`()`|

=== "输入"
    `model`定义需要训练的模型对象，即[Module][torch.nn.Module]对象。

    `train_loader`与`validate_loader`定义训练过程中训练数据集与验证数据集的数据加载器，即[DataLoader][torch.utils.data.DataLoader]对象。

    `optimizer`定义训练使用的优化器对象，即[Optimizer][torch.optim.Optimizer]对象。

    `device`定义模型训练过程中使用的设备，详见[Device][torch.torch.device]。

    `loss`定义训练过程中优化的损失函数对象，即[Module][torch.nn.Module]对象。

    `metrics_params`定义训练过程中显示的指标对象参数列表，每个元素参数中的`reference`为指标类的路径，关于指标类详见[ignite.metrics](https://pytorch.org/ignite/metrics.html)。

    `max_epochs`定义训练过程的最大轮数。

    `non_blocking`定义训练过程中数据加载是否为非阻塞方式。

=== "输出"
    `model`为训练完成时的模型对象，即[Module][torch.nn.Module]对象。

=== "类型"
    `task`