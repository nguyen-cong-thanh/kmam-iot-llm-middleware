# Project: KMAM LLM Middleware

Đồ án môn "Chuyên đề cơ sở hướng ứng dụng". Đề tài: **mô hình middleware bảo mật kiểm soát
truy cập thiết bị IoT trong hệ thống điều khiển dùng LLM Agent**. Hai sản phẩm song song:
**báo cáo** (`docs/`) và **thực nghiệm** (`src/`).

## Ngôn ngữ
- Báo cáo và tài liệu trong `docs/*.md`: **tiếng Việt**, văn phong học thuật.
- Trả lời chat với người dùng: **tiếng Việt**.
- Code, comment, tên định danh, commit message: **tiếng Anh**.
- Thuật ngữ kỹ thuật (prompt injection, RBAC, middleware…) giữ nguyên tiếng Anh trong báo cáo.

## Liêm chính học thuật (BẮT BUỘC — ưu tiên cao nhất)
- KHÔNG bịa số liệu thực nghiệm, bảng, biểu đồ, hay kết quả đánh giá.
- Mọi con số trong báo cáo phải đến từ output thật của code trong `src/`. Nếu chưa chạy được,
  để chỗ trống và ghi rõ `[TODO: số liệu từ thực nghiệm]` thay vì điền số tạm.
- KHÔNG bịa trích dẫn/tài liệu tham khảo. Chỉ ghi nguồn khi chắc chắn có thật; nếu không chắc,
  đánh dấu `[cần kiểm chứng]` để người dùng tự bổ sung.
- Khi tóm tắt kiến thức (định nghĩa IoT, LLM, RBAC…) được phép trình bày kiến thức chung,
  nhưng không gán cho một nguồn cụ thể nếu không chắc nguồn đó nói vậy.

## Báo cáo (docs/)
- `docs/outline.md` là **định hướng**, không phải khuôn cứng — được điều chỉnh/gộp/tách mục khi
  hợp lý, nhưng nên báo người dùng khi thay đổi cấu trúc lớn.
- Viết vào `docs/report.md`. Viết theo từng mục được yêu cầu, không tự ý viết tràn toàn bộ.
- **Viết theo từng phần/mục một, KHÔNG gộp cả chương trong một lần** để tránh chạm giới hạn
  output và tránh mỗi mục bị sơ sài. Viết xong một phần thì dừng cho người dùng xem rồi đi tiếp.
- Số liệu, hình, kết quả đánh giá ở Chương 3 phải khớp với thực nghiệm trong `src/`.

### Văn phong báo cáo
- **Ngôi viết khách quan, vô nhân**: tránh "em/tôi/nhóm". Dùng dạng bị động/vô nhân:
  "báo cáo này trình bày…", "middleware được thiết kế…".
- **Đoạn văn là chính**: viết thành đoạn liền mạch có lập luận; chỉ dùng gạch đầu dòng khi
  liệt kê/phân loại. Tránh kiểu trình bày như slide.
- **Súc tích, đúng trọng tâm**: đủ ý, tránh dài dòng lặp lại; mỗi mục tập trung luận điểm chính.
- **Thuật ngữ kỹ thuật giữ tiếng Anh** (prompt injection, RBAC, middleware…): lần xuất hiện đầu
  tiên kèm giải thích/bản EN ngắn trong ngoặc, các lần sau dùng thẳng EN.
- **Chỉ chú thích tiếng Anh khi thực sự cần** (tên riêng kỹ thuật, từ khóa tra cứu tài liệu).
  KHÔNG chú thích EN cho từ thông thường đã rõ nghĩa, ví dụ tránh viết "hành động (acting)",
  "suy luận (reasoning)".
- **KHÔNG BAO GIỜ dùng dấu chấm phẩy `;`** trong báo cáo. Tách thành câu riêng hoặc dùng dấu phẩy.
- **Lời nói đầu và tiêu đề các chương dùng Heading 1 (`#`)**; các mục con dùng heading cấp thấp hơn.

