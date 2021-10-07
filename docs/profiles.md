# 配置文件

Geyser依靠遵循[Geyser JSON Schema](schema.json)的配置文件来编排执行各类任务。

## 基本概念

以下仅简要介绍对应概念，详细概念请点击标题。

### [Task](https://docs.openstack.org/taskflow/latest/user/atoms.html)

[`Task`][taskflow.task.Task]是任务流模型的基本单元，定义了基本的任务行为。你可以继承[`Task`][taskflow.task.Task]来定义你的任务，并通过[`Geyser.task`][geyser.Geyser.task]来注册你的任务。

如果只需要通过某个函数定义任务行为，Geyser会通过[`FunctorTask`][taskflow.task.FunctorTask]来将你的函数封装为`Task`。

### [Flow](https://docs.openstack.org/taskflow/latest/user/patterns.html)

[`Flow`][taskflow.flow.Flow]是任务流模型的编排规则，定义了任务的执行流程。

目前支持以下类型的`Flow`：

|类型             |行为                                            |
|----------------|------------------------------------------------|
|`linear`        |所有任务线性执行。                                 |
|`unordered`     |所有任务乱序执行。                                 |
|`graph`         |所有任务按DAG编排执行。                            |
|`targeted_graph`|所有任务按DAG编排执行，但不被目标任务依赖的任务不被执行。|

!!! warning
    `targeted_graph`类型尚未完全支持，可能存在问题，会在后续版本完善。

### [Engine](https://docs.openstack.org/taskflow/latest/user/engines.html)

`Flow`定义了任务的编排流程，而实际[`Engine`][taskflow.engines.base.Engine]依照`Flow`的规则驱动任务执行。

目前支持一下类型的`Engine`：

