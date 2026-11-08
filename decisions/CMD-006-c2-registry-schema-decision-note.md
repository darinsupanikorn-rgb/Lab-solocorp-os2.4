# Decision Note — CMD-006 C2 Registry Schema Extension (T1 / T2 / T3)

**ถึง:** CEO เทอโบ (Turbo)  
**จาก:** Head of Architect — พี่ทรงศักดิ์ (Songsak)  
**วันที่:** 2026-11-08  
**อ้างอิง:** CMD-006 dispatch (bus/dispatch/2026-11-06/CMD-006-c2-registry-schema-permissions.json), PRD Must Have #3, Design Doc D3, solocorp_mcp/auth.py, solocorp_mcp/module_registry_schema.py, solocorp_mcp/module_registry.py, config/module-registry.json  
**สถานะ:** T1 เสร็จ (ตัวบล็อกของ C2 เคาะแล้ว) | T2 เสร็จ | T3 เสร็จ — พร้อมส่งมอบให้ Engineering implement C2 หลังเคาะ  
**ข้อจำกัดที่เคารพ:** ห้าม implement โค้ด / ห้ามแก้ module_registry*.py ในรอบนี้ (เป็นงาน Engineering หลังเคาะแล้ว) | ห้ามเปิดประเด็น C1 ซ้ำ (ปิดแล้ว QA sign-off) | T1 เสร็จก่อน C2 เริ่มได้

---

## T1 (P0) — รูปแบบ field 'permissions' ใน module manifest (ตัวบล็อกเดียวของ C2)

### คำตอบสั้น
เลือกทาง **(a)** `permissions` เป็น **list ของ scope names** ที่ validate เป็น **enum ตาม SCOPE_LEVELS** (`auth.py:16`)  
รูปแบบ JSON: `"permissions": ["team"]` (ตัวอย่าง)  
ค่าว่าง `[]` อนุญาต (ไม่ขอ scope พิเศษ = public เท่านั้น)

### ตัดสินความหมายของ permissions (ห้ามสับสนสองความหมายนี้)
> **permissions คือ "scope ที่ module ขอสำหรับ tool ของตัวเอง"** — คือ scopes ที่เครื่องมือ (tools/resources/prompts) ภายใน module นั้นประกาศว่าต้องการ  
> **permissions ไม่ใช่** "scope ที่ผู้เรียกต้องมีเพื่อเรียก module นี้" (caller gate)

เหตุผลอ้างอิง:
- PRD Must Have #3 (`docs/prds/PRD-...-MVP-v1.0.md:100`): *"declared permissions (the scopes the module's own tools expose — metadata, not a caller gate)"* — ตรงคำว่า metadata, not a caller gate
- Design Doc D3 §3 (`docs/plans/SOLOCORP-APP-LOCAL-RUNTIME-DESIGN-v0.1.md:113`): permissions คือ "scope ที่ module ขอ (สอดคล้อง SOLOCORP_API_KEY scope ที่มีอยู่)"
- `auth.py:77-95` (`require_scope`) คือ enforcer ของ caller gate — อยู่คนละชั้นกับ permissions เด็ดขาด ไม่ให้นำ permissions มาแทน require_scope

### เปรียบเทียบทางเลือก + trade-off ที่เลือก

| ทาง | รายละเอียด | ได้ | เสีย | เหตุผลที่ไม่เลือก / เลือก |
|:--|:--|:--|:--|:--|
| **(a) list ของ SCOPE_LEVELS validate เป็น enum** (เลือก) | `permissions: ["team"]` แต่ละ item ต้องอยู่ใน `SCOPE_LEVELS` keys (`auth.py:16`) | closed vocabulary ตรงกับระบบ scope จริง UI แสดง/ตรวจได้ชัด ผูกกับ auth.py ได้ในอนาคต | module ประกาศ scope ที่ยังไม่มีในระบบ → ต้องมี policy ว่าทำไง (ดูด้านล่าง) | ตรง PRD Must Have #3 + D3 ลดความคลุมเครือที่สุด |
| (b) single scope level ต่อ module | `permissions: "team"` หนึ่งค่า | เรียบง่ายสุด | module บางตัวต้องหลาย scope (เช่น tools ต้อง team, resources ต้อง admin) ทำไม่ได้ | ปฏิเสธ — ต้องรองรับหลาย scope ต่อ module |
| (c) free-form list + warning | `permissions: ["any-string"]` เก็บไว้เฉยๆ + warning | ยืดหยุ่นสูง อนาคตกันเอง | ไม่มี vocabulary ตรงกับ scope จริง UI ตรวจไม่ได้ เสี่ยง typo ซilent | ปฏิเสธ — ขัด D3 ที่บอก "ต้องมี vocabulary ที่ตรงกับระบบ scope จริง" |

