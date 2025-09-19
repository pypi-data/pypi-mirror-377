"""Representation of an Afero Lock and its corresponding updates."""

from dataclasses import dataclass, field

from aioafero.v1.models import features

from .resource import DeviceInformation, ResourceTypes
from .sensor import AferoBinarySensor, AferoSensor


@dataclass
class Lock:
    """Representation of an Afero Lock."""

    id: str  # ID used when interacting with Afero
    available: bool

    position: features.CurrentPositionFeature
    # Defined at initialization
    instances: dict = field(default_factory=dict, repr=False, init=False)
    device_information: DeviceInformation = field(default_factory=DeviceInformation)
    sensors: dict[str, AferoSensor] = field(default_factory=dict)
    binary_sensors: dict[str, AferoBinarySensor] = field(default_factory=dict)

    type: ResourceTypes = ResourceTypes.FAN

    def __init__(self, functions: list, **kwargs):  # noqa: D107
        for key, value in kwargs.items():
            if key == "instances":
                continue
            setattr(self, key, value)
        instances = {}
        for function in functions:
            instances[function["functionClass"]] = function.get(
                "functionInstance", None
            )
        self.instances = instances

    def get_instance(self, elem):
        """Lookup the instance associated with the elem."""
        return self.instances.get(elem, None)


@dataclass
class LockPut:
    """States that can be updated for a Lock."""

    position: features.CurrentPositionFeature | None = None
