from jcweaver.core.logger import jcwLogger
from jcweaver.core.const import Platform
from .modelarts import ModelArtsAdapter
from .octopus import OctopusAdapter
from .openi import OpenIAdapter


def get_adapter(platform: str):
    platform = platform.lower()
    if platform == Platform.MODELARTS:
        return ModelArtsAdapter()
    elif platform == Platform.OPENI:
        return OpenIAdapter()
    elif platform == Platform.OCTOPUS:
        return OctopusAdapter()
    jcwLogger.error(f"Unsupported platform: {platform}")
    return None
