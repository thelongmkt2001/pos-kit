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

Nen bo nay tao 17 file, va them 7 file neu ban goi --day-du.

Da co san mot kho dang chay? Dung --kho: no chi tao NHUNG FILE MA CAC CONG
NHIN KHO doi, va khong dung toi file nao ban da co. Them artifact khi
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
PHIEN_BAN = "1.24.3"

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

GIAI DOAN: <ten ngan. Phai KHOP voi giai doan dang lam trong `GIAI-DOAN.md`>
THOAT KHI: <mot cau. Phai co SO, hoac co mot NGUOI CU THE lam duoc mot VIEC CU
            THE. "Xong het task" khong dung duoc — task la thu ban chon, muc
            tieu la thu phai thanh that.>

<Ca day giai doan, va cai moi giai doan CO Y hoan lai, nam o `GIAI-DOAN.md`.
File nay chi noi ban dang o dau.>

## Dang chay ban nao

<Commit nao dang chay that, o dau. Chua chay o dau thi viet "chua chay o dau ca".

Va mot o rieng, vi no la o hay giet nguoi nhat:
CO DOI GI BANG TAY sau khi dua len khong?  <co / khong / khong nho>

"Co" hoac "khong nho" thi ghi ngay vao muc "Da biet nhung chua sua" ben duoi —
mot lan sua tay khong ghi lai la mot phien ban khong ton tai o dau ca.>

## Dang o dau

<Mot doan. Cai gi vua xong, cai gi dang do.>

## Viec tiep theo

VIEC:    <MOT viec. Liet ke bay viec thi khong ai biet lam cai nao truoc.>
CHO AI:  <toi lam / cho ai do chot — ghi ro ten>

<Muon ke them boi canh thi viet o duoi. Nhung hai dong tren phai luon co: mot
muc dai va doc rat xuoi van co the khong ke ra viec nao — vi du khi moi dong
trong do deu da "Xong". Cong doc HAI DONG TREN, khong doc doan van.>

## Dang chay the nao

<He thong co dang chay khong, o dau, phien ban nao. Chua co thi viet "chua chay
o dau ca" — do cung la mot cau tra loi.>

## Da biet nhung chua sua

<Mon no. Cai gi dang sai ma minh CHAP NHAN tam. Viet ra day thi no la no; khong
viet ra thi no la mot cai bay co hen gio.>

Moi mon CON MO viet thanh mot dong `- `, va mang theo hai moc:

- <mot mon no chua sua *(soi 2026-01-15, lai 2026-04-15)* — bo dau < > di khi
  ban viet mon that>

Mon da dong thi gach di: `- ~~Mon cu~~ **Dong 2026-04-02** ...` — cong bo qua
cac dong gach.

> Vi sao hai moc do: mot dong no la **loi khai ve hien tai viet o thi qua khu**.
> Khong co gi buoc ai doc lai no, nen no gia di trong im lang va nguoi doc tuong
> minh dang doc hien trang. Do duoc tren du an goc ngay 2026-09-17: BA phien
> lien tiep, BA tren BA dong no hoa ra da cu truoc khi co ai dung toi.
>
> Gian han ra theo tinh chat, dung dat cung mot ngay — bay dong cung do mot hom
> thi cong keu mot tran roi bi tat, va luc do no bao ve KHONG cai nao.

## Chua chac

<Cho ban dang nghi ngo. Day la dong dat nhat trong ca file, va la dong hay bi bo
nhat: phien sau doc code la suy ra duoc hai muc tren, nhung KHONG suy ra duoc
cho ban dang nghi ngo.>
"""

AGENTS = """# Lam viec trong du an nay

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

## Ba vai, va ai duoc quyet cai gi

| Vai | Quyet cai gi | KHONG duoc quyet |
|---|---|---|
| Chu du an | du an la gi, khong lam gi, dung o dau | cach hien thuc |
| Nguoi lam (nguoi hay AI) | cach hien thuc, thu tu buoc | doi huong du an |
| Nguoi phan quyet | viec nay da xong CHUA | "cho qua lan nay" |

Ai lam thi KHONG tu nhan viec cua minh la xong. Lam ra bang chung, nguoi khac
doc bang chung roi moi noi xong. Khong co nguoi khac thi doc lai vao hom sau,
va phai doc BANG CHUNG chu khong doc lai loi ke.

## Bat dau mot phien — hoac mot cua so chat moi

Lenh dau tien:

    python kit/cong.py --tiep

No doc GIAI-DOAN.md, muc "viec tiep theo" cua file trang thai, va tat ca cac
cong chay duoc khong can mang; roi in ra dang o dau, sap lam gi, cai gi dang
chan. No THOAT 1 chu khong doan: hai giai doan cung dang lam, hoac khong cho
nao ghi viec sap lam, thi mot chu "tiep" khong tro vao dau ca — va mot cau
doan nghe cho xuoi con te hon mot loi tu choi.

Kho nay da nhan bo kit, nen ca 22 cong deu co cho de nhin. Tren mot kho CHUA
nhan kit thi chay `python cong.py --kho`: no chi chay 5 cong nhin kho nhu no
dang la, va 17 cong con lai im lang — im o do KHONG phai la dat.

