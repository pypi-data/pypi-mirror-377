# ImageDeduplication

图像去重
> 项目地址：https://github.com/firstelfin/ImageDeduplication
> PYPI地址：https://pypi.org/project/imgDedup/

## 自定义去重数据HashCode

数据类，包含了success、value（phash的hex值）、error、img_path属性。集成了`__sub__`、`__repr__`、`__bool__`、`to_dict`方法。这是去重的基本数据结构。

## 去重核心算法-phash

> 代码路径：`imgDedup/tools/imageFingerprint.py`

imageFingerprint:get_phash 基于`imagehash.phash`实现了感知哈希算法，计算图像的指纹。函数的输入可以是图像路径，也可以是图像ndarray。

## 去重管线1--单个数据集去重

> 代码路径：`imgDedup/utils/deduplication.py`

`deduplication:SelfDeduplication` 类实现了单个数据集的去重。去重逻辑是并发加载每个图片的HashCode, 然后初始化一个保存的空列表，循环这些HashCode，如果HashCode与列表中的HashCode都不相似，则将此HashCode加入列表。最后返回列表中的HashCode。

**使用案例：**

```python
>>> sd = SelfDeduplication(
...     src_dir=Path(f"xxxx"),
...     dst_dir=Path(f"xxxxx"),
...     use_link=True,
...     threshold=5,
...     hash_size=16
... )
>>> sd(save_json_path=Path(f"xxx/dedup测试/status/deduplication_record.json"))
```

## 去重管线2--多个数据集去重

> 代码路径：`imgDedup/utils/deduplication.py`

`deduplication:CrossDatasetDeduplication` 类实现了多个数据集的去重。去重逻辑是并发加载每个数据集的图片的HashCode, 然后初始化一个保存的空列表，循环这些HashCode，如果HashCode与列表中的HashCode都不相似，则将此HashCode加入列表。最后返回列表中的HashCode。

**使用案例：**

```python
>>> mdl = MultiDeduplication(
...     src_dir=Path("xxx/xxxx_deduplication_record.json"),
...     dst_dir=Path("xxxxx/images"),
...     targets=[
...         Path("xxxxxx/images"),
...         Path("aaaaaa/images"),
...         Path("ssssss/images"),
...         Path("wwwwww/images"),
...         Path("ffffff/xxxxxx_deduplication_record.json"),
...         Path("ccccccc/eeeeee_deduplication_record.json"),
...     ],
...     threshold=26,
...     use_link=False,
...     hash_size=16
... )
... mdl(save_json_path=Path("xxxss--202508_deduplication_record.json"))
```

## Install

源码安装：

```shell
>>> git clone https://github.com/firstelfin/ImageDeduplication.git
>>> cd &&pip install .
```

通过PYPI安装：

```shell
>>> pip install imgDedup
```
