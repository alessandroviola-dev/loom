import { createHash } from "node:crypto";
import {
  chmodSync,
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  renameSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { dirname, join, resolve } from "node:path";

const EVIDENCE_ID_RE = /^ev1-([0-9a-f]{64})$/;

function safeName(value) {
  return String(value ?? "unknown").replace(/[^a-zA-Z0-9_.-]/g, "_");
}

function canonicalize(value) {
  if (Array.isArray(value)) return value.map(canonicalize);
  if (value && typeof value === "object") {
    const output = {};
    for (const key of Object.keys(value).sort()) output[key] = canonicalize(value[key]);
    return output;
  }
  return value;
}

export function canonicalJson(value) {
  return JSON.stringify(canonicalize(value));
}

export function hashEvidenceMessage(message) {
  const canonical = canonicalJson(message);
  const sha256 = createHash("sha256").update(canonical, "utf8").digest("hex");
  return {
    evidenceId: `ev1-${sha256}`,
    sha256,
    canonical,
  };
}

export function collectEvictedEvidence(originalMessages, visibleMessages) {
  const visibleCounts = new Map();
  for (const message of visibleMessages ?? []) {
    const { sha256 } = hashEvidenceMessage(message);
    visibleCounts.set(sha256, (visibleCounts.get(sha256) ?? 0) + 1);
  }

  const evicted = [];
  for (let index = 0; index < (originalMessages ?? []).length; index += 1) {
    const message = originalMessages[index];
    const hashed = hashEvidenceMessage(message);
    const remaining = visibleCounts.get(hashed.sha256) ?? 0;
    if (remaining > 0) {
      visibleCounts.set(hashed.sha256, remaining - 1);
      continue;
    }
    evicted.push({
      messageIndex: index,
      role: message?.role ?? "unknown",
      message,
      ...hashed,
    });
  }
  return evicted;
}

function ensureDir(path) {
  mkdirSync(path, { recursive: true, mode: 0o700 });
  try {
    chmodSync(path, 0o700);
  } catch {
    // Best-effort permission tightening on platforms that support it.
  }
}

function atomicWriteJson(path, value) {
  ensureDir(dirname(path));
  const temp = `${path}.tmp-${process.pid}-${Math.random().toString(16).slice(2)}`;
  writeFileSync(temp, `${JSON.stringify(value, null, 2)}\n`, { encoding: "utf8", mode: 0o600, flag: "wx" });
  renameSync(temp, path);
  try {
    chmodSync(path, 0o600);
  } catch {
    // Best-effort permission tightening on platforms that support it.
  }
}

export function evidencePaths(rootDir, sessionId) {
  const root = resolve(rootDir);
  const evidenceRoot = join(root, "evidence");
  return {
    root,
    evidenceRoot,
    blobsDir: join(evidenceRoot, "blobs"),
    sessionsDir: join(evidenceRoot, "sessions"),
    sessionDir: join(evidenceRoot, "sessions", safeName(sessionId)),
  };
}

function verifyExistingBlob(path, expectedSha) {
  const parsed = JSON.parse(readFileSync(path, "utf8"));
  if (parsed?.schemaVersion !== 1 || parsed?.sha256 !== expectedSha || parsed?.evidenceId !== `ev1-${expectedSha}`) {
    throw new Error(`evidence blob metadata mismatch: ${path}`);
  }
  const actual = hashEvidenceMessage(parsed.message).sha256;
  if (actual !== expectedSha) throw new Error(`evidence blob hash mismatch: ${path}`);
}

export function archiveEvictedEvidence({
  rootDir,
  sessionId,
  originalMessages,
  visibleMessages,
  cwd = process.cwd(),
  capturedAt = new Date().toISOString(),
}) {
  const paths = evidencePaths(rootDir, sessionId);
  ensureDir(paths.blobsDir);
  ensureDir(paths.sessionDir);

  const candidates = collectEvictedEvidence(originalMessages, visibleMessages);
  let blobsCreated = 0;
  let sessionRefsCreated = 0;
  const evidenceIds = [];

  for (const candidate of candidates) {
    const blobPath = join(paths.blobsDir, `${candidate.sha256}.json`);
    if (existsSync(blobPath)) {
      verifyExistingBlob(blobPath, candidate.sha256);
    } else {
      atomicWriteJson(blobPath, {
        schemaVersion: 1,
        evidenceId: candidate.evidenceId,
        sha256: candidate.sha256,
        message: candidate.message,
      });
      blobsCreated += 1;
    }

    const refPath = join(paths.sessionDir, `${candidate.sha256}.json`);
    if (!existsSync(refPath)) {
      atomicWriteJson(refPath, {
        schemaVersion: 1,
        evidenceId: candidate.evidenceId,
        sha256: candidate.sha256,
        capturedAt,
        sessionId,
        cwd,
        messageIndex: candidate.messageIndex,
        role: candidate.role,
        reason: "not-visible-verbatim-after-pack",
      });
      sessionRefsCreated += 1;
    }
    evidenceIds.push(candidate.evidenceId);
  }

  return {
    candidates: candidates.length,
    blobsCreated,
    sessionRefsCreated,
    deduped: candidates.length - sessionRefsCreated,
    evidenceIds,
  };
}

export function parseEvidenceId(evidenceId) {
  const match = EVIDENCE_ID_RE.exec(String(evidenceId ?? ""));
  if (!match) throw new Error(`invalid evidence id: ${evidenceId}`);
  return { evidenceId: match[0], sha256: match[1] };
}

export function readEvidenceById(rootDir, evidenceId) {
  const { sha256 } = parseEvidenceId(evidenceId);
  const { blobsDir } = evidencePaths(rootDir, "unused");
  const path = join(blobsDir, `${sha256}.json`);
  if (!existsSync(path)) throw new Error(`evidence not found: ${evidenceId}`);
  verifyExistingBlob(path, sha256);
  return JSON.parse(readFileSync(path, "utf8"));
}

function lexicalTokens(query) {
  return String(query ?? "")
    .toLowerCase()
    .split(/[^a-z0-9_./:-]+/i)
    .map((token) => token.trim())
    .filter((token) => token.length >= 2);
}

function snippet(text, terms, maxChars = 220) {
  const lower = text.toLowerCase();
  let start = 0;
  for (const term of terms) {
    const index = lower.indexOf(term);
    if (index >= 0) {
      start = Math.max(0, index - Math.floor(maxChars / 3));
      break;
    }
  }
  const clipped = text.slice(start, start + maxChars).replace(/\s+/g, " ").trim();
  return `${start > 0 ? "…" : ""}${clipped}${start + maxChars < text.length ? "…" : ""}`;
}

export function searchEvidence(rootDir, { query, sessionId = null, limit = 10 } = {}) {
  const terms = lexicalTokens(query);
  if (terms.length === 0) return [];
  const { sessionsDir, blobsDir } = evidencePaths(rootDir, sessionId ?? "unused");
  if (!existsSync(sessionsDir)) return [];

  const sessionNames = sessionId ? [safeName(sessionId)] : readdirSync(sessionsDir).sort();
  const bestByEvidence = new Map();

  for (const sessionName of sessionNames) {
    const sessionDir = join(sessionsDir, sessionName);
    if (!existsSync(sessionDir) || !statSync(sessionDir).isDirectory()) continue;
    for (const file of readdirSync(sessionDir)) {
      if (!file.endsWith(".json")) continue;
      let ref;
      try {
        ref = JSON.parse(readFileSync(join(sessionDir, file), "utf8"));
      } catch {
        continue;
      }
      if (!ref?.sha256) continue;
      const blobPath = join(blobsDir, `${ref.sha256}.json`);
      if (!existsSync(blobPath)) continue;
      let blob;
      try {
        blob = JSON.parse(readFileSync(blobPath, "utf8"));
      } catch {
        continue;
      }
      const text = canonicalJson(blob.message).toLowerCase();
      let score = 0;
      for (const term of terms) {
        let cursor = 0;
        let occurrences = 0;
        while ((cursor = text.indexOf(term, cursor)) >= 0) {
          occurrences += 1;
          cursor += term.length;
          if (occurrences >= 8) break;
        }
        if (occurrences > 0) score += 10 + Math.min(occurrences, 8);
      }
      if (score === 0) continue;
      const result = {
        evidenceId: blob.evidenceId,
        sha256: blob.sha256,
        sessionId: ref.sessionId,
        role: ref.role,
        capturedAt: ref.capturedAt,
        score,
        snippet: snippet(canonicalJson(blob.message), terms),
      };
      const previous = bestByEvidence.get(blob.evidenceId);
      if (!previous || result.score > previous.score) bestByEvidence.set(blob.evidenceId, result);
    }
  }

  return [...bestByEvidence.values()]
    .sort((a, b) => b.score - a.score || String(b.capturedAt).localeCompare(String(a.capturedAt)) || a.evidenceId.localeCompare(b.evidenceId))
    .slice(0, Math.max(1, Number(limit) || 10));
}
