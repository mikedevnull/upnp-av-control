from fastapi.staticfiles import StaticFiles
import os
import typing


class StaticFilesSPA(StaticFiles):
    """
    Static files mount point with fallback to main index,
    useful to support html history mode for react/vue router
    """

    def __init__(self, directory: os.PathLike, index='index.html', packages=None, html=False, check_dir=True) -> None:
        super().__init__(directory=directory, packages=packages, html=html, check_dir=check_dir)
        self._fallback = super().lookup_path(index)

    def lookup_path(self, path: str) -> typing.Tuple[str, os.stat_result]:
        """
        Normal static file lookup with fallback to index file
        """

        full_path, stat_result = super().lookup_path(path)

        if stat_result is None:
            return self._fallback

        return (full_path, stat_result)
