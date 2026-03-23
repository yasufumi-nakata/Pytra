// Generated std/os_path.js delegates host bindings through this native seam.

import nodePath from "node:path";
import { existsSync } from "node:fs";

export function join(a, b) {
    return nodePath.join(a, b);
}

export function dirname(p) {
    return nodePath.dirname(p);
}

export function basename(p) {
    return nodePath.basename(p);
}

export function splitext(p) {
    const ext = nodePath.extname(p);
    const root = ext !== "" ? p.substring(0, p.length - ext.length) : p;
    return [root, ext];
}

export function abspath(p) {
    return nodePath.resolve(p);
}

export function exists(p) {
    return existsSync(p);
}
