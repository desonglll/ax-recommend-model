from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.neighbors import NearestNeighbors
import numpy as np
import psycopg2
import logging
from psycopg2.extras import RealDictCursor

# 创建 Flask 应用
app = Flask(__name__)
CORS(app)

# 配置日志
logging.basicConfig(level=logging.INFO)

# 数据库连接配置（根据实际情况配置）
DATABASE_CONFIG = {
    'dbname': 'hello_rocket',
    'user': '',
    'password': '',
    'host': 'localhost',
    'port': 5432
}


def get_db_connection():
    """获取数据库连接"""
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        return conn
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        return None


def fetch_tweet_data():
    """从数据库中获取推文数据"""
    conn = get_db_connection()
    if not conn:
        raise Exception("Failed to connect to the database")

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT id, like_count, dislike_count, engagement_rate
                FROM posts
            """)
            posts = cursor.fetchall()
            print(posts)

            # 将推文的特征向量提取出来
            tweet_data = np.array([
                [post['like_count'], post['dislike_count'], post['engagement_rate']]
                for post in posts
            ])
            tweet_ids = np.array([post['id'] for post in posts])

            return tweet_data, tweet_ids

    except Exception as e:
        logging.error(f"Error fetching tweet data: {e}")
        raise
    finally:
        conn.close()


def load_model():
    """加载或训练最近邻模型"""
    try:
        tweet_data, tweet_ids = fetch_tweet_data()
        model = NearestNeighbors(n_neighbors=3, algorithm='auto').fit(tweet_data)
        return model, tweet_ids
    except Exception as e:
        logging.error(f"Error loading recommendation model: {e}")
        raise


# 初始化推荐模型（生产中可能需要定期重新训练模型）
try:
    model, tweet_ids = load_model()
    logging.info("Recommendation model loaded successfully")
except Exception as e:
    logging.error(f"Failed to initialize recommendation model: {e}")
    model, tweet_ids = None, None


# 定义预测路由
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json(force=True)
        print(f"data: {data}")

        # 校验输入数据
        if 'liked_posts_count' not in data or 'average_comment_count' not in data or 'engagement_rate' not in data:
            return jsonify({'error': 'Missing user feature fields'}), 400

        # 用户特征向量
        user_features = np.array([[
            data['liked_posts_count'],
            data['average_comment_count'],
            data['engagement_rate']
        ]])
        print(f"user_features: {user_features}")

        if model is None:
            raise Exception("Recommendation model is not available")

        # 使用最近邻模型找到最相似的推文
        distances, indices = model.kneighbors(user_features)

        # 获取推荐的推文ID
        recommended_tweets = tweet_ids[indices[0]].tolist()
        print(f"recommend_tweets: {recommended_tweets}")

        return jsonify({'message': "Recommended tweets", 'data': recommended_tweets})

    except Exception as e:
        logging.error(f"Error during prediction: {e}")
        return jsonify({'error': 'An error occurred during prediction'}), 500


@app.route('/', methods=['GET'])
def index():
    data = {'message': 'Flask API is working!', 'data': [1, 2, 3, 4]}
    return jsonify(data)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8001, debug=False)
