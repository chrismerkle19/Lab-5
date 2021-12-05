from flask import Flask, request, jsonify
import hashlib
from math import sqrt
from itertools import count, islice
import requests
from redis import StrictRedis, RedisError
import base64

app = Flask(__name__)

# Use strict redis
redis = StrictRedis(host="redis", port=6379, charset="utf-8", decode_responses=True)


# Factorial

@app.route('/factorial/<int:num>')
def factorial(num):
    temp_num = 1
    if num < 0:
        return jsonify(
            input=int(num),
            output="Error: Input not positive"
        )

    elif num == 0:
        return jsonify(
            input=int(num),
            output=int(1)
        )

    else:
        for i in range(1, int(num) + 1):
            temp_num = temp_num * i
        return jsonify(
            input=int(num),
            output=int(temp_num)
        )


# Fibonacci


@app.route("/fibonacci/<int:number>")
def calc_fibonacci(number):
    fibonacci = [0]
    c1 = 0
    c2 = 1
    check = 0

    if number < 0:
        return jsonify(input=number, output="Error: Please use a number greater or equal to 0")
    elif number == 0:
        fibonacci = [0]
    else:
        while check == 0:
            fib = c1 + c2
            c2 = c1
            c1 = fib
            if fib <= number:
                fibonacci.append(fib)
            else:
                check = 1
    return jsonify(input=number, output=fibonacci)


# is_prime


@app.route('/is-prime/<int:n>')
def prime(n):
    return jsonify(
        input=n,
        output=is_prime(n)
    )


def is_prime(n):
    if n < 2:
        return False

    for number in islice(count(2), int(sqrt(n) - 1)):
        if n % number == 0:
            return False

    return True


# md5


@app.route('/md5/<string:result>')
def md5(result):
    start = result
    result = result
    result = hashlib.md5(result.encode())
    result = result.hexdigest()

    return jsonify(
        input=start,
        output=result
    )


# slack alert


#@app.route('/slack-alert/<string:message>')
#def slackalert(message):
    # sad little work-around that the slack webcrawler will hopefully ignore
#    url = "aHR0cHM6Ly9ob29rcy5zbGFjay5jb20vc2VydmljZXMvVDI1N1VCREhEL0IwMlBNTjBUTjdKLzFFcVY1b0haOW5PTEJhOWxjbHhUR3RqOA=="
#    payload = '{"text":"%s"}' % message
#    requests.post(base64.b64decode(url),
#                  data=payload.encode('utf-8'))
#    return jsonify(input=message, output=True)


# LAB 6

@app.route('/keyval', methods=['POST', 'PUT'])
def kv_upsert():
    # Set up the values for the return JSON
    _JSON = {
        'key': None,
        'value': None,
        'command': 'CREATE' if request.method=='POST' else 'UPDATE',
        'result': False,
        'error': None
    }

    # First check for a valid JSON payload
    try:
        payload = request.get_json()
        _JSON['key'] = payload['key']
        _JSON['value'] = payload['value']
        _JSON['command'] += f" {payload['key']}/{payload['value']}"
    except:
        _JSON['error'] = "Missing or malformed JSON in client request."
        return jsonify(_JSON), 400

    # Now try to connect to Redis
    try:
        test_value = redis.get(_JSON['key'])
    except RedisError:
        _JSON['error'] = "Cannot connect to redis."
        return jsonify(_JSON), 400

    # POST == create only
    if request.method == 'POST' and not test_value == None:
        _JSON['error'] = "Cannot create new record: key already exists."
        return jsonify(_JSON), 409

    # PUT == update only
    elif (request.method == 'PUT' and test_value == None):
        _JSON['error'] = "Cannot update record: key does not exist."
        return jsonify(_JSON), 404

    # OK, create or update the record with the user-supplied values
    else:
        if redis.set(_JSON['key'], _JSON['value']) == False:
            _JSON['error'] = "There was a problem creating the value in Redis."
            return jsonify(_JSON), 400
        else:
            _JSON['result'] = True
            return jsonify(_JSON), 200


@app.route('/keyval/<string:key>', methods=['GET', 'DELETE'])
def kv_retrieve(key):
    # Set up the values for the return JSON
    _JSON = {
        'key': key,
        'value': None,
        'command': "{} {}".format('RETRIEVE' if request.method=='GET' else 'DELETE', key)
        'result': False,
        'error': None
    }

    try:
        test_value = redis.get(key)
    except RedisError:
        _JSON['error'] = "Cannot connect to redis."
        return jsonify(_JSON), 400

    # Can't retrieve OR delete if the value doesn't exist
    if test_value == '':
        _JSON['error'] = "Key does not exist."
        return jsonify(_JSON), 404
    else:
        _JSON['value'] = test_value

    if request.method == 'GET':
        _JSON['result'] = True
        return jsonify(_JSON), 200

    elif request.method == 'DELETE':
        ret = redis.delete(key)
        if ret == 1:
            _JSON['result'] = True
            return jsonify(_JSON)
        else:
            _JSON['error'] = f"Unable to delete key (expected return value 1; client returned {ret})"
            return jsonify(_JSON), 400


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
