<p align="center">
  <img src="img/utilities.png" alt="Utilități Moldova Logo" width="128" height="128">
</p>

# Utilități Moldova - Home Assistant Custom Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/default)

A unified Home Assistant integration for managing Moldova utility services. Centralizes invoices, payment due dates, overdue notifications, and meter index submissions in one clean interface, regardless of utility provider.

> [!WARNING]
> 🛠️ **Active Development Warning**: This project is under **active development** and may undergo frequent changes or be unstable. Use with caution.

---

## ℹ️ Data Source & Backend Architecture

Currently, this integration utilizes **[oplata.md](https://oplata.md)** as the primary backend data source to retrieve balance amounts, unpaid invoices, and sub-service payment breakdowns across Moldova utility providers without requiring complex login credentials.

---

## 🏢 Supported Providers & Development Status

| Provider | Utility Type | Status | Supported Features |
|---|---|---|---|
| 🚰 **InfoSarp** | Water & Communal / Servicii Comunale | 🟢 **Supported** | Invoice tracking, Balance, Line-item breakdown |
| 🔥 **Energocom** | Natural Gas / Gaz | 🟢 **Supported** | Invoice tracking, Balance |
| 🌐 **StarNet** | Internet & TV / Internet | 🟢 **Supported** | Invoice tracking, Balance |
| 💡 **Premier Energy** | Electricity / Energie Electrică | 🟢 **Supported** | Invoice tracking, Balance |
| 🚰 **Apă-Canal Chișinău** | Water & Sewage / Apă | 🟡 **In Progress** | Invoice tracking, Balance (Pending live invoice) |
| 🗑️ **Regia AutoSalubritate** | Waste Management / Salubrizare | 🟡 **In Progress** | Invoice tracking, Balance (Pending live invoice) |

---

## 🚀 Future Roadmap & Planned Features

- 🔑 **Direct Personal Cabinet Integrations**: Future releases will introduce direct authentication with provider customer portals (e.g., **Premier Energy**, **StarNet**) to unlock advanced capabilities:
  - Direct meter index submissions (*Indicații contor*)
  - Detailed historical consumption metrics (*Consum kWh / m³*)
  - Direct PDF invoice downloads & payment history
- ⚡ **Actions & Services**: Custom Home Assistant services (such as `utilitati_md.submit_meter_reading`) for submitting monthly index readings are planned for a future release once direct provider portal connectors are active.
- ⚠️ **Service Disruption & Outage Alerts**: Planned integration for contract address outage alerts and scheduled maintenance notifications (*Deconectări de servicii sau avarii pe adresa contractului*).

---

## ⚡ Features

- 🏢 **Multi-Provider Support**: Unified experience across utility providers in Moldova.
- 📊 **Sensors & Binary Sensors**: Balance (MDL), Due Date, Meter Index, Consumption, and Overdue Payment Alerts.
- 🌐 **Multi-Language Support**: English, Romanian (`ro`), and Russian (`ru`).

---

## 📸 Entity Overview & Dashboard Example

Here is an example of the entities created by **Utilități Moldova** inside Home Assistant:

<p align="center">
  <img src="img/example.png" alt="Utilități Moldova Entities Example" width="600">
</p>

---

## 📦 Installation via HACS

1. Open **HACS** in your Home Assistant instance.
2. Click the top-right 3 dots and select **Custom repositories**.
3. Add the repository URL `https://github.com/prescornic/ha_utilitati_md`.
4. Category: **Integration**.
5. Click **Add**, then find **Utilități Moldova** and click **Download**.
6. Restart Home Assistant.

---

## ⚙️ Configuration

1. Go to **Settings** -> **Devices & Services** -> **Add Integration**.
2. Search for **Utilități Moldova**.
3. Select your Utility Provider (e.g., **InfoSarp**, **Energocom**, **StarNet**, **Premier Energy**, **Apă-Canal Chișinău**).
4. Enter Account Alias (optional) and Contract Number / Personal Code (e.g., `123/1234567890`).
5. Click **Submit**.

---

## 📄 License

MIT License. Developed for the Home Assistant Moldova Community.
