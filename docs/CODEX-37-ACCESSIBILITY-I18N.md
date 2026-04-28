# Orthodox Connect Accessibility and Internationalisation

## 1. Accessibility Goals

Accessibility should make Orthodox Connect usable by ordinary parish, diocesan, monastic, and community users without weakening the invite-only trust model.

Goals:

- Keep invite redemption, account status, verification requests, chat access, meeting links, and admin review workflows usable with common assistive technology.
- Support desktop and mobile browsers.
- Keep language clear for non-technical users.
- Make administrator workflows readable, predictable, and safe under keyboard-only use.
- Make status, role, verification, room, and meeting access visible without relying only on colour.
- Avoid exposing internal service names, tokens, secrets, or private notes in accessibility text.
- Treat accessibility defects in invite, verification, admin, and meeting workflows as operational risks before broad deployment.

Accessibility must not bypass authentication, role checks, suspension state, room policy, meeting policy, or audit requirements.

## 2. Target Accessibility Baseline

The target baseline is WCAG 2.2 AA where practical. This is a design target, not a claim of certification.

Baseline requirements:

- Use semantic HTML for pages, forms, headings, tables, and landmarks.
- Keep every form field labelled.
- Keep focus order logical.
- Keep visible focus indicators.
- Support keyboard-only navigation.
- Provide clear field-level validation errors.
- Keep pages usable at browser zoom levels common for low-vision users.
- Avoid flashing, distracting motion, and hover-only controls.
- Keep admin tables readable and offer mobile-friendly views where practical.
- Test the invite, verification, room, meeting, and admin workflows before production use.

Third-party interfaces such as Converse.js and Jitsi must be reviewed in practice. Their accessibility limits should be documented honestly rather than hidden by Orthodox Connect branding.

## 3. Keyboard Navigation Requirements

All portal workflows should work without a mouse.

Requirements:

- Provide a logical tab order from header, navigation, main content, forms, tables, and action buttons.
- Keep skip links or equivalent navigation shortcuts for repeated page structure.
- Make buttons and links visually distinct.
- Keep all admin actions reachable by keyboard.
- Keep confirmation dialogs keyboard-accessible.
- Move focus into modal dialogs when opened and return focus when closed.
- Avoid keyboard traps in dialogs, menus, embedded chat, and meeting views.
- Make table actions reachable with clear link or button labels.
- Use server-side permission checks even when UI controls are hidden.

Chat and meeting keyboard behaviour depends partly on Converse.js and Jitsi. Any deployment guidance should note tested browser and client behaviour.

## 4. Screen Reader Requirements

Screen reader support should make account state and trust decisions understandable without exposing admin-only data.

Requirements:

- Use one clear `h1` per page and ordered section headings.
- Use landmarks for navigation, main content, and footer where appropriate.
- Associate labels, hints, and errors with form fields.
- Announce successful invite redemption, verification submission, approval, rejection, room changes, and meeting creation where the UI updates without a full page reload.
- Use text labels for roles and verification state, not icon-only or colour-only indicators.
- Give icon actions accessible names if icons are used.
- Use table headers and captions for admin data tables.
- Avoid unexpected focus changes after filtering, sorting, or submitting forms.
- Keep internal verification notes, raw tokens, JWT contents, and secrets out of accessible labels and live regions.

Status text should be brief and direct, such as `Pending review`, `Approved`, `Rejected`, `Suspended`, `Clergy verified`, or `Room unavailable`.

## 5. Colour Contrast Requirements

Colour choices should support readability and not carry trust meaning by themselves.

Requirements:

- Meet WCAG AA contrast targets for normal text, large text, controls, and focus indicators.
- Use text labels with colour for status badges.
- Do not use colour alone for approval, rejection, suspension, verification, room access, or meeting access.
- Keep focus rings visible against the page background.
- Test alert, error, success, badge, table, and button states.
- If a dark mode is added later, test both light and dark themes.
- Avoid low-contrast muted text for important errors, warnings, or admin decisions.

