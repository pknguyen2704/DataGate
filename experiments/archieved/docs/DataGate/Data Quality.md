![[Pasted image 20260413083025.png]]

Modern data stack

- Thực hiện giám sát chất lượng dữ liệu bằng phương pháp học máy không giám sát
- Giải pháp này tự động học các ngưỡng thích hợp để xác định xem một thay đổi về dữ liệu có đủ lớn để báo hiệu vấn đề về chất lượng dữ liệu hay không

Thách thức
- Xây dựng mô hình
- Đảm bảo hoạt động trên nhiều loại dữ liệu thực tế mà không đưa ra cảnh báo quá mức hoặc thiếu chính xác

## Chapter 2
Chiến lược giám sát chất lượng dữ liệu và vai trò của việc tự động hóa

### Chiến lược giám sát chất lượng dữ liệu phải đáp ứng được
![[Pasted image 20260413090303.png]]
- Alert Fatigue: 
	- không cảnh báo về một vấn đề thực sự (âm tính giả)
	- cảnh báo về một vấn đề mà người dùng không quan tâm hoặc thực sự không phải là vấn đề (dương tính giả)
	![[Pasted image 20260413090608.png]]
	
### Data observability
- Cần nhưng chưa đủ
- Bản chất là thực hiện việc quan sát dữ liệu toàn diện từ các siêu dữ liệu của các bảng chứ không phải là nội dung của dữ liệu
- Truy cập các thông tin về metadata như 
	- Thời gian cập nhật lần cuối
	- Số hàng
	- Tên cột
	- Loại cột
### Các phương pháp truyền thống
- Giám sát thủ công
- Giám sát dựa trên các luật
- Giám sát bằng các chỉ số của dữ liệu (tỷ lệ null, tỷ lệ trùng lặp, giá trị trung bình, min/max,...)
- Giám sát theo chuooxi thời gian

## Tự động hóa giám sát chất lượng dữ liệu bằng Machine Learning không giám sát
- Học máy không giám sát: mô hình không có nhãn do con người cung cấp, chỉ có dữ liệu cùng với các mẫu và mối quan hệ vốn có trong dữ liệu, mô hình sẽ tự học từ dữ liệu mới dựa trên những gì đã quan sát được trước đó
- Học máy không giám sát phù hợp bởi:
	- bắt đầu giám sát dataset mà không cần thiết lập ban đầu
	- Tự học và thích nghi dữ liệu thay đổi theo thời gian
	- Có thể tinh chỉnh để phát hiện các vấn đề phức tạp như
		- Tỷ lệ giá trị null trong một nhóm cột tăng lên
		- Một segment dữ liệu cụ thể biến mất hoặc có ít bản ghi hơn dự kiến
		- Phân phối của một cột thay đổi đáng kể (điểm tín dụng bị cao bất thường)
		- Mối quan hệ nhiều cột thay đổi (trước đây các cột cộng lại bằng nhau nhưng giờ không còn đúng với một số bản ghi)
- Điểm mạnh nhất của học máy không giám sát chính là **phát hiện sự thay đổi trong mối quan hệ giữa các dữ liệu trong toàn bộ bảng**
- So với metric hay rule truyền thống, một mô hình có thể
	- Phát hiện nhiều loại vấn đề về chất lượng dữ liệu lớn, kể cả những vấn đề mà con người chưa nghĩ tới
	- Tự động giảm nhiễu cảnh báo lặp lại
	- Gom nhiều vấn đề liên quan đến nhiều cột thành một sự cố duy nhất thay vì các cảnh báo rời rạc
- Các tiếp cận này giúp cho
	- Giảm đáng kể noise (cảnh báo ngu)
	- Tăng độ chính xác và hữu ích của cảnh báo
	- Cải thiện an toàn và trải nghiệm người dùng
	- Rule và metrics giống như hệ thống cảnh báo đơn giản, UML giuống như một hệ thống hiểu ngữ cảnh -> giúp phát hiện vấn đề chính xác hơn, itys nhiễu hơn và hiệu quả hơn ở quy mô lớn
