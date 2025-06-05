🏠 UniFi Speed Monitor Custom Component for Home Assistant
This custom Home Assistant integration provides real-time monitoring of your UniFi gateway's internet speeds (download/upload), system uptime, and WAN IP address directly within Home Assistant. It's designed to fetch data directly from your UniFi Controller's API, offering a convenient way to get insights into your network performance beyond what the official UniFi integration might cover for these specific metrics.

✨ Features
Live Internet Speed Monitoring: Get real-time download and upload speeds (in Mbps).

System Uptime: Track your UniFi gateway's uptime.

WAN IP Address: Display your public WAN IP address.

Direct API Communication: Fetches data directly from your UniFi Controller, no intermediate Node.js proxy needed after setup.

Configurable SSL Verification: Option to disable SSL certificate verification for controllers using self-signed certificates (use with caution!).

🚀 Installation
Prerequisites
Home Assistant with HACS (Home Assistant Community Store) installed.

Your UniFi Controller URL, username, and password.

1. Add this Repository to HACS
Open HACS in your Home Assistant instance.

Go to Integrations.

Click on the three dots in the top right corner and select Custom repositories.

In the Add custom repository field, paste your GitHub repository URL: https://github.com/Nhscan/UDM_Speedtest

Select Integration as the Category.

Click Add.

Alternatively, you can click the "Add to Home Assistant" button above in this README.

2. Install the Integration
After adding the repository, search for "UniFi Speed Monitor" in the HACS Integrations section.

Click on it and select Download.

Choose the latest version and click Download.

3. Restart Home Assistant
A full Home Assistant restart is required for the newly installed custom component to be recognized.

Go to Settings -> System -> Hardware (or Host).

Click on RESTART HOST and confirm.

⚙️ Configuration
To enable the UniFi Speed Monitor, add the following to your configuration.yaml file. Make sure to replace the placeholder values with your actual UniFi Controller details.

# Example configuration.yaml entry
sensor:
  - platform: unifi_speed_monitor
    name: My UniFi Network      # (Optional) Prefix for your sensor entity names. Defaults to "UniFi Network".
    unifi_url: https://192.168.2.186:8443 # (Required) The full URL to your UniFi Controller (e.g., https://your_controller_ip:8443)
    username: your_unifi_username # (Required) Your UniFi Controller username
    password: your_unifi_password # (Required) Your UniFi Controller password
    unifi_site: default         # (Optional) The name of your UniFi site. Defaults to "default".
    verify_ssl: false           # (Optional) Set to true if your UniFi Controller has a valid SSL certificate. Defaults to false (for self-signed certs).

Configuration Variables:
name (Optional): A prefix used for your sensor entity names. For example, if name is "My UniFi Network", the download speed sensor will be sensor.my_unifi_network_download_speed.

unifi_url (Required): The full URL to your UniFi Controller, including the port (e.g., https://192.168.2.186:8443). Make sure to use https:// if your controller uses SSL.

username (Required): The username for logging into your UniFi Controller.

password (Required): The password for logging into your UniFi Controller.

unifi_site (Optional): The name of the UniFi site you want to monitor. For most home users, this is default.

verify_ssl (Optional): Set to true if your UniFi Controller has a valid, trusted SSL certificate. Set to false if you use a self-signed certificate or don't want strict SSL verification (e.g., for local network use). Using false reduces security and is not recommended for production environments.

🔄 Restart Home Assistant
After adding/modifying the configuration.yaml entry:

Check Configuration: Go to Developer Tools -> YAML and click CHECK CONFIGURATION to ensure there are no syntax errors.

Restart Home Assistant Host: Go to Settings -> System -> Hardware (or Host depending on your HA version). Click on RESTART HOST and confirm. This performs a full restart of the underlying operating system/container, which is essential for new custom components.

📊 Sensors
Once successfully configured and Home Assistant has restarted, you will find the following new sensor entities:

sensor.<your_name_prefix>_download_speed (e.g., sensor.my_unifi_network_download_speed) - Unit: Mbps

sensor.<your_name_prefix>_upload_speed (e.g., sensor.my_unifi_network_upload_speed) - Unit: Mbps

sensor.<your_name_prefix>_system_uptime (e.g., sensor.my_unifi_network_system_uptime) - Unit: seconds

sensor.<your_name_prefix>_wan_ip_address (e.g., sensor.my_unifi_network_wan_ip_address) - No unit

These sensors can then be added to your Home Assistant dashboards, used in automations, or tracked for historical data by Home Assistant's recorder component.

⚠️ Troubleshooting
If you encounter issues, check the following:

Home Assistant Logs: Go to Settings -> System -> Logs. Filter for custom_components.unifi_speed_monitor or homeassistant.loader for detailed error messages.

File Structure & Naming: Double-check that all directories (custom_components, unifi_speed_monitor) and files (__init__.py, sensor.py, manifest.json) are correctly named and located, paying close attention to case sensitivity.

__init__.py empty: Ensure this file is truly empty.

manifest.json content: Verify the JSON syntax and that the domain matches the folder name.

UniFi Controller Credentials/URL: Confirm your unifi_url, username, and password in configuration.yaml are correct and have access to the UniFi API.

verify_ssl option: If you're using a self-signed certificate on your UniFi Controller, ensure verify_ssl: false is set in your configuration.yaml.

Full Host Restart: Always perform a full Home Assistant host restart after making changes to custom components.

Feel free to open an issue on GitHub if you continue to experience problems!