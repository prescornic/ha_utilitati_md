<p align="center">
  <img src="img/utilities.png" alt="Utilități Moldova Logo" width="128" height="128">
</p>

# Utilități Moldova - Home Assistant Custom Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/default)

A unified Home Assistant integration for managing Moldova utility services. Centralizes invoices, payment due dates, overdue notifications, consumption, and meter readings in one clean interface, regardless of utility provider.

> [!WARNING]
> 🛠️ **Active Development Warning**: This project is under **active development** and may undergo frequent changes or be unstable. Use with caution.

---

## ℹ️ Data Sources & Backend Architecture

This integration leverages three primary backend methods to fetch utility details:
1. 🔑 **Direct Personal Cabinet API / Scraper**: Authenticates directly with official provider portals (e.g., **Premier Energy** `oficiulonline.premierenergy.md`, **StarNet** `my.starnet.md`) to extract full invoice details, PDF downloads, and real-time balances.
2. 💳 **bpay.md API**: Queries the `bpay.md` check endpoint (`bscm-xapi.bpay.md`) for structured JSON invoices, line-item breakdowns, subscriber names, and meter indices without requiring portal login credentials.
3. 🌐 **oplata.md Portal**: Queries `oplata.md/payment/check` as a lightweight backend connector for balance totals and sub-service breakdowns.

---

## 🏢 Supported Providers & Data Methods

| Provider | Utility Type | Status | Backend Method | Extracted Details & Features |
|---|---|---|---|---|
| 💡 **Premier Energy** | Electricity / Energie Electrică | 🟢 **Supported** | 🔑 **Personal Cabinet** (`oficiulonline.premierenergy.md`) | Debt (`Datoria NLC`), Advance (`Avans`), Invoice #, Issue & Due Dates, Current & Previous Meter Readings (`kWh`), Monthly Consumption (`kWh`), Bill Amount (`MDL`), Billing Period, Payment Status |
| 🌐 **StarNet** | Internet & TV / Internet | 🟢 **Supported** | 🔑 **Personal Cabinet** (`my.starnet.md`) | Account Balance (`Soldul în lei`), Invoice #, Issue Date, Due Date (End of Month), Bill Amount (`MDL`), Payment Status (`Achitat`/`Neachitat`), Direct PDF Download Link |
| 🚰 **Apă-Canal Chișinău** | Water & Sewage / Apă | 🟢 **Supported** | 💳 **bpay.md API** | Unpaid Balance (`MDL`), Line-item breakdown (`Apă potabilă`, `Canalizare`), Current Meter Index (`m³`), Customer Name & Address |
| 🚰 **InfoSapr** | Water & Communal / Servicii Comunale | 🟢 **Supported** | 🌐 **oplata.md Portal** | Unpaid Balance (`MDL`), Sub-service breakdown (`Deservirea bloc`, `Transport gunoi`, `Lift`, `Fond rezerva`) |
| 🔥 **Energocom** | Natural Gas / Gaz | 🟢 **Supported** | 💳 **bpay.md API** | Unpaid Balance (`MDL`), Subscriber Name (`customer_name`) |
| ⚡ **FEE Nord** | Electricity / Energie Electrică | 🟢 **Supported** | 🌐 **oplata.md Portal** | Unpaid Balance (`MDL`) |
| 🗑️ **Regia AutoSalubritate** | Waste Management / Salubrizare | 🟡 **In Progress** | 🌐 **oplata.md Portal** | Unpaid Balance (`MDL`) *(Pending live invoice test)* |

---

## 💡 Personal Cabinet Extracted Details

### 💡 Premier Energy (`oficiulonline.premierenergy.md`)
- 📊 **Balance & Credit**: Real-time contract debt (`Datoria totală pe NLC`), Advance Credit (`Avans`).
- 🧾 **Invoice Details**: Invoice Number (`Nr. facturii`), Bill Amount (`MDL`), Issue Date (`Data emiterii`), Due Date (`Data scadenței`), Billing Period (`Perioada de facturare`), Payment Status (`Achitata` / `Neachitata`).
- ⚡ **Consumption & Meter Readings**: Current Meter Index (`kWh`), Previous Index (`kWh`), Net Monthly Consumption (`kWh`).

### 🌐 StarNet (`my.starnet.md`)
- 📊 **Balance & Status**: Real-time account balance (`Soldul în lei`), Payment Status (`Achitat` / `Neachitat`).
- 🧾 **Invoice Details**: Invoice Number (e.g., `1234567890`), Bill Amount (`260.00 MDL`), Issue Date (e.g., `01.08.2026`).
- 📅 **Payment Due Date**: Automatically set to **End of Month** (e.g., `31.08.2026`).
- 📄 **Document Downloads**: Direct PDF Invoice Download Link (`pdf_url`).

---

## 🚀 Future Roadmap & Planned Features

- 🔑 **Additional Personal Cabinet Connectors**: Expanding direct personal cabinet integrations to remaining providers (**Energocom**, **Apă-Canal**) for PDF downloads and consumption history.
- ⚡ **Actions & Services**: Custom Home Assistant services (such as `utilitati_md.submit_meter_reading`) for submitting monthly index readings are planned for a future release once direct provider portal submission APIs are active.
- ⚠️ **Service Disruption & Outage Alerts**: Planned integration for contract address outage alerts and scheduled maintenance notifications (*Deconectări de servicii sau avarii pe adresa contractului*).

---

## ⚡ Features

- 🏢 **Multi-Provider & Multi-NLC Support**: Unified experience across Moldova utility providers with support for multiple contract NLCs per account.
- 📊 **Sensors & Binary Sensors**: Balance (MDL), Due Date, Meter Index (`kWh`/`m³`), Monthly Consumption, and Overdue Payment Alerts.
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
3. Select your Utility Provider (e.g., **Premier Energy**, **StarNet**, **Apă-Canal Chișinău**, **InfoSapr**, **Energocom**, **FEE Nord**).
4. Enter Account Alias (optional), Contract Number / Personal ID (e.g., `372594`), and credentials (Username & Password for Personal Cabinet providers like Premier Energy & StarNet).
5. Click **Submit**.

---

## 📄 License

MIT License. Developed for the Home Assistant Moldova Community.
