# Production Brief (2026-09-28T00:16:36+07:00)

🎬 PRODUCTION BRIEF: SoloCorp OS 2.4
1) คืออะไร: ไม่ใช่โค้ดทั่วไป แต่คือ Organizational OS สำหรับ AI agents
แบบ docs-as-code: `profiles/*/SOUL.md` คือตัวตนแผนก, `rules/` คือพฤติกรรม 6 ไฟล์, `sop/` คือวิธีทำ, `central_bus/` คือ service จริงตัวเดียว (busd :8099 + govctl :8765)
หลักการ: Heads Lead, Agents Execute / Head-to-Head / แยก Control (สั่ง-อนุมัติ) vs Data (ของ-งานผ่าน Bus) / ทุกงานมีเจ้าของ / Audit Everything
โครง L5 Owner → L4 CEO → L3 COO → 19 Dept Heads + 62+ Specialists (.codex/*.toml + .claude/agents + skills)
2) ตัวละครหลัก:
Owner Dr.solodev (L5): Vision + Final Say อย่างเดียว ห้ามแตะงาน L1-L3
CEO หนุมาน Turbo (L4, default agent): ทิศทาง-สั่ง-ชี้ขาด ไม่โค้ดเอง
COO กิจ Kit (L3): ประตู daily ops กันงานเล็กไม่ให้ถึง Owner
CFO meetoo: งบ-ต้นทุน / CMO มาร์ค Mark: การตลาด-brand-content / Architect ทรงศักดิ์: Central Bus, routing, pipeline
Orchestrator วุฒิ: pipeline autopilot / Product โปรดัค: roadmap / Engineering ช่างฟูล: code / Design ครีเอท + UI: UX/visual
QA / Sales / Support / Legal ตุลย์ / Web3 อัยวา / Content เสก / NetEng / CyberSec: ทีมเฉพาะทาง รับงานจาก Head เท่านั้น ห้ามคุยข้ามแผนกตรง
3) 3 PLOT THREADS สำหรับ EP ต่อไป:
EP1 “ห้อง Forum ที่ห้ามลงมือทำ” - ไอเดีย Owner: ตกผลึกด้านเดียวทำให้พลาดมุมสำคัญ → CEO โยนแผนกลางห้อง รับหมด-ห้ามวิจารณ์รอบแรก สถานะ SPEC LOCKED รอไฟเขียวบิลด์
EP2 “Bus ฆ่าคอขวด” - งาน 80% ส่งตรง Head-to-Head ไม่ผ่านคนกลาง, escalation แค่ 5% - Control คุยกัน Data วิ่งผ่านคิว จะรอดไหมถ้า Bus ล่ม?
EP3 “หัวหน้าห้ามทำงาน” - Head ที่เขียนโค้ดเอง = sys
