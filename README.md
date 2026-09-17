# pos-kit — Hệ điều hành dự án, bản chạy được

Một bộ tối thiểu để khởi tạo và giữ trật tự cho **bất kỳ dự án nào chạy bằng AI**.

**Hai file Python. Thư viện chuẩn. Không cài đặt gì.**

```bash
git clone https://github.com/thelongmkt2001/pos-kit
python pos-kit/khoi-tao.py <thu-muc-du-an> --day-du    # dựng bộ tối thiểu
cd <thu-muc-du-an>
python kit/cong.py                                     # kiểm
python kit/cong.py --tu-kiem                           # kiểm CHÍNH CÁC PHÉP KIỂM
```

`khoi-tao.py` tự chép `cong.py` vào dự án mới, nên sau bước đầu bạn không cần kho này nữa.

---

## Vì sao nó nhỏ như vậy

Bản tiêu chuẩn mà bộ này dựa vào liệt kê **25 artifact** "gần như dự án nào cũng phải có".

Đem chấm trên một dự án thật đã chạy 20 ngày, 180 commit và đã phát hành: **12 có, 13 chưa bao giờ
được tạo** — dự án vẫn chạy và vẫn ship.

> 📌 Đó không chứng minh 13 cái kia vô dụng. Nó chứng minh **"gần như dự án nào cũng phải có" là câu
> quá mạnh cho một danh sách 25 món** — và một bộ kit phát ra 25 template thì tuần thứ hai là bị bỏ.

Thêm artifact khi có một **câu hỏi thật** chưa có chỗ trả lời. Đừng tạo trước rồi tìm việc cho nó.

---

## Vì sao phần chính là mã chạy được, không phải văn bản

Đây là chỗ bộ kit này khác một bộ template.

Dự án sinh ra nó có một sổ ghi lỗi. Sổ đó **gọi tên cơ chế lỗi bằng chữ** — rồi chính cơ chế ấy lặp
lại **19 lần tính tới 2026-09-17**, trong đó có những lần xảy ra **ngay trong lúc đang viết về nó**,
và một lần xảy ra **bên trong chính công cụ dựng ra để bắt nó**.

Cơ chế đó, nói một lần: một phép đo trả về thứ **có hình dạng của câu trả lời** — một con số, một
danh sách rỗng — nhưng thứ đó nói về **chính công cụ**, không nói về hệ thống. Người đo đọc nó như
câu trả lời.

> Một luật viết ra giấy được thi hành bởi **chính bên bị ràng buộc**. Đó không phải một ranh giới.

Thứ bắt được lần thứ 11 không phải một câu nhắc nhở. Là một phép kiểm chạy **ngoài phán đoán của
người viết**, và đòi hỏi kết quả phải đổi.

---

## Hai luật bộ kit tự áp cho mình

**1. Mỗi cổng phải khai nó KHÔNG chứng minh được gì.**

Chạy `python kit/cong.py` và bạn thấy, với từng cổng, hai dòng:

```
chung minh:       khong co chuoi nao KHOP CAC MAU DA BIET trong file dang theo doi
KHONG chung minh: repo khong co bi mat. No tim theo HINH DANG; mot bi mat dat
                  ten la `cau_hinh_3` thi no khong thay.
```

Dòng thứ hai mới là dòng quan trọng. Một câu nghe như lời bảo đảm mà thực chất nói ít hơn **tự nó là
một cái bẫy** — và nó bẫy đúng người tin nó nhất: người đã viết ra nó.

**2. Mỗi cổng phải chứng minh được là nó trượt được.**

```bash
python kit/cong.py --tu-kiem
```

Nó chép dự án sang thư mục tạm, **cố ý phá** đúng thứ mỗi cổng sinh ra để bắt, rồi đòi kết quả phải
đổi. **Dự án thật không bao giờ bị đụng tới.**

> Một phép kiểm chưa bao giờ báo đỏ thì bạn chưa biết nó báo đỏ được không.

⚠️ Khi `--tu-kiem` báo một cổng "không bắt được gì", hỏi **câu này trước**: *phép phá của tôi có phá
đúng chỗ không?* Dự án gốc chạy phép kiểm tương tự và có ba cổng bị đọc là "mù" — **cả ba đều là
phép thử viết sai**, không phải cổng hỏng. Cách giải thích dễ chịu hơn sai ba trên ba lần.

