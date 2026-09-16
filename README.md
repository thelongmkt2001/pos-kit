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
lại **16 lần tính tới 2026-09-16**, trong đó có những lần xảy ra **ngay trong lúc đang viết về nó**,
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
| **Phụ thuộc ngoài còn sống** *(`--ngoai`)* | URL đã khai báo mà chết | Nội dung sau URL còn đúng |

Cổng cuối cần mạng nên **tuỳ chọn** — để `python kit/cong.py` chạy được cả lúc không có Internet.

---

## Những file nó tạo, và mỗi file trả lời câu gì

Bộ mặc định:

| File | Câu hỏi nó trả lời | Đổi bao lâu một lần |
|---|---|---|
| `PROJECT.md` | Dự án là gì, và **KHÔNG** làm gì? | Hiếm |
| `STATE.md` | Đang ở đâu, việc kế tiếp? | Gần như mỗi phiên |
| `CLAUDE.md` | Làm việc ở đây theo quy ước gì? | Khi quy ước đổi |
| `QUYET-DINH/README.md` + `0001-mau.md` | Đã chốt gì, vì sao? | Khi quyết một chuyện khó lùi |
| `viec/MAU-VIEC.md` | Việc đang làm là gì, đi tới đâu? | Mỗi việc một tờ |
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

## Việc đầu tiên sau khi khởi tạo

**Không phải viết code.** Là điền `PROJECT.md`, nhất là mục **"KHÔNG phải mục tiêu"**.

Chỗ đó quan trọng hơn nó trông. Thứ bạn cố ý không làm sẽ bị đề nghị lại nhiều lần — và mỗi lần
không có dòng đó thì bạn phải cãi lại từ đầu.

---

## Giới hạn, nói trước

- **Bộ kit này không kiểm code của bạn.** Nó kiểm *cách dự án tự giữ mình*. Test, build, lint là việc
  của dự án.
- **`--tu-kiem` chứng minh mỗi cổng bắt được ĐÚNG MỘT kiểu hỏng đã biết.** Không chứng minh cổng nào
  bắt được mọi thứ. Một cổng qua được nó vẫn có thể mù trước thứ khác.
- **Mọi thứ in ra là ASCII**, vì console Windows là cp1252 và `print` tiếng Việt có dấu thì
  `UnicodeEncodeError`. Đây là số đo trên máy thật, không phải phòng xa.
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