Tren mot may moi — may khac, nguoi khac, hay chinh may nay sau khi cai lai —
chay them:

    python kit/cong.py --ha-tang

No CHAY THAT tung lenh khai trong phu-thuoc-ngoai.txt de xem may nay co du
cong cu lam viec khong. Thieu mot cai thi moi file trong kho van du, va van
khong lam duoc gi.

Cau de dan vao mot cua so chat moi, thay cho chu "tiep":

    Chay `python kit/cong.py --tiep` trong kho nay, doc ket qua, roi lam tiep
    dung viec no chi ra. Dung dua vao tri nho chat; kho la tri nho.

## Loi giao toi tay ban, truoc khi ban lam gi voi no

Loi giao la thu DAU TIEN co the sai, va no sai truoc moi thu khac. Mot loi giao
mo ma van lam duoc thi ca buoi di theo huong khong ai dinh.

O so 0 cua `viec/MAU-VIEC.md` la cho lam viec do: chep nguyen van loi giao, do
no bang nam cau, roi VIET LAI mot doan bang chu cua minh va gui lai truoc khi
bat dau. Cho lech nhau lo ra o do, luc no con re.

Khong cong nao kiem duoc buoc nay. Cai dong vai tro cong la loi xac nhan cua
nguoi giao.

## Viec KHONG giao duoc — dung lai va hoi

Bon chieu. Viec nao nang o MOT chieu thoi cung dung:

- **hau qua lon**      — hong thi anh huong ra ngoai may nay
- **kho lui**          — xoa du lieu, doi lich su, gui ra ngoai, tra tien
- **cham tien hoac du lieu ca nhan**
- **sai am tham**      — hong ma khong co gi keu len

Khong phai "viec kho thi dung". La: cai gia cua mot lan sai o day khong nam
trong tam ma nguoi giao viec chiu duoc.

Cach dung cho dung: noi DANG O DAU, VUA BIET GI, CHUA CHAC CHO NAO. Ba dong
do phien sau khong tu suy ra duoc.

## Khi chay nhieu hon mot con AI

Tach viec ra cho khac chi khi viec do **doc duoc mot minh** — nguoi nhan khong
can doc lai ca cuoc hoi thoai nay moi hieu. Khong doc duoc mot minh thi tach
ra chi lam ton them lan ke lai.

Giao gi:  muc tieu, ranh gioi, va NHIN VAO DAU DE BIET LA XONG.
Nhan lai: bang chung, khong phai loi ke. "Da xong" khong phai ket qua.

Hai con AI sua cung mot file thi cai sau de len cai truoc ma khong ai biet.
Chia theo FILE, khong chia theo y tuong.

## Truoc khi dung cai gi mat hon nua ngay

Tra xem co ai lam san chua. Doc giay phep TRUOC khi doc code — mot thu viec
dung duoc ve ky thuat ma khong dung duoc ve giay phep thi biet som re hon biet
muon.

Ghi ket qua vao `DA-TRA.md`, ke ca khi ket luan la TU DUNG. Dong dat nhat
khong phai cai ban chon, la cai ban LOAI va vi sao — do la dong khien lan sau
khong ai phai tra lai tu dau.

## Cai gi doc moi phien, cai gi doc khi can

Muc "Doc truoc khi lam" o dau file nay la thu duoc doc LAI MOI PHIEN. No co
ngan sach, ghi trong `NGAN-SACH.md`, va co cong giu.

Moi thu khac — nhat ky, boi canh, so tra cuu, ho so tung viec — doc KHI CAN.
Khong doc chung khong phai bo sot.

Cach re nhat de pha chuyen nay ma khong ai thay: de lich su tich lai trong
`STATE.md`. Trang thai la CAI DANG DUNG; cai da qua thuoc ve nhat ky.

## Truoc khi cam them mot cho noi

Plugin, connector, MCP, khoa API — hoi mot cau truoc: **viec nao trong du an
nay dang can no?** Tra loi duoc thi ghi vao `KET-NOI.md` kem QUYEN no co, cho
no cham toi, va cach tat. Tra loi khong duoc thi dung cam vao.

Mot cho noi khong phai mot tinh nang, no la MOT QUYEN. Them mot cai la mo rong
pham vi mot lan sai — va pham vi do khong con nam trong thu muc nay nua.

## Ban giao giua hai phien

Phien sau khong co tri nho cua phien nay. Thu duy nhat di qua duoc la file:

- `STATE.md`   — dang o dau, viec ke tiep
- `NHAT-KY.md` — da thu gi, hong ra sao, vi sao doi huong
- `QUYET-DINH/` — cai da chot, va ly do

Viet ba dong nhat ky truoc khi dong may. Dong dat nhat la dong CHUA CHAC.

## Khong lam

- Khong commit bi mat that.
- Khong `git reset --hard` de cay cho sach.
- Khong tu doi huong du an; de nghi thi duoc, tu doi thi khong.
- Khong chep quy uoc sang file khac. File nay la ban chinh; cho khac tro toi
  no. Hai ban sao thi mot ban se cu di ma khong ai biet ban nao cu.
