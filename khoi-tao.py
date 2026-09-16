# -*- coding: utf-8 -*-
"""khoi-tao.py — dung bo toi thieu cho mot du an moi.

    python kit/khoi-tao.py <thu-muc>
    python kit/khoi-tao.py <thu-muc> --day-du     them so gia dinh, so seo,
                                                  so rui ro, cho dua

KHONG CAI DAT GI. Thu vien chuan.

NO TAO BAO NHIEU FILE, VA VI SAO IT
-----------------------------------
Ban tieu chuan goc liet ke 25 artifact "gan nhu du an nao cung phai co". Cham
tren du an that da chay 20 ngay, 180 commit va da phat hanh: 12 co, 13 KHONG
BAO GIO duoc tao, du an van chay.

Nen bo nay tao 8 file, va them 6 file neu ban goi --day-du. Them artifact khi
co mot CAU HOI THAT chua co cho tra loi — dung tao truoc roi tim viec cho no.

Co hai thu CO Y KHONG co file rieng: nhat ky thay doi va so bang chung. Ca hai
da co nha roi, la LOI COMMIT — permanent, tim duoc, va dinh dung vao thay doi
sinh ra no. De them hai tai lieu khong ai cap nhat thi te hon.

(Con so o tren tung bi ghi cung va tung sai. Gio no duoc DEM lue chay — xem
bien `da_tao`. Mot con so ghi cung trong tai lieu la mot con so se muc.)

MAU VIET BANG CAU HOI, KHONG PHAI TIEU DE TRONG
-----------------------------------------------
Mot tieu de trong se duoc dien bang thu nghe cho xuoi. Mot cau hoi thi hoac
duoc tra loi, hoac bo trong mot cach nhin thay duoc. Do la khac biet giua mot
tai lieu song va mot tai lieu de cho co.

Moi thu in ra deu la ASCII, vi console Windows la cp1252.
"""
import io
import os
import subprocess
import sys
import datetime

# Phien ban cua bo kit. Ban da chep file nay vao du an cua ban, nen no
# khong tu cap nhat — con so nay la cach duy nhat biet ban dang giu ban nao.
# Thay doi giua cac ban: CHANGELOG.md trong kho pos-kit.
PHIEN_BAN = "1.0.0"

HOM_NAY = datetime.date.today().isoformat()

# ---------------------------------------------------------------- noi dung mau
PROJECT = """# {ten}

> File nay tra loi: **du an nay la gi, va KHONG lam gi?**
> Doi hiem. Neu no doi moi tuan thi no khong con dinh huong duoc gi.

## Du an nay ton tai de lam gi

<Mot cau. Khong phai "xay mot he thong X" — la "de <ai do> lam duoc <viec gi>".>

## Ai dung no

<Ai that su ngoi truoc no. Neu chua biet, viet "CHUA BIET" — dung doan.>

## Ket qua nao duoc coi la thanh cong

<Phai quan sat duoc. "He thong on" khong dem duoc. "Ban duoc mot don ma ton kho
khong xuong am" thi dem duoc.>

## KHONG phai muc tieu

<Cho nay quan trong hon no trong. Thu ban co y KHONG lam se bi de nghi lai
nhieu lan, va moi lan khong co dong nay thi ban phai cai lai tu dau.>

-

## Rang buoc khong bo qua duoc

<Tien, du lieu ca nhan, phap ly, thoi han, nguoi, thiet bi. Cai gi that su
khong the thuong luong.>

## Ai quyet dieu gi

Khi hai chi dan mau thuan, ben nao thang:

```
1. File nay                        <- cao nhat
2. Quyet dinh da chot (QUYET-DINH/)
3. Ke hoach chang hien tai
4. Chi dan trong mot task
5. De nghi cua AI                  <- thap nhat
```

<Sua thu tu nay neu du an cua ban khac. Nhung PHAI co mot thu tu — khong co thi
moi mau thuan lai thanh mot cuoc tranh luan moi.>
"""

