# Welcome

![GitHub](https://img.shields.io/github/license/chenrz925/geyser?style=for-the-badge)

![PyPI](https://img.shields.io/pypi/v/geyser?label=Geyser&style=for-the-badge)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/chenrz925/geyser?label=Geyser&style=for-the-badge)
![GitHub last commit](https://img.shields.io/github/last-commit/chenrz925/geyser?label=Geyser&style=for-the-badge)
![PyPI - Status](https://img.shields.io/pypi/status/geyser?label=Geyser&style=for-the-badge)

![PyPI](https://img.shields.io/pypi/v/geyser-lava?label=Lava&style=for-the-badge)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/chenrz925/geyser-lava?label=Lava&style=for-the-badge)
![GitHub last commit](https://img.shields.io/github/last-commit/chenrz925/geyser-lava?label=Lava&style=for-the-badge)
![PyPI - Status](https://img.shields.io/pypi/status/geyser-lava?label=Lava&style=for-the-badge)

## Quick Start

Install `geyser` and `geyser-lava`。

```bash
pip install geyser geyser-lava
```

Execute：

```bash
geyser -d hello/hello.yaml
```

Geyser will display the following messages when installed successfully：

```
(2021-09-30 09:52:51,010)[DEBUG][2328932][140688370164544][geyser_lava.task.hello.Hello]: Hello, level debug.
(2021-09-30 09:52:51,010)[INFO][2328932][140688370164544][geyser_lava.task.hello.Hello]: Hello, level info.
(2021-09-30 09:52:51,010)[WARNING][2328932][140688370164544][geyser_lava.task.hello.Hello]: Hello, level warning
(2021-09-30 09:52:51,010)[ERROR][2328932][140688370164544][geyser_lava.task.hello.Hello]: Hello, level error.
(2021-09-30 09:52:51,010)[CRITICAL][2328932][140688370164544][geyser_lava.task.hello.Hello]: Hello, level critical.
```

### Core Install

You can only install `geyser` to support your own tasks：

```bash
pip install geyser
```

### Extra Install

#### Support PyTorch

According to the installation of [PyTorch](https://pytorch.org/) to install `pytorch`, `torchvision` and `torchaudio`. `pytorch-ignite` is also needed with the installation in [PyTorch Ignite](https://pytorch.org/ignite/).

When successfully installed, you can train a ResNet-50 model on CIFAR10 dataset:

```bash
geyser torch/train_resnet_cifar10.yaml
```