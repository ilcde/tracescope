# Hướng dẫn TraceScope

TraceScope 0.2 là công cụ thực thi và học bằng quan sát đã chạy được, **chưa hoàn thành toàn bộ đặc tả sản phẩm**. Xem `capabilities.json` và `REQUIREMENTS.md` để biết phạm vi đã kiểm chứng.

## Khởi động trên Windows

```powershell
.venv\Scripts\python.exe -m tracescope desktop --trusted-local
```

Ứng dụng mở bằng WebView2 gốc của Windows. `--trusted-local` cho phép chạy Python/JVM/mã gốc với quyền tệp và mạng của tài khoản hiện tại. Đây **không phải sandbox**. Bỏ cờ này để khóa thực thi mã gốc; WASM cục bộ vẫn dùng được. Không chạy mã nhập không đáng tin trong chế độ này.

Có thể chạy `serve --trusted-local` thay `desktop --trusted-local` và mở URL mà máy chạy in ra. Mã truy cập nằm trong fragment URL, được lưu theo phiên và gửi bằng tiêu đề Authorization. Mặc định máy chạy chỉ nghe loopback. Dừng máy chạy để thu hồi mã được sinh tự động.

Bản Windows đóng gói: `packages\TraceScope-Windows\TraceScope.exe desktop --trusted-local`. Giữ nguyên thư mục cùng `runtime`, `tracescope` và `dist`. Có sẵn Python và thư viện mô phỏng; bộ công cụ Java/Kotlin/C/C++/Rust cần cài riêng hoặc trỏ đường dẫn bằng biến `TRACESCOPE_*` mô tả trong hướng dẫn tiếng Anh.

## Quan sát chương trình

1. Chọn ngôn ngữ hoặc mở mã nguồn. Có thể sửa mọi ví dụ. Java dùng `Main.java` với lớp `Main`; Kotlin dùng `Main.kt`.
2. Đọc giới hạn quan sát phía trên trình soạn thảo. Thiết lập đầu vào chuẩn, mảng JSON tham số, cấu hình CPU và chế độ chạy.
3. Nhấn **Chạy và ghi vết** (F5). Tốc độ phát không điều khiển thời gian thực thi. Điểm dừng Python tạm dừng trước dòng; các bộ chuyển tiếp khác thu bản ghi có giới hạn rồi xem lại.
4. Kéo dòng thời gian hoặc dùng bước vào/qua/ra/lùi. Khi Python đang tạm dừng trực tiếp, các nút bước gửi lệnh gỡ lỗi. Khi xem lại, chúng chỉ đọc dữ liệu đã ghi. Không có thông tin độ sâu ngăn xếp thì không thể suy ra bước qua/ra thực sự.
5. Chọn nút có kiểu để xem giá trị, trạng thái, định danh và thông tin quan sát được. Định danh đối tượng logic không phải địa chỉ bộ nhớ. Hai tham chiếu cùng đối tượng dùng chung định danh.
6. Đổi giữa sơ đồ giá trị/đối tượng, đường đi đã quan sát và ngăn xếp lời gọi. Xuất SVG tạo ảnh chụp các giá trị kèm kiểu. Ctrl+F tìm trong mã; nhấn lề để bật điểm dừng.
7. Bytecode Python/JVM, JavaScript sinh ra và lệnh máy được ghi nhãn riêng. Chúng không thay thế cho nhau. Ánh xạ mã nguồn có thể thiếu, đặc biệt khi bật tối ưu.
8. Xuất/nhập JSON để xem lại ngoại tuyến. Không lặp I/O hay chạy lại chương trình. Mã đã sửa không thay đổi bản chụp cũ; nhấn xem mã của bản ghi để đối chiếu. Phiên hoàn tất cuối cùng được lưu trong IndexedDB.

## Số đo và độ phức tạp

Chế độ đo hiệu năng chạy một lần thực thi riêng, bỏ hook ghi câu lệnh hoặc trình gỡ lỗi khi có thể. Thu đầu ra vẫn có chi phí. Số đo JVM gồm khởi động lạnh, chưa phải benchmark ổn định theo JMH. Thời gian ghi vết gồm chi phí kiểm tra và chờ gỡ lỗi.

