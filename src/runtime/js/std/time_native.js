// Generated std/time.js delegates host bindings through this native seam.

export function perf_counter() {
    return Number(process.hrtime.bigint()) / 1_000_000_000;
}
