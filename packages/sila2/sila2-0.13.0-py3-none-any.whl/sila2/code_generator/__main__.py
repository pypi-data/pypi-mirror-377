# ruff: noqa: B008,T201
# B008 prohibits function calls as default arguments (typer.Argument/Option)
# T201 prohibits using print
import os
import platform
import sys
from contextlib import contextmanager
from glob import glob
from os.path import isdir, join
from typing import Dict, List

from typer import Argument, Option, Typer

from sila2.config import ENCODING
from sila2.framework.utils import parse_feature_definition, xpath_sila

main = Typer(help="SiLA 2 Python Code Generator")
__DEBUG = False


def _get_feature_definition_paths(feature_definition_paths: List[str]) -> List[str]:
    if platform.system() != "Windows":
        return feature_definition_paths

    paths = []
    for path in feature_definition_paths:
        files = glob(path, recursive=True)
        if not files:
            raise FileNotFoundError(f"No such files: '{path}'")
        paths.extend(files)
    return paths


def find_matching_directory(pattern: str) -> str:
    matches = glob(pattern)
    if not matches:
        raise ValueError(f"No matching directory found: {pattern}")
    if len(matches) > 1:
        raise ValueError(f"Multiple matches found: {pattern}")

    match = matches[0]
    if not isdir(match):
        raise NotADirectoryError(f"Not a directory: {match}")
    return match


@contextmanager
def print_exception_if_not_debug():
    try:
        yield
    except Exception as ex:
        if __DEBUG:
            raise ex

        print(f"{ex.__class__.__name__}: {ex}", file=sys.stderr)
        return 1


@main.callback()
def main_args(debug: bool = Option(False, help="Display more detailed error messages")):
    global __DEBUG  # noqa: PLW0603, use of `global` to update state
    __DEBUG = debug


@main.command()
def new_package(
    feature_definitions: List[str] = Argument(None, help="SiLA 2 feature definition files (*.sila.xml)"),
    package_name: str = Option(..., "-n", "--package-name", help="Package name"),  # ellipsis makes option required
    output_directory: str = Option(
        ".", "-o", "--output-directory", help="Package directory (will contain setup files)"
    ),
    overwrite: bool = Option(default=False, help="Overwrite existing files"),
    generate_main: bool = Option(default=True, help="Generate __main__.py to make the package executable"),
    git: bool = Option(default=False, help="Generate .gitignore and README.md"),
    lock_controller: bool = Option(default=False, help="Add default implementation of the core feature LockController"),
    auth_features: bool = Option(
        default=False,
        help="Add default implementations of the core features AuthenticationService, "
        "AuthorizationProviderService and AuthorizationService",
    ),
):
    """Generate a SiLA 2 Server/Client Python package from given feature definitions"""
    from sila2.code_generator.code_generator import CodeGenerator  # noqa: PLC0415 (local import)
    from sila2.framework.feature import Feature  # noqa: PLC0415 (local import)

    with print_exception_if_not_debug():
        features = [Feature(fdl_file) for fdl_file in sorted(feature_definitions)]
        generator = CodeGenerator(overwrite=overwrite)
        generator.generate_package(
            package_name,
            features,
            output_directory,
            generate_main=generate_main,
            lock_controller=lock_controller,
            auth_features=auth_features,
            for_git_repo=git,
        )
        generator.format_generated_files()


@main.command()
def add_features(
    feature_definitions: List[str] = Argument(None, help="SiLA 2 feature definition files (*.sila.xml)"),
    package_directory: str = Option(".", "--package-directory", "-d", help="Package directory"),
):
    """Add features to previously generated package"""
    from sila2.code_generator.code_generator import CodeGenerator  # noqa: PLC0415 (local import)
    from sila2.framework.feature import Feature  # noqa: PLC0415 (local import)

    with print_exception_if_not_debug():
        if not {"setup.py", "pyproject.toml"}.intersection(os.listdir(package_directory)):
            print("Given directory is not a package (does not contain setup.py or pyproject.toml)", file=sys.stderr)
            return

        generated_dir = find_matching_directory(join(package_directory, "*", "generated"))
        implementation_dir = find_matching_directory(join(package_directory, "*", "feature_implementations"))
        server_file = glob(join(package_directory, "*", "server.py"))[0]

        existing_fdl_files = glob(join(generated_dir, "*", "*.sila.xml"))

        old_features = {}
        for fdl_file in existing_fdl_files:
            feature = Feature(fdl_file)
            old_features[feature._identifier] = feature

        new_features = {}
        for fdl_file in _get_feature_definition_paths(feature_definitions):
            feature = Feature(fdl_file)
            if feature._identifier in old_features:
                raise ValueError(f"Feature {feature._identifier} already exists. Use 'update' instead.")
            new_features[feature._identifier] = feature

        new_features = list(new_features.values())
        old_features = list(old_features.values())
        features = old_features + new_features
        features.sort(key=lambda f: f._identifier)

        generator = CodeGenerator(overwrite=True)
        generator.generate_generated_dir(features, generated_dir)
        generator.generate_implementations(new_features, implementation_dir)
        generator.add_features_to_server_file(new_features, server_file)
        generator.format_generated_files()


