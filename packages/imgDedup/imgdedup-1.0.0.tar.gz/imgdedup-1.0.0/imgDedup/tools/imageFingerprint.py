#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   imageFingerprint.py
@Time    :   2025/09/09 14:44:00
@Author  :   firstElfin 
@Version :   0.0
@Desc    :   图像指纹算法
'''

import imagehash
from PIL import Image
from pathlib import Path
from imagehash import ImageHash
from dataclasses import dataclass, asdict


@dataclass
class HashCode:
    success: bool
    value: ImageHash | None = None
    error: str | None = None
    img_path: Path | None = None

    def __sub__(self, other: 'HashCode') -> int:
        """重载减法：计算两个哈希的汉明距离"""
        if not isinstance(other, HashCode):
            return NotImplemented
        if self.value is None or other.value is None:
            raise ValueError("HashCode object is None")
        return self.value - other.value
    
    def __repr__(self):
        return str(self.value)
    
    def __bool__(self) -> bool:
        """使对象支持 if 判断: success 为 True 时对象为真"""
        return self.success
    
    def to_dict(self) -> dict:
        """将 HashCode 对象转换为字典"""
        if not self.success:
            return dict()
        elif self.img_path:
            return dict(img_path=str(self.img_path), value=str(self.value))
        else:
            return dict(value=str(self.value))


def load_hash_code(hash_code: dict) -> HashCode:
    """从字典中加载 HashCode 对象

    :param dict hash_code: 字典
    :return HashCode: HashCode 对象
    """

    if not hash_code:
        return HashCode(False)
    return HashCode(True, value=ImageHash(hash_code['value']), img_path=hash_code.get('img_path'))


def get_phash(image: str | Path | Image.Image, hash_size: int = 8) -> HashCode:
    """感知哈希算法, string对象长度为 hash_size ** 2 / 4

    :param str | Path | Image.Image image: 图像路径或图像对象
    :param int hash_size: 哈希长度
    :return: 图像的感知哈希值
    :rtype: HashCode

    Example::

        >>> img_path = "20250903-184723.png"
        >>> src_img = Image.open(img_path)
        >>> phash1 = get_phash(src_img, hash_size=16)
        >>> phash2 = get_phash(img_path, hash_size=16)
        >>> print(phash1)
        >>> print(phash2)
    """

    img_path = None
    try:
        if isinstance(image, (str, Path)):
            img_path = Path(image)
            pil_image = Image.open(image).convert('RGB')
        elif isinstance(image, Image.Image):
            pil_image = image.convert('RGB')
        else:
            raise TypeError("image must be str, Path or Image.Image")
        pil_image.load()
    except Exception as e:
        return HashCode(False, error=str(e), img_path=img_path)
    hash_code = imagehash.phash(pil_image, hash_size=hash_size)
    return HashCode(True, value=hash_code, img_path=img_path)
