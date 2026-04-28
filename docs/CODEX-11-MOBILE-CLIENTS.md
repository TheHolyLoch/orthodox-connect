# Orthodox Connect Mobile Clients

## Mobile Access Goals

Mobile access should let approved users reach Orthodox Connect from common phones without weakening the invite-only, manually verified trust model.

Goals:

- Make chat, portal notices, and meeting links usable from mobile browsers.
- Give administrators a clear list of tested native XMPP clients before recommending them to parishes or monasteries.
- Keep public registration disabled.
- Keep clergy, monastic, parish admin, and platform admin status controlled by portal verification.
- Avoid claiming platform-wide end-to-end encryption unless a specific client and room workflow has been tested.
- Avoid adding push notification services until metadata and account ownership are reviewed.

Mobile support must serve ordinary parish users first. A person should not need to understand XMPP, Prosody, WebSocket, BOSH, JWT, or federation to join the community.

## Beginner-Friendly User Journey

The preferred journey is:

1. A trusted administrator creates an invite.
2. The user opens the invite link on a phone.
3. The user creates a portal account through the invite-only flow.
4. The user waits for approval or verification when required.
5. The user opens chat in the mobile browser as the first supported path.
6. The user joins allowed rooms based on verified role and group membership.
7. The user opens meeting links issued by the portal when allowed.
8. Native mobile client setup is offered only after Prosody account provisioning and client testing are complete.

Support material should use the community's own domain names and screenshots from the actual deployment. It should avoid asking users to choose between many clients unless they already want a native app.

## Supported Client Options

| Option                    | Status   | Use Case                                      | Notes |
| ------------------------- | -------- | --------------------------------------------- | ----- |
| Mobile browser portal     | Required | Invites, approval status, admin review, links. | Must use the same portal role checks as desktop. |
| Mobile browser chat       | Required | First chat path through Converse.js.           | Uses the existing reverse proxy and browser XMPP transport. |
| Android native XMPP app   | Planned  | Better notifications and mobile chat UX.       | Requires account provisioning and client compatibility testing. |
| iOS native XMPP app       | Planned  | Better notifications and mobile chat UX.       | Requires account provisioning and client compatibility testing. |
| Jitsi mobile browser/app  | Planned  | Meetings issued by the portal.                | Must keep JWT meeting access and role-gated room creation. |
| Branded Orthodox Connect app | Deferred | One official app for non-technical users.   | Only after the web and XMPP workflows are stable. |

Native XMPP clients must be treated as supported only after testing login, MUC room access, message history, file upload policy, OMEMO behavior, account removal, suspension handling, and verification-label limitations.

## Recommended Android Clients

Android recommendations should start with standards-based XMPP clients that can connect to a self-hosted Prosody server.

First candidates:

- Conversations: primary Android candidate for testing because it is a mature XMPP client, supports common mobile XMPP features, and is widely used in the XMPP ecosystem.
- Cheogram Android: secondary candidate for testing, especially where users need a Conversations-family client available through F-Droid.

Android policy:

- Do not recommend clients that require public account creation with an unrelated provider as the normal path.
- Do not recommend phone-number onboarding as the primary Orthodox Connect account model.
- Do not claim that verified Orthodox Connect roles will display correctly in a native client until tested.
- Document exact setup steps only after Prosody account provisioning exists.
- Test battery behavior, background connection behavior, message sync, MUC notifications, and OMEMO device handling before parish-wide use.

## Recommended iOS Clients

iOS recommendations should start with clients that can connect to a self-hosted XMPP server and support ordinary chat and group chat workflows.

First candidates:

- Monal: primary iOS candidate for testing because it is an active XMPP client for iOS and macOS.
- Siskin IM: secondary iOS candidate for testing because it is an XMPP client for iPhone and iPad with mobile-focused features.

iOS policy:

- Test push behavior carefully before recommending a client as reliable for urgent pastoral or administrative notices.
- Do not claim OMEMO or media behavior is consistent across iOS clients until tested with Orthodox Connect rooms.
- Do not rely on an iOS client to show clergy, monastic, or administrator verification labels unless the portal or client integration explicitly supports it.
- Keep the mobile browser chat path available even if a native iOS client is recommended.

## Web Portal Mobile Mode

The portal should be usable from a phone before a native mobile app is considered.

Mobile portal requirements:

- Invite redemption works on narrow screens.
- Login and approval status pages fit on narrow screens.
- Admin lists remain readable for basic review tasks.
- Verification decisions remain admin-only.
- Room and meeting links are easy to open.
- Sensitive admin actions require clear confirmation.
- Internal notes are not exposed to ordinary users.

The portal should not try to replace a full XMPP mobile client. Its mobile role is onboarding, identity, verification, room policy visibility, meeting links, and admin review.

## Push Notification Considerations

No push notification service is added in the current design.

Push notification review must happen before production mobile recommendations because push can expose metadata to mobile operating system vendors, app stores, app developers, or third-party push gateways.

Future push review should decide:

- Whether native XMPP clients use their own push infrastructure.
- Whether Prosody push modules are needed.
- What metadata leaves the Orthodox Connect server.
- Whether administrators can disable push for sensitive rooms.
- Whether push is acceptable for clergy, monastic, or private rooms.
- How suspended users lose mobile notification access.
- How push failures are explained to users.

The MVP posture is conservative: mobile browser access first, native clients later, and no new push service until reviewed.

## OMEMO and Device Verification Guidance

OMEMO is client-side encryption and depends on the selected client, device state, room type, and user behavior. Orthodox Connect must not describe all chat as end-to-end encrypted by default.

Guidance:

- Treat OMEMO as a client feature to test, not a platform guarantee.
- Teach users that adding a new phone may require device verification.
- Teach users that old message history may not decrypt on a new device.
- Tell users to report unexpected device warnings.
- Do not use screenshots of OMEMO status as proof of clergy or monastic verification.
- Review OMEMO behavior separately for one-to-one chat and group chat.
- Keep server-side metadata risks visible in user guidance.

Admins should decide whether sensitive rooms require native clients with tested OMEMO support or whether those rooms should avoid mobile client recommendations until policy is clearer.

## Jitsi Mobile Access

Jitsi mobile access should use the same authenticated meeting model as desktop.

Requirements:

- Meeting links are issued by the portal.
- Room creation remains limited to approved roles.
- Guests join only where explicitly allowed.
- JWT access remains required.
- Meeting names alone do not grant access.
- Anonymous public room creation remains disabled.
- Jitsi over Tor is not promised.

Users may join from a mobile browser or the Jitsi mobile app after deployment testing. The support guide should tell users which path the local administrator has tested.

## Account Recovery on Mobile

Mobile account recovery must not bypass verification, suspension, invite controls, or admin review.

Future recovery requirements:

- Lost phone recovery should require a reviewed recovery path.
- Privileged roles need stricter recovery review.
- Device changes should not automatically preserve verified status if the account is suspicious.
- Recovery tokens must expire and must not appear in logs.
- Admins should be able to revoke sessions and require password reset after device loss.
- Users should be told to contact an administrator if a phone is lost or stolen.

Until account recovery is implemented, documentation should say that recovery is handled by local administrators.

## Security Risks

Mobile risks:

- Phones are lost, shared, unlocked, or backed up to cloud accounts.
- Native clients may hide Orthodox Connect verification status.
- Push notifications may reveal room names, sender names, or message previews.
- External app updates may change behavior without operator review.
- OMEMO device confusion can cause users to miss messages or trust the wrong device.
- Mobile browsers may keep sessions open longer than expected.
- Meeting links may be forwarded outside the approved group.
- Users may install lookalike or unsupported XMPP apps.
- App store availability can change by country or policy.

Mitigations:

- Prefer short, local support instructions.
- Keep role and verification truth in the portal.
- Keep sensitive rooms role-gated.
- Keep meeting creation role-gated.
- Encourage screen locks and prompt lost-device reports.
- Avoid message previews for sensitive rooms where possible.
- Review client recommendations on a schedule.

## User Support Notes

Support should be written for clergy, monastics, parish staff, and ordinary members.

Support notes should cover:

- Which mobile path is supported first.
- The community's exact portal and chat domains.
- How to redeem an invite.
- How to wait for approval.
- How to join chat from the phone browser.
- How to join an approved meeting.
- What to do after a lost phone.
- What to do if a room is missing.
- What to do if a client asks about unknown devices.
- Who to contact for local help.

Support notes should avoid long protocol explanations. XMPP, Prosody, Converse.js, WebSocket, BOSH, JWT, and OMEMO details belong in operator documentation unless a user-facing warning needs them.

## Future Branded App Option

A branded app is deferred.

Reasons to wait:

- The portal must first have stable production authentication.
- Prosody account provisioning must be complete.
- Mobile XMPP behavior must be tested with real policies.
- Push notification policy must be decided.
- Jitsi mobile joining must be tested.
- Account recovery must be stable.
- App store maintenance creates long-term operational duties.

Possible future app directions:

- A thin wrapper around the mobile portal and web chat.
- A custom XMPP client profile for Orthodox Connect accounts.
- A branded fork or configuration of an existing F/OSS client, if licensing and maintenance fit.

The first branded app should reduce user confusion, not add a second identity or messaging model.

## Rollback Plan

Rollback should remove mobile-specific guidance or access paths without disrupting desktop web access.

Rollback steps:

1. Mark a native client recommendation as unsupported in local user guidance.
2. Remove setup instructions for the affected client.
3. Keep portal and web chat available through normal HTTPS.
4. Revoke affected sessions or credentials if a client exposed account data.
5. Tell users to use the mobile browser path while the issue is reviewed.
6. Review audit events for suspicious access.
7. Review logs for client-specific errors without collecting message bodies.
8. Update administrator support notes before recommending the client again.

Rollback must not delete users, roles, rooms, verification records, meetings, audit events, or unrelated service data.
