"""
dotyaml: Bridge YAML configuration files and environment variables

A simple library that allows applications to be configured via either YAML files
or environment variables, providing maximum deployment flexibility.
"""

__version__ = "0.1.3"

# Main API - keep it simple like python-dotenv
from .loader import load_config, ConfigLoader
from .interpolation import interpolate_env_vars

__all__ = ["load_config", "ConfigLoader", "interpolate_env_vars"]
