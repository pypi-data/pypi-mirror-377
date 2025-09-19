"""Representation of an Afero Fan and its corresponding updates."""

from dataclasses import dataclass, field

from aioafero.v1.models import features

from .resource import DeviceInformation, ResourceTypes
from .sensor import AferoBinarySensor, AferoSensor


@dataclass
class Fan:
    """Representation of an Afero Fan."""

    id: str  # ID used when interacting with Afero
    available: bool

    on: features.OnFeature
    speed: features.SpeedFeature | None
    direction: features.DirectionFeature | None
    preset: features.PresetFeature | None

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

    @property
    def supports_direction(self):
        """Determine if you can change the direction of the fan."""
        return self.direction is not None

    @property
    def supports_on(self):
        """Determine if you can turn the fan on or off."""
        return self.on is not None

    @property
    def supports_presets(self):
        """Determine if presets are supported by this fan."""
        return self.preset is not None

    @property
    def supports_speed(self):
        """Determine if a speed feature is supported by this fan."""
        return self.speed is not None

    @property
    def is_on(self) -> bool:
        """Return bool if fan is currently powered on."""
        if self.on:
            return self.on.on
        return False

    @property
    def current_direction(self) -> bool:
        """Return if the direction is forward."""
        if self.direction:
            return self.direction.forward
        return False

    @property
    def current_speed(self) -> int:
        """Current speed of the fan, as a percentage."""
        if self.speed:
            return self.speed.speed
        return 0

    @property
    def current_preset(self) -> str | None:
        """Current fan preset."""
        if self.preset and self.preset.enabled:
            return self.preset.func_instance
        return None


@dataclass
class FanPut:
    """States that can be updated for a Fan."""

    on: features.OnFeature | None = None
    speed: features.SpeedFeature | None = None
    direction: features.DirectionFeature | None = None
    preset: features.PresetFeature | None = None
