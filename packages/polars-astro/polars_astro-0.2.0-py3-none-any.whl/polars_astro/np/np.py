import polars as pl
from typing import Iterable
from polars._typing import IntoExpr
import numpy as np

@pl.api.register_dataframe_namespace("np")
class NumpyFrame:
    def __init__(self, df: pl.DataFrame) -> None:
        self._df = df

    def select(self, *exprs: IntoExpr | Iterable[IntoExpr], **named_exprs: IntoExpr) -> list[np.ndarray]:
        return [s.to_numpy().flatten() for s in self._df.select(*exprs, **named_exprs).iter_columns()]