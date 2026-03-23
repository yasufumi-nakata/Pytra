// Generated std/os.js delegates host bindings through this native seam.

import { mkdirSync } from "node:fs";
import { resolve } from "node:path";

export function getcwd() {
    return process.cwd();
}

export function mkdir(p) {
    mkdirSync(p);
}

export function makedirs(p, exist_ok = false) {
    mkdirSync(p, { recursive: exist_ok });
}
