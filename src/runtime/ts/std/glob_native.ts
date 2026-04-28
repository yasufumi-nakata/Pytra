// Generated std/glob.ts delegates host bindings through this native seam.

declare function require(id: string): any;

const __pytraFs = require("fs");
const __pytraPath = require("path");

export function glob(pattern: string): string[] {
    const idx = pattern.lastIndexOf("/");
    let dir = ".";
    let filePattern = pattern;
    if (idx >= 0) {
        dir = pattern.substring(0, idx);
        filePattern = pattern.substring(idx + 1);
    }
    if (filePattern === "*") {
        try {
            const entries = __pytraFs.readdirSync(dir);
            return entries.map((e: string) => __pytraPath.join(dir, e));
        } catch (_e) {
            return [];
        }
    }
    if (filePattern.startsWith("*")) {
        const suffix = filePattern.substring(1);
        try {
            const entries = __pytraFs.readdirSync(dir);
            return entries.filter((e: string) => e.endsWith(suffix)).map((e: string) => __pytraPath.join(dir, e));
        } catch (_e) {
            return [];
        }
    }
    try {
        __pytraFs.statSync(pattern);
        return [pattern];
    } catch (_e) {
        return [];
    }
}
