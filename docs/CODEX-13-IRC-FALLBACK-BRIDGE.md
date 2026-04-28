# Orthodox Connect IRC Fallback and Bridge

## IRC Purpose

IRC is a possible post-MVP fallback or bridge for communities that already use IRC or need a simple text-only emergency channel.

IRC must not become the primary Orthodox Connect trust layer. The portal remains authoritative for invitations, approval, verification, roles, room policy, suspension, and audit records. Prosody and Converse.js remain the primary chat model for Orthodox Connect.

IRC may be useful only when the deployment has a clear use case, tested software, and a moderation policy that accepts IRC's weaker identity guarantees.

## What IRC Is Suitable For

IRC can be suitable for:

- Text-only fallback communication during a partial web chat outage.
- Operator coordination during an incident.
- A low-bandwidth parish or group help channel.
- Bridging a small number of non-sensitive announcement or support rooms.
- Migrating an existing community away from IRC gradually.
- Temporary read-only notices during disaster recovery.
- Technical maintainer support where participants already understand IRC.

IRC works best for non-sensitive, low-trust, low-feature communication where message history, verified status, room access, and user experience expectations are modest.

## What IRC Is Not Suitable For

IRC is not suitable for:

- Primary identity or verification.
- Clergy or monastic status proof.
- Sensitive pastoral conversation.
- Private clergy, monastic, admin, youth, or restricted rooms.
- Replacing portal invitations, approvals, roles, or audit records.
- Reliable mobile push notifications.
- Strong end-to-end encryption guarantees.
- Jitsi meeting authentication.
- Account recovery.
- Open public chat for unverified users.

IRC nicknames and channel operator status must not be treated as Orthodox Connect verification.

## Fallback-Only Mode

Fallback-only mode means IRC runs as a separate emergency or legacy text channel without bridging live Orthodox Connect rooms.

Fallback-only policy:

- Use only for non-sensitive rooms.
- Keep membership instructions limited to approved users.
- Do not use IRC to grant Orthodox Connect access.
- Do not use IRC to approve users, verify clergy, verify monastics, or assign roles.
- Do not publish private room names in public IRC topics.
- Prefer read-only announcement channels for disaster use.
- Keep the normal portal and XMPP stack authoritative once service is restored.

Fallback-only mode has the lowest integration risk because messages are not automatically copied between IRC and XMPP.

## Bridge Mode

Bridge mode means messages move between selected IRC channels and selected Orthodox Connect rooms.

Bridge mode should be deferred until:

- Prosody account provisioning is complete.
- Room access policy is enforced.
- Moderation and abuse workflows are defined.
- Message retention policy is reviewed.
- Identity mapping rules are tested.
- Operators accept the metadata and impersonation risks.

Bridge mode rules:

- Bridge only named, approved rooms.
- Start with non-sensitive rooms.
- Do not bridge clergy, monastic, admin, private, or pastoral rooms by default.
- Clearly label bridged users and bridged messages where clients support it.
- Do not let IRC channel presence imply Orthodox Connect room membership.
- Do not let IRC operators change portal roles or room policy.
- Disable bridge access quickly if abuse or leakage occurs.

Bridge mode increases support load because users may see different names, timestamps, formatting, moderation actions, and message history across clients.

## Authentication Model

Orthodox Connect authentication remains portal-controlled.

IRC authentication should be separate and limited:

- IRC account identity may help operators manage IRC access.
- IRC account identity must not grant portal access.
- Portal roles must not be inferred from IRC nicknames.
- Verified Orthodox Connect roles should not be mirrored to IRC unless policy and labeling are reviewed.
- Suspended Orthodox Connect users should lose IRC fallback or bridge access where identity mapping exists.
- Emergency operator channels should require known accounts or out-of-band verification.

If a bridge maps IRC users to Orthodox Connect users, that mapping must be explicit, reviewed, and revocable.

## NickServ and Account Policy

If an IRCd with services is used later, NickServ or an equivalent account service should be required for any non-public fallback channel.

Policy:

- Require registered nicknames for access to private or semi-private IRC channels.
- Reserve names that could impersonate clergy, monastics, parish admins, diocesan admins, platform admins, or official parish accounts.
- Require administrators to document the relationship between IRC accounts and portal users where access is restricted.
- Do not allow users to register misleading official names.
- Remove or rename accounts that imitate verified roles.
- Review stale IRC accounts before enabling bridge mode.

Nickname registration does not equal Orthodox Connect verification. A registered nickname only proves control of that IRC account.

## Channel Policy

IRC channels must be intentionally scoped.

Allowed channel types:

| Channel Type       | Use Case                         | Default |
| ------------------ | -------------------------------- | ------- |
| operator_fallback  | Technical incident coordination. | Allowed |
| public_notice      | Read-only emergency notices.     | Allowed |
| member_help        | Basic user support.              | Review  |
| parish_general     | Non-sensitive broad chat.        | Review  |
| bridge_test        | Disposable bridge testing.       | Review  |
| clergy_private     | Clergy conversation.             | Denied  |
| monastic_private   | Monastic conversation.           | Denied  |
| admin_private      | Admin conversation.              | Denied  |
| pastoral_private   | Sensitive pastoral conversation. | Denied  |

Channel rules:

- Keep channel names generic enough to avoid leaking sensitive group details.
- Restrict channel operator powers to trusted admins.
- Use invite-only or registered-only modes for non-public fallback channels.
- Keep topics free of private links, invite tokens, recovery tokens, and meeting secrets.
- Review channel logs before retaining or backing them up.

## Clergy Impersonation Risks

IRC creates specific impersonation risk because nicknames are easy to mimic and clients may not show account status clearly.

Controls:

- Reserve obvious clergy, monastic, admin, and parish official nicknames.
- Do not allow unverified users to use titles that imply verified status.
- Do not display IRC nicknames as verified Orthodox Connect labels.
- Use portal-visible verification as the source of truth.
- Warn users that IRC nicknames are not proof of clergy or monastic status.
- Keep sensitive clergy and monastic rooms off IRC by default.
- Audit any manual mapping between IRC accounts and portal users.

If a clergy or monastic impersonation incident occurs, IRC access should be suspended for the affected channel until names, mappings, and logs are reviewed.

## Logging Policy

IRC logging must follow the same privacy posture as the rest of Orthodox Connect.

Log intentionally:

- IRC service start, stop, restart, and errors.
- Authentication failures.
- Channel join failures for restricted channels.
- Operator actions.
- Bridge start, stop, and errors if a bridge exists.
- Abuse-related kicks, bans, and account changes.

Avoid logging:

- Passwords.
- Invite tokens.
- Recovery tokens.
- Message bodies by default.
- Private room content.
- Full hostmasks if not needed.
- Full request or command payloads containing secrets.

Channel logs should be disabled by default unless a deployment has a clear policy. If channel logs are enabled, they must be treated as sensitive records and excluded from Git.

## Abuse Controls

IRC abuse controls should support, not replace, portal moderation.

Controls:

- Registered-only channels for restricted fallback use.
- Invite-only channels for non-public groups.
- Channel operator limits.
- Nickname reservation for official names.
- Kicks and temporary bans for disruption.
- Permanent bans for repeated or severe abuse.
- Bridge shutdown for leakage or impersonation.
- Manual review before restoring access after impersonation.
- Audit notes in the portal for incidents that affect Orthodox Connect users.

Public IRC access increases spam and impersonation risk. Open public IRC channels should not be connected to Orthodox Connect rooms.

## Disaster and Fallback Usage

IRC fallback may be useful if the normal web chat path is unavailable but basic network access remains.

Disaster use cases:

- Operators coordinate while repairing portal, Caddy, Prosody, or database issues.
- Approved users receive read-only notices.
- Administrators publish a temporary support contact.
- Existing IRC communities continue limited chat during migration.

Disaster rules:

- Do not distribute new invite links through public IRC.
- Do not perform verification decisions in IRC.
- Do not share database details, secrets, backup paths, or private host information.
- Move users back to portal and XMPP once service is restored.
- Record important decisions in the portal audit trail after recovery.

IRC is not a replacement for backups, restore testing, DNS control, monitoring, or operator runbooks.

## Migration Path From Existing IRCd and Services

Some communities may already have an IRCd, NickServ, ChanServ, channel logs, and user expectations.

Migration path:

1. Inventory existing IRC servers, services, channels, operators, and logs.
2. Identify which channels are public, member-only, admin-only, or sensitive.
3. Freeze creation of new official IRC channels during migration planning.
4. Map active IRC accounts to portal users only where needed.
5. Reserve official names before announcing migration.
6. Move sensitive conversation to Orthodox Connect rooms instead of bridging it.
7. Create read-only IRC notices pointing users to the portal when appropriate.
8. Test any bridge with a disposable channel first.
9. Retire old channels after users have moved, or keep them as fallback-only.

Existing IRC logs should not be imported into Orthodox Connect unless privacy, consent, and retention policy have been reviewed.

## Risks and Limitations

Risks:

- Weak identity compared with portal-approved accounts.
- Clergy, monastic, and admin impersonation.
- Message leakage through bridges.
- Channel names and logs exposing sensitive groups.
- Different moderation state between IRC and XMPP.
- Increased support load for non-technical users.
- Public IRC spam and abuse.
- Bridge outages or duplicate messages.
- Inconsistent history and search behavior.
- Existing IRC logs containing old sensitive content.

Limitations:

- IRC is not implemented in the current repository.
- No IRC service or bridge is deployed.
- No IRC account provisioning exists.
- No tested bridge software has been selected.
- IRC does not carry Orthodox Connect verification labels by default.
- IRC cannot enforce portal policy unless explicit integration is built later.

## Rollback Plan

Rollback must be able to remove IRC access or bridging without disrupting portal, Prosody, Converse.js, Jitsi, backups, or audit records.

Rollback steps:

1. Disable the affected bridge or IRC fallback channel.
2. Confirm Orthodox Connect rooms still work through the normal web chat path.
3. Remove IRC channel references from user guidance.
4. Preserve portal audit events and operator incident notes.
5. Review IRC logs for sensitive exposure.
6. Revoke or rename misleading IRC accounts.
7. Remove IRC users from bridged room mappings.
8. Notify affected administrators and users through the normal portal or approved contact path.
9. Document whether IRC should be restored, reduced to fallback-only, or retired.

Rollback must not delete portal users, portal roles, verification records, XMPP rooms, meeting records, backups, or unrelated service data.
