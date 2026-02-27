import argparse
import socket
import struct
import time


def get_args():
    '''
    Gets the arguments from the command line and returns them
    Returns: the arguments from the command line
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="the destination host")
    parser.add_argument(
        "-n", help="Print hop addresses numerically rather than symbolically and numerically.", action="store_true")
    parser.add_argument(
        "-q", help="Set the number of probes per TTL to nqueries .", type=int, default=3)
    parser.add_argument(
        "-S", help="Print a summary of how many probes were not answered for each hop.", action="store_true")
    return parser.parse_args()


def probe(ttl, dest_addr):
    '''
    Sends UDP proble with a give ttl to the dst
    ttl: the ttl to set for the probe
    dest_addr: the destination address to send the probe to
    Returns: the time the probe was sent
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
    send_time = time.time()
    sock.sendto(b"", (dest_addr, 33434))
    sock.close()
    return send_time


def receive_reply(sock, send_time, timeout):
    '''
    Gets the reply from the probe
    send_time: the time the probe was sent
    timeout: the time to wait for a reply before giving up
    Returns: the address of the reply and the round trip time
    '''
    sock.settimeout(timeout)

    try:
        data, addr = sock.recvfrom(1024)
        rtt = (time.time() - send_time) * 1000
        return addr[0], rtt

    except socket.timeout:
        return None


def main():
    args = get_args()
    dst_addr = socket.gethostbyname(args.host)


if __name__ == "__main__":
    main()
