from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

@app.route('/')
def hello_world():
	x = 'world'
	return f"Helloooow, {x}"

if __name__ == "__main__":
    app.run()