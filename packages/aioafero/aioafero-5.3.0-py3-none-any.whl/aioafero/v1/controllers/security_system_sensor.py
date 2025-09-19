"""Controller holding and managing Afero IoT resources of type `security-system`."""

from aioafero.device import AferoDevice
from aioafero.errors import DeviceNotFound
from aioafero.v1.models import SecuritySystemSensor, SecuritySystemSensorPut, features
from aioafero.v1.models.resource import DeviceInformation, ResourceTypes

from .base import AferoBinarySensor, AferoSensor, AferoState, BaseResourcesController
from .security_system import SENSOR_SPLIT_IDENTIFIER


class SecuritySystemSensorController(BaseResourcesController[SecuritySystemSensor]):
    """Controller holding and managing Afero IoT `security-system` for the sensors."""

    ITEM_TYPE_ID = ResourceTypes.DEVICE
    ITEM_TYPES = [ResourceTypes.SECURITY_SYSTEM_SENSOR]
    ITEM_CLS = SecuritySystemSensor
    ITEM_MAPPING = {}

    BYPASS_MODES = {0: "Off", 1: "On"}
    CHIRP_MODES = {0: "Off", 1: "On"}
    TRIGGER_MODES = {
        0: "Off",
        1: "Home",
        2: "Away",
        3: "Home/Away",
    }

    SENSOR_TYPES = {
        1: "Motion Sensor",
        2: "Door/Window Sensor",
    }

    async def initialize_elem(self, device: AferoDevice):
        """Initialize the element.

        :param afero_device: Afero Device that contains the updated states

        :return: Newly initialized resource
        """
        available: bool = False
        numbers: dict[tuple[str, str | None], features.NumbersFeature] | None = {}
        selects: dict[tuple[str, str | None], features.SelectFeature] | None = {}
        sensors: dict[str, AferoSensor] = {}
        binary_sensors: dict[str, AferoBinarySensor] = {}
        device_type: int | None = None
        config_key: str | None = None
        for state in device.states:
            if state.functionClass == "sensor-state":
                data = state.value["security-sensor-state"]
                device_type = data["deviceType"]
                binary_sensors["tampered"] = AferoBinarySensor(
                    id="tampered",
                    owner=device.device_id,
                    instance="tampered",
                    current_value=data["tampered"],
                    _error=1,
                )
                binary_sensors["triggered"] = AferoBinarySensor(
                    id="triggered",
                    owner=device.device_id,
                    instance="triggered",
                    current_value=data["triggered"],
                    _error=1,
                )
                sensors["battery-level"] = AferoSensor(
                    id=state.functionClass,
                    owner=device.device_id,
                    value=data["batteryLevel"],
                    unit="%",
                )
                available = not bool(data["missing"])
            else:
                config_key = list(state.value.keys())[0]
                data = state.value[config_key]
                selects[(state.functionInstance, "chirpMode")] = features.SelectFeature(
                    selected=self.CHIRP_MODES.get(data["chirpMode"]),
                    selects=set(self.CHIRP_MODES.values()),
                    name="Chirp Mode",
                )
                selects[(state.functionInstance, "triggerType")] = (
                    features.SelectFeature(
                        selected=self.TRIGGER_MODES.get(data["triggerType"]),
                        selects=set(self.TRIGGER_MODES.values()),
                        name="Triggers",
                    )
                )
                selects[(state.functionInstance, "bypassType")] = (
                    features.SelectFeature(
                        selected=self.BYPASS_MODES.get(data["bypassType"]),
                        selects=set(self.BYPASS_MODES.values()),
                        name="Can Be Bypassed",
                    )
                )
        self._items[device.id] = SecuritySystemSensor(
            [],
            _id=device.id,
            split_identifier=SENSOR_SPLIT_IDENTIFIER,
            config_key=config_key,
            available=available,
            sensors=sensors,
            binary_sensors=binary_sensors,
            numbers=numbers,
            selects=selects,
            device_information=DeviceInformation(
                device_class=device.device_class,
                default_image=device.default_image,
                default_name=device.default_name,
                manufacturer=device.manufacturerName,
                model=self.SENSOR_TYPES.get(device_type, "Unknown"),
                name=device.friendly_name,
                parent_id=device.device_id,
            ),
        )
        return self._items[device.id]

    async def update_elem(self, afero_device: AferoDevice) -> set[str]:
        """Update the Security System Sensor with the latest API data.

        :param afero_device: Afero Device that contains the updated states

        :return: States that have been modified
        """
        return update_from_states(afero_device.states, self[afero_device.id])

    async def set_state(
        self,
        device_id: str,
        selects: dict[tuple[str, int | None], str] | None = None,
    ) -> None:
        """Set supported feature(s) to fan resource."""
        update_obj = SecuritySystemSensorPut()
        try:
            cur_item: SecuritySystemSensor = self.get_device(device_id)
        except DeviceNotFound:
            self._logger.info("Unable to find device %s", device_id)
            return
        if selects:
            chirp_modes = {y: x for x, y in self.CHIRP_MODES.items()}
            trigger_types = {y: x for x, y in self.TRIGGER_MODES.items()}
            bypass_types = {y: x for x, y in self.BYPASS_MODES.items()}
            # Load the current values as it all needs to be sent
            select_vals = {
                "chirpMode": chirp_modes[
                    cur_item.selects.get(
                        (f"{SENSOR_SPLIT_IDENTIFIER}-{cur_item.instance}", "chirpMode")
                    ).selected
                ],
                "triggerType": trigger_types[
                    cur_item.selects.get(
                        (
                            f"{SENSOR_SPLIT_IDENTIFIER}-{cur_item.instance}",
                            "triggerType",
                        )
                    ).selected
                ],
                "bypassType": bypass_types[
                    cur_item.selects.get(
                        (f"{SENSOR_SPLIT_IDENTIFIER}-{cur_item.instance}", "bypassType")
                    ).selected
                ],
            }
            for select, select_val in selects.items():
                if select[1] == "chirpMode":
                    select_vals["chirpMode"] = chirp_modes[select_val]
                elif select[1] == "triggerType":
                    select_vals["triggerType"] = trigger_types[select_val]
                elif select[1] == "bypassType":
                    select_vals["bypassType"] = bypass_types[select_val]
                else:
                    continue
            update_obj.sensor_config = features.SecuritySensorConfigFeature(
                sensor_id=cur_item.instance, key_name=cur_item.config_key, **select_vals
            )
            await self.update(cur_item.id, obj_in=update_obj)