---

## Các cổng, và mỗi cổng bắt cái gì

| Cổng | Bắt | Không bắt |
|---|---|---|
| **Trạng thái còn sống** | Thiếu `STATE.md`, hoặc nó tụt lại quá xa so với commit | Nội dung trong đó còn đúng |
| **Sổ giả định có hạn kiểm** | Giả định không có trạng thái; giả định **quá hạn mà vẫn chưa kiểm** | Giả định *quan trọng nhất* đã được viết ra |
| **Lệnh trong tài liệu chạy được** | Lệnh trỏ tới file không tồn tại | Lệnh đó chạy ra kết quả đúng |
| **Bí mật không nằm trong repo** | Chuỗi khớp các mẫu đã biết | Repo không có bí mật — nó tìm theo **hình dạng** |
| **Cái đã bỏ thì không ai trỏ tới** | Tài liệu đang dùng trỏ tới file đã đánh dấu bỏ | Mọi thứ đã cũ đều được đánh dấu |
| **Trạng thái dự án gọi tên được** | `STATE.md` không có trạng thái thuộc danh sách, hoặc thiếu điều kiện thoát | Trạng thái đó **đúng** |
| **Rủi ro đang mở có cò báo** | Rủi ro còn mở mà ô cò báo trống, hoặc chỉ là một **ý định** | Cò báo đó sẽ kêu |
| **Chỗ dựa được ghi ra** | Có dấu vết phụ thuộc ngoài mà không danh sách nào ghi | Danh sách đó đủ, hay đúng |
| **Bản đồ hệ thống còn đúng** | Bản đồ trỏ tới đường dẫn không còn tồn tại | Bản đồ đúng, đủ, hay **có tồn tại** |
| **Tầng luôn đọc còn trong ngân sách** | Tổng số từ của những file được đọc **mỗi phiên** vượt con số đã khai | Con số ngân sách đó **đúng**; và nó chỉ đo những file bạn **kể ra** |
| **Dãy giai đoạn còn chốt được** | Giai đoạn không gọi tên trạng thái, hoặc gọi bằng một chữ tự nghĩ ra (*"sắp xong"*); điều kiện thoát **không đo được**; không ghi cái cố ý hoãn lại; **hai** giai đoạn cùng đang làm; tên đang làm **lệch với `STATE.md`** | Kế hoạch đó đúng, khả thi, hay đủ |
| **Chỗ nối ghi được thì có cách tắt** | Một chỗ nối không gọi tên **quyền** của nó, hoặc gọi bằng một chữ tự nghĩ ra; chỗ nối **ghi** hoặc **tiêu tiền** được mà không viết ra giới hạn và cách tắt | Bạn đã khai báo **đủ** chỗ nối — nó đọc file, không đi dò máy bạn |
| **Sổ "đã tra" ngăn được lần tra lại** | Một mục **đã chọn** mà không ghi đã loại gì; chọn thứ bên ngoài mà không ghi giấy phép; giấy phép *không rõ* mà không có hạn xem lại, hoặc hạn đã qua | Bạn đã tra **đủ**, hay tra **đúng**, hay giấy phép ghi trong đó là thật |
| **Quy ước tới được cả hai loại công cụ** | Chỉ có một trong hai tên `AGENTS.md` / `CLAUDE.md`; hoặc **cả hai đều mang nội dung** — hai nguồn sự thật | Công cụ **có đọc** file đó thật không, hay có làm theo không |
| **Nhật ký còn được ghi** | Nhật ký trỏ tới hồ sơ đã mất; hoặc kho chạy tiếp **10 commit** mà không ai ghi thêm dòng nào | Mục nhật ký đó đúng, hay có ích |
| **Việc tiếp theo còn đúng giai đoạn** | Mục *việc tiếp theo* của `STATE.md` **không còn gọi tên** giai đoạn đang làm — phần nhìn về phía trước đã chết mà vẫn đọc lên như một kế hoạch | Những việc kể trong đó **đang** làm, hay đủ, hay xếp đúng thứ tự |
| **Việc lặp lại đã được gọi lại** | Một việc ghi **từ 3 lần trở lên** trong `LAP-LAI.md` mà ô *gọi thành* còn bỏ trống, hoặc chỉ ghi *"chưa"* | Bạn đã ghi **đủ** những việc đang lặp — việc làm năm lần mà không ai ghi vào đó thì nó không thấy |
| **Bản trong kho khớp bản đã công bố** *(`--ngoai`)* | File đã khai báo **lệch** với bản đang nằm ở URL tương ứng; hoặc không tải được bản đó | Bạn đã khai báo **đủ** file được công bố |
| **Tên miền còn hạn** *(`--ngoai`)* | Tên miền đã khai báo còn **≤ 60 ngày** là hết hạn; hoặc **không tra được hạn** | Thẻ thanh toán gia hạn còn sống. Nó đọc sổ đăng ký, không đọc ví bạn |
| **Phụ thuộc ngoài còn sống** *(`--ngoai`)* | URL đã khai báo mà chết | Nội dung sau URL còn đúng |

