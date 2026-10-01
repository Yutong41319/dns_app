import socket
import json
import os

UDP_IP = "0.0.0.0"
UDP_PORT = 53533
STORAGE_FILE = "dns_records.json"


def load_records():
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_records(records):
    with open(STORAGE_FILE, "w") as f:
        json.dump(records, f)


def parse_name_line(line):
    hostname = None
    ip = None
    ttl = None
    for token in line.split():
        if token.startswith("NAME="):
            hostname = token[len("NAME="):]
        elif token.startswith("VALUE="):
            ip = token[len("VALUE="):]
        elif token.startswith("TTL="):
            ttl = token[len("TTL="):]
    return hostname, ip, ttl


def main():
    records = load_records()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"AS listening on {UDP_IP}:{UDP_PORT}")

    while True:
        data, addr = sock.recvfrom(1024)
        message = data.decode().strip()
        lines = message.split("\n")
        name_line = lines[1] if len(lines) > 1 else ""
        hostname, ip, ttl = parse_name_line(name_line)

        if ip is not None:
            # Registration: message contains a VALUE field
            records[hostname] = {"ip": ip, "ttl": ttl}
            save_records(records)
            response = f"TYPE=A\nNAME={hostname} VALUE={ip} TTL={ttl}"
            print(f"Registered {hostname} -> {ip} (TTL={ttl})")
        else:
            # Query: message has no VALUE field
            if hostname in records:
                rec = records[hostname]
                response = f"TYPE=A\nNAME={hostname} VALUE={rec['ip']} TTL={rec['ttl']}"
            else:
                response = ""
                print(f"Query for unknown hostname: {hostname}")

        sock.sendto(response.encode(), addr)


if __name__ == "__main__":
    main()
