# MFA & Account Reset Runbook

**Audience:** IT help desk staff and the automated support assistant
**Applies to:** All NWG employee accounts (NWG.LOCAL / Azure AD hybrid)
**Last updated:** IT Systems Team

## Overview

This runbook covers the most common account-access issue reported to IT:
employees unable to complete multi-factor authentication (MFA), either
because they've lost their phone, reinstalled Microsoft Authenticator, or
switched devices without transferring their MFA registration. This document
also covers standard password resets, which are lower-risk and more
frequently self-serviceable.

**Every action in this runbook that changes an account's state (MFA reset,
password reset, account unlock) requires verification of the employee's
identity and a human approval before execution — see the Verification and
Approval sections below. No account-modifying action should ever be taken
purely on the basis of a chat message claiming to be that employee.**

## Category 1: "I forgot my MFA" / lost or reinstalled Authenticator

### Step 1: Determine self-service eligibility

Ask whether the employee has a **backup MFA method** already registered
(many employees have both a phone push and a set of printed recovery codes
from onboarding). If yes, direct them to sign in at
`myaccount.microsoft.com` and complete verification using the backup method
— this fully resolves the issue with no IT action required.

### Step 2: If no backup method is available

This requires an MFA registration reset, which is an account-state change
and **must go through identity verification and approval** before execution:

1. **Identity verification** — confirm the employee's identity via at least
   two of: employee ID number, manager name, site location, or a callback to
   their number on file in the HR system (never a number provided in the
   request itself)
2. **Log a ServicePoint ticket** under **Account Access > MFA Reset**,
   recording the verification method used
3. **Route for approval** — MFA resets require sign-off from either the
   employee's manager or an IT Systems team lead before the reset is
   executed. This is not a formality: MFA reset is one of the most common
   social-engineering targets in account-takeover attempts, so verification
   is treated as mandatory, not optional, regardless of how urgent the
   request seems
4. **Once approved**, an IT Systems team member resets the MFA registration
   in Azure AD, which prompts the employee to re-register Authenticator on
   next login
5. **Notify the employee** of completion via their NWG email address (not
   the channel the original request came in on, as an added verification
   layer)

### Step 3: Confirm re-registration

Ask the employee to confirm they've successfully re-registered Microsoft
Authenticator and can complete a test sign-in before closing the ticket.

## Category 2: Password reset

Lower risk than MFA reset, but still treated as an account-state change.

- **Self-service first:** direct the employee to
  `myaccount.microsoft.com/password` — if they can still complete MFA, this
  requires no IT involvement
- **If MFA is also unavailable:** this becomes a combined password + MFA
  reset and follows the full verification and approval process in Category 1,
  since resetting both simultaneously is a higher-risk action
- **If only the password is needed** (MFA still working): standard identity
  verification (one method is sufficient, since MFA already provides a second
  factor), no manager approval required, IT Systems can reset directly and
  log the ticket

## Category 3: Account locked out (too many failed attempts)

- Confirm this is a genuine lockout (Azure AD sign-in logs show repeated
  failures) rather than a disabled or suspended account, which follows a
  different process
- Standard identity verification, no approval escalation required — this is
  a low-risk, self-correcting action since it doesn't change credentials,
  only unlocks the existing ones
- IT Systems can unlock directly via Azure AD and should remind the employee
  to wait a few minutes before retrying, as lockouts can take a short time to
  clear across all systems

## Verification methods (in order of preference)

1. Callback to the employee's phone number on file in the HR system
2. Video call with camera on, employee ID card visible
3. Confirmation from the employee's manager via a separate channel
4. In-person verification at a Northbridge site (least common, used only
   when other methods aren't practical)

**Never** accept a text message, chat message, or email alone as sufficient
verification for an MFA or combined password+MFA reset — these are the
easiest channels to spoof.

## Escalation

If identity cannot be verified through any available method, or if there's
any indication the request may not be genuine (unusual urgency, request
originating from an unfamiliar channel, inconsistent details), stop the
process and escalate to the IT Systems team lead rather than proceeding.
