# eHealth Status – Home Assistant Custom Integration 🇧🇪

This is a **custom integration for Home Assistant** that monitors the real-time operational status of various services provided by the [Belgian eHealth platform](https://www.ehealth.fgov.be).

It fetches data directly from the official public status page and creates sensors based on service groups.

## 📡 What It Does

- Connects to the public API:  
  https://status.ehealth.fgov.be/nl/api/components/prod
- Creates one sensor per service group (`group_name_nl`)
- Sensor state reflects `status_name`, e.g.:
  - Operational
  - Degraded Performance
  - Partial Outage
  - Major Outage
- Polls the API every 60 seconds

## 🛠️ Manual Installation

1. Copy this repo to `custom_components/ehealth_status/` in your Home Assistant config
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration → Search for **eHealth Status**

## 🧩 HACS Installation

1. Add this repo as a **Custom Repository** in HACS → Integrations:
   ```
   https://github.com/sebadv/ha-ehealth-status
   ```
2. Search and install “eHealth Status” via HACS
3. Restart Home Assistant

## 🧾 Example Entities

- `sensor.ehealth_ehealth_platform_services`
- `sensor.ehealth_authenticatie_services_riziv`

## 📦 Compatibility

- ✅ Home Assistant Core 2024+
- ✅ HACS Custom Repository Compatible
