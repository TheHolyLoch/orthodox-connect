# Orthodox Connect User Onboarding Guide

## 1. Onboarding Goals

This guide explains the first user journey for Orthodox Connect in plain language.

Goals:

- Help invited users create an account.
- Explain why access is invite-only.
- Explain what approval and verification mean.
- Help users find chat rooms, direct messages, and meetings.
- Give simple security advice.
- Give users a clear support path without exposing private contact details in the repository.

This is a design document for user guidance. It does not add UI, code, accounts, or real support contacts.

## 2. Who This Guide Is For

This guide is for approved or invited users of an Orthodox Connect community.

Possible users:

- Parish members.
- Clergy.
- Monastics.
- Parish or group administrators.
- Inquirers or guests invited by the community.
- Members of a monastery, mission, ministry, or trusted group.

Users do not need to understand Docker, Caddy, Prosody, XMPP, Converse.js, Jitsi, JWT, federation, or server administration.

## 3. How Users Receive an Invite

Orthodox Connect is invite-only.

Users should receive an invite from a trusted administrator through an approved community contact path. The invite may arrive by email, direct message, printed note, or another local method chosen by the community.

Invite rules:

- Do not post invite links publicly.
- Do not forward invite links unless an administrator says to.
- Some invites work only once.
- Some invites expire.
- An administrator can revoke an invite.
- An invite does not automatically grant clergy, monastic, parish admin, diocesan admin, or platform admin status.

If an invite does not work, the user should contact the local administrator through the support contact path.

## 4. How To Create An Account

The basic account creation flow is:

1. Open the invite link.
2. Confirm that the invite page shows the expected community.
3. Enter the account details requested by the page.
4. Choose a strong password if password setup is shown.
5. Submit the form.
6. Wait for the next account status page.

The account may start as pending, limited, or guest-level until an administrator reviews it.

Users should not be asked to choose clergy, monastic, parish admin, diocesan admin, or platform admin status for themselves.

## 5. First Login Experience

After account creation, the user may see one of these states:

- Pending approval.
- Approved for basic access.
- Asked to request verification for a specific role.
- No rooms available yet.
- Access denied because the invite is invalid, expired, revoked, or already used.

If the account is pending, the user should wait for administrator review. The community may use an outside contact path to confirm identity before approval.

Users should not expect full chat or meeting access until approval and room access are granted.

## 6. How To Verify Identity (If Required)

Some users may need extra verification.

Supported verification types:

- Clergy.
- Monastic.
- Parish admin.

The user flow is:

1. Sign in to the portal.
2. Open the verification request area if it is available.
3. Choose the needed verification type.
4. Add a short note if the local policy asks for one.
5. Submit the request.
6. Wait for an administrator decision.

Important rules:

- Users cannot approve themselves.
- Users cannot self-assign clergy or monastic status.
- Users cannot self-assign parish admin status.
- Approved verification may add a visible role or badge.
- Rejected verification may include a reason visible only where policy allows.
- Verification decisions are made by administrators, not by software automation.

## 7. Understanding Roles And Badges

Roles control what a user may see or do.

Common roles may include:

- Guest.
- Inquirer.
- Member.
- Verified Clergy.
- Verified Monastic.
- Parish Admin.
- Diocesan Admin.
- Platform Admin.

Badges or labels should come from administrator-approved portal data. A display name, chat nickname, or meeting name is not proof of a role.

If a role looks wrong, the user should contact an administrator. Users should not edit their display name to imitate a verified role.

## 8. Joining Rooms And Channels

Rooms and channels are group spaces for chat.

A user may see only the rooms they are allowed to access. Room access can depend on:

- Account approval.
- Parish or group membership.
- Assigned roles.
- Clergy or monastic verification.
- Explicit room membership.
- Suspension or disabled account state.

Common room types:

- General member rooms.
- Group-only rooms.
- Clergy-only rooms.
- Monastic-only rooms.
- Admin-only rooms.
- Invite-only rooms.

If a room is missing, it may be restricted. The user should ask an administrator rather than asking another user to forward private room content.

## 9. Sending Messages And DMs

