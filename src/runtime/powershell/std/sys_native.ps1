# sys_native.ps1 — native seam for pytra.std.sys

$script:__sys_argv = @()
$script:__sys_path = @()

function get_argv {
    param()
    return $script:__sys_argv
}

function set_argv {
    param($values)
    $script:__sys_argv = @($values)
}

function get_path {
    param()
    return $script:__sys_path
}

function set_path {
    param($values)
    $script:__sys_path = @($values)
}

function exit_ {
    param($code = 0)
    [Environment]::Exit($code)
}

function write_stderr {
    param($text)
    [Console]::Error.Write($text)
}

function write_stdout {
    param($text)
    [Console]::Out.Write($text)
}
