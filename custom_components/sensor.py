# sensor.py in custom_components/unifi_speed_monitor/

import logging
import aiohttp
import asyncio
from datetime import timedelta
# import ssl # No longer directly using ssl.create_unverified_context, aiohttp handles it

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import (
    CONF_NAME,
    CONF_USERNAME,
    CONF_PASSWORD,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

# Define the update interval for fetching data (e.g., every 10 seconds)
SCAN_INTERVAL = timedelta(seconds=10)

# Custom configuration constants
CONF_UNIFI_URL = "unifi_url"
CONF_UNIFI_USERNAME = CONF_USERNAME # Reuse HA's standard username conf
CONF_UNIFI_PASSWORD = CONF_PASSWORD # Reuse HA's standard password conf
CONF_UNIFI_SITE = "unifi_site"
CONF_VERIFY_SSL = "verify_ssl" # New option for SSL verification

# Default values
DEFAULT_NAME = "UniFi Network"
DEFAULT_UNIFI_SITE = "default"
DEFAULT_VERIFY_SSL = False # Default to false for self-signed certificates

# Validation for the configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_UNIFI_URL): cv.url, # UniFi Controller URL
    vol.Required(CONF_UNIFI_USERNAME): cv.string,
    vol.Required(CONF_UNIFI_PASSWORD): cv.string,
    vol.Optional(CONF_UNIFI_SITE, default=DEFAULT_UNIFI_SITE): cv.string,
    vol.Optional(CONF_VERIFY_SSL, default=DEFAULT_VERIFY_SSL): cv.boolean,
})

