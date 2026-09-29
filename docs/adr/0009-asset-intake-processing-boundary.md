# ADR-0009: Asset intake and processing boundary

- Status: Accepted for contract design and synthetic-only local development
- Date: 2026-09-29
- Decision owner: Project owner (delegated implementation decisions)

## Context

GrowthTwin is intended to use an advertiser's existing documents and creative
materials as sources for campaign work. The current product has no file upload,
asset library, document extraction, or media processing. Real advertiser data is
explicitly deferred until the product's separate readiness gate is satisfied.

Files are an untrusted input surface. Uploading a file does not establish its
ownership, license, permission to transform it, permission to send it to an AI
provider, or permission to use it as an advertisement. File contents can include
personal data, malware, active content, and instructions that must not change
the system's behavior.

## Decision

1. **Separate contract from file handling.** Add asset workflow types and rules
   before selecting storage, parsers, OCR, media tools, or providers. This stage
   may use synthetic fixtures only. It must not accept files from users or make
   network/provider calls.
2. **Workspace ownership is server-authorized.** Future original assets and
   derivatives belong to a workspace. Each access is checked against the
   authenticated owner or a later explicit membership role. A client-supplied
   workspace or asset ID is never authorization.
3. **Keep declarations distinct.** Record separately whether the submitter
   declares a right to provide/use the material, whether processing for the
   requested task is authorized, and whether any identified provider may receive
   the content. Unknown or withdrawn permission blocks the corresponding
   processing. These declarations do not replace legal review or establish
   copyright ownership.
4. **Use explicit processing states.** The contract must distinguish pending
   declarations, quarantined, security-check pending, rejected, extraction
   pending, ready for a permitted task, failed, deletion requested, and deleted.
   Only a clean security result plus task permission may advance to extraction.
   Failed or uncertain checks fail closed; retry behavior must be bounded and
   idempotent before an adapter is introduced.
5. **Preserve originals and provenance.** Never overwrite an original. Every
   extracted fact or generated/adapted derivative must reference its source
   asset/version and record the processing tool/model, task, settings, and time
   when available. An original does not become an approved advertising claim.
6. **Treat content as untrusted.** Instructions embedded in files cannot change
   system/developer rules or enable tools. Extracted material is untrusted input;
   personal or sensitive information requires a separate classification and
   use decision. AI access remains off unless the user is informed, gives
   task-specific permission, and the provider's current terms/data location are
   approved for that data class.
7. **Keep storage private and deletion complete.** Any future quarantine and
   original storage must be outside public static/media serving and inaccessible
   without owner authorization. Deletion must cover originals and their
   derivatives; retention periods and backup deletion behavior remain open until
   purpose-specific privacy/legal review.
8. **Do not open upload or persistence yet.** Before implementation accepts
   files, select supported formats and size limits, private storage, malware
   scanning, parser/OCR sandboxing, sensitive-data handling, retention/deletion,
   provider rules, and tested tenant isolation. Verify backup/restore and
   deletion behavior. Keep real data blocked until a separate owner decision.

## Consequences

- Local contract work can proceed without collecting customer files or adding
  paid infrastructure.
- Upload API, durable asset rows, object storage, OCR/video processing, public
  file URLs, and AI ingestion remain out of scope for this ADR.
- Supported formats, limits, scanners/parsers, storage technology, processing
  region, retention durations, legal basis and commercial-use language remain
  unresolved and must be decided before real files are accepted.
- A clean local or CI synthetic example does not prove real-data readiness.

## Follow-up

- Define pure, storage/provider-independent workflow types and transitions with
  synthetic examples; verify illegal transitions fail closed.
- Only after that contract is reviewed, design isolated local file handling and
  its threat-focused verification. Do not enable user uploads as a side effect.
