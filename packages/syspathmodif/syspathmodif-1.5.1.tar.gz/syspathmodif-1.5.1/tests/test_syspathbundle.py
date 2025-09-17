from pathlib import Path
import sys
from typing import Generator

from strath import ensure_path_is_str


_INIT_SYS_PATH = list(sys.path)

_LOCAL_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _LOCAL_DIR.parent
_LIB_DIR = _REPO_ROOT/"syspathmodif"


def _reset_sys_path() -> None:
	# Copying the list is necessary to preserve the initial state.
	sys.path = list(_INIT_SYS_PATH)


sys.path.insert(0, str(_REPO_ROOT))
from syspathmodif import SysPathBundle
_reset_sys_path()


def _assert_path_in_sys_path(
		some_path: str|Path,
		is_in_sys_path: bool
	) -> None:
	some_path = ensure_path_is_str(some_path, True)
	assert (some_path in sys.path) == is_in_sys_path


def _assert_path_is_present(
		some_path: str|Path,
		bundle: SysPathBundle,
		is_in_sys_path: bool,
		is_in_bundle: bool
	) -> None:
	some_path = ensure_path_is_str(some_path, True)
	assert (some_path in sys.path) == is_in_sys_path
	assert bundle.contains(some_path) == is_in_bundle


def _generate_paths() -> Generator[Path, None, None]:
	yield _LOCAL_DIR
	yield _REPO_ROOT
	yield _LIB_DIR


def test_init_generator() -> None:
	try:
		from inspect import isgenerator

		content_gen = _generate_paths()
		assert isgenerator(content_gen)
		bundle = SysPathBundle(content_gen)
		assert not bundle.cleared_on_del

		_assert_path_is_present(_LOCAL_DIR, bundle, True, False)
		_assert_path_is_present(_REPO_ROOT, bundle, True, True)
		_assert_path_is_present(_LIB_DIR, bundle, True, True)

	finally:
		_reset_sys_path()


def test_init_list() -> None:
	try:
		content = [_LOCAL_DIR, _REPO_ROOT, _LIB_DIR]
		assert isinstance(content, list)
		bundle = SysPathBundle(content)
		assert not bundle.cleared_on_del

		_assert_path_is_present(_LOCAL_DIR, bundle, True, False)
		_assert_path_is_present(_REPO_ROOT, bundle, True, True)
		_assert_path_is_present(_LIB_DIR, bundle, True, True)

	finally:
		_reset_sys_path()


def test_init_tuple() -> None:
	try:
		content = (_LOCAL_DIR, _REPO_ROOT, _LIB_DIR)
		assert isinstance(content, tuple)
		bundle = SysPathBundle(content)
		assert not bundle.cleared_on_del

		_assert_path_is_present(_LOCAL_DIR, bundle, True, False)
		_assert_path_is_present(_REPO_ROOT, bundle, True, True)
		_assert_path_is_present(_LIB_DIR, bundle, True, True)

	finally:
		_reset_sys_path()


def test_init_set() -> None:
	try:
		content = {_LOCAL_DIR, _REPO_ROOT, _LIB_DIR}
		assert isinstance(content, set)
		bundle = SysPathBundle(content)
		assert not bundle.cleared_on_del

		_assert_path_is_present(_LOCAL_DIR, bundle, True, False)
		_assert_path_is_present(_REPO_ROOT, bundle, True, True)
		_assert_path_is_present(_LIB_DIR, bundle, True, True)

	finally:
		_reset_sys_path()


def test_clear() -> None:
	try:
		bundle = SysPathBundle((_LOCAL_DIR, _REPO_ROOT, _LIB_DIR))
		bundle.clear()

		_assert_path_is_present(_LOCAL_DIR, bundle, True, False)
		_assert_path_is_present(_REPO_ROOT, bundle, False, False)
		_assert_path_is_present(_LIB_DIR, bundle, False, False)

		assert sys.path == _INIT_SYS_PATH

	finally:
		_reset_sys_path()


def test_cleared_on_del() -> None:
	try:
		bundle = SysPathBundle((_LOCAL_DIR, _REPO_ROOT, _LIB_DIR), True)
		assert bundle.cleared_on_del
		del bundle

		_assert_path_in_sys_path(_LOCAL_DIR, True)
		_assert_path_in_sys_path(_REPO_ROOT, False)
		_assert_path_in_sys_path(_LIB_DIR, False)

		assert sys.path == _INIT_SYS_PATH

	finally:
		_reset_sys_path()


def test_context_management() -> None:
	try:
		with SysPathBundle((_LOCAL_DIR, _REPO_ROOT, _LIB_DIR)) as bundle:
			_assert_path_is_present(_LOCAL_DIR, bundle, True, False)
			_assert_path_is_present(_REPO_ROOT, bundle, True, True)
			_assert_path_is_present(_LIB_DIR, bundle, True, True)

		_assert_path_in_sys_path(_LOCAL_DIR, True)
		_assert_path_in_sys_path(_REPO_ROOT, False)
		_assert_path_in_sys_path(_LIB_DIR, False)

		assert sys.path == _INIT_SYS_PATH

	finally:
		_reset_sys_path()