"""

AGENTS_TRO = """# Quy uoc: doc `CLAUDE.md`

Quy uoc lam viec cua du an nay nam o `CLAUDE.md`. Doc file do truoc khi lam.

---

Vi sao co file nay du noi dung nam cho khac: cac cong cu AI khong doc cung mot
ten file. Co cong cu tu doc `CLAUDE.md`, co cong cu tu doc `AGENTS.md`. Thieu
ten nao thi voi cong cu do, quy uoc cua ban la MOT THU VO HINH — va no im lang
y het luc quy uoc co ma khong co tac dung.

Nen: hai TEN, mot BAN NOI DUNG. Day la cai TEN; ban noi dung o `CLAUDE.md`.
Chep noi dung sang day nua thi thanh hai nguon su that, va `cong.py` se bao do.
"""

CLAUDE = """# Quy uoc: doc `AGENTS.md`

Quy uoc lam viec cua du an nay nam o `AGENTS.md`. Doc file do truoc khi lam.

@AGENTS.md

---

Vi sao hai file ma chi mot ban noi dung: cac cong cu AI khong doc cung mot ten
file. Co cong cu tu doc `CLAUDE.md`, co cong cu tu doc `AGENTS.md`. Thieu ten
nao thi voi cong cu do, quy uoc cua ban la MOT THU VO HINH — va no im lang y
het luc quy uoc co ma khong co tac dung.

Nen: hai TEN, mot BAN NOI DUNG. Chep noi dung sang day nua thi thanh hai nguon
su that, va cong `kit/cong.py` se bao do.
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

KHI_HONG = """# Khi hong thi lam gi

> `RUI-RO.md` tra loi: **cai gi co the hong, va dau hieu nao bao no dang hong.**
> File nay tra loi cau dung sau do: **keu roi thi lam gi.**

Mot so rui ro day du ma khong co file nay thi doc len van yen tam. Do la kieu
yen tam dat nhat: ban biet cai gi se hong, va khong ai biet luc do lam gi.

Chi viet vao day nhung thu **hong that thi dau**. Mot muc cho moi thu do, va
moi muc phai tra loi duoc bon cau — neu khong tra loi duoc thi do moi la thu
dang biet.

Kiem:  python kit/cong.py

---

## <chuyen gi hong — mot cau, bang tieng cua nguoi dung chu khong phai cua may>

DAU HIEU:     <nhin vao DAU thi biet no dang hong. Mot cho cu the: mot trang,
               mot lenh, mot con so. "De y" hay "theo doi" khong phai dau hieu>
CAT MAU:      <viec DAU TIEN de no thoi hong them. Chua chac la sua — thuong la
               tat mot thu gi do>
LUI VE:       <lui ve dau, bang lenh hay buoc nao. Neu khong lui duoc thi ghi
               ro la khong lui duoc — do cung la mot cau tra loi>
XONG KHI:     <nhin vao dau de biet da ve binh thuong. Khong phai "moi thu on">
DA DIEN TAP:  <chua / NGAY da thu that, dang 2026-01-15. Cong dem theo NGAY,
               nen mot o viet dai ma khong co ngay van la chua>

<!-- Chep khoi tren xuong duoi day cho moi thu. -->

---

📌 **Vi sao co o DA DIEN TAP, va vi sao no khong lam cong do.**

Mot quy trinh lui chua bao gio chay thu la **mot loi hua ve cach kiem, chua bao
gio duoc kiem**. Cong nay dem va in ra con so do, nhung khong bat no do: bat do
thi hoac sinh ra dien tap gia, hoac cong bi tat — va luc do no bao ve khong cai
nao.

Con so do la de ban nhin, khong phai de may phan xu.
"""

RUI_RO = """# So rui ro

> File nay tra loi: **chuyen gi co the hong, va toi se THAY GI neu no bat dau
> xay ra?**

Cot **Co bao** la cot lam viec cua ca bang. Mot rui ro khong co co bao thi khong
phai rui ro duoc quan — no la mot noi lo. Va mot danh sach toan noi lo thi sau
hai tuan khong ai mo ra nua, vi mo ra cung khong lam duoc gi.

Co bao la phep do do chia ve phia truoc: *neu chuyen nay bat dau xay ra, toi se
thay gi khac di?*

Trang thai: `DANG MO` · `DA XAY RA` · `HET RUI RO`

| Rui ro | Hong co nao | Lam gi truoc | Co bao | Trang thai | Khi hong |
|---|---|---|---|---|---|
| <vi du: nha cung cap X doi gia hoac ngung dich vu> | <phan nao cua du an dung lai> | <lam gi de giam kha nang do xay ra> | <nhin vao dau de biet no dang xay ra> | DANG MO | <ten muc trong KHI-HONG.md, hoac 'khong can, vi ...'> |

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

<Cho phan nay goi phan kia. Day la cho doi mot ben thi ben kia vo.>

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

HOOK = """#!/bin/sh
# Chay cac cong TRUOC khi day len. Thoat khac 0 la huy ca lan day.
#
# BAT NO LEN (mot lan cho moi ban clone):
#
#     git config core.hooksPath hooks
#
# Vi sao phai go mot dong: FILE nay di theo ban clone vi no nam trong kho.
# DONG CAU HINH thi khong — no o .git/config, khong thuoc noi dung kho.
#
# DAY LA MOT CAI RAO, KHONG PHAI MOT CAI KHOA. `git push --no-verify` bo qua
# no hoan toan. No chan cai quen, khong chan cai co y.

