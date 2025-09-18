#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   deduplication.py
@Time    :   2025/09/09 17:31:48
@Author  :   firstElfin 
@Version :   1.0
@Desc    :   去重核心管线
'''

import os
import time
import json
import shutil
import imagehash
import numpy as np
from pathlib import Path
from tqdm import tqdm
from loguru import logger
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from imgDedup.tools import get_phash, HashCode


IMG_EXT = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
cpu_count = os.cpu_count()
cpu_count = cpu_count if cpu_count is not None else 4
MAX_WORKERS = max(4, cpu_count // 2)


class DedupPipelineBase:

    @classmethod
    def save_dedup_img(cls, saved_list: list[HashCode], dst_dir: Path, use_link: bool = False):
        """保存去重后的图片

        :param list[HashCode] saved_list: 保存的HashCode列表
        :param Path dst_dir: 保存目录
        :param bool use_link: 是否使用软链接, 默认为False
        """
        dst_dir.mkdir(exist_ok=True, parents=True)

        def con_save(hash_code: HashCode):
            if hash_code.img_path is None:
                raise ValueError("HashCode object has no img_path attribute.")
            img_path = Path(hash_code.img_path)  # type: Path
            dst_path = dst_dir / img_path.name
            if dst_path.exists():
                # 文件存在，添加时间戳信息
                dst_path = dst_dir / f"{img_path.stem}_{int(time.time() * 1000)}{img_path.suffix}"
            # 复制文件
            dst_path.symlink_to(img_path) if use_link else shutil.copy2(img_path, dst_path)
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            tql_res = [executor.submit(con_save, hash_code) for hash_code in saved_list]
            exec_bar = tqdm(
                as_completed(tql_res), total=len(tql_res), desc='\033[94m\033[1mSaving Images\033[0m', 
                unit='img', colour="#CD8500", smoothing=0.3, dynamic_ncols=False
            )
            for tpl_res in exec_bar:
                tpl_res.result()
    
    @classmethod
    def save_dedup_record(cls, dedup_list: list[HashCode], save_json_path: Path) -> Path:
        """保存去重记录到json文件

        :param list[HashCode] dedup_list: 去重后的HashCode列表
        :param Path save_json_path: 保存路径
        :return: 保存路径
        """
        if save_json_path.exists():
            save_json_path = save_json_path.parent / f"{save_json_path.stem}_{int(time.time() * 1000)}{save_json_path.suffix}"
        record_list = [hash_code.to_dict() for hash_code in dedup_list]
        with open(save_json_path, 'w+', encoding='utf-8') as f:
            json.dump(record_list, f, indent=4, ensure_ascii=False)
        return save_json_path

    @classmethod
    def load_hash_codes(cls, img_files: list[Path], hash_size: int = 8) -> list[HashCode]:
        """使用多线程加载图片的HashCode对象

        :param list[Path] img_files: 图片文件列表
        :param int hash_size: 哈希值长度, 默认为8, hex字符串长度计算公式: hash_size ** 2 / 4
        :return list[HashCode]: HashCode列表(排除错误对象)
        """

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            tpl_res = [executor.submit(get_phash, img_file, hash_size) for img_file in img_files]
            exec_bar = tqdm(
                as_completed(tpl_res), total=len(tpl_res), desc='\033[94m\033[1mLoading HashCodes\033[0m', 
                unit='img', colour="#CD8500", smoothing=0.3, dynamic_ncols=False
            )
            res_list = []
            for tpl_res in exec_bar:
                res_list.append(tpl_res.result())
                
        return [hash_code for hash_code in res_list if hash_code]

    @classmethod
    def load_items(cls, src_dir: Path, hash_size: int = 8) -> list[HashCode]:
        """加载待处理的图片文件或HashCode记录

        :param Path src_dir: 待处理数据集目录或者HashCode记录文件路径
        :param int hash_size: 哈希值长度, 默认为8, hex字符串长度计算公式: hash_size ** 2 / 4
        :return list[HashCode]: HashCode列表
        """

        if src_dir.is_file() and src_dir.suffix.lower() == ".json":
            with open(src_dir, 'r', encoding='utf-8') as f:
                items = json.load(f)
            assert items is not None, "Invalid json file."
            return [HashCode(True, value=imagehash.hex_to_hash(item['value']), img_path=Path(item['img_path'])) for item in items]
        else:
            items = [img_file for img_file in src_dir.rglob('*') if img_file.is_file() and img_file.suffix.lower() in IMG_EXT]
            hash_codes = cls.load_hash_codes(items, hash_size=hash_size)
            return hash_codes

class SelfDeduplication(DedupPipelineBase):
    """数据集内部去重

    :param src_dir: 原始数据集目录或HashCode记录文件路径
    :param dst_dir: 去重后数据集目录
    :param threshold: 相似度阈值, 默认为5
    :param use_link: 是否使用软链接, 默认为False
    :param hash_size: 哈希值长度, 默认为8, hex字符串长度计算公式: hash_size ** 2 / 4

    Example::

        >>> sd = SelfDeduplication(
        ...     src_dir=Path(f"xxxx"),
        ...     dst_dir=Path(f"xxxxx"),
        ...     use_link=True,
        ...     threshold=5,
        ...     hash_size=16
        ... )
        >>> sd(save_json_path=Path(f"xxx/dedup测试/status/deduplication_record.json"))
    """

    def __init__(self, src_dir: Path, dst_dir: Path, threshold: float | int = 5, use_link: bool = False, hash_size: int = 8):
        super().__init__()
        self.src_dir = src_dir
        self.dst_dir = dst_dir
        self.threshold = threshold
        self.use_link = use_link
        self.img_list = []
        self.hash_size = hash_size
        self.saved_list = []  # type: list[HashCode]
        self.error_count = 0
        self.dup_count = 0
    
    @staticmethod
    def set_bar(items):
        bar = tqdm(
            items, total=len(items), desc='\033[94m\033[1mDeduplication\033[0m', unit='img',
            colour="#CD8500", smoothing=0.3, dynamic_ncols=False
        )
        return bar
    
    def __call__(self, save_json_path: Path | None = None, *args, **kwargs):
        """执行数据集内部去重

        :param Path save_json_path: 保存去重记录的json文件路径, 默认为None, 保存到dst_dir/deduplication_record.json
        """
        
        logger.info(f"Loading images HashCodes from {self.src_dir}...")
        self.img_list = self.load_items(self.src_dir, self.hash_size)  # type: list[HashCode]
        exec_bar = self.set_bar(self.img_list)  # 配置进度条
        for hash_code in exec_bar:
            is_dup = False
            for comp_code in self.saved_list:
                if hash_code - comp_code < self.threshold:
                    self.dup_count += 1  # 去重
                    is_dup = True
                    break
            
            if not is_dup:
                self.saved_list.append(hash_code)
        exec_bar.close()

        # 保存去重结果
        logger.info(f"Total images: {len(self.img_list)}, Duplicated images: {self.dup_count}, Saving images: {len(self.saved_list)}.")
        self.save_dedup_img(self.saved_list, self.dst_dir, self.use_link)
        
        # 保存去重记录
        json_path = save_json_path or self.dst_dir / "deduplication_record.json"
        json_path.parent.mkdir(exist_ok=True, parents=True)
        save_json_path = self.save_dedup_record(self.saved_list, save_json_path=json_path)
        logger.info(f"Deduplication record saved to {save_json_path}.")


class MultiDeduplication(DedupPipelineBase):
    """多重图像去重

    :param src_dir: 待去重数据集目录或HashCode记录文件路径
    :param dst_dir: 去重后数据集目录
    :param threshold: 相似度阈值, 默认为5
    :param use_link: 是否使用软链接, 默认为False
    :param hash_size: 哈希值长度, 默认为8, hex字符串长度计算公式: hash_size ** 2 / 4
    :param targets: 已经去重的目标数据集目录列表, 元素可以是Path文件夹路径或HashCode的json文件, 默认为空

    Example::

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

    """

    def __init__(
            self, src_dir: Path, dst_dir: Path, threshold: float | int = 5, 
            use_link: bool = False, hash_size: int = 8, targets: list=[], **kwargs
        ):
        super().__init__()
        self.src_dir = src_dir
        self.dst_dir = dst_dir
        self.threshold = threshold
        self.use_link = use_link
        self.targets = targets
        self.hash_size = hash_size
        self.saved_list = []  # type: list[HashCode]
        self.error_count = 0
    
    @classmethod
    def load_targets(cls, targets: list[Path | str], hash_size: int = 8) -> list[list[HashCode]]:
        """加载已经去重的目标数据集

        :param list[Path | str] targets: json文件标识HashCode存储json文件, 其他标识已经去重的文件夹路径
        :param int hash_size: 哈希值长度, 默认为8, hex字符串长度计算公式: hash_size ** 2 / 4
        """

        res = []
        if not isinstance(targets, list):
            raise TypeError("targets must be a list of Path or str.")
        for target in targets:
            if not isinstance(target, (str, Path)):
                raise TypeError("targets must be a list of Path or str.")
            target = Path(target)

            # 从文件夹加载图像的HashCode列表
            if target.is_dir():
                target_hash_codes = cls.load_items(target, hash_size=hash_size)  # type: list[HashCode]
                res.append(target_hash_codes)
            # 从json文件加载图像的HashCode列表
            else:
                with open(target, 'r+', encoding='utf-8') as f:
                    json_list = json.load(f)
                    if json_list is None:
                        raise ValueError(f"Invalid json file: {target}.")
                res.append([
                    HashCode(
                        True, 
                        value=imagehash.hex_to_hash(json_dict['value']), 
                        img_path=Path(json_dict.get('img_path'))
                    ) for json_dict in json_list
                ])
        return res
    
    def similarity_check(self, check_hash_codes: list[HashCode], taget_hash_codes: list[HashCode]) -> list[bool]:
        """图像HashCode相似度检查

        :param list[HashCode] check_hash_codes: 待检查的HashCode列表
        :param list[HashCode] taget_hash_codes: 目标HashCode列表
        :return list[bool]: 待检查的HashCode是否与目标HashCode相似的列表
        """

        res = [False] * len(check_hash_codes)

        for i, check_hash_code in enumerate(check_hash_codes):
            for j, target_hash_code in enumerate(taget_hash_codes):
                if check_hash_code - target_hash_code < self.threshold:
                    res[i] = True
                    break
        return res
    
    def __call__(self, save_json_path: Path | None = None, *args, **kwargs):
        """执行多重图像去重

        :param Path | None save_json_path: 保存去重记录的json文件路径, defaults to None, 保存到dst_dir/deduplication_record.json
        """

        logger.info(f"Loading images HashCodes from {self.src_dir}...")
        check_hash_codes = self.load_items(self.src_dir, self.hash_size)  # type: list[HashCode]
        logger.info(f"Loading targets from {self.targets}.")
        targets_hash_lists = self.load_targets(self.targets, self.hash_size)
        status = np.array([False] * len(check_hash_codes), dtype=bool)

        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            pp_exec_res = [executor.submit(self.similarity_check, check_hash_codes, target_hash_codes) for target_hash_codes in targets_hash_lists]

            try:
                for status_res in as_completed(pp_exec_res):
                    new_status = status_res.result()
                    status |= np.array(new_status, dtype=bool)
            except Exception as e:
                logger.error(f"Error occurred when checking similarity: {e}.")
                return None
        
        self.saved_list = [hash_code for i, hash_code in enumerate(check_hash_codes) if not status[i]]
        check_num = len(check_hash_codes)
        dup_num = check_num - len(self.saved_list)

        # 保存去重结果
        logger.info(f"Total images: {check_num}, Duplicated images: {dup_num}, Saving images: {len(self.saved_list)}.")
        self.save_dedup_img(self.saved_list, self.dst_dir, self.use_link)
        
        # 保存去重记录
        json_path = save_json_path or self.dst_dir / "deduplication_record.json"
        json_path.parent.mkdir(exist_ok=True, parents=True)
        save_json_path = self.save_dedup_record(self.saved_list, save_json_path=json_path)
        logger.info(f"Deduplication record saved to {save_json_path}.")


