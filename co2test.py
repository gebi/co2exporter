#!/usr/bin/env python3
#  from https://hackaday.io/project/5301-reverse-engineering-a-low-cost-usb-co-monitor/log/17909-all-your-base-are-belong-to-us

import sys
import fcntl
import time

# decrypt data {{{
def decrypt(key,  data):
    cstate = [0x48,  0x74,  0x65,  0x6D,  0x70,  0x39,  0x39,  0x65]
    shuffle = [2, 4, 0, 7, 1, 6, 5, 3]

    phase1 = [0] * 8
    for i, o in enumerate(shuffle):
        phase1[o] = data[i]

    phase2 = [0] * 8
    for i in range(8):
        phase2[i] = phase1[i] ^ key[i]

    phase3 = [0] * 8
    for i in range(8):
        phase3[i] = ( (phase2[i] >> 3) | (phase2[ (i-1+8)%8 ] << 5) ) & 0xff

    ctmp = [0] * 8
    for i in range(8):
        ctmp[i] = ( (cstate[i] >> 4) | (cstate[i]<<4) ) & 0xff

    out = [0] * 8
    for i in range(8):
        out[i] = (0x100 + phase3[i] - ctmp[i]) & 0xff

    return out
# }}}

def hd(d):
    return " ".join("%02X" % e for e in d)

def checksum_valid(d):
    if d[4] == 0x0d and (sum(d[:3]) & 0xff) == d[3]:
        return True
    else:
        return False

if __name__ == "__main__":
    # Key retrieved from /dev/random, guaranteed to be random ;)
    key = [0xc4, 0xc6, 0xc0, 0x92, 0x40, 0x23, 0xdc, 0x96]

    fp = open(sys.argv[1], "a+b",  0)

    HIDIOCSFEATURE_9 = 0xC0094806
    set_report = "\x00" + "".join(chr(e) for e in key)
    fcntl.ioctl(fp, HIDIOCSFEATURE_9, set_report)

    # global dictionary with all values received from sensor
    values = {}

    while True:
        data = fp.read(8)
        if checksum_valid(data):
            decrypted = data
        else:
            decrypted = decrypt(key, data)
        if not checksum_valid(data):
            print(hd(data), " => ", hd(decrypted),  "Checksum error")
        else:
            op = decrypted[0]
            val = decrypted[1] << 8 | decrypted[2]

            values[op] = val

            # Output all data, mark just received value with asterisk
            print(", ".join( "%s%02X: %04X %5i" % ([" ", "*"][op==k], k, v, v) for (k, v) in sorted(values.items())), "  ", end=' ')
            ## From http://co2meters.com/Documentation/AppNotes/AN146-RAD-0401-serial-communication.pdf
            if 0x50 in values:
                print("CO2: %4i" % values[0x50], end=' ')
            if 0x42 in values:
                print("T: %2.2f" % (values[0x42]/16.0-273.15), end=' ')
            if 0x44 in values:
                print("RH: %2.2f" % (values[0x44]/100.0), end=' ')
            if 0x41 in values:
                print("RH: %2.2f" % (values[0x41]/100.0), end=' ')
            print()