- Điểm yếu
	- Không phát hiện tốt ra kim trong đống cỏ
		- Bỏ xót những lỗi rất hiếm, chỉ cần một bản ghi vi phạm, rule sẽ phát hiện được còn UML thì có thể không nhìn thấy
	- Không phát hiện được lỗi tồn tại từ lâu
		- UML tập trung vào thay đổi mới tỏng dữ liệu
	- Không ưu tiên những phần dữ liệu quan trọng
		- Coi mọi cột và mọi dòng là như nhau
-> Dù manhju mã nhưng ML không phải là hoàn hảo, một chiến lược tốt cần kết hợp
	Rules based
	Metric monitoring
	UML
### Cách tiếp cận đúng đắn
- Sinh ra những rules cơ bản và phải cho phép người dùng tự định nghĩa các rule của mình theo hiểu biết về nghiệp vụ -> Chỉ tạo những rule thực sự quan trọng → giảm false positive và giảm chi phí maintain (không nên tự động hóa nhưng có thể predefine)

## 4 trụ cốt cho giám sát chất lượng dữ liệu
![[Pasted image 20260413094403.png]]
- Triển khai Data obserbility
- Triển khai UML (Tự động)
- Triển khai Rule based testing
- Metrics monitoring
	- Theo dõi các chỉ số quan trọng và các segment cụ thể
- Tác dụng
	- Có thể đạt được mục tiêu: Phát hiện, cảnh báo, xử lý, mở rộng
- Mang lại:
	- Độ bao phủ cao cho rủi ro chất lượng dữ liệu
	- Ít cảnh báo sai
	- Giảm alert ngu

## Tự động giám sát chất lượng dữ liệu bằng học máy
- So với phương pháp thống kê, so với rules và metric monitoring
- Chúng ta sẽ làm một giải pháp
	- Huấn luyện model
	- Phát triển model
	- Sử dụng model để phát hiện lỗi chất lượng dữ liệu
	- Xác định mức độ nghiêm trọng
	- Xác định vị trí lỗi trong dữ liệu
- Chương này sẽ
	- Giải thích phương pháp ML phù hợp nhất
	- Trình bài các bước triển khai
- Trả lời thêm
	- Lấy bao nhiêu sample là đủ
	- Làm sao để output có thể giải thích được
### Yêu cầu
- Độ nhạy
	- Khả năng đo lường của mô hình ML trong việc phát hiện true pos
	- Phát hiện được nhiêu loại lỗi chất lượng dữ liệu khác nhau
	- Áp dụng tốt trên dữ liệu bảng trong thực tế
	- Phát hiện các thay đổi ảnh hưởng đến lớn hơn 1% số bản ghi
	- Thay đổi > 1% là các thay đối quan trọng, lỗi lớn, shock hoặc scar trong dữ liệu
- Độ đặc hiệu
	- Đo lường khả năng của mô hình trong việc tránh tạo ra các cảnh báo sai
		- Model học seasonality
		- Hiểu correlation
		- Tự điều chỉnh theo dữ liệu
- Tính minh bạch
	- Giải thích được
	- Giúp người dùng tìm ra root cause
- Khả năng mở rộng
	- Không cần cấu hình thủ công ban đầu
	- Không cần tuning liên tục
	- Query Footprint thấp
	- Có thể chạy trên hạ tàng rẻ bên ngoài
- Model không cần phải phát hiện từ record lỗi: Việc này áp dụng rules base
- không cần xử lý realtime -> chạy theo batch
- Không hoạt động nếu không có yếu tố thời gian
	- Cần theo dõi dữ liệu theo thời gian

### Giám sát chất lượng dữ liệu khôn phải là phát hiện ngoại lai
- Phát hiện ngoại lai để tìm ra bất thường, phát hiện outlier có thể sử dụng ML nhằm tìm ra các điểm bất thường trong dữ liệu. Tuy nhiên chỉ tương đồng với monitoring ở đó
- Thực tế, mọi tập dữ liệu đều có outlier nhưng không nhất thiết phải là lỗi về chất lượng dữ liệu
- Để phát hiện vấn đề về chất lượng dữ liệu, ta cần biết khi nào xảy ra sự thay đổi cấu trúc đột ngộ trong phân phối dữ liệu
	- Trước đây dữ liệu có phân phối, pattern hoặc mối quan hệ nhất định
	- Và hiện tại những đặc điểm đó có thay đổi đáng kế
