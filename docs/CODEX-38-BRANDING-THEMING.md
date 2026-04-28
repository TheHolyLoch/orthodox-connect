# Orthodox Connect Branding and Theming

## 1. Branding Goals

Orthodox Connect branding should make the platform feel trustworthy, calm, and appropriate for parish, diocesan, monastic, and community use.

Goals:

- Present Orthodox Connect as a private, invite-only communications platform.
- Keep the focus on community communication, verification, rooms, meetings, and administration.
- Make the portal, chat, and meeting entry points feel related without hiding their different roles.
- Support local parish, monastery, diocese, or group identity where a deployment wants it.
- Avoid implying official ecclesiastical endorsement unless the deployment has that authority.
- Keep branding clear for non-technical users.
- Preserve accessibility, privacy, and security requirements.

Branding must not change registration, verification, role checks, room access, meeting access, suspension, or audit behaviour.

## 2. Visual Identity Principles

The visual identity should be restrained and functional.

Principles:

- Use quiet layouts that support repeated daily use.
- Prefer clarity over decoration.
- Use consistent spacing, headings, buttons, links, badges, and form styles.
- Keep important actions visually distinct.
- Keep admin views dense enough to scan without feeling crowded.
- Keep ordinary user screens simpler than admin screens.
- Keep decorative elements secondary to content and workflow.
- Use local deployment names only where the operator has chosen them.

Orthodox Connect should look maintained and serious, not promotional or entertainment-focused.

## 3. Orthodox Visual Language

Orthodox visual references should be used with care.

Appropriate directions:

- Use dignity, order, and calm as the main design tone.
- Use simple cross, church, lamp, book, bell, or meeting symbols only after icon policy is reviewed.
- Use subtle border, panel, and section treatments inspired by traditional order rather than heavy ornament.
- Keep role and verification badges plain and readable.
- Use Orthodox terms accurately and consistently.

Rules:

- Do not use icons of Christ, the Theotokos, saints, or liturgical scenes as decorative UI assets without explicit permission and pastoral review.
- Do not use holy imagery as avatars, loading indicators, error screens, badges, or marketing decoration.
- Do not make visual design imply clergy, monastic, diocesan, or canonical authority beyond portal verification state.
- Do not mix sacred imagery with casual notifications, warning banners, or error states.

The interface should respect Orthodox visual tradition without turning worship imagery into interface decoration.

## 4. British and Celtic Visual Notes

Some deployments may want a British or Celtic Orthodox tone. That direction can be appropriate when it reflects the local community.

Possible influences:

- Insular manuscript spacing, borders, and restrained pattern work.
- Stone, slate, wool, parchment, green, blue, and muted gold references.
- Simple cross forms, chapel silhouettes, or local landscape references after artwork review.
- Modest knotwork-inspired dividers used sparingly.
- Clear English wording with local British spelling where the deployment prefers it.

Risks to avoid:

- Treating Celtic style as a substitute for Orthodox identity.
- Using nationalist, political, or romanticised imagery.
- Overloading the interface with knotwork or manuscript-style decoration.
- Using copyrighted manuscript images, photographs, icons, or scanned art.
- Making a local theme hard to read or hard to translate.

British or Celtic theming should remain optional and deployment-specific.

## 5. Colour Palette Placeholders

No final colour palette is defined by this document. Palette work should happen in a later design implementation pass.

Placeholder roles:

| Token Role       | Intended Use |
| ---------------- | ------------ |
| `background`     | Main page background. |
| `surface`        | Forms, tables, panels, and repeated content areas. |
| `text`           | Main readable text. |
| `muted_text`     | Secondary text that still meets contrast requirements. |
| `primary`        | Main action buttons and active navigation. |
| `accent`         | Limited emphasis and local deployment identity. |
| `border`         | Dividers, table lines, and quiet structure. |
| `success`        | Approved and completed states. |
| `warning`        | Pending, expiring, or review-needed states. |
| `danger`         | Suspended, revoked, rejected, or destructive states. |
| `info`           | Neutral notices and help text. |

Rules:

- Do not rely on colour alone for status.
- Keep strong contrast for text, controls, focus indicators, and badges.
- Avoid one-note palettes dominated by one hue.
- Avoid overly bright, neon, or decorative colour schemes.
- Test palette choices on mobile, desktop, and high-zoom browser settings.

## 6. Typography Placeholders

No final typeface is selected by this document.

Typography direction:

- Prefer readable system fonts for the first production-ready UI.
- Use clear hierarchy for page titles, section headings, labels, body text, tables, and badges.
- Keep body text comfortable for older users and mobile users.
- Avoid decorative fonts for normal UI.
- Avoid script, pseudo-medieval, or manuscript-style fonts for functional text.
- Use liturgical or decorative type only for carefully reviewed optional branding, not controls or admin data.

Rules:

- Do not scale font size directly with viewport width.
- Do not use negative letter spacing.
- Keep button, badge, and table text from overflowing.
- Support future translation expansion where words may become longer.

## 7. Logo and Icon Placeholder Policy

No logo, icon, image, or asset is added by this document.

Future logo policy:

- A simple wordmark may be enough for the MVP.
- A local deployment may add a parish, diocese, monastery, or group name if authorised.
- Any symbol should be simple, readable at small sizes, and distinct from role badges.
- Artwork must be original, licensed for the project, or explicitly permitted by the owner.
- Source, licence, and permission notes should be recorded before committing assets.

