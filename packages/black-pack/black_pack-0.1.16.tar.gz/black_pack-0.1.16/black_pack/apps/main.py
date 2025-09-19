import black_pack
import argparse
import os
import shutil
from importlib import resources as importlib_resources
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="black-pack",
        description="Lint the structure of your python-package.",
    )
    commands = parser.add_subparsers(help="Commands", dest="command")

    # init
    # ====
    init_cmd = commands.add_parser(
        "init", help="Initialize an empyt python-package."
    )
    init_cmd.add_argument(
        "pkg_dir",
        metavar="PATH",
        type=str,
        help=("The directory to contain the python-package."),
    )
    init_cmd.add_argument(
        "-n",
        "--name",
        metavar="NAME",
        type=str,
        help=("The name of the package as it would appear in PyPi."),
        required=False,
        default="my_package",
    )
    init_cmd.add_argument(
        "-b",
        "--basename",
        metavar="BASENAME",
        type=str,
        help=("The name of the package as it is imported in python."),
        required=False,
        default="my_package",
    )
    init_cmd.add_argument(
        "-a",
        "--author",
        metavar="AUTHOR",
        type=str,
        help=("The name of the author of the package."),
        required=False,
        default="AUTHOR",
    )
    init_cmd.add_argument(
        "-l",
        "--license",
        metavar="KEY",
        type=str,
        help=("The license of the package."),
        required=False,
        default="MIT",
    )
    init_cmd.add_argument(
        "-u",
        "--host",
        metavar="URL",
        type=str,
        help=("The of url where the package is hosted."),
        required=False,
        default="https://github.com/cherenkov-plenoscope",
    )

    # check
    # =====
    check_cmd = commands.add_parser(
        "check", help="Check an existing python-package."
    )
    check_cmd.add_argument(
        "pkg_dir",
        metavar="PATH",
        type=str,
        help=("The directory of the python-package."),
    )

    # write
    # =====
    write_cmd = commands.add_parser(
        "write", help="Writes a specific file into an existing python-package."
    )
    write_cmd.add_argument(
        "pkg_dir",
        metavar="PATH",
        type=str,
        help=("The directory of the python-package."),
    )
    write_cmd.add_argument(
        "file",
        metavar="RELATIVE_PATH",
        type=str,
        help=("The path inside the python-package to be (over)written."),
    )

    args = parser.parse_args()

    if args.command == "init":
        black_pack.init(
            pkg_dir=args.pkg_dir,
            name=args.name,
            basename=args.basename,
            author=args.author,
            exist_ok=True,
            github_organization_url=args.host,
            github_workflows_test=True,
            github_workflows_release=True,
            license_key=args.license,
        )

    elif args.command == "write":
        resources_dir = os.path.join(
            importlib_resources.files("black_pack"), "resources"
        )
        relpath = args.file
        pkg_dir = args.pkg_dir

        github_workflows_dir = os.path.join(".github", "workflows")
        if relpath == os.path.join(github_workflows_dir, "test.yml"):
            os.makedirs(
                os.path.join(pkg_dir, github_workflows_dir), exist_ok=True
            )
            shutil.copy(
                src=os.path.join(resources_dir, "github_workflows_test.yml"),
                dst=os.path.join(pkg_dir, github_workflows_dir, "test.yml"),
            )
            return

        if relpath == os.path.join(github_workflows_dir, "release.yml"):
            os.makedirs(
                os.path.join(pkg_dir, github_workflows_dir), exist_ok=True
            )
            shutil.copy(
                src=os.path.join(
                    resources_dir, "github_workflows_release.yml"
                ),
                dst=os.path.join(pkg_dir, github_workflows_dir, "release.yml"),
            )
            return

        if relpath == os.path.join(".gitignore"):
            shutil.copy(
                src=os.path.join(
                    resources_dir, "gitignore_commit_8e67b94_2023-09-10"
                ),
                dst=os.path.join(pkg_dir, ".gitignore"),
            )
            return

        if relpath == os.path.join("requirements.txt"):
            shutil.copy(
                src=os.path.join(resources_dir, "requirements.txt"),
                dst=os.path.join(pkg_dir, "requirements.txt"),
            )
            return

        if relpath == os.path.join("pyproject.toml"):
            shutil.copy(
                src=os.path.join(resources_dir, "pyproject.toml"),
                dst=os.path.join(pkg_dir, "pyproject.toml"),
            )
            return

        print("File: {:s} is not knwon.".format(relpath))

    elif args.command == "check":
        black_pack.check_package(pkg_dir=args.pkg_dir)

    else:
        print("No or unknown command.")
        parser.print_help()
        sys.exit(17)


if __name__ == "__main__":
    main()