def format_uptime(seconds):
    """Helper function to format uptime in a readable way."""
    if not isinstance(seconds, (int, float)) or seconds < 0:
        return "N/A"
    
    days = int(seconds // (3600 * 24))
    seconds -= days * 3600 * 24
    hours = int(seconds // 3600)
    seconds -= hours * 3600
    minutes = int(seconds // 60)
    seconds -= minutes * 60
    
    uptime_string = ''
    if days > 0: uptime_string += f"{days}d "
    if hours > 0: uptime_string += f"{hours}h "
    if minutes > 0: uptime_string += f"{minutes}m "
    if seconds > 0 or uptime_string == '': uptime_string += f"{int(seconds)}s"
    
    return uptime_string.strip() or "0s"


class UniFiClient:
    """Handles communication with the UniFi Controller API."""
    
    def __init__(self, hass: HomeAssistant, unifi_url, username, password, site, verify_ssl):
        """Initialize the UniFi client."""
        self._hass = hass
        self._unifi_url = unifi_url
        self._username = username
        self._password = password
        self._site = site.lower() # Ensure site is lowercase
        self._verify_ssl = verify_ssl
        self._session = async_get_clientsession(hass)
        self._cookies = {} # Store session cookies
        self._csrf_token = None

    async def async_login(self):
        """Logs in to the UniFi Controller and retrieves session cookies and CSRF token."""
        login_url = f"{self._unifi_url}/api/login"
        payload = {"username": self._username, "password": self._password}
        
        _LOGGER.debug(f"Attempting UniFi login to {login_url}")
        try:
            async with self._session.post(
                login_url, 
                json=payload, 
                ssl=False if not self._verify_ssl else True, # Pass ssl=False or ssl=True
                timeout=15
            ) as response:
                response.raise_for_status()
                
                # Extract all cookies
                self._cookies = response.cookies
                
                # Check for CSRF token in cookies first
                if 'csrf_token' in self._cookies:
                    self._csrf_token = self._cookies['csrf_token'].value
                    _LOGGER.debug("Successfully logged in to UniFi Controller and obtained CSRF token from cookies.")
                # Fallback: Check for CSRF token in X-CSRF-Token header
                elif 'X-CSRF-Token' in response.headers:
                    self._csrf_token = response.headers['X-CSRF-Token']
                    _LOGGER.debug("Successfully logged in to UniFi Controller and obtained CSRF token from X-CSRF-Token header.")
                else:
                    self._csrf_token = None
                    _LOGGER.warning("Login successful, but no csrf_token found in cookies or X-CSRF-Token header.")
                
                return True
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            _LOGGER.error(f"UniFi login failed: {e}")
            self._cookies = {}
            self._csrf_token = None
            return False
        except Exception as e:
            _LOGGER.error(f"Unexpected error during UniFi login: {e}")
            self._cookies = {}
            self._csrf_token = None
            return False

    async def async_get_unifi_data(self):
        """Fetches device statistics from the UniFi Controller."""
        api_url = f"{self._unifi_url}/api/s/{self._site}/stat/device"
        
        headers = {}
        if self._csrf_token:
            headers['X-CSRF-Token'] = self._csrf_token

        _LOGGER.debug(f"Fetching UniFi device data from {api_url}")
        try:
            async with self._session.get(
                api_url, 
                headers=headers, 
                cookies=self._cookies, # Pass the cookies
                ssl=False if not self._verify_ssl else True, # Pass ssl=False or ssl=True
                timeout=30
            ) as response:
                if response.status in (401, 403):
                    _LOGGER.warning("UniFi API access denied. Attempting to re-login.")
                    if await self.async_login():
                        # Retry after successful re-login
                        async with self._session.get(
                            api_url, 
                            headers=headers, 
                            cookies=self._cookies, # Pass the new cookies
                            ssl=False if not self._verify_ssl else True, # Pass ssl=False or ssl=True
                            timeout=30
                        ) as retry_response:
                            retry_response.raise_for_status()
                            return await retry_response.json()
                    else:
                        _LOGGER.error("Failed to re-login to UniFi Controller.")
                        return None
                
                response.raise_for_status()
                return await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            _LOGGER.error(f"Error fetching UniFi device data: {e}")
            return None
        except Exception as e:
            _LOGGER.error(f"Unexpected error fetching UniFi device data: {e}")
            return None

class UniFiSpeedSensor(SensorEntity):
    """Representation of a UniFi Speed Monitor sensor."""

    def __init__(self, client: UniFiClient, name_prefix, sensor_type, sensor_label, unit_of_measurement):
        """Initialize the sensor."""
        self._client = client
        self._name_prefix = name_prefix
        self._sensor_type = sensor_type
        self._sensor_label = sensor_label
        self._unit_of_measurement = unit_of_measurement
        self._state = None
        self._available = False # Start as unavailable until data is fetched

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._name_prefix}_{self._sensor_type}"

    @property
    def unique_id(self):
        """Return a unique ID for this sensor."""
        # Make the unique ID robust against URL changes by sanitizing it
        # and ensuring it's unique per sensor type and controller instance
        sanitized_url = self._client._unifi_url.replace('.', '_').replace(':', '_').replace('/', '_').replace('-', '_')
        return f"unifi_speed_monitor_{sanitized_url}_{self._sensor_type}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def available(self):
        """Return True if entity is available."""
        return self._available

    @property
    def device_info(self):
        """Return device information for the UniFi gateway."""
        return {
            "identifiers": {("UniFi Gateway", self._client._unifi_url)},
            "name": f"{self._name_prefix} Gateway",
            "manufacturer": "Ubiquiti",
            "model": "UDM Pro (Monitored)", # This can be made dynamic if multiple UDM models exist
            "via_device": ("UniFi Controller", self._client._unifi_url),
        }

    async def async_update(self):
        """Fetch new state data for the sensor from UniFi Controller."""
        data = await self._client.async_get_unifi_data()

        if data and data.get('data') and isinstance(data['data'], list):
            # Find the UniFi Gateway device (UDM-Pro) that has the WAN port data.
            # We'll search for a device that has a port_table entry with is_uplink: true and network_name: 'wan'.
            # Or fallback to the U7PRO if it's the one reporting uplink data to "Gateway Max"
            
            gateway_device = None
            for device in data['data']:
                # Prioritize finding the device with a WAN uplink in its port_table
                if device.get('port_table') and isinstance(device['port_table'], list):
                    for port in device['port_table']:
                        if port.get('is_uplink') and port.get('network_name') == 'wan' and port.get('ip'):
                            gateway_device = device
                            _LOGGER.debug(f"Identified primary gateway device via WAN port: {gateway_device.get('name') or gateway_device.get('model')}")
                            break
                    if gateway_device:
                        break
            
            # Fallback if no direct WAN port device found, use U7PRO (Dining Room UniFi)
            # This logic assumes the U7PRO is what you are using to report overall gateway stats
            if not gateway_device:
                for device in data['data']:
                    if device.get('name') == 'Dining Room UniFi' and device.get('model') == 'U7PRO' and \
                       device.get('uplink') and device['uplink'].get('uplink_device_name') == 'Gateway Max':
                        gateway_device = device
                        _LOGGER.debug("Identified gateway via 'Dining Room UniFi' U7PRO's uplink.")
                        break

            if gateway_device:
                self._available = True
                
                if self._sensor_type == "download_speed":
                    # Use device's top-level rx_bytes-r or uplink's rx_bytes-r
                    bytes_per_sec = gateway_device.get('rx_bytes-r') or gateway_device.get('uplink', {}).get('rx_bytes-r', 0)
                    self._state = round((bytes_per_sec * 8) / 1_000_000, 2)
                    
                elif self._sensor_type == "upload_speed":
                    # Use device's top-level tx_bytes-r or uplink's tx_bytes-r
                    bytes_per_sec = gateway_device.get('tx_bytes-r') or gateway_device.get('uplink', {}).get('tx_bytes-r', 0)
                    self._state = round((bytes_per_sec * 8) / 1_000_000, 2)
                    
                elif self._sensor_type == "system_uptime":
                    uptime_seconds = gateway_device.get('uptime') # Uptime is directly in seconds
                    self._state = uptime_seconds # Store as seconds for HA's TIME_SECONDS unit
                    
                elif self._sensor_type == "wan_ip_address":
                    wan_ip = "N/A"
                    # Check the identified gateway_device's port_table for the WAN IP
                    if gateway_device.get('port_table') and isinstance(gateway_device['port_table'], list):
                        for port in gateway_device['port_table']:
                            if port.get('is_uplink') and port.get('network_name') == 'wan' and port.get('ip'):
                                wan_ip = port['ip']
                                break
                    self._state = wan_ip
            else:
                _LOGGER.warning("UniFi Gateway device not found in API response. Setting sensor to unavailable.")
                self._available = False
                self._state = None
        else:
            _LOGGER.warning("No data or invalid data structure from UniFi Controller. Setting sensor to unavailable.")
            self._available = False
            self._state = None

async def async_setup_platform(
    hass: HomeAssistant, config, async_add_entities, discovery_info=None
):
    """Set up the UniFi Speed Monitor sensor platform."""
    name_prefix = config.get(CONF_NAME)
    unifi_url = config.get(CONF_UNIFI_URL)
    unifi_username = config.get(CONF_UNIFI_USERNAME)
    unifi_password = config.get(CONF_UNIFI_PASSWORD)
    unifi_site = config.get(CONF_UNIFI_SITE)
    verify_ssl = config.get(CONF_VERIFY_SSL)

    unifi_client = UniFiClient(hass, unifi_url, unifi_username, unifi_password, unifi_site, verify_ssl)

    # Initial login attempt for the client
    if not await unifi_client.async_login():
        _LOGGER.error("Initial login to UniFi Controller failed. Cannot set up sensors.")
        return False

    sensors = [
        UniFiSpeedSensor(unifi_client, name_prefix, "download_speed", "Download Speed", "Mbps"),
        UniFiSpeedSensor(unifi_client, name_prefix, "upload_speed", "Upload Speed", "Mbps"),
        UniFiSpeedSensor(unifi_client, name_prefix, "system_uptime", "System Uptime", "s"), # HA uses 's' for TIME_SECONDS
        UniFiSpeedSensor(unifi_client, name_prefix, "wan_ip_address", "WAN IP Address", None), # No unit
    ]

    async_add_entities(sensors, True)
