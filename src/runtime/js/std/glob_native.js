// Generated std/glob.js delegates host bindings through this native seam.

import { readdirSync, statSync } from "node:fs";
import { join, resolve, dirname, basename } from "node:path";

export function glob(pattern) {
    // Minimal glob: supports trailing * only (e.g. "dir/*.txt")
    const idx = pattern.lastIndexOf("/");
    let dir = ".";
    let filePattern = pattern;
    if (idx >= 0) {
        dir = pattern.substring(0, idx);
        filePattern = pattern.substring(idx + 1);
    }
    if (filePattern === "*") {
        try {
            const entries = readdirSync(dir);
            const out = [];
            for (const e of entries) {
                out.push(join(dir, e));
            }
            return out;
        } catch (_e) {
            return [];
        }
    }
    // Wildcard prefix match: "*.ext"
    if (filePattern.startsWith("*")) {
        const suffix = filePattern.substring(1);
        try {
            const entries = readdirSync(dir);
            const out = [];
            for (const e of entries) {
                if (e.endsWith(suffix)) {
                    out.push(join(dir, e));
                }
            }
            return out;
        } catch (_e) {
            return [];
        }
    }
    // No wildcard: return pattern as-is if it exists
    try {
        statSync(pattern);
        return [pattern];
    } catch (_e) {
        return [];
    }
}