set -e

# Dung trinh Python cua du an neu co. Goi `python` tran o mot du an co moi
# truong rieng thi moi phep kiem hong vi thieu thu vien — tuc la hook bao do
# vi LY DO SAI, con te hon la khong co hook.
if [ -x ".venv/Scripts/python.exe" ]; then PY=".venv/Scripts/python.exe"
elif [ -x ".venv/bin/python" ]; then PY=".venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then PY=python3
else PY=python
fi
export PYTHONIOENCODING=utf-8

$PY kit/cong.py
"""

LAP_LAI = """# Viec lap lai

> Viec lam MOT lan thi lam. Lam BA lan thi goi no lai — thanh mot lenh, mot
> script, mot dong quy uoc, hay mot muc trong `AGENTS.md`.

Luat ba lan khong phai con so dep. Duoi ba lan thi ban chua biet phan nao that
su lap va phan nao chi giong nhau; goi som thi goi nham. Tu ba lan tro len thi
cai gia cua viec KHONG goi bat dau lon hon cai gia cua viec goi.

Vi sao can mot cho ghi: khong ai nho minh da lam mot viec may lan. Lan thu sau
van thay nhu lan thu nhat — hoi lau mot chut, nhung khong du kho de dung lai
ma nghi.

Kiem:  python kit/cong.py

---

## <viec gi — mo ta bang dong tu, khong phai ten cong cu>

DA LAM:    <so lan> lan
MOI LAN:   <ton bao lau, hoac may buoc>
GOI THANH: <script nao / lenh nao / dong quy uoc nao — hoac "chua", va cong se
            doi khi so lan tu ba tro len>

<!-- Chep khoi tren xuong duoi day cho moi viec. Muc cu cong them so lan, dung
     tao muc moi cho cung mot viec. -->
"""

NGAN_SACH = """# Ngan sach ngu canh

> Cai dat nhat khong phai file dai nhat. La file duoc doc LAI MOI PHIEN.

Mot tai lieu 20 nghin tu doc mot lan mot thang thi re. Mot file 20 nghin tu
nam trong danh sach "doc truoc khi lam" thi ban tra tien cho no O MOI PHIEN,
mai mai, TRUOC KHI noi duoc cau nao ve viec that.

Nen chia lam hai tang, va chi mot tang co ngan sach:

  TANG LUON DOC    quy uoc + du an la gi + dang o dau. Co ngan sach.
  TANG DOC KHI CAN tra cuu, ho so, nhat ky, boi canh. KHONG co ngan sach —
                   cang day cang tot, mien la khong ai bi bat doc het.

Cach re nhat de vuot ngan sach ma khong ai thay: de LICH SU tich lai trong
file trang thai. No lon len moi tuan mot it, khong lan nao dang de ai keu, va
sau ba thang thi phan "dang o dau" chi con la 5% cua thu ban bat moi phien doc.

Kiem:  python kit/cong.py

## Cai doc MOI PHIEN

NGAN SACH: 6000 tu
GOM:       `AGENTS.md`, `CLAUDE.md`, `PROJECT.md`, `STATE.md`
VI SAO:    <Con so nay la mot LUA CHON, khong phai mot hang so do duoc. Gia
            tri cua no khong nam o cho no toi uu, nam o cho no DUOC KHAI RA VA
            CO CONG GIU. Sua no thi sua o day, va viet ly do — mot ngan sach
            tu nhien to len la mot ngan sach khong ton tai.>

## Cai chi doc KHI CAN

<Ke ra day cho tra cuu, de nguoi sau biet rang KHONG doc chung la dung, chu
khong phai bo sot.>

- `NHAT-KY.md`, `boi-canh/` — doc khi can biet vi sao hoi do lam the
- `DA-TRA.md`, `KET-NOI.md`, `GIAI-DOAN.md` — doc khi dung toi
"""

GIAI_DOAN = """# Giai doan

> `STATE.md` noi ban DANG o giai doan nao. File nay noi co nhung giai doan
> nao, va moi giai doan CO Y HOAN LAI cai gi.

Mot giai doan la MOT CAU HOI ban chua tra loi duoc, khong phai mot o trong
danh sach quy trinh. Du an mot cau hoi thi mot giai doan — dung nghi ra them
cho du bo.

Truong dat nhat o day la HOAN LAI. Mot ke hoach chi ghi "giai doan nay lam
gi" thi den thang sau se co nguoi keo mot viec cua giai doan 3 vao giai doan
1, rat hop ly, rat thuyet phuc — va khong ai con nho rang no da duoc CAN NHAC
VA GAT DI, chu khong phai bi bo quen. Do la duong di quen thuoc nhat toi chuyen
dap di xay lai.

Ten giai doan dang lam phai KHOP voi dong GIAI DOAN trong `STATE.md`. Hai file
noi hai ten khac nhau thi khong file nao sai ro rang, va do moi la kieu kho
chiu nhat.