Bộ phân tích tĩnh Python chỉ chấp nhận tập con vô hướng/range có giới hạn, không có lời gọi chưa biết hiệu ứng. Có thể suy ra cận hằng số, tuyến tính, vòng lặp độc lập và vòng lặp tam giác theo mô hình chi phí đơn vị. Lời gọi ngoài, đệ quy chưa hỗ trợ và cận thay đổi trả về **chưa biết**. Không suy ra Big O chính xác cho mọi chương trình. Bộ nhớ phụ trợ tính ô vô hướng, không phải RSS hoặc độ dài số nguyên.

Thí nghiệm JavaScript/TypeScript đưa 16, 64, 256, 1024 vào `input()`, mỗi kích thước chạy ba lần riêng. Hiển thị trung vị, khoảng dao động và sai số khớp đường cong. Chương trình phải thực sự dùng giá trị đó làm kích thước. Khớp thực nghiệm không chứng minh cận xấu nhất.

## Hợp ngữ

Hỗ trợ cơ sở giảng dạy x86-16 real mode (tập lệnh 386+, không BIOS/DOS), x86-32/64, ARM32 ARM/Thumb, AArch64, RV32I và RV64I. Unicorn thực thi byte máy; Capstone giải mã đúng byte đó. RISC-V dùng bộ hợp dịch Zig/LLVM.

Mô phỏng ánh xạ 128 KiB, bắt đầu tại 0x1000, ngăn xếp ban đầu 0xf000. Không có hệ điều hành hoặc syscall. Với x86-64 nên dùng thanh ghi cơ sở để truy cập bộ nhớ; Keystone có thể giải mã `[địa chỉ]` thành địa chỉ tương đối RIP ở một số dạng. Luôn đối chiếu toán hạng đã giải mã. Hiệu ứng thanh ghi/bộ nhớ là quan sát thực tế, không phải chu kỳ CPU vật lý. Chưa tải và chạy ELF/PE tổng quát trong trình mô phỏng.

## Android

Cài `packages/TraceScope-debug.apk`. Đây là APK phát triển có ký debug và bật gỡ lỗi, chưa phải bản phát hành cửa hàng. JavaScript, TypeScript, HTML, CSS, soạn mã và xem lại dùng tài nguyên WASM đóng gói cục bộ. Mở tệp qua bộ chọn tài liệu Android; xuất tệp yêu cầu tạo tài liệu bằng cơ chế Android. Phiên hoàn tất cuối cùng được lưu cục bộ. Chưa có dịch vụ duy trì phiên trực tiếp khi hệ thống hủy activity.

Ghép nối thủ công bằng URL HTTPS và mã truy cập trong Thiết lập chạy. Chứng chỉ phải được Android tin cậy; không bỏ qua lỗi TLS. Biên dịch mã nặng diễn ra trên máy đã ghép nối, không phải Android. Chưa kiểm chứng trọn vẹn hành trình ghép nối TLS trên thiết bị. Kiểm thử máy ảo không chứng minh tương thích thiết bị vật lý Poco X6 Pro.

## Giới hạn và chẩn đoán

Chạy `.venv\Scripts\python.exe -m tracescope doctor` để kiểm tra bộ công cụ. Lỗi biên dịch giữ thông báo gốc và thời gian. Khi hủy hoặc vượt hạn mức, giữ lại phần bản ghi hợp lệ. Trạng thái thất bại có thể do chính chương trình ném ngoại lệ hoặc thoát khác 0.

Hạn mức gồm tối đa 5.000 sự kiện, 24 MB bản ghi, đầu ra 64 KiB ở các bộ ghi có kiểm soát, 120 giây thời gian máy chạy và hai phiên đồng thời. Windows Job giới hạn bộ nhớ committed toàn nhóm 1 GiB, 24 tiến trình và 60 giây CPU khi gán Job thành công. Các hạn mức này **không tạo ranh giới cách ly**. Hạn mức đầu ra ở mọi tiến trình biên dịch/benchmark còn chưa hoàn chỉnh.

