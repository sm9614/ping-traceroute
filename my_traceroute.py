import argparse
import socket
import time


def get_args():
    '''
    Gets the arguments from the command line and returns them

    Returns: 
        the arguments from the command line
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

    args:
        ttl: the ttl to set for the probe
        dest_addr: the destination address to send the probe to
    Returns: 
        the time the probe was sent
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
    send_time = time.time()

    # port 33433 is used for traceroute probes
    sock.sendto(b"", (dest_addr, 33434))
    return sock, send_time


def receive_reply(sock, send_time, timeout):
    '''
    Waits for reply from probe and calculates rtt

    args:
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
        return None, None

def print_hop(ttl, hop_addr, rtts, args):
    '''
    Prints the traceroute hops

    args:
        ttl: the ttl of the hop
        addr: the address of the hop
        rtt: the round trip time of the hop
        args: the arguments from the command line
    '''

    print(f"\t{ttl}, ", end="")

    for rtt in rtts:
        print(f"\t{rtt:.3f} ms, ", end="")

    for i in range(args.q - len(rtts)):
        print(f"\t*\t", end="")
    
    if hop_addr:
        if args.n:
            print(f"\t{hop_addr}")
        else:
            try:
                host = socket.gethostbyaddr(hop_addr)[0]
                print(f"\t{host}")
            except socket.herror:
                print(f"\t{hop_addr}")


def main():
    args = get_args()
    dst_addr = socket.gethostbyname(args.host)
    print(f"\ntraceroute to {args.host} [{dst_addr}] \nover a maximum of 30 hops:")

    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    recv_sock.settimeout(1)
    unanswered = 0

    # 30 is the maximum number of hops to trace
    for ttl in range(1, 31):
        rtts = []
        hop_addr = None

        for i in range(args.q):
            # uses udp to send the probe and raw socket to receive the reply
            send_sock, send_time = probe(ttl, dst_addr)
            addr, rtt = receive_reply(recv_sock, send_time, timeout=1)

            if addr:
                hop_addr = addr
                rtts.append(rtt)
            else:
                unanswered += 1
            
            send_sock.close()
            
        print_hop(ttl, hop_addr, rtts, args)
            
        if hop_addr == dst_addr:
            print("\nTrace complete.")
            break

    if args.S:
        print(f"{unanswered} unanswered probes")

if __name__ == "__main__":
    main()  
  