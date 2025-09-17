# __all__ declared at the module's end

from pathlib import Path
import sys

from strath import ensure_path_is_str

from .individual_paths_no_type_check import\
	sp_append_no_type_check,\
	sp_prepend_no_type_check,\
	sp_remove_no_type_check


def sp_append(some_path: str|Path) -> bool:
	"""
	Adds the given path to the end of list sys.path if it does not already
	contain the path. If the path is None, this function does not change
	sys.path.

	Args:
		some_path: the path to append to sys.path.

	Returns:
		bool: True if some_path was appended to sys.path, False otherwise.

	Raises:
		TypeError: if argument some_path is not None and not of type str or
			pathlib.Path.
	"""
	some_path = ensure_path_is_str(some_path, True)
	return sp_append_no_type_check(some_path)


def sp_contains(some_path: str|Path) -> bool:
	"""
	Indicates whether list sys.path contains the given path.

	Args:
		some_path: the path whose presence is verified.

	Returns:
		bool: True if sys.path contains argument some_path, False otherwise.

	Raises:
		TypeError: if argument some_path is not None and not of type str or
			pathlib.Path.
	"""
	some_path = ensure_path_is_str(some_path, True)
	return some_path in sys.path


def sp_prepend(some_path: str|Path) -> bool:
	"""
	Adds the given path to the beginning of list sys.path if it does not
	already contain the path. If the path is None, this function does not
	change sys.path.

	Args:
		some_path: the path to prepend to sys.path.

	Returns:
		bool: True if some_path was prepended to sys.path, False otherwise.

	Raises:
		TypeError: if argument some_path is not None and not of type str or
			pathlib.Path.
	"""
	some_path = ensure_path_is_str(some_path, True)
	return sp_prepend_no_type_check(some_path)


def sp_remove(some_path: str|Path) -> bool:
	"""
	Removes the given path from list sys.path if it contains the path.

	Args:
		some_path: the path to remove from sys.path.

	Returns:
		bool: True if some_path was removed from sys.path, False otherwise.

	Raises:
		TypeError: if argument some_path is not None and not of type str or
			pathlib.Path.
	"""
	some_path = ensure_path_is_str(some_path, True)
	return sp_remove_no_type_check(some_path)


__all__ = [
	sp_append.__name__,
	sp_contains.__name__,
	sp_prepend.__name__,
	sp_remove.__name__
]
