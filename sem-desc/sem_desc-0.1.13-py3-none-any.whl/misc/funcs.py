import glob
import re
from contextlib import contextmanager
from multiprocessing.pool import Pool, ThreadPool
from operator import itemgetter
from pathlib import Path
from typing import Dict, Generic, TypeVar, Union, Callable, Any, List, Optional, KeysView

from loguru import logger
from tqdm.auto import tqdm


def str2bool(x):
    assert x in {"True", "False", "true", "false", "null"}
    if x == "<null>":
        return None
    return x.lower() == "true"


def nullable_str(x):
    if x == "<null>":
        return None
    return x


def str2int(x):
    if x == "<null>":
        return None
    return int(x)


def percentage(a, b):
    return "%.2f%% (%d/%d)" % (a * 100 / b, a, b)


def filter_duplication(lst: List[Any], key_fn: Callable[[Any], Any] = None):
    key_fn = key_fn or identity_func
    keys = set()
    new_lst = []
    for item in lst:
        k = key_fn(item)
        if k in keys:
            continue

        keys.add(k)
        new_lst.append(item)
    return new_lst


def identity_func(x):
    return x


def get_latest_version(file_pattern: Union[str, Path]) -> int:
    """Assuming the file pattern select list of files tagged with an integer version for every run, this
    function return the latest version number that you can use to name your next run.

    For example:
    1. If your pattern matches folders: version_1, version_5, version_6, this function will return 6.
    2. If your pattern does not match anything, return 0
    """
    files = [Path(file) for file in sorted(glob.glob(str(file_pattern)))]
    if len(files) == 0:
        return 0

    file = sorted(files)[-1]
    match = re.match("[^0-9]*(\d+)[^0-9]*", file.name)
    if match is None:
        raise Exception("Invalid naming")
    return int(match.group(1))


def get_incremental_path(path: Union[str, Path]) -> str:
    path = Path(str(path))
    if path.suffix == "":
        char = "_"
    else:
        char = "."

    pattern = path.parent / f"{path.stem}{char}*{path.suffix}"
    version = get_latest_version(pattern) + 1

    return str(path.parent / f"{path.stem}{char}{version:02d}{path.suffix}")


def get_latest_path(path: Union[str, Path]) -> Optional[str]:
    path = Path(str(path))
    pattern = path.parent / f"{path.stem}.*{path.suffix}"
    version = get_latest_version(pattern)
    if version == 0:
        return None
    return str(path.parent / f"{path.stem}.{version:02d}{path.suffix}")


def auto_wrap(word: str, max_char_per_line: int, delimiters: List[str] = None, camelcase_split: bool = True) -> str:
    """
    Treat this as optimization problem, where we trying to minimize the number of line break
    but also maximize the readability in each line, i.e: maximize the number of characters in each lines

    Using greedy search.
    :param word:
    :param max_char_per_line:
    :param delimiters:
    :return:
    """
    # split original word by the delimiters
    if delimiters is None:
        delimiters = [' ', ':', '_', '/']

    sublines: List[str] = [""]
    for i, c in enumerate(word):
        if c not in delimiters:
            sublines[-1] += c

            if camelcase_split and not c.isupper() and i + 1 < len(word) and word[i + 1].isupper():
                # camelcase_split
                sublines.append("")
        else:
            sublines[-1] += c
            sublines.append("")

    new_sublines: List[str] = [""]
    for line in sublines:
        if len(new_sublines[-1]) + len(line) <= max_char_per_line:
            new_sublines[-1] += line
        else:
            new_sublines.append(line)

    return "\n".join(new_sublines)


def flatten_dict(odict: dict, result: Optional[dict] = None, prefix: str = ""):
    if result is None:
        result = {}

    for k, v in odict.items():
        if isinstance(v, dict):
            flatten_dict(v, result, prefix=prefix + k + ".")
        else:
            result[prefix + k] = v
    return result


class ParallelMapFnWrapper:
    def __init__(self, fn):
        self.fn = fn

    def run(self, args):
        idx, r = args
        try:
            r = self.fn(r)
            return idx, r
        except:
            logger.error(f"[ParallelMap] Error while process item {idx}")
            raise


def parallel_map(fn, inputs, show_progress=False, progress_desc="", is_parallel=True, use_threadpool=False, n_processes: Optional[int]=None):
    if not is_parallel:
        iter = (fn(item) for item in inputs)
        if show_progress:
            iter = tqdm(iter, total=len(inputs), desc=progress_desc)
        return list(iter)

    if use_threadpool:
        with ThreadPool(processes=n_processes) as pool:
            iter = pool.imap_unordered(ParallelMapFnWrapper(fn).run, enumerate(inputs))
            if show_progress:
                iter = tqdm(iter, total=len(inputs), desc=progress_desc)
            results = list(iter)
            results.sort(key=itemgetter(0))
    else:
        with Pool(processes=n_processes) as pool:
            iter = pool.imap_unordered(ParallelMapFnWrapper(fn).run, enumerate(inputs))
            if show_progress:
                iter = tqdm(iter, total=len(inputs), desc=progress_desc)
            results = list(iter)
            results.sort(key=itemgetter(0))
    return [v for i, v in results]


@contextmanager
def print2file(file_path: Union[str, Path], mode="w", file_only: bool = False):
    """Yield a print function that can be both print to file or print to std"""
    Path(file_path).parent.mkdir(exist_ok=True, parents=True)
    origin_print = print
    with open(str(file_path), mode) as f:
        def print_fn(*args):
            if not file_only:
                origin_print(*args)
            origin_print(*args, file=f)

        try:
            yield print_fn
        finally:
            pass


class FakeTQDM:
    def update(self, *args):
        pass

    def close(self):
        pass


K = TypeVar('K')
V = TypeVar('V')
V2 = TypeVar('V2')


class DictProxy(Dict[K, V2]):
    """Dictionary proxy to access objects' property

    Args:
        odict: dictionary of object
        access: function to access property of an object
    """

    def __init__(self, odict: Dict[K, V], access: Callable[[V], V2]):
        self.odict = odict
        self.access = access

    def __iter__(self):
        return self.odict.__iter__()

    def __getitem__(self, item):
        return self.access(self.odict[item])

    def __contains__(self, item):
        return item in self.odict

    def keys(self) -> KeysView[K]:
        return self.odict.keys()

    def values(self):
        return (self.access(v) for v in self.odict.values())

    def items(self):
        return ((k, self.access(v)) for k, v in self.odict.items())
