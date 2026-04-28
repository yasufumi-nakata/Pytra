// Generated std/time.ts delegates host bindings through this native seam.

declare const process: { hrtime: { bigint(): bigint } };

export function perf_counter(): number {
    return Number(process.hrtime.bigint()) / 1_000_000_000;
}

export const perfCounter = perf_counter;