STATE = """# Trang thai

> File nay tra loi: **dang o dau, va viec ke tiep la gi?**
> Doi gan nhu moi phien. Ai mo du an nay ra deu doc file nay TRUOC.

**Cap nhat lan cuoi:** {ngay}

TRANG THAI: DANG TIM HIEU

<Mot chu, chon DUNG MOT trong tam chu duoi day. Mot chu thi may doc duoc va
nguoi la doc duoc; mot doan van thi khong.

  DANG TIM HIEU   chua chac nen xay gi
  DANG DUNG       da chot huong, dang lam
  DANG KIEM       lam xong roi, dang chung minh no dung
  CHO PHAT HANH   da chung minh, chua dua ra
  DANG CHAY THAT  co nguoi dung that
  DANG GIU        khong them gi moi, chi giu cho chay
  TAM DUNG        co y dung, se quay lai
  DA DONG         khong quay lai nua

Muon hai chu la dau hieu: hoac du an that su co hai luong (noi ra), hoac ban
chua quyet giai doan nay hoi cau gi.>

## Giai doan hien tai

<Giai doan la MOT CAU HOI ban chua tra loi duoc, khong phai mot o trong danh
sach quy trinh. Du an mot cau hoi thi mot giai doan.>

GIAI DOAN: <ten ngan>
THOAT KHI: <mot cau. Phai co SO, hoac co mot NGUOI CU THE lam duoc mot VIEC CU
            THE. "Xong het task" khong dung duoc — task la thu ban chon, muc
            tieu la thu phai thanh that.>

## Dang chay ban nao

<Commit nao dang chay that, o dau. Chua chay o dau thi viet "chua chay o dau ca".

Va mot o rieng, vi no la o hay giet nguoi nhat:
CO DOI GI BANG TAY sau khi dua len khong?  <co / khong / khong nho>

"Co" hoac "khong nho" thi ghi ngay vao muc "Da biet nhung chua sua" ben duoi —
mot lan sua tay khong ghi lai la mot phien ban khong ton tai o dau ca.>

## Dang o dau

<Mot doan. Cai gi vua xong, cai gi dang do.>

## Viec tiep theo

<Mot viec. Neu liet ke bay viec thi khong ai biet lam cai nao truoc.>

## Dang chay the nao

<He thong co dang chay khong, o dau, phien ban nao. Chua co thi viet "chua chay
o dau ca" — do cung la mot cau tra loi.>

## Da biet nhung chua sua

<Mon no. Cai gi dang sai ma minh CHAP NHAN tam. Viet ra day thi no la no; khong
viet ra thi no la mot cai bay co hen gio.>

## Chua chac

<Cho ban dang nghi ngo. Day la dong dat nhat trong ca file, va la dong hay bi bo
nhat: phien sau doc code la suy ra duoc hai muc tren, nhung KHONG suy ra duoc
cho ban dang nghi ngo.>
"""

CLAUDE = """# Lam viec trong du an nay

> File nay tra loi: **lam viec o day theo quy uoc gi?**
> Cong cu AI tu doc file nay moi phien. Viet ngan, viet thu that su can.

## Doc truoc khi lam

1. `PROJECT.md` — du an la gi, khong lam gi
2. `STATE.md` — dang o dau, viec ke tiep

## Bat dau tu thuc te

Kiem nhanh trang thai kho truoc khi lam: nhanh nao, co gi chua commit, co lech
voi ban tren mang khong. Dung lam viec tren mot phien ban nho trong dau.

## Quy uoc cua du an nay

<Viet nhung thu ban da phai nhac lai TU BA LAN TRO LEN. Duoi ba lan thi chua
phai khuon — dung dua vao day voi.>

- <vi du: chi dung thu vien chuan, khong them phu thuoc ngoai>
- <vi du: khong doi file cau hinh>

Moi dong o tren nen co mot dong ly do ngay duoi no. Dong khong co ly do thi
nguoi sau khong dam xoa ma cung khong dam tin — no se nam do mai.

## Bang chung

Truoc khi noi mot viec da xong, hoi mot cau:

> **Neu viec nay hong, thu toi dang nhin co khac di khong?**

Tra loi "khong" thi chua kiem duoc gi ca. Mot bo test xanh ca khi hong, khi da
sua, va khi bi xoa han tinh nang thi no khong noi gi ve viec nay.

## Truoc khi ban giao

```
python kit/cong.py
```

Doc ca dong "KHONG chung minh" cua tung cong. Mot cong xanh chi co nghia la thu
no nhin thi khong hong.

## Khong lam

- Khong commit bi mat that.
- Khong `git reset --hard` de cay cho sach.
- Khong tu doi huong du an; de nghi thi duoc, tu doi thi khong.
"""