- Lúc này các outlier vẫn tồn tại tự nhiên trong dữ liệu, vì vật phát hiện outlier và giám sát chất lượng dữ liệu là hai bài toán khác nhau
- Những yếu tố feature engineering và tuning mô hình có vai trò quyết định giữa một hệ thống hiệu quả hoặc hệ thống gây ra quá ít hoặc quá nhiều cảnh báo
- Mục tiêu là xây dựng mô hình ML phát hiện những thay đổi bất thường trong dữ liệu mà không cần con người gán nhãn trước thế nào là lỗi trong chất lượng dữ liệu

### Ý tưởng chính
- Mỗi ngày có một snapshot về dữ liệu
- Sau đó huấn luyện một classifier để dự đoán: "Dữ liệu ngày có phải từ hôm nay hay không"
	- Nếu không bất thường gì về mặt thống kê, thì việc phân biệt hôm nay và các ngày còn lại thì gần như là không thể
	- Nếu train được model dự đoán chính xác, tức là dữ liệu hôm nay có điều gì đó khác thường, sự khác biệt này đủ lớn và có ý nghĩa
	- Phương pháp hỗ trợ đo được mức độ nghiệp trọng của thay đổi
	- Đặt thresshold để tránh alert nhầm
	- Giải thích được nguyên nhân 
- Lưu ý
	- Có những thay đổi lớn nhưng không quan trọng: ví dụ thời gian hay các thay đổi không quan trọng với bussiness
- Các bước tiếp theo
	- Lấy mẫu
	- Feature Encoding
	- Model Develop
	- Model Explainability
#### Lấy mẫu
- Bước đầu tiên để lấy mẫu từ toàn bộ dữ liệu
	- **“Hôm nay” (label = 1)** – dữ liệu cần kiểm tra
	- **“Không phải hôm nay” (label = 0)** – dữ liệu lịch sử để so sánh
- Dữ liệu không phải hôm nay nên bao gồm nhiều mốc thời gian
	- Hôm qua (hoặc lần cập nhật gần nhất) -> để phát hiện thay đổi đột ngột
	- Các thời điểm cùng chu kỳ: cùng ngày trong tuần/năm -> để xử lý tính vụ mùa
- Ví dụ, với dataset có 150k–250k dòng/ngày, bạn có thể lấy:
	- 10,000 dòng từ ngày cần kiểm tra
	- 10,000 dòng từ hôm qua
	- 10,000 dòng từ 1 tuần trước
	- 10,000 dòng từ 2 tuần trước
- Tuy nhiên nếu so sánh một ngày trong quá khứ vốn đã có lỗi thì có thể gặp shadow anomally
	- Ví dụ tuần trước bị lỗi, so sánh hôm nay với tuần trước có thêm nhiều -> không phải tăng đột biến mà do tuần trước mất
	- Cách giải quyết: Lấy mẫu từ nhiều ngày trong quá khứ hoặc loại bỏ các ngày có anomaly mạnh
- kích thước mẫu
	- Tối thiểu 100 record trên ngày để có ý nghĩa
	- Thực tế: 10000 record một ngày
		- Có thể phát hiện thay đổi ảnh hưởng từ 1 đến 5% dữ liệu
	- Trên 100000 -> cải thiện rất ít
	- 1000000 record -> Tốn tài nguyên , không đáng trừ khi
		- Data rất ổn định
		- Cần detect thay đổi rất nhỏ (~0,1%)
	- Quan trọng:
		- Khong lấy theo tỷ lệ (ví dụ 10%), chỉ cần sample ngẫu nhiên đủ lớn là đại diện tốt, bất kể dataset lớn cỡ nào

