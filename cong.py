# -*- coding: utf-8 -*-
"""cong.py — bo cong kiem cho mot du an chay bang AI.

    python kit/cong.py              chay het cac cong
    python kit/cong.py --ngoai      chay them cong goi ra Internet
    python kit/cong.py --tu-kiem    CHUNG MINH tung cong co the truot

MOT FILE, KHONG CAI DAT GI. Chep file nay vao du an cua ban la chay duoc.

VI SAO NO TON TAI
-----------------
Mot bo tieu chuan viet ra giay duoc thi hanh boi chinh nguoi bi rang buoc. Do
khong phai mot ranh gioi. Du an sinh ra file nay da do duoc dieu do: no GOI TEN
co che loi cua chinh no bang chu, roi van lap lai co che do 16 lan — sau lan
trong so do xay ra NGAY TRONG LUC dang viet ve co che ay, hoac dang
dung chinh cai cong sinh ra de bat no.

Thu bat duoc lan thu 11 khong phai mot cau nhac nho. La mot phep kiem chay
NGOAI phan doan cua nguoi viet, va doi hoi ket qua phai doi.

HAI LUAT CUA CHINH FILE NAY
---------------------------
1. Moi cong phai khai bao no KHONG chung minh duoc gi. Mot cau nghe nhu loi bao
   dam ma thuc chat noi it hon la mot cai bay — va no bay dung nguoi tin no nhat.
2. Moi cong phai co trong --tu-kiem, kem mot cach PHA no. Mot phep kiem chua bao
   gio bao do thi ban chua biet no bao do duoc khong.

Moi thu in ra deu la ASCII. Do tren Windows: console cp1252, print tieng Viet
co dau thi UnicodeEncodeError. Noi dung file thi UTF-8 tieng Viet binh thuong.
"""
import glob
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata

# Phien ban cua bo kit. Ban da chep file nay vao du an cua ban, nen no
# khong tu cap nhat — con so nay la cach duy nhat biet ban dang giu ban nao.
# Thay doi giua cac ban: CHANGELOG.md trong kho pos-kit.
PHIEN_BAN = "1.0.0"

GOC = os.getcwd()
NL = chr(10)

# Thu muc khong bao gio quet
BO_QUA_THU_MUC = {".git", "node_modules", "__pycache__", ".venv", "venv",
                  ".wrangler", "dist", "build", ".next", ".cache"}

# File khai bao phu thuoc ngoai, moi dong: <url><TAB hoac 2 space><vai tro>
TEP_PHU_THUOC = "phu-thuoc-ngoai.txt"

# File khai bao nhung cho CO Y sai — vi du mot fixture day hoc mang loi co chu y.
# Moi dong khong bat dau bang '#' la mot duong dan (hoac tien to duong dan).
#
# Vi sao mot DANH SACH KHAI BAO chu khong phai mot luat am trong code: mot cong
# keu nham se bi nguoi sau tat di, va do la ket cuc te nhat. Nhung mot cho duoc
# mien tru ma khong ai nhin thay cung te khong kem — nen danh sach nay duoc IN RA
# moi lan chay.
TEP_BO_QUA = "kit/bo-qua.txt"


def nap_bo_qua(goc):
    """Tra ve (danh sach tien to duong dan, duong dan file khai bao)."""
    f = os.path.join(goc, TEP_BO_QUA)
    if not os.path.exists(f):
        f2 = os.path.join(goc, "bo-qua.txt")
        if not os.path.exists(f2):
            return [], None
        f = f2
    ra = []
    for d in doc(f).splitlines():
        d = d.strip()
        if d and not d.startswith("#"):
            ra.append(d.replace("\\", "/").rstrip("/"))
    return ra, ngan(goc, f)


def bi_bo_qua(duong_dan_ngan, ds):
    for x in ds:
        if duong_dan_ngan == x or duong_dan_ngan.startswith(x + "/"):
            return True
    return False


# ===================================================================== tien ich
def moi_file(goc, duoi=(".md",)):
    for thu, cac_thu, cac_tep in os.walk(goc):
        cac_thu[:] = [d for d in cac_thu if d not in BO_QUA_THU_MUC]
        for t in cac_tep:
            if t.lower().endswith(duoi):
                yield os.path.join(thu, t)


