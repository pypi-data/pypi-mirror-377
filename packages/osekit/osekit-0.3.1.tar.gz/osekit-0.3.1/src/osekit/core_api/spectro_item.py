"""SpectroItem corresponding to a portion of a SpectroFile object."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from osekit.core_api.base_file import BaseFile
from osekit.core_api.base_item import BaseItem
from osekit.core_api.spectro_file import SpectroFile

if TYPE_CHECKING:
    from pandas import Timedelta, Timestamp
    from scipy.signal import ShortTimeFFT


class SpectroItem(BaseItem[SpectroFile]):
    """SpectroItem corresponding to a portion of a SpectroFile object."""

    def __init__(
        self,
        file: SpectroFile | None = None,
        begin: Timestamp | None = None,
        end: Timestamp | None = None,
    ) -> None:
        """Initialize a SpectroItem from a SpectroFile and begin/end timestamps.

        Parameters
        ----------
        file: osekit.data.spectro_file.SpectroFile
            The SpectroFile in which this Item belongs.
        begin: pandas.Timestamp (optional)
            The timestamp at which this item begins.
            It is defaulted to the SpectroFile begin.
        end: pandas.Timestamp (optional)
            The timestamp at which this item ends.
            It is defaulted to the SpectroFile end.

        """
        super().__init__(file, begin, end)

    @property
    def time_resolution(self) -> Timedelta:
        """Time resolution of the associated SpectroFile."""
        return None if self.is_empty else self.file.time_resolution

    @classmethod
    def from_base_item(cls, item: BaseItem) -> SpectroItem:
        """Return a SpectroItem object from a BaseItem object."""
        file = item.file
        if not file or isinstance(file, SpectroFile):
            return cls(file=file, begin=item.begin, end=item.end)
        if isinstance(file, BaseFile):
            return cls(
                file=SpectroFile.from_base_file(file),
                begin=item.begin,
                end=item.end,
            )
        raise TypeError

    def get_value(
        self,
        fft: ShortTimeFFT | None = None,
        sx_dtype: type[complex] = complex,
    ) -> np.ndarray:
        """Get the values from the File between the begin and stop timestamps.

        If the Item is empty, return a single 0.
        """
        if not self.is_empty:
            sx = self.file.read(start=self.begin, stop=self.end)

            if self.file.sx_dtype is not sx_dtype:
                if sx_dtype is float:
                    sx = abs(sx) ** 2
                if sx_dtype is complex:
                    raise TypeError(
                        "Cannot convert absolute npz values to complex sx values."
                        "Change the SpectroData dtype to absolute.",
                    )

            return sx

        return np.zeros(
            (
                fft.f.shape[0],
                fft.p_num(int(self.duration.total_seconds() * fft.fs)),
            ),
            dtype=sx_dtype,
        )
