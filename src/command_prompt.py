import subprocess

def icmp(host):
    stdoutdata = subprocess.check_output(f"ping {host}",
                                         creationflags=0x08000000)
    return stdoutdata.decode('ascii', 'ignore')
