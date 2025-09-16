# -*- coding: utf-8 -*-

import os
import os.path as path
import hashlib
import requests
import logging
import json
import http.client
import socket
import random

import xarray as xr
import numpy as np
import pandas as pd
from wxbtool.data.path import DataPathManager

import msgpack
import msgpack_numpy as m
from wxbtool.nn.setting import Setting

m.patch()

from torch.utils.data import Dataset, DataLoader, Sampler  # noqa: E402


logger = logging.getLogger()


class WindowArray(type(np.zeros(0, dtype=np.float32))):
    def __new__(subtype, orig, shift=0, step=1):
        shape = [orig.shape[_] for _ in range(len(orig.shape))]
        self = np.ndarray.__new__(
            subtype, shape, dtype=np.float32, buffer=orig.tobytes()
        )[shift::step]
        return self


class WxDataset(Dataset):
    def __init__(
        self,
        root=None,
        resolution=None,
        years=None,
        vars=None,
        levels=None,
        step=None,
        input_span=None,
        pred_shift=None,
        pred_span=None,
        setting=None,
    ):
        self.setting = setting if setting is not None else Setting()

        # Use values from setting if not explicitly provided
        self.root = root if root is not None else self.setting.root
        self.resolution = (
            resolution if resolution is not None else self.setting.resolution
        )
        self.input_span = (
            input_span if input_span is not None else self.setting.input_span
        )
        self.step = step if step is not None else self.setting.step
        self.pred_shift = (
            pred_shift if pred_shift is not None else self.setting.pred_shift
        )
        self.pred_span = pred_span if pred_span is not None else self.setting.pred_span
        self.years = years if years is not None else self.setting.years_train
        self.vars = vars if vars is not None else self.setting.vars
        self.levels = levels if levels is not None else self.setting.levels
        self.inputs = {}
        self.targets = {}
        self.shapes = {
            "data": {},
        }
        self.accumulated = {}

        if resolution == "5.625deg":
            self.height = 13
            self.width = 32
            self.length = 64

        code = "%s:%s:%s:%s:%s:%s:%s:%s:%s:%s" % (
            self.resolution,
            self.years,
            self.vars,
            self.levels,
            self.step,
            self.input_span,
            self.pred_shift,
            self.pred_span,
            self.setting.granularity,
            self.setting.data_path_format,
        )
        hashstr = hashlib.md5(code.encode("utf-8")).hexdigest()
        self.hashcode = hashstr

        dumpdir = path.abspath(
            "%s/.cache/%s" % (self.root, hashstr)
        )  # every time has to reload the .cache file
        # if not path.exists(dumpdir):
        os.makedirs(dumpdir, exist_ok=True)
        self.load(dumpdir)

        self.memmap(dumpdir)

    def load(self, dumpdir):
        import wxbtool.data.variables as v  # noqa: E402

        # Determine available levels only if any of the requested variables are 3D
        all_levels = []
        # Identify 3D variables present in the current dataset variables (self.vars)
        var3d_list = [var for var in self.vars if var in v.vars3d]
        if var3d_list:
            first3d = var3d_list[0]
            try:
                var3d_path = os.path.join(self.root, first3d)
                any_file = os.listdir(var3d_path)[0]
                sample_data = xr.open_dataarray(f"{var3d_path}/{any_file}")
                all_levels = sample_data.level.values.tolist()
            except (FileNotFoundError, IndexError, AttributeError) as e:
                logger.error(
                    f"Failed to read levels from 3D variable '{first3d}'. "
                    f"Please check data integrity and paths. Original error: {e}"
                )
                raise ValueError(
                    f"Configuration requires 3D variables in dataset (found {var3d_list}), "
                    f"but failed to load level info from '{first3d}'."
                )

        # Find indices of requested levels in the available levels
        levels_selector = []
        for lvl in self.levels:
            try:
                levels_selector.append(all_levels.index(float(lvl)))
            except ValueError:
                logger.error(f"Level {lvl} not found in available levels: {all_levels}")
                raise ValueError(
                    f"Level {lvl} not found in available levels: {all_levels}"
                )

        selector = np.array(levels_selector, dtype=np.int64)

        size = 0
        lastvar = None

        # Construct a date range covering selected years according to granularity
        min_year, max_year = min(self.years), max(self.years)
        start_date = f"{min_year}-01-01"
        end_date = f"{max_year}-12-31"
        freq_map = {
            "yearly": "YS",
            "quarterly": "QS",
            "monthly": "MS",
            "weekly": "W-MON",
            "daily": "D",
            "hourly": "H",
        }
        freq = freq_map.get(self.setting.granularity, "D")
        if self.setting.granularity not in freq_map:
            logger.warning(
                f"Unknown granularity '{self.setting.granularity}', defaulting to daily frequency 'D'"
            )
        date_range = pd.date_range(start=start_date, end=end_date, freq=freq)

        for var in self.vars:
            file_paths = DataPathManager.get_file_paths(
                self.root,
                var,
                self.resolution,
                self.setting.data_path_format,
                date_range,
            )
            for data_path in file_paths:
                if not os.path.exists(data_path):
                    logger.debug(f"Missing data file skipped: {data_path}")
                    continue

                if var in v.vars3d:
                    length = self.load_3ddata(
                        data_path, var, selector, self.accumulated
                    )
                elif var in v.vars2d:
                    length = self.load_2ddata(data_path, var, self.accumulated)
                else:
                    raise ValueError(f"variable {var} does not supported!")
                size += length

            if lastvar and lastvar != var:
                self.inputs[lastvar] = WindowArray(
                    self.accumulated[lastvar],
                    shift=self.input_span * self.step,
                    step=self.step,
                )
                self.targets[lastvar] = WindowArray(
                    self.accumulated[lastvar],
                    shift=self.pred_span * self.step + self.pred_shift,
                    step=self.step,
                )
                self.dump_var(dumpdir, lastvar)

            lastvar = var

        if lastvar:
            self.inputs[lastvar] = WindowArray(
                self.accumulated[lastvar],
                shift=self.input_span * self.step,
                step=self.step,
            )
            self.targets[lastvar] = WindowArray(
                self.accumulated[lastvar],
                shift=self.pred_span * self.step + self.pred_shift,
                step=self.step,
            )
            self.dump_var(dumpdir, lastvar)

        if not self.accumulated:
            logger.error("No data accumulated. Please check the data loading process.")
            raise ValueError(
                "No data accumulated. Ensure that data is correctly loaded and accumulated."
            )

        lengths = {var: acc.shape[0] for var, acc in self.accumulated.items()}
        unique_lengths = set(lengths.values())

        if len(unique_lengths) != 1:
            max_length = max(unique_lengths)

            inconsistent_vars = {
                var: length for var, length in lengths.items() if length != max_length
            }

            if inconsistent_vars:
                for var, length in inconsistent_vars.items():
                    logger.error(
                        f"Variable {var} has inconsistent length {length}. Expected length: {max_length}."
                    )

                raise ValueError(
                    "Inconsistent data lengths across variables detected. Please check the data loading process."
                )
        else:
            logger.info("All variables have consistent data lengths.")

        with open("%s/shapes.json" % dumpdir, mode="w") as fp:
            json.dump(self.shapes, fp)

        self.size = size // len(self.vars)
        logger.info("total %s items loaded!", self.size)

        for var in list(self.accumulated.keys()):
            del self.accumulated[var]

    def load_2ddata(self, data_path, var, accumulated):
        import wxbtool.data.variables as v  # noqa: E402

        with xr.open_dataset(data_path) as ds:
            ds = ds.transpose("time", "lat", "lon")
            if var not in accumulated:
                accumulated[var] = np.array(ds[v.codes[var]].data, dtype=np.float32)
            else:
                accumulated[var] = np.concatenate(
                    [
                        accumulated[var],
                        np.array(ds[v.codes[var]].data, dtype=np.float32),
                    ],
                    axis=0,
                )
            logger.info(
                "%s[%s]: %s",
                var,
                os.path.basename(data_path),
                str(accumulated[var].shape),
            )

        return accumulated[var].shape[0]

    def load_3ddata(self, data_path, var, selector, accumulated):
        import wxbtool.data.variables as v  # noqa: E402

        with xr.open_dataset(data_path) as ds:
            ds = ds.transpose("time", "level", "lat", "lon")
            if var not in accumulated:
                accumulated[var] = np.array(ds[v.codes[var]].data, dtype=np.float32)[
                    :, selector, :, :
                ]
            else:
                accumulated[var] = np.concatenate(
                    [
                        accumulated[var],
                        np.array(ds[v.codes[var]].data, dtype=np.float32)[
                            :, selector, :, :
                        ],
                    ],
                    axis=0,
                )
            logger.info(
                "%s[%s]: %s",
                var,
                os.path.basename(data_path),
                str(accumulated[var].shape),
            )

        return accumulated[var].shape[0]

    def dump_var(self, dumpdir, var):
        file_dump = "%s/%s.npy" % (dumpdir, var)
        self.shapes["data"][var] = self.accumulated[var].shape
        np.save(file_dump, self.accumulated[var])

    def memmap(self, dumpdir):
        import wxbtool.data.variables as v  # noqa: E402

        with open("%s/shapes.json" % dumpdir) as fp:
            shapes = json.load(fp)

        for var in self.vars:
            file_dump = "%s/%s.npy" % (dumpdir, var)

            # load data from memmap, and skip the first shift elements of mmap data header
            shape = shapes["data"][var]
            total_size = np.prod(shape)
            data = np.memmap(file_dump, dtype=np.float32, mode="r")
            shift = data.shape[0] - total_size
            self.accumulated[var] = np.reshape(data[shift:], shape)

            if var in v.vars2d or var in v.vars3d:
                self.inputs[var] = self.accumulated[var]
                self.targets[var] = self.accumulated[var]

    def __len__(self):
        length = (
            self.accumulated[self.vars[0]].shape[0]
            - (self.input_span - 1) * self.step
            - (self.pred_span - 1) * self.step
            - self.pred_shift
        )
        logger.info(f"Dataset length: {length}")
        return length

    def __getitem__(self, item):
        import wxbtool.data.variables as v  # noqa: E402

        inputs, targets = {}, {}
        for var in self.vars:
            if var in v.vars2d or var in v.vars3d:
                input_slice = self.inputs[var][item :: self.step][: self.input_span]
                target_slice = self.targets[var][
                    item
                    + self.step * (self.input_span - 1)
                    + self.pred_shift :: self.step
                ][: self.pred_span]
                inputs[var] = input_slice
                targets[var] = target_slice
                if input_slice.shape[0] != self.input_span:
                    logger.warning(
                        f"Input slice for var {var} at index {item} has shape {input_slice.shape}"
                    )
                if target_slice.shape[0] != self.pred_span:
                    logger.warning(
                        f"Target slice for var {var} at index {item} has shape {target_slice.shape}"
                    )

        # In RNN mode, return combined inputs and targets as 'all'
        # if hasattr(self, 'rnn_mode') and self.rnn_mode:
        #     all_data = {}
        #     for var in self.vars:
        #         if var in inputs and var in targets:
        #             # Combine inputs and targets for each variable
        #             all_data[var] = np.concatenate([inputs[var], targets[var]], axis=0)
        #     return all_data, all_data, item

        return inputs, targets, item


