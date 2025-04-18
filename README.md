# eHealth Status – Home Assistant Custom Integration 🇧🇪

This is a **custom integration for Home Assistant** that monitors the real-time operational status of various services provided by the [Belgian eHealth platform](https://www.ehealth.fgov.be).

It fetches data directly from the official public status page and creates sensors based on service groups.

---

## 📡 What It Does

- Connects to the public API at:  
  [`https://status.ehealth.fgov.be/nl/api/components/prod`](https://status.ehealth.fgov.be/nl/api/components/prod)
  
- Automatically creates a **sensor for each service group**, based on the field `group_name_nl`.

- Each sensor shows the **current operational status** from the `status_name` field, such as:
  - `Operational`
  - `Degraded Performance`
  - `Partial Outage`
  - `Major Outage`

- Updates every **60 seconds** using Home Assistant’s polling coordinator.

---

## 🛠️ Installation (Manual)

1. Copy this repository into your Home Assistant config under:

custom_components/ehealth_status/


2. Restart Home Assistant.

3. In Home Assistant:
- Go to **Settings → Devices & Services**
- Click **Add Integration**
- Search for **eHealth Status**
- Confirm to install — no configuration is required

---

## 🔍 Example Sensors

Once added, you’ll see sensors such as:

- `sensor.ehealth_ehealth_platform_services`
- `sensor.ehealth_authenticatie_services_riziv`
- `sensor.ehealth_mycarenet_platform`
- etc.

Each sensor corresponds to a group of eHealth services and reflects the current operational status.

---

## 📅 Update Frequency

The integration fetches data from the API **every 60 seconds**.

This is a **polling integration**, designed for monitoring.

---

## 🧩 Data Fetched

Each sensor is built from:
- `group_name_nl`: used as the sensor name
- `status_name`: used as the sensor state

Optionally, you can extend the integration to include:
- `description`
- `component_name_nl`
- or other status fields from the API

---

## 📦 Compatibility

- ✅ Home Assistant Core (2024.x+)
- ❌ Not currently in HACS (manual install only)

---

## 🙌 Author

Made by [@sebadv](https://github.com/sebadv)  
API provided by [status.ehealth.fgov.be](https://status.ehealth.fgov.be)