### Hình ảnh & bảng biểu
- Ảnh lưu trong thư mục **`docs/images/`**.
- Tiêu đề chương dùng **số La Mã**: "CHƯƠNG I", "CHƯƠNG II", "CHƯƠNG III".
- Hình và bảng đánh số dạng **`{số chương}.{số thứ tự} {tiêu đề}`**, trong đó số chương dùng
  **số Ả Rập** (khớp cách đánh mục 1.1, 2.3). Ví dụ: "Bảng 1.1 …", "Hình 2.3 …".
- **Tiêu đề bảng đặt PHÍA TRÊN bảng**; **tiêu đề hình đặt PHÍA DƯỚI hình**.

### Trích dẫn & tài liệu tham khảo (BẮT BUỘC)
- Báo cáo **luôn có mục "Tài liệu tham khảo" ở cuối**, cập nhật liên tục khi viết.
- Viết tới đâu tham khảo nguồn nào thì **chèn trích dẫn inline ngay tại đó** (ví dụ `[1]`,
  `[2]`) trỏ tới mục trong danh sách tham khảo cuối báo cáo.
- **Ưu tiên nguồn uy tín**: paper khoa học (IEEE/ACM/arXiv…), tiêu chuẩn (NIST, OWASP…),
  tài liệu/website chính thống (LangChain docs, OWASP LLM Top 10…). Tránh blog/nguồn không
  kiểm chứng.
- Áp dụng quy tắc liêm chính ở trên: chỉ ghi nguồn khi chắc chắn có thật; nếu không chắc
  thì đánh dấu `[cần kiểm chứng]` để người dùng tự xác nhận, KHÔNG bịa nguồn.

## Thực nghiệm (src/)
- Quản lý package bằng **`uv`** (`uv add`, `uv run`). KHÔNG dùng `pip` trực tiếp. Tôn trọng
  `pyproject.toml` và `.python-version` (Python 3.14).
- Middleware tích hợp **LangChain** (callbacks/tools/runnables theo API hiện hành của LangChain).
- Thiết bị IoT được **mô phỏng bằng code** (mock/simulator), không yêu cầu phần cứng thật.
- Logic kiểm soát truy cập (RBAC/ABAC/policy) và phát hiện prompt injection phải có **unit test**
  để tạo số liệu đánh giá có thể tái lập. Chạy test bằng `uv run`.
- Kết quả thực nghiệm dùng cho báo cáo nên xuất ra dạng tái lập được (script/log/bảng), không
  chỉ chép tay con số.

## Đồng bộ code ↔ report (BẮT BUỘC)
Code trong `src/` và nội dung trong `docs/report.md` phải **luôn đồng bộ** ở bốn khía cạnh:
**số liệu & kết quả đánh giá**, **kiến trúc & thiết kế**, **kịch bản kiểm thử**, và
**thuật ngữ & tên gọi**.

- **Nguồn chân lý = bên được thực hiện sau:**
  - Sau khi sửa code và chạy lại → cập nhật report cho khớp, gồm cả số liệu/output thật.
  - Sau khi sửa nội dung report (thiết kế/yêu cầu) → cập nhật code cho khớp, chạy lại, rồi cập
    nhật output trong report nếu cần.
- **Cơ chế:** khi một thay đổi làm bên còn lại bị lệch, **nêu rõ chỗ bị ảnh hưởng và HỎI người
  dùng trước khi cập nhật bên kia** (không tự ý sửa lan sang bên còn lại).
- Tên component/module/cơ chế dùng nhất quán giữa report và code (ví dụ tên class khớp tên
  trong sơ đồ kiến trúc).

## Quy ước làm việc
- **Thêm/sửa rule trong CLAUDE.md: PHẢI hỏi người dùng trước, được đồng ý rồi mới chỉnh.**
- **Memory: được tự ý thêm/sửa, không cần hỏi.**
- Trước khi đổi cấu trúc outline hoặc kiến trúc middleware lớn: hỏi người dùng.
- Không tự ý chạy lệnh ghi/cài đặt ngoài phạm vi yêu cầu; ưu tiên giải thích trước khi thực thi.