QUYET_DINH = """# Quyet dinh

> Thu muc nay tra loi: **da chot gi, va vi sao?**
> Mot file cho mot quyet dinh kho lui. Khong sua file cu — viet file moi noi ro
> no thay the cai nao.

Chi ghi quyet dinh nao dat: kho lui lai, doi huong, hoac se bi hoi lai sau sau
thang. Quyet dinh vat thi khong can file.

Dat ten: `0001-mot-cau-ngan.md`
"""

QD_MAU = """# QD 0001 — <quyet dinh nay la gi, mot cau>

**Ngay:** {ngay}
**Trang thai:** Da chot
**Ai quyet:** <ten>

## Boi canh

<Chuyen gi dan toi cho phai quyet. Viet du de sau sau thang doc lai van hieu ma
khong can hoi ai.>

## Da can nhac gi

<It nhat hai phuong an. Mot quyet dinh chi co mot phuong an thi no khong phai
quyet dinh, no la phan xa.>

## Chot gi

<Noi thang. Khong "co le nen".>

## Bang chung

<Da do gi truoc khi chot? Neu chua do gi, viet "chua do — chot bang phan doan".
Do la mot cau tra loi hop le, va no thanh that hon la bia ra mot ly do.>

## Cho nay con chua chac

<Mot quyet dinh gan nhu khong bao gio dung tren toan su that do duoc. Viet ra
phan CHUA CHAC, thay vi de no lan vao phan tren va doi nhan.

  * do duoc      — mo file ra / chay lenh ra la thay
  * suy ra       — dua tren mot thu do duoc, roi ket luan them. NOI RO cho dua
  * chua kiem    — kiem duoc nhung chua ai kiem -> chep sang GIA-DINH.md, CO HAN
  * khong kiem duoc — mot lua chon, khong co phep thu. Ghi TEN NGUOI CHON

Dong "chua kiem" nao khong sang so gia dinh thi sau nay se tu thanh su that chi
vi no duoc lap lai du nhieu lan.>

## Ke theo sau

<Chon nay khoa lai nhung gi? Sau nay muon doi thi phai lam gi?>
"""

GIA_DINH = """# So gia dinh

> File nay tra loi: **du an dang dua tren nhung dieu gi chua kiem?**

Mot gia dinh khong co han kiem se thanh su that chi vi no duoc lap lai du nhieu
lan. Cot **Han kiem** la cot lam viec cua ca bang nay.

Trang thai: `CHUA-KIEM` · `DA-XAC-NHAN` · `DA-BAC-BO` · `HET-HAN`

| Gia dinh | Tu dau ra | Sai thi hong gi | Kiem bang cach nao | Han kiem | Trang thai |
|---|---|---|---|---|---|
| <vi du: nguoi dung se chap nhan dang nhap bang email> | <phong van 2 nguoi> | <ca luong dang ky phai lam lai> | <hoi 5 nguoi dung that> | {han} | CHUA-KIEM |

⚠️ `python kit/cong.py` se bao hong neu mot gia dinh qua han ma van `CHUA-KIEM`.
Do la chu y: het han mà khong ai kiem thi no khong con la gia dinh nua — no la
mot niem tin.
"""