- Vấn đề bias
	- Sample phải hoàn toàn ngẫu nhiên nếu không sẽ bị bias
	- Tối ưu hiệu năng
		- Sampling tốn tài nguyên vì bảng có hàng tỷ dòng và nhiều cột
#### Feature Encoding
- Các mô hình k học trực tiếp từ dữ liệu thô mà học từ dạng các đặc trưng số -> Biến đổi thành các tín hiệu mà mô hình có thể sử dụng. Cách bạn biến đổi dữ liệu thô có ảnh hưởng đến hiệu năng của mô hình, cần đòi hỏi kiến thức và hiểu biết về domain
- Cách hoạt động
	- Mỗi bản ghi trong sample có nhiều cột, có thể ở dạng int, float, string, boolean, date,timestamp, hoặc nhiều kiểu phức tạo
	- Cần có một pipeline
		- Duyệt từng cột, nếu cột phức tạp thì phải tách thành các cột con
		- Trích xuất thông tin hữu ích, chuyển thành ma trận số để đưa vào model
	- Lưu ý
		- Gán nhãn 0 là dữ liệu cũ
		- 1 là dữ liệu hôm nay
- Các encoder khuyến nghị
	- Numeric: Boolean, int, float -> đưa về float
	- Frequency: Tần suất xuất hiện của mỗi giá trị trong sample -> giúp phát hiện lỗi thay đổi phân phối 
	- IsNull: Biến nhị phân
		- 1 = Null
		- 0 = không null
		--> giúp phát hiện lỗi missing dữ liệu
	- Timedelta:
		- - Khoảng thời gian giây giờ một timestampe và thời điểm tạo record -> phát hiện delay, lag hoặc thay đổi pipeline
	- SecondOfDay
		- Thời điểm trong ngày -> bắt partern theo giờ
	- One-Hot Encoding
		- Biến các categorical thành vector nhị phân -> giúp model hiểu các category
- Lưu ý về các encoder nâng cao
	- Một số kỹ thuật TF-IDF, mean coding, PCA, Laplace smoothing thường không phù hợp do không hiệu quả với tree-based models, cần nhiều domain knowledge, khó giải thích đặc trưng
- Cân bằng sức mạnh và khả năng giải thích
	- Nếu encoding quá phức tạp thì gây khó hiểu, khó debug, khó giải thích cho user
- Feature coding phải tự động, có ý nghĩa, dễ giải thích
#### Phát triển mô hình
- Để đáp ứng yêu cầu về khả năng mở rộng và linh hoạt trong thực tế, cần phải một mô hình huấn luyện nhanh, suy luận nhanh, có thể hoạt động với mẫu dữ liệu nhỏ, khả năng tổng quát hóa tốt cho dữ liệu dạng bảng
- Lựa chọn tốt nhất là gradient boosting với XGBoost
- Mô hình hoạt động như chuỗi các cây quyêt ssinhfj
- Ưu điểm
	- Số lượng tham số cần tinh chỉnh ít (chủ yếu là learning rate và độ phức tạp của cây)
	- Huấn luyện nhanh ngay cả với hàng nghìn hoặc hàng triệu bảng khác nhau
- Nhược điểm
	- Cần feature engineering (thiết kế đặc trung đầu vào), tốn công sức và chuyên môn
- Do mô hình có thể lặp vô hạn, nên cần
	- Giới hạn số lượng cây
	- Đánh giá hiệu suất sau mỗi bước
- Cách làm
	- Tác một phần dữ liệu làm tập validation
	- Theo dõi lỗi (loss) trên tập train và test
- Các trường hợp chính
	- không có bất thường
		- Train không cải thiện nhiều
		- Test nhanh chóng tệ đi
			-> Dữ liệu hôm nay bình thường
	- Dữ liệu chưa hội tụ
		- Train và test đều tiếp tục cải thiện -> Cân thêm cây hoặc tăng learning rate
	- Tối ưu 
		- Traing và test cùng cải thiện
		- Sau đó test bắt đầu xấu đi
			- Dừng lại tại thời điểm test là tốt nhất
