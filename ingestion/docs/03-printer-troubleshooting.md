# Printer Troubleshooting Guide

**Applies to:** Shared network printers at all distribution centers (HP LaserJet fleet)

## Can't print — printer shows offline

1. Confirm the printer itself is powered on and shows no error on its front
   panel display
2. On your laptop, go to **Settings > Bluetooth & devices > Printers &
   scanners**, select the printer, and click **Open print queue**
3. If there are stuck jobs in the queue, cancel all of them and try printing
   again
4. If the printer still shows offline, it's usually a network issue rather
   than a driver issue — confirm you're connected to the office Wi-Fi or
   wired network (printers aren't reachable over VPN from home)

## Print jobs stuck in queue

Restart the **Print Spooler** service: open **Services** (search from the
Start menu), find **Print Spooler**, right-click, and select **Restart**.
This clears most stuck-queue issues without needing to reinstall the printer.

## Poor print quality (streaks, faded text)

Usually a toner or drum issue rather than a network/driver issue. Check the
printer's front panel for a low-toner warning. If toner was recently replaced
and quality is still poor, submit a ServicePoint ticket under
**Hardware > Printer Maintenance** — this may need a technician visit.

## Printer not appearing in the printer list at all

The printer may not be installed on your machine yet. Go to **Settings >
Bluetooth & devices > Printers & scanners > Add device**, and search for the
printer by its site-specific name (e.g. `HAM-PRINT-02` for the second shared
printer at the Hamilton site — check the label on the printer itself for its
exact name).

## Escalation

If none of the above resolves the issue, submit a ServicePoint ticket under
**Hardware > Printer Issue**, including the printer's name/asset tag and a
description of what you've already tried.