|类型                      |行为                                                        |
|-------------------------|------------------------------------------------------------|
|`serial`                 |所有任务在一个线程中执行。                                      |
|`parallel`               |所有任务在不同线程（或进程）并行执行，具体执行方式见[Executor](profiles.md#Executor)。|
|`worker-based`或`workers`|所有任务在不同机器分布式执行，具体执行方式见[Workers](https://docs.openstack.org/taskflow/latest/user/workers.html)|

!!! warning
    `worker-based`或`workers`类型尚未完全支持，可能存在问题，可能会在后续版本完善。

当“engine”字段为`parallel`时，需要额外定义“executor”的类型，支持的启动器类型如下：

|类型                                          |行为                              |
|---------------------------------------------|----------------------------------|
|`process`或`processes`                        |所有任务在不同进程中执行。           |
|`thread`、`threaded`或`threads`               |所有任务在不同线程中执行。            |
|`greenthread`、`greedthreaded`或`greenthreads`|所有任务在不同协程（或绿色线程）中执行。|

!!! warning
    由于CPython的GIL（全局解释器锁）限制，使用除线程启动器（即选择`process`或`processes`）以外的启动器启动任务，可能由于解释器本身的原因并行执行难以生效。

## 编写配置文件

### 使用Geyser编辑

您可以使用Geyser调用编辑器来编写配置文件，例如：

```bash
geyser -e [配置文件路径]
```

Geyser会按以下优先级选择编辑器：

- 环境变量中定义`EDITOR`变量时，Geyser优先执行`EDITOR`定义的编辑器。
- 当用户在`~/.geyser/EDITOR`文件中定义编辑器时，会在环境变量`EDITOR`不存在的情况下执行该文件定义的编辑器。
- Geyser默认会使用vim作为编辑器

### “tasks”字段

“tasks”字段定义了所有任务的列表，对于每个任务需要的配置项如下：

|名称          |内容               |必填                          |
|-------------|------------------|------------------------------|
|reference    |任务路径            |:white_check_mark:           |
|name         |任务名称           |:white_check_mark:            |
|type         |任务类型            |:white_check_mark:           |
|inject       |输入任务参数        |:negative_squared_cross_mark: |
|rebind       |输入参数名称映射     |:negative_squared_cross_mark: |
|rename       |输出参数名称映射     |:negative_squared_cross_mark: |
|revert_rebind|回滚时输入参数名称映射|:negative_squared_cross_mark: |

=== "reference"
    任务真实路径，可以通过[`reference`][geyser.utility.reference]函数从类或函数获得。

=== "name"
    任务名称，**注意不能与其他任务重名**，在“flow”字段中按照该名称调用任务。

=== "type"
    任务类型，取决于注册时使用的装饰器。
    
    如果使用[`Geyser.functor`][geyser.Geyser.functor]，依照对参数的处理方式，可以使用`functor`、`mapper`或者`reducer`。

    如果使用[`Geyser.task`][geyser.Geyser.task]，使用`task`。


=== "inject"
    输入参数，直接注入到该任务参数注入的作用域中，但不会存在于后续任务的作用域中，不在`provides`中声明的参数依旧不会被传入任务中。

=== "rebind"
    重新绑定输入参数，按照**键**为**目标名称**，**值**为**原始名称**的方式进行映射。

=== "rename"
    重新命名输出参数，按照**键**为**原始名称**，**值**为**目标名称**的方式进行映射。

=== "revert_rebind"
    与`rebind`行为类似，但定义的是显式定义[`revert`][taskflow.atom.Atom.revert]函数即任务回滚时需要的输入参数。

### “flow”字段

“flow”字段定义的是任务流的逻辑结构，对于任务流需要的配置项如下：

|名称          |内容          |必填              |
|-------------|--------------|------------------|
|name         |任务流名称     |:white_check_mark:|
|type         |任务流类型     |:white_check_mark:|
|include      |任务流包含列表  |:white_check_mark:|

=== "name"
    任务流名称，建议不与其他任务流重名，同时将根任务流命名为“root”。

=== "type"
    任务流类型，可以使用的任务流类型参见[Flow](#flow)

=== "include"
    任务流包含列表，列表元素为字符串时将对应名称任务加入该任务流。当列表元素为与[“flow”字段](#flow字段)相同结构的对象时，会构建子任务流加入该任务流。

### “engine”字段

“engine”字段定义执行任务流过程中使用的引擎类型，对应[Engine](#engine)中对应的类型。

### “inject”字段

“inject”字段（可选）定义整个任务流执行过程中初始的输入参数，直接注入到全局作用域中。

### “backend”字段

“backend”字段（可选）定义任务引擎存储参数使用的后端，支持的后端有`memory`、`dir`、`file`、`mysql`、`postgres`、`sqlite`以及`zookeeper`，默认为`memory`。

!!! warning
    目前只支持`memory`后端进行存储，其他后端尚未经过测试。

### “executor”字段

如果“engine”字段为`parallel`，“executor”字段定义执行任务的基本单元，详见[Engine](#engine)。

## 完整示例

以下是`torch/train_resnet_cifar10.[format]`配置文件的完整示例。

### JSON

```json
{
  "$schema": "https://geyser.waterch.cn/zh_CN/latest/schema.json",
  "tasks": [
    {
      "reference": "geyser_lava.task.utility.IdProvider",
      "name": "id",
      "type": "task",
      "inject": {
        "title": "cifar10_resnet50"
      }
    },
    {
      "reference": "geyser_lava.task.utility.PathProvider",
      "name": "path",
      "type": "task",
      "rename": {
        "path_provider": "path"
      }
    },
    {
      "reference": "geyser_lava.task.utility.PathBuilder",
      "name": "dataset_root",
      "type": "functor",
      "inject": {
        "typename": "current",
        "subpaths": [
          "dataset",
          "cifar10"
        ]
      },
      "rename": {
        "path": "dataset_root"
      }
    },
    {
      "reference": "geyser_lava.profile._support.operator.ToTensor",
      "name": "vision_transform",
      "type": "functor"
    },
    {
      "reference": "geyser_lava.profile._support.operator.CifarUnflatten",
      "name": "train_dataset_params",
      "type": "functor",
      "inject": {
        "reference": "torchvision.datasets.cifar.CIFAR10",
        "train": true,
        "download": true
      },
      "rebind": {
        "root": "dataset_root"
      },
      "rename": {
        "obj": "train_dataset_params"
      }
    },
    {
      "reference": "geyser_lava.profile._support.operator.CifarUnflatten",
      "name": "validate_dataset_params",
      "type": "functor",
      "inject": {
        "reference": "torchvision.datasets.cifar.CIFAR10",
        "train": false,
        "download": true
      },
      "rebind": {
        "root": "dataset_root"
      },
      "rename": {
        "obj": "validate_dataset_params"
      }
    },
    {
      "reference": "geyser_lava.task.torch.common.DataLoaderProvider",
      "name": "train_loader",
      "type": "task",
      "rebind": {
        "dataset_params": "train_dataset_params"
      },
      "inject": {
        "loader_params": {
          "batch_size": 32,
          "shuffle": true
        }
      },
      "rename": {
        "loader": "train_loader"
      }
    },
    {
      "reference": "geyser_lava.task.torch.common.DataLoaderProvider",
      "name": "validate_loader",
      "type": "task",
      "rebind": {
        "dataset_params": "validate_dataset_params"
      },
      "inject": {
        "loader_params": {
          "batch_size": 32,
          "shuffle": true
        }
      },
      "rename": {
        "loader": "validate_loader"
      }
    },
    {
      "reference": "geyser_lava.task.torch.common.ModelProvider",
      "name": "model",
      "type": "task",
      "inject": {
        "model_params": {
          "reference": "torchvision.models.resnet.resnet50",
          "pretrained": false,
          "progress": false,
          "num_classes": 10
        }
      }
    },
    {
      "reference": "geyser_lava.task.torch.common.OptimizerProvider",
      "name": "optimizer",
      "type": "task",
      "inject": {
        "optimizer_params": {
          "reference": "torch.optim.adamw.AdamW"
        }
      }
    },
    {
      "reference": "geyser_lava.task.torch.common.LossProvider",
      "name": "loss",
      "type": "task",
      "inject": {
        "loss_params": {
          "reference": "torch.nn.modules.loss.CrossEntropyLoss"
        }
      }
    },
    {
      "reference": "geyser_lava.task.torch.trainer.SupervisedTrainer",
      "name": "trainer",
      "type": "task",
      "inject": {
        "max_epochs": 100,
        "device": "cuda:0",
        "metrics_params": [
          {
            "reference": "ignite.metrics.accuracy.Accuracy",
            "name": "accuracy",
            "params": {
              "device": "cuda:0"
            }
          },
          {
            "reference": "ignite.metrics.fbeta.Fbeta",
            "name": "f1macro",
            "params": {
              "beta": 1
            }
          }
        ],
        "non_blocking": true
      }
    }
  ],
  "flow": {
    "name": "root",
    "type": "graph",
    "include": [
      "id",
      "path",
      "dataset_root",
      "vision_transform",
      "train_dataset_params",
      "validate_dataset_params",
      "train_loader",
      "validate_loader",
      "model",
      "optimizer",
      "loss",
      "trainer"
    ]
  },
  "engine": "serial"
}
```

### YAML

```yaml
$schema: https://geyser.waterch.cn/zh_CN/latest/schema.json
tasks:
  - reference: geyser_lava.task.utility.IdProvider
    name: id
    type: task
    inject:
      title: cifar10_resnet50
  - reference: geyser_lava.task.utility.PathProvider
    name: path
    type: task
    rename:
      path_provider: path
  - reference: geyser_lava.task.utility.PathBuilder
    name: dataset_root
    type: functor
    inject:
      typename: current
      subpaths:
        - dataset
        - cifar10
    rename:
      path: dataset_root
  - reference: geyser_lava.profile._support.operator.ToTensor
    name: vision_transform
    type: functor
  - reference: geyser_lava.profile._support.operator.CifarUnflatten
    name: train_dataset_params
    type: functor
    inject:
      reference: torchvision.datasets.cifar.CIFAR10
      train: true
      download: true
    rebind:
      root: dataset_root
    rename:
      obj: train_dataset_params
  - reference: geyser_lava.profile._support.operator.CifarUnflatten
    name: validate_dataset_params
    type: functor
    inject:
      reference: torchvision.datasets.cifar.CIFAR10
      train: false
      download: true
    rebind:
      root: dataset_root
    rename:
      obj: validate_dataset_params
  - reference: geyser_lava.task.torch.common.DataLoaderProvider
    name: train_loader
    type: task
    rebind:
      dataset_params: train_dataset_params
    inject:
      loader_params:
        batch_size: 32
        shuffle: true
    rename:
      loader: train_loader
  - reference: geyser_lava.task.torch.common.DataLoaderProvider
    name: validate_loader
    type: task
    rebind:
      dataset_params: validate_dataset_params
    inject:
      loader_params:
        batch_size: 32
        shuffle: true
    rename:
      loader: validate_loader
  - reference: geyser_lava.task.torch.common.ModelProvider
    name: model
    type: task
    inject:
      model_params:
        reference: torchvision.models.resnet.resnet50
        pretrained: false
        progress: false
        num_classes: 10
  - reference: geyser_lava.task.torch.common.OptimizerProvider
    name: optimizer
    type: task
    inject:
      optimizer_params:
        reference: torch.optim.adamw.AdamW
  - reference: geyser_lava.task.torch.common.LossProvider
    name: loss
    type: task
    inject:
      loss_params:
        reference: torch.nn.modules.loss.CrossEntropyLoss
  - reference: geyser_lava.task.torch.trainer.SupervisedTrainer
    name: trainer
    type: task
    inject:
      max_epochs: 100
      device: cuda:0
      metrics_params:
        - reference: ignite.metrics.accuracy.Accuracy
          name: accuracy
          params:
            device: cuda:0
        - reference: ignite.metrics.fbeta.Fbeta
          name: f1macro
          params:
            beta: 1
      non_blocking: true
flow:
  name: root
  type: graph
  include:
    - id
    - path
    - dataset_root
    - vision_transform
    - train_dataset_params
    - validate_dataset_params
    - train_loader
    - validate_loader
    - model
    - optimizer
    - loss
    - trainer
engine: serial
```

### TOML

```toml
"$schema" = "https://geyser.waterch.cn/zh_CN/latest/schema.json"
engine = "serial"

[[tasks]]
reference = "geyser_lava.task.utility.IdProvider"
name = "id"
type = "task"
[tasks.inject]
title = "cifar10_resnet50"

[[tasks]]
reference = "geyser_lava.task.utility.PathProvider"
name = "path"
type = "task"
[tasks.rename]
path_provider = "path"

[[tasks]]
reference = "geyser_lava.task.utility.PathBuilder"
name = "dataset_root"
type = "functor"
[tasks.inject]
typename = "current"
subpaths = [ "dataset", "cifar10",]
[tasks.rename]
path = "dataset_root"

[[tasks]]
reference = "geyser_lava.profile._support.operator.ToTensor"
name = "vision_transform"
type = "functor"

[[tasks]]
reference = "geyser_lava.profile._support.operator.CifarUnflatten"
name = "train_dataset_params"
type = "functor"
[tasks.inject]
reference = "torchvision.datasets.cifar.CIFAR10"
train = true
download = true
[tasks.rebind]
root = "dataset_root"
[tasks.rename]
obj = "train_dataset_params"

[[tasks]]
reference = "geyser_lava.profile._support.operator.CifarUnflatten"
name = "validate_dataset_params"
type = "functor"
[tasks.inject]
reference = "torchvision.datasets.cifar.CIFAR10"
train = false
download = true
[tasks.rebind]
root = "dataset_root"
[tasks.rename]
obj = "validate_dataset_params"

[[tasks]]
reference = "geyser_lava.task.torch.common.DataLoaderProvider"
name = "train_loader"
type = "task"
[tasks.rebind]
dataset_params = "train_dataset_params"
[tasks.rename]
loader = "train_loader"
[tasks.inject.loader_params]
batch_size = 32
shuffle = true

[[tasks]]
reference = "geyser_lava.task.torch.common.DataLoaderProvider"
name = "validate_loader"
type = "task"
[tasks.rebind]
dataset_params = "validate_dataset_params"
[tasks.rename]
loader = "validate_loader"
[tasks.inject.loader_params]
batch_size = 32
shuffle = true

[[tasks]]
reference = "geyser_lava.task.torch.common.ModelProvider"
name = "model"
type = "task"
[tasks.inject.model_params]
reference = "torchvision.models.resnet.resnet50"
pretrained = false
progress = false
num_classes = 10

[[tasks]]
reference = "geyser_lava.task.torch.common.OptimizerProvider"
name = "optimizer"
type = "task"
[tasks.inject.optimizer_params]
reference = "torch.optim.adamw.AdamW"

[[tasks]]
reference = "geyser_lava.task.torch.common.LossProvider"
name = "loss"
type = "task"
[tasks.inject.loss_params]
reference = "torch.nn.modules.loss.CrossEntropyLoss"

[[tasks]]
reference = "geyser_lava.task.torch.trainer.SupervisedTrainer"
name = "trainer"
type = "task"
[tasks.inject]
max_epochs = 100
device = "cuda:0"
non_blocking = true
[[tasks.inject.metrics_params]]
reference = "ignite.metrics.accuracy.Accuracy"
name = "accuracy"
[tasks.inject.metrics_params.params]
device = "cuda:0"
[[tasks.inject.metrics_params]]
reference = "ignite.metrics.fbeta.Fbeta"
name = "f1macro"
[tasks.inject.metrics_params.params]
beta = 1

[flow]
name = "root"
type = "graph"
include = [ "id", "path", "dataset_root", "vision_transform", "train_dataset_params", "validate_dataset_params", "train_loader", "validate_loader", "model", "optimizer", "loss", "trainer",]
```

### HOCON

```hocon
"$schema" = "https://geyser.waterch.cn/zh_CN/latest/schema.json"
tasks = [
  {
    reference = "geyser_lava.task.utility.IdProvider"
    name = "id"
    type = "task"
    inject {
      title = "cifar10_resnet50"
    }
  }
  {
    reference = "geyser_lava.task.utility.PathProvider"
    name = "path"
    type = "task"
    rename {
      path_provider = "path"
    }
  }
  {
    reference = "geyser_lava.task.utility.PathBuilder"
    name = "dataset_root"
    type = "functor"
    inject {
      typename = "current"
      subpaths = [
        "dataset"
        "cifar10"
      ]
    }
    rename {
      path = "dataset_root"
    }
  }
  {
    reference = "geyser_lava.profile._support.operator.ToTensor"
    name = "vision_transform"
    type = "functor"
  }
  {
    reference = "geyser_lava.profile._support.operator.CifarUnflatten"
    name = "train_dataset_params"
    type = "functor"
    inject {
      reference = "torchvision.datasets.cifar.CIFAR10"
      train = true
      download = true
    }
    rebind {
      root = "dataset_root"
    }
    rename {
      obj = "train_dataset_params"
    }
  }
  {
    reference = "geyser_lava.profile._support.operator.CifarUnflatten"
    name = "validate_dataset_params"
    type = "functor"
    inject {
      reference = "torchvision.datasets.cifar.CIFAR10"
      train = false
      download = true
    }
    rebind {
      root = "dataset_root"
    }
    rename {
      obj = "validate_dataset_params"
    }
  }
  {
    reference = "geyser_lava.task.torch.common.DataLoaderProvider"
    name = "train_loader"
    type = "task"
    rebind {
      dataset_params = "train_dataset_params"
    }
    inject {
      loader_params {
        batch_size = 32
        shuffle = true
      }
    }
    rename {
      loader = "train_loader"
    }
  }
  {
    reference = "geyser_lava.task.torch.common.DataLoaderProvider"
    name = "validate_loader"
    type = "task"
    rebind {
      dataset_params = "validate_dataset_params"
    }
    inject {
      loader_params {
        batch_size = 32
        shuffle = true
      }
    }
    rename {
      loader = "validate_loader"
    }
  }
  {
    reference = "geyser_lava.task.torch.common.ModelProvider"
    name = "model"
    type = "task"
    inject {
      model_params {
        reference = "torchvision.models.resnet.resnet50"
        pretrained = false
        progress = false
        num_classes = 10
      }
    }
  }
  {
    reference = "geyser_lava.task.torch.common.OptimizerProvider"
    name = "optimizer"
    type = "task"
    inject {
      optimizer_params {
        reference = "torch.optim.adamw.AdamW"
      }
    }
  }
  {
    reference = "geyser_lava.task.torch.common.LossProvider"
    name = "loss"
    type = "task"
    inject {
      loss_params {
        reference = "torch.nn.modules.loss.CrossEntropyLoss"
      }
    }
  }
  {
    reference = "geyser_lava.task.torch.trainer.SupervisedTrainer"
    name = "trainer"
    type = "task"
    inject {
      max_epochs = 100
      device = "cuda:0"
      metrics_params = [
        {
          reference = "ignite.metrics.accuracy.Accuracy"
          name = "accuracy"
          params {
            device = "cuda:0"
          }
        }
        {
          reference = "ignite.metrics.fbeta.Fbeta"
          name = "f1macro"
          params {
            beta = 1
          }
        }
      ]
      non_blocking = true
    }
  }
]
flow {
  name = "root"
  type = "graph"
  include = [
    "id"
    "path"
    "dataset_root"
    "vision_transform"
    "train_dataset_params"
    "validate_dataset_params"
    "train_loader"
    "validate_loader"
    "model"
    "optimizer"
    "loss"
    "trainer"
  ]
}
engine = "serial"
```

### Apple pList

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>$schema</key>
	<string>https://geyser.waterch.cn/zh_CN/latest/schema.json</string>
	<key>engine</key>
	<string>serial</string>
	<key>flow</key>
	<dict>
		<key>include</key>
		<array>
			<string>id</string>
			<string>path</string>
			<string>dataset_root</string>
			<string>vision_transform</string>
			<string>train_dataset_params</string>
			<string>validate_dataset_params</string>
			<string>train_loader</string>
			<string>validate_loader</string>
			<string>model</string>
			<string>optimizer</string>
			<string>loss</string>
			<string>trainer</string>
		</array>
		<key>name</key>
		<string>root</string>
		<key>type</key>
		<string>graph</string>
	</dict>
	<key>tasks</key>
	<array>
		<dict>
			<key>inject</key>
			<dict>
				<key>title</key>
				<string>cifar10_resnet50</string>
			</dict>
			<key>name</key>
			<string>id</string>
			<key>reference</key>
			<string>geyser_lava.task.utility.IdProvider</string>
			<key>type</key>
			<string>task</string>
		</dict>
		<dict>
			<key>name</key>
			<string>path</string>
			<key>reference</key>
			<string>geyser_lava.task.utility.PathProvider</string>
			<key>rename</key>
			<dict>
				<key>path_provider</key>
				<string>path</string>
			</dict>
			<key>type</key>
			<string>task</string>
		</dict>
		<dict>
			<key>inject</key>
			<dict>
				<key>subpaths</key>
				<array>
					<string>dataset</string>
					<string>cifar10</string>
				</array>
				<key>typename</key>
				<string>current</string>
			</dict>
			<key>name</key>
			<string>dataset_root</string>
			<key>reference</key>
			<string>geyser_lava.task.utility.PathBuilder</string>
			<key>rename</key>
			<dict>
				<key>path</key>
				<string>dataset_root</string>
			</dict>
			<key>type</key>
			<string>functor</string>
		</dict>
		<dict>
			<key>name</key>
			<string>vision_transform</string>
			<key>reference</key>
			<string>geyser_lava.profile._support.operator.ToTensor</string>
			<key>type</key>
			<string>functor</string>
		</dict>
		<dict>
			<key>inject</key>
			<dict>
				<key>download</key>
				<true/>
				<key>reference</key>
				<string>torchvision.datasets.cifar.CIFAR10</string>
				<key>train</key>
				<true/>
			</dict>
			<key>name</key>
			<string>train_dataset_params</string>
			<key>rebind</key>
			<dict>
				<key>root</key>
				<string>dataset_root</string>
			</dict>
			<key>reference</key>
			<string>geyser_lava.profile._support.operator.CifarUnflatten</string>
			<key>rename</key>
			<dict>
				<key>obj</key>
				<string>train_dataset_params</string>
			</dict>
			<key>type</key>
			<string>functor</string>
		</dict>
		<dict>
			<key>inject</key>
			<dict>
				<key>download</key>
				<true/>
				<key>reference</key>
				<string>torchvision.datasets.cifar.CIFAR10</string>
				<key>train</key>
				<false/>
			</dict>
			<key>name</key>
			<string>validate_dataset_params</string>
			<key>rebind</key>
			<dict>
				<key>root</key>
				<string>dataset_root</string>
			</dict>
			<key>reference</key>
			<string>geyser_lava.profile._support.operator.CifarUnflatten</string>
			<key>rename</key>
			<dict>
				<key>obj</key>
				<string>validate_dataset_params</string>
			</dict>
			<key>type</key>
			<string>functor</string>
		</dict>
		<dict>
			<key>inject</key>
			<dict>
				<key>loader_params</key>
				<dict>
					<key>batch_size</key>
					<integer>32</integer>
					<key>shuffle</key>
					<true/>
				</dict>
			</dict>
			<key>name</key>
			<string>train_loader</string>
			<key>rebind</key>
			<dict>
				<key>dataset_params</key>
				<string>train_dataset_params</string>
			</dict>
			<key>reference</key>
			<string>geyser_lava.task.torch.common.DataLoaderProvider</string>
			<key>rename</key>
			<dict>
				<key>loader</key>
				<string>train_loader</string>
			</dict>
			<key>type</key>
			<string>task</string>
		</dict>
		<dict>
			<key>inject</key>
			<dict>
				<key>loader_params</key>
				<dict>
					<key>batch_size</key>
					<integer>32</integer>
					<key>shuffle</key>
					<true/>
				</dict>
			</dict>
			<key>name</key>
			<string>validate_loader</string>
			<key>rebind</key>
			<dict>
				<key>dataset_params</key>
				<string>validate_dataset_params</string>
			</dict>
			<key>reference</key>
			<string>geyser_lava.task.torch.common.DataLoaderProvider</string>
			<key>rename</key>
			<dict>
				<key>loader</key>
				<string>validate_loader</string>
			</dict>
			<key>type</key>
			<string>task</string>
		</dict>
		<dict>
			<key>inject</key>
			<dict>
				<key>model_params</key>
				<dict>
					<key>num_classes</key>
					<integer>10</integer>
					<key>pretrained</key>
					<false/>
					<key>progress</key>
					<false/>
					<key>reference</key>
					<string>torchvision.models.resnet.resnet50</string>
				</dict>
			</dict>
			<key>name</key>
			<string>model</string>
			<key>reference</key>
			<string>geyser_lava.task.torch.common.ModelProvider</string>
			<key>type</key>
			<string>task</string>
		</dict>
		<dict>
			<key>inject</key>
			<dict>
				<key>optimizer_params</key>
				<dict>
					<key>reference</key>
					<string>torch.optim.adamw.AdamW</string>
				</dict>
			</dict>
			<key>name</key>
			<string>optimizer</string>
			<key>reference</key>
			<string>geyser_lava.task.torch.common.OptimizerProvider</string>
			<key>type</key>
			<string>task</string>
		</dict>
		<dict>
			<key>inject</key>
			<dict>
				<key>loss_params</key>
				<dict>
					<key>reference</key>
					<string>torch.nn.modules.loss.CrossEntropyLoss</string>
				</dict>
			</dict>
			<key>name</key>
			<string>loss</string>
			<key>reference</key>
			<string>geyser_lava.task.torch.common.LossProvider</string>
			<key>type</key>
			<string>task</string>
		</dict>
		<dict>
			<key>inject</key>
			<dict>
				<key>device</key>
				<string>cuda:0</string>
				<key>max_epochs</key>
				<integer>100</integer>
				<key>metrics_params</key>
				<array>
					<dict>
						<key>name</key>
						<string>accuracy</string>
						<key>params</key>
						<dict>
							<key>device</key>
							<string>cuda:0</string>
						</dict>
						<key>reference</key>
						<string>ignite.metrics.accuracy.Accuracy</string>
					</dict>
					<dict>
						<key>name</key>
						<string>f1macro</string>
						<key>params</key>
						<dict>
							<key>beta</key>
							<integer>1</integer>
						</dict>
						<key>reference</key>
						<string>ignite.metrics.fbeta.Fbeta</string>
					</dict>
				</array>
				<key>non_blocking</key>
				<true/>
			</dict>
			<key>name</key>
			<string>trainer</string>
			<key>reference</key>
			<string>geyser_lava.task.torch.trainer.SupervisedTrainer</string>
			<key>type</key>
			<string>task</string>
		</dict>
	</array>
</dict>
</plist>
```