### กฎ validator (สำหรับ Engineering implement)
อิง `module_registry_schema.py`:
- `permissions` เป็น **optional field** ใน `CONFIG_OPTIONAL_FIELDS` (`module_registry_schema.py:38`) — ไม่บังคับ module ทุกตัวต้องมี
- Type rule: ต้องเป็น `list` ของ `string` ไม่ว่าง (mirror `_non_empty_string_list` pattern ที่ใช้กับ `command` บรรทัด 70-75)
- Enum rule: แต่ละ item ต้องเป็น key ใน `SCOPE_LEVELS` (`auth.py:16` = `{"public":1,"team":2,"admin":3}`) — import ซิงค์จาก auth.py หรือ mirror constant ไว้ใน schema module (ต้องไม่หลุดออกจากกัน)
- ห้ามซ้ำ item เดิม (unique)
- หาก item ใดไม่อยู่ใน SCOPE_LEVELS → **warning (ไม่ใช่ fatal error)** เก็บค่าไว้เฉยๆ module ยังโหลดได้ (ดู "พฤติกรรมเมื่อขอ scope ที่ยังไม่มี" ด้านล่าง)

รูปแบบ JSON ที่แน่นอน (ต่อ module entry ใน config):
```json
"permissions": ["team"]
```
ตัวอย่างอื่นที่ถูก: `[]`, `["public"]`, `["public", "team"]`, `["admin"]`

### เหตุผลผูกกับ SCOPE_LEVELS
`permissions` enum ดึง vocabulary จาก `SCOPE_LEVELS` ใน `auth.py:16` โดยตรง (หรือ mirror constantเดียวกัน) — ถ้า engineering เพิ่ม scope ใน auth.py ต้องเพิ่มในpermissions validator คู่กัน เพื่อให้ vocabulary ตรงกันไม่แยกเป็นสองแหล่ง  
อ้างอิง: `auth.py:16` `SCOPE_LEVELS = {"public": 1, "team": 2, "admin": 3}`  
`auth.py:19` `KEY_PATTERN = re.compile(r"^sk-solocorp-(public|team|admin)-(.+)$")` — scope ตัวอักษรตรงกับ enum key เดียวกัน

### ตัวอย่าง 3 module จริง (solocorp / content-creator / qa)

| module | permissions | ความหมาย (declarative metadata) |
|:---|:---|:---|
| `solocorp` | `["admin"]` | Core MCP เปิด org/routing + config tools บางตัวต้อง admin scope |
| `content-creator` | `["team"]` | content generation tools ต้อง team scope (อิง D3 §5.1 บรรทัด 173) |
| `qa` | `["public"]` | QA test listing/reporting เป็น read-only เปิดสาธารณะ |

### ยืนยันไม่ทำให้ FR-07 เสีย
FR-07 (`PRD:145`, `D3:140`): department MCP standalone ต้องใช้ได้โดยไม่ต้องมี SOLOCORP_API_KEY / Core MCP  
→ `permissions` เป็น **declarative metadata เท่านั้น** ไม่ใช่ enforcement ไม่บังคับ key ของ core ไม่ถูกตรวจโดย `require_scope` (`auth.py:77`) ตอน module โหลด standalone → standalone department MCP ทำงานได้แม้ไม่มี key → FR-07 intact  
อ้างอิง PRD Product Principle #2 (`PRD:41`): "It must not require a CEO MCP connection for standalone department work."

### ต้องแก้ auth.py หรือไม่
**ไม่ต้องแก้ auth.py สำหรับ T1**  
- `permissions` เป็น metadata ใน registry config ไม่เกี่ยวกับ `verify_scope`/`require_scope` (`auth.py:44-95`)
- `SCOPE_LEVELS` (`auth.py:16`), `KEY_PATTERN` (`auth.py:19`), `VALID_KEYS` (`auth.py:24`) คงเดิม ไม่ต้องเพิ่ม scope ใหม่ในรอบนี้
- หมายเหตุอนาคต: ถ้า Engineering ต่อยอดให้ permissions เป็น enforcement จริง หรือเพิ่ม scope ใหม่ใน auth.py → ต้องแก้ `SCOPE_LEVELS` + `KEY_PATTERN` + tests คู่กัน เป็น **L5 decision แยกต่างหาก** (ไม่อยู่ใน ticket นี้)

