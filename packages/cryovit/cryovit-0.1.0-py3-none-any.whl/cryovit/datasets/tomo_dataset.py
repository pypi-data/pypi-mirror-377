"""Dataset class for loading DINOv2 features for CryoVIT models."""

from pathlib import Path
from typing import Any

import h5py
import numpy as np
import pandas as pd
from torch.utils.data import Dataset

from cryovit.config import tomogram_exts
from cryovit.types import TomogramData


class TomoDataset(Dataset):
    """A dataset class for handling and preprocessing tomographic data for CryoVIT models."""

    def __init__(
        self,
        records: pd.DataFrame | None,
        input_key: str,
        label_key: str,
        split_key: str,
        data_root: Path,
        aux_keys: list[str] | None = None,
        train: bool = False,
        predict: bool = False,
    ) -> None:
        """Creates a new TomoDataset object.

        Args:
            records (pd.DataFrame): A DataFrame containing records of tomograms.
            input_key (str): The key in the HDF5 file to access input features.
            label_key (str): The key in the HDF5 file to access labels.
            data_root (Path): The root directory where the tomograms are stored.
            train (bool): Flag to determine if the dataset is for training (enables transformations).
            aux_keys (list[str]): Additional keys for auxiliary data to load from the HDF5 files.
        """
        if aux_keys is None:
            aux_keys = []
        self.records = self._read_records(records)
        self.input_key = input_key
        self.label_key = label_key
        self.split_key = split_key
        self.aux_keys = aux_keys
        self.data_root = (
            data_root if isinstance(data_root, Path) else Path(data_root)
        )
        self.train = train
        self.predict = predict

    def __len__(self) -> int:
        """Returns the total number of tomograms in the dataset."""
        return len(self.records)

    def __getitem__(self, idx: int) -> TomogramData:  # type: ignore
        """Retrieves a single item from the dataset.

        Args:
            idx (int): The index of the item.

        Returns:
            record (dict[str, Any]): A dictionary containing the loaded data and labels.

        Raises:
            IndexError: If index is out of the range of the dataset.
        """
        if idx >= len(self):
            raise IndexError

        record = self.records.iloc[idx]
        assert isinstance(record, pd.Series)
        data = self._load_tomogram(record)

        if self.train:
            self._random_crop(data)

        return TomogramData(
            sample=record["sample"],
            tomo_name=record["tomo_name"],
            split_id=data.get("split_id", None),
            data=data["input"],
            label=data["label"],
            aux_data={key: data[key] for key in self.aux_keys if key in data},
        )  # type: ignore

    def _read_records(self, records: pd.DataFrame | None) -> pd.DataFrame:
        if records is not None:
            return records

        # Should only run for prediction datasets with no split file
        records_dict = {
            "sample": [],
            "tomo_name": [],
        }
        # Read samples and files from directory
        samples = [f.name for f in self.data_root.glob("*") if f.is_dir()]
        for sample in samples:
            tomo_dir = self.data_root / sample
            for tomo_name in [
                t.name for t in tomo_dir.glob("*") if t.suffix in tomogram_exts
            ]:
                records_dict["sample"].append(sample)
                records_dict["tomo_name"].append(tomo_name)

        records_df = pd.DataFrame(records_dict)
        return records_df

    def _load_tomogram(self, record: pd.Series) -> dict[str, Any]:
        """Loads a single tomogram based on the record information.

        Args:
            record (pd.Series): A series containing the sample and tomogram names.

        Returns:
            data (dict[str, Any]): A dictionary with input data, label, and any auxiliary data.
        """
        tomo_path = self.data_root / record["sample"] / record["tomo_name"]

        # sample, tomo_name, split_id, input, label

        data = {"sample": record["sample"], "tomo_name": record["tomo_name"]}
        if self.split_key in record.index:
            data["split_id"] = record[self.split_key]

        with h5py.File(tomo_path) as fh:
            data["input"] = fh[self.input_key][()]  # type: ignore
            if data["input"].dtype == np.uint8:  # type: ignore
                data["input"] = data["input"].astype(np.float32) / 255.0  # type: ignore
            if len(data["input"].shape) == 3:  # type: ignore
                data["input"] = data["input"][np.newaxis, ...]  # type: ignore # add channel dimension
            data["label"] = fh["labels"][self.label_key][()]  # type: ignore
            data |= {key: fh[key][()] for key in self.aux_keys if key in fh}  # type: ignore

        return data

    def _random_crop(self, data: dict[str, Any]) -> None:
        """Applies a random crop to the input data in the record dictionary.

        Args:
            record (dict[str, Any]): The record dictionary containing 'input' and 'label' data.
        """
        max_depth = 128
        side = 32 if self.input_key == "dino_features" else 512
        d, h, w = data["input"].shape[-3:]
        x, y, z = min(d, max_depth), side, side

        if (d, h, w) == (x, y, z):
            return  # nothing to be done

        delta_d = d - x + 1
        delta_h = h - y + 1
        delta_w = w - z + 1

        di = np.random.choice(delta_d) if delta_d > 0 else 0
        hi = np.random.choice(delta_h) if delta_h > 0 else 0
        wi = np.random.choice(delta_w) if delta_w > 0 else 0

        data["input"] = data["input"][
            ..., di : di + x, hi : hi + y, wi : wi + z
        ]

        if self.input_key == "dino_features":
            hi, wi, y, z = 16 * np.array([hi, wi, y, z])

        data["label"] = data["label"][di : di + x, hi : hi + y, wi : wi + z]