Cổng cuối cần mạng nên **tuỳ chọn** — để `python kit/cong.py` chạy được cả lúc không có Internet.

---

## Những file nó tạo, và mỗi file trả lời câu gì

Bộ mặc định:

| File | Câu hỏi nó trả lời | Đổi bao lâu một lần |
|---|---|---|
| `PROJECT.md` | Dự án là gì, và **KHÔNG** làm gì? | Hiếm |
| `STATE.md` | Đang ở đâu, việc kế tiếp? | Gần như mỗi phiên |
| `AGENTS.md` | Làm việc ở đây theo quy ước gì? **Bản chính.** | Khi quy ước đổi |
| `CLAUDE.md` | *(một dòng trỏ tới `AGENTS.md` — hai tên, một bản nội dung)* | — |
| `QUYET-DINH/README.md` + `0001-mau.md` | Đã chốt gì, vì sao? | Khi quyết một chuyện khó lùi |
| `viec/MAU-VIEC.md` | **Lời giao đã sắc chưa**, việc đang làm là gì, đi tới đâu? | Mỗi việc một tờ |
| `NHAT-KY.md` | Đã thử gì rồi, hỏng ra sao, **vì sao đổi hướng**? | Mỗi phiên một mục |
| `DA-TRA.md` | Đã tra gì rồi, chọn gì, **loại gì và vì sao**? | Mỗi lần tra một mục |
| `KET-NOI.md` | Công cụ **với tay ra được tới đâu**, và tắt bằng cách nào? | Khi cắm thêm hoặc gỡ một chỗ nối |
| `GIAI-DOAN.md` | Có những giai đoạn nào, mỗi cái **cố ý hoãn lại** gì? | Khi sang giai đoạn khác |
| `NGAN-SACH.md` | Cái gì đọc **mỗi phiên**, và nó được phép to đến đâu? | Hiếm — mỗi lần đổi phải viết lý do |
| `LAP-LAI.md` | Việc nào đã làm **ba lần** mà vẫn đang làm tay? | Khi bắt gặp mình làm lại một việc |
| `boi-canh/` | *(nguyên liệu thô: bản phân tích dài, đoạn chat, kết quả đo)* | — |
| `README.md` | Người mới bắt đầu từ đâu? | Hiếm |
| `kit/cong.py` | *(bản sao của bộ cổng, để dự án chạy độc lập)* | — |

Thêm với `--day-du`:

| File | Câu hỏi nó trả lời |
|---|---|
| `GIA-DINH.md` | Đang dựa trên điều gì **chưa kiểm**? |
| `SO-SEO.md` | Dự án này đã tự lừa mình những lần nào? |
| `RUI-RO.md` | Chuyện gì có thể hỏng, và **dấu hiệu nào báo** nó đang hỏng? |
| `CHO-DUA.md` | Thứ gì bên ngoài mà mất là dự án chết? |
| `BAN-DO.md` | Đổi một chỗ thì **chỗ nào khác động theo**? |
| `phu-thuoc-ngoai.txt` | *(một nguồn cho cả người lẫn cổng kiểm)* |

📌 Mẫu viết bằng **câu hỏi**, không phải tiêu đề trống. Một tiêu đề trống sẽ được điền bằng thứ nghe
cho xuôi. Một câu hỏi thì hoặc được trả lời, hoặc bỏ trống **một cách nhìn thấy được**.

