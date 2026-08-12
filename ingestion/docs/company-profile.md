# Company Profile: Northbridge Wholesale Group

**Used as the fictional backdrop for all documentation in this project. Entirely
invented — not based on any real company's internal data.**

## Overview

Northbridge Wholesale Group (NWG) is a wholesale distribution company supplying
grocery, foodservice, and retail goods to independent stores and restaurants
across Southern Ontario. Founded in 1998, NWG operates five distribution
centers and a head office, employing approximately 450 people across
warehouse, logistics, sales, and corporate roles.

## Locations

| Site | Role | Approx. staff |
|---|---|---|
| Hamilton, ON | Head office + primary distribution center | 140 |
| London, ON | Distribution center | 85 |
| Kitchener, ON | Distribution center | 70 |
| Barrie, ON | Distribution center | 60 |
| Sudbury, ON | Distribution center | 45 |
| Windsor, ON | Distribution center (satellite, smaller footprint) | 50 |

## IT environment

- **Domain:** `NWG.LOCAL` (on-prem Active Directory, hybrid-joined to Azure AD)
- **Fleet:** Windows 11 on corporate laptops/desktops; ruggedized Zebra
  handhelds on the warehouse floor
- **Productivity suite:** Microsoft 365 (Exchange Online, Teams, SharePoint)
- **MFA:** Microsoft Authenticator, enforced on all M365 and VPN logins
- **VPN:** Cisco AnyConnect, split-tunnel, required for any remote access to
  internal systems
- **Ticketing system:** ServicePoint (internal name for the IT help desk
  platform)
- **ERP / warehouse system:** NorthLogix WMS (fictional warehouse management
  system used across all distribution centers)
- **IT team structure:** A small central IT team based in Hamilton supports
  all six sites, with one on-site "site champion" per distribution center
  who handles first-line hardware issues

## Support model

Employees at any site can reach IT three ways: the ServicePoint self-service
portal, the internal #it-help Teams channel, or by calling the help desk
extension. Standard SLA is same-business-day response for non-urgent issues
and 1-hour response for anything marked urgent (network outage, security
incident, or a full site unable to work).
