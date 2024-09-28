# 推文推荐系统 - Flask API

## Main Project

[Ax](https://github.com/desonglll/ax)

这是一个基于 Flask 和最近邻算法的推文推荐系统。系统使用从数据库中提取的推文特征训练一个最近邻模型，并根据用户特征返回最相似的推文推荐。

## 项目结构

```
├── app.py                 # Flask 应用及 API 路由
├── requirements.txt       # 项目所需的 Python 包依赖
└── README.md              # 项目说明文件
```

## 环境要求

- Python 3.x
- PostgreSQL 数据库

### Python 依赖包

项目依赖的 Python 包可以在 `requirements.txt` 中列出。你可以通过以下命令安装依赖包：

```bash
pip install -r requirements.txt
```

**主要依赖项：**

- `Flask`：用于创建 Web API。
- `psycopg2`：用于连接 PostgreSQL 数据库。
- `scikit-learn`：用于最近邻算法的模型训练和预测。
- `numpy`：用于处理数据矩阵。

## 数据库设置

项目使用 PostgreSQL 数据库来存储推文及其相关特征。请确保 PostgreSQL 服务正在运行，并根据项目需求创建以下表结构：

### `posts` 表结构

```sql
CREATE TABLE posts
(
    id              SERIAL PRIMARY KEY,
    content         TEXT    NOT NULL,
    like_count      INTEGER NOT NULL DEFAULT 0,
    dislike_count   INTEGER NOT NULL DEFAULT 0,
    engagement_rate FLOAT   NOT NULL DEFAULT 0.0
);
```

**说明：**

- `like_count`: 记录推文的点赞数。
- `dislike_count`: 记录推文的点踩数。
- `engagement_rate`: 记录推文的参与率。

## 使用方法

### 1. 配置数据库连接

打开 `app.py` 文件，找到以下部分并根据实际数据库的配置更新 `DATABASE_CONFIG`：

```python
DATABASE_CONFIG = {
    'dbname': 'your_database_name',
    'user': 'your_database_user',
    'password': 'your_database_password',
    'host': 'localhost',
    'port': 5432
}
```

### 2. 启动 Flask 服务

在项目根目录下运行以下命令启动 Flask 应用：

```bash
python app.py
```

Flask API 将在 `http://127.0.0.1:8001` 上运行。

### 3. API 路由

#### `GET /`

这是一个简单的健康检查 API，用于确认 Flask 应用是否正常运行。

- 请求示例：

```bash
curl http://127.0.0.1:8001/
```

- 响应：

```json
{
  "message": "Flask API is working!",
  "data": [
    1,
    2,
    3,
    4
  ]
}
```

#### `POST /predict`

此 API 接收用户特征，返回与用户特征最相似的推文 ID 列表。

- 请求示例：

```bash
curl -X POST http://127.0.0.1:8001/predict -H "Content-Type: application/json" -d '{
    "liked_posts_count": 10,
    "average_comment_count": 5.5,
    "engagement_rate": 0.8
}'
```

- 请求参数：

| 参数                      | 类型      | 说明            |
|-------------------------|---------|---------------|
| `liked_posts_count`     | integer | 用户点赞的推文数量     |
| `average_comment_count` | float   | 用户发布推文的平均评论数量 |
| `engagement_rate`       | float   | 用户的参与度（例如点赞率） |

- 响应示例：

```json
{
  "message": "Recommended tweets",
  "data": [
    3,
    1,
    2
  ]
}
```

## 模型说明

### 推文特征

- `like_count`: 推文的点赞数。
- `dislike_count`: 推文的点踩数。
- `engagement_rate`: 推文的参与率。

### 最近邻算法

项目使用了 `scikit-learn` 的 `NearestNeighbors` 算法来训练模型。模型使用推文的 `like_count`、`dislike_count`
和 `engagement_rate` 特征进行训练，并根据用户输入的特征（如用户的 `liked_posts_count`、`average_comment_count`
和 `engagement_rate`）返回最相似的推文。

```python
model = NearestNeighbors(n_neighbors=3, algorithm='auto').fit(tweet_data)
```

### 数据提取

`fetch_tweet_data` 函数从 PostgreSQL 数据库的 `posts` 表中获取推文的特征，并构建推文特征矩阵 `tweet_data` 和推文 ID
列表 `tweet_ids`。

## 常见问题

1. **如何添加更多特征？**
    - 如果需要添加更多推文特征（如评论数、分享数等），可以修改 `fetch_tweet_data` 函数并扩展 `posts` 表的结构。

2. **如何调整推荐结果的数量？**
    - 可以通过调整 `NearestNeighbors` 模型中的 `n_neighbors` 参数来控制返回的推荐推文数量。

3. **数据库连接失败？**
    - 请确保 PostgreSQL 正常运行，并且 `DATABASE_CONFIG` 配置正确。可以尝试手动连接数据库，确保数据库凭据正确。

## 贡献

如果你发现任何问题或有改进建议，欢迎提交 issue 或 Pull Request。

## 许可证

该项目采用 MIT 许可证，详情请参阅 LICENSE 文件。