- Hiệu quả tính toán
	- Dữ liệu lớn, hàng tỷ bản ghi, để tránh chi phí cao cần
	- Giới hạn số lượng abrn ghi (sampling) -> chi phí dựa vào số cột
	- Số cột có thể rất lớn
	- CÁc tối ưu
		- Chỉ query dữ liệu theo từng ngày và lưu snapshot
		- Sampling trực tiếp trong warehouse
		- Giới hạn
			- Độ sâu của câu
			- Số lượng cây
		- Dừng sớm nếu test error tăng
		- Tối ưu huấn hiện
			- Encoding sparse
			- multiprocessing
			- GPU nếu cần
#### Giải thích kết quả của mô hình
- Giải thích kết quả phát hiện của mô hình
	- cho biết mức độ bất thường của dữ liệu ngày hôm nay, giúp tinh chỉnh hệ thống để tránh tình trnjag quá nhiều cảnh báo, mức độ nghiêm trọng sẽ giúp người dùng ưu tiên xử lý
	- Cho bạn biết bất thường nằm ở đâu trong dữ liệu
- Cách hoạt động
	- Ý tưởng chính là tính toán điểm đóng góp cho từng ô dữ liệu, thể hiện mức độ nó ảnh hưởng đến khả năng dự đoán của mô hình
	- Có nhiều phương pháp nhưng ở đây dung SHAP về cơ bản là xấp xỉ mô hình bằng một mô hình tuyến tính cụ bộ để hiểu đóng góp của từng feature
	- Ví dụ
		- Giả sử dữ liệu giao dịch thẻ tín dụng
		- Lấy 10000 bản ghi hôm qua và hôm nay, huấn luyện mô hình dự đoán bản ghi thuộc ngày nào
		- Dự đoán xong bạn có xác suất một record thuộc today, thì thay vì dùng xác xuất trực tiếp thì dùng logs odds
			- Log odds có thể biểu diễn tuyến tính -> Phân tích bằng SHAP
	- Phân rã bằng SHAP
		- Phân ra log odds thành tổng đóng góp của từng cột, một record có xác suất 78% là ngày hôm nay thì SHAP cho thấy các cột đóng góp lớn nhất là cột naofg
	- Anomlly Score (điểm bất thường)
		- Sau khi chuẩn hóa và tinh chỉnh SHAP thì sẽ thu được anomally score, điều này rất mạnh vì có thể
		- Tính được ở nhiều mức
			- Cell
			- Row
			- Segment
			- Column
			- Toàn bảng
		- Mục tiêu
			- Tìm ra record bất thường nhất
			- Tìm cột bất thường nhất
			- Tìm segment lỗi
			- Phát hiện correlation giữa các cột
	- Trực quan hóa 
		- ngay cả khi không có vấn đề lớn thì anomaly score vẫn hữu ích, có thể vẽ biểu đồ để đặt bất thường vào ngữ cảnh
	- Phân loại mức độ bất thường, từ rất nhỏ -> cực lớn
		- - **Minimal (Tối thiểu)**  
		    Hầu như không có thay đổi đáng kể trong dữ liệu.
		- **Weak (Yếu)**  
		    Một tỷ lệ nhỏ dữ liệu bị ảnh hưởng bởi thay đổi cần phân tích kỹ mới phát hiện được.
		- **Moderate (Trung bình)**  
		    Một phần nhỏ dữ liệu bị ảnh hưởng bởi thay đổi rõ ràng, hoặc một phần vừa phải bị ảnh hưởng bởi thay đổi có thể giải thích đơn giản.
		- **Strong (Mạnh)**  
		    Một phần đáng kể dữ liệu bị ảnh hưởng bởi thay đổi rõ ràng, hoặc phần lớn dữ liệu bị ảnh hưởng bởi thay đổi có thể giải thích được (dù ban đầu chưa очевид).
		- **Severe (Nghiêm trọng)**  
		    Phần lớn dữ liệu bị ảnh hưởng bởi một thay đổi rõ ràng.
		- **Extreme (Cực đoan)**  
		    Gần như toàn bộ dữ liệu trong ngày bị ảnh hưởng bởi thay đổi.
			
