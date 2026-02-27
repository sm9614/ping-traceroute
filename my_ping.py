import argparse
import socket
import struct
import time
import os


def get_args():
    '''
    Gets the arguments from the command line and returns them
    Returns: the arguments from the command line
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="The host to ping")
    parser.add_argument(
        "-c", help="Stop after sending (and receiving) count", type=int)
    parser.add_argument(
        "-i", help="Wait for wait seconds between sending each packet. Default is 1", type=float, default=1)
    parser.add_argument(
        "-s", help="Specify the number of data bytes to be sent. Default is 56", type=int, default=56)
    parser.add_argument(
        "-t", help="Specify a timeout in seconds before ping exits regardless of how many packets have been received.", type=int)
    return parser.parse_args()


def get_checksum(data):
    '''
    Calculates the checksum of the given data
    Data: the data to calculate the checksum of
    Returns: the checksum of the data
    '''
    checksum = 0

    # Iterate through the data in 16-bit chunks and add them to the checksum
    for i in range(0, len(data) - 1, 2):
        checksum += (data[i] << 8) + data[i+1]

    # checks if there is a left over byte
    if len(data) % 2 == 1:
        checksum += data[-1] << 8

    # Add the carry bits
    checksum = (checksum >> 16) + (checksum & 0xffff)
    checksum += (checksum >> 16)

    # returns the 1's complement of the checksum
    return ~checksum & 0xffff


def icmp_packet(id, seq, size):
    '''
    Creates an ICMP echo request packet
    id: the id of the packet
    seq: the sequence number of the packet
    size: the size of the data to be sent
    Returns: the ICMP echo request packet
    '''
    # !BBHHH is 1 byte for type, 1 byte for code,
    # 2 bytes for checksum, 2 bytes for id, and 2 bytes for sequence number
    header = struct.pack("!BBHHH", 8, 0, 0, id, seq) # type 8 is echo request
    data = struct.pack("!d", time.time()) + bytes(size) # 8 bytes for timestamp + size bytes of data

    checksum_value = get_checksum(header + data)
    header = struct.pack("!BBHHH", 8, 0, checksum_value, id, seq)
    return header + data


def receive_reply(sock, id, seq, timeout):
    '''
    Receives an ICMP echo reply packet
    sock: the socket to receive the packet on
    id: the id of the packet to receive
    seq: the sequence number of the packet to receive
    timeout: the timeout in seconds to wait for a reply
    Returns: the RTT, TTL, and source IP address of the reply packet
    '''
    start = time.time()
    sock.settimeout(timeout)
    try:
        while True:
            pkt, addr = sock.recvfrom(1024)

            # IpV4 header is 20 bytes
            ip_header = pkt[:20]

            # ICMP header is the next 8 bytes after the IP header
            icmp_header = pkt[20:28]
            # TTL is the 9th byte of the IP header
            ttl = struct.unpack("!B", ip_header[8:9])[0]
            pkt_type, code, checksum, pkt_id, pkt_seq = struct.unpack(
                "!BBHHH", icmp_header)
            if pkt_type == 0 and pkt_id == id and pkt_seq == seq:
                
                sent_time = struct.unpack("!d", pkt[28:36])[0]
                rtt = (time.time() - sent_time)
                return rtt, ttl, addr[0]
    except socket.timeout:
        return None


def main():
    args = get_args()
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

    if args.t:
        sock.settimeout(args.t)

    dst_addr = socket.gethostbyname(args.host)
    print(f"pinging {args.host} [{dst_addr}] with {args.s} bytes of data:")

    sequence_number = 1
    id = os.getpid() & 0xFFFF

    if args.c:
        count = args.c
    else:
        count = float('inf')
    rtts = []
    pkts_sent = 0
    pkts_received = 0
    try:
        while pkts_sent < count:
            pkt = icmp_packet(id, sequence_number, args.s)
            sock.sendto(pkt, (dst_addr, 1))
            pkts_sent += 1
            reply = receive_reply(sock, id, sequence_number, args.i)
            
            if reply:
                rtt, ttl, addr = reply
                pkts_received += 1
                rtts.append(rtt)
                print(f"Reply from {dst_addr}: bytes={args.s} time={int(rtt * 1000)}ms TTL={ttl}")
            else:
                print(f"Request timed out.")
            sequence_number += 1
            time.sleep(args.i)
    except KeyboardInterrupt:
        pass
    loss = (pkts_sent - pkts_received) / pkts_sent * 100
    print(f"\nPing Statistics for {dst_addr}:")
    print(f"\tPackets: Sent = {pkts_sent}, Received = {pkts_received}, Lost = {loss:.2f}% loss),")
    if rtts:
        print(f"Approximate round trip times in milli-seconds:")
        print(f"\tMinimum = {int(min(rtts) * 1000)}ms, Maximum = {int(max(rtts) * 1000)}ms, Average = {int(sum(rtts) / len(rtts) * 1000)}ms")


if __name__ == "__main__":
    main()