SO_SEO = """# So seo

> File nay tra loi: **du an nay da tu lua minh nhung lan nao?**

Khong phai de tu trach. De ghi **co che**, vi co che thi lap lai, va cai lap lai
thi hoc duoc.

Ghi khi: mot phep do tra ve dieu ban tin, roi hoa ra no do mot thu khac. Mot ban
va lam cho khac muc di. Mot su co mat nua ngay ma nguyen nhan chi la mot dong.

| Ngay | Do cai gi | May tra ve | Suyt ket luan | That ra |
|---|---|---|---|---|
| {ngay} | <vi du: grep tim mot chuoi> | <0 dong> | <"cho do khong ton tai"> | <chuoi do viet bang chu khac> |

📌 Neu ban ghi duoc ba dong vao bang nay, ban se thay chung khong phai ba loi
khac nhau. Chung la mot co che, xay ra ba lan.
"""

RUI_RO = """# So rui ro

> File nay tra loi: **chuyen gi co the hong, va toi se THAY GI neu no bat dau
> xay ra?**

Cot **Co bao** la cot lam viec cua ca bang. Mot rui ro khong co co bao thi khong
phai rui ro duoc quan — no la mot noi lo. Va mot danh sach toan noi lo thi sau
hai tuan khong ai mo ra nua, vi mo ra cung khong lam duoc gi.

Co bao chinh la phep do cua M7, chia ve phia truoc: *neu chuyen nay bat dau xay
ra, toi se thay gi khac di?*

Trang thai: `DANG MO` · `DA XAY RA` · `HET RUI RO`

| Rui ro | Hong co nao | Lam gi truoc | Co bao | Trang thai |
|---|---|---|---|---|
| <vi du: kho fixture bi doi ten hoac chuyen rieng tu> | <nua phan thuc hanh chet> | <khai bao vao phu-thuoc-ngoai.txt> | <phep kiem goi URL do moi lan chay> | DANG MO |

⚠️ `python kit/cong.py` bao hong neu mot rui ro DANG MO ma o Co bao de trong,
hoac chi ghi mot y dinh ("de y xem", "theo doi").

Dung ghi rui ro cho du. Ghi rui ro co the gay hau qua that. Mot so rui ro lam
cho co thi te hon khong co — no tao cam giac da lo roi.
"""

BAN_DO = """# Ban do he thong

> File nay tra loi: **doi mot cho thi cho nao khac dong theo?**
> No khong phai mot buc tranh. No la mot cong cu de tra loi cau tren.

⚠️ **SAU DONG. Khong hon.** Phep thu: dong file lai, ve lai trong nam phut. Ve
khong noi thi no qua to — ma qua to nghia la ban se khong cap nhat no, va mot
ban do cu con te hon khong co ban do: khong co thi ban di hoi, co ban do sai
thi ban khong hoi ai ca.

## Gom nhung phan nao

<Ke ten, moi phan kem cho no nam. Vi du: "Trang ban hang — `app.py`".>

## Du lieu nam o dau

<Cho dat nhat trong ca file. Code sai thi sua lai; du lieu sai thi KHONG LUI
DUOC. Ke ca file do cong cu tu sinh ra ma ban khong tao.>

## Chung gap nhau o cho nao

<Cho phan nay goi phan kia. Day la cho doi thi ben kia vo — M14 Phan 5b.>

## Ra ngoai o cho nao

<Tro sang `CHO-DUA.md`, dung chep lai. Hai noi khai cung mot su that thi co
ngay hai noi khac nhau.>

## Cho nao hong la ca he thong dung

<Mot cau nay quyet dinh ban lo cho nao truoc.>

## No chay o dau

<May ban / cho thu / cho co nguoi dung that. Cho nao ton tai cung phai noi duoc
no ton tai DE LAM GI.>

---

Nam cau CO Y khong co o day: luong dieu khien, luong su kien, ranh gioi tin cay,
luoc do API, diem hong theo tang. Chung deu dung — va deu la cau cua mot he
thong DA CO nhung thu do. Them mot dong khi du an moc them mot thu that, khong
phai khi ban doc thay mot danh sach dai hon.
"""

