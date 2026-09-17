# -*- coding: utf-8 -*-
"""cong.py — bo cong kiem cho mot du an chay bang AI.

    python kit/cong.py              chay het cac cong
    python kit/cong.py --ngoai      chay them cong goi ra Internet
    python kit/cong.py --ha-tang    chay them cong GOI LENH kiem cong cu
    python kit/cong.py --kho        CHI chay cac cong nhin kho nhu no dang la
                                    — dung duoc tren mot kho chua nhan bo kit
    python kit/cong.py --tu-kiem    CHUNG MINH tung cong co the truot
    python kit/cong.py --tiep       "tiep" nghia la gi: dang o dau, sap lam gi

MOT FILE, KHONG CAI DAT GI. Chep file nay vao du an cua ban la chay duoc.

VI SAO NO TON TAI
-----------------
Mot bo tieu chuan viet ra giay duoc thi hanh boi chinh nguoi bi rang buoc. Do
khong phai mot ranh gioi. Du an sinh ra file nay da do duoc dieu do: no GOI TEN
co che loi cua chinh no bang chu, roi van lap lai co che do 17 lan — sau lan
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
PHIEN_BAN = "1.20.2"

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
    """Tra ve (tien to duong dan, tien to DICH cua lenh, duong dan file khai bao).

    Dong bat dau bang "-> " la mien tru DICH: no tha mot lenh tro toi cho do,
    va KHONG tha ca file chua lenh ay. Vi sao can phan biet: mot file tai lieu
    phuc vu hai kho se co dung mot lenh sai o kho nay va dung o kho kia. Mien
    tru ca file thi cac lenh con lai trong do cung thoi duoc kiem.
    """
    f = os.path.join(goc, TEP_BO_QUA)
    if not os.path.exists(f):
        f2 = os.path.join(goc, "bo-qua.txt")
        if not os.path.exists(f2):
            return [], [], None
        f = f2
    ra, dich = [], []
    for d in doc(f).splitlines():
        d = d.strip()
        if not d or d.startswith("#"):
            continue
        if d.startswith("->"):
            dich.append(d[2:].strip().replace("\\", "/").rstrip("/"))
        else:
            ra.append(d.replace("\\", "/").rstrip("/"))
    return ra, dich, ngan(goc, f)


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


# Thu muc cua CONG CU, khong phai ho so cua du an. tim_tep() do theo TEN FILE,
# nen khong chan thi no di lac vao day: do duoc 2026-09-17 tren kho
# autonomous-ai-binance-futures, hai cong khac nhau cung bat nham —
# .claude/commands/trang-thai.md bi doc nhu file trang thai, va
# .claude/rules/rui-ro.md bi doc nhu so rui ro. Mot nguyen nhan, hai cong.
THU_MUC_CONG_CU = (".claude/", ".github/", ".vscode/", ".cursor/", ".idea/")


def bi_bo_qua_may(duong):
    """Duong dan nay thuoc thu muc cau hinh cong cu, khong phai ho so du an."""
    d = duong.replace("\\", "/")
    if d.startswith("./"):
        d = d[2:]
    return any(d.startswith(x) or ("/" + x) in d
               for x in THU_MUC_CONG_CU)


def tim_tep(goc, *ten):
    """Tra ve duong dan dau tien tim thay trong cac ten duoc dua vao."""
    for t in ten:
        p = os.path.join(goc, t)
        if os.path.exists(p):
            return p
    for f in moi_file(goc):
        if bi_bo_qua_may(ngan(goc, f)):
            continue
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


cong_trang_thai.nhin_kho = True
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
        # Ngay phai lay o COT HAN KIEM, khong phai ngay dau tien tren dong.
        # Mot hang that thuong co ngay o cot khac — "tu dau ra", "do ngay nao" —
        # va lay nham cai do thi cong bao QUA HAN cho mot gia dinh con han.
        # Cot han kiem la cot ap chot, tinh tu phai sang: trang thai la cot cuoi.
        ngay = None
        if len(o) >= 2:
            ngay = re.search(r"(20\d\d)-(\d\d)-(\d\d)", o[-2])
        if ngay is None and len(o) == 1:
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
cong_gia_dinh.chung_minh = "moi gia dinh ghi ra deu co trang thai, va khong cai nao qua han ma van chua kiem (han doc o COT AP CHOT, khong phai ngay dau tien tren dong)"
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
    bo, bo_dich, tep_bo = nap_bo_qua(goc)
    if bo:
        ra.append(("--", "Bo qua %d cho da khai bao trong %s" % (len(bo), tep_bo)))
        for x in bo:
            ra.append(("  ", "   %s" % x))
    if bo_dich:
        ra.append(("--", "Bo qua %d DICH lenh da khai bao trong %s"
                   % (len(bo_dich), tep_bo)))
        for x in bo_dich:
            ra.append(("  ", "   -> %s" % x))
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
            if bi_bo_qua(muc.replace("\\", "/").rstrip("/"), bo_dich):
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


cong_lenh_tai_lieu.nhin_kho = True
cong_lenh_tai_lieu.mo_ta = "Lenh trong tai lieu chay duoc"
cong_lenh_tai_lieu.chung_minh = "file ma lenh tro toi co ton tai"
cong_lenh_tai_lieu.khong_chung_minh = "lenh do CHAY duoc, hay chay ra ket qua dung. No chi kiem su ton tai."
cong_lenh_tai_lieu.pha = lambda g: _pha_them(
    g, ["README.md", "docs/README.md"],
    "\n\nChay thu: `python khong-he-ton-tai-9k2x.py`\n")


# ======================================================================= cong 4
# Nhung gia tri KHONG phai bi mat, do duoc tren hai kho that ngay 2026-09-17.
# Loc theo hinh dang CUA GIA TRI. Khong loai tru theo thu muc: bo qua moi file
# ten test_* thi mot bi mat that nam trong do se im mai mai.
CHU_GIU_CHO = ("placeholder", "your_", "your-", "changeme", "change_me",
               "example", "sample", "dummy", "fake", "test", "xxxx", "todo",
               "redacted", "<", "{", "$")


def _co_ve_that(gia_tri):
    """Gia tri bat duoc co the la mot bi mat that khong.

    Ba loai bi loai, moi loai do duoc tren kho that:
      - trong gia tri co ma: `; ` hay `)` — do la nhan nhac printf hoac mot
        khang dinh phu dinh, khong phai mot gia tri;
      - gia tri la cho giu cho: your_..., {secret}, control-test;
      - gia tri lap mot ky tu — token gia kieu "AAAAAAAAAAAA".
    """
    v = gia_tri.strip()
    if not v or len(v) < 6:
        return False
    if ";" in v or ")" in v or v.startswith(" "):
        return False
    # Mot khoa hau nhu khong bao gio co dau cach. Do 2026-09-17 tren sau kho:
    # o mot ung dung nhat ky, "secret" la mot TRUONG NGHIEP VU va gia tri la
    # van xuoi tieng Viet — bon cho, ca bon deu co dau cach. Hai cho dang
    # thong tin dang nhap that thi khong co cai nao.
    #
    # Danh doi: mot passphrase that co dau cach se bi bo qua. Doi lai, mot cong
    # bat 4/6 nham tren kho that se bi tat, va luc do no bao ve khong cai nao.
    if " " in v:
        return False
    t = v.lower()
    if any(x in t for x in CHU_GIU_CHO):
        return False
    lap = 1
    dai_nhat = 1
    for i in range(1, len(v)):
        lap = lap + 1 if v[i] == v[i - 1] else 1
        dai_nhat = max(dai_nhat, lap)
    return dai_nhat < 8


HINH_DANG_BI_MAT = [
    (r"(?i)\b(password|passwd|secret|token|api[_-]?key|private[_-]?key)\b\s*[:=]\s*['\"](?P<gt>[^'\"]{6,})",
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
                # Mau thu nhat bat theo TEN BIEN, nen no bat ca ma shell
                # lan cho giu cho. Loc theo hinh dang GIA TRI. Bon mau con
                # lai la hinh dang rieng cua khoa that — khong loc.
                if m.re.groupindex.get("gt") and not _co_ve_that(
                        m.group("gt")):
                    continue
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


cong_bi_mat.nhin_kho = True
cong_bi_mat.mo_ta = "Bi mat khong nam trong repo"
cong_bi_mat.chung_minh = "khong co chuoi nao KHOP CAC MAU DA BIET trong file dang theo doi"
cong_bi_mat.khong_chung_minh = "repo khong co bi mat. No tim theo HINH DANG; mot bi mat dat ten la `cau_hinh_3` thi no khong thay. Va no chi nhin file, khong nhin LICH SU git. Va tu 2026-09-17 no BO QUA moi gia tri co dau cach — do la cach duy nhat do duoc de phan biet mot khoa voi mot truong nghiep vu ten `secret` chua van xuoi; mot passphrase that co dau cach se lot qua."
cong_bi_mat.pha = lambda g: _pha_them(
    g, ["README.md", "docs/README.md"], '\n\nAPI_KEY = "sk-abcdefghijklmnopqrstuvwxyz"\n')


# ======================================================================= cong 5
def cong_vong_doi(goc):
    """File danh dau da bo con duoc tai lieu dang dung tro toi khong."""
    ra = []
    bo, bo_dich, tep_bo = nap_bo_qua(goc)
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
        # Cong nay CHI nhin cac dong la URL. File khai bao con mang nhung
        # dang dong khac — "ten-mien ...", "ban-sao ..." — do cong khac lo.
        #
        # Luat nay viet theo LOP chu khong theo tung ca: lan dau them mot dang
        # dong moi, hai cong doc file nay deu goi no nhu mot dia chi web va do
        # ca hai. Sua tung cai mot thi dang dong thu ba lai vap y het.
        if not url.lower().startswith(("http://", "https://")):
            continue
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


cong_cho_dua.nhin_kho = True
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
def soi_duong_dan(goc, than):
    """Duong dan viet trong mot doan van co con tro toi cho co that khong.

    Luat hep nhat ma van bat duoc lan hong that: PHAI co dau "/", va doan dau
    phai la mot thu muc CO THAT o goc du an.

    Ban dau luat nay rong hon, nhan ca ten file tran (`build.py`). Chay tren
    chinh kho sinh ra no thi bao 6 cho — trong do co `build.py` (van xuoi, y la
    `site/build.py`) va `ai.thelong.tech` (mot TEN MIEN). Keu nham ngay lan
    chay dau. Mot cong keu nham se bi nguoi sau tat di, nen luat hep la co y.
    """
    goc_thu_muc = set(n for n in os.listdir(goc)
                      if os.path.isdir(os.path.join(goc, n)))
    thieu, soi = [], 0
    for m in re.finditer(r"`([A-Za-z0-9_][A-Za-z0-9_.\-]{0,40}"
                         r"(?:/[A-Za-z0-9_.\-]{1,40}){0,4}/?)`", than):
        p = m.group(1).rstrip("/")
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
    return soi, thieu


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

    # CHI soi trong nhung muc DA DUOC TRA LOI. Mau cua kit co duong dan vi du
    # nam trong phan con trong ('<...>') — quet ca chung thi cong bao hong ngay
    # khi nguoi ta vua dien MOT muc. Do dung la kieu keu nham da ghi o lo B:
    # cong doc dong vi du roi bao loi.
    than_da_dien = NL.join(v for k, v in muc.items() if k in da_tra_loi)
    soi, thieu = soi_duong_dan(goc, than_da_dien)

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


def khop_ten(v, cac_gia_tri):
    """Mot truong GOI TEN DUOC phai khop BANG mot gia tri, khong phai CHUA no.

    Truoc day ham nay la mot phep tim chuoi con, va "sap xong" bi tinh la
    "xong" vi no chua chu do. Cong im lang cho mot giai doan chua xong. Do la
    kieu hong nguy nhat: khong bao sai, chi bao it hon su that.
    """
    x = " ".join(khong_dau(v).split())
    return x if x in cac_gia_tri else None


# So commit duoc phep chong len nhat ky truoc khi cong nay keu.
#
# Vi sao la mot NGUONG chu khong phai 1: khong phai commit nao cung dang mot
# muc nhat ky — sua chinh ta, doi ten file, cap nhat phu thuoc. Bao do tu
# commit dau tien la keu nham, va cong keu nham thi bi tat di. Con 10 commit
# thi khong con goi la "quen mot lan" duoc nua.
NGUONG_COMMIT_CHONG_NHAT_KY = 10


def cong_nhat_ky(goc):
    """Nhat ky con duoc ghi khong, va no co tro toi cho co that khong.

    Hai kieu hong khac han nhau:
      * nhat ky NOI DOI  — tro toi file boi-canh khong con ton tai
      * nhat ky DUNG LAI — kho van chay tiep ma khong ai ghi them dong nao
    Cai thu hai moi la cai giet du an, va no khong co trieu chung nao khac.
    """
    ra = []
    f = tim_tep(goc, "NHAT-KY.md", "docs/NHAT-KY.md")
    if not f:
        ra.append(("--", "Khong co nhat ky — bo qua cong nay"))
        ra.append(("  ", "Can no khi phien sau khong con ai nho vi sao phien"))
        ra.append(("  ", "truoc doi huong. Tao san bang:"))
        ra.append(("  ", "  python kit/khoi-tao.py ."))
        return 0, ra

    t = doc(f)
    ngay = re.findall(r"^## (\d{4}-\d{2}-\d{2})", t, re.M)
    if not ngay:
        ra.append(("HONG", "Nhat ky khong co muc nao co ngay"))
        ra.append(("   ", "Moi muc bat dau bang '## YYYY-MM-DD — <viec gi>'."))
        ra.append(("   ", "Khong co ngay thi khong ai biet no con moi hay da chet."))
        return 1, ra

    # Bo cac cho con trong ('<...>') truoc khi soi duong dan. Mau cua kit co
    # duong dan vi du nam trong do — quet ca chung thi cong bao hong ngay o
    # du an vua khoi tao. Cung ho keu nham da ghi o lo B.
    soi, thieu = soi_duong_dan(goc, re.sub(r"<[^>]*>", "", t))
    if thieu:
        ra.append(("HONG", "Nhat ky tro toi %d cho khong con ton tai"
                   % len(thieu)))
        for x in sorted(set(thieu))[:8]:
            ra.append(("   ", "   %s" % x))
        ra.append(("   ", "Ho so mat thi muc nhat ky con lai mot cau ket luan"))
        ra.append(("   ", "khong con gi do lai — do dung la thu khong tin duoc."))
        return 1, ra

    moi_nhat = max(ngay)
    chong = None
    if os.path.isdir(os.path.join(goc, ".git")):
        try:
            r = subprocess.run(["git", "log", "--pretty=%ad", "--date=short"],
                               cwd=goc, capture_output=True)
            if r.returncode == 0:
                out = r.stdout.decode("utf-8", "replace")
                chong = [d for d in out.split() if d > moi_nhat]
        except OSError:
            chong = None

    if chong is not None and len(chong) >= NGUONG_COMMIT_CHONG_NHAT_KY:
        ra.append(("HONG", "Nhat ky dung o %s, sau do kho co %d commit"
                   % (moi_nhat, len(chong))))
        ra.append(("   ", "Khong phai bat ban viet nhieu. La: tu day tro di,"))
        ra.append(("   ", "cau hoi 'vi sao hoi do lam the' khong con cho tra loi."))
        return 1, ra

    d = "%s: %d muc, moi nhat %s" % (ngan(goc, f), len(ngay), moi_nhat)
    if soi:
        d += ", %d duong dan deu con that" % soi
    if chong:
        d += ", %d commit chua ghi" % len(chong)
    ra.append(("ok", d))
    return 0, ra


cong_nhat_ky.mo_ta = "Nhat ky con duoc ghi"
cong_nhat_ky.chung_minh = "nhat ky co muc co ngay, khong tro toi ho so da mat, va khong bi bo lai sau %d commit" % NGUONG_COMMIT_CHONG_NHAT_KY
cong_nhat_ky.khong_chung_minh = "muc nhat ky co DUNG hay co ich. Va phan 'bi bo lai' KHONG duoc --tu-kiem phu: ban chep sandbox khong mang theo .git nen doan do im lang o day."


def _pha_nhat_ky(goc):
    """Gieo mot muc nhat ky tro toi ho so khong con ton tai.

    Pha dung cai kiem duoc o moi noi. Phan 'dung lai sau N commit' KHONG gieo
    duoc trong --tu-kiem vi ban chep khong co .git — va cho do duoc khai thang
    trong khong_chung_minh thay vi gia vo la da phu.
    """
    muc = (NL + "## 2026-01-02 — mot phien khong co that" + NL + NL
           + "DA LAM:     de phep thu co cho bam" + NL
           + "HO SO:      `kit/khong-he-co-9k2x/ghi.md`" + NL)
    duong = os.path.join(goc, "NHAT-KY.md")
    if not os.path.exists(duong):
        duong2 = os.path.join(goc, "docs", "NHAT-KY.md")
        if os.path.exists(duong2):
            duong = duong2
        else:
            io.open(duong, "w", encoding="utf-8", newline="").write(
                "# Nhat ky" + NL + muc)
            return
    io.open(duong, "a", encoding="utf-8", newline="").write(muc)


cong_nhat_ky.pha = _pha_nhat_ky


# Hai ten file quy uoc pho bien nhat. Khong cong cu nao doc ca hai.
CAP_QUY_UOC = ("AGENTS.md", "CLAUDE.md")

# Bao nhieu dong CO NOI DUNG thi coi la mot ban chinh chu khong phai mot dong
# tro. Khong dem dong trong, dong trich dan, dong '@import'.
NGUONG_DAY = 15


def _dong_that(t):
    n = 0
    for d in t.splitlines():
        d = d.strip()
        if not d or d.startswith((">", "@", "#", "-" * 3)):
            continue
        n += 1
    return n


def cong_quy_uoc(goc):
    """File quy uoc co toi duoc cong cu khong, va co dung MOT ban khong.

    Do duoc, khong phong xa: mot cong cu khac hang KHONG doc CLAUDE.md, no doc
    AGENTS.md. Thieu ten nao thi voi cong cu do, quy uoc la MOT THU VO HINH —
    va no im lang y het truong hop quy uoc co ma khong co tac dung. Hai thu ay
    cho ra CUNG MOT quan sat, nen phai chan bang file chu khong bang niem tin.

    Ma chep noi dung sang ca hai thi thanh hai nguon su that, va mot ban se cu
    di ma khong ai biet ban nao cu. Do la ho loi so 5.
    """
    ra = []
    co = [t for t in CAP_QUY_UOC if os.path.exists(os.path.join(goc, t))]
    if not co:
        ra.append(("--", "Khong co file quy uoc — bo qua cong nay"))
        ra.append(("  ", "Can no khi ban phai nhac lai mot thu den lan thu ba."))
        ra.append(("  ", "Tao san bang:  python kit/khoi-tao.py ."))
        return 0, ra

    if len(co) == 1:
        thieu = [t for t in CAP_QUY_UOC if t not in co][0]
        ra.append(("HONG", "Chi co %s, khong co %s" % (co[0], thieu)))
        ra.append(("   ", "Cong cu nao tu doc %s se khong thay quy uoc nao ca," % thieu))
        ra.append(("   ", "va no khong bao loi — no chay nhu the ban chua viet gi."))
        ra.append(("   ", "Sua: tao %s voi DUNG MOT DONG tro toi %s." % (thieu, co[0])))
        return 1, ra

    day = [t for t in co if _dong_that(doc(os.path.join(goc, t))) >= NGUONG_DAY]

    if len(day) == 2:
        ra.append(("HONG", "Ca %s deu la ban day — hai nguon su that"
                   % " va ".join(co)))
        ra.append(("   ", "Sua mot ban thi ban kia cu di ma khong ai biet ban nao"))
        ra.append(("   ", "cu. Giu MOT ban chinh, ban con lai chi tro toi no."))
        return 1, ra

    if not day:
        ra.append(("ok", "%s: ca hai deu ngan, chua co ban chinh nao de lech"
                   % " + ".join(co)))
        return 0, ra

    chinh = day[0]
    mong = [t for t in co if t != chinh][0]
    if chinh not in doc(os.path.join(goc, mong)):
        ra.append(("HONG", "%s khong tro toi %s" % (mong, chinh)))
        ra.append(("   ", "Cong cu doc %s se thay mot file rong nghia — no khong" % mong))
        ra.append(("   ", "di tim tiep. Viet thang ten %s vao trong do." % chinh))
        return 1, ra

    ra.append(("ok", "%s la ban chinh, %s tro toi no" % (chinh, mong)))
    return 0, ra


cong_quy_uoc.nhin_kho = True
cong_quy_uoc.mo_ta = "Quy uoc toi duoc ca hai loai cong cu"
cong_quy_uoc.chung_minh = "ca %s deu co, chi mot ban mang noi dung, ban kia goi ten no" % " va ".join(CAP_QUY_UOC)
cong_quy_uoc.khong_chung_minh = "cong cu CO DOC file do that khong, hay co lam theo khong. Mot luat khong duoc doc va mot luat khong co tac dung cho ra cung mot quan sat — cong nay chi chan duoc ve thu nhat."


def _pha_quy_uoc(goc):
    """Chep ban chinh sang ban tro — gieo dung hai nguon su that."""
    duong = [os.path.join(goc, t) for t in CAP_QUY_UOC]
    if not os.path.exists(duong[0]):
        io.open(duong[0], "w", encoding="utf-8", newline="").write(
            doc(duong[1]) if os.path.exists(duong[1]) else "# quy uoc" + NL)
    if not os.path.exists(duong[1]):
        io.open(duong[1], "w", encoding="utf-8", newline="").write("# tro" + NL)
    day = doc(duong[0]) if _dong_that(doc(duong[0])) >= NGUONG_DAY else doc(duong[1])
    if _dong_that(day) < NGUONG_DAY:
        day = ("# ban day gia lap" + NL
               + NL.join("- dong quy uoc %d" % i for i in range(NGUONG_DAY + 2)))
    for d in duong:
        io.open(d, "w", encoding="utf-8", newline="").write(day)


cong_quy_uoc.pha = _pha_quy_uoc


# Mot dong truong: "TEN: gia tri". Mau nay dung o HAI cho — _muc_truong() va
# _truong_trong() — nen no phai nam dung mot cho. Chep lam hai ban thi ban thu
# hai se cu di ma khong ai thay.
MAU_TRUONG = re.compile(r"^([A-Za-z\u00C0-\u1EF9 ]{3,20}):\s*(.*)$")


def _truong_trong(t):
    """Cac dong "TEN: gia tri" trong mot DOAN van ban, khong can tieu de muc.

    Dung cho nhung cho da cat san doan can doc — vi du muc "viec tiep theo",
    von co the nam duoi mot tieu de "###" chu khong phai "##".
    """
    truong = {}
    for d in t.splitlines():
        m = MAU_TRUONG.match(d)
        if m:
            truong[khong_dau(m.group(1)).strip()] = m.group(2).strip()
    return truong


def _muc_truong(t):
    """Chia mot file thanh cac muc "## ", moi muc la mot dict truong.

    Dung cho DA-TRA.md va KET-NOI.md. Muc KHONG co truong nao la van xuoi
    (vi du muc "Co y KHONG noi"), nguoi goi tu bo qua.

    Truong chua tra loi = gia tri bat dau bang '<' (quy uoc cho trong cua kit),
    hoac vang mat. Ten truong duoc bo dau de nguoi viet "GIAY PHEP" hay
    "GIAY PHEP" deu duoc.
    """
    ra, ten, truong = [], None, None
    for d in t.splitlines():
        if d.startswith("## "):
            if ten is not None:
                ra.append((ten, truong))
            ten, truong = d[3:].strip(), {}
            continue
        if truong is None:
            continue
        m = MAU_TRUONG.match(d)
        if m:
            # khong_dau() tra ve CHU THUONG — tra khoa phai dung chu
            # thuong, neu khong cong se im lang vi KHONG THAY MUC NAO.
            truong[khong_dau(m.group(1)).strip()] = m.group(2).strip()
    if ten is not None:
        ra.append((ten, truong))
    return ra


# Nhung chu dien vao cho co, khong tra loi gi. So sanh NGUYEN O chu khong phai
# tien to: "chua" khong phai cau tra loi, nhung "chua can, vi X" thi la — no co
# ly do di kem. Lay tien to thi cai thu hai bi bao nham, va mot cong keu nham
# se bi tat di.
KHONG_PHAI_TRA_LOI = (
    "chua", "chua lam", "chua co", "chua ro", "chua biet", "se lam",
    "se lam sau", "sau", "todo", "tbd", "khong biet", "n/a", "na", "-",
    "?", "...", "x",
)


def _da_tra_loi(v):
    """O co duoc dien mot cau tra loi that khong.

    Ba kieu khong phai tra loi: bo trong, con nguyen placeholder <...>, va
    dien mot chu giu cho nhu "chua". Kieu thu ba la kieu duy nhat doc len
    giong nhu da lam xong.
    """
    if not v or v.startswith("<"):
        return False
    return khong_dau(v).strip().strip(".!,;:") not in KHONG_PHAI_TRA_LOI


def cong_da_tra(goc):
    """So 'da tra': mot muc phai ngan duoc lan tra lai, va phai co giay phep.

    Cai dat nhat trong mot ghi chep tra cuu khong phai cai DA CHON, la cai DA
    LOAI. Thieu dong do thi ba tuan sau van co nguoi tra lai tu dau — va co the
    ra ket luan nguoc, khong phai vi su that doi ma vi ly do cu da mat.

    Giay phep thi kiem vi mot ly do khac: no la thu khong bao gio bao loi luc
    build. No chi noi chuyen rat lau ve sau, va luc do thi da muon.
    """
    ra = []
    f = tim_tep(goc, "DA-TRA.md", "docs/DA-TRA.md")
    if not f:
        ra.append(("--", "Khong co so 'da tra' — bo qua cong nay"))
        ra.append(("  ", "Can no lan dau ban dinh dung mot thu mat hon nua ngay."))
        ra.append(("  ", "Tao san bang:  python kit/khoi-tao.py ."))
        return 0, ra

    t = doc(f)
    muc = [(k, v) for k, v in _muc_truong(t) if not k.startswith("<") and v]
    if not muc:
        ra.append(("--", "So 'da tra' chua co muc nao — chua co gi de kiem"))
        ra.append(("  ", "Dien khi lan dau ban tra xem co ai lam san chua."))
        ra.append(("  ", "Truoc do no dung ra la con trong."))
        return 0, ra

    hom_nay = time.strftime("%Y-%m-%d")
    hong = []
    for ten, tr in muc:
        chon = tr.get("chon", "")
        if not _da_tra_loi(chon):
            continue
        ngan_ten = ten if len(ten) <= 46 else ten[:43] + "..."

        if not _da_tra_loi(tr.get("da loai", "")):
            hong.append((ngan_ten, "khong ghi DA LOAI gi",
                         "Muc nay khong ngan duoc lan tra lai. Nguoi sau van"
                         " phai tu hoi 'the da xem cai kia chua?'"))
            continue

        tu_dung = khong_dau(chon).find("tu dung") >= 0
        gp = tr.get("giay phep", "")
        if not tu_dung and not _da_tra_loi(gp):
            hong.append((ngan_ten, "chon mot thu ben ngoai ma khong ghi giay phep",
                         "Giay phep khong bao gio bao loi luc build. No chi noi"
                         " chuyen rat lau ve sau."))
            continue

        if khong_dau(gp).find("khong ro") >= 0:
            han = tr.get("xem lai", "")
            m = re.search(r"\d{4}-\d{2}-\d{2}", han)
            if not m:
                hong.append((ngan_ten, "giay phep 'khong ro' ma khong co han xem lai",
                             "Ghi 'khong ro' la trung thuc va duoc phep. De no"
                             " khong co han thi moi la bo quen."))
            elif m.group(0) < hom_nay:
                hong.append((ngan_ten, "giay phep 'khong ro', han xem lai %s da qua"
                             % m.group(0),
                             "Han tu dat ma tu bo qua thi lan sau khong ai dat"
                             " han that nua."))

    if hong:
        ra.append(("HONG", "So 'da tra': %d muc co van de" % len(hong)))
        for ten, vi_sao, giai in hong[:6]:
            ra.append(("   ", "   %s" % ten))
            ra.append(("   ", "      -> %s" % vi_sao))
            ra.append(("   ", "      %s" % giai))
        return 1, ra

    soi, thieu = soi_duong_dan(goc, re.sub(r"<[^>]*>", "", t))
    if thieu:
        ra.append(("HONG", "So 'da tra' tro toi %d cho khong con ton tai"
                   % len(thieu)))
        for x in sorted(set(thieu))[:8]:
            ra.append(("   ", "   %s" % x))
        return 1, ra

    d = "%s: %d muc da tra loi" % (ngan(goc, f), len(muc))
    if soi:
        d += ", %d duong dan deu con that" % soi
    ra.append(("ok", d))
    return 0, ra


cong_da_tra.mo_ta = "So 'da tra' ngan duoc lan tra lai"
cong_da_tra.chung_minh = "moi muc DA CHON deu ghi ro da loai gi, va ghi giay phep; giay phep 'khong ro' phai co han xem lai chua qua"
cong_da_tra.khong_chung_minh = "ban da tra DU, hay tra DUNG, hay giay phep ghi trong do la that. No doc chu, khong doc giay phep goc."


def _pha_da_tra(goc):
    """Gieo mot muc DA CHON mot thu ben ngoai ma khong ghi giay phep."""
    muc = (NL + "## Chon thu vien bieu do nao" + NL + NL
           + "NGAY:      2026-01-02" + NL
           + "DA TRA:    hai ung vien pho bien" + NL
           + "CHON:      cai thu nhat" + NL
           + "VI SAO:    nhe hon" + NL
           + "DA LOAI:   cai thu hai, vi keo theo mot bo phu thuoc lon" + NL)
    for ten in ("DA-TRA.md", os.path.join("docs", "DA-TRA.md")):
        duong = os.path.join(goc, ten)
        if os.path.exists(duong):
            io.open(duong, "a", encoding="utf-8", newline="").write(muc)
            return
    io.open(os.path.join(goc, "DA-TRA.md"), "w", encoding="utf-8",
            newline="").write("# Da tra" + NL + muc)


cong_da_tra.pha = _pha_da_tra


# Ba muc quyen, xep theo cai gia cua mot lan sai.
QUYEN_CHO_NOI = ("doc", "ghi", "tieu tien")


def cong_ket_noi(goc):
    """Cho noi nao GHI duoc thi phai co gioi han viet ra va mot cach tat.

    Cho noi khac cho dua. Cho dua la thu MAT THI MINH CHET, va cong
    cong_cho_dua da nhin phan do. Cho noi la thu MINH VOI TOI DUOC — plugin,
    connector, MCP, khoa API. Cai duoc them vao khong phai "kha nang gui mail",
    la "tu gio con AI nay gui mail duoc". Hai cau do nghe giong nhau va khac
    han nhau dung luc mot thu chay sai.

    Nen cong nay khong hoi "no con song khong". No hoi "no lam duoc gi, va ai
    chan".
    """
    ra = []
    f = tim_tep(goc, "KET-NOI.md", "docs/KET-NOI.md")
    if not f:
        ra.append(("--", "Khong co so cho noi — bo qua cong nay"))
        ra.append(("  ", "Can no lan dau ban cam mot plugin / connector / MCP"))
        ra.append(("  ", "vao du an. Tao san bang:  python kit/khoi-tao.py ."))
        return 0, ra

    t = doc(f)
    # Muc khong co truong nao la van xuoi — vi du muc "Co y KHONG noi", chinh
    # la muc dang co nhat trong file. Quet no nhu mot cho noi thi cong bao
    # hong ngay o du an vua khoi tao, va do la kieu keu nham da ghi o lo B.
    muc = [(k, v) for k, v in _muc_truong(t) if not k.startswith("<") and v]
    if not muc:
        ra.append(("--", "Chua khai bao cho noi nao — chua co gi de kiem"))
        ra.append(("  ", "Do KHONG phai 'du an nay khong noi ra ngoai'. Cong nay"))
        ra.append(("  ", "doc file, no khong di do xem ban da cam gi vao may."))
        return 0, ra

    hong = []
    for ten, tr in muc:
        ngan_ten = ten if len(ten) <= 46 else ten[:43] + "..."
        q = tr.get("quyen", "")
        if not _da_tra_loi(q):
            hong.append((ngan_ten, "khong ghi QUYEN",
                         "Khong biet no doc hay ghi thi khong ai uoc luong duoc"
                         " mot lan sai dat toi dau."))
            continue
        nang = khop_ten(q, QUYEN_CHO_NOI)
        if not nang:
            hong.append((ngan_ten, "QUYEN '%s' khong nam trong danh sach" % q,
                         "Phai khop BANG mot trong: %s. Mot chu tu nghi ra, hay"
                         " 'doc va ghi', thi may doc duoc ma nguoi thi moi nguoi"
                         " hieu mot kieu." % " / ".join(QUYEN_CHO_NOI)))
            continue
        if nang == "doc":
            continue
        thieu = [ten_t.upper() for ten_t, kh in
                 (("gioi han", "gioi han"), ("tat ra sao", "tat ra sao"))
                 if not _da_tra_loi(tr.get(kh, ""))]
        if thieu:
            hong.append((ngan_ten, "quyen '%s' ma thieu: %s"
                         % (nang, ", ".join(thieu)),
                         "Mot cho noi GHI duoc ma khong ai viet ra gioi han va"
                         " cach tat thi luc can tat, khong ai biet tat o dau."))

    if hong:
        ra.append(("HONG", "So cho noi: %d cho co van de" % len(hong)))
        for ten, vi_sao, giai in hong[:6]:
            ra.append(("   ", "   %s" % ten))
            ra.append(("   ", "      -> %s" % vi_sao))
            ra.append(("   ", "      %s" % giai))
        return 1, ra

    soi, thieu = soi_duong_dan(goc, re.sub(r"<[^>]*>", "", t))
    if thieu:
        ra.append(("HONG", "So cho noi tro toi %d cho khong con ton tai"
                   % len(thieu)))
        for x in sorted(set(thieu))[:8]:
            ra.append(("   ", "   %s" % x))
        return 1, ra

    dem = {}
    for _, tr in muc:
        x = khop_ten(tr.get("quyen", ""), QUYEN_CHO_NOI)
        if x:
            dem[x] = dem.get(x, 0) + 1
    d = "%s: %d cho noi (%s)" % (
        ngan(goc, f), len(muc),
        ", ".join("%d %s" % (dem[x], x) for x in QUYEN_CHO_NOI if x in dem))
    ra.append(("ok", d))
    return 0, ra


cong_ket_noi.mo_ta = "Cho noi ghi duoc thi co cach tat"
cong_ket_noi.chung_minh = "moi cho noi da khai bao deu goi ten QUYEN cua no, va cho nao GHI hay TIEU TIEN duoc thi co viet ra gioi han lan cach tat"
cong_ket_noi.khong_chung_minh = "ban da khai bao DU cho noi. No doc file, no KHONG di do xem may ban dang cam nhung gi — cho noi khong ai ghi thi no khong thay."


def _pha_ket_noi(goc):
    """Gieo mot cho noi GHI duoc ma khong ai viet gioi han lan cach tat."""
    muc = (NL + "## Hop thu chung cua nhom" + NL + NL
           + "DUNG DE:     gui bao cao hang tuan" + NL
           + "QUYEN:       ghi" + NL
           + "CHAM TOI:    toan bo hop thu, ke ca thu cu" + NL
           + "BAT BOI:     khong ro, 2026-01-02" + NL)
    for ten in ("KET-NOI.md", os.path.join("docs", "KET-NOI.md")):
        duong = os.path.join(goc, ten)
        if os.path.exists(duong):
            io.open(duong, "a", encoding="utf-8", newline="").write(muc)
            return
    io.open(os.path.join(goc, "KET-NOI.md"), "w", encoding="utf-8",
            newline="").write("# Cho noi" + NL + muc)


cong_ket_noi.pha = _pha_ket_noi


TRANG_THAI_GIAI_DOAN = ("chua toi", "dang lam", "xong")


def _do_duoc(v):
    """Mot dieu kien thoat DO DUOC: co so, co duong dan, hoac tro toi mot file.

    Luat hep va co y hep. No KHONG kiem duoc "dieu kien nay dung"; no chi loai
    duoc loai cau khong bao gio chot lai duoc — "xong het task", "on dinh",
    "day du". Do dung la thu du an sinh ra file nay tu cam trong STATE.md.
    """
    return bool(re.search(r"[0-9]", v) or "/" in v or "`" in v)


def cong_giai_doan(goc):
    """Day giai doan: dung MOT cai dang lam, dieu kien thoat do duoc, va khop
    voi STATE.md.

    STATE.md noi ban DANG o dau. File nay noi co nhung giai doan nao va moi
    cai CO Y hoan lai gi. Hai file noi hai ten khac nhau thi khong file nao
    sai ro rang — va do moi la kieu kho chiu nhat, vi khong ai biet phai sua
    ben nao.
    """
    ra = []
    f = tim_tep(goc, "GIAI-DOAN.md", "docs/GIAI-DOAN.md")
    if not f:
        ra.append(("--", "Khong co day giai doan — bo qua cong nay"))
        ra.append(("  ", "Can no khi du an dai hon mot cau hoi. Tao san bang:"))
        ra.append(("  ", "  python kit/khoi-tao.py ."))
        return 0, ra

    t = doc(f)
    muc = [(k, v) for k, v in _muc_truong(t) if not k.startswith("<") and v]
    if not muc:
        ra.append(("--", "Chua khai bao giai doan nao — chua co gi de kiem"))
        ra.append(("  ", "Mot du an mot cau hoi thi mot giai doan, va luc do"))
        ra.append(("  ", "STATE.md da du. File nay de danh cho luc dai hon."))
        return 0, ra

    hong, dang_lam = [], []
    for ten, tr in muc:
        ngan_ten = ten if len(ten) <= 46 else ten[:43] + "..."
        tt = tr.get("trang thai", "")
        if not _da_tra_loi(tt):
            hong.append((ngan_ten, "khong ghi TRANG THAI",
                         "Khong biet giai doan nay da qua, dang lam hay chua"
                         " toi thi ca day nay chi la van xuoi."))
            continue
        x = khop_ten(tt, TRANG_THAI_GIAI_DOAN)
        if not x:
            hong.append((ngan_ten, "TRANG THAI '%s' khong nam trong danh sach" % tt,
                         "Phai khop BANG mot trong: %s. 'sap xong' khong phai"
                         " mot trang thai — no la mot cam giac."
                         % " / ".join(TRANG_THAI_GIAI_DOAN)))
            continue
        if x == "dang lam":
            dang_lam.append(ten)

        thoat = tr.get("thoat khi", "")
        if not _da_tra_loi(thoat):
            hong.append((ngan_ten, "khong ghi THOAT KHI",
                         "Giai doan khong co dieu kien thoat thi no khong ket"
                         " thuc, no chi nhat dan."))
        elif not _do_duoc(thoat):
            hong.append((ngan_ten, "THOAT KHI khong do duoc: %s"
                         % (thoat if len(thoat) <= 52 else thoat[:49] + "..."),
                         "Can mot SO, mot DUONG DAN, hoac mot nguoi cu the lam"
                         " duoc viec cu the. 'Xong het task' thi khong ai chot"
                         " lai duoc."))

        if not _da_tra_loi(tr.get("hoan lai", "")):
            hong.append((ngan_ten, "khong ghi HOAN LAI",
                         "Thang sau se co nguoi keo mot viec cua giai doan sau"
                         " vao day, rat hop ly — va khong ai con nho rang no da"
                         " duoc CAN NHAC VA GAT DI."))

    chua_xong = [k for k, v in muc
                 if khop_ten(v.get("trang thai", ""), TRANG_THAI_GIAI_DOAN)
                 != "xong"]
    if len(dang_lam) > 1:
        hong.append((", ".join(dang_lam[:3]), "%d giai doan cung 'dang lam'"
                     % len(dang_lam),
                     "Hoac du an that su chay hai luong — noi ra — hoac khong"
                     " ai biet minh dang o dau."))
    elif not dang_lam and chua_xong:
        hong.append(("(ca day)", "khong giai doan nao 'dang lam'",
                     "Con %d giai doan chua xong ma khong cai nao dang chay."
                     " Dang tam dung thi ghi ra; khong ghi thi no la troi."
                     % len(chua_xong)))

    # Doi chieu voi STATE.md — cho hai file noi nguoc nhau ma khong ai sai ro
    fs = tim_tep(goc, "STATE.md", "docs/STATE.md", "TRANG-THAI.md")
    if fs and len(dang_lam) == 1:
        m = re.search(r"^GIAI DOAN:\s*(.+)$", doc(fs), re.M)
        if m:
            ten_s = m.group(1).strip().strip("`")
            if _da_tra_loi(ten_s):
                a = khong_dau(ten_s).strip()
                b = khong_dau(dang_lam[0]).strip()
                if a and b and a.find(b) < 0 and b.find(a) < 0:
                    hong.append((ngan(goc, fs),
                                 "STATE noi '%s', day giai doan dang lam '%s'"
                                 % (ten_s[:40], dang_lam[0][:40]),
                                 "Hai file noi hai ten khac nhau. Khong file nao"
                                 " sai ro rang, nen khong ai sua ben nao ca."))

    if hong:
        ra.append(("HONG", "Day giai doan: %d cho co van de" % len(hong)))
        for ten, vi_sao, giai in hong[:6]:
            ra.append(("   ", "   %s" % ten))
            ra.append(("   ", "      -> %s" % vi_sao))
            ra.append(("   ", "      %s" % giai))
        return 1, ra

    soi, thieu = soi_duong_dan(goc, re.sub(r"<[^>]*>", "", t))
    if thieu:
        ra.append(("HONG", "Day giai doan tro toi %d cho khong con ton tai"
                   % len(thieu)))
        for x in sorted(set(thieu))[:8]:
            ra.append(("   ", "   %s" % x))
        return 1, ra

    d = "%s: %d giai doan" % (ngan(goc, f), len(muc))
    d += ", dang lam: %s" % (dang_lam[0][:40] if dang_lam else "khong con cai nao")
    ra.append(("ok", d))
    return 0, ra


cong_giai_doan.mo_ta = "Day giai doan con chot duoc"
cong_giai_doan.chung_minh = "moi giai doan goi ten TRANG THAI, co dieu kien thoat DO DUOC va co ghi cai hoan lai; dung mot giai doan dang lam; va ten do khop voi STATE.md"
cong_giai_doan.khong_chung_minh = "ke hoach do DUNG, hay kha thi, hay du. Dieu kien thoat co SO khong co nghia la con so ay do dung thu can do."


def _pha_giai_doan(goc):
    """Gieo HAI giai doan cung 'dang lam'.

    Pha kieu nay chay duoc ca tren du an vua khoi tao (chua co giai doan nao,
    cong dang im) lan tren du an da co san mot giai doan.
    """
    khoi = (NL + "## Cau hoi khong co that %d" + NL + NL
            + "TRANG THAI:   dang lam" + NL
            + "THOAT KHI:    `kit/cong.py` thoat 0" + NL
            + "TRONG DO:     de phep thu co cho bam" + NL
            + "HOAN LAI:     khong gi ca" + NL
            + "DUNG LAI NEU: khong bao gio" + NL)
    xau = (khoi % 1) + (khoi % 2)
    for ten in ("GIAI-DOAN.md", os.path.join("docs", "GIAI-DOAN.md")):
        duong = os.path.join(goc, ten)
        if os.path.exists(duong):
            io.open(duong, "a", encoding="utf-8", newline="").write(xau)
            return
    io.open(os.path.join(goc, "GIAI-DOAN.md"), "w", encoding="utf-8",
            newline="").write("# Giai doan" + NL + xau)


cong_giai_doan.pha = _pha_giai_doan


def _dem_tu(t):
    """Dem tu tho, bo khoi ma va the HTML. Cung cach voi `wc -w` ve do lon."""
    t = re.sub(r"```.*?```", " ", t, flags=re.S)
    t = re.sub(r"<[^>]{1,200}>", " ", t)
    return len(t.split())


def cong_ngan_sach(goc):
    """Tang LUON DOC co vuot ngan sach da khai khong.

    Cai dat nhat khong phai file dai nhat, la file duoc doc LAI MOI PHIEN. Mot
    tai lieu 20 nghin tu doc mot lan mot thang thi re. Cung 20 nghin tu do nam
    trong danh sach "doc truoc khi lam" thi phai tra o MOI PHIEN, mai mai, va
    tra TRUOC KHI noi duoc cau nao ve viec that.

    Cach re nhat de vuot ma khong ai thay: de LICH SU tich lai trong file trang
    thai. No lon len moi tuan mot it, khong lan nao dang de ai keu.
    """
    ra = []
    f = tim_tep(goc, "NGAN-SACH.md", "docs/NGAN-SACH.md")
    if not f:
        ra.append(("--", "Khong co ngan sach ngu canh — bo qua cong nay"))
        ra.append(("  ", "Can no khi file trang thai bat dau dai ra. Tao san:"))
        ra.append(("  ", "  python kit/khoi-tao.py ."))
        return 0, ra

    t = doc(f)
    m = re.search(r"^NGAN SACH:\s*([0-9][0-9 .,]*)", t, re.M)
    mg = re.search(r"^GOM:\s*(.+)$", t, re.M)
    if not m or not mg:
        ra.append(("HONG", "Ngan sach thieu dong NGAN SACH hoac dong GOM"))
        ra.append(("   ", "Khong co so thi khong ai vuot duoc, va do khong phai"))
        ra.append(("   ", "la an toan — do la khong do."))
        return 1, ra

    tran = int(re.sub(r"[^0-9]", "", m.group(1)))
    ten = re.findall(r"`([^`]{1,120})`", mg.group(1))
    if not ten:
        ra.append(("HONG", "Dong GOM khong ke ten file nao"))
        ra.append(("   ", "Ghi ten trong dau nguoc, vi du `AGENTS.md`."))
        return 1, ra

    do = []
    for x in ten:
        p = tim_tep(goc, x, os.path.join("docs", x))
        if p:
            do.append((x, _dem_tu(doc(p))))
    if not do:
        ra.append(("--", "Khong file nao trong dong GOM ton tai — chua do duoc"))
        return 0, ra

    tong = sum(n for _, n in do)
    do.sort(key=lambda z: -z[1])
    if tong > tran:
        ra.append(("HONG", "Tang luon doc: %d tu, vuot ngan sach %d tu"
                   % (tong, tran)))
        for x, n in do[:5]:
            ra.append(("   ", "   %-28s %6d tu  (%d%%)"
                       % (x, n, round(100.0 * n / tong))))
        ra.append(("   ", "Day la khoan tra o MOI PHIEN, truoc khi noi duoc cau"))
        ra.append(("   ", "nao ve viec that. Cho phinh to nhat thuong la LICH SU"))
        ra.append(("   ", "tich trong file trang thai — chuyen no sang nhat ky."))
        return 1, ra

    ra.append(("ok", "%s: tang luon doc %d/%d tu (%d file)"
               % (ngan(goc, f), tong, tran, len(do))))
    for x, n in do[:3]:
        ra.append(("  ", "   %-28s %6d tu" % (x, n)))
    return 0, ra


cong_ngan_sach.mo_ta = "Tang luon doc con trong ngan sach"
cong_ngan_sach.chung_minh = "tong so tu cua cac file da khai o dong GOM khong vuot so da khai o dong NGAN SACH"
cong_ngan_sach.khong_chung_minh = "con so ngan sach do DUNG, hay tiet kiem. Va no chi do nhung file BAN KE RA — mot file duoc doc moi phien ma khong ai ke vao GOM thi no khong thay."


def _pha_ngan_sach(goc):
    """Ha tran xuong duoi muc dang do duoc.

    Pha o phia NGAN SACH chu khong phai phia noi dung, vi mot du an vua khoi
    tao chi co vai nghin tu — nhoi them cho du vai chuc nghin tu thi phep thu
    dang do toc do ghi dia chu khong do cai gi ca.
    """
    for ten in ("NGAN-SACH.md", os.path.join("docs", "NGAN-SACH.md")):
        duong = os.path.join(goc, ten)
        if os.path.exists(duong):
            t = doc(duong)
            t2 = re.sub(r"^NGAN SACH:\s*[0-9][0-9 .,]*.*$",
                        "NGAN SACH: 1 tu", t, count=1, flags=re.M)
            io.open(duong, "w", encoding="utf-8", newline="").write(t2)
            return
    io.open(os.path.join(goc, "NGAN-SACH.md"), "w", encoding="utf-8",
            newline="").write(
        "# Ngan sach" + NL + NL + "NGAN SACH: 1 tu" + NL
        + "GOM:       `AGENTS.md`, `CLAUDE.md`" + NL)


cong_ngan_sach.pha = _pha_ngan_sach


# Con bao nhieu ngay thi keu. Vi sao 60: du de gia han khong voi, va du muon
# de khong keu suot nua nam. Mot cong keu 200 ngay lien thi bi tat di.
NGUONG_NGAY_TEN_MIEN = 60

# Dong khai bao ten mien trong phu-thuoc-ngoai.txt. Dung tien to rieng de cong
# URL cu KHONG co goi no nhu mot dia chi web.
TIEN_TO_TEN_MIEN = "ten-mien "


def _han_ten_mien(ten):
    """Tra ve (ngay het han dang YYYY-MM-DD, trang thai) hoac (None, ly do).

    Di qua bang chi duong cua IANA roi toi may chu cua chinh khu vuc do. Khong
    dung mot dich vu trung gian: mot cai tra ve HTML khi loi, va luc do script
    doc duoc "khong sao ca" tu mot thu khong phai du lieu.
    """
    import json as _json
    import urllib.request
    kv = ten.rsplit(".", 1)[-1].lower()
    try:
        bt = urllib.request.urlopen(
            urllib.request.Request("https://data.iana.org/rdap/dns.json",
                                   headers={"User-Agent": "kit-cong"}),
            timeout=20).read().decode("utf-8", "replace")
        dich = None
        for svc in _json.loads(bt).get("services", []):
            if kv in [x.lower() for x in svc[0]]:
                dich = svc[1][0]
                break
        if not dich:
            return None, "IANA khong co may chu RDAP cho duoi .%s" % kv
        u = dich.rstrip("/") + "/domain/" + ten
        t = urllib.request.urlopen(
            urllib.request.Request(u, headers={"User-Agent": "kit-cong"}),
            timeout=20).read().decode("utf-8", "replace")
        d = _json.loads(t)
    except Exception as e:
        return None, type(e).__name__

    for ev in d.get("events", []):
        if ev.get("eventAction") == "expiration":
            return (ev.get("eventDate", "")[:10],
                    ",".join(d.get("status", []) or ["?"]))
    return None, "RDAP khong tra ve ngay het han"


def cong_ten_mien(goc):
    """Ten mien da khai bao con bao lau nua het han. Can mang.

    Het han thi may chu van chay, moi cong trong nha van xanh, va dia chi
    nguoi ta go vao thi khong vao duoc. Do la kieu hong im lang nhat trong
    danh sach: khong co gi bao loi ca, chi la khong ai vao duoc nua.
    """
    ra = []
    f = tim_tep(goc, TEP_PHU_THUOC, "docs/" + TEP_PHU_THUOC)
    ten_mien = []
    if f:
        for d in doc(f).splitlines():
            d = d.strip()
            if d.lower().startswith(TIEN_TO_TEN_MIEN):
                phan = re.split(r"\s{2,}|\t", d[len(TIEN_TO_TEN_MIEN):].strip(), 1)
                ten_mien.append((phan[0].strip(),
                                 phan[1].strip() if len(phan) > 1 else ""))
    if not ten_mien:
        ra.append(("--", "Khong khai bao ten mien nao — bo qua cong nay"))
        ra.append(("  ", "Khai bao trong %s, moi dong:" % TEP_PHU_THUOC))
        ra.append(("  ", "  ten-mien vi-du.com<hai dau cach>vai tro cua no"))
        return 0, ra

    hom_nay = time.strftime("%Y-%m-%d")
    hong = 0
    for ten, vai in ten_mien:
        han, tt = _han_ten_mien(ten)
        if not han:
            ra.append(("HONG", "%-30s khong tra duoc han: %s" % (ten, tt)))
            ra.append(("   ", "Khong tra duoc KHONG PHAI la 'con han'. Do la"))
            ra.append(("   ", "khong biet — va khong biet thi khong yen tam duoc."))
            hong += 1
            continue
        con = _so_ngay(hom_nay, han)
        d = "%-30s het han %s (con %d ngay)  %s" % (ten, han, con, vai[:24])
        if con <= NGUONG_NGAY_TEN_MIEN:
            ra.append(("HONG", d))
            ra.append(("   ", "Het han thi may chu van chay va moi cong van xanh."))
            ra.append(("   ", "Khong co gi bao loi ca — chi la khong ai vao duoc."))
            hong += 1
        else:
            ra.append(("ok", d))
            if "active" not in tt and "ok" not in tt.lower():
                ra.append(("   ", "Trang thai dang ky: %s" % tt))
    return (1 if hong else 0), ra


def _so_ngay(a, b):
    """So ngay tu a den b, ca hai dang YYYY-MM-DD. Khong dung thu vien ngoai."""
    import calendar

    def stt(x):
        y, m, d = [int(z) for z in x.split("-")]
        n = d
        for yy in range(1970, y):
            n += 366 if calendar.isleap(yy) else 365
        for mm in range(1, m):
            n += calendar.monthrange(y, mm)[1]
        return n
    return stt(b) - stt(a)


cong_ten_mien.mo_ta = "Ten mien con han"
cong_ten_mien.can_mang = True
cong_ten_mien.chung_minh = "ten mien DA KHAI BAO con han qua %d ngay, theo so dang ky" % NGUONG_NGAY_TEN_MIEN
cong_ten_mien.khong_chung_minh = "ban da khai bao DU ten mien, hay the thanh toan gia han con song. No doc so dang ky, khong doc vi cua ban."


def _pha_ten_mien(goc):
    """Gieo mot ten mien khong co that trong danh sach da khai."""
    for ten in (TEP_PHU_THUOC, os.path.join("docs", TEP_PHU_THUOC)):
        duong = os.path.join(goc, ten)
        if os.path.exists(duong):
            io.open(duong, "a", encoding="utf-8", newline="").write(
                NL + "ten-mien khong-he-ton-tai-9k2x.tech  gieo de thu phep kiem" + NL)
            return
    io.open(os.path.join(goc, TEP_PHU_THUOC), "w", encoding="utf-8",
            newline="").write(
        "ten-mien khong-he-ton-tai-9k2x.tech  gieo de thu phep kiem" + NL)


cong_ten_mien.pha = _pha_ten_mien


# Dong khai bao ban sao, moi dong: ban-sao <duong dan trong kho><2 dau cach><URL>
TIEN_TO_BAN_SAO = "ban-sao "


def _bo_xuong_dong(t):
    """So sanh noi dung, khong so ky tu xuong dong.

    Windows va Linux ghi khac nhau, va mot cong bao do vi CRLF thi bi tat di
    trong tuan dau tien.
    """
    return t.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")


def cong_ban_sao(goc):
    """File trong kho co con khop voi ban DA CONG BO khong. Can mang.

    Tach lam hai kho la BAT BUOC khi mot ben phai cong khai con ben kia rieng
    tu — khong ai publish duoc mot thu muc con cua kho rieng tu. Cai KHONG bat
    buoc la de viec dong bo hai ben song bang tri nho.

    Kieu hong o day im lang tuyet doi: hai ban tu tu lech nhau, ca hai deu chay
    duoc, va moi cong trong nha van xanh.
    """
    ra = []
    f = tim_tep(goc, TEP_PHU_THUOC, "docs/" + TEP_PHU_THUOC)
    cap = []
    if f:
        for d in doc(f).splitlines():
            d = d.strip()
            if d.lower().startswith(TIEN_TO_BAN_SAO):
                phan = re.split(r"\s{2,}|\t", d[len(TIEN_TO_BAN_SAO):].strip(), 1)
                if len(phan) == 2:
                    cap.append((phan[0].strip(), phan[1].strip()))
    if not cap:
        ra.append(("--", "Khong khai bao ban sao nao — bo qua cong nay"))
        ra.append(("  ", "Can no khi mot phan cua kho nay duoc cong bo o cho"))
        ra.append(("  ", "khac. Khai bao trong %s, moi dong:" % TEP_PHU_THUOC))
        ra.append(("  ", "  ban-sao kit/cong.py<hai dau cach><URL ban cong bo>"))
        return 0, ra

    import urllib.request
    hong = 0
    for duong, url in cap:
        p = os.path.join(goc, duong)
        if not os.path.exists(p):
            ra.append(("HONG", "%-28s khong co trong kho nay" % duong))
            hong += 1
            continue
        try:
            # Xin dung tra ban cache. Nhieu CDN giu ban cu vai phut, va ngay
            # sau mot lan cong bo thi cong nay se bao LECH trong khi hai ben
            # that su da khop.
            yc = urllib.request.Request(url, headers={
                "User-Agent": "kit-cong",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                # Do duoc: header no-cache mot minh KHONG du — CDN cua GitHub
                # van tra ban cu. Duong qua API thi tuoi ngay lap tuc, va
                # header nay bao no tra ve NOI DUNG THO thay vi JSON.
                # "*/*" de may chu khong phai GitHub van phuc vu binh thuong.
                "Accept": "application/vnd.github.raw, */*",
            })
            xa = urllib.request.urlopen(yc, timeout=20).read().decode(
                "utf-8", "replace")
        except Exception as e:
            ra.append(("HONG", "%-28s khong tai duoc ban cong bo: %s"
                       % (duong, type(e).__name__)))
            ra.append(("   ", "Khong tai duoc KHONG PHAI la 'van khop'."))
            hong += 1
            continue
        if _bo_xuong_dong(doc(p)) == _bo_xuong_dong(xa):
            ra.append(("ok", "%-28s khop ban da cong bo" % duong))
        else:
            ra.append(("HONG", "%-28s LECH voi ban da cong bo" % duong))
            ra.append(("   ", "   %s" % url[:66]))
            hong += 1
    if hong:
        ra.append(("   ", "Hai ban lech nhau thi ca hai van chay duoc, va moi"))
        ra.append(("   ", "cong trong nha van xanh. Do la kieu hong im nhat."))
        ra.append(("   ", "NHUNG: vua cong bo xong ma thay LECH thi kha nang cao"))
        ra.append(("   ", "la CDN chua kip — doi vai phut roi chay lai. Cong nay"))
        ra.append(("   ", "KHONG phan biet duoc hai truong hop do."))
    return (1 if hong else 0), ra


cong_ban_sao.mo_ta = "Ban trong kho khop ban da cong bo"
cong_ban_sao.can_mang = True
cong_ban_sao.chung_minh = "tung file DA KHAI BAO giong het ban dang nam o URL tuong ung, bo qua khac biet ky tu xuong dong"
cong_ban_sao.khong_chung_minh = "ban da khai bao DU cac file duoc cong bo. Mot file cong bo ma khong ai khai thi cong nay khong thay. Va no KHONG phan biet duoc 'lech that' voi 'CDN chua kip cap nhat' — vua cong bo xong thi doi vai phut roi chay lai."


def _pha_ban_sao(goc):
    """Gieo mot cap ban-sao doi nhau: mot file trong kho, mot URL khac han."""
    dong = (NL + "ban-sao kit/bo-qua.txt  "
            "https://raw.githubusercontent.com/thelongmkt2001/pos-kit/main/LICENSE"
            + NL)
    for ten in (TEP_PHU_THUOC, os.path.join("docs", TEP_PHU_THUOC)):
        duong = os.path.join(goc, ten)
        if os.path.exists(duong):
            io.open(duong, "a", encoding="utf-8", newline="").write(dong)
            return
    io.open(os.path.join(goc, TEP_PHU_THUOC), "w", encoding="utf-8",
            newline="").write(dong)


cong_ban_sao.pha = _pha_ban_sao


# Cac tieu de duoc coi la "phan nhin ve phia truoc" cua file trang thai.
TIEU_DE_VIEC_TIEP = ("viec tiep theo", "next", "viec ke tiep")


def _muc_theo_tieu_de(t, ten_chuan):
    """Than cua muc co tieu de khop — SAU NHAT trong cac muc khop, hoac None.

    Nhan ca "## " lan "### ". Vi sao lay cai sau nhat: mot muc ngoai co the
    chua mot muc con cung ten, va phan dau cua muc ngoai thuong la doan giai
    thich. Lay muc ngoai thi doan giai thich do — la lich su — se duoc doc nhu
    la viec sap lam. Do duoc ngay 2026-09-17 tren chinh kho nay.
    """
    dong = t.splitlines()
    dau = []
    for i, d in enumerate(dong):
        for muc in (3, 2):           # "### " truoc, roi "## "
            mo = "#" * muc + " "
            if d.startswith(mo) and not d.startswith(mo + "#"):
                ten = khong_dau(d[len(mo):]).strip()
                if any(ten.startswith(x) for x in ten_chuan):
                    dau.append((i, muc))
                break
    if not dau:
        return None
    i, muc = dau[-1]
    ra = []
    for d in dong[i + 1:]:
        if d.startswith("#"):
            bac = len(d) - len(d.lstrip("#"))
            if bac <= muc and d[bac:bac + 1] == " ":
                break
        ra.append(d)
    return NL.join(ra).strip()


def cong_viec_tiep(goc):
    """Muc "viec tiep theo" co con noi ve giai doan dang lam khong.

    Moi muc khac trong file trang thai deu ke chuyen DA XAY RA, nen khi chung
    cu di thi con doc ra duoc. Muc nay ke chuyen SAP LAM — no cu di ma van doc
    len nhu mot ke hoach, va do la kieu hong khong ai phat hien bang mat.
    """
    ra = []
    fs = tim_tep(goc, "STATE.md", "docs/STATE.md", "TRANG-THAI.md")
    fg = tim_tep(goc, "GIAI-DOAN.md", "docs/GIAI-DOAN.md")
    if not fs or not fg:
        ra.append(("--", "Thieu file trang thai hoac day giai doan — bo qua"))
        return 0, ra

    dang_lam = [k for k, v in _muc_truong(doc(fg))
                if not k.startswith("<") and v
                and khop_ten(v.get("trang thai", ""), TRANG_THAI_GIAI_DOAN)
                == "dang lam"]
    if len(dang_lam) != 1:
        ra.append(("--", "Khong co dung mot giai doan dang lam — cong 'day giai"))
        ra.append(("  ", "doan' lo phan do; cong nay khong co gi de doi chieu."))
        return 0, ra

    than = _muc_theo_tieu_de(doc(fs), TIEU_DE_VIEC_TIEP)
    if than is None:
        ra.append(("--", "File trang thai khong co muc 'viec tiep theo'"))
        ra.append(("  ", "Them mot muc '## Viec tiep theo'. Khong co no thi"))
        ra.append(("  ", "khong cho nao ke ra viec sap lam."))
        return 0, ra
    if not than or than.startswith("<"):
        ra.append(("--", "Muc 'viec tiep theo' con trong — chua co gi de kiem"))
        return 0, ra

    tr = _truong_trong(than)
    if not _da_tra_loi(tr.get("viec", "")):
        ra.append(("HONG", "Muc 'viec tiep theo' khong goi ten MOT viec nao"))
        ra.append(("   ", "   Them mot dong:  VIEC: <mot viec>"))
        ra.append(("   ", "Mot doan van ke rang moi thu deu xong van doc len"))
        ra.append(("   ", "nhu mot cau tra loi — va cong nay tung cho no qua."))
        ra.append(("   ", "Do duoc ngay 2026-09-17, ngay sau khi giao --tiep."))
        return 1, ra

    ten = dang_lam[0]
    if khong_dau(than).find(khong_dau(ten).strip()) < 0:
        ra.append(("HONG", "'Viec tiep theo' khong nhac giai doan dang lam"))
        ra.append(("   ", "   dang lam: %s" % ten[:56]))
        ra.append(("   ", "Moi muc khac trong file trang thai ke chuyen DA xay"))
        ra.append(("   ", "ra, nen cu di thi doc ra duoc. Muc nay ke chuyen SAP"))
        ra.append(("   ", "LAM — no cu di ma van doc len nhu mot ke hoach."))
        return 1, ra

    ra.append(("ok", "Viec ke tiep: %s" % tr["viec"][:54]))
    if _da_tra_loi(tr.get("cho ai", "")):
        ra.append(("  ", "   cho: %s" % tr["cho ai"][:56]))
    return 0, ra


cong_viec_tiep.mo_ta = "Viec tiep theo con dung giai doan"
cong_viec_tiep.chung_minh = "muc 'viec tiep theo' co mot dong VIEC: da tra loi, VA co goi ten giai doan dang lam"
cong_viec_tiep.khong_chung_minh = "nhung viec ke trong do DANG lam, hay du, hay xep dung thu tu. No doi chieu hai file, khong doc duoc y dinh."


def _pha_viec_tiep(goc):
    """Doi muc 'viec tiep theo' sang mot noi dung khong lien quan giai doan."""
    for ten in ("STATE.md", os.path.join("docs", "STATE.md")):
        duong = os.path.join(goc, ten)
        if not os.path.exists(duong):
            continue
        t = doc(duong)
        ra, dang = [], False
        for d in t.splitlines():
            if d.startswith("## "):
                if dang:
                    dang = False
                elif any(khong_dau(d[3:]).strip().startswith(x)
                         for x in TIEU_DE_VIEC_TIEP):
                    ra.append(d)
                    ra.append("")
                    ra.append("Mot viec khong lien quan gi toi giai doan dang lam.")
                    ra.append("")
                    dang = True
                    continue
            if dang:
                continue
            ra.append(d)
        io.open(duong, "w", encoding="utf-8", newline="").write(NL.join(ra) + NL)
        return


cong_viec_tiep.pha = _pha_viec_tiep


# So lan tro len thi doi phai goi lai. Luat nay da nam san trong mau AGENTS.md
# ("nhung thu ban da phai nhac lai TU BA LAN TRO LEN"); o day no thanh mot con
# so may doc duoc.
NGUONG_LAP_LAI = 3


def cong_lap_lai(goc):
    """Viec da lam tu ba lan tro len ma chua duoc goi lai thanh cai gi.

    Duoi ba lan thi ban chua biet phan nao that su lap; goi som thi goi nham.
    Tu ba lan tro len thi cai gia cua viec KHONG goi bat dau lon hon.

    Vi sao phai co cho ghi: khong ai nho minh da lam mot viec may lan. Lan thu
    sau van thay nhu lan thu nhat — hoi lau mot chut, nhung khong du kho de
    dung lai ma nghi.
    """
    ra = []
    f = tim_tep(goc, "LAP-LAI.md", "docs/LAP-LAI.md")
    if not f:
        ra.append(("--", "Khong co so viec lap lai — bo qua cong nay"))
        ra.append(("  ", "Can no lan thu hai ban lam lai mot viec. Tao san:"))
        ra.append(("  ", "  python kit/khoi-tao.py ."))
        return 0, ra

    muc = [(k, v) for k, v in _muc_truong(doc(f))
           if not k.startswith("<") and v]
    if not muc:
        ra.append(("--", "So viec lap lai chua co muc nao — chua co gi de kiem"))
        ra.append(("  ", "Do KHONG phai 'khong co viec nao lap'. Cong nay doc"))
        ra.append(("  ", "file, no khong nhin duoc ban dang lam gi."))
        return 0, ra

    hong, tong = [], 0
    for ten, tr in muc:
        m = re.search(r"(\d+)", tr.get("da lam", ""))
        if not m:
            continue
        lan = int(m.group(1))
        tong += 1
        if lan < NGUONG_LAP_LAI:
            continue
        if not _da_tra_loi(tr.get("goi thanh", "")):
            hong.append((ten if len(ten) <= 46 else ten[:43] + "...", lan))

    if hong:
        ra.append(("HONG", "%d viec da lam tu %d lan tro len ma chua goi lai"
                   % (len(hong), NGUONG_LAP_LAI)))
        for ten, lan in hong[:6]:
            ra.append(("   ", "   %-46s %d lan" % (ten, lan)))
        ra.append(("   ", "Lam mot viec ba lan bang tay thi lan thu tu cung se"))
        ra.append(("   ", "bang tay, va lan nao cung co the sai mot kieu khac."))
        return 1, ra

    ra.append(("ok", "%s: %d viec co ghi so lan, khong cai nao qua nguong ma"
               " chua goi lai" % (ngan(goc, f), tong)))
    return 0, ra


cong_lap_lai.mo_ta = "Viec lap lai da duoc goi lai"
cong_lap_lai.chung_minh = "moi viec ghi tu %d lan tro len deu co dong GOI THANH" % NGUONG_LAP_LAI
cong_lap_lai.khong_chung_minh = "ban da ghi DU nhung viec dang lap. Mot viec lam nam lan ma khong ai ghi vao day thi cong nay khong thay — va do dung la truong hop hay xay ra nhat."


def _pha_lap_lai(goc):
    """Gieo mot viec da lam nhieu lan ma chua goi lai."""
    muc = (NL + "## Chep tay ba file sang mot kho khac" + NL + NL
           + "DA LAM:    6 lan" + NL
           + "MOI LAN:   ba lenh cp, roi mot lan commit" + NL)
    for ten in ("LAP-LAI.md", os.path.join("docs", "LAP-LAI.md")):
        duong = os.path.join(goc, ten)
        if os.path.exists(duong):
            io.open(duong, "a", encoding="utf-8", newline="").write(muc)
            return
    io.open(os.path.join(goc, "LAP-LAI.md"), "w", encoding="utf-8",
            newline="").write("# Viec lap lai" + NL + muc)


cong_lap_lai.pha = _pha_lap_lai


# Dong khai bao ha tang, moi dong: ha-tang <ten><2 dau cach><lenh chung minh>
TIEN_TO_HA_TANG = "ha-tang "
GIAY_CHO_LENH = 60


def cong_ha_tang(goc):
    """Thu can co de lam duoc viec o day — kiem bang cach CHAY, khong bang doc.

    Thu tu cac dong cung la thu tu dung len: cai o tren can co truoc.

    Cong nay chay lenh lay tu mot file trong kho. Do la ly do no mac dinh bi bo
    qua va phai bat bang tay — va la ly do no in tung lenh ra truoc khi chay.
    """
    import subprocess
    ra = []
    f = tim_tep(goc, TEP_PHU_THUOC, "docs/" + TEP_PHU_THUOC)
    cap = []
    if f:
        for d in doc(f).splitlines():
            d = d.strip()
            if d.lower().startswith(TIEN_TO_HA_TANG):
                phan = re.split(r"\s{2,}|\t",
                                d[len(TIEN_TO_HA_TANG):].strip(), 1)
                if len(phan) == 2:
                    cap.append((phan[0].strip(), phan[1].strip()))
    if not cap:
        ra.append(("--", "Khong khai bao ha tang nao — bo qua cong nay"))
        ra.append(("  ", "Can no lan dau ban dung du an nay tren mot may khac."))
        ra.append(("  ", "Khai bao trong %s, moi dong mot thu, XEP THEO THU TU"
                   % TEP_PHU_THUOC))
        ra.append(("  ", "phai dung len truoc:"))
        ra.append(("  ", "  ha-tang git<hai dau cach>git --version"))
        return 0, ra

    hong = 0
    for ten, lenh in cap:
        ra.append(("  ", "  $ %s" % lenh[:64]))
        try:
            p = subprocess.run(lenh, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               timeout=GIAY_CHO_LENH)
            ma = p.returncode
            loi = ""
        except subprocess.TimeoutExpired:
            ma, loi = 1, "qua %d giay" % GIAY_CHO_LENH
        except Exception as e:
            ma, loi = 1, type(e).__name__
        if ma == 0:
            ra.append(("ok", "%-28s dung duoc" % ten))
        else:
            ra.append(("HONG", "%-28s KHONG dung duoc %s" % (ten, loi)))
            hong += 1
    if hong:
        ra.append(("   ", "Thieu mot thu trong day nay thi may nay khong lam"))
        ra.append(("   ", "duoc viec cua du an — du moi file trong kho deu du."))
    return (1 if hong else 0), ra


cong_ha_tang.mo_ta = "Ha tang du an dung duoc tren may nay"
cong_ha_tang.can_lenh = True
cong_ha_tang.chung_minh = "tung lenh DA KHAI BAO chay xong va thoat 0 tren chinh may dang chay"
cong_ha_tang.khong_chung_minh = "tai khoan phia sau cong cu do con song, con quyen, hay con han. `wrangler --version` tra loi khong co nghia la ban deploy duoc. Va no chi biet nhung thu BAN DA KHAI — cai ban quen khai thi no khong thay."


def _pha_ha_tang(goc):
    """Gieo mot dong ha-tang tro toi mot lenh khong he ton tai."""
    dong = (NL + "ha-tang cong cu khong he ton tai  "
            "lenh-khong-he-ton-tai-9k2x --version" + NL)
    for ten in (TEP_PHU_THUOC, os.path.join("docs", TEP_PHU_THUOC)):
        duong = os.path.join(goc, ten)
        if os.path.exists(duong):
            io.open(duong, "a", encoding="utf-8", newline="").write(dong)
            return
    io.open(os.path.join(goc, TEP_PHU_THUOC), "w", encoding="utf-8",
            newline="").write(dong)


cong_ha_tang.pha = _pha_ha_tang


# Cac tieu de duoc coi la "so no" cua file trang thai.
TIEU_DE_NO = ("known debt", "so no", "no da biet", "da biet nhung chua sua",
              "no")
# Moi dong no song phai mang: soi <ngay>  va  lai <ngay>
MAU_SOI = re.compile(r"\bsoi\s+(\d{4}-\d{2}-\d{2})")
MAU_LAI = re.compile(r"\blai\s+(\d{4}-\d{2}-\d{2})")


def cong_no_cu(goc):
    """Dong no nao qua han soi lai, hoac chua bao gio khai la soi luc nao.

    Mot dong no la mot loi khai ve HIEN TAI, viet o thi qua khu. Khong co gi
    buoc ai doc lai no, nen no gia di ma van doc len nhu hien trang — va nguoi
    doc di sua mot thu da duoc sua roi.

    Cong nay chi biet DA BAO LAU KHONG AI SOI. No khong biet mon do con that
    hay khong; may khong doc duoc y nghia, va mot cong hua dieu do se duoc
    thoa man bang mot cau nghe cho xuoi.
    """
    ra = []
    f = tim_tep(goc, "STATE.md", "docs/STATE.md", "TRANG-THAI.md")
    if not f:
        ra.append(("--", "Khong co file trang thai — bo qua cong nay"))
        return 0, ra

    than = _muc_theo_tieu_de(doc(f), TIEU_DE_NO)
    if than is None:
        ra.append(("--", "File trang thai khong co muc so no — bo qua"))
        ra.append(("  ", "Them mot muc '## Da biet nhung chua sua'. Khong co no"))
        ra.append(("  ", "thi mon no nam trong dau nguoi, va dau nguoi thi im."))
        return 0, ra

    hom_nay = time.strftime("%Y-%m-%d")
    song, thieu, qua = 0, [], []
    for d in than.splitlines():
        d = d.strip()
        if not d.startswith("- "):
            continue
        noi = d[2:].strip()
        if noi.startswith("~~") or noi.startswith("<"):
            continue                      # da dong, hoac con la cho trong
        song += 1
        kd = khong_dau(noi)
        m_soi, m_lai = MAU_SOI.search(kd), MAU_LAI.search(kd)
        ten = noi[:44] + ("..." if len(noi) > 44 else "")
        if not m_soi or not m_lai:
            thieu.append(ten)
        elif m_lai.group(1) < hom_nay:
            qua.append((ten, m_lai.group(1)))

    if not song:
        ra.append(("--", "So no khong con mon nao dang mo — chua co gi de kiem"))
        return 0, ra

    if thieu or qua:
        ra.append(("HONG", "%d/%d mon no khong con noi duoc no con dung hay khong"
                   % (len(thieu) + len(qua), song)))
        for t in thieu[:4]:
            ra.append(("   ", "   thieu moc:  %s" % t))
        for t, h in qua[:4]:
            ra.append(("   ", "   qua han %s:  %s" % (h, t)))
        ra.append(("   ", "Ba lan lien tiep ngay 2026-09-17, mot dong no doc len"))
        ra.append(("   ", "nhu hien trang trong khi mon do da xong tu truoc."))
        ra.append(("   ", "Moi dong con mo phai mang: soi <ngay>  va  lai <ngay>"))
        return 1, ra

    ra.append(("ok", "%s: %d mon no dang mo, deu con trong han soi lai"
               % (ngan(goc, f), song)))
    return 0, ra


cong_no_cu.mo_ta = "So no khong tu gia di trong im lang"
cong_no_cu.chung_minh = "moi mon no DANG MO co ghi soi lan cuoi va han soi lai, va chua qua han"
cong_no_cu.khong_chung_minh = "mon no do CON THAT hay da duoc sua tu luc nao. May khong doc duoc y nghia — no chi dem ngay. Va no chi thay nhung mon BAN DA GHI RA."


def _pha_no_cu(goc):
    """Gieo mot dong no co han soi lai da qua."""
    for ten in ("STATE.md", os.path.join("docs", "STATE.md")):
        duong = os.path.join(goc, ten)
        if not os.path.exists(duong):
            continue
        t = doc(duong)
        than = _muc_theo_tieu_de(t, TIEU_DE_NO)
        if than is None:
            continue
        dong = None
        for d in than.splitlines():
            if d.strip().startswith("- "):
                dong = d
                break
        moi = "- Mon gieo vao de thu cong (soi 2020-01-01, lai 2020-06-01)"
        if dong is None:
            continue
        io.open(duong, "w", encoding="utf-8", newline="").write(
            t.replace(dong, dong + NL + moi, 1))
        return


cong_no_cu.pha = _pha_no_cu


# O "da dien tap" ghi NGAY da thu that, hoac "chua". Dem theo ngay.
MAU_NGAY = re.compile(r"\d{4}-\d{2}-\d{2}")


def cong_khi_hong(goc):
    """Hong roi thi lam gi — co viet ra khong, va co phai mot BUOC khong.

    `RUI-RO.md` tra loi "cai gi co the hong". Cong nay hoi cau dung sau do. Mot
    so rui ro day du ma khong co trang tra loi thi doc len van yen tam, va do la
    kieu yen tam dat nhat.

    Dung lai CO_BAO_RONG cua cong rui ro: "de y", "theo doi", "xem xet" la y
    dinh chu khong phai mot buoc — du no dung o o co bao hay o o lui ve.
    """
    ra = []
    f = tim_tep(goc, "KHI-HONG.md", "docs/KHI-HONG.md")
    if not f:
        ra.append(("--", "Khong co trang 'khi hong thi lam gi' — bo qua cong nay"))
        ra.append(("  ", "Can no khi du an co thu hong that thi dau. So rui ro"))
        ra.append(("  ", "noi cai gi co the hong; cho nay noi luc do lam gi."))
        return 0, ra

    muc = [(k, v) for k, v in _muc_truong(doc(f))
           if not k.startswith("<") and v]
    if not muc:
        ra.append(("--", "Trang 'khi hong' chua co muc nao — chua co gi de kiem"))
        ra.append(("  ", "Do KHONG phai 'khong co gi hong duoc'."))
        return 0, ra

    DOI = (("dau hieu", "nhin vao dau thi biet"),
           ("cat mau", "viec dau tien de no thoi hong them"),
           ("lui ve", "lui ve dau, bang cach nao"),
           ("xong khi", "nhin vao dau de biet da ve binh thuong"))
    hong, dien_tap = [], 0
    for ten, tr in muc:
        ng = ten if len(ten) <= 40 else ten[:37] + "..."
        for kh, _y in DOI:
            v = tr.get(kh, "")
            if not _da_tra_loi(v):
                hong.append((ng, kh, "bo trong"))
                continue
            gon = khong_dau(v).strip().strip("<>").strip("*` ").strip()
            if any(x in gon for x in CO_BAO_RONG):
                hong.append((ng, kh, "moi la mot y dinh"))
        # Dem theo NGAY, khong theo "o co chu". _da_tra_loi() nhan moi chu
        # khong phai cho giu cho, nen "chua — nhung ..." duoc dem la DA dien
        # tap. Do duoc 2026-09-17: cong in 3/4 trong khi so dung la 2/4.
        if MAU_NGAY.search(tr.get("da dien tap", "")):
            dien_tap += 1

    if hong:
        ra.append(("HONG", "%d o chua tra loi duoc, tren %d thu da ghi"
                   % (len(hong), len(muc))))
        for ng, kh, vi in hong[:6]:
            ra.append(("   ", "   %-40s %s: %s" % (ng, kh.upper(), vi)))
        ra.append(("   ", "Mot quy trinh lui viet bang 'xem xet' thi luc cham"))
        ra.append(("   ", "vao khong ai biet phai go gi."))
        return 1, ra

    # ---- noi voi so rui ro: moi rui ro DANG MO phai co mot cau tra loi
    ten_muc = [khong_dau(k) for k, _v in muc]
    thieu, lac = [], []
    fr = tim_tep(goc, "RUI-RO.md", "docs/RUI-RO.md", "RISKS.md",
                 "docs/RISKS.md")
    co_cot = False
    if fr:
        dong = [d for d in doc(fr).splitlines() if d.strip().startswith("|")]
        hang = [d for d in dong
                if not re.match(r"^\|[\s:|-]+\|$", d.strip())]
        if hang:
            co_cot = len([x for x in hang[0].strip().strip("|").split("|")]) >= 6
        for h in hang[1:] if co_cot else []:
            o = [x.strip() for x in h.strip().strip("|").split("|")]
            if len(o) < 6 or not o[0] or o[0].startswith("<"):
                continue
            if "DANG MO" not in o[4].upper() and "OPEN" not in o[4].upper():
                continue
            tl = o[5].strip().strip("*` ").strip()
            ng = o[0][:44]
            if not _da_tra_loi(tl):
                thieu.append(ng)
                continue
            g = khong_dau(tl)
            if g.startswith("khong can") or g.startswith("khong co"):
                continue          # da quyet dinh, va da ghi ly do ngay o do
            if not any(g in x or x in g for x in ten_muc):
                lac.append((ng, tl[:34]))

    if thieu or lac:
        ra.append(("HONG", "%d rui ro dang mo chua noi duoc voi mot loi lui"
                   % (len(thieu) + len(lac))))
        for ng in thieu[:4]:
            ra.append(("   ", "   o 'khi hong' de trong:  %s" % ng))
        for ng, tl in lac[:4]:
            ra.append(("   ", "   tro toi muc khong co:    %s -> %r" % (ng, tl)))
        ra.append(("   ", "So rui ro noi CAI GI CO THE HONG. Cot nay doi mot"))
        ra.append(("   ", "cau tra loi cho cau dung sau do — ke ca cau"))
        ra.append(("   ", "'khong can, vi ...'. Bo trong thi moi noi chi nam"))
        ra.append(("   ", "trong dau nguoi doc."))
        return 1, ra

    ra.append(("ok", "%s: %d thu da ghi, bon o deu tra loi duoc"
               % (ngan(goc, f), len(muc))))
    if fr and not co_cot:
        ra.append(("  ", "   so rui ro chua co cot 'Khi hong' — chua doi chieu"))
        ra.append(("  ", "   duoc hai file. Them mot cot thu sau vao cuoi bang."))
    ra.append(("  ", "   da dien tap that: %d/%d (dem theo NGAY ghi trong o) —"
               " con so nay KHONG lam cong do" % (dien_tap, len(muc))))
    return 0, ra


cong_khi_hong.mo_ta = "Hong roi thi biet lam gi"
cong_khi_hong.chung_minh = "moi thu da ghi deu co dau hieu, buoc cat mau, cho lui ve va dieu kien xong, khong o nao chi la mot y dinh; VA moi rui ro dang mo trong so rui ro deu tra loi duoc cot 'khi hong' — tro toi mot muc co that, hoac ghi 'khong can, vi ...'"
cong_khi_hong.khong_chung_minh = "quy trinh do CHAY DUOC. May doc duoc chu, khong biet lenh lui kia con dung hay khong — o DA DIEN TAP duoc dem va in ra chinh vi the, va no KHONG lam cong do. Va no chi thay nhung thu BAN DA GHI."


def _pha_khi_hong(goc):
    """Gieo mot thu co the hong ma o lui ve chi la mot y dinh."""
    muc = (NL + "## Thu gieo vao de thu cong" + NL + NL
           + "DAU HIEU:     trang bao loi 500" + NL
           + "CAT MAU:      tat dich vu" + NL
           + "LUI VE:       theo doi roi tinh sau" + NL
           + "XONG KHI:     trang tra ve 200" + NL
           + "DA DIEN TAP:  chua" + NL)
    for ten in ("KHI-HONG.md", os.path.join("docs", "KHI-HONG.md")):
        duong = os.path.join(goc, ten)
        if os.path.exists(duong):
            io.open(duong, "a", encoding="utf-8", newline="").write(muc)
            return
    io.open(os.path.join(goc, "KHI-HONG.md"), "w", encoding="utf-8",
            newline="").write("# Khi hong thi lam gi" + NL + muc)


cong_khi_hong.pha = _pha_khi_hong


# ==================================================================== danh sach
CAC_CONG = [
    cong_trang_thai,
    cong_gia_dinh,
    cong_lenh_tai_lieu,
    cong_bi_mat,
    cong_vong_doi,
    cong_trang_thai_ten,
    cong_rui_ro,
    cong_khi_hong,
    cong_cho_dua,
    cong_ban_do,
    cong_nhat_ky,
    cong_quy_uoc,
    cong_da_tra,
    cong_ket_noi,
    cong_giai_doan,
    cong_viec_tiep,
    cong_lap_lai,
    cong_no_cu,
    cong_ngan_sach,
    cong_phu_thuoc,
    cong_ten_mien,
    cong_ban_sao,
    cong_ha_tang,
]


# ======================================================================== tiep
# Cau de dan vao mot cua so chat moi, thay cho chu "tiep". Ngan, va khong dua
# vao tri nho hoi thoai — cua so moi thi tri nho do bang khong.
CAU_MO_PHIEN = (
    "Chay `python kit/cong.py --tiep` trong kho nay, doc ket qua, roi lam tiep"
    " dung viec no chi ra. Dung dua vao tri nho chat; kho la tri nho."
)


def _giai_tiep(goc):
    """Tra ve (ma thoat, cac dong) — dang o dau, sap lam gi, cai gi dang chan."""
    ra = []
    fg = tim_tep(goc, "GIAI-DOAN.md", "docs/GIAI-DOAN.md")
    fs = tim_tep(goc, "STATE.md", "docs/STATE.md", "TRANG-THAI.md")

    # ---- dang o dau
    ra.append(("", "== DANG O DAU =="))
    if not fg:
        ra.append(("!", "Khong co day giai doan. Chua co gi de noi 'tiep' vao."))
        ra.append((" ", "  python kit/khoi-tao.py ."))
        return 1, ra

    muc = [(k, v) for k, v in _muc_truong(doc(fg))
           if not k.startswith("<") and v]
    dem = {x: 0 for x in TRANG_THAI_GIAI_DOAN}
    dang_lam = []
    for ten, tr in muc:
        x = khop_ten(tr.get("trang thai", ""), TRANG_THAI_GIAI_DOAN)
        if x:
            dem[x] += 1
        if x == "dang lam":
            dang_lam.append((ten, tr))
    ra.append((" ", "  %s: %d xong / %d dang lam / %d chua toi"
               % (ngan(goc, fg), dem["xong"], dem["dang lam"],
                  dem["chua toi"])))

    if len(dang_lam) != 1:
        ra.append(("!", "Co %d giai doan 'dang lam'. Phai co dung mot."
                   % len(dang_lam)))
        ra.append((" ", "  Khong mot thi 'tiep' tro vao cho nao cung duoc, va"))
        ra.append((" ", "  lan nao cung ra mot cho khac."))
        return 1, ra

    ten, tr = dang_lam[0]
    ra.append((" ", "  Giai doan: %s" % ten[:60]))
    thoat = tr.get("thoat khi", "")
    if _da_tra_loi(thoat):
        ra.append((" ", "  Thoat khi: %s" % _bo_xuong_dong(thoat)[:60]))
    else:
        ra.append(("!", "  Giai doan nay chua co dieu kien thoat do duoc."))

    # ---- sap lam gi
    ra.append(("", ""))
    ra.append(("", "== VIEC KE TIEP =="))
    than = _muc_theo_tieu_de(doc(fs), TIEU_DE_VIEC_TIEP) if fs else None
    if not than or than.startswith("<"):
        ra.append(("!", "File trang thai khong ke ra viec sap lam."))
        ra.append((" ", "  Them mot muc '## Viec tiep theo' vao %s."
                   % (ngan(goc, fs) if fs else "file trang thai")))
        ra.append((" ", "  Khong co no thi 'tiep' khong giai ra duoc gi — va"))
        ra.append((" ", "  doan bua thi nghe van xuoi."))
        return 1, ra
    tr = _truong_trong(than)
    if not _da_tra_loi(tr.get("viec", "")):
        ra.append(("!", "Khong co viec nao duoc goi ten."))
        ra.append((" ", "  Them vao muc do mot dong:  VIEC: <mot viec>"))
        ra.append((" ", "  Muc do co the dai va doc rat xuoi ma van khong ke ra"))
        ra.append((" ", "  viec nao — vi du khi moi dong deu da 'Xong'. Do dung"))
        ra.append((" ", "  la truong hop cho nay tung cho qua."))
        return 1, ra

    ra.append((" ", "  VIEC:   %s" % tr["viec"][:66]))
    if _da_tra_loi(tr.get("cho ai", "")):
        ra.append((" ", "  CHO AI: %s" % tr["cho ai"][:66]))
    ra.append((" ", ""))
    dong = [d.rstrip() for d in than.splitlines()
            if d.strip() and not MAU_TRUONG.match(d)]
    for d in dong[:12]:
        ra.append((" ", "  " + d[:74]))
    if len(dong) > 12:
        ra.append((" ", "  ... con %d dong, doc %s"
                   % (len(dong) - 12, ngan(goc, fs))))

    # ---- cai gi dang chan
    ra.append(("", ""))
    ra.append(("", "== CO GI DANG CHAN KHONG =="))
    do = []
    for c in CAC_CONG:
        if getattr(c, "can_mang", False) or getattr(c, "can_lenh", False):
            continue
        try:
            ma, _ = c(goc)
        except Exception as e:
            do.append("%s (cong nay loi: %s)" % (c.mo_ta, type(e).__name__))
            continue
        if ma:
            do.append(c.mo_ta)
    if do:
        ra.append(("!", "%d cong dang bao hong — sua truoc khi lam viec moi:"
                   % len(do)))
        for x in do:
            ra.append((" ", "  - " + x))
    else:
        ra.append((" ", "  Cac cong chay khong can mang deu khong bao hong."))
        ra.append((" ", "  Chua chay o day: python kit/cong.py --ngoai"
                   " --ha-tang"))

    # ---- cau de mo phien moi
    ra.append(("", ""))
    ra.append(("", "== DAN CAU NAY VAO MOT CHAT MOI =="))
    ra.append((" ", "  " + CAU_MO_PHIEN))
    return 0, ra


def tiep():
    goc = GOC
    print()
    print("  " + "=" * 68)
    print("  cong.py %s — 'tiep' nghia la gi o kho nay" % PHIEN_BAN)
    print("  Thu muc: %s" % goc)
    print("  " + "=" * 68)
    print()
    ma, dong = _giai_tiep(goc)
    for nhan, noi in dong:
        print("  %-1s %s" % (nhan, noi) if nhan else "  %s" % noi)
    print()
    print("  " + "-" * 68)
    if ma:
        print("  KHONG giai duoc chu 'tiep'. Doc cac dong co dau ! o tren.")
        print("  Mot chu 'tiep' giai ra con so khong phai cau tra loi — no chi")
        print("  doc len giong mot cau tra loi.")
    else:
        print("  Cho nay KHONG chung minh viec ke tiep la viec DUNG nen lam.")
        print("  No doc hai file va cac cong. Thu tu uu tien la cua nguoi.")
    print("  " + "-" * 68)
    return ma


# ======================================================================== chay
def chay_het(goc, co_mang=False, im=False, co_lenh=False, chi_kho=False,
             dem=None):
    """Chay cac cong. `dem` la mot dict de nhan lai so lieu, hoac None.

    `dem` tach hai thu ma mat thuong doc len y het nhau: cong DA NHIN THAY mot
    thu roi bao dat, va cong KHONG CO GI de nhin. Ca hai deu in chu "ok".
    """
    tong = 0
    da_nhin = chua_co = 0
    for c in CAC_CONG:
        if chi_kho and not getattr(c, "nhin_kho", False):
            continue
        if getattr(c, "can_mang", False) and not co_mang:
            if not im:
                print()
                print("  [ bo qua ] %s  (can mang: them --ngoai)" % c.mo_ta)
            continue
        if getattr(c, "can_lenh", False) and not co_lenh:
            if not im:
                print()
                print("  [ bo qua ] %s  (chay lenh: them --ha-tang)" % c.mo_ta)
            continue
        ma, dong = c(goc)
        tong = max(tong, ma)
        # Cong IM khi trong toan bo dong ra KHONG co dong nao mang nhan "ok".
        #
        # Luat dau tien viet la "dong dau mang nhan --", va no dem nham: mot
        # cong co the in "--" de KHAI MIEN TRU truoc roi moi in ket qua that.
        # Tren kho goc, "Lenh trong tai lieu chay duoc" bi xep vao nhom im
        # trong khi no vua soi xong mot dong lenh that. Do duoc 2026-09-17.
        if ma == 0 and not any(n.strip() == "ok" for n, _ in dong):
            chua_co += 1
        else:
            da_nhin += 1
        if im:
            continue
        print()
        print("  [ %s ] %s" % ("HONG" if ma else " ok ", c.mo_ta))
        for nhan, noi in dong:
            print("     %-5s %s" % (nhan, noi))
        print("     %-5s chung minh:     %s" % ("", c.chung_minh))
        print("     %-5s KHONG chung minh: %s" % ("", c.khong_chung_minh))
    if dem is not None:
        dem["da nhin"] = da_nhin
        dem["chua co gi"] = chua_co
    return tong


def main():
    co_mang = "--ngoai" in sys.argv
    co_lenh = "--ha-tang" in sys.argv
    chi_kho = "--kho" in sys.argv
    goc = GOC
    print()
    print("  " + "=" * 68)
    print("  cong.py %s — kiem mot du an chay bang AI%s"
          % (PHIEN_BAN, " (chi cac cong NHIN KHO)" if chi_kho else ""))
    print("  Thu muc: %s" % goc)
    print("  " + "=" * 68)

    dem = {}
    ma = chay_het(goc, co_mang, co_lenh=co_lenh, chi_kho=chi_kho, dem=dem)

    print()
    print("  " + "-" * 68)
    if ma:
        print("  CO CONG BAO HONG. Doc phan 'chung minh' cua cong do truoc khi sua.")
    else:
        print("  Moi cong da chay deu khong bao hong.")

    # Con so nay khong lien quan gi toi chuyen co cong do hay khong, nen no
    # nam ngoai ca hai nhanh. Lan dau viet no chi nam trong nhanh "khong hong",
    # va no bien mat dung luc co mot cong do — tuc dung luc nguoi doc dang can
    # biet trong so cong CON LAI co bao nhieu cai that su da nhin.
    chua = dem.get("chua co gi", 0)
    nhin = dem.get("da nhin", 0)
    if chua:
        print()
        print("  Trong so cong vua chay:")
        print("      %2d cong DA NHIN THAY mot thu" % nhin)
        print("      %2d cong KHONG CO GI DE NHIN — file chua co, hoac moi la"
              % chua)
        print("         cho trong <...> chua ai dien")
        print()
        print("  %d cong kia KHONG phai la dat. Chung im lang, va im lang doc"
              % chua)
        print("  len y het dat — do la ly do dong nay ton tai.")
        print("  Moi cong im deu da in mot dong '--' noi no thieu gi.")
    print()
    print("  Day KHONG phai 'du an nay dung'. Moi cong chi nhin dung mot thu,")
    print("  va tung cong da tu khai no khong nhin thay gi.")
    if not chi_kho:
        so_kho = sum(1 for c in CAC_CONG if getattr(c, "nhin_kho", False))
        print()
        print("  Hai loai cong, va chung tra loi hai cau khac nhau:")
        print("    %2d cong NHIN KHO NHU NO DANG LA — chay duoc tren bat ky kho"
              % so_kho)
        print("       nao, ke ca kho chua bao gio nghe ten bo kit nay.")
        print("    %2d cong CANH HO SO do chinh bo kit sinh ra — tren mot kho"
              % (len(CAC_CONG) - so_kho))
        print("       chua nhan kit, chung do 'da nhan kit chua', khong do kho do.")
        print("  Con so do khong phai y kien: do ngay 2026-09-17 tren hai kho")
        print("  that, 13/18 cong that su chay la im lang.")
        print("      python %s --kho     chi chay %d cong loai dau"
              % (os.path.basename(__file__), so_kho))

    print()
    print("  Muon biet cac cong nay co THAT SU truot duoc khong:")
    print("      python %s --tu-kiem" % os.path.basename(__file__))
    print("  Quen dang lam gi, hoac vua mo mot cua so chat moi:")
    print("      python %s --tiep" % os.path.basename(__file__))
    print("  " + "-" * 68)
    return ma


# ===================================================================== tu kiem
def tu_kiem():
    """Chep du an sang thu muc tam, CO Y pha tung thu, doi ket qua phai doi.

    Du an that khong bao gio bi sua.
    """
    co_mang = "--ngoai" in sys.argv
    co_lenh = "--ha-tang" in sys.argv
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
            if getattr(c, "can_lenh", False) and not co_lenh:
                print()
                print("  BO QUA  %-34s (chay lenh: them --ha-tang)" % c.mo_ta)
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
    if "--tu-kiem" in sys.argv:
        sys.exit(tu_kiem())
    elif "--tiep" in sys.argv:
        sys.exit(tiep())
    else:
        sys.exit(main())