Kiem:  python kit/cong.py

---

## <ten giai doan — viet thanh CAU HOI chua tra loi duoc>

TRANG THAI:   <chua toi | dang lam | xong>
THOAT KHI:    <mot cau DO DUOC. Phai co SO, hoac mot DUONG DAN co that, hoac
               mot NGUOI CU THE lam duoc mot VIEC CU THE. "Xong het task"
               khong dung duoc — task la thu ban chon, muc tieu la thu phai
               thanh that.>
TRONG DO:     <lam gi trong giai doan nay>
HOAN LAI:     <cai gi CO Y de lai, va de lai toi giai doan nao. Viet ra thi no
               la mot lua chon; khong viet thi thang sau no quay lai>
DUNG LAI NEU: <dau hieu bao DUNG CA GIAI DOAN, khong phai co them. Dien o nay
               luc dang tinh tao, vi luc can den no thi khong ai tinh tao>

<!-- Chep khoi tren xuong duoi day cho moi giai doan. -->
"""

KET_NOI = """# Cho noi

> Plugin, connector, MCP, khoa API, webhook — thu ban cam vao du an de mot
> cong cu voi tay ra NGOAI thu muc nay.

Doc ky mot cau: MOT CHO NOI KHONG PHAI MOT TINH NANG, NO LA MOT QUYEN. Cai
ban them khong phai "kha nang gui mail", la "tu gio con AI nay gui mail duoc".
Hai cau do nghe giong nhau va khac han nhau luc mot thu chay sai.

Khac `CHO-DUA.md` cho nao: cho dua la thu MAT THI MINH CHET. Cho noi la thu
MINH VOI TOI DUOC. Mot thu co the vua la ca hai, va luc do no dang o ca hai
file — dung, khong phai trung lap.

Kiem:  python kit/cong.py

## Co y KHONG noi

<Viet o day thu ban CO THE noi ma quyet dinh khong. Vi sao muc nay dung truoc:
danh sach da noi thi tu no dai ra, con danh sach TU CHOI thi khong ai viet ho.
Khong co no, ba thang nua ban se noi lai dung thu hom nay ban da tu choi, va
khong con ly do cu de doc.>

- <vi du: khong noi thang vao co so du lieu that — chi qua ban sao>

---

## <ten cho noi>

DUNG DE:     <viec gi trong du an nay can no. Khong tra loi duoc thi go ra>
QUYEN:       <doc | ghi | tieu tien>
CHAM TOI:    <no voi tay ra toi dau ngoai thu muc nay>
GIOI HAN:    <cai gi no KHONG duoc lam, va cai gi CHAN — nguoi hay may>
BAT BOI:     <ai bat, ngay nao>
TAT RA SAO:  <tat bang cach nao. Mot dong. Luc can den dong nay thi khong ai
              con binh tinh di tim>

<!-- Chep khoi tren xuong duoi day cho moi cho noi. -->
"""

DA_TRA = """# Da tra

> Truoc khi dung mot thu mat hon nua ngay, tra xem co ai lam san chua. Tra
> xong thi ghi vao day — KE CA khi ket luan la tu dung.

Vi sao file nay ton tai: cai dat nhat khong phai cai ban CHON, la cai ban
LOAI. Ba tuan nua se co nguoi (hoac chinh ban) hoi "the da xem cai X chua?".
Khong co dong nao tra loi thi ban tra lai tu dau, va lan nay co the ra ket
luan nguoc — khong phai vi su that doi, ma vi ban quen mat ly do cu.

Mot muc = mot cau hoi da tra, khong phai mot cong cu. "Chon thu vien bieu do
nao" la mot muc; "Chart.js" thi khong.

Kiem:  python kit/cong.py

---

## <can gi — viet thanh CAU HOI, khong phai ten cong cu>

NGAY:      {ngay}
DA TRA:    <tra o dau, thay nhung ung vien nao>
CHON:      <cai nao — hoac "tu dung", do cung la mot lua chon>
VI SAO:    <ly do chon>
DA LOAI:   <loai cai nao, VI SAO. Day la dong khien lan sau khoi tra lai>
GIAY PHEP: <MIT / Apache-2.0 / GPL-3.0 / khong ro / khong ap dung>
XEM LAI:   <ngay, hoac "khong can". BAT BUOC co ngay neu giay phep "khong ro">

<!-- Chep khoi tren xuong duoi dong nay cho moi lan tra. Muc cu de nguyen. -->
"""

NHAT_KY = """# Nhat ky

> Moi phien lam viec them MOT muc, DAT LEN TREN cung, ngay duoi dong ke ngang.
> KHONG sua muc cu. Muc cu sai thi viet muc moi noi no sai o dau.

QUYET-DINH/ giu cai DA CHOT. File nay giu cai CHUA CHOT: da thu gi, hong ra
sao, vi sao doi huong, cai gi luc do tuong la dung. Do la phan khong ai nho
noi sau ba tuan — va la phan khien nguoi ta dap di xay lai lan thu hai, vi
khong con ai biet lan thu nhat da dung o dau.

