# -*- coding: utf-8 -*-


from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Callable, List, Optional, Tuple, Union

from micropy import utils

from .package import Package
from .source import DependencySource


class PackageDependencySource(DependencySource):

    def __init__(self, package: Package,
                 format_desc: Optional[Callable[..., Any]] = None):
        super().__init__(package)
        self._meta: dict = utils.get_package_meta(str(self.package), self.package.pretty_specs)
        self.format_desc = format_desc or (lambda n: n)

    @property
    def source_url(self) -> str:
        return self._meta['url']

    @property
    def file_name(self) -> str:
        return utils.get_url_filename(self.source_url)

    def fetch(self) -> bytes:
        self.log.debug(f"fetching package: {self.file_name}")
        desc = self.format_desc(self.file_name)
        content = utils.stream_download(self.source_url, desc=desc)
        return content

    def __enter__(self) -> Union[Path, List[Tuple[Path, Path]]]:
        with TemporaryDirectory() as tmp_dir:
            with self.handle_cleanup():
                tmp = Path(tmp_dir)
                path = utils.extract_tarbytes(self.fetch(), tmp)
                stubs = self.generate_stubs(path)
                pkg_root = self.get_root(path)
            return pkg_root or stubs

    def __exit__(self, *args):
        return super().__exit__(*args)
