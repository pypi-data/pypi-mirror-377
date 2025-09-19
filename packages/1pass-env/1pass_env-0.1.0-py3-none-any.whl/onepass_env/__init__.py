"""1pass-env: A CLI tool for managing environment variables with 1Password integration."""

from onepass_env.__about__ import __version__
from onepass_env.cli import cli, main
from onepass_env.core import EnvImporter, EnvExporter
from onepass_env.onepassword import OnePasswordClient, get_client
from onepass_env.validation import validate_fields, validate_output_path, validate_input_file

__all__ = [
    "__version__",
    "cli",
    "main", 
    "EnvImporter",
    "EnvExporter",
    "OnePasswordClient",
    "get_client",
    "validate_fields",
    "validate_output_path", 
    "validate_input_file"
]
