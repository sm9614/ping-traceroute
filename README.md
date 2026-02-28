# ping and traceroute

```
Recreated the ping and traceroute commands.

Running the code:
  1. Create a venv using python -m venv /path/to/new/virtual/environment
  2. Activate the venv using .\venv\Scripts\activate.bat
  3. Install the requirements using pip install -r requirements.txt
  3. run the code with through the terminal with sudo python3 my_ping hostname or sudo python3 my_traceroute hostname

usage: my_ping.py [-h] [-c C] [-i I] [-s S] [-t T] host

positional arguments:
  host        The host to ping

options:
  -h, --help  show this help message and exit
  -c C        Stop after sending (and receiving) count
  -i I        Wait for wait seconds between sending each packet. Default is 1
  -s S        Specify the number of data bytes to be sent. Default is 56
  -t T        Specify a timeout in seconds before ping exits regardless of how many packets have been received.

usage: my_traceroute.py [-h] [-n] [-q Q] [-S] host

positional arguments:
  host        the destination host

options:
  -h, --help  show this help message and exit
  -n          Print hop addresses numerically rather than symbolically and numerically.
  -q Q        Set the number of probes per TTL to nqueries .
  -S          Print a summary of how many probes were not answered for each hop.
```