---

## Khi một cổng kêu đúng chỗ bạn CỐ Ý làm sai

Có những dự án mang một chỗ sai có chủ đích — một fixture dạy học, một ví dụ cố tình hỏng. Cổng sẽ
kêu, và kêu đúng.

Tạo `kit/bo-qua.txt` trong dự án của bạn, mỗi dòng một đường dẫn (hoặc tiền tố):

```
# Ghi LY DO ngay phia tren moi dong. Khong ly do thi nguoi sau khong biet
# co nen xoa khong.

# Vi du: thu muc nay mang loi CO Y de day hoc; sua no di la xoa mat bai giang.
vi-du/du-an-hong
```

⚠️ Danh sách này **được in ra mỗi lần chạy cổng**, cố ý. Một chỗ được miễn trừ mà không ai nhìn
thấy chính là kiểu hỏng mà cả bộ cổng này sinh ra để chặn.

---

## Việc đầu tiên sau khi khởi tạo

**Không phải viết code.** Là điền `PROJECT.md`, nhất là mục **"KHÔNG phải mục tiêu"**.

Chỗ đó quan trọng hơn nó trông. Thứ bạn cố ý không làm sẽ bị đề nghị lại nhiều lần — và mỗi lần
không có dòng đó thì bạn phải cãi lại từ đầu.

---

## Vì sao có cả `AGENTS.md` lẫn `CLAUDE.md`

**Không công cụ nào đọc cả hai tên.** Công cụ này tự đọc `CLAUDE.md`, công cụ hãng khác tự đọc
`AGENTS.md`. Thiếu tên nào thì với công cụ đó, quy ước của bạn là **một thứ vô hình** — và nó im
lặng y hệt lúc quy ước có mà không có tác dụng. Hai chuyện khác hẳn nhau ấy cho ra **cùng một quan
sát**, nên phải chặn bằng file chứ không bằng niềm tin.

Đo được ngày 2026-09-17, không phải phòng xa: một phép đối chứng suýt hỏng vì chỉ đặt một tên.

> ### Hai **tên**, một **bản nội dung**.

`AGENTS.md` mang nội dung. `CLAUDE.md` chỉ một dòng trỏ tới nó. Chép sang cả hai thì sửa bản này,
bản kia cũ đi mà không ai biết bản nào cũ — và cổng báo đỏ đúng chuyện đó.

---

## Khi một phần của kho được công bố ở chỗ khác

Tách làm hai kho là **bắt buộc** khi một bên phải công khai còn bên kia riêng tư — không ai publish
được một thư mục con của kho riêng tư. Cái **không** bắt buộc là để việc đồng bộ hai bên sống bằng
trí nhớ.

Khai báo trong `phu-thuoc-ngoai.txt`:

```
ban-sao kit/cong.py  https://raw.githubusercontent.com/<ban>/<kho>/main/cong.py
```

> ### Hai bản lệch nhau thì **cả hai vẫn chạy được**, và mọi cổng trong nhà vẫn xanh.

📌 Kho sinh ra bộ kit này dính cả hai vế trong cùng một ngày: ba file được chép tay sang kho công
khai **sáu lần** trong một buổi, và một cặp khác — bản chép của dự án mẫu — bị phát hiện đã **lệch
108 dòng suốt 16 ngày** mà không cổng nào thấy. Bản chép đó đã bị gỡ hẳn; cái còn lại thì giờ có
cổng canh.

⚠️ **"Không tải được bản đã công bố" tính là hỏng**, không phải *"chắc là vẫn khớp"*. Và cổng so
theo nội dung, **bỏ qua khác biệt ký tự xuống dòng** — Windows và Linux ghi khác nhau, mà một cổng
báo đỏ vì CRLF thì bị tắt đi trong tuần đầu.

---

## Một kiểu hỏng không cổng nào trong nhà nhìn thấy

Tên miền hết hạn. Máy chủ vẫn chạy, mọi cổng vẫn xanh, và người ta gõ địa chỉ thì **không vào được**.
Không có gì báo lỗi cả — chỉ là không ai vào được nữa.

Khai báo nó trong `phu-thuoc-ngoai.txt`:

