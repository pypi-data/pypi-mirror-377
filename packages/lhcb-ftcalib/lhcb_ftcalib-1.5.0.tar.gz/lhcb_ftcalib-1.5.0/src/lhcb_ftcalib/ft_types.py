import pathlib
from typing import Any, Union, List, Tuple, Callable, Literal
import numpy
import pandas

from typing import TYPE_CHECKING 

if TYPE_CHECKING:
    from .Tagger import Tagger
    from .apply_tagger import TargetTagger, TargetTaggerCollection
    from .TaggerCollection import TaggerCollection

    TaggerList = Union[List[Tagger], List[TargetTagger], TaggerCollection, TargetTaggerCollection]
    AnyTaggerCollection = Union[TaggerCollection, TargetTaggerCollection]
else:
    TaggerList = Any
    AnyTaggerCollection = Any

NPArray = Union[numpy.ndarray, pandas.Series]
NPMatrix = List[NPArray]  # Numpy does not implement this as a type
NPArrayOrScalar = Union[numpy.ndarray, pandas.Series, float]

AnyList = Union[numpy.ndarray, pandas.Series, List]
PathStr = Union[pathlib.PosixPath, str]

StrOptionOrSettingsList = Union[str, Union[List, Tuple]]
TransformFunc = Callable[[float], float]
ScaleType = Union[
    Literal["asinh", "linear", "log", "logit", "symlog"],
    Tuple[TransformFunc, TransformFunc]
]