```
# Import chung
import pandas as pd
import datetime as dt
import xgboost as xgb
from sklearn.model_selection import train_test_split
from shap import TreeExplainer

# Import các module giả định
from data_access import query_random_sample
from feature_engineering import determine_features, encode_feature
from explainability import compute_column_scores

def detect_anomalies(
    table: str,
    time_column: str,
    current_date: dt.date,
    prior_date: dt.date,
    sample_size: int
) -> dict[str, float]:

```
Ở đây ta định nghĩa một hàm (mã giả) để phát hiện bất thường bằng cách:
- Lấy mẫu dữ liệu từ hai ngày khác nhau
- Huấn luyện mô hình
- Tính toán anomaly score
**Tham số đầu vào:**
- `table`: tên bảng dữ liệu
- `time_column`: cột thời gian dùng để lọc dữ liệu
- `current_date`: ngày hiện tại cần kiểm tra
- `prior_date`: ngày trước đó để so sánh
- `sample_size`: số dòng lấy mẫu ngẫu nhiên cho mỗi ngày
**Kết quả trả về:**
- Một dictionary, trong đó:
    - key = tên cột
    - value = anomaly score của cột đó
```
# Lấy mẫu ngẫu nhiên dữ liệu cho hai ngày
data_current = query_random_sample(
    table, time_column, current_date, sample_size)

data_prior = query_random_sample(
    table, time_column, prior_date, sample_size)

# Tạo nhãn: 1 = today, 0 = prior
y = [1] * len(data_current) + [0] * len(data_prior)

# Gộp dữ liệu lại
data_all = pd.concat([data_current, data_prior], ignore_index=True)

# Xác định các feature cần tạo cho từng cột
feature_list = {
    column: determine_features(data_all, column)
    for column in data_all.columns
}

# Encode feature (mỗi feature thành dạng số)
encoded_features = [
    encode_feature(data_all, column, feature)
    for column, feature in feature_list
]

# Gộp tất cả feature thành ma trận X
X = pd.concat(encoded_features, axis=1)

# Chia train/test
X_train, X_eval, y_train, y_eval = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Huấn luyện mô hình
model = xgb.XGBClassifier()
model.fit(
    X_train,
    y_train,
    early_stopping_rounds=10,
    eval_set=[(X_eval, y_eval)],
    verbose=False,
)

# Tính SHAP values để giải thích mô hình
explainer = TreeExplainer(model)
shap_values = explainer.shap_values(X)

# Tính anomaly score theo từng cột
column_scores = compute_column_scores(shap_values, feature_list)

return column_scores
```
Pipeline này gồm các bước chính:

1. **Sampling**: lấy dữ liệu từ 2 thời điểm
2. **Labeling**: gán nhãn today vs not today
3. **Feature Engineering**: biến dữ liệu thành dạng ML
4. **Training**: học mô hình phân biệt 2 ngày
5. **Explainability (SHAP)**: hiểu vì sao mô hình phân biệt được
6. **Aggregation**: tổng hợp thành anomaly score theo cột

## Chương 5: Xâ dựng mô hình hoạt động tốt với dữ liệu thực tế
- Cần có chiến lược như: Tính mùa vụ, đặc trưng theo thời gian, tương gian giữa các cột nếu không mô hình sẽ thực hiện cảnh báo quá nhiều hoặc bỏ sót lõi
- không chỉ tránh lỗi mà còn liên tục cải tiến
	- Đánh giá mô hình liên tục
	- Sử dụng benchmarch để kiểm tra hiệu quả
- Mục tiêu hiểu mô hình sai ở đâu, cải thiện như thế nào
- Kiểm thử mô hình: Phương pháp test hiệu quả, xây một thư viện test
	- Thêm hỗn loạn vào dữ liệu vốn đang hoàn hảo -> Cố tình làm hỏng dữ liệu để xem mô hình có phát hiện được không
