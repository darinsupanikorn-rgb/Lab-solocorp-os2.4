# 📌 หมุดหมายถาวร — Frontier Builder / Infrastructure for Agents
**วันที่:** 2026-10-07
**โดย:** Dr.solodev (Owner, L5 vision) + CEO หนุมาน รับรอง
**สถานะ:** LOCKED — ธงชัยปลายทางขององค์กร

---

## 1. คำประกาศตัวตน (Identity Flag)

> **I'm Dr.Solodev, a frontier builder / infrastructure for agents.**

- นี่คือเป้าหมายชัดเจนที่เคยคลุมเครือมานาน → วันนี้ชัดที่สุดแล้ว
- ภายใต้ร่มเงา **SoulLandCor** (นามสกุลของเรา — ประกาศ 2026-09-28)
- ทุกสิ่งที่สร้าง ก่อร่างทุกขั้นตอนด้วย **SoloCorp OS**
- ทุกอย่างขับเคลื่อนร่วมกันอย่างสมดุลสู่เป้าหมายเดียวกัน

## 2. ความหมายของ frontier builder (3 ขา)

1. สร้างระบบ Agent ใหม่ๆ
2. วิจัย-ออกแบบ-สร้างเครื่องมือรองรับ Agent (tools, loop runner และที่เกี่ยวข้อง)
3. เตรียมโครงสร้างให้คนทั่วไป (non-technical) ใช้ AI agent ได้ง่ายในอนาคต

## 3. Product Philosophy (คำ Owner — จดเป็นหลักการ)

> เรียบหรู ดุแพง น้อยแต่มาก ทรงประสิทธิภาพ
> สร้างของที่ขายตัวมันเองได้ — ขายคุณค่า ไม่ขายวิญญาณ
> เราไม่ใช่วัยแว๊นแต่งซิ่ง เราเป็นวัยผู้ใหญ่ที่สร้างของ

## 4. เครื่องหลัก — Acer TravelMate (solocorp-main)

- CPU i7-3632QM / RAM 16GB / Intel HD 4000 only / LAN เป็นหลัก
- OS ปัจจุบัน: Linux Mint 22.3 (พาหนะที่พามาสู่โลก Linux ครบสมบูรณ์แล้ว — ให้เกียรติ ไม่ทิ้งแบบหักดิบ)
- OS ปลายทาง: **Fedora Workstation (GNOME)** — ตัดสินใจร่วม CEO+Owner แล้ว (ใจตรงกัน)
  - เหตุผล: kernel/toolchain/container/AI stack ใหม่สุด, Podman rootless first-class, Toolbox, SELinux enforcing, Flatpak, อัปเดตเร็ว iterate เร็ว, upstream ของ RHEL
  - ไม่เอา KDE Plasma เป็นหลัก: สวยแรงแต่คือรถแต่ง ของรบกวนเยอะ อัปเดตทีของแต่งหักที — ขัดกับปรัชญาเรียบหรู
  - แผนย้าย: Live USB ทดสอบ HW → backup → dual-boot 2 สัปดาห์ → ย้าย default boot → เซ็ต Podman/Toolbox/SELinux profile สำหรับ agent
- บทบาท: สร้าง + ออกแบบประสบการณ์สะอาดให้คนทั่วไปเข้าสู่โลก Agent โดยไม่ต่อต้าน

## 5. เครื่องรอง — Lenovo Z580 (test host)

- บทบาทใหม่: **โฮสต์ทดลอง** ไม่ใช่ daily driver แล้ว
- แผนดิสก์: ลูกใน = Ubuntu Server (ฐานนิ่ง) / AgenticLinux บน External SSD บูตผ่าน USB (F12) — ไม่ต้องไขควงถอด-ใส่บ่อย
- กันพัง: ทำ Clonezilla image ของทั้งสองลูกก่อนเสมอ
- เน็ตเวิร์ก: **LAN-only** (ไม่ใช้ WiFi — ตัดความเสี่ยง driver เก่าทิ้ง)
- กราฟิก: ล็อก Intel HD อย่างเดียว (BIOS ถ้ามี, ไม่งั้น blacklist nouveau) — ปู่ GT630M Optimus ไม่เหมาะกับ Fedora ใหม่ + Wayland
- บทบาท: ทดลอง + อยู่กับชุมชน Agent แบบเข้มข้น สลับกับ Ubuntu Server เป็นช่วงๆ

