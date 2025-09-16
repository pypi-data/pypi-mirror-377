from . import _version
__version__ = _version.get_versions()['version']

from .ApiClient import ApiClient
from .VerboseLoggingOutputFilteredClass import VerboseLoggingOutputFilteredClass
from .Exceptions import FailedToLoginException

frontend_instance_map = {
    "dev": {
        "url": "http://localhost:9000/#"
    },
    "prod": {
        "url": "https://evernetproperties.com/#"
    }
}