```
ten-mien vi-du.com  dia chi nguoi ta go vao de toi du an nay
```

> ### Đừng hỏi trang web. Hỏi **sổ đăng ký**.

Cách hiển nhiên — gọi thử địa chỉ đó xem còn sống không — **đã thử và không chạy**: rất nhiều địa
chỉ trả `HTTP 403` với script, và lúc đó không phân biệt được *"trang chết"* với *"trang sống nhưng
chặn tôi"*. Hạn tên miền thì không nằm ở trang web; nó nằm ở sổ đăng ký, và RDAP trả nó về dưới dạng
**dữ liệu**, không phải một trang có thể bị chặn.

Cổng đi qua bảng chỉ đường của **IANA** để tìm máy chủ RDAP của đuôi tên miền, rồi hỏi thẳng máy chủ
đó — không qua dịch vụ trung gian nào.

📌 **"Không tra được hạn" tính là hỏng**, không phải *"chắc là còn hạn"*. Không biết thì không yên
tâm được. Ngưỡng 60 ngày: đủ để gia hạn không vội, đủ muộn để không kêu suốt nửa năm — một cổng kêu
200 ngày liền thì bị tắt đi, và lúc bị tắt nó không bảo vệ gì nữa.

---

## Để các cổng tự chạy, thay vì trông vào trí nhớ

Bộ kit dựng sẵn `hooks/pre-push`. Bật một lần cho mỗi bản clone:

```bash
git config core.hooksPath hooks
```

Từ đó `git push` chạy `kit/cong.py` trước, và **huỷ lần đẩy** nếu có cổng nào đỏ. Đo trên một dự án
vừa khởi tạo: **0,7 giây**.

Vì sao vẫn phải gõ một dòng: **file** đi theo bản clone vì nó nằm trong kho; **dòng cấu hình** thì
không — nó ở `.git/config`, không thuộc nội dung kho. Đã đo tại chỗ, không phải đoán.

> ### Đây là một cái **rào**, không phải một cái **khoá**.

`git push --no-verify` bỏ qua nó hoàn toàn — cũng đã đo. Nó chặn cái **quên**, không chặn cái **cố
ý**. Muốn tầng không tắt được thì phải là thứ chạy ở nơi người đẩy không với tới, ví dụ CI.

📌 Hook tự chọn `.venv` của dự án nếu có. Gọi `python` trần ở một dự án có môi trường riêng thì mọi
phép kiểm hỏng vì thiếu thư viện — **đỏ vì lý do sai**, còn tệ hơn không có hook.

---

## Cái đắt nhất không phải file dài nhất

Là file được đọc **lại mỗi phiên**.

Một tài liệu 20 nghìn từ đọc một lần một tháng thì rẻ. Cùng 20 nghìn từ đó nằm trong danh sách
*"đọc trước khi làm"* thì bạn trả **ở mỗi phiên, mãi mãi, trước khi nói được câu nào về việc thật**.

Nên chia hai tầng, và **chỉ một tầng có ngân sách**:

| | |
|---|---|
| **Tầng luôn đọc** | quy ước · dự án là gì · đang ở đâu. **Có** ngân sách, có cổng giữ |
| **Tầng đọc khi cần** | tra cứu, hồ sơ, nhật ký, bối cảnh. **Không** ngân sách — càng đầy càng tốt, miễn là không ai bị bắt đọc hết |

> ### Cách rẻ nhất để vượt ngân sách mà không ai thấy: để **lịch sử tích lại trong file trạng thái**.

Nó lớn lên mỗi tuần một ít, không lần nào đáng để ai kêu, và sau ba tháng thì phần *"đang ở đâu"*
chỉ còn là vài phần trăm của thứ bạn bắt mỗi phiên đọc.

📌 Chính kho sinh ra bộ kit này dính đúng chuyện đó: `STATE.md` phình tới **26.664 từ**, chiếm
**89%** tầng luôn đọc, trong khi dòng đầu của nó vẫn ghi *"mô tả hiện trạng, không phải lịch sử"*.
Không cổng nào thấy, cho tới khi có cổng này. Lịch sử đã chuyển sang `boi-canh/`, không xoá dòng nào.

Cổng in con số đo được **mỗi lần chạy**, kể cả khi xanh — một ngân sách chỉ nhìn thấy lúc vượt thì
không ai canh được nó.

