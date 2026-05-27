# Two-Factor Authentication

Enable TOTP-based two-factor authentication for enhanced security.

---

## Overview

Dango supports time-based one-time passwords (TOTP) as a second authentication factor. When 2FA is enabled, logging in requires both your password and a 6-digit code from an authenticator app.

2FA follows [RFC 6238](https://datatracker.ietf.org/doc/html/rfc6238) (TOTP) and is compatible with any standard authenticator app.

---

## Compatible Apps

Any TOTP-compatible authenticator app works with Dango:

- **Google Authenticator** (Android, iOS)
- **Authy** (Android, iOS, Desktop)
- **1Password** (all platforms)
- **Bitwarden** (all platforms)
- **Microsoft Authenticator** (Android, iOS)
- **KeePassXC** (Desktop)

---

## Setting Up 2FA

### Step-by-Step

1. Log into the Dango web UI
2. Go to **Account** (`/settings/account`)
3. Click **Enable Two-Factor Authentication**
4. Enter your current password to confirm
5. Scan the QR code with your authenticator app
6. Enter the 6-digit verification code from the app
7. Save the recovery codes displayed on screen

!!! success "Verification Required"
    You must enter a valid TOTP code to complete setup. This confirms your authenticator app is configured correctly before 2FA takes effect.

---

## Recovery Codes

When you enable 2FA, Dango generates **8 recovery codes**. These are one-time-use codes that let you log in if you lose access to your authenticator app.

### Recovery Code Format

Each code follows the format `XXXX-XXXX` — 8 uppercase alphanumeric characters split by a dash. Ambiguous characters (`O`, `I`, `0`, `1`) are excluded to prevent misreading.

Example:

```
ABCD-EFGH
JKLM-NPQR
STUW-VXYZ
...
```

### Storage

- Recovery codes are **SHA-256 hashed** before storage — Dango cannot display them again after initial generation
- When you use a recovery code, it is consumed and cannot be reused
- Input is case-insensitive and the dash is optional (e.g., `abcdefgh` works)

!!! danger "Save Your Recovery Codes"
    Recovery codes are shown **only once** when 2FA is enabled. Save them in a password manager or other secure location. If you lose both your authenticator app and recovery codes, you'll need an admin to run `dango auth recover`.

---

## Login with 2FA

When 2FA is enabled, the login process adds a second step:

1. Enter your email and password as usual
2. A **partial session** is created (valid for **5 minutes**)
3. Enter either:
    - A 6-digit TOTP code from your authenticator app, or
    - A recovery code (format: `XXXX-XXXX`)
4. On success → full session is created

### Attempt Limit

You get **5 attempts** to enter a correct code. After 5 failed attempts:

- The partial session is invalidated
- You must restart the login process (enter password again)
- This is tracked per partial session, not per account

### Time Window

TOTP codes are valid for a **30-second window** with a ±1 step tolerance (effectively ±30 seconds). If your code is rejected, wait for the next code to appear in your authenticator app.

---

## Regenerating Recovery Codes

If you've used some recovery codes or want a fresh set:

1. Go to **Account** (`/settings/account`)
2. Click **Regenerate Recovery Codes**
3. Enter your current password and a TOTP code to confirm
4. New codes are generated — **all previous codes are invalidated**
5. Save the new codes securely

---

## Disabling 2FA

To turn off two-factor authentication:

1. Go to **Account** (`/settings/account`)
2. Click **Disable Two-Factor Authentication**
3. Enter your current password to confirm
4. 2FA is disabled immediately — future logins require only a password

---

## Emergency Admin Recovery

If all admin accounts are locked out (lost password + lost 2FA + lost recovery codes):

```bash
dango auth recover
```

This command:

1. Creates a new emergency admin account with a temporary password
2. The temporary password is displayed in the terminal
3. The emergency admin account is created without 2FA, so only the temporary password is needed to log in
4. After logging in, you can reset other accounts or disable their 2FA

!!! warning "Physical Server Access Required"
    `dango auth recover` must be run on the machine where Dango is installed. For cloud deployments, SSH into the server first: `dango remote ssh`.

---

## Troubleshooting

### Code Rejected ("Invalid Code")

**Clock drift**: TOTP codes depend on accurate system time. If your device clock is more than 30 seconds off, codes will be rejected.

- **Phone**: Enable automatic time sync in your device settings
- **Server**: Verify NTP is running: `timedatectl status` (should show "NTP synchronized: yes")

### New Phone

If you switched to a new phone:

1. If you have recovery codes → log in with a recovery code
2. Go to **Account** → disable 2FA → re-enable 2FA on the new phone
3. If no recovery codes → ask an admin to run `dango auth recover`

### Lost Authenticator App and Recovery Codes

If you've lost both:

1. Contact an admin to use `dango auth recover`
2. Log in with the temporary admin account
3. Reset the locked-out account's 2FA via the admin user management page

### 2FA Setup QR Code Not Scanning

If the QR code won't scan:

- Try the manual entry option — enter the secret key directly into your authenticator app
- Ensure your authenticator app supports TOTP (not HOTP)
- Check that the QR code is fully visible and not cropped

---

## Next Steps

- [Authentication](authentication.md) — session management and login flows
- [Users & Roles](users-roles.md) — manage user accounts
- [Audit Logging](audit-logging.md) — 2FA events are logged automatically
- [Hardening Guide](hardening.md) — additional security measures
