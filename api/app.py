from flask import Flask, request, jsonify
import hashlib
from math import sqrt
from itertools import count, islice
import requests
from redis import StrictRedis
import os

#change

# Use strict redis
r = StrictRedis(host="127.0.0.1", port=6379, charset="utf-8", decode_responses=True)
app = Flask(__name__)


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
        for i in range(1, int(num)+1):
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


@app.route('/slack-alert/<string:message>')
def slackalert(message):
    payload = '{"text":"%s"}' % message
    requests.post('https://hooks.slack.com/services/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', data=payload.encode('utf-8'))
    return jsonify(input=message, output=True)


# LAB 6


# POST function
@app.route('/keyval', methods=['POST'])
def handle_post():
    client_data = request.get_json()
    v = client_data('value')

    # Check for valid JSON
    if client_data.get('key'):
        k = client_data.get('key')
    else:
        k = ''
        err_string = "Invalid request from client"
        return jsonify(
            key=k,
            value=v,
            command=f"CREATE {k}/{v}",
            result=False,
            error=err_string
        ), 400

    # Check if key already exists
    if r.exists(k):
        err_string = "Key already exists"
        return jsonify(
            key=k,
            value=v,
            command=f"CREATE {k}/{v}",
            result=False,
            error=err_string
        ), 409

    # Store data in redis
    redis_result = r.set(k, v)
    if not redis_result:
        err_string = "Could not write to DB"
    else:
        err_string = None

    return jsonify(
        key=k,
        value=v,
        command=f"CREATE {k}/{v}",
        result=redis_result,
        error=err_string
    ), 400


# PUT function
@app.route('/keyval', methods=['PUT'])
def handle_put():
    client_data = request.get_json()
    v = client_data('value')

    # Check for valid JSON
    if client_data.get('key'):
        k = client_data.get('key')
    else:
        k = ''
        err_string = "Invalid request from client"
        return jsonify(
            key=k,
            value=v,
            command=f"CREATE {k}/{v}",
            result=False,
            error=err_string
        ), 400

    # Check if key doesn't exist
    if r.exists(k):
        err_string = "Key already exists"
        return jsonify(
            key=k,
            value=v,
            command=f"CREATE {k}/{v}",
            result=False,
            error=err_string
        ), 409
    else:
        # store data in redis
        redis_result = r.set(k, v)
        err_string = None
        return jsonify(
            key=k,
            value=v,
            command=f"CREATE {k}/{v}",
            result=redis_result,
            error=err_string
        )


# GET FUNCTION
@app.route("/keyval/<string:key_string>", methods=["GET"])
def get_value(key_string):
    client_data = request.get_json()
    v = client_data('value')
    
    try:
        temp_string = r.get(key_string)

    except client_data.get('key'):
        k = ''
        err_string = "Invalid request from client"
        return jsonify(
            key=k,
            value=v,
            command=f"CREATE {k}/{v}",
            result=False,
            error=err_string
        ), 400

    if not r.exists(key_string):
        return jsonify(key=key_string,
                       value=temp_string,
                       command="GET " + key_string,
                       result=False,
                       error="Key does not exist."), 404

    else:
        val = r.get(key_string)
        return jsonify(key=key_string,
                       value=val,
                       command="GET " + key_string,
                       result=True,
                       error=""), 200


# DELETE function
@app.route("/keyval/<string:key_string>", methods=["DELETE"])
def delete(key_string):
    client_data = request.get_json()
    v = client_data('value')
    
    try:
        temp_string = r.get(key_string)

    except client_data.get('key'):
        k = ''
        err_string = "Invalid request from client"
        return jsonify(
            key=k,
            value=v,
            command=f"CREATE {k}/{v}",
            result=False,
            error=err_string
        ), 400

    if r.exists(key_string):
        r.delete(key_string)
        return jsonify(key=key_string,
                       value=temp_string,
                       command="DELETE " + key_string,
                       result=True,
                       error=""), 200
    else:
        return jsonify(key=key_string,
                       value=temp_string,
                       command="DELETE " + key_string,
                       result=False,
                       error="Key does not exist."), 404


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