### Tính mùa vụ
- Seasonality thường xuất hiện ở mọi dataset
- Như đã trình bày thì so sánh dữ liệu hôm nay và hôm qua là chưa đủ, vì nếu hôm nay là thứ 2 homo qua là chủ nhật thì dữ liệu khác nhau là do hành vi, không phải lỗi
- Nếu so sánh cùng ngày tuần trước cũng chưa đủ, ví không biết lỗi đã tồn tại bao lâu, tuần trước có thể là lỗi hoặc ngày lễ
- Giải pháp
	- Lấy từ nhiều thời điểm trong quá khứ: hôm qua, 2 ngày trước, 1 tuần trước, 2 tuần trước
	- Nếu hôm nay giống bất kỳ mốc nào -> coi là bình thường
- Ngoài ra nên tạo metadata theo thời gian, dùng time series để học pattern mùa vụ và giảm ảnh hưởng của chúng
- Feature liên quan đến thời gian
	- Có những cột liên quan trực tiếp đến thời gian: như timestampe hay id tăng dần, dễ làm sai lệch kết quả
	- Giải pháp: Loại bỏ các trường liên quan mạnh đến thời gian hoặc train một model đơn giản, tìm các feature có importance quá cao -> loại bỏ chúng
- Một dataset loạn do thay đổi liên tục
	- Theo dõi anomaly score theo thời gian
	- Dùng time series model để học mức độ laonj của từng bảng
	- Tạo thresshold động
	- Kỹ thuật
		- Ban đầu đặt thress hold cao
		- Sau đó giảm dần và kết hợp với model time series
- Tương quan giữa các cột
	- Các cột tương quan có thể một lỗi ảnh hưởng nheieuf cột cùng lúc
	- Model có thể: Dùng shap value, phân tích row level hoặc cluster các cột anomaly trên cùng một tập record
### Kiểm thử mô hình
- làm sao để mô hình đã xây thực sự hoạt động tốt trên thực tế và cải tiến theo từng bước
- ý tưởng cốt lõi là
	- Các vấn đề chaatys lượng dữ liệu thực tế không khó để chèn vào một cách có lập trình, chúng tôi nhận thấy rằng việc bất thường giả lập, =cụ thể
		- Thu thập một tập các dataset các bảng đại diện
		- Chạy mô hình trên dữ liệu gốc
		- Sau đó chạy lại sau khi chèn các bất thường giả lập
		- Đo các chỉ số về thời gian chạy và độ chính xác
		- Tinh chỉnh các tham số
		- Lặp lại
	- Chèn lỗi giả lập
		- Sử dụng SQL để phá dữ liệu theo cách giống lỗi thực tế
		- Các lỗi chỉ ảnh hưởng một phần dữ liệu không phải toàn bộ
			- Một segment, một số cotoj, một phần trăm dữ liệu
		- Sau đó đo hiệu năng bằng
			- Sensitive (recal)
			- Sepcificity
			- AUC
			- Thời gian chạy
			- Khả năng phát hiện ra từng lỗi
		- Thư viện Chaos, Một số thao tác chaos phổ biến:
			- ColumnGrow: nhân giá trị cột với số ngẫu nhiên
			- ColumnModeDrop: xóa các dòng có giá trị phổ biến nhất
			- ColumnNull: biến một phần dữ liệu thành NULL
			- ColumnRandom: thay bằng giá trị ngẫu nhiên
			- TableReplicate: nhân bản thêm dòng
	- Benchmark gồm nhiều dataset mẫu (gọi là backtest), Mỗi backtest:

		- Chạy mô hình theo từng ngày liên tiếp
		- Ghi lại:
		    - anomaly score
		    - threshold động
		- Sau đó:
			- Chạy lại với dữ liệu đã bị “chaos”
			- So sánh kết quả
	- ## **Phân tích hiệu năng**
		- Các metric phổ biến:
		### **AUC**
		- Đo khả năng phân biệt giữa:
		    - dữ liệu có chaos
		    - dữ liệu bình thường
		- 0.5 = random
		- 1.0 = hoàn hảo
		### **Precision**
		- Khi model cảnh báo → đúng bao nhiêu %
		### **Recall**
		- Bao nhiêu % lỗi được phát hiện
		### **F1 Score**
		- Trung hòa giữa precision và recall

