// Generated std/os_path.ts delegates host bindings through this native seam.

declare function require(id: string): any;

const __pytraPath = require("path");
const __pytraFs = require("fs");

export function join(a: string, b: string): string {
    return __pytraPath.join(a, b);
}

export function dirname(p: string): string {
    return __pytraPath.dirname(p);
}

export function basename(p: string): string {
    return __pytraPath.basename(p);
}

export function splitext(p: string): [string, string] {
    const ext = __pytraPath.extname(p);
    const root = ext !== "" ? p.substring(0, p.length - ext.length) : p;
    return [root, ext];
}

export function abspath(p: string): string {
    return __pytraPath.resolve(p);
}

export function exists(p: string): boolean {
    return __pytraFs.existsSync(p);
}