Thuật ngữ: trace = bản ghi/vết thực thi; frame = khung lời gọi; heap = vùng nhớ động; stack = ngăn xếp; alias = tham chiếu cùng đối tượng; unavailable = không khả dụng; uncaptured = chưa ghi nhận; optimized out = bị tối ưu bỏ; replay = xem lại; bound = cận; empirical fit = khớp thực nghiệm.

## Sơ đồ nơ-ron và toàn màn hình

Chọn “Sơ đồ nơ-ron” để xem các nút có tên, kiểu và giá trị cùng đường nối chứa/tham chiếu từ dữ liệu đã ghi nhận. Đối tượng dùng chung chỉ xuất hiện một lần; đây không phải suy luận phụ thuộc dữ liệu hoặc mạng AI. Nút toàn màn hình mở rộng sơ đồ nhưng vẫn giữ điều khiển xem lại. Dùng phóng to/thu nhỏ hoặc “Vừa khung”; có thể xuất sơ đồ đang hiển thị thành SVG. Trên điện thoại, các nút được xếp dọc để dễ đọc.

## Dự án nhiều tệp

Mở nhiều tệp nguồn cùng lúc hoặc nhập JSON theo định dạng `tracescope-project/1`. Các tab dùng để sửa từng tệp; tệp chạy chính được chọn riêng trong Thiết lập chạy. “Lưu dự án” xuất toàn bộ tệp và cấu hình. Dự án được lưu cục bộ qua lần tải lại trong giới hạn dung lượng. Xem [PROJECTS.md](PROJECTS.md) để biết đường dẫn lồng nhau và định dạng mô-đun hỗ trợ.

Khi xem lại, trình soạn thảo hiển thị ảnh chụp của đúng tệp chứa sự kiện. “Trở lại mã đang sửa” phục hồi dự án hiện tại. Sửa tệp phụ cũng đánh dấu bản ghi cũ; phải chạy lại để quan sát thay đổi. Xem lại không sửa bản ghi và không lặp tác dụng I/O.

## Điều kiện điểm dừng và theo dõi Python

Đặt điểm dừng ở lề, rồi nhập điều kiện như `i >= 3 and total < 100` trong Thiết lập chạy. Điều kiện chỉ đọc biến nguyên thủy, hằng, phép so sánh, toán tử logic và số học có giới hạn. Không cho gọi hàm, đọc thuộc tính hoặc truy cập chỉ số; không chạy getter hay phương thức so sánh của người dùng. Giá trị thiếu hoặc không nguyên thủy làm điều kiện sai.

Ô theo dõi nhận tên biến ngăn cách bằng dấu phẩy, ví dụ `total, result`. Chương trình dừng khi biểu diễn đã ghi nhận của biến đổi tại ranh giới dòng/opcode. Đây không phải watchpoint phần cứng; thay đổi giữa hai lần chụp hoặc ngoài độ sâu giới hạn có thể không thấy. Chức năng hiện dành cho Python và áp dụng khi chạy lần kế tiếp.

## Cài đặt và WebUI

[WebUI công khai](https://ilcde.github.io/tracescope/) chạy JS/TS qua WASM và hiển thị HTML/CSS ngay trên thiết bị. Python, JVM, C/C++/Rust và hợp ngữ cần máy chạy riêng; nhập URL HTTPS và mã ghép nối trong Thiết lập chạy. Không nhập token GitHub vào ô mã ghép nối.

Hướng dẫn [INSTALL.md](INSTALL.md) có gói Windows, RPM Fedora 43/44, DEB Ubuntu 24.04, APK Android, cách cập nhật và vị trí dữ liệu. Máy chạy gốc mặc định bị khóa; `--trusted-local` cho chương trình quyền của tài khoản hiện tại, không phải sandbox. Kiểm thử container không thay thế kiểm chứng SELinux/Wayland hoặc thiết bị Android thật.
