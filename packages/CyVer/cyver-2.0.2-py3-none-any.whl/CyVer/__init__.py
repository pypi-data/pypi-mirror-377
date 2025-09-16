from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("CyVer")  # Make sure this matches the package name in setup.py
except PackageNotFoundError:
    __version__ = "unknown"

from CyVer.validators.syntax_validator import SyntaxValidator
from CyVer.validators.properties_validator import PropertiesValidator
from CyVer.validators.schema_validator import SchemaValidator
