import polars as pl
from typing import Iterable
from polars._typing import IntoExpr
import numpy as np

@pl.api.register_dataframe_namespace("np")
class NumpyFrame:
    def __init__(self, df: pl.DataFrame) -> None:
        self._df = df

    def select(self, *exprs: IntoExpr | Iterable[IntoExpr], **named_exprs: IntoExpr) -> np.ndarray | tuple[np.ndarray]:
        cols = []
        
        for c in self._df.select(*exprs, **named_exprs).iter_columns():
            cols.append(c.to_numpy().flatten())

        return cols[0] if len(cols) == 1 else tuple(cols)