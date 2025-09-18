#!/usr/bin/env python3
# encoding: utf-8
# @author: firstelfin
# @time: 2025/09/17 21:17:58

import os
import sys
import warnings
import argparse
from pathlib import Path
warnings.filterwarnings('ignore')
FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # project root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH

from imgDedup.utils.deduplication import SelfDeduplication, MultiDeduplication


class DedupCli:

    def __init__(
            self, src_dir: bool = True, dst_dir: bool = True, threshold: bool = True, 
            use_link: bool = True, hash_size: bool = True, save_path: bool = True,
            targets: bool = True
        ):
        self.src_dir = src_dir
        self.dst_dir = dst_dir
        self.threshold = threshold
        self.use_link = use_link
        self.hash_size = hash_size
        self.save_path = save_path
        self.targets = targets
    
    def set_args(self, parser, sub_name, desc):
        config = parser.add_parser(sub_name, help=desc)
        if self.src_dir:
            config.add_argument('src_dir', type=str, help='waitting for deduplication directory.')
        if self.dst_dir:
            config.add_argument('dst_dir', type=str, help='deduplication result directory.')
        if self.targets:
            config.add_argument('targets', type=str, nargs='+', help='target images for multi deduplication.')
        if self.threshold:
            config.add_argument('--threshold', type=int, help='threshold for phash distance.')
        if self.use_link:
            config.add_argument('--use_link', action='store_true', help='keep the first image in the group.')
        if self.hash_size:
            config.add_argument('--hash_size', type=int, default=8, help='hash size for phash algorithm.')
        if self.save_path:
            config.add_argument('--save_path', type=str, help='save the deduplication result to json file.')
        

# 开始设置命令行工具
def set_args():
    dedup_image_parser = argparse.ArgumentParser(
        description='Image Deduplication Tools',
        epilog='Enjoy the program! ',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    dedup_image_parser.add_argument('-s', '--sub', help='Subcommand to run')
    sub_command_parser = dedup_image_parser.add_subparsers(dest="sub", title="subcommands")
    DedupCli(targets=False).set_args(sub_command_parser, "self", "Self Deduplication")
    DedupCli().set_args(sub_command_parser, "multi", "Multi Deduplication")
    args = dedup_image_parser.parse_args()
    return args


def dedupImgCli():
    print("Welcome to Image Deduplication Tools!")
    args = set_args()
    if args.sub == "self":
        src_dir, dst_dir = args.src_dir, args.dst_dir
        threshold = args.threshold
        use_link = args.use_link
        hash_size = args.hash_size
        save_path = args.save_path if args.save_path else None
        self_dedup = SelfDeduplication(
            src_dir=Path(src_dir),
            dst_dir=Path(dst_dir),
            threshold=threshold,
            use_link=use_link,
            hash_size=hash_size
        )
        self_dedup(save_json_path=save_path)
    elif args.sub == "multi":
        src_dir, dst_dir = args.src_dir, args.dst_dir
        threshold = args.threshold
        use_link = args.use_link
        hash_size = args.hash_size
        save_path = args.save_path if args.save_path else None
        targets = args.targets
        multi_dedup = MultiDeduplication(
            src_dir=Path(src_dir),
            dst_dir=Path(dst_dir),
            threshold=threshold,
            use_link=use_link,
            hash_size=hash_size,
            targets=[Path(target) for target in targets]
        )
        multi_dedup(save_json_path=save_path)
    else:
        print("Invalid subcommand")