---

## Giai đoạn, và cái mỗi giai đoạn cố ý hoãn lại

`STATE.md` nói bạn **đang ở** giai đoạn nào — một dòng. `GIAI-DOAN.md` nói có **những** giai đoạn
nào. Hai file, hai câu hỏi khác nhau, và cổng đối chiếu chúng: khi chúng nói hai tên khác nhau thì
**không file nào sai rõ ràng**, nên không ai sửa bên nào cả.

Một giai đoạn là **một câu hỏi chưa trả lời được**, không phải một ô trong danh sách quy trình. Dự
án một câu hỏi thì một giai đoạn — đừng nghĩ ra thêm cho đủ bộ.

> ### Trường nặng nhất không phải `TRONG DO`. Là `HOAN LAI`.

Một kế hoạch chỉ ghi *"giai đoạn này làm gì"* thì tháng sau sẽ có người kéo một việc của giai đoạn
sau vào giai đoạn này — rất hợp lý, rất thuyết phục — và không ai còn nhớ rằng nó đã được **cân
nhắc và gạt đi**, chứ không phải bị bỏ quên.

Đó là đường đi quen thuộc nhất tới chuyện **đập đi xây lại**: không phải vì ai đó lười, mà vì phạm
vi nở ra từng chút một cho tới lúc không còn chốt lại được nữa.

📌 `THOAT KHI` phải **đo được**: có một con số, một đường dẫn có thật, hoặc một người cụ thể làm
được một việc cụ thể. *"Xong hết task"* không dùng được — task là thứ bạn chọn, mục tiêu là thứ
phải thành thật.

---

## Trước khi cắm thêm một chỗ nối

Plugin, connector, MCP, khóa API. Hỏi một câu trước: **việc nào trong dự án này đang cần nó?** Trả
lời được thì ghi vào `KET-NOI.md`. Trả lời không được thì đừng cắm vào.

> ### Một chỗ nối không phải một tính năng. Nó là một **quyền**.

Thứ bạn thêm không phải *"khả năng gửi mail"*, mà là *"từ giờ con AI này gửi mail được"*. Hai câu đó
nghe giống nhau và hết giống nhau đúng lúc một thứ chạy sai.

Khác `CHO-DUA.md` chỗ nào: **chỗ dựa** là thứ mất thì mình chết. **Chỗ nối** là thứ mình với tới
được. Một thứ có thể là cả hai, và lúc đó nó nằm ở cả hai file — không phải trùng lặp.

Cổng đòi đúng ba thứ, và chỉ đòi khi chỗ nối đó **ghi** hoặc **tiêu tiền** được:

| | |
|---|---|
| `QUYEN` | một trong ba: `doc` · `ghi` · `tieu tien`. Một chữ tự nghĩ ra thì mỗi người hiểu một kiểu |
| `GIOI HAN` | cái gì nó **không** được làm, và cái gì chặn |
| `TAT RA SAO` | một dòng. Lúc cần đến dòng này thì không ai còn bình tĩnh đi tìm |

📌 Mục **"Cố ý KHÔNG nối"** đứng trước danh sách. Danh sách đã nối thì tự nó dài ra; danh sách **từ
chối** thì không ai viết hộ — và ba tháng nữa bạn sẽ nối lại đúng thứ hôm nay bạn đã từ chối.

---

## Trước khi dựng cái gì mất hơn nửa ngày

Tra xem có ai làm sẵn chưa. **Đọc giấy phép trước khi đọc code** — một thứ dùng được về kỹ thuật mà
không dùng được về giấy phép thì biết sớm rẻ hơn biết muộn.

Ghi vào `DA-TRA.md`, **kể cả khi kết luận là tự dựng**. Một mục là một **câu hỏi** đã tra, không
phải một công cụ: *"chọn thư viện biểu đồ nào"* là một mục, *"Chart.js"* thì không.

> ### Dòng đắt nhất không phải `CHON`. Là `DA LOAI`.

Ba tuần nữa sẽ có người hỏi *"thế đã xem cái X chưa?"*. Không có dòng nào trả lời thì bạn tra lại từ
đầu — và lần này có thể ra kết luận ngược, không phải vì sự thật đổi, mà vì lý do cũ đã mất.