## 6. AgenticLinux — บทบาท "ผู้ร่วมก่อร่าง" (ไม่ใช่ user มาขอของ)

- Repo: https://github.com/ericcurtin/agenticlinux (สำรวจ 2026-10-07: 42 stars / 1 fork / 69 commits)
- คืออะไร: bootc image จาก Fedora 44 packages (มี GNOME/KDE/sway/cosmic/xfce/budgie/base + CentOS Stream variants), ติดตั้ง claude/codex/opencode/openclaw/goose + herdr + CodexBar + llmman + Docker Engine (rootful+rootless) + Docker Sandboxes + QEMU/KVM + GPU runtimes มาเลย, rebuild ทุก 4 ชม., rollback คำสั่งเดียว
- ทำไมต้องเข้าตอนนี้: ยังเล็ก ยังไม่สมบูรณ์ ยังไม่มีเจ้าถิ่น — คนเข้าตอนนี้คือคนกำหนดทิศ คนเข้าทีหลังคือผู้ตาม
- ช่องของเรา (ไม่ทับเจ้าถิ่น): เขาทำ "ยัดของมาให้ครบ" แล้ว — ยังไม่มีใครทำ **"UX ให้คนทั่วไปใช้ได้โดยไม่กลัว"** → นั่นคือที่ยืนของเรา เสริมเขา ไม่แย่งเขา
- ข้อควรระวัง: maintainer หลักคนเดียว, image ยังไม่ signed, ฐาน Fedora 44 สดมากเจอบั๊กแน่, เขาใช้ Docker เป็นหลัก ส่วนเราใช้ Podman+SELinux (คุยกันได้ — เอาประสบการณ์ไปแชร์)
- Variant เริ่ม: **gnome** (เทียบ 1:1 กับเครื่องหลัก) — จะสลับ DE ทีหลังใช้ `bootc switch` ได้ ไม่ต้องลงใหม่

### ร่าง Issue แรก (อนุมัติแล้ว — รอ Owner กดส่ง)

```markdown
Title: Greetings from a SoloCorp OS builder focused on non-technical UX

Hi, I'm Dr.Solodev (frontier builder / infrastructure for agents).

I build SoloCorp OS — a small agent orchestration system with
loop runners and tooling, now moving my daily driver to Fedora
GNOME and keeping a spare Lenovo Z580 as a test host.

I found AgenticLinux at the right moment (42 stars, bootc-based,
batteries included) and I'd love to learn from it early rather
than join late as a regular user.

What interests me most:
- clean UX so non-technical people can use agents without fear
- tooling around agents (runners, sandboxes, isolation)
- testing on old hardware (Z580) and reporting bugs clearly

Happy to test, report, and share UX findings. Thanks for
building this in the open — excited to follow and help where I can.

— Dr.Solodev
```

- กติกา Issue แรก: สั้น สุภาพ มีทิศ ไม่ขายฝันเกิน ไม่วิจารณ์แรงก่อนใช้จริง ไม่สัญญาฟีเจอร์ก่อนคุย ภาษาอังกฤษ เปิดแล้วรอดูตอบก่อนค่อยขยาย

## 7. การแยกเซสชัน (คำสั่ง Owner 2026-10-07)

- ฝัน/เส้นทางก้าวเดิน → คุยในแชทนี้ (CEO chat)
- โปรเจกต์อื่นที่กำลังสร้าง → คุยแยกในเซสชันของมัน ไม่ปนกัน — เลื่อนแชทดูข้อมูลได้ แยกกันชัดเจน

---

*Owner ฝัน → CEO สั่ง → Architect ออกแบบ → ทีมสร้าง → องค์กรอยู่ยืนยง*
*บันทึกโดย CEO หนุมาน — หมุดนี้ถาวร เปลี่ยนได้เฉพาะ Owner (L5) เท่านั้น*
