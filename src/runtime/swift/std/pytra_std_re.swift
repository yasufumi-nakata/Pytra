import Foundation

let S: Int64 = 1

final class Match {
    private let text: String
    private let groups: [String]

    init(_ text: String = "", _ groups: [String] = []) {
        self.text = text
        self.groups = groups
    }

    func group(_ idx: Int64 = Int64(0)) -> String {
        if idx == 0 {
            return text
        }
        let i = Int(idx - 1)
        if i < 0 || i >= groups.count {
            return ""
        }
        return groups[i]
    }
}

func group(_ m: Any = __pytra_none(), _ idx: Int64 = Int64(0)) -> String {
    guard let mm = m as? Match else {
        return ""
    }
    return mm.group(idx)
}

func strip_group(_ m: Any = __pytra_none(), _ idx: Int64 = Int64(0)) -> String {
    return group(m, idx).trimmingCharacters(in: .whitespacesAndNewlines)
}

final class Pattern {
    private let pattern: String
    private let flags: Int64

    init(_ pattern: String, _ flags: Int64 = Int64(0)) {
        self.pattern = pattern
        self.flags = flags
    }

    func match(_ text: String) -> Any {
        return _re_match(pattern, text, flags)
    }
}

func compile(_ pattern: String, _ flags: Int64 = Int64(0)) -> Pattern {
    return Pattern(pattern, flags)
}

func match(_ pattern: String, _ text: String, _ flags: Int64 = Int64(0)) -> Any {
    return _re_match(pattern, text, flags)
}

private func _re_match(_ pattern: String, _ text: String, _ flags: Int64 = Int64(0)) -> Any {
    _ = flags
    return __pytra_none()
}

func sub(_ pattern: String, _ repl: String, _ text: String, _ flags: Int64 = Int64(0)) -> String {
    _ = flags

    if pattern == "\\s+" {
        var out = ""
        var inWhitespace = false
        for scalar in text.unicodeScalars {
            if CharacterSet.whitespacesAndNewlines.contains(scalar) {
                if !inWhitespace {
                    out += repl
                    inWhitespace = true
                }
            } else {
                out.append(String(scalar))
                inWhitespace = false
            }
        }
        return out
    }

    if pattern == "\\s+#.*$" {
        let chars = Array(text)
        var i = 0
        while i < chars.count {
            let s = String(chars[i]).unicodeScalars.first!
            if CharacterSet.whitespacesAndNewlines.contains(s) {
                var j = i + 1
                while j < chars.count {
                    let sj = String(chars[j]).unicodeScalars.first!
                    if !CharacterSet.whitespacesAndNewlines.contains(sj) {
                        break
                    }
                    j += 1
                }
                if j < chars.count && chars[j] == "#" {
                    return String(chars[0..<i]) + repl
                }
            }
            i += 1
        }
        return text
    }

    if pattern == "[^0-9A-Za-z_]" {
        var out = ""
        for scalar in text.unicodeScalars {
            let isAlphaNum = CharacterSet.alphanumerics.contains(scalar)
            if isAlphaNum || scalar == "_" {
                out.append(String(scalar))
            } else {
                out += repl
            }
        }
        return out
    }

    return text
}

func re_native_sub(_ pattern: String, _ repl: String, _ text: String, _ flags: Int64 = Int64(0)) -> String {
    return sub(pattern, repl, text, flags)
}

func re_native_match(_ pattern: String, _ text: String, _ flags: Int64 = Int64(0)) -> Any {
    return match(pattern, text, flags)
}
