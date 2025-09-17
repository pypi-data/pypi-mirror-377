import pytest

from pathlib import Path
import sys

from strath import ensure_path_is_str


_INIT_SYS_PATH = list(sys.path)

_LOCAL_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _LOCAL_DIR.parent
_LIB_DIR = _REPO_ROOT/"syspathmodif"

_PATH_TYPE_ERROR_MSG = "The path must be None or of type str or pathlib.Path."


def _reset_sys_path() -> None:
	# Copying the list is necessary to preserve the initial state.
	sys.path = list(_INIT_SYS_PATH)


sys.path.insert(0, str(_REPO_ROOT))
from syspathmodif import\
	sp_append,\
	sp_contains,\
	sp_prepend,\
	sp_remove
_reset_sys_path()


def _sp_index(some_path: str|Path) -> int:
	some_path = ensure_path_is_str(some_path, True)
	return sys.path.index(some_path)


def test_sp_contains_true_str() -> None:
	# This test does not change the content of sys.path.
	assert sp_contains(str(_LOCAL_DIR))


def test_sp_contains_true_pathlib() -> None:
	# This test does not change the content of sys.path.
	assert sp_contains(_LOCAL_DIR)


def test_sp_contains_false_str() -> None:
	# This test does not change the content of sys.path.
	assert not sp_contains(str(_LIB_DIR))


def test_sp_contains_false_pathlib() -> None:
	# This test does not change the content of sys.path.
	assert not sp_contains(_LIB_DIR)


def test_sp_contains_none() -> None:
	# This test does not change the content of sys.path.
	assert not sp_contains(None)


def test_sp_contains_exception() -> None:
	# This test does not change the content of sys.path.
	with pytest.raises(TypeError, match=_PATH_TYPE_ERROR_MSG):
		sp_contains(3.14159)


def test_sp_prepend_str() -> None:
	try:
		lib_dir = str(_LIB_DIR)
		success = sp_prepend(lib_dir)
		assert success
		assert _sp_index(lib_dir) == 0
	finally:
		_reset_sys_path()


def test_sp_prepend_pathlib() -> None:
	try:
		success = sp_prepend(_LIB_DIR)
		assert success
		assert _sp_index(_LIB_DIR) == 0
	finally:
		_reset_sys_path()


def test_sp_prepend_no_success() -> None:
	try:
		sys.path.append(str(_LIB_DIR))
		success = sp_prepend(_LIB_DIR)
		assert not success
		assert sp_contains(_LIB_DIR)
	finally:
		_reset_sys_path()


def test_sp_prepend_none() -> None:
	try:
		success = sp_prepend(None)
		assert not success
		assert sys.path == _INIT_SYS_PATH
	finally:
		_reset_sys_path()


def test_sp_append_str() -> None:
	try:
		lib_dir = str(_LIB_DIR)
		success = sp_append(lib_dir)
		assert success
		assert _sp_index(lib_dir) == len(sys.path) - 1
	finally:
		_reset_sys_path()


def test_sp_append_pathlib() -> None:
	try:
		success = sp_append(_LIB_DIR)
		assert success
		assert _sp_index(_LIB_DIR) == len(sys.path) - 1
	finally:
		_reset_sys_path()


def test_sp_append_no_success() -> None:
	try:
		sys.path.append(str(_LIB_DIR))
		success = sp_append(_LIB_DIR)
		assert not success
		assert sp_contains(_LIB_DIR)
	finally:
		_reset_sys_path()


def test_sp_append_none() -> None:
	try:
		success = sp_append(None)
		assert not success
		assert sys.path == _INIT_SYS_PATH
	finally:
		_reset_sys_path()


def test_sp_remove_str() -> None:
	try:
		sys.path.append(str(_LIB_DIR))
		success = sp_remove(str(_LIB_DIR))
		assert success
		assert not sp_contains(str(_LIB_DIR))
	finally:
		_reset_sys_path()


def test_sp_remove_pathlib() -> None:
	try:
		sys.path.append(str(_LIB_DIR))
		success = sp_remove(_LIB_DIR)
		assert success
		assert not sp_contains(_LIB_DIR)
	finally:
		_reset_sys_path()


def test_sp_remove_no_success() -> None:
	try:
		# sys.path does not contain _LIB_DIR.
		success = sp_remove(_LIB_DIR)
		assert not success
		assert not sp_contains(_LIB_DIR)
	finally:
		_reset_sys_path()


def test_sp_remove_none_no_success() -> None:
	try:
		success = sp_remove(None)
		assert not success
		assert sys.path == _INIT_SYS_PATH
	finally:
		_reset_sys_path()


def test_sp_remove_none_success() -> None:
	try:
		sys.path.append(None)
		success = sp_remove(None)
		assert success
		assert sys.path == _INIT_SYS_PATH
	finally:
		_reset_sys_path()
