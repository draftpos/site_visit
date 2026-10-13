# CRM Site Visits & Field Management (crm_site_visit)

[![Odoo Version](https://img.shields.io/badge/Odoo-17.0%20%7C%2018.0-714B67?logo=odoo&logoColor=white)](https://www.odoo.com)
[![License: LGPL-3](https://img.shields.io/badge/License-LGPL--3-blue.svg)](LICENSE)
[![Category](https://img.shields.io/badge/Category-Sales%2FCRM-orange.svg)]()
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

> **Streamlined Client Site Visit Booking, Field Representative Scheduling, Location Tracking & Reschedule Audit Trail for Odoo CRM.**

---

## 📌 Overview

**CRM Site Visits & Field Management** empowers sales and technical service teams to schedule, dispatch, and track on-site client demonstrations, assessments, and technical visits directly from Odoo CRM leads. It bridges the gap between digital pipeline management and field execution with complete status lifecycles, location tracking, and reschedule auditing.

---

## ✨ Key Features

### 1. 📍 Direct Lead-to-Site Visit Booking
- **1-Click Booking**: Schedule site visits directly from CRM lead forms with automatic customer, phone, and address prefill.
- **Smart Sequence Tracking**: Automated unique site visit tracking numbers (`VISIT/0001`).
- **Lead Sync**: Updates the parent lead's `write_date` and `write_uid` ensuring CRM activity audits stay synchronized.

### 2. 📅 Interactive Scheduling & Calendar Integration
- **Interactive Calendar View**: View scheduled, completed, and pending visits across technicians and sales representatives.
- **Field Assignment**: Assign specific visitors, technicians, or sales reps with immediate notification.
- **City & Location Intelligence**: Track customer premises addresses, landmark notes, and city boundaries.

### 3. 🔄 Reschedule Wizard with Audit Trail
- **Formal Reschedule Workflow**: Integrated wizard capturing reschedule reason, requester, and new proposed dates.
- **Audit History**: Logs every historical change in the chatter with full accountability.

### 4. 📊 Multi-Status Lifecycle
- Clear progression stages:
  - **Booked** ➔ **Confirmed** ➔ **In Progress** ➔ **Completed** / **Cancelled** / **Rescheduled**.
- Quick status transition action buttons with user role validation.

---

## 🚀 Installation & Setup

1. **Clone or Copy** this addon into your Odoo custom addons directory:
   ```bash
   git clone git@github.com:draftpos/site_visit.git crm_site_visit
   ```
2. **Update Addons List**:
   - Activate Developer Mode (`Settings` -> `General Settings` -> `Activate Developer Mode`).
   - Navigate to `Apps` -> `Update Apps List`.
3. **Install the Module**:
   - Search for **CRM Site Visits** (`crm_site_visit`).
   - Click **Install** or **Upgrade**.

---

## 📁 Technical Information

| Attribute | Value |
|---|---|
| **Technical Name** | `crm_site_visit` |
| **Category** | Sales/CRM |
| **Odoo Compatibility** | Odoo 17.0+ & Odoo 18.0+ |
| **Dependencies** | `crm`, `mail` |
| **License** | LGPL-3 |
| **Author** | DraftPOS & Showline Solutions |

---

## 📄 License

This module is licensed under the **GNU Lesser General Public License v3.0 (LGPL-3)**. See the [LICENSE](LICENSE) file for details.
