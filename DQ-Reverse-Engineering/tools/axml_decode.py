#!/usr/bin/env python3
"""Best-effort decoder for Android binary XML (AXML) into readable XML."""
import struct, sys, pathlib, html

def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def pool(b, off, size):
    hs=u16(b,off+2); n=u32(b,off+8); flags=u32(b,off+16); start=u32(b,off+20)
    utf8=bool(flags&0x100); offs=[u32(b,off+hs+4*i) for i in range(n)]
    def len8(p):
        a=b[p]; p+=1
        if a&0x80: a=((a&0x7f)<<8)|b[p]; p+=1
        return a,p
    out=[]
    for ro in offs:
        p=off+start+ro
        if utf8:
            _,p=len8(p); nb,p=len8(p); value=b[p:p+nb].decode('utf-8','replace')
        else:
            nc=u16(b,p); p+=2
            if nc&0x8000: nc=((nc&0x7fff)<<16)|u16(b,p); p+=2
            value=b[p:p+2*nc].decode('utf-16le','replace')
        out.append(value)
    return out

def decode(inp,out):
    b=pathlib.Path(inp).read_bytes()
    if u16(b,0)!=3: raise ValueError('Not Android binary XML')
    strings=[]; pos=8
    while pos+8<=len(b):
        typ=u16(b,pos); hs=u16(b,pos+2); size=u32(b,pos+4)
        if size<=0 or pos+size>len(b): break
        if typ==1: strings=pool(b,pos,size)
        pos+=size
    def S(i): return strings[i] if i!=0xffffffff and i<len(strings) else None
    lines=['<?xml version="1.0" encoding="utf-8"?>']; stack=[]; pos=8
    while pos+8<=len(b):
        typ=u16(b,pos); hs=u16(b,pos+2); size=u32(b,pos+4)
        if size<=0 or pos+size>len(b): break
        if typ==0x0102 and hs>=16:
            name=u32(b,pos+20); ast=u16(b,pos+24); asz=u16(b,pos+26); count=u16(b,pos+28)
            attrs=[]; base=pos+16+ast
            for j in range(count):
                p=base+j*asz; ans=u32(b,p); aname=u32(b,p+4); raw=u32(b,p+8)
                vt=b[p+15]; vd=u32(b,p+16); key=S(aname); ns=S(ans); rv=S(raw)
                if rv is not None: value=rv
                elif vt==3: value=S(vd) or ''
                elif vt==1: value='@0x%08x'%vd
                elif vt==2: value='?0x%08x'%vd
                elif vt==18: value='true' if vd else 'false'
                elif vt in (16,17): value=str(vd) if vt==16 else '0x%08x'%vd
                elif vt==4: value=str(struct.unpack('<f',struct.pack('<I',vd))[0])
                else: value='0x%08x'%vd
                if ns=='http://schemas.android.com/apk/res/android': key='android:'+key
                attrs.append((key,value))
            tag=S(name) or 'unknown'
            if tag=='manifest':
                attrs.append(('xmlns:android','http://schemas.android.com/apk/res/android'))
                attrs.sort(key=lambda a:(a[0]!='package',a[0]))
            attrstr=''.join(' %s="%s"'%(k,html.escape(str(v),quote=True)) for k,v in attrs)
            lines.append('  '*len(stack)+'<'+tag+attrstr+'>'); stack.append(tag)
        elif typ==0x0103 and hs>=16:
            tag=S(u32(b,pos+20)) or 'unknown'
            if stack: stack.pop()
            lines.append('  '*len(stack)+'</'+tag+'>')
        elif typ==0x0104 and hs>=16:
            lines.append('  '*len(stack)+html.escape(S(u32(b,pos+16)) or ''))
        pos+=size
    pathlib.Path(out).write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('wrote',out,'lines',len(lines),'string_pool',len(strings))
if __name__=='__main__':
    if len(sys.argv)!=3: raise SystemExit('usage: axml_decode.py INPUT_XML OUTPUT.xml')
    decode(sys.argv[1],sys.argv[2])