Chat is provided through the web chat frontend.

Basic guidance:

- Use rooms for group discussions.
- Use direct messages only where the community policy allows them.
- Keep private or pastoral matters in the correct approved space.
- Do not share invite links in rooms unless an administrator says to.
- Do not post passwords, recovery codes, meeting tokens, or private administrator notes.
- Report suspicious messages to an administrator.

Message history, notifications, and encryption behavior may depend on the configured XMPP client and server settings. Users should not assume all chat is end-to-end encrypted unless the community has tested and documented that exact workflow.

## 10. Joining Meetings (Jitsi)

Video meetings use Jitsi.

The normal meeting flow is:

1. Sign in or use an approved meeting link.
2. Open the meeting link from the portal, chat, or an administrator-approved message.
3. Allow camera and microphone access in the browser if needed.
4. Join using the name expected by the community.

Meeting rules:

- Meeting creation is restricted to approved roles.
- Anonymous users should not be able to create public rooms.
- Guests can join only where guest access is explicitly allowed.
- A meeting name alone does not grant access.
- Do not share meeting links publicly.
- Do not share meeting tokens or technical link contents.

If a meeting link fails, the user should ask the meeting organizer or local administrator.

## 11. Basic Security Advice

Users should follow basic account safety rules.

Advice:

- Use a strong password.
- Do not reuse a password from another site.
- Do not share your password.
- Do not share invite links publicly.
- Do not forward private room content without permission.
- Check that the site address matches the community address you were given.
- Report unexpected login prompts, changed links, or suspicious messages.
- Log out on shared computers.
- Tell an administrator if your account may be compromised.

Administrators may require stronger review for clergy, monastic, parish admin, diocesan admin, or platform admin accounts.

## 12. Mobile Usage Notes

The first supported mobile path is the web browser.

Users can normally:

- Open invite links on a phone.
- Check account status in the portal.
- Use web chat through the chat site.
- Open meeting links through the meeting site.

Native XMPP mobile apps are planned for later guidance after account provisioning and client testing are complete. Users should not assume that a third-party chat app will show Orthodox Connect roles or badges correctly.

For meetings, users may be asked to use a mobile browser or the Jitsi app depending on the community's instructions.

## 13. Troubleshooting Basics

Common problems:

- Invite expired: Ask an administrator for a new invite.
- Invite revoked: Ask an administrator for help.
- Invite already used: Ask an administrator to check whether a new invite is needed.
- Account pending: Wait for administrator review.
- Cannot see a room: The room may be restricted.
- Cannot send messages: The account may lack approval, room access, or chat setup.
- Cannot join a meeting: The meeting may require approval, a valid link, or a current token.
- Browser warning: Stop and contact an administrator before entering a password.
- Password problem: Use the approved local support path. Full account recovery is not complete in the current MVP.

Users should not send screenshots that contain passwords, invite links, meeting tokens, private messages, or private room names unless an administrator specifically asks for a safe version.

## 14. Support Contact Placeholder

Each deployment should replace this placeholder with its own support instructions outside this repository.

Placeholder:

```text
For help, contact your local Orthodox Connect administrator through the contact method provided by your parish, monastery, mission, or community.
```

Do not commit real names, phone numbers, private email addresses, invite links, meeting links, or emergency contacts to this repository.

## 15. Rollback Plan

If onboarding guidance is wrong or causes user confusion, roll it back without changing user data.

Rollback steps:

1. Stop sending the incorrect guide to new users.
2. Replace it with the last known-good guidance.
3. Notify administrators of the correction.
4. Review whether any users received bad invite, login, room, or meeting instructions.
5. Revoke exposed invite links if needed.
6. Rotate exposed secrets or meeting tokens if needed.
7. Confirm public registration remains disabled.
8. Confirm open federation remains disabled.
9. Confirm Jitsi meeting creation remains authenticated.
10. Confirm admin routes remain role-gated.
11. Record the correction in operator notes.

Rollback must not delete portal users, groups, roles, invites, verification records, rooms, meetings, audit events, Prosody data, Jitsi state, backups, or unrelated service configuration.
