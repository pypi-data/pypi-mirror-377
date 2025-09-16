import os
import sys

from tsapix.utils import read_yaml_file, save_as_yaml, update_yaml
from tsapix.utils import save_npcube, read_npcube
from tsapix.utils import initiate_logger
from tsapix.utils import icloud_froot, env_db_root, cube_warehouse_root, code_univ_save_path, _log_froot

import requests
import json
import numpy as np
import pandas as pd
import multitasking as _multitasking
from tqdm import tqdm
import re
import pandas_market_calendars as mcal

import pandas as _pd
import numpy as _np
import sys as _sys

def empty_df(index=None, cols=[], index_name=None):
    if index is None:
        index = []
    empty = _pd.DataFrame(index=index, data={c:_np.nan for c in cols})
    if index_name:
        empty.index.name = index_name
    return empty


class ProgressBar:
    def __init__(self, iterations, text='completed'):
        self.text = text
        self.iterations = iterations
        self.prog_bar = '[]'
        self.fill_char = '*'
        self.width = 50
        self.__update_amount(0)
        self.elapsed = 1

    def completed(self):
        if self.elapsed > self.iterations:
            self.elapsed = self.iterations
        self.update_iteration(1)
        print('\r' + str(self), end='', file=_sys.stderr)
        _sys.stderr.flush()
        print("", file=_sys.stderr)

    def animate(self, iteration=None):
        if iteration is None:
            self.elapsed += 1
            iteration = self.elapsed
        else:
            self.elapsed += iteration

        print('\r' + str(self), end='', file=_sys.stderr)
        _sys.stderr.flush()
        self.update_iteration()

    def update_iteration(self, val=None):
        val = val if val is not None else self.elapsed / float(self.iterations)
        self.__update_amount(val * 100.0)
        self.prog_bar += f"  {self.elapsed} of {self.iterations} {self.text}"

    def __update_amount(self, new_amount):
        percent_done = int(round((new_amount / 100.0) * 100.0))
        all_full = self.width - 2
        num_hashes = int(round((percent_done / 100.0) * all_full))
        self.prog_bar = '[' + self.fill_char * num_hashes + ' ' * (all_full - num_hashes) + ']'
        pct_place = (len(self.prog_bar) // 2) - len(str(percent_done))
        pct_string = f'{percent_done}%%'
        self.prog_bar = self.prog_bar[0:pct_place] + (pct_string + self.prog_bar[pct_place + len(pct_string):])

    def __str__(self):
        return str(self.prog_bar)