def doc(f):
    try:
        return io.open(f, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def ngan(goc, f):
    return os.path.relpath(f, goc).replace("\\", "/")


def tim_tep(goc, *ten):
    """Tra ve duong dan dau tien tim thay trong cac ten duoc dua vao."""
    for t in ten:
        p = os.path.join(goc, t)
        if os.path.exists(p):
            return p
    for f in moi_file(goc):
        if os.path.basename(f).lower() in {x.lower() for x in ten}:
            return f
    return None


def khong_dau(s):
    """Bo dau tieng Viet de so sanh. Tra ve chu thuong, khong dau.

    Vi sao can: danh sach tu khoa trong file nay viet KHONG DAU (de chinh file
    nay chay duoc tren console cp1252), con noi dung nguoi ta viet thi CO DAU.
    Ban dau hai ben duoc so thang voi nhau, va cong bao xanh vinh vien — no
    khong bao gio khop duoc mot chu tieng Viet that. Mot phep kiem khong nhin
    thay gi va mot phep kiem khong thay loi nao trong giong het nhau.
    """
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.replace("\u0111", "d")


def git(goc, *args):
    try:
        k = subprocess.run(["git"] + list(args), cwd=goc, capture_output=True,
                           text=True, encoding="utf-8", errors="replace")
        return k.returncode, k.stdout or ""
    except OSError:
        return 127, ""


# ======================================================================= cong 1
def cong_trang_thai(goc):
    """File trang thai co ton tai va con duoc cap nhat khong."""
    ra = []
    f = tim_tep(goc, "STATE.md", "docs/STATE.md", "TRANG-THAI.md", "CURRENT.md")
    if not f:
        ra.append(("HONG", "Khong tim thay file trang thai (STATE.md)"))
        ra.append(("   ", "Phien sau se bat dau bang cach doan. Do la cho du an"))
        ra.append(("   ", "bat dau troi ma khong ai bao."))
        return 1, ra

    ra.append(("ok", "File trang thai: %s" % ngan(goc, f)))

    ma, out = git(goc, "log", "-1", "--format=%ct", "--", f)
    if ma == 0 and out.strip().isdigit():
        ngay = (time.time() - int(out.strip())) / 86400.0
        ma2, out2 = git(goc, "log", "-1", "--format=%ct")
        if ma2 == 0 and out2.strip().isdigit():
            ngay_commit = (time.time() - int(out2.strip())) / 86400.0
            lech = ngay - ngay_commit
            if lech > 14:
                ra.append(("HONG", "Trang thai cu hon commit gan nhat %d ngay" % lech))
                ra.append(("   ", "Repo da di tiep ma file trang thai thi khong."))
                ra.append(("   ", "Day la tai lieu cu gia lam su that hien tai."))
                return 1, ra
            ra.append(("ok", "Trang thai cu hon commit gan nhat %.1f ngay" % lech))
    return 0, ra


cong_trang_thai.mo_ta = "File trang thai con song"
cong_trang_thai.chung_minh = "co file trang thai, va no khong tut lai qua xa so voi commit"
cong_trang_thai.khong_chung_minh = "NOI DUNG trong do con dung. May khong doc duoc y nghia."
cong_trang_thai.pha = lambda g: _pha_xoa(g, ["STATE.md", "docs/STATE.md"])


# ======================================================================= cong 2
TRANG_THAI_GD = ("CHUA-KIEM", "DA-XAC-NHAN", "DA-BAC-BO", "HET-HAN",
                 "UNVERIFIED", "VALIDATED", "REJECTED", "EXPIRED")


def cong_gia_dinh(goc):
    """So gia dinh: moi gia dinh con song phai co trang thai va han kiem."""
    ra = []
    f = tim_tep(goc, "GIA-DINH.md", "docs/GIA-DINH.md", "ASSUMPTIONS.md",
                "docs/ASSUMPTIONS.md")
    if not f:
        ra.append(("--", "Khong co so gia dinh — bo qua cong nay"))
        ra.append(("  ", "Neu du an dang dua tren dieu gi chua kiem, do la cho"))
        ra.append(("  ", "no nen duoc viet ra. Tao san bang:"))
        ra.append(("  ", "  python kit/khoi-tao.py . --day-du"))
        return 0, ra

    t = doc(f)
    dong = [d for d in t.splitlines() if d.strip().startswith("|")]
    hang = [d for d in dong if not re.match(r"^\|[\s:|-]+\|$", d.strip())][1:]
    if not hang:
        ra.append(("HONG", "So gia dinh co mat nhung KHONG CO gia dinh nao"))
        ra.append(("   ", "Mot so rong doc y het mot so chua bao gio duoc mo."))
        return 1, ra

    thieu, het_han = [], []
    for h in hang:
        o = [x.strip() for x in h.strip().strip("|").split("|")]
        noi_dung = o[0] if o else ""
        if not noi_dung or noi_dung.startswith("<"):
            continue
        co_tt = any(tt in h.upper() for tt in TRANG_THAI_GD)
        if not co_tt:
            thieu.append(noi_dung[:54])
        ngay = re.search(r"(20\d\d)-(\d\d)-(\d\d)", h)
        if ngay and "HET-HAN" not in h.upper() and "EXPIRED" not in h.upper():
            try:
                han = time.mktime(time.strptime(ngay.group(0), "%Y-%m-%d"))
                if time.time() > han and ("CHUA-KIEM" in h.upper()
                                          or "UNVERIFIED" in h.upper()):
                    het_han.append("%s (han %s)" % (noi_dung[:40], ngay.group(0)))
            except ValueError:
                pass

    ra.append(("ok", "So gia dinh: %s, %d gia dinh" % (ngan(goc, f), len(hang))))
    for x in thieu:
        ra.append(("HONG", "Gia dinh khong co trang thai: %s" % x))
    for x in het_han:
        ra.append(("HONG", "Gia dinh QUA HAN KIEM ma van CHUA-KIEM: %s" % x))
    if thieu or het_han:
        ra.append(("   ", "Mot gia dinh khong co han kiem se thanh su that chi vi"))
        ra.append(("   ", "no duoc lap lai du nhieu lan."))
        return 1, ra
    return 0, ra


cong_gia_dinh.mo_ta = "So gia dinh co han kiem"
cong_gia_dinh.chung_minh = "moi gia dinh ghi ra deu co trang thai, va khong cai nao qua han ma van chua kiem"
cong_gia_dinh.khong_chung_minh = "gia dinh QUAN TRONG NHAT da duoc viet ra. Cai nguy hiem nhat thuong la cai khong ai nghi la gia dinh."
def _pha_gia_dinh(goc):
    """Gieo mot hang gia dinh KHONG CO TRANG THAI.

    Ban dau phep pha nay chi noi them mot dong. Tren mot kho CHUA CO so gia
    dinh, no tao ra file chi co dung mot dong — va cong truot vi "so rong",
    khong phai vi "hang thieu trang thai". Phep thu van bao DAT, nhung no dang
    thu MOT THU KHAC voi thu no khai. Phai viet ca bang de no thu dung cho.
    """
    hang_xau = ("| gia dinh gieo de thu cong | nguon | hong nang |"
                " cach kiem | 2099-01-01 |  |" + NL)
    for ten in ("GIA-DINH.md", "docs/GIA-DINH.md"):
        p = os.path.join(goc, ten)
        if os.path.exists(p):
            with io.open(p, "a", encoding="utf-8", newline="") as h:
                h.write(hang_xau)
            return
    io.open(os.path.join(goc, "GIA-DINH.md"), "w",
            encoding="utf-8", newline="").write(
        "# So gia dinh" + NL + NL
        + "| Gia dinh | Tu dau | Sai thi hong gi | Kiem the nao | Han | Trang thai |" + NL
        + "|---|---|---|---|---|---|" + NL
        + "| gia dinh lanh | nguon | hong nhe | cach kiem | 2099-01-01 | CHUA-KIEM |" + NL
        + hang_xau)


cong_gia_dinh.pha = _pha_gia_dinh


# ======================================================================= cong 3
LENH = re.compile(r"""(?x)
    (?:^|\s|`)
    (python3?|node|npm\s+run|yarn|make|bash|sh|go\s+run|cargo\s+run|deno)
    \s+([A-Za-z0-9_./\\-]+)
""")
TEN_TAI_LIEU = {"readme.md", "readme.rst", "readme.txt", "contributing.md",
                "install.md", "setup.md", "huong-dan.md", "getting-started.md"}


def cong_lenh_tai_lieu(goc):
    """Lenh ghi trong tai lieu co tro toi file co that khong."""
    ra, hong, da_soi = [], [], 0
    bo, tep_bo = nap_bo_qua(goc)
    if bo:
        ra.append(("--", "Bo qua %d cho da khai bao trong %s" % (len(bo), tep_bo)))
        for x in bo:
            ra.append(("  ", "   %s" % x))
    for f in moi_file(goc, (".md", ".rst", ".txt")):
        if os.path.basename(f).lower() not in TEN_TAI_LIEU:
            continue
        if bi_bo_qua(ngan(goc, f), bo):
            continue
        for m in LENH.finditer(doc(f)):
            cong_cu, muc = m.group(1).strip(), m.group(2)
            da_soi += 1
            if cong_cu.startswith(("npm", "yarn", "make", "go", "cargo")):
                continue
            if not re.search(r"\.(py|js|mjs|ts|sh)$", muc):
                continue
            if not os.path.exists(os.path.join(goc, muc)):
                hong.append("%s  ->  %s %s" % (ngan(goc, f), cong_cu, muc))

    if da_soi == 0:
        ra.append(("--", "Khong tim thay lenh chay nao trong tai lieu"))
        return 0, ra
    if not hong:
        ra.append(("ok", "%d lenh trong tai lieu deu tro toi file co that" % da_soi))
        return 0, ra
    for x in hong:
        ra.append(("HONG", x))
    ra.append(("   ", "Nguoi moi lam theo tai lieu se vap ngay o buoc dau."))
    return 1, ra


cong_lenh_tai_lieu.mo_ta = "Lenh trong tai lieu chay duoc"
cong_lenh_tai_lieu.chung_minh = "file ma lenh tro toi co ton tai"
cong_lenh_tai_lieu.khong_chung_minh = "lenh do CHAY duoc, hay chay ra ket qua dung. No chi kiem su ton tai."
cong_lenh_tai_lieu.pha = lambda g: _pha_them(
    g, ["README.md", "docs/README.md"],
    "\n\nChay thu: `python khong-he-ton-tai-9k2x.py`\n")


# ======================================================================= cong 4
HINH_DANG_BI_MAT = [
    (r"(?i)\b(password|passwd|secret|token|api[_-]?key|private[_-]?key)\b\s*[:=]\s*['\"][^'\"]{6,}",
     "gan gia tri cho mot ten nghe nhu bi mat"),
    (r"\b(sk|pk)-[A-Za-z0-9]{16,}", "khoa dang sk-/pk-"),
    (r"\bAKIA[0-9A-Z]{12,}", "khoa AWS"),
    (r"\bgh[pousr]_[A-Za-z0-9]{20,}", "token GitHub"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "khoa rieng"),
]


def cong_bi_mat(goc):
    """Hinh dang bi mat trong file dang theo doi va trong lich su git."""
    ra, thay = [], []
    DUOI = (".py", ".js", ".ts", ".md", ".txt", ".json", ".yml", ".yaml",
            ".env", ".sh", ".cfg", ".ini", ".toml")
    ma, out = git(goc, "ls-files")
    tep = [os.path.join(goc, d.strip()) for d in out.splitlines() if d.strip()] \
        if ma == 0 else []
    nguon = "git ls-files"
    if not tep:
        # Kho chua commit gi thi ls-files tra ve RONG. Lan chay dau tien cua
        # file nay in "khong thay bi mat trong 0 file" va thoat 0 — tuc la bao
        # xanh cho mot phep soi KHONG SOI GI. "0 loi" va "0 thu duoc kiem"
        # trong giong het nhau; do la cho ho loi nay song.
        tep = list(moi_file(goc, DUOI))
        nguon = "quet thu muc (kho chua commit gi)"
    for f in tep:
        if not os.path.isfile(f):
            continue
        if os.path.basename(f) in ("cong.py", "khoi-tao.py"):
            continue          # chinh bo cong chua cac MAU nay
        t = doc(f)
        for mau, ten in HINH_DANG_BI_MAT:
            for m in re.finditer(mau, t):
                d = t[:m.start()].count("\n") + 1
                thay.append("%s:%d  %s" % (ngan(goc, f), d, ten))

    if thay:
        for x in sorted(set(thay))[:10]:
            ra.append(("HONG", x))
        if len(set(thay)) > 10:
            ra.append(("   ", "... va %d cho nua" % (len(set(thay)) - 10)))
        ra.append(("   ", "Chi in TEN va CHO, khong in gia tri."))
        ra.append(("   ", "Xoa dong di KHONG go duoc no ra khoi lich su git."))
        return 1, ra
    if not tep:
        ra.append(("HONG", "Khong soi duoc file nao — phep kiem nay dang vo dung"))
        ra.append(("   ", "'0 bi mat' va '0 file duoc kiem' trong giong het nhau."))
        return 1, ra
    ra.append(("ok", "Khong thay hinh dang bi mat trong %d file (%s)"
               % (len(tep), nguon)))
    return 0, ra


cong_bi_mat.mo_ta = "Bi mat khong nam trong repo"
cong_bi_mat.chung_minh = "khong co chuoi nao KHOP CAC MAU DA BIET trong file dang theo doi"
cong_bi_mat.khong_chung_minh = "repo khong co bi mat. No tim theo HINH DANG; mot bi mat dat ten la `cau_hinh_3` thi no khong thay. Va no chi nhin file, khong nhin LICH SU git."
cong_bi_mat.pha = lambda g: _pha_them(
    g, ["README.md", "docs/README.md"], '\n\nAPI_KEY = "sk-abcdefghijklmnopqrstuvwxyz"\n')


# ======================================================================= cong 5
def cong_vong_doi(goc):
    """File danh dau da bo con duoc tai lieu dang dung tro toi khong."""
    ra = []
    bo, tep_bo = nap_bo_qua(goc)
    da_bo = {}
    for f in moi_file(goc):
        if bi_bo_qua(ngan(goc, f), bo):
            continue
        # Trang thai phai duoc KHAI BAO, khong phai chi duoc NHAC TOI.
        # Ban dau ham nay tim chu "SUPERSEDED" o bat ky dau trong 800 ky tu dau,
        # va no da bat nham mot cau van DUNG chu do ("still teaches the superseded
        # assumptions"). Do la khop HINH DANG thay vi khop thu can tim — dung ho
        # loi ma ca bo cong nay sinh ra de chan.
        for d in doc(f)[:1200].splitlines():
            m = re.match(r"^\s*(?:>|\*\*|#+)?\s*"
                         r"(?:STATUS|TRANG THAI|TR\u1ea0NG TH\u00c1I|Status)"
                         r"\s*[:\*]*\s*(.+)$", d.strip())
            if not m:
                continue
            gt = m.group(1).upper()
            for tt in ("SUPERSEDED", "DEPRECATED", "ARCHIVED", "DA-THAY-THE", "DA-BO"):
                if tt in gt:
                    da_bo[ngan(goc, f)] = tt
                    break
            if ngan(goc, f) in da_bo:
                break

    if not da_bo:
        ra.append(("--", "Khong file nao KHAI BAO trang thai da bo"))
        ra.append(("  ", "Cach khai bao: mot dong 'STATUS: SUPERSEDED' hoac"))
        ra.append(("  ", "'**Trang thai:** DEPRECATED' o dau file."))
        return 0, ra

    hong = []
    for f in moi_file(goc):
        n = ngan(goc, f)
        if n in da_bo or bi_bo_qua(n, bo):
            continue
        noi = doc(f)
        for cu_dp in da_bo:
            # Khop DUONG DAN, khong khop ten file. Ban dau ham nay khop
            # basename, nen mot dong viet khuon `work/<ID>-<slug>/BRIEF.md`
            # trong CLAUDE.md bi tinh la tro toi MOI file ten BRIEF.md.
            if cu_dp in noi.replace("\\", "/"):
                hong.append("%s  van tro toi  %s (%s)" % (n, cu_dp, da_bo[cu_dp]))

    ra.append(("ok", "%d file tu danh dau la da bo" % len(da_bo)))
    for x in sorted(set(hong)):
        ra.append(("HONG", x))
    if hong:
        ra.append(("   ", "Kien truc cu va kien truc moi dang cung ton tai."))
        return 1, ra
    return 0, ra


cong_vong_doi.mo_ta = "Cai da bo thi khong ai con tro toi"
cong_vong_doi.chung_minh = "khong tai lieu dang dung nao tro toi mot file da tu danh dau la bo"
cong_vong_doi.khong_chung_minh = "moi thu da cu deu duoc danh dau. File cu ma khong ai danh dau thi no khong thay."
cong_vong_doi.pha = lambda g: _pha_vong_doi(g)


# ======================================================================= cong 6
def cong_phu_thuoc(goc):
    """Cac URL ngoai ma du an dua vao co con song khong. Can mang."""
    import urllib.request
    ra = []
    f = tim_tep(goc, TEP_PHU_THUOC, "docs/" + TEP_PHU_THUOC)
    if not f:
        ra.append(("--", "Khong co %s — bo qua" % TEP_PHU_THUOC))
        ra.append(("  ", "Thu du an dua vao ma khong cong nao nhin toi thi hong"))
        ra.append(("  ", "IM LANG: moi cong trong nha van xanh het."))
        return 0, ra

    hong = 0
    for d in doc(f).splitlines():
        d = d.strip()
        if not d or d.startswith("#"):
            continue
        phan = re.split(r"\s{2,}|\t", d, 1)
        url = phan[0].strip()
        vai = phan[1].strip() if len(phan) > 1 else ""
        try:
            yc = urllib.request.Request(url, method="HEAD",
                                        headers={"User-Agent": "kit-cong"})
            ma = urllib.request.urlopen(yc, timeout=15).status
            ok = 200 <= ma < 400
        except Exception as e:
            ma, ok = type(e).__name__, False
        ra.append(("ok" if ok else "HONG", "%-58s %s" % (url[:58], vai[:40])))
        if not ok:
            ra.append(("   ", "-> %s" % ma))
            hong += 1
    return (1 if hong else 0), ra


cong_phu_thuoc.mo_ta = "Phu thuoc ngoai con song"
cong_phu_thuoc.can_mang = True
cong_phu_thuoc.chung_minh = "cac URL da KHAI BAO deu tra loi"
cong_phu_thuoc.khong_chung_minh = "noi dung sau URL do con dung. Va no chi nhin nhung URL ban da khai bao."
cong_phu_thuoc.pha = lambda g: _pha_them(
    g, [TEP_PHU_THUOC, "docs/" + TEP_PHU_THUOC],
    "\nhttps://khong-he-ton-tai-9k2x.example  phu thuoc gieo de thu cong\n")


# ================================================================ cach pha chung
def _pha_xoa(goc, ung_vien):
    for t in ung_vien:
        p = os.path.join(goc, t)
        if os.path.exists(p):
            os.remove(p)
            return
    raise AssertionError("khong tim thay file de xoa: %s" % ung_vien)


def _pha_them(goc, ung_vien, them):
    for t in ung_vien:
        p = os.path.join(goc, t)
        if os.path.exists(p):
            with io.open(p, "a", encoding="utf-8", newline="") as h:
                h.write(them)
            return
    p = os.path.join(goc, ung_vien[0])
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    with io.open(p, "a", encoding="utf-8", newline="") as h:
        h.write(them)


def _pha_vong_doi(goc):
    """Tao mot file da bo, va mot file dang dung tro toi no."""
    d = os.path.join(goc, "docs")
    os.makedirs(d, exist_ok=True)
    io.open(os.path.join(d, "kien-truc-cu-9k2x.md"), "w",
            encoding="utf-8", newline="").write(
        "# Kien truc cu\n\nSTATUS: SUPERSEDED\n")
    _pha_them(goc, ["docs/STATE.md", "STATE.md"],
              "\n\nXem them docs/kien-truc-cu-9k2x.md de ro.\n")


# ======================================================================= cong 7
# Tam trang thai du an. Danh sach nay la NOI DUY NHAT dinh nghia chung — mau
# trong khoi-tao.py chi nhac lai. Neu tach thanh hai ban thi som muon hai ban
# lech nhau, va do la ho loi so 5.
TRANG_THAI_DU_AN = ("DANG TIM HIEU", "DANG DUNG", "DANG KIEM", "CHO PHAT HANH",
                    "DANG CHAY THAT", "DANG GIU", "TAM DUNG", "DA DONG")


def cong_trang_thai_ten(goc):
    """File trang thai co mot TRANG THAI GOI TEN DUOC khong."""
    ra = []
    f = tim_tep(goc, "STATE.md", "docs/STATE.md", "TRANG-THAI.md", "CURRENT.md")
    if not f:
        ra.append(("--", "Khong co file trang thai — cong 1 da noi roi"))
        return 0, ra

    t = doc(f)
    # Dung [ \t] chu KHONG dung \s sau tu khoa. `\s` khop CA XUONG DONG, nen
    # ban dau mau nay nuot tu tieu de "# Trang thai" o dong 1, qua hai dong
    # trong, roi bat lay dong 3 lam gia tri. Cong bao HONG tren mot file hoan
    # toan dung. Mot ky tu sai trong mau, va phep kiem noi ve mot dong khac
    # voi dong no tuong minh dang doc.
    m = re.search(r"(?mi)^[ \t]*(?:>|\*\*|#+)?[ \t]*TRANG THAI[ \t]*[:\*]*[ \t]*(.+)$", t)
    if not m:
        ra.append(("HONG", "%s khong khai bao TRANG THAI" % ngan(goc, f)))
        ra.append(("   ", "Van xuoi noi 'dang o dau' thi nguoi doc ky hieu duoc,"))
        ra.append(("   ", "nhung khong ai kiem duoc, va may thi khong doc duoc."))
        ra.append(("   ", "Them mot dong:  TRANG THAI: <mot trong %d chu>"
                   % len(TRANG_THAI_DU_AN)))
        return 1, ra

    gt = m.group(1).strip().strip("*").strip().upper()
    gt = re.sub(r"[^A-Z ]", " ", gt).strip()
    gt = re.sub(r"\s+", " ", gt)
    khop = [x for x in TRANG_THAI_DU_AN if gt.startswith(x)]
    if not khop:
        ra.append(("HONG", "TRANG THAI = %r khong nam trong danh sach" % gt[:40]))
        ra.append(("   ", "Chon mot: %s" % " | ".join(TRANG_THAI_DU_AN)))
        ra.append(("   ", "Du an cua ban can chu khac thi doi DANH SACH, dung"))
        ra.append(("   ", "viet mot chu khong ai khai bao."))
        return 1, ra

    ra.append(("ok", "TRANG THAI: %s" % khop[0]))

    if not re.search(r"(?mi)^[ \t]*THOAT KHI[ \t]*:", t):
        ra.append(("HONG", "Co TRANG THAI nhung khong co THOAT KHI"))
        ra.append(("   ", "Giai doan khong co dieu kien thoat thi no khong ket thuc."))
        ra.append(("   ", "Tick het task KHONG phai xong giai doan."))
        return 1, ra
    ra.append(("ok", "Co dong THOAT KHI"))
    return 0, ra


cong_trang_thai_ten.mo_ta = "Trang thai du an goi ten duoc"
cong_trang_thai_ten.chung_minh = "co mot TRANG THAI thuoc danh sach da khai bao, va co mot dong THOAT KHI"
cong_trang_thai_ten.khong_chung_minh = "trang thai do DUNG, hay dieu kien thoat kia DO DUOC. May doc duoc chu, khong doc duoc su that."
cong_trang_thai_ten.pha = lambda g: _pha_trang_thai(g)


def _pha_trang_thai(goc):
    """Doi TRANG THAI sang mot chu khong co trong danh sach."""
    for ten in ("STATE.md", "docs/STATE.md"):
        p = os.path.join(goc, ten)
        if os.path.exists(p):
            t = io.open(p, encoding="utf-8").read()
            if re.search(r"(?mi)^[ \t]*TRANG THAI[ \t]*:", t):
                t = re.sub(r"(?mi)^([ \t]*TRANG THAI[ \t]*:).*$",
                           r"\1 DANG LAM GI DO 9K2X", t, count=1)
            else:
                t = "TRANG THAI: DANG LAM GI DO 9K2X" + NL + NL + t
            io.open(p, "w", encoding="utf-8", newline="").write(t)
            return
    raise AssertionError("khong tim thay file trang thai de pha")


# ======================================================================= cong 8
# Y DINH khong phai CO BAO. Danh sach nay la nhung chu bao hieu mot o co bao
# moi chi la du dinh theo doi, chua phai thu nhin thay duoc.
CO_BAO_RONG = ("de y", "theo doi", "chu y", "canh chung", "luu y", "quan sat",
               "xem xet", "watch", "monitor", "keep an eye")


def cong_rui_ro(goc):
    """So rui ro: rui ro DANG MO phai co co bao NHIN THAY DUOC."""
    ra = []
    f = tim_tep(goc, "RUI-RO.md", "docs/RUI-RO.md", "RISKS.md", "docs/RISKS.md")
    if not f:
        ra.append(("--", "Khong co so rui ro — bo qua cong nay"))
        ra.append(("  ", "Neu du an co rui ro that, do la cho no nen duoc viet"))
        ra.append(("  ", "ra, KEM co bao. Tao san bang:"))
        ra.append(("  ", "  python kit/khoi-tao.py . --day-du"))
        return 0, ra

    t = doc(f)
    dong = [d for d in t.splitlines() if d.strip().startswith("|")]
    hang = [d for d in dong if not re.match(r"^\|[\s:|-]+\|$", d.strip())][1:]
    if not hang:
        ra.append(("HONG", "So rui ro co mat nhung KHONG CO rui ro nao"))
        ra.append(("   ", "Mot so rong doc y het mot so chua bao gio duoc mo."))
        return 1, ra

    xau = []
    for h in hang:
        o = [x.strip() for x in h.strip().strip("|").split("|")]
        if len(o) < 5:
            continue
        ten, co_bao, tt = o[0], o[3], o[4]
        if not ten or ten.startswith("<"):
            continue
        if "DANG MO" not in tt.upper() and "OPEN" not in tt.upper():
            continue          # da xay ra hoac het rui ro thi khong doi co bao
        # Boc ca dau nhan manh cua markdown. Ban dau khong boc, nen mot o ghi
        # "**chua co co bao**" khong khop duoc voi phep so — cong bao xanh cho
        # dung cai o tu khai la trong.
        cb = khong_dau(co_bao.strip().strip("<>").strip("*` ").strip())
        if not cb or cb in ("-", "--", "chua co", "khong"):
            xau.append((ten[:46], "o Co bao de trong"))
            continue
        if any(x in cb for x in CO_BAO_RONG):
            xau.append((ten[:46], "co bao chi la mot Y DINH: %r" % co_bao[:34]))
        elif cb.startswith("chua co"):
            xau.append((ten[:46], "tu khai la CHUA CO co bao"))

    ra.append(("ok", "So rui ro: %s, %d rui ro" % (ngan(goc, f), len(hang))))
    for ten, vs in xau:
        ra.append(("HONG", "%s  ->  %s" % (ten, vs)))
    if xau:
        ra.append(("   ", "Co bao khong phai dieu ban DINH LAM. La thu ban se"))
        ra.append(("   ", "NHIN THAY, ke ca hom do ban khong nghi toi no."))
        return 1, ra
    return 0, ra


cong_rui_ro.mo_ta = "Rui ro dang mo co co bao"
cong_rui_ro.chung_minh = "moi rui ro DANG MO deu co o Co bao, va o do khong phai mot y dinh chung chung"
cong_rui_ro.khong_chung_minh = "co bao do SE KEU. May doc duoc chu, khong biet cai co bao ay co ai nhin khong."
cong_rui_ro.pha = lambda g: _pha_rui_ro(g)


def _pha_rui_ro(goc):
    """Gieo mot rui ro DANG MO voi co bao chi la mot y dinh."""
    hang = ("| rui ro gieo de thu cong | hong nang | lam gi do |"
            " de y xem | DANG MO |" + NL)
    for ten in ("RUI-RO.md", "docs/RUI-RO.md"):
        p = os.path.join(goc, ten)
        if os.path.exists(p):
            with io.open(p, "a", encoding="utf-8", newline="") as h:
                h.write(hang)
            return
    io.open(os.path.join(goc, "RUI-RO.md"), "w",
            encoding="utf-8", newline="").write(
        "# So rui ro" + NL + NL
        + "| Rui ro | Hong co nao | Lam gi truoc | Co bao | Trang thai |" + NL
        + "|---|---|---|---|---|" + NL
        + "| rui ro lanh | hong nhe | lam gi do |"
          " phep kiem goi URL moi lan chay | DANG MO |" + NL
        + hang)


# ======================================================================= cong 9
def _dau_vet_cho_dua(goc):
    """Bang chung rang du an NAY that su co cho dua ben ngoai.

    Khong doan. Chi lay thu nhin thay duoc:
      - remote git tro ra ngoai;
      - dong da khai bao trong phu-thuoc-ngoai.txt;
      - mien ngoai xuat hien trong file dang theo doi.
    """
    dau = set()

    ma, out = git(goc, "remote", "-v")
    if ma == 0:
        for d in out.splitlines():
            m = re.search(r"https?://([a-zA-Z0-9.\-]+)|@([a-zA-Z0-9.\-]+):", d)
            if m:
                dau.add((m.group(1) or m.group(2)).lower())

    f = tim_tep(goc, TEP_PHU_THUOC, "docs/" + TEP_PHU_THUOC)
    if f:
        for d in doc(f).splitlines():
            d = d.strip()
            if d and not d.startswith("#"):
                m = re.match(r"https?://([a-zA-Z0-9.\-]+)", d)
                if m:
                    dau.add(m.group(1).lower())

    ma, out = git(goc, "ls-files")
    tep = [os.path.join(goc, d.strip()) for d in out.splitlines() if d.strip()] \
        if ma == 0 else []
    if not tep:
        # Khong co git, hoac kho chua commit gi -> quet thu muc.
        #
        # Quan trong hon: BO TU KIEM CHEP KHO MA BO .git DI, nen trong ban chep
        # `git ls-files` khong chay duoc. Khong co nhanh nay thi cong nhin thay
        # mot thu khac han luc THU so voi luc THAT — va phep thu chung minh it
        # hon han no to ra. Cong bi mat da co dung nhanh nay tu truoc.
        tep = list(moi_file(goc, (".md", ".txt", ".py", ".js", ".ts", ".json",
                                  ".html", ".yml", ".yaml", ".toml", ".cfg")))
    for p in tep[:400]:
        if not os.path.isfile(p):
            continue
        # Bo qua chinh bo cong: file nay chua cac URL VI DU dung de pha trong
        # --tu-kiem. Quet ca no thi cong luon "thay dau vet", ke ca tren mot
        # du an trang. Cong bi mat da phai ne dung cho nay tu truoc.
        if os.path.basename(p) in ("cong.py", "khoi-tao.py"):
            continue
        # Va bo qua file khai bao phu thuoc: no da duoc doc rieng o tren,
        # dung cach — ton trong dau '#'.
        if os.path.basename(p) == TEP_PHU_THUOC:
            continue
        for dong in doc(p).splitlines():
            # BO QUA DONG DA COMMENT. Mot URL vi du nam sau dau '#' khong phai
            # mot cho dua. Ban dau vong nay doc thang ca file, va mot dong mau
            # trong phu-thuoc-ngoai.txt du de lam cong bao HONG tren mot du an
            # vua khoi tao — cong keu nham ngay ngay dau thi bi tat di.
            if dong.lstrip().startswith(("#", "//")):
                continue
            for m in re.finditer(r"https?://([a-zA-Z0-9.\-]+)", dong):
                g = m.group(1).lower()
                if not g.startswith(("127.0.0.1", "localhost", "example.")):
                    dau.add(g)
    return dau


def cong_cho_dua(goc):
    """Co cho dua ben ngoai ma khong ai ghi ra khong."""
    ra = []
    f = tim_tep(goc, "CHO-DUA.md", "docs/CHO-DUA.md", "CONG-CU.md",
                "docs/CONG-CU.md", "TOOLS.md", "docs/TOOLS.md")

    dau = _dau_vet_cho_dua(goc)

    if not dau:
        ra.append(("--", "Khong thay dau vet cho dua ben ngoai nao"))
        ra.append(("  ", "Du an chua noi ra ngoai, hoac chua commit gi. Cong nay"))
        ra.append(("  ", "chua co gi de doi chieu — do KHONG phai 'da sach'."))
        return 0, ra

    if not f:
        ra.append(("HONG", "Thay %d cho dua ben ngoai, khong co file nao ghi chung"
                   % len(dau)))
        for x in sorted(dau)[:8]:
            ra.append(("   ", "   %s" % x))
        ra.append(("   ", "Thu chay tot thi thoi duoc nhin thay. Cai khong ai viet"))
        ra.append(("   ", "ra thi khong phep kiem nao nhin toi — va khi no chet,"))
        ra.append(("   ", "MOI CONG TRONG NHA VAN XANH HET."))
        return 1, ra

    t = doc(f)
    dong = [d for d in t.splitlines() if d.strip().startswith("|")]
    hang = [d for d in dong if not re.match(r"^\|[\s:|-]+\|$", d.strip())][1:]
    that = [h for h in hang
            if h.strip().strip("|").split("|")[0].strip()
            and not h.strip().strip("|").split("|")[0].strip().startswith("<")]

    if not that:
        ra.append(("HONG", "Thay %d cho dua ben ngoai, nhung %s chua ghi cai nao"
                   % (len(dau), ngan(goc, f))))
        for x in sorted(dau)[:8]:
            ra.append(("   ", "   %s" % x))
        ra.append(("   ", "May chi dua duoc UNG VIEN — no khong phan biet duoc"))
        ra.append(("   ", "'thu toi dua vao' voi 'thu toi tinh co nhac ten'."))
        ra.append(("   ", "Doc tung cai roi ghi, dung chep thang danh sach nay."))
        return 1, ra

    ra.append(("ok", "%s: %d cho dua da ghi | thay %d dau vet"
               % (ngan(goc, f), len(that), len(dau))))
    return 0, ra


cong_cho_dua.mo_ta = "Cho dua duoc ghi ra"
cong_cho_dua.chung_minh = "khi co dau vet cho dua ben ngoai, co mot danh sach da ghi it nhat mot dong"
cong_cho_dua.khong_chung_minh = "danh sach do DU, hay DUNG. Thu ban quen thi phep kiem nay cung khong biet la ban quen."
cong_cho_dua.pha = lambda g: _pha_cho_dua(g)


def _pha_cho_dua(goc):
    """Gieo dung dieu kien cong nay sinh ra de bat: CO dau vet, KHONG ai ghi.

    Ban dau phep pha nay chi xoa cac hang da ghi. Tren mot du an chua co dau
    vet cho dua nao, cong tra 0 ca truoc lan sau — va bo tu kiem bao TRUOT,
    doc y het "cong mu". That ra la phep pha chua tao duoc dieu kien de cong
    co gi ma noi. Nen no phai lam CA HAI: tao mot dau vet, va lam rong danh sach.
    """
    _pha_them(goc, ["README.md", "docs/README.md"],
              NL + NL + "Du an nay nap thu vien tu https://cdn.vi-du-9k2x.net"
              + NL)
    for ten in ("CHO-DUA.md", "docs/CHO-DUA.md", "CONG-CU.md", "docs/CONG-CU.md"):
        p = os.path.join(goc, ten)
        if os.path.exists(p):
            giu = []
            for d in doc(p).splitlines():
                s = d.strip()
                if (s.startswith("|") and not re.match(r"^\|[\s:|-]+\|$", s)
                        and not s.lower().startswith("| cho dua")):
                    continue
                giu.append(d)
            io.open(p, "w", encoding="utf-8", newline="").write(NL.join(giu))
            return
    raise AssertionError("khong tim thay file cho dua de pha")


# ===================================================================== cong 10
def cong_ban_do(goc):
    """Ban do he thong: duong dan no ke ten phai con ton tai.

    Cong nay CHI soi trong chinh file ban do, khong soi ca kho. Do la chu y:
    phep soi duong dan tren toan kho da duoc do, va no bao 85 cho tren mot kho
    khoe manh (xem bai thuc hanh M21). Mot cong keu nham se bi tat di. Gioi han
    vao sau dong ban do thi ti le keu nham gan bang khong — va day dung la sau
    dong nguoi ta se tin nhat khi quyet dinh doi cai gi.
    """
    ra = []
    f = tim_tep(goc, "BAN-DO.md", "docs/BAN-DO.md", "ARCHITECTURE.md",
                "docs/ARCHITECTURE.md")
    if not f:
        ra.append(("--", "Khong co ban do he thong — bo qua cong nay"))
        ra.append(("  ", "Can no khi lan dau ban khong chac doi mot cho thi dau"))
        ra.append(("  ", "dong theo. Tao san bang:"))
        ra.append(("  ", "  python kit/khoi-tao.py . --day-du"))
        return 0, ra

    t = doc(f)

    # Chia theo tieu de '## ', roi xem MUC nao da duoc tra loi. Mau cua kit de
    # cho trong bang mot dong bat dau bang '<'.
    muc = {}
    ten, than = None, []
    for d in t.splitlines():
        if d.startswith("## "):
            if ten is not None:
                muc[ten] = NL.join(than).strip()
            ten, than = d[3:].strip(), []
        elif ten is not None:
            than.append(d)
    if ten is not None:
        muc[ten] = NL.join(than).strip()

    da_tra_loi = [k for k, v in muc.items() if v and not v.startswith("<")]

    if muc and not da_tra_loi:
        # KHONG bao hong. Mot du an vua khoi tao thi ban do dung ra la con
        # trong — bao do o day la keu nham ngay ngay dau, va mot cong keu nham
        # ngay dau thi bi tat di. Do la ho loi da ghi trong lo B.
        ra.append(("--", "Ban do chua dien gi — chua co gi de kiem"))
        ra.append(("  ", "Dien khi lan dau ban khong chac doi mot cho thi dau"))
        ra.append(("  ", "dong theo. Truoc do no dung ra la con trong."))
        return 0, ra

    # Da bat dau dien roi thi cau dat nhat khong duoc bo trong.
    for k, v in muc.items():
        if khong_dau(k).find("du lieu") >= 0 and (not v or v.startswith("<")):
            ra.append(("HONG", "Ban do da dien, nhung muc '%s' con trong" % k))
            ra.append(("   ", "Day la dong dat nhat: code sai thi sua lai, du lieu"))
            ra.append(("   ", "sai thi khong lui duoc."))
            return 1, ra

    goc_thu_muc = set(n for n in os.listdir(goc)
                      if os.path.isdir(os.path.join(goc, n)))
    thieu, soi = [], 0
    # CHI soi trong nhung muc DA DUOC TRA LOI. Mau cua kit co duong dan vi du
    # nam trong phan con trong ('<...>') — quet ca chung thi cong bao hong ngay
    # khi nguoi ta vua dien MOT muc. Do dung la kieu keu nham da ghi o lo B:
    # cong doc dong vi du roi bao loi.
    than_da_dien = NL.join(v for k, v in muc.items() if k in da_tra_loi)
    for m in re.finditer(r"`([A-Za-z0-9_][A-Za-z0-9_.\-]{0,40}"
                         r"(?:/[A-Za-z0-9_.\-]{1,40}){0,4}/?)`", than_da_dien):
        p = m.group(1).rstrip("/")
        # Luat hep nhat ma van bat duoc ca lan hong that: PHAI co dau "/",
        # va doan dau phai la mot thu muc CO THAT o goc du an.
        #
        # Ban dau cong nay nhan ca ten file tran (`build.py`). Chay tren chinh
        # kho khoa hoc thi no bao 6 cho — trong do co `build.py` (van xuoi, y
        # la `site/build.py`) va `ai.thelong.tech` (mot TEN MIEN). Keu nham
        # ngay lan chay dau. Do la lan thu hai trong cung mot lo.
        if "..." in p or "://" in p or "/" not in p:
            continue
        if p.split("/")[0] not in goc_thu_muc:
            continue
        soi += 1
        if os.path.exists(os.path.join(goc, p)):
            continue
        if glob.glob(os.path.join(goc, p) + "*"):
            continue
        thieu.append(p)

    if thieu:
        ra.append(("HONG", "Ban do tro toi %d cho khong con ton tai" % len(thieu)))
        for x in sorted(set(thieu))[:8]:
            ra.append(("   ", "   %s" % x))
        ra.append(("   ", "Mot ban do sai te hon khong co ban do: khong co thi ban"))
        ra.append(("   ", "di hoi, co ban do sai thi ban khong hoi ai ca."))
        return 1, ra

    ra.append(("ok", "%s: %d duong dan, deu con that"
               % (ngan(goc, f), soi)))
    return 0, ra


cong_ban_do.mo_ta = "Ban do he thong con dung"
cong_ban_do.chung_minh = "moi duong dan VIET TRONG BAN DO deu con ton tai, va muc du lieu khong bo trong"
cong_ban_do.khong_chung_minh = "ban do do DUNG, hay DU, hay CO TON TAI. Ban do trong thi cong nay im — no chi bat ban do DANG NOI DOI, khong bat ban do vang mat."


def _pha_ban_do(goc):
    """Gieo mot dong ban do tro toi mot cho khong ton tai.

    Phep pha nay phai lam HAI viec, khong phai mot. Tren mot ban do chua dien
    gi, cong im lang (dung vay) — nen neu chi them mot duong dan hong thi cong
    se do vi mot LY DO KHAC: "da dien nhung bo trong muc du lieu". Bo tu kiem
    van bao DAT, nhung no dang thu MOT THU KHAC voi thu no khai. Dung ho loi da
    ghi o _pha_gia_dinh, va lan nay bi bat bang cach GOI THANG cong ra doc
    thong bao, chu khong chi nhin ma thoat.
    """
    xau = (NL + "## Phan khong co that" + NL + NL
           + "Nam o `kit/khong-he-co-9k2x/loi.md`, goi sang phan ban hang." + NL)
    dien = "Trong `kit/cong.py` — dong nay chi de phep thu co cho bam."
    for ten in ("BAN-DO.md", "docs/BAN-DO.md"):
        duong = os.path.join(goc, ten)
        if not os.path.exists(duong):
            continue
        ra, trong_muc = [], False
        for d in doc(duong).splitlines():
            if d.startswith("## "):
                trong_muc = "du lieu" in khong_dau(d)
                ra.append(d)
                if trong_muc:
                    ra.append("")
                    ra.append(dien)
                continue
            if trong_muc:
                # bo nguyen phan than cu cua muc do, ke ca cho trong '<...>'
                continue
            ra.append(d)
        io.open(duong, "w", encoding="utf-8", newline="").write(
            NL.join(ra) + NL + xau)
        return
    io.open(os.path.join(goc, "BAN-DO.md"), "w", encoding="utf-8",
            newline="").write(
        "# Ban do he thong" + NL + NL
        + "## Du lieu nam o dau" + NL + NL + dien + NL + xau)


cong_ban_do.pha = _pha_ban_do


# ==================================================================== danh sach
CAC_CONG = [
    cong_trang_thai,
    cong_gia_dinh,
    cong_lenh_tai_lieu,
    cong_bi_mat,
    cong_vong_doi,
    cong_trang_thai_ten,
    cong_rui_ro,
    cong_cho_dua,
    cong_ban_do,
    cong_phu_thuoc,
]


# ======================================================================== chay
def chay_het(goc, co_mang=False, im=False):
    tong = 0
    for c in CAC_CONG:
        if getattr(c, "can_mang", False) and not co_mang:
            if not im:
                print()
                print("  [ bo qua ] %s  (can mang: them --ngoai)" % c.mo_ta)
            continue
        ma, dong = c(goc)
        tong = max(tong, ma)
        if im:
            continue
        print()
        print("  [ %s ] %s" % ("HONG" if ma else " ok ", c.mo_ta))
        for nhan, noi in dong:
            print("     %-5s %s" % (nhan, noi))
        print("     %-5s chung minh:     %s" % ("", c.chung_minh))
        print("     %-5s KHONG chung minh: %s" % ("", c.khong_chung_minh))
    return tong


def main():
    co_mang = "--ngoai" in sys.argv
    goc = GOC
    print()
    print("  " + "=" * 68)
    print("  cong.py %s — kiem mot du an chay bang AI" % PHIEN_BAN)
    print("  Thu muc: %s" % goc)
    print("  " + "=" * 68)

    ma = chay_het(goc, co_mang)

    print()
    print("  " + "-" * 68)
    if ma:
        print("  CO CONG BAO HONG. Doc phan 'chung minh' cua cong do truoc khi sua.")
    else:
        print("  Moi cong da chay deu khong bao hong.")
        print("  Day KHONG phai 'du an nay dung'. Moi cong chi nhin dung mot thu,")
        print("  va tung cong da tu khai no khong nhin thay gi.")
    print()
    print("  Muon biet cac cong nay co THAT SU truot duoc khong:")
    print("      python %s --tu-kiem" % os.path.basename(__file__))
    print("  " + "-" * 68)
    return ma


# ===================================================================== tu kiem
def tu_kiem():
    """Chep du an sang thu muc tam, CO Y pha tung thu, doi ket qua phai doi.

    Du an that khong bao gio bi sua.
    """
    co_mang = "--ngoai" in sys.argv
    print()
    print("  " + "=" * 68)
    print("  tu-kiem — moi cong co THAT SU truot duoc khong?")
    print("  Du an that khong bi dong toi. Moi phep pha dien ra tren ban chep.")
    print("  " + "=" * 68)

    tam = tempfile.mkdtemp(prefix="kit-tu-kiem-")
    sach = os.path.join(tam, "sach")
    shutil.copytree(GOC, sach,
                    ignore=shutil.ignore_patterns(*BO_QUA_THU_MUC, "*.pyc"))

    dat = truot = bo = khong_do = 0
    try:
        for so, c in enumerate(CAC_CONG, 1):
            if getattr(c, "can_mang", False) and not co_mang:
                print()
                print("  BO QUA  %-34s (can mang: them --ngoai)" % c.mo_ta)
                bo += 1
                continue

            ma_sach, _ = c(sach)

            # Nen da do thi PHEP THU NAY KHONG DO DUOC GI. Truoc day truong hop
            # do bi in ra la "TRUOT", doc y het "cong nay mu" — trong khi su
            # that la "toi khong phan biet duoc". Do dung kieu cau noi it hon
            # no nghe, va la thu ca bo cong nay sinh ra de chan.
            if ma_sach != 0:
                print()
                print("  KHONG DO DUOC  %-24s nen da do san (ma thoat %d)"
                      % (c.mo_ta, ma_sach))
                print("          >> Khong phai cong mu. La phep thu nay khong")
                print("          >> phan biet duoc, vi ca truoc va sau deu do.")
                print("          >> Sua cho dang do truoc, roi chay lai.")
                khong_do += 1
                continue

            pha = os.path.join(tam, "pha-%02d" % so)
            shutil.copytree(sach, pha)
            try:
                c.pha(pha)
            except Exception as e:
                print()
                print("  LOI     %-34s khong gieo duoc loi: %s" % (c.mo_ta, e))
                truot += 1
                continue
            ma_pha, _ = c(pha)

            khac = ma_sach != ma_pha
            print()
            print("  %-7s %-34s ma thoat: %d -> %d"
                  % ("DAT" if khac else "TRUOT", c.mo_ta, ma_sach, ma_pha))
            if khac:
                dat += 1
            else:
                truot += 1
                print("          >> CONG NAY KHONG NHIN THAY CHUYEN DO.")
                print("          >> Truoc khi ket luan cong hong, hoi cau nay TRUOC:")
                print("          >>   phep PHA cua toi co pha dung cho khong?")
                print("          >> Du an sinh ra file nay chay phep kiem tuong tu va")
                print("          >> co 3 cong 'khong bat duoc gi' — ca ba deu la PHEP")
                print("          >> THU viet sai, khong phai cong mu.")
    finally:
        shutil.rmtree(tam, ignore_errors=True)

    print()
    print("  " + "-" * 68)
    print("  %d cong chung minh duoc la truot duoc | %d khong | %d bo qua"
          % (dat, truot, bo))
    if khong_do:
        print("  %d cong KHONG DO DUOC vi nen dang do — khac han voi 'mu'."
              % khong_do)
    print()
    print("  Cai nay KHONG chung minh cac cong bat duoc moi kieu hong.")
    print("  No chi chung minh moi cong bat duoc DUNG MOT kieu da biet.")
    print("  " + "-" * 68)
    return 1 if truot else 0     # 'khong do duoc' khong tinh la truot


if __name__ == "__main__":
    sys.exit(tu_kiem() if "--tu-kiem" in sys.argv else main())
