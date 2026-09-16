# Thay đổi giữa các bản

Theo lối [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), đánh số theo
[SemVer](https://semver.org/lang/vi/).

> **Vì sao file này tồn tại, khi dự án gốc cố ý không có changelog.**
> Trong dự án gốc, nhà của nhật ký thay đổi là **lời commit** — người đọc duy nhất là chính dự án
> đó. Công bố thì đổi người đọc: ai chép `cong.py` vào dự án của họ sẽ **không bao giờ nhìn thấy**
> lịch sử commit ở đây. Với họ, lời commit không phải một cái nhà, nó là một chỗ không tới được.

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
