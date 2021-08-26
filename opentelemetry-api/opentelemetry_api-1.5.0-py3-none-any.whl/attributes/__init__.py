# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# type: ignore

import logging
import threading
from collections import OrderedDict
from collections.abc import MutableMapping
from typing import Optional, Sequence, Union

from opentelemetry.util import types

# bytes are accepted as a user supplied value for attributes but
# decoded to strings internally.
_VALID_ATTR_VALUE_TYPES = (bool, str, bytes, int, float)


_logger = logging.getLogger(__name__)


def _clean_attribute(
    key: str, value: types.AttributeValue, max_len: Optional[int]
) -> Optional[types.AttributeValue]:
    """Checks if attribute value is valid and cleans it if required.

    The function returns the cleaned value or None if the value is not valid.

    An attribute value is valid if it is either:
        - A primitive type: string, boolean, double precision floating
            point (IEEE 754-1985) or integer.
        - An array of primitive type values. The array MUST be homogeneous,
            i.e. it MUST NOT contain values of different types.

    An attribute needs cleansing if:
        - Its length is greater than the maximum allowed length.
        - It needs to be encoded/decoded e.g, bytes to strings.
    """

    if not (key and isinstance(key, str)):
        _logger.warning("invalid key `%s`. must be non-empty string.", key)
        return None

    if isinstance(value, _VALID_ATTR_VALUE_TYPES):
        return _clean_attribute_value(value, max_len)

    if isinstance(value, Sequence):
        sequence_first_valid_type = None
        cleaned_seq = []

        for element in value:
            # None is considered valid in any sequence
            if element is None:
                cleaned_seq.append(element)

            element = _clean_attribute_value(element, max_len)
            # reject invalid elements
            if element is None:
                continue

            element_type = type(element)
            # Reject attribute value if sequence contains a value with an incompatible type.
            if element_type not in _VALID_ATTR_VALUE_TYPES:
                _logger.warning(
                    "Invalid type %s in attribute value sequence. Expected one of "
                    "%s or None",
                    element_type.__name__,
                    [
                        valid_type.__name__
                        for valid_type in _VALID_ATTR_VALUE_TYPES
                    ],
                )
                return None

            # The type of the sequence must be homogeneous. The first non-None
            # element determines the type of the sequence
            if sequence_first_valid_type is None:
                sequence_first_valid_type = element_type
            # use equality instead of isinstance as isinstance(True, int) evaluates to True
            elif element_type != sequence_first_valid_type:
                _logger.warning(
                    "Mixed types %s and %s in attribute value sequence",
                    sequence_first_valid_type.__name__,
                    type(element).__name__,
                )
                return None

            cleaned_seq.append(element)

        # Freeze mutable sequences defensively
        return tuple(cleaned_seq)

    _logger.warning(
        "Invalid type %s for attribute value. Expected one of %s or a "
        "sequence of those types",
        type(value).__name__,
        [valid_type.__name__ for valid_type in _VALID_ATTR_VALUE_TYPES],
    )
    return None


def _clean_attribute_value(
    value: types.AttributeValue, limit: Optional[int]
) -> Union[types.AttributeValue, None]:
    if value is None:
        return None

    if isinstance(value, bytes):
        try:
            value = value.decode()
        except UnicodeDecodeError:
            _logger.warning("Byte attribute could not be decoded.")
            return None

    if limit is not None and isinstance(value, str):
        value = value[:limit]
    return value


class BoundedAttributes(MutableMapping):
    """An ordered dict with a fixed max capacity.

    Oldest elements are dropped when the dict is full and a new element is
    added.
    """

    def __init__(
        self,
        maxlen: Optional[int] = None,
        attributes: types.Attributes = None,
        immutable: bool = True,
        max_value_len: Optional[int] = None,
    ):
        if maxlen is not None:
            if not isinstance(maxlen, int) or maxlen < 0:
                raise ValueError(
                    "maxlen must be valid int greater or equal to 0"
                )
        self.maxlen = maxlen
        self.dropped = 0
        self.max_value_len = max_value_len
        self._dict = OrderedDict()  # type: OrderedDict
        self._lock = threading.Lock()  # type: threading.Lock
        if attributes:
            for key, value in attributes.items():
                self[key] = value
        self._immutable = immutable

    def __repr__(self):
        return "{}({}, maxlen={})".format(
            type(self).__name__, dict(self._dict), self.maxlen
        )

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        if getattr(self, "_immutable", False):
            raise TypeError
        with self._lock:
            if self.maxlen is not None and self.maxlen == 0:
                self.dropped += 1
                return

            if key in self._dict:
                del self._dict[key]
            elif self.maxlen is not None and len(self._dict) == self.maxlen:
                del self._dict[next(iter(self._dict.keys()))]
                self.dropped += 1

            value = _clean_attribute(key, value, self.max_value_len)
            if value is not None:
                self._dict[key] = value

    def __delitem__(self, key):
        if getattr(self, "_immutable", False):
            raise TypeError
        with self._lock:
            del self._dict[key]

    def __iter__(self):
        with self._lock:
            return iter(self._dict.copy())

    def __len__(self):
        return len(self._dict)

    def copy(self):
        return self._dict.copy()
