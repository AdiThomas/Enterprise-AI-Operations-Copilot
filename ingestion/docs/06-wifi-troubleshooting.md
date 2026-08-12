# Wi-Fi Connectivity Troubleshooting

**Applies to:** Office and warehouse Wi-Fi at all NWG sites

## Can't connect to the corporate Wi-Fi network

1. Confirm you're selecting the correct network name: `NWG-Corp` for
   laptops, `NWG-Handheld` for Zebra warehouse devices (these are separate
   networks and a device configured for one won't automatically work on the
   other)
2. Forget the network on your device and reconnect, entering credentials
   fresh — cached credentials from a password change can cause silent
   connection failures
3. Confirm your account isn't locked (see the MFA & Account Reset runbook) —
   a locked account can cause Wi-Fi authentication to fail even though the
   network itself is fine

## Connected but no internet access

- Site-wide issue: check the #it-help Teams channel for any posted outage
  notice before troubleshooting your individual device
- Single-device issue: restart the device's Wi-Fi adapter (toggle Wi-Fi off
  and back on) before assuming a broader problem

## Weak signal in specific warehouse areas

Some areas of larger distribution centers (particularly high-rack storage
zones) have known weaker coverage. This is a layout limitation, not a fault
— if it's affecting daily work, submit a ServicePoint ticket under
**Network > Coverage Request** so it can be considered for the next access
point placement review, rather than expecting an immediate fix.

## Escalation

If reconnecting doesn't resolve the issue and it's affecting only you (not a
site-wide outage), submit a ServicePoint ticket under **Network > Wi-Fi
Connectivity**, including your device name and the specific network you're
trying to join.
