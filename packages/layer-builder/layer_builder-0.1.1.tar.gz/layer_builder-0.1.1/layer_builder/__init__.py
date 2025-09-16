import os
import shutil
import subprocess
from pathlib import Path
from shutil import rmtree
from typing import Callable
from collections import Counter

# The following are packages included in the base lambda image
LOCAL = [
    "awslambdaric",
    "python-dateutil",
    "urllib3",
    "jmespath",
    "botocore",
    "simplejson",
    "boto3",
    "s3transfer",
    "six",
    "future",
]


def build_from_requirements(
    requirements_path: str,
    output_path: str,
    version: str = "313",
    clean: bool = True,
    graviton: bool = False,
    exclude_local_packages: bool = True,
    additional_commands: list[str] = None,
    cleanup_function: Callable = None,
    max_mb: float = None,
) -> str:
    install_path = Path(output_path, "python")
    if clean and install_path.exists():
        shutil.rmtree(install_path)
    platform = "manylinux2014_aarch64" if graviton else "manylinux2014_x86_64"
    result = subprocess.run(
        f"pip3 install --platform {platform} --only-binary=:all: -r {requirements_path} -qq --target {str(install_path)} --implementation cp --python-version {version}",
        shell=True,
        capture_output=True,
    )
    if result.stdout:
        with open(Path(output_path, "install_log.txt"), "wb") as fp:
            fp.write(result.stdout)
    if result.stderr:
        with open(Path(output_path, "install_errors.txt"), "wb") as fp:
            fp.write(result.stderr)

    if additional_commands:
        for command in additional_commands:
            result = subprocess.run(command, shell=True)
            print(result)

    if exclude_local_packages:
        # This removes the packages that are already included in Python Lambdas
        for p in install_path.iterdir():
            if p.name in LOCAL:
                if p.is_dir():
                    rmtree(p)
                else:
                    p.unlink()
            elif p.name.endswith("dist-info") or p.name.endswith(".py"):
                for name in LOCAL:
                    if p.name.startswith(name):
                        if p.is_dir():
                            rmtree(p)
                        else:
                            p.unlink()

    # This script moves the pyc files out of the pycache into the root, but I'm not sure that's of any real value
    # The strip command is useful for removing debug statements from the modules, need to find a way to replicate
    """
    mkdir -p {deps_dir}/python && \
    pip3 install --platform manylinux2014_x86_64 --only-binary=:all: -qq -r {requirements_deps_file} -t {deps_dir}/python --implementation cp --python-version 311 && \
    cd {deps_dir}/python && \
    find . -type f -name '*.pyc' | \
    while read f; do n=$(echo $f | \
    sed 's/__pycache__\///' | \
    sed 's/.cpython-[2-3] [0-9]//'); \
    cp $f $n; \
    done \
    && find . -type d -a -name '__pycache__' -print0 | xargs -0 rm -rf \
    && find . -type d -a -name 'tests' -print0 | xargs -0 rm -rf \
    && find . -type d -a -name '*.dist-info' -print0 | xargs -0 rm -rf \
    && find . -type f -a -name '*.so' -print0 | xargs -0 strip --strip-unneeded
    """

    if cleanup_function:
        cleanup_function(output_path)

    total_size = _get_directory_size(output_path)
    _print_package_statistics(output_path, total_size)
    if max_mb is not None and total_size / 1024 / 1024 > max_mb:
        raise Exception(
            f"Total size of installed packages ({round(total_size/1024/1024, 1)}mb exceeds maximum size of {max_mb}"
        )
    return output_path


def _get_directory_size(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size


def _print_package_statistics(install_path, total_size=None):
    python_path = Path(install_path, "python")
    if total_size is None:
        total_size = _get_directory_size(python_path)
    dirs = [x for x in python_path.iterdir() if x.is_dir()]
    package_sizes = Counter({d.name: _get_directory_size(d) for d in dirs})
    print(
        f"Installed packages to {install_path} total {round(total_size/1024/1024, 1)} megabytes"
    )
    print(f"Top contributors")
    for contributor, size in package_sizes.most_common(5):
        print(
            f" * {contributor}: {round(size/1024/1024, 1)} ({round(size/total_size*100, 1)}%)"
        )
