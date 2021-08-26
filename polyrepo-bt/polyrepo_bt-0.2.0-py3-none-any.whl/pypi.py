from typing import Optional, Dict
import requests


PYPI_INDEX = "https://pypi.org"


class PyPI:
    instances: Dict[str, "PyPI"] = {}

    def __init__(self, index: str):
        self.index = index
        self.pkgs: Dict[str, Optional[dict]] = {}

    @staticmethod
    def get_instance(index: str = PYPI_INDEX) -> "PyPI":
        if index not in PyPI.instances:
            PyPI.instances[index] = PyPI(index)
        return PyPI.instances[index]

    def does_package_exist(
        self, pkg_name: str, package_version: Optional[str] = None
    ) -> bool:
        """Check if a package exist in pypi index"""
        pkg_info = self.fetch_pkg_info(pkg_name)
        if pkg_info is None:
            return False
        releases = pkg_info["releases"]
        return package_version in releases

    def get_hash(self, pkg_name: str, pkg_version: str) -> Optional[str]:
        """Get hash of a package (wheel distribution) at specific version"""
        pkg_info = self.fetch_pkg_info(pkg_name)
        if pkg_info is None:
            return None
        releases = pkg_info["releases"]
        if pkg_version not in releases:
            return None

        lst = [release for release in releases[pkg_version] if release['filename'].endswith(".whl")]
        if len(lst) != 1:
            raise Exception("Can't obtain hash of package %s as it does not have wheel release" % (pkg_name))
        return lst[0]["digests"]["sha256"]

    def fetch_pkg_info(self, pkg_name: str) -> Optional[dict]:
        if pkg_name not in self.pkgs:
            resp = requests.get(self.index + f"/pypi/{pkg_name}/json")
            if resp.status_code == 404:
                self.pkgs[pkg_name] = None
            else:
                assert resp.status_code == 200
                self.pkgs[pkg_name] = resp.json()

            return self.pkgs[pkg_name]
