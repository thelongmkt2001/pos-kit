# Góp vào pos-kit

Cảm ơn bạn đã đọc tới đây. Bộ này cố ý **nhỏ**, nên phần lớn đóng góp giá trị nhất không phải thêm
tính năng.

## Thứ được hoan nghênh nhất

**Kể lại một lần bộ kit này nói sai với bạn.**

Cụ thể là hai loại:

| Loại | Ví dụ |
|---|---|
| **Một cổng báo xanh trong khi có chuyện thật** | cổng bí mật không thấy một khóa vì nó đặt tên lạ |
| **Một cổng báo đỏ mà không có chuyện gì** | cổng kêu nhầm trên một dự án bình thường |

Loại thứ hai **quan trọng hơn** loại thứ nhất. Một cổng kêu nhầm sẽ bị tắt đi, và lúc bị tắt nó
thôi bắt luôn cả những ca thật.

Mở một issue kèm: bạn chạy lệnh gì, nó in ra gì, và bạn **mong** nó in ra gì.

## Nếu bạn muốn thêm một cổng

Bộ này có hai luật tự áp, và một cổng mới phải qua cả hai:

**1. Khai nó KHÔNG chứng minh được gì.** Mỗi cổng có `chung_minh` và `khong_chung_minh`. Dòng thứ
hai mới là dòng quan trọng — một câu nghe như lời bảo đảm mà thực chất nói ít hơn tự nó là một cái
bẫy.

**2. Chứng minh nó trượt được.** Mỗi cổng phải có hàm `pha` — cách cố ý phá đúng thứ nó sinh ra để
bắt. `python cong.py --tu-kiem` sẽ chép dự án sang thư mục tạm, gọi `pha`, và đòi mã thoát phải đổi.

> Một phép kiểm chưa bao giờ báo đỏ thì bạn chưa biết nó báo đỏ được không.

⚠️ Và một yêu cầu nữa, khó hơn nó nghe: **chạy cổng mới trên một dự án vừa khởi tạo và chưa điền
gì.** Nếu nó báo đỏ ở đó thì nó kêu nhầm ngay ngày đầu, và nó sẽ bị tắt. Chuyện này đã xảy ra hai
lần trong lúc dựng bộ này.

## Thứ gần như chắc chắn bị từ chối

- **Thêm một file mẫu mới.** Bộ này đã cắt từ 25 xuống còn danh sách hiện tại, bằng cách chấm trên
  một dự án thật. Một file mới cần một câu hỏi thật chưa có chỗ trả lời — không phải một chỗ trống
  trông có vẻ nên có.
- **Thêm phụ thuộc.** Thư viện chuẩn, không cài đặt gì. Đó là một nửa lý do bộ này dùng được.
- **Đổi mọi thứ in ra thành tiếng Việt có dấu.** Console Windows là cp1252; `print` tiếng Việt có
  dấu thì `UnicodeEncodeError`. Đây là số đo trên máy thật.

## Cách chạy thử trước khi gửi

```bash
python khoi-tao.py /tmp/thu-nghiem --day-du
cd /tmp/thu-nghiem
python kit/cong.py            # phai thoat 0 tren mot du an vua khoi tao
python kit/cong.py --tu-kiem  # moi cong phai chung minh duoc la truot duoc
```

Cả hai phải xanh **trước khi** bạn mở pull request.

## Ngôn ngữ

Nội dung mẫu và tài liệu viết **tiếng Việt**. Mã nguồn, chú thích và mọi thứ in ra màn hình viết
**không dấu** — xem lý do ở trên. Issue và pull request thì tiếng Việt hay tiếng Anh đều được.
