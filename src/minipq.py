"""Minimal pure-Python Parquet reader used by the data scripts, so that they run without extra libraries
(pandas.read_parquet with pyarrow gives the same tables).
Supports: thrift compact, DATA_PAGE v1/v2 pages, codec UNCOMPRESSED/SNAPPY/GZIP/ZSTD(no),
encoding PLAIN, RLE_DICTIONARY/PLAIN_DICTIONARY, RLE definition levels (optional flat columns)."""
import struct, zlib, io

# ---------- thrift compact protocol (generic) ----------
class TReader:
    def __init__(self, b, pos=0): self.b, self.p = b, pos
    def byte(self): v = self.b[self.p]; self.p += 1; return v
    def varint(self):
        r = s = 0
        while True:
            x = self.byte(); r |= (x & 0x7f) << s; s += 7
            if not x & 0x80: return r
    def zz(self): v = self.varint(); return (v >> 1) ^ -(v & 1)
    def val(self, t):
        if t in (1, 2): return t == 1          # bool true/false (in struct field header)
        if t == 3: return struct.unpack('b', bytes([self.byte()]))[0]
        if t in (4, 5, 6): return self.zz()
        if t == 7: v = struct.unpack('<d', self.b[self.p:self.p+8])[0]; self.p += 8; return v
        if t == 8: n = self.varint(); v = self.b[self.p:self.p+n]; self.p += n; return v
        if t in (9, 10):
            h = self.byte(); n = h >> 4; et = h & 0x0f
            if n == 15: n = self.varint()
            if et in (1, 2): return [self.byte() == 1 for _ in range(n)]
            return [self.val(et) for _ in range(n)]
        if t == 12: return self.struct()
        raise ValueError(f"tipo thrift {t}")
    def struct(self):
        d = {}; last = 0
        while True:
            h = self.byte()
            if h == 0: return d
            delta, t = h >> 4, h & 0x0f
            fid = last + delta if delta else self.zz()
            d[fid] = self.val(t); last = fid

# ---------- snappy ----------
def snappy_decompress(src):
    p = 0; n = s = 0
    while True:
        x = src[p]; p += 1; n |= (x & 0x7f) << s; s += 7
        if not x & 0x80: break
    out = bytearray()
    while p < len(src):
        tag = src[p]; p += 1; t = tag & 3
        if t == 0:
            ln = tag >> 2
            if ln >= 60:
                nb = ln - 59; ln = int.from_bytes(src[p:p+nb], 'little'); p += nb
            ln += 1; out += src[p:p+ln]; p += ln
        else:
            if t == 1: ln = ((tag >> 2) & 7) + 4; off = ((tag >> 5) << 8) | src[p]; p += 1
            elif t == 2: ln = (tag >> 2) + 1; off = int.from_bytes(src[p:p+2], 'little'); p += 2
            else: ln = (tag >> 2) + 1; off = int.from_bytes(src[p:p+4], 'little'); p += 4
            st = len(out) - off
            for i in range(ln): out.append(out[st + i])
    return bytes(out)

def decompress(codec, data, usize):
    if codec == 0: return data
    if codec == 1: return snappy_decompress(data)
    if codec == 2: return zlib.decompress(data, 31)
    raise NotImplementedError(f"codec {codec}")

# ---------- RLE / bit-packed hybrid ----------
def rle_hybrid(buf, bw, count):
    out = []; p = 0
    while len(out) < count and p < len(buf):
        h = 0; s = 0
        while True:
            x = buf[p]; p += 1; h |= (x & 0x7f) << s; s += 7
            if not x & 0x80: break
        if h & 1:
            ng = h >> 1; nbytes = ng * bw; chunk = int.from_bytes(buf[p:p+nbytes], 'little'); p += nbytes
            mask = (1 << bw) - 1
            for i in range(ng * 8): out.append((chunk >> (i * bw)) & mask if bw else 0)
        else:
            run = h >> 1; nb = (bw + 7) // 8; v = int.from_bytes(buf[p:p+nb], 'little'); p += nb
            out += [v] * run
    return out[:count]

PHYS = {0: 'BOOLEAN', 1: 'INT32', 2: 'INT64', 3: 'INT96', 4: 'FLOAT', 5: 'DOUBLE', 6: 'BYTE_ARRAY', 7: 'FIXED'}

def plain(buf, ptype, n, tlen=0):
    if ptype == 1: return list(struct.unpack(f'<{n}i', buf[:4*n]))
    if ptype == 2: return list(struct.unpack(f'<{n}q', buf[:8*n]))
    if ptype == 4: return list(struct.unpack(f'<{n}f', buf[:4*n]))
    if ptype == 5: return list(struct.unpack(f'<{n}d', buf[:8*n]))
    if ptype == 0:
        return [(buf[i >> 3] >> (i & 7)) & 1 == 1 for i in range(n)]
    if ptype == 6:
        out = []; p = 0
        for _ in range(n):
            ln = struct.unpack('<i', buf[p:p+4])[0]; p += 4; out.append(buf[p:p+ln]); p += ln
        return out
    if ptype == 7: return [buf[i*tlen:(i+1)*tlen] for i in range(n)]
    if ptype == 3:  # INT96: nanoseconds (int64) + Julian day (int32)
        out = []
        for i in range(n):
            ns, jd = struct.unpack('<qi', buf[12*i:12*i+12]); out.append((jd - 2440588) * 86400 + ns / 1e9)
        return out
    raise NotImplementedError(ptype)