Nguyen lieu tho (ban phan tich dai, doan chat, ket qua do) de trong `boi-canh/`
roi tro toi tu dong HO SO cua muc tuong ung.

Kiem:  python kit/cong.py

---

## {ngay} — khoi tao du an

DA LAM:     dung bo khung bang kit/khoi-tao.py
BIET THEM:  <chua co gi. Muc that dau tien se nam TREN muc nay>
CON TREO:   dien PROJECT.md, nhat la muc "KHONG phai muc tieu"
HO SO:      <chua co. Khi co thi ghi duong dan vao day>
"""

BOI_CANH = """# boi-canh — cho de nguyen lieu tho

Cho nay KHONG chua tai lieu. No chua thu de doc lai khi ai do hoi "vi sao hoi
do lam the": ban phan tich dai, doan chat quan trong, ket qua do, log.

Ten file:  YYYY-MM-DD-<viec-gi>.md

BA LUAT

1. KHONG sua file da nam o day. No la ban GHI, khong phai ban thao. Sua no la
   xoa mat ly do cu — ma ly do cu moi la thu ban can khi nhin lai.

2. Moi file o day phai duoc MOT muc trong NHAT-KY.md tro toi. Khong ai tro toi
   thi khong ai tim ra, va sau sau thang no thanh rac roi bi don di cung voi
   thu dang gia. Cong kiem dung chieu nguoc lai: NHAT-KY tro toi cho khong co
   that.

3. KHONG de bi mat that vao day. Doan chat hay dinh kem khoa API, mat khau, du
   lieu khach hang thi cat truoc khi luu. Cong "Bi mat" soi ca thu muc nay.
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
| <vi du: github.com/ten-ban/ten-kho> | <du an dung no de lam gi> | <thieu no thi mat phan nao> | <ai giu, het han khi nao> |

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
> Viec xong thi o 6 di vao STATE / QUYET-DINH, con to nay thanh ho so.

## 0. Loi giao — da sac chua

<Chep NGUYEN VAN loi giao vua nhan vao day, khong sua chu nao. Chep nguyen van
de lat sau con doi chieu duoc: mot loi giao duoc nho lai bao gio cung sac hon
loi giao that.>

```
<loi giao nguyen van>
```

Nam cau do. Cau nao loi giao da tra loi thi ghi "co"; cau nao chua thi ghi
ban se LAM GI voi no — hoi lai, hay tu gia dinh roi viet gia dinh ra.

| Cau hoi | Loi giao co tra loi khong |
|---|---|
| **Dung kho nay khong?** Loi giao dang noi ve cai dang mo truoc mat, hay ve mot du an khac? | |
| **Dich hay duong?** No dang ta KET QUA phai dung, hay dang chi cach lam? Neu chi cach lam ma cach do va voi code that — noi ra truoc, dung lam theo roi bao. | |
| **Xong la the nao?** Ai nhin vao dau de noi la dat? (Khong phai ban. Ban khong tu tuyen bo viec cua minh la da nghiem thu.) | |
| **Cai gi KHONG duoc doi?** Ho so da chot, du lieu dang chay, quyet dinh da co. | |
| **Cho nao hoi lai, cho nao tu quyet?** Mot chon lua lui lai duoc thi tu quyet. Cai doi huong san pham, doi kien truc, tieu tien, hay kho lui — hoi. | |

**Viet lai loi giao, mot doan, bang chu cua ban** — roi GUI LAI cho nguoi giao
truoc khi tieu mot buoi. Cho lech nhau se lo ra o day, luc no con re.

```
<loi giao viet lai>
```

GIA DINH DA GHI: <nhung cho ban khong hoi ma tu chon. Khong ghi ra thi lat sau
                  khong ai phan biet duoc "da thong nhat" voi "toi doan the">

<!-- Khong cong nao kiem duoc o nay. Viec lam sac dien ra TRUOC khi co file nao
     ton tai, va mot o bat buoc phai day se duoc day bang thu nghe cho xuoi.
     Cai dong vai tro cong o day la loi XAC NHAN cua nguoi giao, khong phai
     mot script. -->

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

## 5. Giao di dau — phan nao ban lam, phan nao giao, phan nao KHONG giao

<Chi dien khi viec nay duoc chia cho nhieu hon mot nguoi hoac mot cong cu. Mot
minh lam het thi bo trong o nay — no khong phai thu tuc.>

GIAO CHO:    <ai, hoac cong cu nao — va lam PHAN NAO>
SO HUU:      <duong dan ma phan do duoc sua. Trong luc no chay, khong ai khac
              cham vao>
GOP TAI:     <cho hai ben gap lai, va nhin vao dau thi biet la gop xong. Dinh
              cho nay TRUOC khi chia — dinh sau thi moi ben da di mot huong>
KHONG GIAO:  <phan ban giu lai, va vi sao. Bon chieu o muc "Viec KHONG giao
              duoc" trong AGENTS.md la cho de quyet>

<Khong cong nao kiem o nay, va ly do khac voi o 0: thu dang so nhat khi chia
viec — hai luong cung sua mot file — DA co mot thu chan, va no chan rat to. Git
bao xung dot luc gop, no do, va khong ai bo qua duoc. Mot cong moi o day chi di
kiem lai thu da duoc kiem.