Cổng bắt đúng ba chuyện: mục đã chọn mà không ghi đã loại gì · chọn thứ bên ngoài mà không ghi giấy
phép · giấy phép *không rõ* mà không có hạn xem lại. Ghi *"không rõ"* là **trung thực và được
phép** — để nó không có hạn mới là bỏ quên.

---

## Việc cuối cùng trước khi đóng máy

Thêm một mục vào **đầu** `NHAT-KY.md`. Ba dòng là đủ.

```
## 2026-09-17 — thử đổi cách lưu ảnh

DA LAM:     chuyển sang lưu ngoài, bỏ cột blob
BIET THEM:  bản cũ chậm không phải vì ảnh, là vì thiếu index
CON TREO:   chưa đo lại sau khi thêm index
HO SO:      `boi-canh/` — đặt tên YYYY-MM-DD-viec-gi.md
```

`QUYET-DINH/` giữ cái **đã chốt**. Nhật ký giữ cái **chưa chốt** — đã thử gì, hỏng ra sao, lúc đó
tưởng gì là đúng. Đó là phần không ai nhớ nổi sau ba tuần, và là phần khiến người ta **đập đi xây
lại lần thứ hai** vì không còn ai biết lần thứ nhất đã dừng ở đâu.

Dòng `HO SO` trỏ vào `boi-canh/` — chỗ để nguyên liệu thô. Cổng kiểm đúng chiều ngược lại: nhật ký
trỏ tới hồ sơ **không còn tồn tại** thì nó báo đỏ. Một kết luận không còn gì đỡ phía dưới là thứ
không tin được.

---

## Giới hạn, nói trước

- **Bộ kit này không kiểm code của bạn.** Nó kiểm *cách dự án tự giữ mình*. Test, build, lint là việc
  của dự án.
- **`--tu-kiem` chứng minh mỗi cổng bắt được ĐÚNG MỘT kiểu hỏng đã biết.** Không chứng minh cổng nào
  bắt được mọi thứ. Một cổng qua được nó vẫn có thể mù trước thứ khác.
- **Mọi thứ in ra là ASCII**, vì console Windows là cp1252 và `print` tiếng Việt có dấu thì
  `UnicodeEncodeError`. Đây là số đo trên máy thật, không phải phòng xa.
- **Cổng nhật ký chỉ kiểm được một nửa bằng `--tu-kiem`.** Phần "trỏ tới hồ sơ đã mất" thì có;
  phần "10 commit mà không ai ghi" thì không, vì bản chép sandbox không mang theo `.git`. Phần
  đó được thử riêng bằng tay, và giới hạn này in ra ngay trong dòng *KHÔNG chứng minh* của cổng.
- **Chưa ai ngoài tác giả dùng bộ này trên một dự án mới từ đầu tới cuối.**

---

## Giấy phép — hai giấy, và lý do

| Phần | Giấy phép |
|---|---|
| `khoi-tao.py`, `cong.py` | **MIT** — xem `LICENSE` |
| **Nội dung mẫu mà hai file đó viết vào dự án của bạn** | **CC0 1.0** — xem `LICENSE-TEMPLATES` |

Vì sao tách: mọi giấy phép phần mềm, kể cả MIT, **đều đòi ghi công**; CC0 là lựa chọn duy nhất
không đòi. Mà nội dung mẫu thì nằm bên trong `PROJECT.md` và `STATE.md` **của bạn** — bắt bạn mang
một dòng ghi công trong đó là một luật không ai tuân, và một luật không ai tuân thì tệ hơn không có.

Nói gọn: **giữ bộ công cụ có tên tác giả; những gì nó viết vào dự án bạn thì là của bạn.**

---

## Bộ này từ đâu ra

Nó được **rút ra** từ một khóa học tiếng Việt về cách chủ dự án giữ kiểm soát khi làm việc với AI —
không phải nghĩ ra rồi đem áp. Mỗi cổng truy được về một lần hỏng có thật, ghi trong sổ sẹo của
chính dự án đó.

Khóa học: <https://ai.thelong.tech>

Đóng góp: xem `CONTRIBUTING.md`. Thay đổi giữa các bản: xem `CHANGELOG.md`.
