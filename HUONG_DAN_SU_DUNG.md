# Huong Dan Su Dung - AI Study Assistant

> Tai lieu nay huong dan chi tiet cach cai dat va su dung ung dung.
> Danh cho tat ca nguoi dung, ke ca nguoi khong co nen tang IT.

---

## Muc luc

1. [Yeu cau he thong](#1-yeu-cau-he-thong)
2. [Lay API Key mien phi](#2-lay-api-key-mien-phi-google-gemini)
3. [Cai dat ung dung](#3-cai-dat-ung-dung)
4. [Cach su dung tung tinh nang](#4-cach-su-dung-tung-tinh-nang)
5. [Cac loi thuong gap va cach xu ly](#5-cac-loi-thuong-gap-va-cach-xu-ly)
6. [Luu y an toan](#6-luu-y-an-toan)

---

## 1. Yeu cau he thong

| Yeu cau | Chi tiet |
|---------|---------|
| **He dieu hanh** | Windows 10/11, macOS, hoac Linux |
| **Python** | Phien ban 3.10 tro len |
| **Trinh duyet** | Chrome, Firefox, Edge (bat ky trinh duyet hien dai) |
| **Ket noi mang** | Can Internet de goi AI API |

### Kiem tra Python da cai chua

Mo Terminal (hoac Command Prompt tren Windows) va go:

```bash
python --version
```

Neu hien `Python 3.10.x` tro len la duoc. Neu chua cai, tai tai: https://www.python.org/downloads/

> **Luu y cho Windows:** Khi cai Python, nho tich vao o **"Add Python to PATH"**.

---

## 2. Lay API Key mien phi (Google Gemini)

API Key la "mat khau" de ung dung ket noi voi AI. Ban can 1 key de su dung.

### Cach lay (mien phi, khong can the tin dung):

1. Mo trinh duyet, truy cap: **https://aistudio.google.com/apikey**
2. Dang nhap bang tai khoan Google (Gmail)
3. Nhan nut **"Create API key"**
4. Chon **"Create API key in new project"**
5. Key se hien len (bat dau bang `AIza...`) — nhan **Copy**

> Luu key nay lai (dan vao Notepad). Ban se can no khi su dung ung dung.
>
> **Khong chia se key cho nguoi khac.** Key nay la cua rieng ban.

### Neu muon dung provider khac (khong bat buoc):

| Provider | Link dang ky | Chi phi |
|----------|-------------|---------|
| Google Gemini | https://aistudio.google.com/apikey | Mien phi |
| Anthropic Claude | https://console.anthropic.com/ | Tra phi ($5 credit khi dang ky) |
| OpenAI GPT | https://platform.openai.com/api-keys | Tra phi |

---

## 3. Cai dat ung dung

### Cach 1: Tai tu GitHub (khuyen nghi)

```bash
# Buoc 1: Tai source code
git clone <link-repo>.git
cd END_OF_COURSE_PROJECT

# Buoc 2: Vao thu muc ung dung
cd src/v2

# Buoc 3: Cai dat thu vien
pip install -r requirements.txt

# Buoc 4: Chay ung dung
streamlit run app.py
```

### Cach 2: Tai file ZIP

1. Tren trang GitHub cua du an, nhan nut xanh **"Code"** > **"Download ZIP"**
2. Giai nen file ZIP
3. Mo Terminal, `cd` vao thu muc `src/v2`
4. Chay `pip install -r requirements.txt`
5. Chay `streamlit run app.py`

### Ket qua

Trinh duyet se tu dong mo tai dia chi: **http://localhost:8501**

Neu khong tu mo, hay copy dia chi tren va dan vao trinh duyet.

---

## 4. Cach su dung tung tinh nang

### 4.0. Thiet lap ban dau (lam 1 lan)

Khi ung dung mo len:

1. O thanh ben trai (**sidebar**), tim muc **"Cau hinh"**
2. Chon **LLM Provider**: `Gemini (Google — Mien phi)` (da chon san)
3. Dan **API Key** da copy o Buoc 2 vao o "API Key"

### 4.1. Upload tai lieu

1. O thanh ben trai, nhan **"Browse files"**
2. Chon file tai lieu cua ban:
   - **PDF**: Toi da 50 trang, phai la PDF co text (khong phai PDF scan/hinh anh)
   - **TXT**: Toi da 100KB
3. Nhap **ten mon hoc** (vi du: "Cau truc du lieu va giai thuat")
4. Doi he thong xu ly — khi thay thong bao xanh "Da xu ly: X chunks" la thanh cong

### 4.2. Tom Tat Tai Lieu (Tab "Tom Tat")

1. Nhan tab **"Tom Tat"** o khu vuc chinh
2. Chon muc do:
   - **Lop 1: Key Points** — 5-7 diem chinh ngan gon (dung khi can nam nhanh)
   - **Lop 2: Phan tich co cau truc** — Phan tich theo tung chu de (dung khi hoc ky)
   - **Lop 3: Nhan xet sau** — Lien he giua cac khai niem (dung khi on thi)
3. Nhan **"Tao Tom Tat"**
4. Doc ket qua — chu y cac trich dan **[Trang X]** de doi chieu voi tai lieu goc

### 4.3. Tao Cau Hoi On Tap (Tab "Cau Hoi On Tap")

1. Nhan tab **"Cau Hoi On Tap"**
2. Keo thanh truot chon so luong cau hoi (5-20)
3. Chon muc do kho:
   - **Can bang**: 40% Nho, 30% Ap dung, 30% Phan tich
   - **De**: Nhieu cau nho, it cau kho
   - **Kho**: Nhieu cau phan tich
4. Nhan **"Tao Cau Hoi"**
5. (Tuy chon) Nhan **"Tao file Anki TSV"** de xuat flashcard, roi **"Download"**

> **Meo:** Neu tai lieu ngan, he thong se tu dong canh bao va goi y so cau hoi phu hop.

### 4.4. Giai Thich Khai Niem (Tab "Giai Thich")

1. Nhan tab **"Giai Thich"**
2. Nhap khai niem can giai thich (vi du: `Binary Search Tree`)
3. Chon che do:
   - **Chain of Thought**: AI giai thich tung buoc tu co ban den nang cao
   - **Socratic Tutoring**: AI hoi nguoc ban de ban tu kham pha
4. Nhan **"Giai Thich"**

> **Luu y:** Neu khai niem khong co trong tai lieu, AI se tra loi:
> *"Thong tin nay khong co trong tai lieu duoc cung cap."*
> Day la hanh vi dung — AI khong bia thong tin.

### 4.5. Danh Gia Cau Tra Loi (Tab "Danh Gia")

1. Nhan tab **"Danh Gia"**
2. Nhap **cau hoi** vao o dau tien
3. Nhap **cau tra loi cua ban** vao o thu hai
4. Nhan **"Danh Gia"**
5. Xem ket qua:
   - Diem so (X/10)
   - Nhung diem dung va sai
   - Goi y cai thien
   - Dap an tham khao tu tai lieu

---

## 5. Cac loi thuong gap va cach xu ly

| Loi | Nguyen nhan | Cach khac phuc |
|-----|------------|----------------|
| "Chua cung cap API Key" | Chua dan key vao o API Key | Dan API Key vao o o sidebar ben trai |
| "File trong hoac khong doc duoc" | File PDF la anh scan, khong co text | Dung file PDF co text, hoac convert sang TXT |
| "Vuot qua gioi han 50 trang" | File qua dai | Chia file thanh nhieu phan nho roi upload tung phan |
| Ket qua khong chinh xac | AI hallucination | Doi chieu voi tai lieu goc. Nhan "Tao Tom Tat" lai |
| "Loi sau 3 lan thu" | API key sai hoac het han | Kiem tra lai API key. Tao key moi neu can |
| App khong mo | Port 8501 dang bi chiem | Thu: `streamlit run app.py --server.port 8502` |
| Canh bao vang trong ket qua | He thong phat hien ket qua co the chua chinh xac | Doc ky canh bao va doi chieu thong tin voi tai lieu goc |

---

## 6. Luu y an toan

### Quy tac vang

> **KHONG BAO GIO tin AI 100%.** Ket qua AI chi la tham khao — luon doi chieu voi tai lieu goc.

### Nen lam

- Upload tai lieu hoc thuat cong khai (slides da publish, giao trinh online)
- Su dung API key ca nhan
- Dong tab/trinh duyet sau khi su dung xong
- Thu tu tra loi truoc khi xem dap an cua AI (active recall)

### KHONG nen lam

- Upload de thi chua cong bo hoac tai lieu mat
- Nhap thong tin ca nhan (MSSV, email, so dien thoai)
- Chia se API key cho nguoi khac
- Su dung ket qua AI de nop bai hoac gian lan thi cu
- De phien lam viec mo tren may tinh cong cong

### Phan loai tai lieu truoc khi upload

| Loai | Co the upload? | Vi du |
|------|---------------|-------|
| **Cong khai** | Co | Slides da publish, giao trinh online |
| **Noi bo** | Can than | Slides noi bo lop hoc |
| **Nhay cam** | Khong | De thi, bai giai chinh thuc |
| **Bi mat** | Tuyet doi khong | Du lieu ca nhan, thong tin mat |

---

## Hoi dap nhanh

**H: Toi co can biet lap trinh khong?**
D: Khong. Chi can biet cai Python va chay 2 lenh trong Terminal la dung duoc.

**H: Phi su dung bao nhieu?**
D: Mien phi neu dung Google Gemini. Chi phi API key cua Claude/GPT thi tuy vao luong su dung.

**H: Tai lieu cua toi co bi luu lai khong?**
D: Khong. Tai lieu chi ton tai trong phien lam viec (session). Khi dong tab, du lieu bi xoa.

**H: Co chay tren dien thoai duoc khong?**
D: Ung dung web nen co the mo tren trinh duyet dien thoai, nhung trai nghiem tot nhat tren may tinh.

**H: Tai sao AI tu choi tra loi?**
D: Vi khai niem ban hoi khong co trong tai lieu da upload. Day la thiet ke co chu dich (Zero-Trust) — AI chi tra loi dua tren noi dung tai lieu de tranh bia thong tin sai.

---

*AI Study Assistant — AOTS AI Engineering Program, HCMUT 2026.*
