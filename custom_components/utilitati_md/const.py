"""Constants for the Utilități Moldova integration."""

from typing import Final

DOMAIN: Final = "utilitati_md"
MANUFACTURER: Final = "Utilități Moldova"
ATTRIBUTION: Final = "Data provided by Moldova Utility Providers"

# Configuration options
CONF_PROVIDER: Final = "provider"
CONF_CONTRACT_NUMBER: Final = "contract_number"
CONF_PLACE_OF_CONSUMPTION: Final = "place_of_consumption"
CONF_USERNAME: Final = "username"
CONF_PASSWORD: Final = "password"
CONF_SCAN_INTERVAL: Final = "scan_interval"

DEFAULT_SCAN_INTERVAL_HOURS: Final = 4

# Provider identifiers
PROVIDER_PREMIER_ENERGY: Final = "premier_energy"
PROVIDER_CHISINAU_GAZ: Final = "chisinau_gaz"
PROVIDER_INFO_SARP: Final = "info_sarp"
PROVIDER_AUTO_SALUBRITATE: Final = "auto_salubritate"

PROVIDERS: Final = {
    PROVIDER_PREMIER_ENERGY: {
        "name": "Premier Energy (Energie Electrică)",
        "unit_of_measurement": "kWh",
        "icon": "mdi:lightning-bolt-outline",
        "supports_meter_submission": True,
    },
    PROVIDER_CHISINAU_GAZ: {
        "name": "Chișinău-Gaz (Gaz Naturale)",
        "unit_of_measurement": "m³",
        "icon": "mdi:fire",
        "supports_meter_submission": True,
    },
    PROVIDER_INFO_SARP: {
        "name": "InfoSarp (Servicii Comunale / Apă)",
        "unit_of_measurement": "m³",
        "icon": "mdi:water-pump",
        "supports_meter_submission": True,
    },
    PROVIDER_AUTO_SALUBRITATE: {
        "name": "Regia Autosalubritate (Salubrizare)",
        "unit_of_measurement": "MDL",
        "icon": "mdi:delete-outline",
        "supports_meter_submission": False,
    },
}

# Sensor keys
SENSOR_UNPAID_BALANCE: Final = "unpaid_balance"
SENSOR_LAST_INVOICE_AMOUNT: Final = "last_invoice_amount"
SENSOR_LAST_INVOICE_DATE: Final = "last_invoice_date"
SENSOR_DUE_DATE: Final = "due_date"
SENSOR_METER_INDEX: Final = "meter_index"
SENSOR_MONTHLY_CONSUMPTION: Final = "monthly_consumption"

# Binary sensor keys
BINARY_SENSOR_OVERDUE_ALERT: Final = "overdue_alert"
BINARY_SENSOR_PROVIDER_STATUS: Final = "provider_status"

# Services
SERVICE_SUBMIT_METER_READING: Final = "submit_meter_reading"
SERVICE_REFRESH_DATA: Final = "refresh_data"