Phan con lai — giao gi, giu gi — la mot QUYET DINH. Viet ra de lat sau con doi
chieu duoc voi ket qua, khong phai de may doc.>

## 6. Ghi lai — xong roi con lai cai gi

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
# Ngoai dong URL, file nay con nhan ba dang dong khac, moi dang mot cong doc:
#   ten-mien <ten mien>            — han dang ky, doc qua RDAP     (--ngoai)
#   ban-sao  <duong dan>  <url>    — ban trong kho vs ban da cong bo (--ngoai)
#   ha-tang  <ten>  <lenh>         — cong cu phai dung duoc tren may (--ha-tang)
#
# Dong ha-tang xep theo THU TU DUNG LEN: cai o tren can co truoc. Vi du:
#   ha-tang git  git --version
#
# Vi sao ha-tang la mot LENH chu khong phai mot o de dien: mot o doi phai co
# "cach dung lai" se duoc dien bang mot cau nghe cho xuoi, va khong ai biet
# cau do con dung khong. Mot lenh thi hoac thoat 0 hoac khong.
#
# Vi sao co file nay: cai gi khong cong nao nhin toi thi khi no chet, moi cong
# trong nha van xanh het. Do dung la kieu hong im lang.
#
# Kiem:  python kit/cong.py --ngoai
#
# Dong bat dau bang "ten-mien " duoc mot cong KHAC lo: no doc SO DANG KY qua
# RDAP chu khong goi trang web. Vi sao tach ra: nhieu dia chi tra HTTP 403 voi
# script, va luc do khong phan biet duoc "trang chet" voi "trang song nhung
# chan toi". Han ten mien thi khong hoi trang, hoi so dang ky.

# https://github.com/<ai do>/<kho gi do>  kho ma du an nay clone tu day
# ten-mien vi-du.com  dia chi nguoi ta go vao de toi du an nay
"""

README_KIT = """# Bat dau

Du an nay dung bo cong cua Project Operating System.

## Doc theo thu tu nay

1. `PROJECT.md` — du an la gi, va KHONG lam gi
2. `STATE.md` — dang o dau, viec ke tiep la gi
3. `AGENTS.md` — lam viec o day theo quy uoc gi (`CLAUDE.md` tro toi no)
4. `NHAT-KY.md` — da thu gi roi, vi sao doi huong
5. `DA-TRA.md` — da tra gi roi, chon gi, loai gi
6. `KET-NOI.md` — cong cu voi tay ra duoc toi dau, va tat bang cach nao
7. `GIAI-DOAN.md` — co nhung giai doan nao, moi cai hoan lai cai gi
8. `NGAN-SACH.md` — cai gi doc moi phien, va no duoc phep to den dau
9. `LAP-LAI.md` — viec nao da lam ba lan ma chua duoc goi lai

## Truoc khi dong may

Them mot muc vao dau `NHAT-KY.md`. Ba dong cung duoc. Thu dat nhat la dong
CON TREO va cho dang nghi ngo — phien sau KHONG tu suy ra duoc.

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


def _cho_chay(p):
    """Bat bit thuc thi. Tren Linux/macOS thieu no thi git IM LANG bo qua hook,
    va mot hook bi bo qua khong khac gi mot hook khong ton tai."""
    try:
        os.chmod(p, 0o755)
    except OSError:
        pass


