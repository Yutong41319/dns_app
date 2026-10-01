import socket
from flask import Flask, request

app = Flask(__name__)


def fib(n):
    if n < 0:
        return None
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


@app.route("/register", methods=["PUT"])
def register():
    data = request.get_json(force=True)
    hostname = data["hostname"]
    ip = data["ip"]
    as_ip = data["as_ip"]
    as_port = int(data["as_port"])

    message = f"TYPE=A\nNAME={hostname} VALUE={ip} TTL=10\n"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)
    sock.sendto(message.encode(), (as_ip, as_port))
    try:
        sock.recvfrom(1024)
    except socket.timeout:
        sock.close()
        return "Registration failed", 500
    sock.close()
    return "", 201


@app.route("/fibonacci", methods=["GET"])
def fibonacci():
    number = request.args.get("number")
    try:
        n = int(number)
    except (TypeError, ValueError):
        return "Bad request: number must be an integer", 400

    result = fib(n)
    if result is None:
        return "Bad request: number must be non-negative", 400
    return str(result), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090)
