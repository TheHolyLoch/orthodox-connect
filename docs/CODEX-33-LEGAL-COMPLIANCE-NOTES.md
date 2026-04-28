# Orthodox Connect Legal and Compliance Notes

## 1. Legal and Compliance Goals

These notes identify legal and compliance areas that operators should review before using Orthodox Connect with real parish, diocesan, monastic, or community data.

Goals:

- Keep Orthodox Connect aligned with its private, invite-only service model.
- Avoid public registration by default.
- Avoid open federation by default.
- Keep personal data collection minimal.
- Treat verification, moderation, audit, backup, and meeting data as sensitive.
- Identify areas that require local policy decisions before production use.
- Identify areas that require professional legal advice.
- Avoid making legal claims in product documentation.

This document is a design note. It is not legal advice and does not implement compliance controls.

Reference sources for operator review:

- UK ICO guidance on data protection: <https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/>
- UK ICO guidance on children's information: <https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/childrens-information/>
- UK ICO Children's code introduction: <https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/childrens-information/childrens-code-guidance-and-resources/introduction-to-the-childrens-code/>
- UK ICO content moderation and data protection guidance: <https://ico.org.uk/media/for-organisations/uk-gdpr-guidance-and-resources/online-safety-and-data-protection/content-moderation-and-data-protection-0-0.pdf>

## 2. Service Classification Assumptions

Orthodox Connect is designed as a private community communications platform, not a public social network.

Current assumptions:

- Accounts are invite-only.
- Users are manually reviewed.
- Public self-registration is disabled.
- Open XMPP federation is disabled.
- Meeting creation is authenticated and role-gated.
- Chat, meeting, and portal access are scoped by user state, group membership, roles, and explicit room policy.
- Operators control hosting, DNS, TLS, backups, and access policy.

These assumptions should be reviewed for each deployment. A service run by a parish, diocese, monastery, charity, school, club, or informal group may have different legal duties depending on jurisdiction, user base, governance, and whether minors can access it.

## 3. Private Membership Service Model

The preferred model is a private membership service for approved users.

Policy notes:

- Access should require invitation or administrator approval.
- Membership rules should be clear before users join.
- Administrators should know who may create invites.
- Administrators should know who may approve users.
- Administrators should know who may verify clergy, monastic, and parish admin status.
- Users should receive plain guidance on expected conduct, account status, and who to contact for support.
- Private room names and membership lists should not be exposed to users without access.
- Suspended or disabled users should lose access to portal, chat, rooms, and meetings.

The private membership model reduces public abuse risk, but it does not remove privacy, safeguarding, moderation, copyright, or data protection considerations.

## 4. Public-Facing Service Risks

Even a private service has public-facing surfaces.

Public-facing risks:

- The portal, chat, and meeting hostnames are visible on the internet.
- Invite redemption pages may be reachable by anyone with a link.
- Reverse proxy logs may contain IP addresses, user agents, paths, and error metadata.
- Jitsi media traffic may reveal meeting participation metadata.
- Public DNS records may reveal service names.
- TLS certificate transparency logs may reveal public hostnames.
- A misconfigured service could expose registration, federation, internal ports, or admin endpoints.

Controls to preserve:

- Keep public registration disabled.
- Keep open federation disabled.
- Keep internal service ports private.
- Keep admin routes role-gated.
- Keep Prosody admin interfaces private.
- Keep Jitsi room creation authenticated.
- Avoid putting secrets, invite tokens, recovery tokens, or JWT bodies in URLs where possible.

Public-facing behavior should be reviewed before using real domains.

## 5. Age-Related Access Considerations

Orthodox Connect may be used by families, youth groups, catechumens, schools, or parish ministries. Operators must decide whether minors are allowed and under what supervision model.

Design considerations:

- Decide whether minors may have accounts.
- Decide whether parents or guardians must be involved.
- Decide whether youth rooms are allowed.
- Decide which adults may administer or moderate youth spaces.
- Avoid direct message policies that conflict with local safeguarding rules.
- Avoid collecting birth dates unless a reviewed age policy requires them.
- Avoid profiling or engagement-maximising features for minors.
- Keep reporting and escalation paths clear for youth-related concerns.
- Review whether the UK Children's code or similar local rules may apply.

If children are likely to access the service, operators should review child data protection, safeguarding, content moderation, and supervision requirements before deployment.

## 6. UK Data Protection Considerations

UK deployments should be reviewed against UK data protection requirements and ICO guidance before production use.

Data protection areas to review:

- Who is the controller for each deployment.
- Whether any processor relationship exists with a hosting provider, technical maintainer, or managed service operator.
- Lawful basis for each type of processing.
- Data minimisation.
- Transparency notices for users.
- Retention periods.
- User rights handling.
- Security measures.
- Backup and restore handling.
- Breach response process.
- Children and youth data handling if minors may access the service.
- Special category data risk if religious affiliation or role data is handled.

Orthodox Connect may reveal religious community membership, clergy status, monastic status, parish affiliation, meeting participation, and room membership. Operators should treat this data as sensitive and obtain professional advice before production deployment.

## 7. User-Generated Content Considerations

User-generated content may include chat messages, meeting names, room names, uploaded files if added later, reports, and administrator notes.

Policy questions:

- Whether message archives are enabled.
- How long message history is retained.
- Who can see room history.
- Whether direct messages are allowed.
- Whether users may upload files.
- Whether moderators can view reported content.
- How disputed or unlawful content is handled.
- Whether content can be exported.
- Whether deleted or suspended users retain historical content in rooms.

Rules to preserve:

- Do not store message bodies in portal audit records by default.
- Do not expose private room content to unauthorised users.
- Do not use chat uploads as a library service.
- Do not add public file upload without a reviewed policy.
- Do not claim end-to-end security unless that has been verified for the exact client and workflow.

## 8. Moderation Record Considerations

Moderation records can contain sensitive allegations, screenshots, excerpts, account metadata, room names, and administrator decisions.

Policy notes:

- Collect only the evidence needed for review.
- Keep report notes short and factual.
- Avoid turning moderation notes into pastoral, personnel, or disciplinary files.
- Restrict report access by administrator scope.
- Avoid storing passwords, invite tokens, recovery tokens, JWTs, session cookies, full request bodies, or unnecessary message content in reports.
- Preserve audit records for moderation actions.
- Define temporary and permanent suspension policy.
- Define who reviews appeals.
- Define how long moderation records are retained.
- Define how moderation records appear in backups and exports.

Moderation workflows should not replace pastoral care, safeguarding procedures, civil reporting obligations, or professional advice where those apply.

## 9. Clergy Verification Data Considerations

Clergy, monastic, and parish administrator verification data is sensitive because it records trust decisions and may reveal religious status, vocation, community role, jurisdiction, or local standing.

Policy notes:

- Users must not self-assign clergy, monastic, parish admin, diocesan admin, or platform admin status.
- Verification decisions must be made by authorised administrators.
- Every verification decision should be tied to an administrator.
- Every verification decision should create an audit event.
- Verification notes should be minimal.
- Rejection reasons should be visible only to authorised administrators unless a user-safe message is intentionally shown.
- Revocation should create a new record rather than deleting history.
- Cross-server clergy verification should not transfer automatically.

Operators should decide who may verify clergy and monastic status before production use. Broader diocesan or multi-parish deployments may require stricter review and professional guidance.

## 10. Copyright and Library Considerations

The library service is not implemented in the current MVP, but future PDF and ebook support creates copyright and permissions risk.

Policy notes:

- Do not upload books, PDFs, ebooks, cover images, or metadata to Git.
- Do not assume a physical copy gives permission to upload or distribute a digital copy.
- Do not upload purchased ebooks unless the licence permits the intended sharing.
- Mark public-domain, licensed, locally authored, and restricted-use materials separately.
- Require administrator review before import.
- Keep library access role-based and separate from chat access unless portal policy explicitly links them.
- Remove disputed material while permissions are reviewed.
- Include library files and metadata in backups only after the library service exists and backup support is reviewed.

Copyright and licence questions require professional advice or written permission from the rights holder where appropriate.

## 11. Lawful Request Handling Placeholder

Operators may receive requests for records, logs, user information, moderation records, or content.

Placeholder process:

1. Record the request date, requester, scope, and delivery method.
2. Do not disclose data immediately unless an approved emergency policy requires action.
3. Preserve relevant logs and audit records without altering them.
4. Verify the request through an appropriate out-of-band process.
5. Identify the responsible operator or governing body.
6. Seek professional legal advice before disclosure where required.
7. Disclose only the minimum data approved for the request.
8. Record what was disclosed, when, by whom, and under what authority.

Do not add automated lawful request tooling until a later reviewed implementation pass defines the process.

## 12. Jurisdiction Risks

Orthodox Connect deployments may involve users, administrators, servers, churches, dioceses, monasteries, hosting providers, and DNS providers in different jurisdictions.

Risks to review:

- Where the server is hosted.
- Where the operator is established.
- Where users are located.
- Where backups are stored.
- Which law applies to user data.
- Whether religious affiliation data receives special protection.
- Whether minors can access the service.
- Whether federation or bridges move data across borders.
- Whether Tor, IRC, or future mobile push services change data flows.
- Whether a hosting provider has access to server-side data.

Operators should not assume one deployment's legal review applies to another jurisdiction.

## 13. What Requires Professional Legal Advice

Professional legal advice is required before relying on any policy in production.

Areas that should be reviewed:

- Controller and processor roles.
- UK GDPR, Data Protection Act 2018, and local data protection obligations.
- Whether religious affiliation or verified clergy or monastic status creates special category data handling duties.
- Privacy notices and terms of use.
- Age-related access policy.
- Safeguarding and youth communication rules.
- Moderation, evidence retention, and appeals.
- Data retention and deletion.
- Data export and migration.
- Breach response.
- Lawful request handling.
- Cross-border hosting, backups, federation, bridges, or remote services.
- Copyright and library import rules.
- Liability, governance, and operator responsibilities.

Repository documentation should remain operational and design-focused. It should not present itself as a legal compliance guarantee.

## 14. Rollback Plan

Rollback should remove or pause legally risky behavior without deleting trust records or evidence.

Rollback steps:

1. Disable the affected route, workflow, room, meeting, bridge, federation scope, or library access.
2. Preserve relevant audit events, logs, reports, backups, and operator notes.
3. Stop new invites, verification decisions, room access changes, or meeting creation if the issue affects account trust.
4. Confirm public registration remains disabled.
5. Confirm open federation remains disabled.
6. Confirm admin routes remain role-gated.
7. Confirm Jitsi room creation remains authenticated.
8. Review whether data was exposed, copied, exported, or backed up.
9. Rotate secrets if tokens, credentials, or private keys were exposed.
10. Seek professional legal advice before notifying users, deleting records, or disclosing data where legal duties may apply.
11. Record the rollback decision and follow-up actions.

Rollback must not delete portal users, groups, roles, invites, verification records, rooms, meetings, audit events, backups, or moderation records unless a reviewed retention or legal process requires it.