def da_co(goc, *duong):
    """Kho nay da co thu do o BAT KY duong dan nao trong danh sach chua.

    viet() chi nhin dung mot duong. Cac cong thi tim theo nhieu duong — cong
    "file trang thai" chap nhan ca STATE.md lan docs/STATE.md. Hai ben khong
    nhin cung mot cho thi --kho se tao mot ban thu hai ben canh ban da co, va
    hai file trang thai la dung kieu hong ca bo cong nay sinh ra de chan.

    Do duoc 2026-09-17: chay --kho tren chinh kho goc tao them STATE.md va
    cong.py o goc, trong khi chung da nam o docs/ va kit/.
    """
    return any(os.path.exists(os.path.join(goc, d)) for d in duong)


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
    chi_kho = "--kho" in sys.argv
    ten = os.path.basename(goc.rstrip(os.sep)) or "du-an"
    han = (datetime.date.today() + datetime.timedelta(days=14)).isoformat()

    os.makedirs(goc, exist_ok=True)
    print()
    print("  Khoi tao: %s%s" % (goc, "   (--kho: chi cac file cong NHIN KHO doi)"
                                if chi_kho else ""))
    print()

    if chi_kho:
        # Dung nhung file ma nam cong `nhin_kho` cua cong.py doi, khong hon.
        # Hai cong con lai trong nam cai do — lenh trong tai lieu, va bi mat —
        # khong can file nao ca.
        da_tao = 0
        if da_co(goc, "STATE.md", "docs/STATE.md", "TRANG-THAI.md",
                 "CURRENT.md"):
            print("  bo qua (da co)  file trang thai")
        else:
            da_tao += viet(goc, "STATE.md", STATE.format(ngay=HOM_NAY))
        # Hai ten, mot ban noi dung. Chon ban chinh theo cai kho DA CO, khong
        # theo mac dinh cua kit: tha mot AGENTS.md day vao mot kho da co
        # CLAUDE.md day thi cong "quy uoc" van do, chi la do vi mot ly do khac
        # — hai nguon su that. Do duoc 2026-09-17 tren mot kho that.
        co_claude = os.path.exists(os.path.join(goc, "CLAUDE.md"))
        co_agents = os.path.exists(os.path.join(goc, "AGENTS.md"))
        if co_claude and not co_agents:
            da_tao += viet(goc, "AGENTS.md", AGENTS_TRO)
        elif co_agents and not co_claude:
            da_tao += viet(goc, "CLAUDE.md", CLAUDE)
        elif not co_agents and not co_claude:
            da_tao += viet(goc, "AGENTS.md", AGENTS)
            da_tao += viet(goc, "CLAUDE.md", CLAUDE)
        else:
            print("  bo qua (da co)  AGENTS.md va CLAUDE.md")
        if da_co(goc, "CHO-DUA.md", "docs/CHO-DUA.md"):
            print("  bo qua (da co)  CHO-DUA.md")
        else:
            da_tao += viet(goc, "CHO-DUA.md", CONG_CU)
        if da_co(goc, "phu-thuoc-ngoai.txt", "docs/phu-thuoc-ngoai.txt"):
            print("  bo qua (da co)  phu-thuoc-ngoai.txt")
        else:
            da_tao += viet(goc, "phu-thuoc-ngoai.txt", PHU_THUOC)
        nguon = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "cong.py")
        dich = os.path.join(goc, "cong.py")
        if da_co(goc, "cong.py", os.path.join("kit", "cong.py")):
            print("  bo qua (da co)  cong.py")
        elif os.path.exists(nguon):
            io.open(dich, "w", encoding="utf-8", newline="").write(
                io.open(nguon, encoding="utf-8").read())
            print("  tao             cong.py")
            da_tao += 1
        print()
        print("  " + "-" * 62)
        print("  Xong. %d file. File nao ban da co thi KHONG bi dung toi." % da_tao)
        print()
        print("  Moi file o tren tra loi dung mot cong:")
        print("    STATE.md              -> File trang thai con song")
        print("    AGENTS.md + CLAUDE.md -> Quy uoc toi duoc ca hai loai cong cu")
        print("    CHO-DUA.md            -> Cho dua duoc ghi ra")
        print("    phu-thuoc-ngoai.txt   -> cho khai URL, ten mien, ban sao")
        print()
        print("  Roi chay:   python cong.py --kho")
        print()
        print("  Day KHONG phai nhan ca bo kit. 18 cong con lai canh nhung ho so")
        print("  bo kit sinh ra, va chung im lang cho toi khi ban co chung.")
        print("  " + "-" * 62)
        print()
        return 0


    # Dem THAT, khong ghi cung. Ban dau file nay in ra mot con so ghi cung
    # va no sai ngay lan chay dau — dung cai ho loi ma chinh bo cong nay bat.
    da_tao = 0
    da_tao += viet(goc, "PROJECT.md", PROJECT.format(ten=ten))
    da_tao += viet(goc, "STATE.md", STATE.format(ngay=HOM_NAY))
    da_tao += viet(goc, "AGENTS.md", AGENTS)
    da_tao += viet(goc, "CLAUDE.md", CLAUDE)
    da_tao += viet(goc, "QUYET-DINH/README.md", QUYET_DINH)
    da_tao += viet(goc, "QUYET-DINH/0001-mau.md", QD_MAU.format(ngay=HOM_NAY))
    da_tao += viet(goc, "viec/MAU-VIEC.md", VIEC)
    da_tao += viet(goc, "NHAT-KY.md", NHAT_KY.format(ngay=HOM_NAY))
    da_tao += viet(goc, "DA-TRA.md", DA_TRA.format(ngay=HOM_NAY))
    da_tao += viet(goc, "KET-NOI.md", KET_NOI)
    da_tao += viet(goc, "GIAI-DOAN.md", GIAI_DOAN)
    da_tao += viet(goc, "NGAN-SACH.md", NGAN_SACH)
    da_tao += viet(goc, "LAP-LAI.md", LAP_LAI)
    da_tao += viet(goc, "hooks/pre-push", HOOK)
    _cho_chay(os.path.join(goc, "hooks", "pre-push"))
    da_tao += viet(goc, "boi-canh/README.md", BOI_CANH)
    da_tao += viet(goc, "README.md", README_KIT)

    if day_du:
        da_tao += viet(goc, "GIA-DINH.md", GIA_DINH.format(han=han))
        da_tao += viet(goc, "SO-SEO.md", SO_SEO.format(ngay=HOM_NAY))
        da_tao += viet(goc, "RUI-RO.md", RUI_RO)
        da_tao += viet(goc, "KHI-HONG.md", KHI_HONG)
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
    print()
    print("  Muon cac cong tu chay moi lan day len, go mot lan:")
    print("      git config core.hooksPath hooks")
    print("  " + "-" * 62)
    return 0


if __name__ == "__main__":
    sys.exit(main())
