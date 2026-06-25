Tên đề tài: **Nghiên cứu xây dựng mô hình middleware bảo mật kiểm soát truy cập thiết bị IoT trong hệ thống điều khiển sử dụng LLM Agent**

**I. Mục tiêu nghiên cứu của đề tài**

**1. Mục tiêu tổng quát**

Nghiên cứu các rủi ro an toàn thông tin trong hệ thống điều khiển thiết bị IoT sử dụng LLM Agent, từ đó xây dựng mô hình middleware bảo mật nhằm kiểm soát truy cập thiết bị IoT, phòng chống các hành vi truy cập trái phép và tấn công prompt injection, góp phần nâng cao mức độ an toàn cho hệ thống điều khiển thông minh.

**2. Mục tiêu cụ thể**

Đề tài hướng tới các mục tiêu sau:

1. Tổng quan kiến trúc hệ thống điều khiển IoT sử dụng LLM Agent.
2. Phân tích các nguy cơ an toàn thông tin trong mô hình LLM Agent điều khiển thiết bị IoT.
3. Nghiên cứu các kỹ thuật tấn công phổ biến vào hệ thống LLM Agent:
   * prompt injection
   * tool misuse
   * command manipulation
   * privilege escalation qua agent
4. Phân tích các mô hình kiểm soát truy cập thiết bị IoT hiện nay:
   * RBAC
   * ABAC
   * policy-based control
5. Đề xuất mô hình middleware bảo mật kiểm soát truy cập giữa LLM Agent và thiết bị IoT.
6. Xây dựng thử nghiệm middleware kiểm soát truy cập trong môi trường mô phỏng.
7. Đánh giá hiệu quả của mô hình middleware đề xuất.

**II. Đề cương chi tiết 3 chương**

(định dạng chuẩn cho chuyên đề ứng dụng / đồ án ATTT)

**CHƯƠNG 1**

TỔNG QUAN HỆ THỐNG ĐIỀU KHIỂN IoT SỬ DỤNG LLM AGENT VÀ CÁC RỦI RO AN TOÀN THÔNG TIN

**1.1. Tổng quan hệ thống Internet of Things (IoT)**

**1.1.1. Khái niệm hệ thống IoT**

* định nghĩa IoT
* thành phần hệ thống IoT
* mô hình kiến trúc IoT phổ biến

**1.1.2. Kiến trúc hệ thống điều khiển thiết bị IoT**

* kiến trúc cloud-based IoT
* edge-based IoT
* hybrid IoT architecture

**1.1.3. Các ứng dụng điều khiển IoT trong thực tế**

* smart home
* smart factory
* smart healthcare

**1.2. Tổng quan mô hình LLM Agent trong hệ thống điều khiển**

**1.2.1. Khái niệm mô hình ngôn ngữ lớn (LLM)**

* đặc điểm LLM
* khả năng suy luận và điều khiển tác vụ

**1.2.2. Kiến trúc LLM Agent**

* tool-using agent
* autonomous agent
* multi-step reasoning agent

**1.2.3. Vai trò của LLM Agent trong hệ thống điều khiển IoT**

* xử lý lệnh tự nhiên
* điều phối thiết bị
* hỗ trợ tự động hóa thông minh

**1.3. Các nguy cơ an toàn thông tin trong hệ thống IoT sử dụng LLM Agent**

**1.3.1. Tấn công prompt injection**

**1.3.2. Tấn công điều khiển trái phép thiết bị IoT**

**1.3.3. Tấn công leo thang đặc quyền thông qua agent**

**1.3.4. Rò rỉ dữ liệu trong hệ thống IoT**

**1.4. Vai trò của middleware bảo mật trong hệ thống điều khiển IoT**

**1.4.1. Khái niệm middleware bảo mật**

**1.4.2. Chức năng của middleware kiểm soát truy cập**

**1.4.3. Các mô hình middleware bảo mật hiện nay**

**CHƯƠNG 2**

PHÂN TÍCH YÊU CẦU BẢO MẬT VÀ MÔ HÌNH KIỂM SOÁT TRUY CẬP TRONG HỆ THỐNG IoT SỬ DỤNG LLM AGENT

**2.1. Phân tích kiến trúc hệ thống điều khiển IoT sử dụng LLM Agent**

**2.1.1. Mô hình kết nối giữa LLM Agent và thiết bị IoT**

**2.1.2. Luồng xử lý lệnh điều khiển thiết bị**

**2.1.3. Các điểm yếu bảo mật trong kiến trúc hệ thống**

**2.2. Phân tích yêu cầu kiểm soát truy cập thiết bị IoT**

**2.2.1. Xác thực truy cập thiết bị**

**2.2.2. Phân quyền truy cập thiết bị**

**2.2.3. Kiểm soát lệnh điều khiển thiết bị**

**2.3. Các mô hình kiểm soát truy cập áp dụng cho hệ thống IoT**

**2.3.1. Mô hình kiểm soát truy cập dựa trên vai trò (RBAC)**

**2.3.2. Mô hình kiểm soát truy cập dựa trên thuộc tính (ABAC)**

**2.3.3. Mô hình kiểm soát truy cập dựa trên chính sách (Policy-based access control)**

**2.4. Phân tích yêu cầu xây dựng middleware bảo mật**

**2.4.1. Yêu cầu chức năng**

* kiểm tra lệnh điều khiển
* kiểm soát quyền truy cập
* xác thực agent

**2.4.2. Yêu cầu phi chức năng**

* hiệu năng
* khả năng mở rộng
* khả năng tích hợp framework agent

**CHƯƠNG 3**

ĐỀ XUẤT MÔ HÌNH MIDDLEWARE BẢO MẬT KIỂM SOÁT TRUY CẬP THIẾT BỊ IoT TRONG HỆ THỐNG ĐIỀU KHIỂN SỬ DỤNG LLM AGENT

(đây là chương đóng góp chính của đề tài ⭐)

**3.1. Kiến trúc tổng thể mô hình middleware đề xuất**

**3.1.1. Mô hình kết nối middleware với LLM Agent**

**3.1.2. Mô hình kết nối middleware với thiết bị IoT**

**3.1.3. Luồng xử lý kiểm soát truy cập trong middleware**

**3.2. Thiết kế cơ chế kiểm soát truy cập trong middleware**

**3.2.1. Cơ chế xác thực LLM Agent**

**3.2.2. Cơ chế kiểm tra quyền truy cập thiết bị**

**3.2.3. Cơ chế kiểm tra hợp lệ lệnh điều khiển**

**3.2.4. Cơ chế phát hiện prompt injection**

**3.3. Xây dựng mô hình thử nghiệm middleware bảo mật**

**3.3.1. Môi trường thử nghiệm hệ thống**

**3.3.2. Kịch bản kiểm thử middleware**

**3.3.3. Triển khai middleware trong môi trường mô phỏng**

**3.4. Đánh giá hiệu quả mô hình đề xuất**

**3.4.1. Đánh giá khả năng kiểm soát truy cập thiết bị**

**3.4.2. Đánh giá khả năng phòng chống tấn công prompt injection**

**3.4.3. Đánh giá khả năng tích hợp hệ thống**

**3.5. Đề xuất hướng phát triển mở rộng**

**3.5.1. Mở rộng kiểm soát đa thiết bị IoT**

**3.5.2. Tích hợp cơ chế học máy phát hiện bất thường**

**3.5.3. Ứng dụng middleware trong hệ thống smart environment**