# LogiThai Express Website

ระบบเว็บไซต์สำหรับบริษัท LogiThai Express ให้บริการโลจิสติกส์ครบวงจร

## โครงสร้างเว็บไซต์

เว็บไซต์นี้ใช้เทคโนโลยี **HTML/CSS/JavaScript** แบบ Static ไม่ต้องพึ่งพา React หรือ Node.js

### ไฟล์หลัก

- `index.html` - หน้าแรก (Homepage)
- `about.html` - หน้าเกี่ยวกับเรา
- `services.html` - หน้าบริการ  
- `quote.html` - หน้าขอใบเสนอราคา
- `404.html` - หน้า Error 404

### โครงสร้างโฟลเดอร์

```
/
├── index.html          # หน้าแรก
├── about.html          # เกี่ยวกับเรา
├── services.html       # บริการ
├── quote.html          # ขอใบเสนอราคา
├── 404.html           # หน้า Error
├── static/            # ไฟล์ Static
│   ├── css/
│   │   └── style.css  # CSS หลัก
│   ├── js/
│   │   ├── main.js    # JavaScript หลัก
│   │   ├── about.js   # Script สำหรับหน้า About
│   │   ├── services.js # Script สำหรับหน้า Services
│   │   └── quote.js   # Script สำหรับหน้า Quote
│   └── images/        # รูปภาพ
└── app.py            # Python Flask server (สำหรับฟอร์ม)
```

## การเปิดเว็บไซต์

### วิธีที่ 1: เปิดไฟล์โดยตรง
เปิดไฟล์ `index.html` ใน Browser โดยตรง

### วิธีที่ 2: ใช้ HTTP Server
```bash
# Python 3
python3 -m http.server 8000

# Python 2
python -m SimpleHTTPServer 8000

# Node.js (ถ้ามี)
npx serve .
```

จากนั้นเปิด http://localhost:8000

## คุณสมบัติ

- ✅ **ไม่มี White Screen** - ใช้ HTML/CSS/JS แบบ Static
- ✅ **การนำทางที่เสถียร** - ไม่มีปัญหา routing
- ✅ **ง่ายต่อการแก้ไข** - ไม่ต้องใช้ build process
- ✅ **รองรับ Mobile** - Responsive design ด้วย Tailwind CSS
- ✅ **รวดเร็ว** - โหลดเร็วไม่ต้องรอ JavaScript compilation

## การแก้ไข

1. **แก้ไขเนื้อหา**: แก้ไขในไฟล์ `.html` โดยตรง
2. **แก้ไขสไตล์**: แก้ไขใน `static/css/style.css`
3. **แก้ไขฟังก์ชัน**: แก้ไขใน `static/js/main.js` หรือไฟล์ JS ที่เกี่ยวข้อง

## เทคโนโลยีที่ใช้

- **HTML5** - โครงสร้างหน้าเว็บ
- **CSS3** - การจัดแต่งหน้าตา
- **JavaScript (Vanilla)** - ฟังก์ชันการทำงาน
- **Tailwind CSS** - Framework สำหรับ CSS
- **Font Awesome** - ไอคอน
- **Python Flask** - Backend สำหรับฟอร์ม (เฉพาะ app.py)

## การติดต่อ

หากมีปัญหาหรือต้องการแก้ไขเพิ่มเติม สามารถติดต่อทีมพัฒนาได้