def update_from_states(
    valid_states: list[AferoState], cur_item: SecuritySystemSensor
) -> set[str]:
    """Update the item from the incoming changes."""
    updated_keys = set()
    for state in valid_states:
        if state.functionClass == "sensor-state":
            data = state.value["security-sensor-state"]
            if data["tampered"] != cur_item.binary_sensors["tampered"].current_value:
                updated_keys.add("tampered")
                cur_item.binary_sensors["tampered"].current_value = data["tampered"]
            if data["triggered"] != cur_item.binary_sensors["triggered"].current_value:
                updated_keys.add("triggered")
                cur_item.binary_sensors["triggered"].current_value = data["triggered"]
            if data["batteryLevel"] != cur_item.sensors["battery-level"].value:
                updated_keys.add("battery-level")
                cur_item.sensors["battery-level"].value = data["batteryLevel"]
            if bool(data["missing"]) == cur_item.available:
                updated_keys.add("available")
                cur_item.available = not bool(data["missing"])
        else:
            top_level_key = list(state.value.keys())[0]
            data = state.value[top_level_key]
            if (
                SecuritySystemSensorController.CHIRP_MODES.get(data["chirpMode"])
                != cur_item.selects[(state.functionInstance, "chirpMode")].selected
            ):
                updated_keys.add("chirpMode")
                cur_item.selects[
                    (state.functionInstance, "chirpMode")
                ].selected = SecuritySystemSensorController.CHIRP_MODES.get(
                    data["chirpMode"]
                )
            if (
                SecuritySystemSensorController.TRIGGER_MODES.get(data["triggerType"])
                != cur_item.selects[(state.functionInstance, "triggerType")].selected
            ):
                updated_keys.add("triggerType")
                cur_item.selects[
                    (state.functionInstance, "triggerType")
                ].selected = SecuritySystemSensorController.TRIGGER_MODES.get(
                    data["triggerType"]
                )
            if (
                SecuritySystemSensorController.BYPASS_MODES.get(data["bypassType"])
                != cur_item.selects[(state.functionInstance, "bypassType")].selected
            ):
                updated_keys.add("bypassType")
                cur_item.selects[
                    (state.functionInstance, "bypassType")
                ].selected = SecuritySystemSensorController.BYPASS_MODES.get(
                    data["bypassType"]
                )
    return updated_keys