Visual design should stay restrained and readable. Decorative colour must not reduce legibility or make status labels ambiguous.

## 6. Plain-Language UX Requirements

User-facing text should use community language rather than protocol or infrastructure language.

Preferred terms:

- account
- invite
- room
- chat
- meeting
- group
- parish
- monastery
- administrator
- verification
- approved
- pending
- suspended

Avoid ordinary-user labels such as:

- XMPP
- MUC
- BOSH
- WebSocket
- Prosody
- JWT
- federation
- component secret

Those technical terms may appear in operator documentation, diagnostics, and administrator help where needed.

Rules:

- Keep error messages short and actionable.
- Say what the user can do next.
- Do not reveal whether private rooms, sensitive accounts, invite tokens, recovery tokens, or internal services exist.
- Keep rejection reasons and verification notes visible only to authorized administrators.
- Avoid pastoral or canonical claims in automated labels.

## 7. Mobile Accessibility Requirements

Mobile access should work for users who rely on browser zoom, touch navigation, and built-in mobile accessibility tools.

Requirements:

- Use responsive layouts for invite redemption, account status, verification requests, room lists, meeting links, and admin review pages.
- Keep tap targets large enough for ordinary use.
- Avoid horizontal scrolling for normal user pages.
- Provide mobile-friendly alternatives for wide admin tables where practical.
- Keep forms short and clearly grouped.
- Avoid hover-only menus.
- Keep page text readable without viewport-scaled font tricks.
- Test chat, portal, and meeting links on common mobile browsers.
- Make browser chat usable before assuming native mobile clients.

Mobile support must not require users to understand XMPP setup, server hostnames, transport URLs, or Jitsi JWT details.

## 8. Internationalisation Goals

Internationalisation should allow Orthodox Connect to serve communities in different languages without changing the trust model.

Goals:

- Separate user-facing text from application logic in future implementation work.
- Support local deployment language needs.
- Keep English as the initial fallback language.
- Support human-reviewed translations for church, role, verification, and administrative terms.
- Avoid external translation services until privacy and operational policy are reviewed.
- Keep translation work separate from secrets, tokens, user data, and production configuration.

Internationalisation must not change role names, permission checks, verification rules, audit event semantics, or room access logic.

## 9. Language Support Strategy

The first supported language is English. Additional languages should be added only when a deployment has reviewers who understand the language and the Orthodox terminology used by that community.

Strategy:

- Add languages one at a time.
- Keep English fallback strings available.
- Use reviewed translations for invite, verification, admin, room, meeting, and error text.
- Prefer deployment-wide language support first.
- Add per-user language selection later only after portal account preferences are implemented.
- Keep admin audit event types stable even when display labels are translated.
- Do not machine-translate verification labels, clergy labels, monastic labels, or legal-sensitive notices without human review.

Translations should support local wording without changing the underlying access policy.

## 10. Translation File Strategy

Translation files are future implementation work. No translation files are added by this document.

Future translation rules:

- Store translations in version-controlled text files only when they contain no secrets or real user data.
- Use stable message keys rather than using English text as the key.
- Keep user-facing, admin-facing, validation, and notification strings organized by area.
- Use named placeholders such as `{display_name}` or `{room_name}` where needed.
- Avoid raw HTML in translation strings where practical.
- Support plural forms before adding languages that need them.
- Keep audit event machine values stable and translate only display labels.
- Review translations before releases that change invite, verification, room, meeting, or admin workflows.

Possible future file layout:

```text
portal/translations/en.json
portal/translations/<locale>.json
```

The exact format should be chosen when portal UI implementation work is approved.

## 11. Right-To-Left Language Placeholder

Right-to-left support is future scope.

Design requirements before adding right-to-left languages:

