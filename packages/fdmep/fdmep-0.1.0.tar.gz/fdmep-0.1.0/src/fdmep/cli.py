# -*- coding: utf-8 -*-
import argparse
from importlib.metadata import version, PackageNotFoundError
from . import __version__
from .scaffolder import run_install

def main():
    parser = argparse.ArgumentParser(
        prog="fdmep",
        description="CLI para inicializar extensões pyRevit rapidamente."
    )
    parser.add_argument("--version", action="store_true", help="Mostra a versão e sai.")
    sub = parser.add_subparsers(dest="command")

    p_install = sub.add_parser("install", help="Executa o scaffolding/instalação da extensão.")

    args = parser.parse_args()

    if args.version:
        try:
            print(version("fdmep"))
        except PackageNotFoundError:
            print(__version__)
        return

    if args.command == "install":
        run_install()
        return

    parser.print_help()
