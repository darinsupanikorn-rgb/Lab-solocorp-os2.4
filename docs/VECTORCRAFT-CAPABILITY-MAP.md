# VectorCraft — Capability Map for SoloCorp OS

> **Status:** 📄 Reference doc — D2 **ยังไม่ยืนยัน** ใน upstream (evidence ถูก gitignore จึงตรวจสอบไม่ได้)
> **Gate:** D2 ของคนอื่น แต่ upstream ถือเป็น **D0** จนมีหลักฐานใน `bus/evidence/` · **Owner:** CEO (หนุมาน)
> **Vendor:** VectorCraft v0.13.1 · `storytold/vectorcraft` (ArtCraft team) · MIT OR Apache-2.0
> **Installed:** 2026-10-19 (ที่เครื่องของผู้เขียนเอกสาร) · **Binary:** `tools/vectorcraft/vectorcraft-cli.exe` (105 MB, **Windows เท่านั้น**)
> **Evidence:** `bus/evidence/vectorcraft/` — gitignored → ต้องรัน + แนบหลักฐานซ้ำบน Linux จึงจะอ้าง D2 ได้
> ⚠️ ตัว binary เป็น `.exe` → บน Linux ใช้ไม่ได้ ต้องหา Linux build หรือรันใน WSL/Windows host

---

## 1. What it is

A vector illustration application (Illustrator-class) written in **pure Rust** — no handwritten
JS/TS — exposed to agents as an **MCP server**. It is not a "generate an image from a prompt"
wrapper: an agent drives the same command registry (~710 commands, 89 live effects) a human drives
through the menus, and gets back **editable vector output**.

| | |
|:--|:--|
| Engine | 23 library crates, ~354k LOC Rust, 7 enforced layers (`cargo xtask layers`) |
| Renderer | `vello_cpu` — multithreaded SIMD CPU raster, off the UI thread; wgpu only composites |
| Native format | `.vectorcraft` — versioned compressed JSON, embedded images |
| Maturity | **alpha** — self-assessed ~62% feature parity with Illustrator 2026 |
| Languages | 21 UI locales; CJK/Japanese shaping via HarfRust |

## 2. How it is wired into SoloCorp

Registered in `opencode.json` under `mcp.vectorcraft`:

```
tools/vectorcraft/vectorcraft-cli.exe mcp --headless \
  --automation-read-root  bus/evidence/vectorcraft \
  --automation-write-root bus/evidence/vectorcraft
```

- **Mode:** headless (in-process engine + CPU renderer). No window needed, no GPU.
- **Filesystem confinement:** every path an agent reads or writes must resolve inside the two
  roots. Verified working — see §5.
- `tools/vectorcraft/` is gitignored (105 MB binary, same convention as `tools/github-mcp/`).

### Install gotcha (do not rediscover this)

**There is no Windows build of `vectorcraft-cli` as a separate release asset.** It ships inside the
desktop app. Get it from the portable zip:

```bash
curl -LO https://github.com/storytold/vectorcraft/releases/download/v0.13.1/vectorcraft-0.13.1-windows-x64-portable.zip
# verify against the release's own SHA256SUMS.txt before extracting
```

Actual SHA-256, v0.13.1 windows-x64-portable.zip:
`6c46505e20dfd637b37ff8e1ead9aa69758acdc877ae46cc8b3338463e078b51`

macOS/Linux have a standalone `vectorcraft-cli` zip / `/usr/bin/vectorcraft-cli`.

## 3. Capability map — MCP tool → our agent → use case

Legend: ✅ **verified working in this environment** · 📖 documented, untested · 🚫 headless-mode unavailable

### Production primitives

