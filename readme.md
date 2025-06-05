# 🏠 UniFi Speed Monitor Custom Component for Home Assistant

[![Open your Home Assistant instance and open a repository.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Nhscan&repository=UDM_Speedtest&category=integration)

This custom Home Assistant integration provides real-time monitoring of your UniFi gateway's internet speeds (download/upload), system uptime, and WAN IP address directly within Home Assistant. It's designed to fetch data directly from your UniFi Controller's API, offering a convenient way to get insights into your network performance beyond what the official UniFi integration might cover for these specific metrics.

## ✨ Features

* **Live Internet Speed Monitoring:** Get real-time download and upload speeds (in Mbps).
* **System Uptime:** Track your UniFi gateway's uptime.
* **WAN IP Address:** Display your public WAN IP address.
* **Direct API Communication:** Fetches data directly from your UniFi Controller, no intermediate Node.js proxy needed after setup.
* **Configurable SSL Verification:** Option to disable SSL certificate verification for controllers using self-signed certificates (use with caution!).

## 🚀 Installation

### Prerequisites

* Home Assistant with [HACS (Home Assistant Community Store)](https://hacs.xyz/) installed.
* Your UniFi Controller URL, username, and password.

### 1. Add this Repository to HACS

To add this integration to HACS, click the button below:

[![Open your Home Assistant instance and open a repository.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Nhscan&repository=UDM_Speedtest&category=integration)

Alternatively, you can manually add the repository:

1.  Open HACS in your Home Assistant instance.
2.  Go to `Integrations`.
3.  Click on the three dots (`⋮`) in the top right corner and select `Custom repositories`.
4.  In the `Add custom repository` field, paste your GitHub repository URL: `https://github.com/Nhscan/UDM_Speedtest`
5.  Select `Integration` as the Category.
6.  Click `Add`.

### 2. Install the Integration

1.  After adding the repository, search for "UniFi Speed Monitor" in the HACS `Integrations` section.
2.  Click on it and select `Download`.
3.  Choose the latest version and click `Download`.

### 3. Restart Home Assistant

A full Home Assistant restart is required for the newly installed custom component to be recognized.

1.  Go to `Settings` -> `System` -> `Hardware` (or `Host`).
2.  Click on `RESTART HOST` and confirm.

## ⚙️ Configuration

To enable the UniFi Speed Monitor, add the following to your `configuration.yaml` file. **Make sure to replace the placeholder values with your actual UniFi Controller details.**

```yaml
# configuration.yaml entry
sensor:
  - platform: unifi_speed_monitor
    name: My UniFi Network      # (Optional) Prefix for your sensor entity names. Defaults to "UniFi Network".
    unifi_url: [https://192.168.2.186:8443](https://192.168.2.186:8443) # (Required) The full URL to your UniFi Controller (e.g., https://your_controller_ip:8443)
    username: your_unifi_username # (Required) Your UniFi Controller username
    password: your_unifi_password # (Required) Your UniFi Controller password
    unifi_site: default         # (Optional) The name of your UniFi site. Defaults to "default".
    verify_ssl: false           # (Optional) Set to true if your UniFi Controller has a valid SSL certificate. Defaults to false (for self-signed certs).