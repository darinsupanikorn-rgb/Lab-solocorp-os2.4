# USAGE — NDA One-way (สัญญา NDA แบบทางเดียว)

## ใช้เมื่อไร

ใช้เมื่อ **เฉพาะ SoloCorp (หรือฝ่ายเปิดเผย)** เป็นฝ่ายเปิดเผยข้อมูลลับแต่เพียงฝ่ายเดียว เช่น:

| Use Case | รายละเอียด |
|:---------|:------------|
| **Vendor engagement** | จ้าง外包 / vendor ที่ต้องเข้าถึง source code, ระบบหลังบ้าน, ข้อมูลลูกค้า |
| **Employee/Contractor onboarding** | พนักงานใหม่ หรือ freelance ที่จะเข้าถึงข้อมูลภายใน |
| **Investor pitch** | พบ VC หรือ angel investor (แม้หลายรายไม่เซ็น NDA — ไว้ป้องกันกรณีมี info leak) |
| **Partnership discussion** | หารือ partnership ที่ SoloCorp เปิดเผย technical/business info ฝ่ายเดียว |
| **DeFi protocol integration** | คุยกับทีม DeFi อื่นที่ต้องรู้ technical spec ของ SoloCorp |

**ถ้าทั้งสองฝ่ายแลกเปลี่ยนข้อมูลลับ → ใช้ `nda-mutual` แทน**

## ขั้นตอนการใช้งาน

1. **กำหนดวัตถุประสงค์** — ระบุในข้อ 1 ให้ชัดเจน (เช่น "เพื่อพิจารณาการจ้างงาน", "เพื่อประเมินเทคโนโลยี")
2. **เลือก use case → ปรับ scope ข้อ 2** — ถ้าที่กำหนดไว้ครอบคลุมแล้ว ใช้ได้เลย
3. **ระยะเวลาสัญญา** — ข้อ 6.1: **2 ปี** (default) — ปรับเป็น 3 ปีได้ถ้าเปิดเผย IP สำคัญ
4. **Survival period** — ข้อ 6.2: **3 ปี** (default) — trade secret เป็น indefinite ตามกฎหมาย
5. **พิจารณา arbitration** — ถ้าคู่สัญญาต่างชาติ → เพิ่มข้อ 9.4 (THAC arbitration)
6. **กรอกข้อมูลคู่สัญญา** — ชื่อ ที่อยู่ ตำแหน่งผู้มีอำนาจลงนาม
7. **ให้ผู้เกี่ยวข้อง review:**
   - CFO (`meetoo`) — review ข้อ 8 (เยียวยา), ข้อ 9 (ข้อพิพาท)
   - Orchestrator หรือ CEO — อนุมัติ
8. **ลงนามทั้งสองฝ่าย** — เก็บต้นฉบับที่ SoloCorp

## ใครอนุมัติ

| มูลค่า / ความเสี่ยง | ระดับการอนุมัติ |
|:--------------------|:----------------|
| ใช้งานทั่วไป (vendor, contractor ทั่วไป) | หัวหน้าแผนก + Orchestrator |
| เปิดเผย source code, trade secret, IP หลัก | CEO (หนุมาน) อนุมัติ |
| contract value > 1,000,000 บาท | CFO (meetoo) co-sign |
| กรณีเกี่ยวข้องกับ on-chain / DeFi data | อาจต้อง Web3 (aywa) review ข้อ 2 |

## ข้อควรระวัง

### 1. Investor Pitch
- VC/angel ส่วนใหญ่ **ไม่ยอมเซ็น NDA** สำหรับ pitch ทั่วไป
- ใช้ NDA นี้เฉพาะเมื่อคุณมั่นใจว่าฝ่ายรับตกลง หรือเมื่อต้องเปิดเผย technical detail/architecture
- ทางเลือก: pitch เฉพาะ public info ก่อน, แล้วค่อยยื่น NDA ก่อน deep-dive

### 2. Employee/Contractor
- ต้องดูว่ามี **IP Assignment Agreement** ประกอบด้วย (ไฟล์ที่เกี่ยวข้อง: `ip-assignment`)
- สำหรับพนักงานทั่วไป สัญญาจ้างงานควรมี confidentiality clause อยู่แล้ว — NDA นี้ใช้เพิ่มเติมกรณีพิเศษ

### 3. DeFi/Web3
- ข้อ 2(ค) ครอบคลุม on-chain data, smart contract, strategy แล้ว
- ปรึกษา aywa (Web3) ถ้าข้อมูลที่เปิดเผยเป็น protocol-critical หรือ MEV-sensitive

### 4. Vendor
- ตรวจสอบว่า vendor มีมาตรการรักษาความปลอดภัยข้อมูล (ISMS) ที่เพียงพอ
- สำหรับ vendor ที่เป็น AI/LLM service → ต้องระบุห้ามใช้ข้อมูลของ SoloCorp train model

### 5. ต่างชาติ
- ถ้าฝ่ายรับอยู่ต่างประเทศ → เพิ่ม arbitration clause (ข้อ 9.4)
- ตรวจสอบว่ากฎหมายประเทศฝ่ายรับมีมาตรการคุ้มครองความลับทางการค้าที่เทียบเท่า

### 6. PDPA
- ข้อ 2(จ) ครอบคลุมข้อมูลส่วนบุคคลแล้ว
- ถ้าฝ่ายรับเป็น "ผู้ประมวลผลข้อมูลส่วนบุคคล" → ต้องมี Data Processing Agreement (DPA) เพิ่มเติม

## ความแตกต่างจาก NDA Mutual

| หัวข้อ | NDA Mutual (สองทาง) | NDA One-way (ทางเดียว) |
|:-------|:-------------------|:----------------------|
| ใครมี obligation | ทั้งสองฝ่าย | เฉพาะฝ่ายรับ |
| ใครเปิดเผยข้อมูล | ทั้งสองฝ่าย | เฉพาะฝ่ายเปิดเผย (SoloCorp) |
| ระยะเวลาสัญญา | 2-3 ปี | 2 ปี (default) |
| Survival | 3 ปี | 3 ปี (ทั่วไป) / indefinite (trade secret) |
| กรรมสิทธิ์ข้อมูล | ฝ่ายเปิดเผยของแต่ละฝ่าย | ฝ่ายเปิดเผย (SoloCorp) |
| Disclaimer | ไม่มี | มีข้อ 4 (as-is, no obligation to disclose) |
| ความซับซ้อน | ปานกลาง | น้อยกว่า (simpler) |

## เอกสารอ้างอิง

- พ.ร.บ. ความลับทางการค้า พ.ศ. 2545 — มาตรา 3 (นิยาม), มาตรา 5 (การละเมิด), มาตรา 7 (ข้อยกเว้น)
- ประมวลกฎหมายแพ่งและพาณิชย์ — มาตรา 149 (นิติกรรม), มาตรา 194 (หนี้)
- พ.ร.บ. คุ้มครองข้อมูลส่วนบุคคล พ.ศ. 2562 — มาตรา 26 (ความลับของข้อมูลส่วนบุคคล)
- US template reference: `ref-us.md` (Cooley One-way NDA)
- แหล่งอ้างอิง:
  - Five Minute Law — Plain-Language NDA philosophy
  - Cooley GO One-way NDA (US) — standard clause structure
  - OneNDA — modern plain-language format