class WxDatasetClient(Dataset):
    def __init__(
        self,
        url,
        phase,
        resolution=None,
        years=None,
        vars=None,
        levels=None,
        step=None,
        input_span=None,
        pred_shift=None,
        pred_span=None,
        setting=None,
    ):
        self.url = url
        self.phase = phase
        self.setting = setting if setting is not None else Setting()

        # Use values from setting if not explicitly provided
        self.resolution = (
            resolution if resolution is not None else self.setting.resolution
        )
        self.step = step if step is not None else self.setting.step
        self.input_span = (
            input_span if input_span is not None else self.setting.input_span
        )
        self.pred_shift = (
            pred_shift if pred_shift is not None else self.setting.pred_shift
        )
        self.pred_span = pred_span if pred_span is not None else self.setting.pred_span
        self.years = years if years is not None else self.setting.years_train
        self.vars = vars if vars is not None else self.setting.vars
        self.levels = levels if levels is not None else self.setting.levels

        code = "%s:%s:%s:%s:%s:%s:%s:%s" % (
            self.resolution,
            self.years,
            self.vars,
            self.levels,
            self.step,
            self.input_span,
            self.pred_shift,
            self.pred_span,
        )
        self.hashcode = hashlib.md5(code.encode("utf-8")).hexdigest()

        if self.url.startswith("unix:"):
            self.url = self.url.replace("/", "%2F")
            self.url = self.url.replace("unix:", "http+unix://")

    def __len__(self):
        url = "%s/%s/%s" % (self.url, self.hashcode, self.phase)
        if self.url.startswith("http+unix://"):
            sock_path = self.url.replace("http+unix://", "").replace("%2F", "/")
            endpoint = f"{self.hashcode}/{self.phase}"
            sock_path = "/" + sock_path
            conn = http.client.HTTPConnection("localhost")
            conn.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            conn.sock.connect(sock_path)
            conn.request(
                "GET",
                "/" + endpoint,
                headers={"Host": "localhost", "Connection": "close"},
            )
            r = conn.getresponse()
            if r.status != 200:
                raise Exception("http error %s: %s" % (r.status, r.reason))
            data = msgpack.loads(r.read())
        else:
            r = requests.get(url)
            if r.status_code != 200:
                raise Exception("http error %s: %s" % (r.status_code, r.text))
            data = msgpack.loads(r.content)

        return data["size"]

    def __getitem__(self, item):
        url = "%s/%s/%s/%d" % (self.url, self.hashcode, self.phase, item)
        if self.url.startswith("http+unix://"):
            sock_path = self.url.replace("http+unix://", "").replace("%2F", "/")
            endpoint = f"{self.hashcode}/{self.phase}/{item}"
            sock_path = "/" + sock_path
            conn = http.client.HTTPConnection("localhost")
            conn.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            conn.sock.connect(sock_path)
            conn.request(
                "GET",
                "/" + endpoint,
                headers={"Host": "localhost", "Connection": "close"},
            )
            r = conn.getresponse()
            if r.status != 200:
                raise Exception("http error %s: %s" % (r.status, r.reason))
            data = msgpack.loads(r.read())
        else:
            r = requests.get(url)
            if r.status_code != 200:
                raise Exception("http error %s: %s" % (r.status_code, r.text))
            data = msgpack.loads(r.content)

        for key, val in data.items():
            if key != "inputs" and key != "targets":
                continue
            for var, blk in val.items():
                val[var] = np.array(np.copy(blk), dtype=np.float32)

        # In RNN mode, return combined inputs and targets as 'all'
        # if hasattr(self, 'rnn_mode') and self.rnn_mode:
        #     all_data = {}
        #     for var in data["inputs"].keys():
        #         if var in data["inputs"] and var in data["targets"]:
        #             # Combine inputs and targets for each variable
        #             all_data[var] = np.concatenate([data["inputs"][var], data["targets"][var]], axis=0)
        #     return all_data, all_data, item

        return data["inputs"], data["targets"], item


class EnsembleBatchSampler(Sampler):
    def __init__(self, dataset, ensemble_size, shuffle=True):
        super().__init__()
        self.dataset = dataset
        self.ensemble_size = ensemble_size
        self.shuffle = shuffle
        self.indices = list(range(len(dataset)))
        if self.shuffle:
            random.shuffle(self.indices)

    def __iter__(self):
        for idx in self.indices:
            for _ in range(self.ensemble_size):
                yield idx

    def __len__(self):
        return len(self.dataset) * self.ensemble_size


def ensemble_loader(dataset, ensemble_size, shuffle=True):
    sampler = EnsembleBatchSampler(dataset, ensemble_size, shuffle)
    return DataLoader(
        dataset,
        batch_size=ensemble_size,
        sampler=sampler,
        num_workers=0,
        pin_memory=True,
    )
