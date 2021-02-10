from multiprocessing import Process
import multiprocessing
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
import jwt
from data import data


app = Flask(__name__)
bcrypt = Bcrypt(app)
CORS(app)

app.config["MONGO_URI"] = "mongodb://localhost:27017/users"
app.config['secret'] = 'hgajashj'
mongo = PyMongo(app)
mongo_op = mongo.db.users


@app.route("/image/<string:quote>")
def get_image(quote):
    return send_file('public/{}.png'.format(quote.lower()))


@app.route("/register", methods=['POST'])
def register():
    if request.method == 'POST':
        firstname = request.json['firstname']
        lastname = request.json['lastname']
        email = request.json['email']
        password = request.json['password']
        auth = mongo_op.find_one({'email': email})
        if auth:
            return jsonify({'msg': 'email already exists'}), 401
        password = bcrypt.generate_password_hash(password)

        userdata = {'firstname': firstname, 'lastname': lastname,
                    'email': email, 'password': password}
        mongo_op.insert_one(userdata)
        return jsonify({'msg': 'registerd sucessfully'})


@app.route("/login", methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.json['email']
        password = request.json['password']
        auth = mongo_op.find_one({'email': email})
        if auth:
            if(bcrypt.check_password_hash(auth['password'], password)):
                token = jwt.encode({'email': auth['email']}, app.config.get(
                    'secret'), algorithm='HS256')
                return jsonify({'firstname': auth['firstname'], 'token': token}), 200
            return jsonify({'msg': 'email or password not matched'}), 401

        else:
            return jsonify({'msg': 'email or password not matched'}), 401


@app.route("/view-stock")
def viewStokc():
    return jsonify(data)


@app.route("/predict-stock/<string:quote>")
def predictStocks(quote):
    from predictstock import predictStock
    manager = multiprocessing.Manager()
    return_dict = manager.dict()

    task = Process(target=predictStock, args=(quote, return_dict))
    task.start()
    task.join()
    print("dgdsgs", return_dict)

    return jsonify('msg:model Trained sucessfully')


if __name__ == "__main__":
    app.run(debug=True)