CONG_CU = """# Cho dua

> File nay tra loi: **du an nay dang dua vao nhung gi ben ngoai chinh no?**

Thu chay tot thi thoi duoc nhin thay. Ban nho nhung thu gay phien; ban quen
nhung thu im lang lam viec — va do dung la nhung thu khi chet se gay nhieu phien
nhat.

Cai khong ai viet ra thi khong phep kiem nao nhin toi. Khi no chet, MOI CONG
TRONG NHA VAN XANH HET.

| Cho dua | Dung de lam gi | No chet thi mat gi | Ai giu / het han khi nao |
|---|---|---|---|
| <vi du: github.com/<ai do>/<kho>> | <moi bai lab clone tu day> | <nua phan thuc hanh> | <tai khoan ca nhan> |

## Cho hay bi bo sot

Khong phai danh sach cong cu — la danh sach CHO DUA:

- kho ma ban clone tu do;
- may chu, ten mien, chung chi;
- noi du lieu that nam, va ai sao luu no;
- thu goi ra ngoai: ban do, gui tin, thanh toan;
- thu NAP LUC CHAY: thu vien tai tu CDN khi nguoi dung mo trang;
- tai khoan va khoa: ai dang giu, het han khi nao.

📌 URL nao chiu luc that thi khai bao them vao `phu-thuoc-ngoai.txt` de
`python kit/cong.py --ngoai` goi that ra kiem, thay vi chi ghi ra day.
"""


VIEC = """# <ten viec, mot cau>

> Dien TRUOC khi go chu dau tien. To giay nay di het mot viec tu dau den cuoi.
> Viec xong thi o 5 di vao STATE / QUYET-DINH, con to nay thanh ho so.

## 1. Muc tieu — cai gi phai DUNG khi xong

<Khong phai "lam cai gi". La "cai gi thanh that".
Phep thu: doc len roi hoi "ai do lam xong thi toi kiem bang cach nao?">

## 2. Ranh gioi — cai gi KHONG duoc doi

<Cho nao dang chay tot? Du lieu nao khong duoc mat? Quyet dinh nao da chot roi?>

## 3. Bang chung — nhin vao dau de biet la xong

**Dien o nay TRUOC KHI bat dau.**

Phep do: *neu viec nay hong, thu toi dinh nhin co khac di khong?*

```
Truoc khi sua:  <so that, do duoc>
Sau khi sua:    <phai ra gi>
```

<O nay kho dien la TIN HIEU, khong phai chuong ngai. Kho dien nghia la ban chua
biet minh muon gi — va do la thu dang biet TRUOC khi tieu mot buoi.>

## 4. Luong — may chang, dung o dau

```
Chang 1: <...>   -> <tu di tiep / DUNG, hoi toi>
Chang 2: <...>   -> <...>
```

<Chang nao nang o mot trong bon chieu nay thi dang dung: hau qua lon · kho lui ·
cham tien hoac du lieu ca nhan · sai am tham.>

## 5. Ghi lai — xong roi con lai cai gi

<Phep thu tai hien loi? Mot dong trong QUYET-DINH? Mot dong trong STATE?
Mon no phai ghi o day — no khong duoc viet ra thi no la bay co hen gio.>

-

## Dang dung o dau  <chi dien khi phai dung giua chung>

```
DANG O DAU:  <chang nao, da xong gi>
VUA BIET:    <phat hien gi>
CHUA CHAC:   <cho dang nghi ngo — dong nay phien sau KHONG tu suy ra duoc>
```
"""

PHU_THUOC = """# Phu thuoc ngoai — thu du an nay dua vao ma nam ngoai tam tay
#
# Moi dong: <url><hai dau cach><vai tro cua no>
# Dong bat dau bang # la ghi chu.
#
# Vi sao co file nay: cai gi khong cong nao nhin toi thi khi no chet, moi cong
# trong nha van xanh het. Do dung la kieu hong im lang.
#
# Kiem:  python kit/cong.py --ngoai

# https://github.com/<ai do>/<kho gi do>  kho ma du an nay clone tu day
"""

