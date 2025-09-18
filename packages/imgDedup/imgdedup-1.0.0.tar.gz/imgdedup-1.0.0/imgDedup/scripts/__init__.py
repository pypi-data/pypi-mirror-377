#!/usr/bin/env python3
# encoding: utf-8
# @author: firstelfin
# @time: 2025/09/17 22:20:48

import os
import sys
import warnings
from pathlib import Path
warnings.filterwarnings('ignore')
FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # project root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
