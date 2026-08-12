# Network Outage Escalation Procedure

**Applies to:** Site-wide or partial network outages at any NWG distribution center

## What counts as an outage worth escalating immediately

- An entire site or floor unable to reach the internet or internal systems
- NorthLogix WMS unreachable from multiple workstations at once (not just one)
- VPN unreachable for all remote employees simultaneously (not an individual
  connectivity issue — see the VPN Setup Guide for single-user issues)

Single-device issues (one laptop can't connect but others nearby are fine)
are not a network outage — treat those as a standard device support request
instead.

## Step 1: Confirm scope

Ask whether the issue affects one person, one area of the site, or the
entire site. This determines urgency and who to notify.

## Step 2: Report immediately

For a confirmed site-wide or multi-user outage:

1. Submit a ServicePoint ticket under **Network > Outage**, marked
   **Urgent**
2. Post in the #it-help Teams channel with the site name and scope, in
   addition to the ticket (outages need both — the ticket for tracking, the
   Teams post for real-time visibility to the on-call IT staff)
3. If Teams itself is unreachable (full internet outage), call the IT help
   desk extension directly

## Step 3: While waiting for resolution

- Do not reboot core network equipment (switches, the site's router/firewall)
  unless explicitly instructed by IT — this can complicate diagnosis
- Individual workstation reboots are fine and sometimes help, but won't
  resolve a genuine site-wide outage
- Warehouse operations should switch to the paper-based fallback process if
  the outage affects NorthLogix WMS for an extended period: pick and receiving
  staff move to printed order/pick sheets, coordinated by the site's on-site
  champion, until systems are restored and the completed paper records can be
  entered back into NorthLogix WMS

## Standard SLA for outages

Site-wide outages are treated as the highest-priority ticket category — a
30-minute target response, tighter than the 1-hour general SLA for other
urgent issues — with hourly status updates until resolved.
