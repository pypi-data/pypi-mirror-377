from enum import StrEnum
from pathlib import Path
from typing import Optional, Union
from .any import ListOfAny, SequenceOfAny
from .dict import StringToAnyDict
from .mapping import StringToAnyMapping


BytesOrMemoryview = Union[bytes, memoryview]
OptionalBytesOrMemoryview = Optional[BytesOrMemoryview]

BytesOrString = Union[bytes, str]
OptionalBytesOrString = Optional[BytesOrString]

IntegerOrString = Union[int, str]
OptionalIntegerOrString = Optional[IntegerOrString]

PathOrString = Union[Path, str]
OptionalPathOrString = Optional[PathOrString]

StringOrStringEnum = Union[str, StrEnum]
OptionalStringOrStringEnum = Optional[StringOrStringEnum]

ListOrStringDictOfAny = Union[ListOfAny, StringToAnyDict]
OptionalListOrStringDictOfAny = Optional[ListOrStringDictOfAny]
SequenceOrStringDictOfAny = Union[SequenceOfAny, StringToAnyDict]
OptionalSequenceOrStringDictOfAny = Optional[Union[SequenceOfAny, StringToAnyDict]]

ListOrStringMappingOfAny = Union[ListOfAny, StringToAnyMapping]
OptionalListOrStringMappingOfAny = Optional[Union[ListOfAny, StringToAnyMapping]]
SequenceOrStringMappingOfAny = Union[SequenceOfAny, StringToAnyMapping]
OptionalSequenceOrStringMappingOfAny = Optional[
    Union[SequenceOfAny, StringToAnyMapping]
]
