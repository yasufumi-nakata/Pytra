// Generated std/sys.js delegates host bindings through this native seam.

function _replaceArray(target, values) {
    const next = Array.isArray(values) ? Array.from(values, (value) => String(value)) : [];
    target.splice(0, target.length, ...next);
}

export const sys = {
    argv: Array.from(process.argv, (value) => String(value)),
    path: [],
    stderr: process.stderr,
    stdout: process.stdout,
    exit(code = 0) {
        process.exit(Number(code) || 0);
    },
};

export const argv = sys.argv;
export const path = sys.path;
export const stderr = sys.stderr;
export const stdout = sys.stdout;

export function exit(code) {
    return sys.exit(code);
}

export function set_argv(values) {
    _replaceArray(sys.argv, values);
}

export function set_path(values) {
    _replaceArray(sys.path, values);
}

export function write_stderr(text) {
    sys.stderr.write(String(text));
}

export function write_stdout(text) {
    sys.stdout.write(String(text));
}

sys.set_argv = set_argv;
sys.set_path = set_path;
sys.write_stderr = write_stderr;
sys.write_stdout = write_stdout;
