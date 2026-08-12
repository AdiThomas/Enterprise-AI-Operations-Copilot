# VPN Setup Guide — Cisco AnyConnect

**Audience:** All NWG employees requiring remote access to internal systems
**Applies to:** Windows 11 corporate laptops
**Last updated:** IT Systems Team

## Overview

NWG uses Cisco AnyConnect for all remote access to internal resources,
including the NWG.LOCAL domain, SharePoint file shares, and NorthLogix WMS.
VPN access is required any time you're connecting from outside a Northbridge
office network — home, a customer site, or while traveling.

## Prerequisites

- A Northbridge-issued laptop already joined to the NWG.LOCAL domain
- An active NWG network account in good standing (not locked or disabled)
- Microsoft Authenticator installed and registered on your phone — VPN login
  requires MFA approval
- Your manager or IT has enabled VPN access on your account (most staff have
  this by default; warehouse-floor-only roles typically do not)

## Step 1: Confirm Cisco AnyConnect is installed

Cisco AnyConnect ships pre-installed on all corporate laptop images. Check by
opening the Start menu and searching "Cisco AnyConnect Secure Mobility
Client." If it's not present, submit a ServicePoint ticket under
**Software > VPN Client Installation** — do not attempt to download it from
the public internet, as only IT-provisioned installers are signed for use on
the domain.

## Step 2: Connect to the VPN

1. Open Cisco AnyConnect
2. In the connection field, enter: `vpn.northbridgewholesale.com`
3. Click **Connect**
4. Enter your NWG network username and password (the same credentials used
   to log into your laptop)
5. Approve the MFA push notification sent to Microsoft Authenticator on your
   phone
6. Once connected, the AnyConnect icon in your system tray will show a solid
   lock icon rather than an outlined one

## Step 3: Verify connectivity

Once connected, confirm access by:
- Opening a File Explorer window and navigating to `\\nwg-fs01\shared` — you
  should see the shared drive without being prompted for credentials again
- Opening NorthLogix WMS in your browser — it should load without a VPN
  warning banner

## Split-tunnel behavior

NWG's VPN is configured for split tunneling: only traffic destined for
internal NWG systems (10.x.x.x address ranges and *.northbridgewholesale.com)
routes through the VPN tunnel. General internet browsing continues to use
your local connection directly. This is expected behavior and does not
indicate a misconfiguration.

## Common issues

**"Connection attempt has failed" error**
Usually caused by an expired or not-yet-provisioned VPN certificate. Submit a
ServicePoint ticket under **Network > VPN Certificate Issue** — this typically
resolves within one business day.

**MFA push notification never arrives**
Check that Microsoft Authenticator has a stable internet or cellular
connection. If the issue persists across multiple attempts, your account's
MFA registration may need to be reset — see the MFA & Account Reset runbook.

**Connected but can't reach internal file shares**
Confirm you're using the internal hostname (`\\nwg-fs01\shared`), not an IP
address bookmarked from a previous session — internal IP ranges are
periodically reassigned during infrastructure maintenance.

**VPN disconnects repeatedly on Wi-Fi**
Common on unstable home or public Wi-Fi. Try switching to a wired connection
if available, or connect to a different Wi-Fi network. If the issue persists
on a normally stable connection, submit a ticket — this can indicate an
MTU/packet fragmentation issue that IT can adjust remotely.

## Escalation

If none of the above resolves your issue, submit a ServicePoint ticket under
**Network > VPN Connectivity**, marked **Urgent** only if it's preventing you
from working entirely. Include your laptop asset tag (found on a sticker on
the bottom of the device) and the exact error message or screenshot.
