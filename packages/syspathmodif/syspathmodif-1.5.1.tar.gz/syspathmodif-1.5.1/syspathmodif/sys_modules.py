import sys


def sm_contains(module_name: str) -> bool:
	"""
	Dictionary sys.modules maps module names (str) to the corresponding module.
	This function indicates whether sys.modules contains the module whose name
	is the argument.

	Args:
		module_name: the name of a module.

	Returns:
		bool: True if argument module_name is a key in sys.modules, False
			otherwise.
	"""
	return module_name in sys.modules


__all__ = [sm_contains.__name__]
