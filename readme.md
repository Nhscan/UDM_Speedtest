### Configuration Variables:

* **`name`** (Optional): A prefix used for your sensor entity names. For example, if `name` is "My UniFi Network", the download speed sensor will be `sensor.my_unifi_network_download_speed`.

* **`unifi_url`** (Required): The full URL to your UniFi Controller, including the port (e.g., `https://192.168.2.186:8443`). Make sure to use `https://` if your controller uses SSL.

* **`username`** (Required): The username for logging into your UniFi Controller.

* **`password`** (Required): The password for logging into your UniFi Controller.

* **`unifi_site`** (Optional): The name of the UniFi site you want to monitor. Most home users, this is `default`.

* **`verify_ssl`** (Optional): Set to `true` if your UniFi Controller has a valid, trusted SSL certificate. Set to `false` if you use a self-signed certificate or don't want strict SSL verification (e.g., for local network use). **Using `false` reduces security and is not recommended for production environments.**

## 🔄 Restart Home Assistant

After adding/modifying the `configuration.yaml` entry:

1. **Check Configuration:** Go to `Developer Tools` -> `YAML` and click `CHECK CONFIGURATION` to ensure there are no syntax errors.

2. **Restart Home Assistant Host:** Go to `Settings` -> `System` -> `Hardware` (or `Host` depending on your HA version). Click on `RESTART HOST` and confirm. This performs a full restart of the underlying operating system/container, which is essential for new custom components.

## 📊 Sensors

Once successfully configured and Home Assistant has restarted, you will find the following new sensor entities:

* `sensor.<your_name_prefix>_download_speed` (e.g., `sensor.my_unifi_network_download_speed`) - Unit: Mbps

* `sensor.<your_name_prefix>_upload_speed` (e.g., `sensor.my_unifi_network_upload_speed`) - Unit: Mbps

* `sensor.<your_name_prefix>_system_uptime` (e.g., `sensor.my_unifi_network_system_uptime`) - Unit: seconds

* `sensor.<your_name_prefix>_wan_ip_address` (e.g., `sensor.my_unifi_network_wan_ip_address`) - No unit

These sensors can then be added to your Home Assistant dashboards, used in automations, or tracked for historical data by Home Assistant's recorder component.

## ⚠️ Troubleshooting

If you encounter issues, check the following:

* **Home Assistant Logs:** Go to `Settings` -> `System` -> `Logs`. Filter for `custom_components.unifi_speed_monitor` or `homeassistant.loader` for detailed error messages.

* **File Structure & Naming:** Double-check that all directories (`custom_components`, `unifi_speed_monitor`) and files (`__init__.py`, `sensor.py`, `manifest.json`) are correctly named and located, paying close attention to case sensitivity.

* **`__init__.py` empty:** Ensure this file is truly empty.

* **`manifest.json` content:** Verify the JSON syntax and that the `domain` matches the folder name.

* **UniFi Controller Credentials/URL:** Confirm your `unifi_url`, `username`, and `password` in `configuration.yaml` are correct and have access to the UniFi API.

* **`verify_ssl` option:** If you're using a self-signed certificate on your UniFi Controller, ensure `verify_ssl: false` is set in your `configuration.yaml`.

* **Full Host Restart:** Always perform a full Home Assistant host restart after making changes to custom components.

Feel free to open an issue on GitHub if you continue to experience problems!