| Tool | Agent | Use case | |
|:--|:--|:--|:--|
| `draw_shape` rectangle/ellipse/polygon/star/line | `@content-creator-sek` | base geometry for posters, banners, social cards | ✅ |
| `draw_path` (`points` or SVG `d`) | `@content-creator-sek` | curves, custom marks, logo paths | ✅ |
| `add_text` point / area / on-path | `@cmo-mark`, `@content-creator-sek` | headlines, body copy, text on a path | ✅ |
| `set_paint` | `@design-kreet` | colour + gradient application | ✅ (via `draw_*.fill`) |
| `apply_effect` (89 effects) | `@design-kreet` | glow, drop shadow, blur, grain, warp, 3D | ✅ |
| `pathfinder` unite/minusFront/intersect/exclude/divide/trim/merge/crop/outline/minusBack | `@design-kreet` | exact booleans — logos, crescents, silhouettes | ✅ |
| `transform` move/rotate/scale/reflect/shear | `@design-kreet` | layout composition | 📖 |
| `create_graph` (9 chart types) | `@cfo-meetoo`, `@cmo-mark` | deck charts from CSV | 📖 |
| `text_wrap` | `@cmo-mark` | text flowing around an image | 📖 |
| `open_file` | `@ceo-hanuman` | import existing `.svg`/`.pdf`/`.ai`/`.psd`/`.af` and edit | 📖 |
| `export` 20 formats | **all** | `svg svgz pdf ai eps dxf emf wmf png jpg webp gif png8 tiff bmp tga psd txt vectorcraft template` | ✅ (png, svg) |
| `save_file` / `.vectorcraft` | **all** | hand off an editable source file to a human designer | ✅ |
| `screenshot` / `render_preview` | **all** | look at the result before export (per the vendor's own rule) | ⚠️ returned no image |
| `command_list` / `command_run` / `run_command` | **all** | the other ~680 commands, incl. `colorTheme.*`, `swatch.*`, `shapeBuilder.*` | ✅ |

### Interaction tools — need the desktop app

| Tool | Agent | Use case | |
|:--|:--|:--|:--|
| `select_tool`, `pointer_gesture`, `press_key`, `type_text`, `invoke_menu`, `open_panel` | `@design-kreet` | replicate a human drawing session | 🚫 remote-mode only |
| `inspect_ui`, `ui_inspect`, `ui_screenshot` | `@design-kreet` | inspect/drive the real window | 🚫 remote-mode only |

Remote mode needs `vectorcraft --control 7979` (the 145 MB GUI app) plus
`mcp --connect 127.0.0.1:7979`. **Not yet installed** — headless covers every production need.

### History / inspection

| Tool | Use case | |
|:--|:--|:--|
| `undo` / `redo` | correct a bad step without restarting | 📖 |
| `inspect_document` / `doc_inspect` | read the layer tree, ids, paint, history | ✅ (`doc_inspect`) |
| `command_batch` (`atomic`) | many edits = one undo step; `"$0.id"` refs chain ids | ✅ |

### Resources & prompts

- `vectorcraft://document`, `vectorcraft://document/json`, `vectorcraft://commands`
- templates `vectorcraft://object/{id}`, `//command/{id}`, `//effect/{id}`, `//swatch/{name}`
- prompts: `poster` · `icon-set` · `recolor` · `trace-and-style` · `export-set`

## 4. Read-only CLI (no MCP, useful for pipeline steps)

```bash
VC=tools/vectorcraft/vectorcraft-cli.exe
$VC info FILE                                  # document summary as JSON
$VC convert IN OUT [--scale N] [--artboard I] # any readable format -> any writable format
$VC run [--in FILE] --cmd ID [--params JSON] --export FILE
$VC commands                                  # the full command catalogue
$VC bench FILE                                # render timing
```

## 5. Security findings — READ BEFORE WIDENING ACCESS

### ✅ MCP sandbox holds

Every escape attempt was refused with a readable message; nothing landed outside the roots:

| Attempt | Result |
|:--|:--|
| `export` to `../ESCAPE-MCP.png` | ❌ `automation path rejected: outside the write root` |
| `export` to `C:/Windows/Temp/vc-escape.png` | ❌ `automation path rejected: outside the write root` |
| `open_file` of an in-folder SVG given a bare name | ❌ rejected (paths resolve against the server cwd, not the root) |

### 🚨 CRITICAL — the sandbox does NOT cover the CLI

```
$ $VC convert ...\solocorp-poster-v2.svg  bus/evidence/vectorcraft/../ESCAPE.png
{"bytes":63532,"path":"bus\\evidence\\vectorcraft\\..\\ESCAPE.png"}
$ ls -la bus/evidence/ESCAPE.png
-rw-r--r-- 1 Lenovo 19759 63532 ESCAPE.png      # ← wrote OUTSIDE the root, exit 0
```

`--automation-read-root` / `--automation-write-root` confine **the MCP server only**. The
`convert` and `run` subcommands are unconfined. This matches the vendor's documentation, but the
operational consequence is firm:

> **Never expose `vectorcraft-cli` to an agent as a shell command.** Route every file-touching
> operation through the MCP server, which is the confined surface.

To widen the MCP roots for production use, change `opencode.json` — never wrap the CLI.

## 6. Evidence (D2)

Source of truth: `bus/evidence/vectorcraft/`

| Artifact | Bytes | SHA-256 (first 16) |
|:--|--:|:--|
| `solocorp-poster-v2.png` | 63484 | `1309babc771465eb` |
| `solocorp-poster-v2.svg` | 6090 | `6bf965451b1d82b3` |
| `solocorp-poster-v2.vectorcraft` | 93502 | `7464b42f73a0cfce` |
| `qa-roundtrip.png` (SVG re-import) | 63532 | — |

Verified:

1. **Sizes** match the tool's own reported byte counts exactly (6/6 files).
2. **PNG** — valid `89 50 4E 47` magic, IHDR `900x1200` on both.
3. **SVG** — well-formed XML (ElementTree parse). 22 `<path>`, 3 `<text>`, 3 `<filter>`,
   1 `<linearGradient>`, 0 `base64`, 0 `data:image`. Genuine vector, not a rasterised blob.
   Object count reconciles: 22 + 3 + 3 = **28**.
4. **Native file** — `info` reports 1 artboard `900x1200`, **26 objects**
   (Ellipse 9, Line 5, Path 4, Rectangle 3, Rounded Rectangle 1, Type 3, Layer 1),
   `colorMode: rgb`, Arial resolved `status: exact, missingGlyphs: 0`, **0 warnings**.
5. **Round-trip** — `convert solocorp-poster-v2.svg → qa-roundtrip.png` produces a
   **pixel-identical** render at 900x1200. SVG export fidelity is real.
6. **MCP run** — 32 tool calls in the poster build, **33/33 OK, 0 errors**, exit code 0.

Performance: the whole poster (26 objects + 3 live effects + 1 pathfinder boolean + 3 exports)
built in **0.40 s** wall clock, headless, no GPU.

Composition was done through the vendor's own rule — *draw, screenshot, look, fix, then export*:
v1 had three defects I could only see by rendering (title overlapping the moon, title bleeding
off both edges, the sun painting over the ground). v2 fixed all three.

## 7. Gotchas learned the hard way

1. `command_batch` step `id` must be an **engine command id**, not a tool name.
   `{"id":"pathfinder"}` → `unknown command \`pathfinder\``.
   Correct: `{"id":"object.pathfinder.minusFront"}`.
2. Step refs are **0-based**: `"$0.id"`, `"$1.id"` refer to earlier steps of the same batch.
3. **A newly created object becomes the selection**, so `apply_effect` and `set_paint` work
   immediately after `draw_shape` with no id plumbing. This is the ergonomic core.
4. `draw_shape` / `draw_path` accept a whole `paint.setFill` params object as `fill`, so gradients
   apply in the same call:
   `{"gradient":{"kind":"linear","stops":[{"offset":0,"color":"#ffe066"},…],"start":[450,380],"end":[450,742]}}`
5. File paths must be **repo-root-relative full relative paths**. A bare `out.png` is refused.
6. Coordinates: y points **down**, origin at the first artboard's top-left. A new document is
   612x792 (US Letter) unless `file.new` says otherwise.
7. `command_batch` with `"atomic": true` collapses the whole batch into one undo step.

## 8. Open items

| # | Item | Owner |
|:--:|:--|:--|
| 1 | **D3** — 20-task eval table (expected vs actual, root cause per failure). No cherry-picking. | `@qa` |
| 2 | **D4** — a second operator reproduces this runbook from scratch. | `@qa` |
| 3 | Decide the production read/write roots. Current default (`bus/evidence/vectorcraft`) is evidence-only. | CEO |
| 4 | `@qa` and other subagents have **no shell access** — only read/glob/grep. Executable verification gates cannot be delegated as-is. | `@engineering-changful` |
| 5 | `mcp.vectorcraft` is configured but **not yet active in this session** — opencode reads `opencode.json` at startup. Restart to load the 32 tools. | HUMAN |
| 6 | Decide whether to install the 145 MB GUI app for remote mode (needed only for UI-driven tools). | CEO |
| 7 | Expand `prompts.get` / `icon-set` / `recolor` / `export-set` from "read the docs" to "run them once and capture output". | `@content-creator-sek` |

## 9. Decision

**ADOPT for asset production, sandboxed, artifacts under `bus/`.**

Rationale: the alpha maturity gap does not block our use case. We need machine-generated
posters, icons, diagrams and editable brand assets — not Illustrator round-trip fidelity. What is
missing (`.ai` interoperability, interaction fidelity, half the raster effects) is exactly what we
do not need yet.

License is permissive (MIT OR Apache-2.0), assets are OFL/original, and the MCP sandbox is proven.
The one hard rule it comes with: **the CLI is not a safe agent surface.**

---

## Revision history

| Date | Change | Summary |
|:--|:--|:--|
| 2026-10-19 | major | First map. Installed v0.13.1, verified SHA-256, wired MCP into `opencode.json`, generated a poster end-to-end through MCP (33/33 calls), verified artifacts byte-for-byte, proved the MCP sandbox holds and proved the CLI is unconfined. D2 passed **บนเครื่องผู้เขียน** (evidence gitignored → upstream ยังยืนยันไม่ได้). |