- Use `dir` and `lang` attributes correctly.
- Prefer logical CSS properties where practical.
- Avoid layout assumptions tied to left-to-right reading.
- Review icons that imply direction, such as back, forward, expand, collapse, previous, and next.
- Test admin tables, room lists, chat views, meeting links, and forms.
- Keep mixed-language names and liturgical terms readable.
- Confirm third-party interfaces such as Converse.js and Jitsi behave acceptably in the selected language.

Right-to-left support must be tested with real translated strings, not placeholder text alone.

## 12. Date and Time Localisation

Dates and times appear in invites, verification requests, verification decisions, meetings, audit events, backups, and admin review pages.

Rules:

- Store timestamps in UTC in backend data.
- Display times with a clear timezone label.
- Use exact dates for audit events, invite expiry, meeting expiry, verification decisions, backup timestamps, and restore notes.
- Avoid ambiguous date-only displays in admin workflows.
- Use locale-aware display formatting when internationalisation is implemented.
- Keep machine-readable timestamps available in admin and operator views where useful.
- Do not use relative time alone for decisions such as `expires soon` or `approved yesterday`.

Liturgical calendars, feast dates, fasting calendars, and old-style or new-style calendar handling are separate product decisions. They should not be mixed into account expiry, audit, backup, or meeting security timestamps.

## 13. Liturgical Terminology Handling

Orthodox terminology must be handled carefully because wording can vary by language, jurisdiction, and local practice.

Rules:

- Keep a glossary for terms used in the portal and chat guidance.
- Treat clergy, monastic, parish, diocese, monastery, mission, chapel, abbot, abbess, bishop, priest, deacon, and administrator as terms needing review.
- Do not use a translated term to imply canonical recognition beyond the local administrator's verification decision.
- Keep verified role labels tied to portal state.
- Do not let users self-label as clergy, monastic, parish admin, diocesan admin, or platform admin.
- Keep internal verification notes separate from public labels.
- Review translations with a person trusted by the local deployment before production use.

Labels should help users understand access and trust state. They should not replace pastoral, diocesan, or canonical judgment.

## 14. Testing and Review Process

Accessibility and internationalisation review should happen before broad community use and before each UI-heavy release.

Manual review checklist:

1. Navigate invite redemption with keyboard only.
2. Navigate account status with keyboard only.
3. Submit a verification request with keyboard only.
4. Review, approve, and reject verification requests with keyboard only.
5. Create, list, revoke, and redeem invites using fake data.
6. View users, groups, roles, rooms, meetings, and audit events on desktop and mobile widths.
7. Confirm field labels and errors work with a screen reader.
8. Confirm colour contrast for text, buttons, badges, links, and focus states.
9. Confirm suspended and unauthorized users receive clear safe messages.
10. Confirm private room names and admin-only notes are not exposed to unauthorized users.
11. Confirm translated strings fit buttons, tables, forms, and mobile layouts when translations are added.
12. Confirm date and time displays include timezone context.
13. Confirm chat and meeting accessibility limits are documented for the tested clients.

Tests should use fake users, fake groups, fake rooms, fake invites, and fake meetings unless a production operator approves a controlled production review.

## 15. Rollback Plan

Accessibility and internationalisation rollback should restore the last known-good user-facing text, layout, or translation without changing trust records.

Rollback steps:

1. Revert the faulty accessibility or internationalisation guidance.
2. Confirm no application code or Docker services were changed by the design rollback.
3. Restore the last known-good text, labels, templates, or translation files when those exist.
4. Confirm invite redemption still rejects expired, revoked, and already-used single-use invites.
5. Confirm public registration remains disabled.
6. Confirm open federation remains disabled.
7. Confirm admin routes remain role-gated.
8. Confirm Jitsi meeting creation remains authenticated and role-gated.
9. Confirm role, room, verification, meeting, and audit semantics did not change because of display text.
10. Preserve audit events, users, groups, rooms, meetings, backups, and service data.

Rollback must not delete portal users, groups, roles, invites, verification records, rooms, meetings, audit events, Prosody data, Jitsi state, backups, or unrelated service configuration.
