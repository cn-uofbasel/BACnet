#!/usr/bin/env python3

import os


class PCAP:

    def __init__(self):
        self.f = None
        self.offset = 0

    def _wr_typed_block(self, t, b):
        m = len(b) % 4
        if m:
            b += b'\x00\x00\x00\x00'
        self.f.write(t.to_bytes(4,'big'))
        l = (8 + len(b) + 4).to_bytes(4,'big')
        self.f.write(l+b+l)

    def open(self, fname, mode): # modes: "r,w,a"
        self.f = open(fname, mode + 'b')
        if mode == 'w':
            # write initial sect block
            self._wr_typed_block(0x0A0D0D0A,
                     0x1A2B3C4D.to_bytes(4, 'big') + \
                     0x00010001.to_bytes(4, 'big') + \
                     (0x7fffffffffffffff).to_bytes(8, 'big'))
            # write interface description block
            self._wr_typed_block(1,
                                 (99).to_bytes(2,'big') + \
                                 b'\00\00\00\00\00\00')
        elif 'a' in mode[0]:
            # seek to end
            pass

    def close(self):
        if self.f:
            self.f.close()
            self.f = None

    def read(self): # returns packets, or None
        while True: # not self.f.eof():
            t = int.from_bytes(self.f.read(4), 'big')
            # print(f"typ={t}")
            self.offset += 4
            l = int.from_bytes(self.f.read(4), 'big')
            # print(f"len={l}")
            self.offset += 4
            if l < 12:
                return None
            b = self.f.read(l-12)
            self.offset += l-12
            _ = self.f.read(4)
            self.offset += 4
            if t == 3:
                l = int.from_bytes(b[:4], 'big')
                # print(f"len2={l}")
                return b[4:4+l]
        return None

    def __iter__(self):
        return self

    def __next__(self):
        block = self.read()
        if not block:
            raise StopIteration
        return block

    def write(self, pkt):
        self._wr_typed_block(3, len(pkt).to_bytes(4,'big') + pkt)


# ----------------------------------------------------------------------

if __name__ == '__main__':
    print('ok')
