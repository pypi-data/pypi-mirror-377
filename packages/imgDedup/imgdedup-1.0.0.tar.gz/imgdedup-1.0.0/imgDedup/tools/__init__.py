#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   __init__.py
@Time    :   2025/09/09 15:23:42
@Author  :   firstElfin 
@Version :   0.0
@Desc    :   None
'''

from imgDedup.tools.imageFingerprint import get_phash, HashCode


__all__ = ['get_phash']
__call__ = ['get_phash', 'HashCode', 'load_hash_code']


def load_hash_code(hash_code_dict: dict) -> HashCode: ...