@main.command("update")
def update_package(
    package_directory: str = Option(".", "--package-directory", "-d", help="Package directory"),
    feature_definitions: List[str] = Argument(None, help="SiLA 2 feature definition files (*.sila.xml)"),
):
    """
    Update a previously generated package after modifications to the feature definitions
    (refreshes the 'generated' submodule)
    """
    from sila2.code_generator.code_generator import CodeGenerator  # noqa: PLC0415 (local import)
    from sila2.code_generator.feature_generator import FeatureGenerator  # noqa: PLC0415 (local import)
    from sila2.framework.feature import Feature  # noqa: PLC0415 (local import)

    with print_exception_if_not_debug():
        generated_dir = find_matching_directory(join(package_directory, "*", "generated"))
        implementation_dir = find_matching_directory(join(package_directory, "*", "feature_implementations"))

        generator = CodeGenerator(overwrite=True)

        # give precedence to explicitly stated features
        def get_identifier(fdl_filepath: str) -> str:
            return xpath_sila(parse_feature_definition(fdl_filepath), "/sila:Feature/sila:Identifier/text()")[0]

        fdl_files_by_identifier: Dict[str, str] = {
            get_identifier(f): f for f in glob(join(generated_dir, "*", "*.sila.xml"))
        }
        fdl_files_by_identifier.update({get_identifier(f): f for f in feature_definitions})

        features: List[Feature] = []
        for fdl_file in fdl_files_by_identifier.values():
            feature = Feature(fdl_file)
            if feature.fully_qualified_identifier == "org.silastandard/core/SiLAService/v1":
                continue
            features.append(feature)
            feature_generator = FeatureGenerator(feature, overwrite=True)
            feature_dir = join(generated_dir, feature._identifier.lower())
            with open(f"{feature_dir}/{feature._identifier.lower()}_base.py", encoding=ENCODING) as fp:
                old_base = fp.read()

            feature_generator.generate_feature_files(feature_dir)
            with open(f"{feature_dir}/{feature._identifier.lower()}_base.py", encoding=ENCODING) as fp:
                new_base = fp.read()

            # if base class changed: generate new impl
            if old_base != new_base:
                feature_generator.generate_impl(implementation_dir, prefix="updated_")
            generator.generated_files.extend(feature_generator.generated_files)
        generator._generate_client(features, generated_dir)
        generator.format_generated_files()


@main.command()
def generate_feature_files(
    output_directory: str = Option(".", "--output-directory", "-o", help="Output directory"),
    overwrite: bool = Option(default=False, help="Overwrite existing files"),
    feature_definitions: List[str] = Argument(None, help="SiLA 2 feature definition files (*.sila.xml)"),
):
    """Generate feature-specific Python files without generating a full server/client package."""
    from sila2.code_generator.feature_generator import FeatureGenerator  # noqa: PLC0415 (local import)
    from sila2.framework.feature import Feature  # noqa: PLC0415 (local import)

    with print_exception_if_not_debug():
        os.makedirs(output_directory, exist_ok=True)

        for fdl_file in sorted(feature_definitions):
            feature = Feature(fdl_file)
            feature_generator = FeatureGenerator(feature, overwrite=overwrite)
            feature_generator.generate_feature_files(
                out_dir=join(output_directory, feature._identifier.lower()),
                part_of_server_package=False,
            )
            feature_generator.format_generated_files()


if __name__ == "__main__":
    sys.exit(main())