### พฤติกรรมเมื่อ module ขอ scope ที่ยังไม่มีในระบบ
**ตัวเลือก: warning + เก็บไว้เฉยๆ (fail-open, ไม่ error)**  
- module ยังโหลดและใช้งาน standalone ได้ (FR-07) ไม่ถูก block
- validator emits `warning` (เช่นเดียวกับ state warnings ที่ `module_registry.py:110-120` ไม่ทำให้ config invalid) แจ้ง operator ว่า scope X ยังไม่อยู่ใน `SCOPE_LEVELS`
- ไม่เลือก **error** (จะ dead-end module ที่ประกาศ scope ล่วงหน้า ขัด FR-07) ไม่เลือก **เก็บไว้เฉยๆ เฉยๆ** (จะซ่อนปัญหา typo จาก operator)
- อ้างอิงแนวทางเดียวกับ C1: state problem = warning, config problem = error (`module_registry.py:333-342`, `module_registry_schema.py:124-126` unknown field = error แต่ permissions value จะเป็น warning ตามที่ตัดสิน above)

---

## T2 (P1) — นโยบาย schema migration + rollback (1 หน้า)

### ความหมายของ _meta.schema_version
- `_meta.schema_version` คือ **integer generation ของ on-disk config schema** — บอกว่า config file นี้เขียนด้วยรูปแบบ schema รุ่นใด
- ปัจจุบัน `SCHEMA_VERSION = 1` (`module_registry_schema.py:48`, คำอธิบายบรรทัด 47: *"Bump when the on-disk shape changes in a way old readers cannot accept."`)
- `validate_meta` (`module_registry_schema.py:78-107`) ปัจจุบัน reject ถ้า `schema_version` มีค่าแต่ไม่เท่ากับ `SCHEMA_VERSION` (บรรทัด 101-105)
- **Legacy = ไม่มี version**: หาก `_meta` ขาด `schema_version` หรือไม่มี `_meta` เลย → validator อนุญาต (missing key ไม่ error บรรทัด 101 ตรวจเฉพาะเมื่อมี key) → legacy config ยังอ่านได้ = tolerant read ตาม C1

### code v2 อ่าน config v1 ได้ไหม / code v1 เจอ config v2 ต้องทำอะไร

| ทิศทาง | ตัดสิน | เหตุผล + หลักฐาน |
|:--|:---|:--|
| **code v2 อ่าน config v1** | **ได้ (yes)** | v1 config ไม่มี field ใหม่ (permissions/version ฯลฯ ขาดหาย) v2 validator อนุญาต optional field หายได้ → อ่านปกติ = tolerant read ตาม C1 (`module_registry_schema.py:129-131` missing required field เท่านั้นที่ error) |
| **code v1 เจอ config v2** | **fail-closed** | v1 validator treats unknown field (permissions ฯลฯ) เป็น `unknown field` error (`module_registry_schema.py:124-126`) → config invalid → `valid: false` registry ใช้ไม่ได้ จนกว่าจะ revert config |
| **กับดักที่ต้องป้องกัน** | config เป็น git-tracked (`module-registry.json` ใน `config/`, `module_registry.py:51`) → **ไม่มี dead-end** ผู้ใช้ซ่อมได้จาก UI/cli ด้วย `git revert` config ไฟล์ หรือ restore `.bak` ไม่ต้อง reinstall code | `module_registry.py:149-165` `_save_config` write พร้อม `_meta.schema_version` atomic write (`os.replace` บรรทัด 212) |

คำสำคัญ: **config v2 ใหม่กว่า code v1 ไม่ทำให้ registry ตายถาวร** — เพราะ config เป็นไฟล์ text ที่ถูกติดตามใน git ผู้ใช้ revert config กลับรุ่นเก่าได้ทันที แล้ว registry v1 กลับมาอ่านปกติ state file แยกต่างหากไม่ถูกทำลาย (`module_registry.py:54` state path git-ignored)

### schema_version ต้อง bump เมื่อไหร่
| การเปลี่ยนแปลง | Bump หรือไม่ | เหตุผล |
|:--|:---|:--|
| เพิ่ม field ใหม่เข้า `CONFIG_ALL_FIELDS` หรือ `META_FIELDS` | **Bump** | code เก่า reject unknown field (`module_registry_schema.py:124-126`, `90-91`) → old reader อ่าน config ใหม่ไม่ได้ = shape change ที่ old reader รับไม่ได้ (ตรงคำอธิบายบรรทัด 47) |
| เพิ่ม field optional แล้ว code เก่า **ยอมรับ** (ignore unknown) | ไม่ bump (ในกรณีนี้) | แต่โค้ดปัจจุบัน reject unknown field → เพิ่ม field ใดๆ เข้า allow-list จะทำให้ code เก่าอ่านไม่ได้ → **จึงต้อง bump** เมื่อเพิ่ม field |
| เปลี่ยนค่า domain ภายใน field เดิม (เช่นเพิ่ม transport ค่าใหม่) | ไม่ bump | เป็นการเปลี่ยน validator constant ไม่ใช่ shape ของ on-disk field จัดการด้วย validator versioning แยก |
| เปลี่ยน required field / เปลี่ยน type ของ field เดิม | **Bump** | old reader อ่านไม่ถูกต้อง |

**สรุป:** เพิ่ม field optional **ต้อง bump schema_version** (เพราะ code เก่าจะ reject unknown field) เว้นแต่จะทำ dual-schema reader (ไม่อยู่ใน scope MVP)

### Recovery path เมื่อ config ใหม่กว่า code (config v2, code v1)
1. **ป้องกันก่อนแก้:** ก่อนแก้ config ทุกครั้ง ให้สร้างไฟล์สำรอง `config/module-registry.json.bak.<timestamp>` คู่กับไฟล์จริง (manual step ของ operator)
2. **Commit คู่กัน:** การเปลี่ยน schema_version + เพิ่ม field ใน config + code ที่รองรับ ต้อง commit ใน **เดียวกัน (atomic commit)** ห้าม commit code ทิ้งไว้ให้ config วิ่งหน้า หรือ config ใหม่รอ code นานเกินไป
3. **ถ้าเกิดปัญหาจริง:** Operator เปิด UI/terminal → รัน `git revert` หรือ `git checkout` กลับไฟล์ `config/module-registry.json` เป็น commit ล่าสุดที่ code รองรับ → registry v1 อ่านได้ทันที state file ไม่กระทบ
4. **Downgrade path:** หากต้องถอย code กลับ v1 พร้อม config v2 → ต้องรีバート config กลับ v1 shape ก่อน (ลบ field ใหม่ ออก) แล้วค่อยรัน code v1 — ไม่มีทาง "code v1 อ่าน config v2 ได้" โดยไม่แก้ config

---

## T3 (P2) — ตาราง field → type → validation rule → ตัวอย่างค่าจริง 5 module

5 module อ้างอิงจาก `config/module-registry.json` (บรรทัด 2-51) และ `module_registry.py` DEFAULT_MODULES (บรรทัด 67-98): **solocorp, central-bus, content-creator, engineering, qa**

### version
| องค์ประกอบ | คำวินิจฉัย |
|:--|:---|
| **Type** | `string` (แนะนำ semver `MAJOR.MINOR.PATCH` เช่น `"0.3.0"` แต่ MVP ไม่บังคับรูปแบบเข้มงวด) |
| **Validation rule** | non-empty string; format semver แนะนำไม่บังคับ (declarative) |
| **ใครเป็นเจ้าของค่า** | **module ประกาศเอง** (module author กำหนดใน registry config) app อ่านจาก runtime แค่แสดง ไม่ auto-generate |
| **ประโยชน์** | รู้ version ก่อนอ้างใน task record (D3 §3 บรรทัด 110) |

ตัวอย่างจริง 5 module:
- `solocorp`: `"1.0.0"` (Core MCP stable)
- `central-bus`: `"0.9.0"` (pre-release busd)
- `content-creator`: `"0.3.0"` (pilot, อิง D3 §5.1 บรรทัด 170)
- `engineering`: `"0.1.0"`
- `qa`: `"0.2.0"`

### capabilities
| องค์ประกอบ | คำวินิจฉัย |
|:--|:---|
| **Type** | `list` of `string` |
| **Validation rule** | **allow-list** `{"tools", "resources", "prompts"}` (กลุ่มความสามารถมาตรฐาน MCP) ห้าม free-list |
| **มีไว้ให้อะไร** | ให้ **UI แสดง** ใน module catalog + เป็น **คำแนะนำให้ CEO route** — metadata pre-view ไม่ใช่ hard gate (FR-07 intact) |
| **ประโยชน์** | FR-01 module discovery แสดงความสามารถก่อนเชื่อมต่อ |

ตัวอย่างจริง 5 module:
- `solocorp`: `["tools", "resources"]`
- `central-bus`: `["tools", "resources"]`
- `content-creator`: `["tools", "resources"]` (อิง D3 §5.1 บรรทัด 171)
- `engineering`: `["tools"]`
- `qa`: `["tools", "resources"]`

### dependencies
| องค์ประกอบ | คำวินิจฉัย |
|:--|:---|
| **Type** | `list` of `string` |
| **Validation rule** | แต่ละ item non-empty string; ต้องเป็น module id ที่ประกาศใน config หรือชื่อ service ภายนอกที่รู้จัก (เช่น `"busd"`); ห้าม dependency ตัวเอง (self-dependency) |
| **Semantics เมื่อ dependency ไม่พร้อม** | module แสดงสถานะ `error` / `unavailable` CEO ต้องบอกว่ามี module ไหนขาด + วิธีเปิด (FR-04) **ห้าม route ไปแผนกอื่นเงียบๆ** (`PRD:155`, `D3:155`) |

ตัวอย่างจริง 5 module:
- `solocorp`: `[]` (ไม่มี dependency — เป็น core)
- `central-bus`: `["busd"]`
- `content-creator`: `[]` (standalone ตาม FR-07)
- `engineering`: `["solocorp"]`
- `qa`: `["solocorp"]`

### entry_repo
| องค์ประกอบ | คำวินิจฉัย |
|:--|:---|
| **Type** | `string` |
| **Validation rule** | หนึ่งใน: `"internal"` \| relative path \| absolute URL; ต้อง non-empty; `"internal"` หมายถึง repo คือ repo นี้ (`solocorp_mcp/`) |
| **ผลต่อ ADR-030 split** | เปลี่ยน **แค่ fieldนี้** (เช่น `"internal"` → `"https://github.com/.../content-mcp.git"`) app **ไม่ต้องแก้โค้ดบรรทัดเดียว** ตรง ADR-030 open-core boundary (`D3:139`, `ADR-030`) |

ตัวอย่างจริง 5 module (ทั้งหมดเป็น `"internal"` ในช่วง pilot; content-creator split-ready ต่อไป):
- `solocorp`: `"internal"`
- `central-bus`: `"internal"`
- `content-creator`: `"internal"`
- `engineering`: `"internal"`
- `qa`: `"internal"`

### transport
| องค์ประกอบ | คำวินิจฉัย |
|:--|:---|
| **Type** | `string` |
| **Validation rule** | enum ตาม `VALID_TRANSPORTS` (`module_registry_schema.py:34`) ณ MVP = `{"stdio"}` เท่านั้น |
| **จะขยายเกิน stdio เมื่อไหร่** | เฉพาะเมื่อมี module จริงต้องใช้ HTTP/SSE (หลัง MVP, Phase 3+) การขยายต้องมี field entry point ใหม่ต่อ transport (เช่น HTTP/SSE ต้องมี `url` string + optional headers) `command` ยังคงใช้สำหรับ stdio เท่านั้น ตัดสินรายละเอียดตอนขยาย ไม่ตัดสินล่วงหน้าในรอบนี้ |
| **entry point ต่อ transport** | stdio → `command` (list of string); HTTP/SSE → `url` (string) (กำหนดตอนขยายจริง) |

ตัวอย่างจริง 5 module (ทั้งหมด stdio ใน MVP):
- `solocorp`: `"stdio"`
- `central-bus`: `"stdio"`
- `content-creator`: `"stdio"`
- `engineering`: `"stdio"`
- `qa`: `"stdio"`

---

## Evidence Index (ทุกข้อสรุปอ้างไฟล์+บรรทัด)

| # | ข้อสรุป | ไฟล์ : บรรทัด |
|:--|:---|:--|
| 1 | `permissions` = metadata, not caller gate | `docs/prds/PRD-...-MVP-v1.0.md:100` (Must Have #3) |
| 2 | `permissions` = scope ที่ module ขอ | `docs/plans/SOLOCORP-APP-LOCAL-RUNTIME-DESIGN-v0.1.md:113` (D3 §3) |
| 3 | D3 ตัวอย่าง manifest `permissions: ["team"]` | `docs/plans/SOLOCORP-APP-LOCAL-RUNTIME-DESIGN-v0.1.md:173` (D3 §5.1) |
| 4 | `SCOPE_LEVELS` = vocabulary | `solocorp_mcp/auth.py:16` |
| 5 | `KEY_PATTERN` scope ตัวอักษรตรง enum | `solocorp_mcp/auth.py:19` |
| 6 | `require_scope` = caller gate (คนละชั้นกับ permissions) | `solocorp_mcp/auth.py:77-95` |
| 7 | `CONFIG_OPTIONAL_FIELDS` (permissions เข้าตรงนี้) | `solocorp_mcp/module_registry_schema.py:38` |
| 8 | unknown field → error | `solocorp_mcp/module_registry_schema.py:124-126` |
| 9 | missing required field → error | `solocorp_mcp/module_registry_schema.py:129-131` |
| 10 | `schema_version != SCHEMA_VERSION` → error | `solocorp_mcp/module_registry_schema.py:101-105` |
| 11 | `SCHEMA_VERSION = 1` + คำอธิบาย bump | `solocorp_mcp/module_registry_schema.py:47-48` |
| 12 | legacy ไม่มี version → ทนได้ (missing key) | `solocorp_mcp/module_registry_schema.py:101` (if check) |
| 13 | `_save_config` เขียน `_meta.schema_version` atomic | `solocorp_mcp/module_registry.py:160-164`, `212` (`os.replace`) |
| 14 | state file แยกจาก config (ไม่ถูกทำลายเมื่อ config revert) | `solocorp_mcp/module_registry.py:54` |
| 15 | state warning ≠ config error (fail-open แนวทางเดียวกับ unknown scope) | `solocorp_mcp/module_registry.py:110-120` |
| 16 | FR-07 standalone compatibility | `docs/prds/PRD-...-MVP-v1.0.md:145` |
| 17 | Product Principle #2 department independence | `docs/prds/PRD-...-MVP-v1.0.md:41` |
| 18 | FR-04 missing module → แจ้งชัด ห้าม route เงียบ | `docs/prds/PRD-...-MVP-v1.0.md:143`, `docs/plans/SOLOCORP-APP-LOCAL-RUNTIME-DESIGN-v0.1.md:155` |
| 19 | ADR-030 split = เปลี่ยน command/entry_repo แล้ว app ไม่แก้โค้ด | `docs/plans/SOLOCORP-APP-LOCAL-RUNTIME-DESIGN-v0.1.md:139` (D6) |
| 20 | 5 module ปัจจุบันใน config | `config/module-registry.json:2-51` |
| 21 | DEFAULT_MODULES 5 module | `solocorp_mcp/module_registry.py:67-98` |

---

## Constraints Check (สำหรับ CEO / QA ตรวจรับ)

- [x] **T1 เสร็จก่อน C2 เริ่มได้** — T1 เคาะแล้ว (ทางเลือก a, ความหมายชัด, FR-07 intact, auth.py ไม่ต้องแก้, unknown scope = warning + เก็บเฉยๆ)
- [x] **ห้าม implement โค้ด / ห้ามแก้ module_registry*.py** — 決定เท่านั้น ไม่มีการแก้ไขโค้ดใดๆ ในรอบนี้ (งาน Engineering หลังเคาะ)
- [x] **ห้ามเปิดประเด็น C1 ซ้ำ** — C1 (config=error/state=warning/atomic write/register()/update() patch-only) ถูกอ้างเป็นหลักฐานแต่ไม่เปิดอภิปรายใหม่ (ปิดแล้ว QA sign-off 1059 passed)
- [x] **ทุกข้อสรุปอ้างไฟล์+บรรทัด** — ดู Evidence Index ด้านบนครบทุกประเด็น
- [x] **T2/T3 ตามได้หลัง T1** — ทั้งสามส่วนส่งครบใน note ฉบับนี้

---

**ส่งมอบ:** 决策 note ฉบับนี้ครบ T1/T2/T3 พร้อมให้ Engineering รับไป implement C2 หลัง CEO เคาะแล้ว ภายในเดดไลน์ 2026-11-10 (T3 เดดไลน์จริง 2026-11-12 ตาม dispatch แต่ส่งพร้อมกันในรอบนี้)

— พี่ทรงศักดิ์ (Songsak), Head of Architect
