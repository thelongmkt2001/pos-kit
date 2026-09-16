# Thay đổi giữa các bản

Theo lối [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), đánh số theo
[SemVer](https://semver.org/lang/vi/).

> **Vì sao file này tồn tại, khi dự án gốc cố ý không có changelog.**
> Trong dự án gốc, nhà của nhật ký thay đổi là **lời commit** — người đọc duy nhất là chính dự án
> đó. Công bố thì đổi người đọc: ai chép `cong.py` vào dự án của họ sẽ **không bao giờ nhìn thấy**
> lịch sử commit ở đây. Với họ, lời commit không phải một cái nhà, nó là một chỗ không tới được.

## [1.7.0] — 2026-09-17

Bộ nền **15 → 16 file**. Số cổng không đổi (16).

### Thêm

- **`hooks/pre-push`** — bộ kit dựng sẵn một git hook chạy `kit/cong.py` **trước mỗi lần đẩy lên**,
  và **huỷ lần đẩy** nếu có cổng nào đỏ. Bật một lần cho mỗi bản clone:

  ```bash
  git config core.hooksPath hooks
  ```

  Đo được: **0,7 giây** trên một dự án vừa khởi tạo. Đã chứng minh hai chiều trên một dự án thật có
  remote — đẩy sạch thì qua, gieo một trạng thái ngoài danh sách thì chặn với mã thoát 1.

  Hook tự chọn `.venv` của dự án nếu có. Gọi `python` trần ở một dự án có môi trường riêng thì mọi
  phép kiểm hỏng vì thiếu thư viện — **đỏ vì lý do sai**, còn tệ hơn không có hook.

  ⚠️ Đây là một cái **rào**, không phải một cái **khoá**. `git push --no-verify` bỏ qua hoàn toàn —
  cũng đã đo. Nó chặn cái **quên**, không chặn cái **cố ý**.

  `khoi-tao.py` bật luôn bit thực thi cho file này: trên Linux/macOS thiếu bit đó thì git **im lặng
  bỏ qua** hook, và một hook bị bỏ qua không khác gì một hook không tồn tại.

### Sửa

- **`bo-qua.txt` biết miễn trừ ĐÍCH của một lệnh**, không chỉ miễn trừ cả file. Dòng bắt đầu bằng
  `-> ` là một đích được tha, ví dụ `-> pos-kit/`.

  Vì sao cần: một file tài liệu phục vụ hai kho sẽ có đúng một lệnh sai ở kho này và đúng ở kho kia.
  Miễn trừ cả file thì những lệnh **đúng** trong đó cũng thôi được kiểm — báo ít hơn sự thật. Khai
  báo này vẫn được **in ra mỗi lần chạy**, như mọi miễn trừ khác.

### Nâng từ 1.6.0

Chép lại `cong.py` và `khoi-tao.py`, rồi `python pos-kit/khoi-tao.py .` — nó bỏ qua file đã có và
chỉ tạo `hooks/pre-push`. Không cổng nào đỏ thêm vì bước này.

## [1.6.0] — 2026-09-17

Bản lớn. Bộ nền **8 → 15 file**, số cổng **10 → 16**.

Các bản 1.1.0–1.5.0 là bước trung gian, **chưa bao giờ công bố** — sáu lô làm liền trong một ngày,
gộp lại thành bản này để người dùng không phải đuổi theo một thứ đang chạy.

### Nâng từ 1.0.x lên: ba bước, theo đúng thứ tự

```bash
cp pos-kit/cong.py kit/cong.py       # chép bộ cổng mới vào dự án của bạn
mv CLAUDE.md AGENTS.md               # quy ước cũ của BẠN trở thành bản chính
python pos-kit/khoi-tao.py .         # tạo phần còn thiếu, BỎ QUA file đã có
```

⚠️ **Bước hai bắt buộc, và phải đứng trước bước ba.** Bỏ nó thì `khoi-tao.py` tạo một `AGENTS.md`
mới bên cạnh `CLAUDE.md` cũ của bạn, thành **hai bản đầy** — và cổng *Quy uoc toi duoc ca hai loai
cong cu* báo đỏ, đúng như nó phải làm.

Bản nháp của mục changelog này ban đầu hứa *"không có gì đỏ lên chỉ vì bạn nâng bản"*. Chạy thử
trên một dự án dựng bằng bản cũ thì nó **đỏ ngay**. Lời hứa bị thay bằng ba dòng lệnh ở trên, và
ba dòng đó đã chạy: 15 cổng xanh, thoát 0.

Năm file còn lại — `DA-TRA.md`, `KET-NOI.md`, `GIAI-DOAN.md`, `NGAN-SACH.md`, `CLAUDE.md` (bản
trỏ) — được tạo mới, và các cổng của chúng **im lặng** khi bạn chưa điền gì.

### Thêm

- **`NHAT-KY.md` + `boi-canh/`** — nhật ký làm việc, và chỗ để nguyên liệu thô. `QUYET-DINH/` giữ
  cái *đã chốt*; nhật ký giữ cái *chưa chốt*: đã thử gì, hỏng ra sao, vì sao đổi hướng.
  Cổng bắt **nhật ký nói dối** (trỏ tới hồ sơ đã mất) và **nhật ký dừng lại** (kho chạy tiếp 10
  commit mà không ai ghi).
- **`AGENTS.md` là bản chính, `CLAUDE.md` là một dòng trỏ tới nó.** Đo được: không công cụ nào đọc
  cả hai tên. Thiếu tên nào thì với công cụ đó, quy ước của bạn là **một thứ vô hình** — và nó im
  lặng y hệt lúc quy ước có mà không có tác dụng. Cổng bắt việc thiếu một tên, **và** việc chép nội
  dung sang cả hai (hai nguồn sự thật).
- **`DA-TRA.md`** — tra trước khi dựng. Cổng đòi dòng **`DA LOAI`**, không phải dòng `CHON`: một sổ
  chỉ ghi cái đã chọn thì không ngăn được lần tra lại. Lấy code ngoài mà không ghi giấy phép cũng
  đỏ; ghi *"không rõ"* thì được, nhưng phải có hạn xem lại.
- **`KET-NOI.md`** — plugin, connector, MCP, khoá API. *Một chỗ nối không phải một tính năng, nó là
  một **quyền**.* Cổng đòi `QUYEN` là một trong `doc` / `ghi` / `tieu tien`, và chỗ nào **ghi** được
  thì phải có giới hạn lẫn **cách tắt**.
- **`GIAI-DOAN.md`** — dãy giai đoạn. Trường nặng nhất là **`HOAN LAI`**: cái mỗi giai đoạn *cố ý*
  để lại. Cổng đòi điều kiện thoát **đo được**, đúng một giai đoạn đang chạy, và tên đó **khớp với
  `STATE.md`**.
- **`NGAN-SACH.md`** — ngân sách cho tầng **luôn đọc**. Cái đắt nhất không phải file dài nhất, là
  file được đọc lại mỗi phiên. Cổng in con số đo được **mỗi lần chạy**, kể cả khi xanh.

### Sửa

- Hai cổng từng **xanh vì lý do sai**, cả hai bắt được bằng cách gọi thẳng cổng ra đọc thông báo
  trên từng nhánh — kể cả nhánh bắt buộc phải xanh:
  - tra khoá trường bằng chữ hoa trong khi hàm bỏ dấu trả về chữ thường, nên **mọi mục đều bị bỏ
    qua** và cổng báo *"không thấy gì sai"* trong khi ý nó là *"tôi không thấy gì cả"*;
  - khớp trạng thái bằng **chuỗi con**, nên `"sắp xong"` được tính là `"xong"`. Nay mọi trường gọi
    tên được đều khớp **bằng**, qua một hàm chung.

### Đo

Chép từ GitHub về, dựng một dự án mới: **21 file**, `python kit/cong.py` thoát 0 ngay ngày đầu —
không cổng nào kêu nhầm — và `--tu-kiem` chứng minh **15/15** cổng trượt được (cổng thứ 16 cần mạng).

## [1.0.1] — 2026-09-17

Chỉ sửa chữ, không đổi hành vi. Bạn đã chép `cong.py` về dự án rồi thì **không cần làm gì** —
trừ khi muốn con số phiên bản in ra cho khớp.

### Sửa

- Sổ sẹo của dự án gốc ghi thêm một trường hợp: một **lời hứa về cách kiểm, chưa bao giờ được
  kiểm**. Con số trong `README.md` và trong đầu `cong.py` đổi từ 16 thành **17**.

## [1.0.0] — 2026-09-16

Bản công bố đầu tiên. Trước đó bộ này chỉ sống bên trong kho khóa học.

### Có gì

- `khoi-tao.py` — dựng bộ tối thiểu cho một dự án mới: 8 file, thêm 6 nữa với `--day-du`, và tự
  chép `cong.py` vào dự án để nó chạy độc lập.
- `cong.py` — mười cổng kiểm trong một file, cộng `--tu-kiem` tự phá một bản chép để chứng minh
  từng cổng **trượt được**.
- Hai luật bộ kit tự áp: mỗi cổng khai nó **không** chứng minh được gì, và mỗi cổng phải chứng minh
  được là nó trượt được.

### Giấy phép

- `khoi-tao.py`, `cong.py` — **MIT**.
- Nội dung mẫu hai file đó viết vào dự án của bạn — **CC0 1.0**, không cần ghi công. Lý do ở
  `LICENSE-TEMPLATES`.

### Biết trước

- Chưa ai ngoài tác giả dùng bộ này trên một dự án mới từ đầu tới cuối.
- `--tu-kiem` chứng minh mỗi cổng bắt được **đúng một** kiểu hỏng đã biết, không chứng minh nó bắt
  được mọi thứ.
