# Orthodox Connect Feedback and Iteration

## 1. Feedback Goals

Feedback should help Orthodox Connect improve without drifting away from the invite-only, manually verified, role-aware MVP.

Goals:

- Find bugs in current workflows.
- Improve usability for non-technical users.
- Improve administrator workflows.
- Catch security concerns early.
- Keep documentation accurate.
- Keep future feature requests separate from implemented behavior.
- Avoid collecting private data that is not needed.
- Avoid uncontrolled scope growth.

Feedback is not an approval path for public registration, open federation, automatic verification, anonymous meeting creation, or new services.

## 2. Feedback Sources

### Users

General users can report:

- Invite onboarding problems.
- Chat and room confusion.
- Missing expected rooms.
- Meeting access problems.
- Plain-language issues in screens or guides.
- Basic accessibility problems.

User feedback should not include passwords, invite tokens, meeting tokens, private keys, session cookies, or private conversations.

### Clergy

Clergy can report:

- Verification status clarity.
- Clergy-only room access problems.
- Meeting access problems.
- Impersonation concerns.
- User-facing language that may confuse pastoral or parish context.

Clergy feedback should not be used as an automatic verification decision. Verification remains an administrator-controlled workflow.

### Parish Admins

Parish admins can report:

- Invite workflow problems.
- Verification review problems.
- Group and room management problems.
- Audit event clarity.
- User support patterns.
- Training and documentation gaps.

Parish admin feedback should include enough detail to reproduce the issue without exposing private user data.

### Platform Admins

Platform admins can report:

- Security concerns.
- Backup and restore problems.
- Deployment and routing issues.
- Service health problems.
- Role or permission drift.
- Jitsi authentication concerns.
- Documentation mismatches.

Platform admin feedback should keep real secrets, production `.env` values, logs with private data, and backup files out of shared issue notes.

## 3. Feedback Collection Methods

### In-App Placeholder

An in-app feedback option is future scope.

If added later, it should:

- Be available only to authenticated users.
- Include category selection.
- Avoid attaching logs automatically.
- Warn users not to include passwords, tokens, or private conversations.
- Include user identity and timestamp only as permitted by the privacy policy.
- Route security-sensitive reports to the correct admin scope.

No in-app feedback system is implemented by this document.

### Email Placeholder

Email feedback is a placeholder for deployments that choose an operator-controlled support address.

Rules:

- Do not commit real email addresses to this repository.
- Use a local deployment placeholder in user-facing docs until the operator sets a real contact path.
- Tell users not to email passwords, invite tokens, meeting tokens, or private keys.
- Do not use email to approve clergy, monastic, or parish admin status outside the portal audit workflow.

Email may be useful for support, but portal records remain the source of truth for roles and access.

### Periodic Review Sessions

Review sessions can collect structured feedback from admins and early users.

Suggested format:

- Review current bugs.
- Review recurring user confusion.
- Review admin workflow problems.
- Review documentation gaps.
- Review security concerns separately.
- Decide which items need action.
- Record decisions without real secrets or private user data.

Sessions should use fake or approved test examples. Do not display production private messages, invite links, JWTs, or raw logs in training or review meetings.

## 4. Categorisation of Feedback

### Bugs

Bugs are faults in implemented behavior.

Examples:

- Valid invite redemption fails.
- Expired invite is accepted.
- Revoked invite is accepted.
- Verification approval fails to assign the expected role.
- Room access is granted when policy should deny it.
- Meeting token issuance ignores role checks.
- Admin UI shows data outside the admin scope.
- Backup script fails to capture expected data.

Bugs affecting trust, access, secrets, backups, or audit records should be handled with higher priority.

### Usability Issues

Usability issues make implemented features hard to use.

Examples:

- Invite status text is unclear.
- Users cannot tell whether their account is pending.
- Room names are confusing.
- Role badges are unclear.
- Meeting access errors do not explain the next step.
- Admin lists are hard to scan.
- Documentation uses technical terms where plain language would work.

Usability changes must not weaken permission checks or expose private records.

### Feature Requests

Feature requests are requests for behavior not currently implemented.

Examples:

- Native mobile app.
- Push notifications.
- Library service.
- Tor onion access.
- Trusted federation.
- IRC bridge.
- Automated moderation.
- Public event pages.

Feature requests should be linked to the relevant design document when one exists. They should not be described to users as available until implemented and reviewed.

### Security Concerns

Security concerns need separate handling.

Examples:

- Public registration appears enabled.
- Open federation appears enabled.
- Anonymous Jitsi room creation appears possible.
- Internal ports appear exposed.
- Admin routes allow non-admin access.
- Invite, meeting, session, or JWT tokens appear in logs.
- Backups contain secrets in manifests.
- A user can self-assign a privileged role.
- A suspended account can still access rooms or meetings.

Security concerns should be triaged immediately by platform admins or technical operators. Public discussion should avoid exploit details until the issue is contained.

## 5. Prioritisation Model

Feedback should be prioritised by risk, user impact, and implementation scope.

Priority levels:

| Priority | Meaning |
| -------- | ------- |
| Critical | Active security exposure, data loss, broken restore path, or access control bypass. |
| High | Major workflow breakage for invites, verification, room access, Jitsi access, backups, or admin views. |
| Medium | Usability issue affecting common user or admin workflows. |
| Low | Minor text, layout, documentation, or rare workflow issue. |
| Deferred | Valid idea that belongs after MVP or requires a separate design pass. |

Security, access control, backups, audit integrity, and public exposure issues outrank cosmetic changes.

## 6. Review Cadence

Review cadence should match deployment maturity.

Suggested cadence:

- During first rollout: weekly feedback review.
- During active onboarding: weekly or fortnightly review.
- During stable operation: monthly review.
- After incidents: immediate review and follow-up.
- Before releases: review open critical and high-priority items.
- After releases: review new feedback within the first week.

Security concerns should not wait for the normal review cycle.

## 7. Decision-Making Process

Decisions should be explicit and recorded.

For each feedback item, decide:

- Is this implemented behavior, a bug, a usability problem, a feature request, or a security concern?
- Does it affect invite-only registration?
- Does it affect manual verification?
- Does it affect role-based room access?
- Does it affect authenticated Jitsi meetings?
- Does it affect backups, restore, logs, secrets, or audit events?
- Does it require a documentation update?
- Does it require a design document before implementation?
- Who has authority to approve the change?

Decisions should prefer small, reviewable changes that preserve the MVP trust model.

## 8. Change Approval Workflow

Change approval should depend on risk.

Suggested workflow:

1. Record the feedback item.
2. Categorise it.
3. Set priority.
4. Identify affected files, services, and documentation.
5. Decide whether a design document update is required.
6. Review security and privacy impact.
7. Approve or reject the change.
8. Implement in a scoped change.
9. Validate with fake or approved test data.
10. Update documentation where needed.
11. Communicate the result.

Approval expectations:

| Change Type | Approval Needed |
| ----------- | --------------- |
| Documentation correction | Documentation maintainer or responsible admin. |
| Minor usability wording | Responsible admin or maintainer. |
| Invite, verification, role, room, meeting, or audit behavior | Project maintainer plus admin review. |
| Security-sensitive behavior | Platform admin, technical operator, and maintainer review. |
| New service or major feature | Design document first, then implementation approval. |

No change should enable public registration, open federation, anonymous meeting creation, or real secrets in committed files.

## 9. Communication Back to Users

Users should receive plain status updates when feedback affects them.

Communication should say:

- Whether the issue was accepted, declined, fixed, or deferred.
- What changed in user-facing terms.
- Whether users need to do anything.
- Whether documentation was updated.
- Where to report follow-up problems.

Communication should not include:

- Private user data.
- Security exploit details before containment.
- Invite tokens.
- Meeting tokens.
- JWTs.
- Session cookies.
- `.env` values.
- Internal hostnames unless already public and safe.

If feedback is declined, state the practical reason, such as security, privacy, scope, or unsupported future feature.

## 10. Documentation Updates

Documentation should change when feedback shows a real gap.

Update docs when:

- A workflow is confusing.
- A setup step is missing or stale.
- A security warning is unclear.
- A role, room, invite, verification, meeting, backup, or restore behavior changes.
- A known limitation needs clearer wording.
- A future feature request needs a roadmap note.

Do not update docs to claim features are implemented when they are only planned. Do not add real contact details, real domains, real accounts, real logs, real backups, or real secrets.

Useful docs to review after feedback:

| Feedback Area | Documents |
| ------------- | --------- |
| User onboarding | `docs/CODEX-43-USER-ONBOARDING-GUIDE.md` |
| Admin onboarding | `docs/CODEX-44-ADMIN-ONBOARDING-GUIDE.md` |
| Training | `docs/CODEX-45-TRAINING-MATERIALS.md` |
| Identity and verification | `docs/CODEX-03-IDENTITY-VERIFICATION.md` |
| Security | `docs/CODEX-04-SECURITY-MODEL.md`, `docs/CODEX-30-THREAT-MODEL.md` |
| Testing | `docs/CODEX-15-TESTING-VALIDATION.md` |
| Operations | `docs/CODEX-29-ADMIN-OPERATIONS.md`, `docs/CODEX-39-OPERATIONS-RUNBOOK.md` |
| Go-live | `docs/CODEX-42-GO-LIVE-CHECKLIST.md` |

## 11. Risk of Uncontrolled Scope Growth

Feedback can easily turn a small private communications system into an unbounded platform.

Scope risks:

- Adding public social network features.
- Enabling public registration.
- Enabling open federation before trusted federation policy exists.
- Adding many bridges before identity mapping is solved.
- Adding mobile, library, Tor, IRC, moderation automation, or notification services before MVP stability.
- Turning admin feedback into broad custom workflows for one deployment.
- Adding features that increase support burden more than they help users.
- Treating training requests as proof that a complex feature is ready.

Controls:

- Keep MVP acceptance criteria visible.
- Require design documents for major features.
- Separate bug fixes from feature requests.
- Keep feature requests marked deferred until approved.
- Prefer improving current workflows before adding new ones.
- Reject requests that weaken registration, verification, access control, backups, audit records, or privacy.

The project should improve by measured iteration, not by adding every requested feature.

## 12. Rollback Plan

Feedback process rollback means undoing a bad process decision or withdrawing unsafe guidance.

Rollback steps:

1. Identify the feedback item, decision, documentation change, or planned change that caused risk.
2. Stop related implementation work if it has not shipped.
3. Withdraw or correct inaccurate user or admin communication.
4. Preserve feedback records, audit events, and relevant notes.
5. Reclassify the item if it was wrongly categorised.
6. Reopen review with the correct admin, maintainer, or technical operator.
7. Restore previous documentation wording if the new wording is inaccurate.
8. Rotate secrets if feedback handling exposed tokens, logs, `.env` values, backups, or private keys.
9. Confirm public registration remains disabled.
10. Confirm open federation remains disabled.
11. Confirm Jitsi authenticated meeting creation remains enabled.
12. Confirm admin routes and privileged actions remain role-gated.

Rollback must not change application code, Docker services, portal data, Prosody data, Jitsi state, backups, logs, or unrelated documentation in this design stage.
