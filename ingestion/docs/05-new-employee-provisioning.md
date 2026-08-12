# New Employee Laptop Provisioning

**Audience:** IT Systems team and site champions
**Applies to:** New hire onboarding at any NWG site

## Before day one

1. HR submits a new hire request through the onboarding portal at least 5
   business days before the employee's start date
2. IT Systems creates the Active Directory account (`NWG.LOCAL`) and Azure AD
   sync, following the standard naming convention: first initial + last name
   (e.g. `jsmith`)
3. A laptop is imaged with the standard Windows 11 corporate image, which
   includes Microsoft 365, Cisco AnyConnect, Microsoft Authenticator
   pre-configured for registration, and role-based software depending on
   department (e.g. NorthLogix WMS client for warehouse and logistics roles)
4. The laptop is shipped to the employee's site or, for remote-eligible
   roles, directly to their home address

## Day one — first login

1. Employee signs in with the temporary password provided by HR, which
   forces an immediate password change
2. Employee registers Microsoft Authenticator by following the on-screen MFA
   enrollment prompt — this is mandatory before any other system access is
   granted
3. Employee is walked through VPN setup by their site champion or a
   scheduled onboarding call with IT (see the VPN Setup Guide)

## Standard access granted by default

- Microsoft 365 (Exchange Online, Teams, SharePoint)
- ServicePoint help desk portal
- VPN access (unless role is warehouse-floor-only, per manager designation
  on the onboarding request)

## Role-specific access

Additional system access (NorthLogix WMS, finance systems, etc.) is granted
based on the department and role specified on the onboarding request, and
requires the employee's manager to confirm the specific access level needed
— IT does not grant elevated or department-specific access without this
confirmation on file.

## Common day-one issues

**Employee can't sign in at all**
Confirm the AD account was actually created and synced to Azure AD — sync
can occasionally lag by up to a few hours after account creation. If more
than half a day has passed, escalate to IT Systems directly rather than
waiting further.

**MFA enrollment fails to complete**
Usually a connectivity issue in Microsoft Authenticator during setup. Have
the employee close and reopen the app and retry — if it fails a second time,
this may need a manual reset of the enrollment session by IT.
