# __all__ declared at the module's end

import sys


def _is_path_acceptable(some_path: str) -> bool:
	return some_path not in sys.path and some_path is not None


def sp_append_no_type_check(some_path: str) -> bool:
	was_path_appended = False

	if _is_path_acceptable(some_path):
		sys.path.append(some_path)
		was_path_appended = True

	return was_path_appended


def sp_prepend_no_type_check(some_path: str) -> bool:
	was_path_prepended = False

	if _is_path_acceptable(some_path):
		sys.path.insert(0, some_path)
		was_path_prepended = True

	return was_path_prepended


def sp_remove_no_type_check(some_path: str) -> bool:
	was_path_removed = False

	try:
		sys.path.remove(some_path)
		was_path_removed = True
	except ValueError:
		# If some_path is not in sys.path.
		pass

	return was_path_removed


__all__ = [
	sp_append_no_type_check.__name__,
	sp_prepend_no_type_check.__name__,
	sp_remove_no_type_check.__name__
]