README_KIT = """# Bat dau

Du an nay dung bo cong cua Project Operating System.

## Doc theo thu tu nay

1. `PROJECT.md` — du an la gi, va KHONG lam gi
2. `STATE.md` — dang o dau, viec ke tiep la gi
3. `CLAUDE.md` — lam viec o day theo quy uoc gi

## Truoc khi ban giao bat cu viec gi

```
python kit/cong.py
```

Doc ca dong "KHONG chung minh" cua tung cong. Mot cong bao xanh chi co nghia la
thu no nhin thi khong hong — khong co nghia la du an dung.

## Muon biet cac cong do co that su truot duoc khong

```
python kit/cong.py --tu-kiem
```

No chep du an sang thu muc tam, co y pha tung thu, va doi hoi ket qua phai doi.
Du an that khong bi dong toi.

Mot phep kiem chua bao gio bao do thi ban chua biet no bao do duoc khong.
"""


def viet(goc, ten, noi_dung):
    p = os.path.join(goc, ten)
    if os.path.exists(p):
        print("  bo qua (da co)  %s" % ten)
        return False
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    io.open(p, "w", encoding="utf-8", newline="").write(noi_dung)
    print("  tao             %s" % ten)
    return True


def main():
    dung = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not dung:
        print(__doc__)
        return 2
    goc = os.path.abspath(dung[0])
    day_du = "--day-du" in sys.argv
    ten = os.path.basename(goc.rstrip(os.sep)) or "du-an"
    han = (datetime.date.today() + datetime.timedelta(days=14)).isoformat()

    os.makedirs(goc, exist_ok=True)
    print()
    print("  Khoi tao: %s" % goc)
    print()

    # Dem THAT, khong ghi cung. Ban dau file nay in ra mot con so ghi cung
    # va no sai ngay lan chay dau — dung cai ho loi ma chinh bo cong nay bat.
    da_tao = 0
    da_tao += viet(goc, "PROJECT.md", PROJECT.format(ten=ten))
    da_tao += viet(goc, "STATE.md", STATE.format(ngay=HOM_NAY))
    da_tao += viet(goc, "CLAUDE.md", CLAUDE)
    da_tao += viet(goc, "QUYET-DINH/README.md", QUYET_DINH)
    da_tao += viet(goc, "QUYET-DINH/0001-mau.md", QD_MAU.format(ngay=HOM_NAY))
    da_tao += viet(goc, "viec/MAU-VIEC.md", VIEC)
    da_tao += viet(goc, "README.md", README_KIT)

    if day_du:
        da_tao += viet(goc, "GIA-DINH.md", GIA_DINH.format(han=han))
        da_tao += viet(goc, "SO-SEO.md", SO_SEO.format(ngay=HOM_NAY))
        da_tao += viet(goc, "RUI-RO.md", RUI_RO)
        da_tao += viet(goc, "CHO-DUA.md", CONG_CU)
        da_tao += viet(goc, "BAN-DO.md", BAN_DO)
        da_tao += viet(goc, "phu-thuoc-ngoai.txt", PHU_THUOC)

    # chep bo cong vao du an moi de no chay duoc doc lap
    nguon = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cong.py")
    dich = os.path.join(goc, "kit", "cong.py")
    if os.path.exists(nguon) and not os.path.exists(dich):
        os.makedirs(os.path.dirname(dich), exist_ok=True)
        io.open(dich, "w", encoding="utf-8", newline="").write(
            io.open(nguon, encoding="utf-8").read())
        print("  tao             kit/cong.py")
        da_tao += 1

    if not os.path.isdir(os.path.join(goc, ".git")):
        try:
            subprocess.run(["git", "init", "-q", "-b", "main"], cwd=goc,
                           capture_output=True)
            print("  tao             .git (nhanh main)")
        except OSError:
            print("  bo qua          .git (khong tim thay git)")

    print()
    print("  " + "-" * 62)
    print("  Xong. %d file. Khong phai 25." % da_tao)
    print()
    print("  Viec dau tien KHONG phai viet code. La dien PROJECT.md —")
    print("  nhat la muc 'KHONG phai muc tieu'. Cho do quan trong hon no trong.")
    print()
    print("  Roi chay:   python kit/cong.py")
    print("  " + "-" * 62)
    return 0


if __name__ == "__main__":
    sys.exit(main())
