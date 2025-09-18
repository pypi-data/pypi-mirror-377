"""CLI package for mcmqtt."""

from .parser import create_argument_parser, parse_arguments
from .version import get_version

__all__ = ['create_argument_parser', 'parse_arguments', 'get_version']