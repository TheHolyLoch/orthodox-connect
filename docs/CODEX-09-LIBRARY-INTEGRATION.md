# Orthodox Connect Library Integration

## Purpose

The library integration is a planned PDF and ebook service for approved Orthodox Connect communities. Its purpose is to provide controlled access to parish, diocesan, monastic, educational, and catechetical reading material without making the chat platform a file archive.

The library must remain separate from chat rooms unless explicit portal policy links a collection to roles or groups.

## Candidate Software

Candidate software should be F/OSS, self-hostable, Docker-friendly, and suitable for PDFs and ebooks.

| Candidate   | Strengths                                             | Concerns                                              |
| ----------- | ----------------------------------------------------- | ----------------------------------------------------- |
| Kavita      | Strong ebook and PDF focus, library collections, web reader. | Access-control integration needs review.              |
| Calibre-Web | Mature Calibre ecosystem, metadata support, simple web UI. | Calibre library management can be operator-heavy.     |
| Komga       | Strong comic and PDF reading model, collections.      | Less focused on general parish ebook libraries.       |
| Audiobookshelf | Strong audio and ebook handling.                  | Broader media scope than needed for the first library.|

No candidate should be added until authentication, collection policy, backups, and copyright rules are reviewed.

## Preferred MVP Candidate

Kavita is the preferred first candidate for the post-MVP library phase.

Reasons:

- It is already named in the project docs as a likely library service.
- It is focused on ebooks, PDFs, collections, and browser reading.
- It can be deployed as a separate service behind the existing reverse proxy model.
- It keeps library concerns separate from chat, video, and identity workflows.

This preference is not a final service choice. A small trial with disposable public-domain or locally authored test files should happen before production use.

## Authentication Model

The library must not allow anonymous public access by default.

Preferred model:

1. Orthodox Connect portal remains the source of identity and role policy.
2. Library access is granted only to approved users.
3. The portal maps approved users to library accounts, groups, or access rules.
4. Administrators manage collection access through portal policy where practical.
5. Library local administrator accounts are limited to trusted operators.

Requirements:

- Public registration remains disabled.
- Users must not self-create privileged library accounts.
- Library access must be removed when a user is suspended or removed.
- Admin actions should be audited in the portal or in a reviewed library audit export.
- Library sessions must not bypass portal approval and role checks.

## Role-Based Access Model

Library access should use explicit roles and group membership.

Suggested access levels:

| Access Level       | Example Roles or Groups                           | Notes |
| ------------------ | ------------------------------------------------- | ----- |
| members            | Approved parish or group members.                 | General parish reading. |
| catechumen         | Approved inquirers, catechumens, catechists.      | Requires local naming policy. |
| clergy             | `clergy_verified` plus explicit approval.         | Does not transfer across servers automatically. |
| monastic           | `monastic_verified` plus explicit approval.       | May be scoped to one monastery or group. |
| administrators     | `parish_admin`, `diocesan_admin`, `platform_admin` where scoped. | Operator and collection management. |
| invite_only        | Named users or explicit temporary guests.         | Should expire or be reviewed. |

Library roles must not grant chat access by themselves. Chat roles may grant library access only when a collection policy says so.

## Collection and Category Model

Collections should be simple and administratively clear.

Suggested collections:

- Parish library.
- Catechism and inquirer reading.
- Liturgical reference.
- Patristic and theological texts.
- Clergy resources.
- Monastic resources.
- Local parish documents.
- Diocesan guidance.
- Public-domain materials.

Collection rules:

- Each collection has an owner or responsible administrator.
- Each collection has allowed roles or groups.
- Sensitive collections must not appear to users without access.
- Local parish documents must be clearly separated from published books.
- Collections must not imply permission to distribute copyrighted material.

## Upload and Import Workflow

Uploads must be administrator-controlled.

Workflow:

1. Administrator confirms the file may be stored and shared.
2. Administrator chooses the collection and access policy before import.
3. File is imported through the library tool or a reviewed import directory.
4. Metadata is reviewed before publication.
5. Access is checked with a non-admin test account.
6. Import action is recorded in an audit trail or operator log.

Rules:

- Ordinary users do not upload directly in the first library phase.
- No real books, PDFs, or metadata are added to Git.
- Import directories must stay outside Git.
- File names should avoid private pastoral or personal details.
- Removed files must also be removed from backups only through the retention policy.

## Metadata Policy

Metadata helps users find materials, but it can also expose sensitive collection contents.

Recommended metadata:

- Title.
- Author or editor where known.
- Publisher or source where relevant.
- Publication year where relevant.
- Language.
- Collection.
- Access level.
- Copyright or permission status.
- Local notes for administrators only.

Avoid by default:

- Private pastoral notes.
- Personal details about donors or readers.
- Sensitive source notes visible to ordinary users.
- Unreviewed imported metadata from public databases.

Metadata corrections should preserve enough history for administrators to understand why access or description changed.

## Copyright and Permissions Policy

The library must not become an unreviewed repository of copyrighted material.

Required policy:

- Only upload material the community has permission to store and share.
- Mark each item with permission status before publication.
- Separate public-domain, licensed, locally authored, and restricted-use material.
- Do not assume a book can be uploaded because a physical copy is owned.
- Do not share purchased ebooks unless the license permits it.
- Remove disputed material promptly while permissions are reviewed.
- Keep copyright decisions outside Git and production logs where possible.

Administrators should treat copyright review as a required part of import, not a cleanup task after publication.

## Backup Requirements

Library backups may become large and sensitive.

Back up:

- Library database or metadata store.
- Uploaded PDF and ebook files.
- Collection and access policy data.
- Library configuration.
- Import logs needed for operations.

Do not commit:

- Books.
- PDFs.
- Cover images extracted from books.
- Library metadata exports from real collections.
- Generated library state.

Backup policy:

- Include library data only after the backup script explicitly supports it.
- Store backups in operator-controlled storage.
- Treat backups as sensitive community records.
- Test restore with disposable library content before production use.
- Document retention separately for library files and metadata.

## Search Requirements

Search should help users find approved materials without revealing restricted collections.

Requirements:

- Users see search results only for collections they may access.
- Search indexes must respect collection permissions.
- Restricted collection names should not leak through search suggestions.
- Search should support title, author, collection, language, and basic full-text where available.
- Full-text search must be reviewed for storage size and sensitivity before enabling.
- Search logs should not become a reading-history database.

Reading history and progress tracking should be optional and reviewed for privacy before being enabled.

## Future Federation and Export Options

Library federation should be separate from chat federation.

Possible future options:

- Export a collection manifest without files for review by another trusted community.
- Export public-domain collections between trusted servers.
- Share metadata for recommended reading lists.
- Import selected files only after local copyright and permission review.
- Map shared collections to trusted federation scopes.

Rules:

- Trusted chat federation does not automatically grant library federation.
- Remote clergy or monastic verification does not automatically grant local library access.
- Exported manifests must not include private reader data.
- Exported files must include permission status and source notes.

## Risks and Limitations

Risks:

- Copyright violations.
- Sensitive document exposure.
- Storage growth beyond backup capacity.
- Access-control drift between portal roles and library roles.
- Metadata leakage through search, covers, filenames, or backups.
- Operator mistakes during import or restore.
- Users mistaking the library for official Church publishing approval.

Limitations:

- Library access is later scope and not part of the current MVP.
- No library service is deployed yet.
- No production candidate has been tested in this repository.
- The portal does not yet provision library accounts or collections.

## Rollback Plan

Rollback must remove library access without disrupting chat, portal, meetings, or backups for existing MVP services.

Rollback steps:

1. Disable the library route in the reverse proxy.
2. Stop the library service when it exists.
3. Preserve audit records and operator notes.
4. Confirm chat, portal, Prosody, Jitsi, and backups still work.
5. Review whether any restricted files were exposed.
6. Remove or quarantine imported files based on the incident decision.
7. Revoke library sessions or accounts if the service supports it.
8. Keep backups until retention and evidence needs are reviewed.
9. Document whether the library can be restored, reduced, or permanently removed.

Rollback must not delete portal users, roles, chat rooms, meeting records, or unrelated service data.
