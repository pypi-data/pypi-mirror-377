# __all__ declared at the module's end

from pathlib import Path
from typing import Iterable, Self

from strath import ensure_path_is_str

from .individual_paths_no_type_check import\
	sp_prepend_no_type_check,\
	sp_remove_no_type_check


class SysPathBundle:
	"""
	Upon instantiation, a bundle stores several paths and prepends them to list
	sys.path. When a bundle is cleared, it erases its content and removes it
	from sys.path. Thus, this class facilitates adding and removing a group of
	paths.

	This class is a context manager. If a bundle is used in a with statement as
	in the following example, it is cleared at the block's end.

	with SysPathBundle(("path/to/module", "path/to/package")):
	
	The constructor can set a bundle to be cleared by the destructor. This
	should not be done for a bundle used as a context manager as exiting the
	with block clears the bundle anyway.
	"""

	def __init__(
			self,
			content: Iterable[str|Path],
			cleared_on_del: bool = False
		) -> None:
		"""
		The constructor needs the paths to store in this bundle and prepend to
		sys.path. If a path in argument content is None or is already in
		sys.path, the bundle will not store it.

		Args:
			content: the paths to store in this bundle.
			cleared_on_del: If it is True, the destructor will clear this
				bundle. This argument should be False if the bundle is used as
				a context manger. Defaults to False.

		Raises:
			TypeError: if a path is not None and not of type str or
				pathlib.Path.
		"""
		self._content = list()
		self._fill_content(content) # Can raise TypeError.

		self._cleared_on_del = cleared_on_del

	def __del__(self) -> None:
		"""
		The destructor will clear this bundle if property cleared_on_del is True.
		"""
		if self._cleared_on_del:
			self.clear()

	def __enter__(self) -> Self:
		return self

	def __exit__(self, exc_type, exc_value, traceback) -> None:
		self.clear()

	def __repr__(self) -> str:
		return self.__class__.__name__\
			+ f"({self._content}, {self._cleared_on_del})"

	@property
	def cleared_on_del(self) -> bool:
		"""
		If this property is True, the destructor will clear this bundle.
		"""
		return self._cleared_on_del

	@cleared_on_del.setter
	def cleared_on_del(self, value: bool) -> None:
		self._cleared_on_del = value

	def clear(self) -> None:
		"""
		Erases this bundle's content and removes it from sys.path.
		"""
		try:
			while len(self._content) > 0:
				path = self._content.pop()
				sp_remove_no_type_check(path)

		except AttributeError:
			# If the destructor clears a bundle when
			# the application ends, sys.path can be None.
			self._content.clear()

	def contains(self, some_path: str|Path) -> bool:
		"""
		Indicates whether this bundle contains the given path.

		Args:
			some_path: the path whose presence is verified.

		Returns:
			bool: True if this bundle contains the given path, False otherwise.

		Raises:
			TypeError: if some_path is not None and not of type str or
				pathlib.Path.
		"""
		some_path = ensure_path_is_str(some_path, True)
		return some_path in self._content

	def _fill_content(self, content: Iterable[str|Path]) -> None:
		for path in content:
			path = ensure_path_is_str(path, True)

			if sp_prepend_no_type_check(path):
				self._content.append(path)


__all__ = [SysPathBundle.__name__]
