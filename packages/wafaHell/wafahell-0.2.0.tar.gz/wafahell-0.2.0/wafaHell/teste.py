from middleware import WafaHell
from flask import Flask
import logging

app = Flask(__name__)
waf = WafaHell(app, monitor_mode=True, block_ip=True, rate_limit=True)

# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR) 

@app.route('/')
def home():
    return "Bem-vindo ao site seguro!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
