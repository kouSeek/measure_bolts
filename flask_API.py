from flask import Flask, jsonify, request
from measure_bolts import *
import io

app = Flask(__name__)
'''
'''

@app.route('/')
def hello():
    print("------- hit homepage -------")
    return "<h1>Hi, welcome to Image Calculations API.</br>by Koushik</h1>"

@app.route("/hello/<name>")
def hello_name(name):
    return f"<h2>hi {name}, nice to meet you.</h2>"

@app.route("/api/v1/", methods=["GET", "POST"])
def post_image():
    if request.method == 'POST':
        print("-------- API hit --------")
        data = request.data
        with open("test.jpg", 'wb') as f:
            f.write(data)
        img = cv2.imread("test.jpg")
        return jsonify(main(img, "ANU_46"))
        # print(f"Your data type is {type(data)} and length is {len(data)}")
        # return f"Your data type is {type(data)} and length is {len(data)}"
    else:
        return "Not post method."


if __name__ == '__main__':
   app.run(host="0.0.0.0", port="5000", debug=True)
