// Generated std/os.ts delegates host bindings through this native seam.

declare function require(id: string): any;
declare const process: { cwd(): string };

const __pytraFs = require("fs");

export function getcwd(): string {
    return process.cwd();
}

export function mkdir(p: string): void {
    __pytraFs.mkdirSync(p);
}

export function makedirs(p: string, exist_ok: boolean = false): void {
    __pytraFs.mkdirSync(p, { recursive: exist_ok });
}