Icon policy:

- Use icons only where they clarify actions.
- Keep icon actions accessible with text labels or accessible names.
- Do not use sacred imagery for status, errors, loading, or ordinary UI controls.
- Do not add copyrighted icon sets unless their licence is reviewed.

Verification badges must come from portal role data, not from user-uploaded images or decorative marks.

## 8. Portal Theming

Portal theming should support invite, verification, role, room, meeting, and admin workflows.

Portal requirements:

- Keep user-facing pages simple and direct.
- Keep admin pages structured for scanning.
- Keep status labels clear for pending, approved, rejected, revoked, suspended, and disabled states.
- Keep role badges plain and readable.
- Keep forms consistent across invites, verification, rooms, meetings, and admin actions.
- Keep destructive actions visually distinct and confirmed.
- Keep audit views sober and data-focused.
- Keep local deployment name and Orthodox Connect name visible where useful.

Portal theming must not hide permission checks. Hidden buttons, colours, and badges are not authorization controls.

## 9. Converse.js Theming

Converse.js theming should make browser chat feel connected to Orthodox Connect while respecting the client interface.

Chat theming requirements:

- Keep sign-in and room views readable.
- Avoid protocol jargon in visible labels where Converse.js allows configuration.
- Keep chat, room, direct message, and account language clear.
- Keep room lists usable on mobile screens.
- Keep unread, mention, error, and connection states visible without relying only on colour.
- Keep verified labels out of Converse.js unless they come from a reviewed portal integration.
- Do not make XMPP nicknames or avatars look like portal verification badges.

The current Converse.js frontend is a static browser chat layer. Full visual integration should wait for a reviewed implementation pass.

## 10. Jitsi Theming

Jitsi theming should be minimal and should not interfere with meetings.

Meeting theming requirements:

- Keep meeting pages focused on audio, video, chat, participants, and controls.
- Preserve camera, microphone, screen sharing, and fullscreen usability.
- Keep joining, waiting, denied, and expired-link states clear.
- Avoid decorative elements that distract during meetings.
- Avoid branding that implies a meeting link grants access by itself.
- Keep JWT token and internal meeting details hidden from users.
- Keep guest access messaging clear where guests are explicitly allowed.

Any Jitsi branding must preserve authenticated room creation and role-gated meeting access.

## 11. Library Theming Placeholder

The library service is not implemented in the current MVP.

Future library theming should:

- Match the general Orthodox Connect tone.
- Keep collection, title, author, language, permission, and access labels readable.
- Keep restricted collections hidden from unauthorized users.
- Avoid using book covers or artwork without permission.
- Avoid making the library look like an official publisher unless the deployment has that authority.
- Support long titles and multiple languages.
- Keep copyright and permission status visible to administrators.

Library theming should be reviewed only after the library service and access model are implemented.

## 12. Accessibility Constraints

Branding must stay inside the accessibility strategy.

Constraints:

- Meet WCAG 2.2 AA contrast targets where practical.
- Do not rely on colour alone for status or priority.
- Keep focus indicators visible.
- Keep fonts readable at normal and zoomed sizes.
- Keep buttons, badges, tables, and form fields readable on mobile.
- Keep screen reader labels accurate and plain.
- Avoid flashing, distracting motion, and animated ornament.
- Test light and dark variants if both are ever added.
- Keep translated text from breaking layout.

Branding that weakens readability should be rejected, even if it looks more distinctive.

## 13. What To Avoid

Avoid:

- Copyrighted artwork without permission.
- Sacred imagery used as decoration, avatars, badges, buttons, or loading states.
- Marketing-style pages where the user needs a working portal, chat, or admin tool.
- Heavy ornamental borders that reduce readability.
- Pseudo-medieval fonts for controls, tables, or body text.
- One-colour themes that make state hard to distinguish.
- Bright novelty palettes.
- Hidden access state represented only by colour or icons.
- Badges that imitate clergy, monastic, or admin verification without portal data.
- Real parish, diocesan, monastic, or production domains in default theme examples.
- Theming that suggests public registration, open federation, public meetings, or unauthorised room discovery.
- Theme settings that require editing Docker services or application code outside a reviewed implementation pass.

The theme should support trust and clarity. It should not become a separate identity system.

## 14. Rollback Plan

Branding rollback should restore the last known-good visual guidance or theme without changing access policy.

Rollback steps:

1. Revert the faulty branding or theming guidance.
2. Confirm no application code, theme files, images, icons, or Docker services were changed by this design edit.
3. Remove any unapproved artwork or icon references from future implementation branches.
4. Restore the last known-good portal, chat, meeting, or library theme files when theme files exist.
5. Confirm public registration remains disabled.
6. Confirm open federation remains disabled.
7. Confirm admin routes remain role-gated.
8. Confirm verified labels still come from portal role and verification state.
9. Confirm Jitsi meeting creation remains authenticated and role-gated.
10. Confirm accessibility checks still pass for contrast, focus, readable text, and mobile layout.
11. Preserve users, groups, roles, invites, verification records, rooms, meetings, audit events, backups, and service data.

Rollback must not delete portal data, Prosody data, Jitsi state, backups, logs, or unrelated service configuration.
