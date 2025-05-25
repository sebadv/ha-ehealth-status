# eHealth Status – Home Assistant Custom Integration 🇧🇪🇫🇷

This is a **custom integration for Home Assistant** that monitors the real‑time operational status of various services provided by the [Belgian eHealth platform](https://www.ehealth.fgov.be).

[![Current Version](https://img.shields.io/badge/version-1.5.16-blue.svg)](https://github.com/sebadv/ha-ehealth-status)
[![HACS Compatible](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/sebadv/ha-ehealth-status)
[![HACS Action](https://github.com/sebadv/ha-ehealth-status/actions/workflows/hacs.yaml/badge.svg)](https://github.com/sebadv/ha-ehealth-status/actions/workflows/hacs.yaml)
[![Validate with hassfest](https://github.com/sebadv/ha-ehealth-status/actions/workflows/hassfest.yaml/badge.svg)](https://github.com/sebadv/ha-ehealth-status/actions/workflows/hassfest.yaml)

It supports **bilingual endpoints** (Dutch/French) and a **two‑step setup**:
1. Select your preferred language (Nederlands / Français)  
2. Choose which services to monitor

## 📡 What It Does

- Fetches data from the public API based on selected language:  
  - Dutch: `https://status.ehealth.fgov.be/nl/api/components/prod`  
  - French: `https://status.ehealth.fgov.be/fr/api/components/prod`
- Creates one sensor per selected service (`name_nl`)
- Sensor state reflects `status_name`, e.g.:
  - Operational  
  - Degraded Performance  
  - Partial Outage  
  - Major Outage
- Polls the API every 60 seconds
- Allows **reconfiguration** (change language/services) via the **Configure** button

## 🏗️ Two‑Step Setup Flow

1. **Language**: Choose between **Nederlands** or **Français**  
2. **Services**: Multi‑select which `name_nl` services you want to monitor  

You can re‑run these steps anytime by going to **Settings → Devices & Services → eHealth Status → Configure**.

## 🛠️ Manual Installation

1. Copy this repo to `custom_components/ehealth_status/` in your Home Assistant config  
2. Restart Home Assistant  
3. Go to **Settings → Devices & Services → Add Integration → eHealth Status**  
4. Follow the two‑step wizard (language + services)

## 🧩 HACS Installation

1. In Home Assistant go to **HACS → Integrations → ⋮ → Custom Repositories**  
2. Add: https://github.com/sebadv/ha-ehealth-status
3. Select **Integration**  
4. Install **eHealth Status**  
5. Restart Home Assistant  
6. Add the integration via **Settings → Devices & Services**

## 🔄 Reconfiguration

- After installation, click **Configure** on the integration entry to:
- Change language  
- Add or remove services  

Changes take effect immediately (after the next poll) without re‑installing.

## 🧾 Example Entities

- `sensor.ehealth_<component_id>`  
- e.g. `sensor.ehealth_12345`

## 📦 Compatibility

- ✅ Home Assistant Core 2024+  
- ✅ HACS Custom Repository Compatible  

## 🆘 Support

If you encounter any issues or have suggestions for improvements:
1. Check the [documentation](https://github.com/sebadv/ha-ehealth-status)
2. Report issues on our [issue tracker](https://github.com/sebadv/ha-ehealth-status/issues)

If you like this integration, feel free to buy me a coffee:

[![Buy Me A Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://buymeacoffee.com/seba.gent)

---

_Developed by [@sebadv](https://github.com/sebadv)_

