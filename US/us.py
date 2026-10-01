import socket
import requests
from flask import Flask, request

app = Flask(__name__)


@app.route("/fibonacci", methods=["GET"])
def fibonacci():
    hostname = request.args.get("hostname")
    fs_port = request.args.get("fs_port")
    number = request.args.get("number")
    as_ip = request.args.get("as_ip")
    as_port = request.args.get("as_port")

    if not all([hostname, fs_port, number, as_ip, as_port]):
        return "Bad request: missing parameters", 400

    # 1. DNS query to AS via UDP
    message = f"TYPE=A\nNAME={hostname}"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)
    sock.sendto(message.encode(), (as_ip, int(as_port)))
    try:
        data, _ = sock.recvfrom(1024)
    except socket.timeout:
        sock.close()
        return "Failed to resolve hostname", 500
    sock.close()

    # 2. Extract FS IP from AS response
    response = data.decode()
    fs_ip = None
    for token in response.split():
        if token.startswith("VALUE="):
            fs_ip = token[len("VALUE="):]
    if fs_ip is None:
        return "Failed to resolve hostname", 500

    # 3-4. Query FS via HTTP
    fs_url = f"http://{fs_ip}:{fs_port}/fibonacci?number={number}"
    r = requests.get(fs_url)

    # 5-6. Return result to client
    return r.text, r.status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
