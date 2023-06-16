from routes import app
from flask_cors import CORS
 

CORS(app)
#CORS 서버는 Access-Control-Allow-Origin: *  으로 응답 모든 도메인에서 접근할 수 있음을 의미
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3001, threaded=True, debug=True, use_reloader=False)