class ParquetFile:
    def __init__(self, path):
        self.f = open(path, 'rb'); self.f.seek(-8, 2)
        ln = struct.unpack('<i', self.f.read(4))[0]; self.f.seek(-8 - ln, 2)
        self.meta = TReader(self.f.read(ln)).struct()
        self.schema = self.meta[2]; self.nrows = self.meta[3]
        # leaf columns (flat schema): name=4, type=1, repetition=3
        self.cols = [(s[4].decode(), s.get(1), s.get(3, 0)) for s in self.schema[1:] if 5 not in s or s.get(5, 0) == 0]
    def column_names(self): return [c[0] for c in self.cols]
    def read(self, names=None):
        names = names or self.column_names()
        res = {n: [] for n in names}
        for rg in self.meta[4]:
            for cc in rg[1]:
                md = cc[3]; path = '.'.join(x.decode() for x in md[3])
                if path not in res: continue
                res[path] += self._chunk(md)
        return res
    def _tlen(self, md):
        name = md[3][-1]
        for s in self.schema[1:]:
            if s[4] == name: return s.get(2, 0)
        return 0
    def _chunk(self, md):
        ptype, codec, nvals = md[1], md[4], md[5]
        start = md.get(11, md[9]) if md.get(11) else md[9]
        self.f.seek(start); total = md[7]; raw = self.f.read(total)
        col = next(c for c in self.cols if c[0] == '.'.join(x.decode() for x in md[3]))
        optional = col[2] == 1
        dictionary = None; out = []; p = 0
        while p < len(raw) and len(out) < nvals:
            tr = TReader(raw, p); ph = tr.struct(); p = tr.p
            ptype_page = ph[1]; usize = ph[2]; csize = ph[3]
            body = raw[p:p+csize]; p += csize
            if ptype_page == 2:  # dictionary page
                data = decompress(codec, body, usize); dh = ph[7]
                dictionary = plain(data, ptype, dh[1], self._tlen(md)); continue
            if ptype_page == 0:  # data page v1
                data = decompress(codec, body, usize); dh = ph[5]; n = dh[1]; enc = dh[2]; q = 0
                if optional:
                    l = struct.unpack('<i', data[:4])[0]; defs = rle_hybrid(data[4:4+l], 1, n); q = 4 + l
                else: defs = [1] * n
            elif ptype_page == 3:  # data page v2
                dh = ph[8]; n = dh[1]; enc = dh[4]; dl = dh[5]; rl = dh[6]
                levels = body[:dl + rl]; rest = body[dl + rl:]
                comp = dh.get(7, True)
                data = decompress(codec, rest, usize - dl - rl) if comp else rest
                defs = rle_hybrid(levels[rl:rl+dl], 1, n) if optional else [1] * n
                q = 0; data = data
            else: continue
            nn = sum(defs); vb = data[q:]
            if enc in (2, 8):
                bw = vb[0]; idx = rle_hybrid(vb[1:], bw, nn); vals = [dictionary[i] for i in idx]
            elif enc == 0: vals = plain(vb, ptype, nn, self._tlen(md))
            else: raise NotImplementedError(f"encoding {enc}")
            it = iter(vals)
            out += [next(it) if d else None for d in defs]
        return out

def to_pandas(path, cols=None):
    import pandas as pd
    pf = ParquetFile(path); d = pf.read(cols)
    sch = {x[4].decode(): x for x in pf.schema[1:]}
    for k in list(d):
        sc = sch[k]
        if sc.get(1) == 7 and sc.get(6) == 5:  # DECIMAL on FIXED_LEN_BYTE_ARRAY
            scale = sc.get(7, 0)
            d[k] = [int.from_bytes(x, 'big', signed=True) / 10**scale if x is not None else None for x in d[k]]
        elif sc.get(1) == 3:  # INT96 -> datetime
            d[k] = pd.to_datetime(pd.Series(d[k], dtype='float64'), unit='s')
    for k, v in d.items():
        if isinstance(v, list) and v and isinstance(next((x for x in v if x is not None), None), bytes):
            d[k] = [x.decode('utf-8', 'replace') if x is not None else None for x in v]
    return pd.DataFrame(d)

def iter_pandas(path, cols=None):
    """Like to_pandas, but reads one row group at a time (for large files): yields one DataFrame per row group."""
    import pandas as pd
    pf = ParquetFile(path); names = cols or pf.column_names()
    sch = {x[4].decode(): x for x in pf.schema[1:]}
    for rg in pf.meta[4]:
        d = {n: [] for n in names}
        for cc in rg[1]:
            md = cc[3]; p = '.'.join(x.decode() for x in md[3])
            if p in d: d[p] = pf._chunk(md)
        for k in list(d):
            sc = sch[k]
            if sc.get(1) == 7 and sc.get(6) == 5:
                scale = sc.get(7, 0)
                d[k] = [int.from_bytes(x, 'big', signed=True) / 10**scale if x is not None else None for x in d[k]]
            elif sc.get(1) == 3:
                d[k] = pd.to_datetime(pd.Series(d[k], dtype='float64'), unit='s')
            v = d[k]
            if isinstance(v, list) and v and isinstance(next((x for x in v if x is not None), None), bytes):
                d[k] = [x.decode('utf-8', 'replace') if x is not None else None for x in v]
        yield pd.DataFrame(d)
