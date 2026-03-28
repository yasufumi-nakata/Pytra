<a href="../../ja/guide/README.md">
  <img alt="Read in Japanese" src="https://img.shields.io/badge/docs-日本語-DC2626?style=flat-square">
</a>

# Guides

For those who can already run Pytra and want to understand how it works. Less formal than the specification, with plenty of diagrams and code examples explaining the "why."

## Reading Order

1. [How EAST works](./east-overview.md) — Follow a concrete example through EAST1 → EAST2 → EAST3
2. [How emitters work](./emitter-overview.md) — See how EAST3 becomes C++/Go/Rust code, with before-and-after comparisons
3. [Type system](./type-system.md) — How type_id, isinstance, narrowing, and union types work internally
4. [How the runtime works](./runtime-overview.md) — `Object<T>`, reference counting, and container reference semantics
5. [@extern and FFI](./extern-ffi.md) — Calling external functions, @abi, @template usage and internals

## Where this fits

```
Tutorial — Get it running, learn the basics
    ↓
Guides (here) — Understand how it works, learn the design philosophy
    ↓
Specification — Look up exact definitions
```
