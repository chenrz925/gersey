# task.utility

### PathProvider

```
geyser_lava.task.utility.PathProvider
```

**提供路径生成器**

|参数类型|定义|
|---|---|
|provides|`('path_provider',)`|
|requires|`()`|
|revert_requires|`()`|

=== "输出"
    `path_provider`为一个包含`temporary`、`home`以及`current`函数的对象。使用上述函数，按文件夹层级输入文件夹名称，能够得到绝对路径的[`Path`][pathlib.Path]对象。

=== "类型"
    `task`

### PathBuilder

```
geyser_lava.task.utility.PathBuilder
```

**生成路径**

|参数类型|定义|
|---|---|
|provides|`('path',)`|
|requires|`('typename', 'subpaths')`|
|revert_requires|`()`|

=== "输入"
    `typename`为生成路径的类型，必须为`temporary`、`home`或`current`。

    `subpaths`为按文件夹层级的文件夹名称列表。

=== "输出"
    `path`为一个包含绝对路径的[`Path`][pathlib.Path]对象。

=== "类型"
    `functor`

### EnvProvider

```
geyser_lava.task.utility.EnvProvider
```

**设置环境变量**

|参数类型|定义|
|---|---|
|provides|`('env',)`|
|requires|`()`|
|revert_requires|`()`|

=== "输入"
    输入参数名称不限，参数名称将被映射为环境变量。

=== "输出"
    `env`为运行时所有环境变量字典。

=== "类型"
    `task`

### IdProvider

```
geyser_lava.task.utility.IdProvider
```

**生成ID**

|参数类型|定义|
|---|---|
|provides|`('id',)`|
|requires|`()`|
|revert_requires|`()`|

=== "输入"
    `title`为自定义的ID前缀。

=== "输出"
    `id`为生成的包含自定义前缀、UUID以及时间戳的ID字符串。

=== "类型"
    `task`