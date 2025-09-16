from whitebox import Plugin

from .base import (
    Device,
    DeviceType,
    DeviceWizard,
)
from .manager import device_manager


class WhiteboxPluginDeviceManager(Plugin):
    name = "Device Manager"

    provides_capabilities = [
        "device",
        "device-wizard",
    ]
    slot_component_map = {
        "device-wizard.screen": "Wizard",
    }
    exposed_component_map = {
        "device-wizard": {
            "device-connection": "common/DeviceConnection",
            "device-list": "DeviceList",
        },
        "device": {
            "camera-input-preview": "common/CameraInputPreview",
        },
    }

    plugin_plugin_classes_map = {
        "device.Device": Device,
        "device.DeviceType": DeviceType,
        "device.DeviceWizard": DeviceWizard,
        "device.DeviceManager": device_manager,
    }

    plugin_url_map = {
        "device.device-connection-management": "whitebox_plugin_device_manager:device-list",
        "device.supported-device-list": "whitebox_plugin_device_manager:device-supported-devices",
    }

    state_store_map = {
        "devices": "stores/devices",
    }


plugin_class = WhiteboxPluginDeviceManager