**Phân tích theo nhiều chiều**
- Bạn có thể phân tích kết quả theo:

	- Dataset
	- Số ngày chạy
	- Loại chaos
	- % dữ liệu bị ảnh hưởng

- Đặc biệt, **chaos fraction** (tỷ lệ dữ liệu bị lỗi) rất quan trọng:

	- Khi chaos 100% → model phải detect tốt
	- Khi chaos nhỏ → biết giới hạn của model
## **Pseudo code (tóm tắt)**

### Tính anomaly score:

def calculate_anomaly_scores(...):  
    column_scores = detect_anomalies(...)  
    return sum(column_scores.values())

---

### Backtest:

def backtest(...):  
    for mỗi ngày:  
        tính score bình thường  
        thêm chaos  
        tính score với chaos

---

### Benchmark nhiều bảng:

def benchmark(...):  
    for mỗi bảng:  
        chạy backtest

---

### Tính AUC tổng:

def calculate_global_auc(...):  
    gộp scores  
    tạo label (0 = bình thường, 1 = chaos)  
    tính AUC

## **Cải thiện mô hình (Improving the Model)**

Việc benchmark và phân tích các chỉ số hiệu năng cực kỳ hữu ích để hiểu và debug mô hình của bạn. Đây cũng là cách để chứng minh với người dùng rằng hệ thống đang hoạt động đúng như kỳ vọng.

Tuy nhiên, một trong những giá trị quan trọng nhất của dữ liệu này là giúp bạn **xác thực các thay đổi đối với mô hình**, đảm bảo rằng bạn đang tinh chỉnh theo hướng thực sự mang lại giá trị. Hình 5-9 minh họa một ví dụ về các thống kê tổng hợp từ benchmark, nhằm đánh giá xem một thay đổi trong mô hình có cải thiện kết quả hay không.

Thay đổi giả định trong ví dụ này là bổ sung một loại feature mới giúp mô hình nhạy hơn với các thay đổi trong **cột dạng chuỗi** (ví dụ: số điện thoại, ID, v.v.).

- **Điểm tiêu cực:**  
    Thời gian chạy (runtime) của benchmark tăng đáng kể → cần tối ưu thêm để tránh tăng độ trễ và chi phí.
- **Điểm tích cực:**
    - Precision và recall đều được cải thiện rõ rệt
    - Số lượng **false negatives giảm**
    - AUC cũng tăng

Mặc dù mức tăng AUC nhìn qua có vẻ nhỏ, nhưng nếu xét so với mức baseline 0.5 (tương đương random), thì mức cải thiện thực tế là:

0.624−0.50.617−0.5−1=5%\frac{0.624 - 0.5}{0.617 - 0.5} - 1 = 5\%0.617−0.50.624−0.5​−1=5%

→ Đây là một cải thiện đáng kể.

---

## **Kết luận**

Chúng ta đã:

- Phân tích các đặc điểm của dữ liệu thực tế (correlation, updated-in-place, v.v.)
- Xây dựng cách benchmark mô hình bằng cách **chèn chaos vào dữ liệu**
- Sử dụng kết quả để đo lường và cải tiến mô hình theo thời gian

Việc xây dựng một mô hình tốt không hề dễ:

- Không được bỏ sót lỗi quan trọng (false negative)
- Không được cảnh báo quá nhiều (false positive)

Khi bạn đã có một mô hình chất lượng cao, điều quan trọng nhất là:  
👉 **Cách bạn sử dụng output của nó để hỗ trợ con người xử lý vấn đề dữ liệu**

Ở chương tiếp theo, tác giả sẽ giải thích cách:

- Xây dựng hệ thống alert hiệu quả
- Giúp người dùng nhanh chóng hiểu và xử lý các bất thường trong dữ liệu