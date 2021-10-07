# utility

## operator

在当前路径下生成实现特定操作的任务。

### unflatten

生成打包参数的任务，将多个参数打包至一个字典中输出至全局作用域。

!!! example
    ```python
    # example.py

    unflatten('a', 'b', name='test_unflatten')
    ```

    ```js
    // example.json

    {
        "tasks": [{
            'reference': 'example.TestUnflatten',
            'name': 'unflatten',
            'type': 'functor',
            'rename': {
                'obj': 'c'
            },
            'rebind': {
                'a': 'c_a',
                'b': 'c_b'
            }
        }],
        "inject": {
            "a": 0,
            "b": 0,
            "c_a": 1,
            "c_b": 1,
        },
        ...
    }
    ```

    ```js
    // storage:

    {
        "a": 0,
        "b": 0,
        "c": {
            "a": 1,
            "b": 1
        },
        "c_a": 1,
        "c_b": 1,
    }
    ```

### flatten

生成拆包参数的任务，将一个字典形式的参数拆分为多个参数加入到全局作用域。

!!! example
    ```python
    # example.py

    flatten('a', 'b', ('c', ('a', 'b')), name='test_flatten')
    ```

    ```js
    // example.json

    {
        "tasks": [
            {
                'reference': 'example.TestFlatten',
                'name': 'flatten',
                'type': 'functor',
                'inject': {
                    'a': 0, 
                    'b': 0
                }
            }
        ],
        "inject": {
            "c": {
                "a": 1,
                "b": 1
            },
        },
        ...
    }
    ```

    ```js
    // storage: 

    {
        "a": 0,
        "b": 0,
        "c": {
            "a": 1,
            "b": 1
        },
        "c_a": 1,
        "c_b": 1,
    }
    ```
