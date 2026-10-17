#!/usr/bin/env python3
"""Build a full Indonesian educational motion master from procedural graphics and generated audio.
No source photographs, stock pictures, storyboard images, or visual reference files are imported.
"""
from __future__ import annotations
import argparse, asyncio, json, math, os, random, re, shutil, subprocess, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W,H,FPS=1280,720,24
OW,OH=1920,1080
DURATIONS=[15]*12+[14]*15
TOTAL=sum(DURATIONS)
VOICE=os.environ.get("EDGE_TTS_VOICE","id-ID-GadisNeural")
REFERENCE_IMAGES_USED=0
EXTERNAL_VISUAL_ASSETS_USED=0
BG0=(7,11,23); BG1=(13,21,39); WHITE=(235,242,255); MUTED=(157,174,202)
CYAN=(84,230,221); BLUE=(88,145,255); VIOLET=(175,123,255); AMBER=(255,190,94)
CORAL=(255,111,129); GREEN=(109,226,162); PANEL=(18,29,51); HI=(26,41,70)
PAPER=(244,241,232); PAPER_INK=(28,39,52)

SCENES=[
{"id":1,"title":"Satu struk, banyak struktur","short":"Dari transaksi menuju struktur","motif":"receipt","narration":"Setiap belanja meninggalkan struk. Komputer harus mengenali simbol dan hubungan di balik angka, lalu membentuk makna berdasarkan aturan yang konsisten."},
{"id":2,"title":"Angka harus tetap benar","short":"Hasil hitung tidak boleh ditebak","motif":"math","narration":"Harga lima puluh empat ribu dikurangi diskon lima ribu empat ratus menghasilkan empat puluh delapan ribu enam ratus. Angka antara tidak boleh menyesatkan."},
{"id":3,"title":"Komputer tidak membaca seperti kita","short":"Karakter belum menjadi makna","motif":"transform","narration":"Komputer menerima rangkaian karakter. Sistem memecah teks, mengenali pola, lalu membangun struktur formal agar operasi dijalankan berdasarkan aturan yang dapat diuji."},
{"id":4,"title":"Mulai dari sebuah ekspresi","short":"Teks masukan yang eksplisit","motif":"code","narration":"Perhatikan total sama dengan lima puluh empat ribu dikurangi lima ribu empat ratus. Awalnya, komputer hanya menerima rangkaian karakter tanpa mengetahui peran simbol."},
{"id":5,"title":"Tokenisasi","short":"Karakter dikelompokkan menjadi unit","motif":"tokens","narration":"Tokenisasi mengenali variabel, operator, tanda sama dengan, dan bilangan, lalu mengelompokkannya menjadi unit leksikal bernama token. Tahap ini belum menentukan makna ekspresi."},
{"id":6,"title":"Urutan token","short":"Identitas dan posisi tetap penting","motif":"stream","narration":"Aliran token berisi IDENTIFIER, EQUALS, NUMBER, MINUS, lalu NUMBER. Identitas dan urutannya membantu parser menentukan struktur serta menemukan kesalahan sejak awal."},
{"id":7,"title":"Token bukan tata bahasa","short":"Leksikal dan sintaks adalah tahap berbeda","motif":"syntax","narration":"Tokenisasi menentukan jenis bagian teks, bukan validitas susunannya. Parser membandingkan urutan token dengan aturan tata bahasa yang eksplisit; keduanya tugas berbeda."},
{"id":8,"title":"Susunan mengubah validitas","short":"Simbol serupa, struktur berbeda","motif":"syntax","narration":"Urutan token yang sama belum tentu membentuk struktur valid. Tata bahasa menentukan susunan yang diterima, jadi parser harus memeriksa setiap relasi."},
{"id":9,"title":"Context-Free Grammar","short":"Aturan pembentuk struktur","motif":"grammar","narration":"Context-Free Grammar atau CFG menetapkan aturan pembentukan struktur. Terminal, nonterminal, dan simbol awal menentukan bagaimana ekspresi sah dibentuk secara sistematis."},
{"id":10,"title":"Aturan dapat berulang","short":"Ekspresi dibangun dari produksi","motif":"rule","narration":"Aturan CFG bisa rekursif: Expr menjadi Expr tambah Term atau Term, sementara Term menjadi Number. Rekursi membentuk ekspresi bersarang dengan batasan jelas."},
{"id":11,"title":"Parse tree","short":"Struktur masukan menjadi pohon","motif":"tree","narration":"Parser menerapkan aturan grammar pada token dan membangun parse tree. Setiap simpul mewakili kategori sintaks, sedangkan cabang menunjukkan hubungan antarbagian input."},
{"id":12,"title":"Pohon menunjukkan hubungan","short":"Cabang menyimpan pengelompokan","motif":"tree_deep","narration":"Parse tree menunjukkan bagaimana masukan dibentuk dari aturan. Cabang bertingkat merekam hubungan induk dan anak, bukan hanya daftar token, secara eksplisit."},
{"id":13,"title":"Prioritas operator","short":"Perkalian dikerjakan lebih dahulu","motif":"precedence","narration":"Pada dua tambah tiga kali empat, perkalian dikelompokkan lebih dahulu. Parse tree menyimpan prioritas operator sehingga hasilnya empat belas, bukan dua puluh."},
{"id":14,"title":"Tanda kurung mengubah kelompok","short":"Kelompok eksplisit mengubah hasil","motif":"parentheses","narration":"Tanda kurung mengubah pengelompokan. Pada buka kurung dua tambah tiga tutup kurung kali empat, jumlah dihitung dahulu dan hasilnya dua puluh."},
{"id":15,"title":"Kesalahan sintaks","short":"Parser melaporkan posisi masalah","motif":"error","narration":"Ketika tanda kurung penutup hilang, parser tidak boleh menebak diam-diam. Parser harus menandai posisi kesalahan atau menjalankan pemulihan yang jelas."},
{"id":16,"title":"Cara parser bekerja","short":"Token dipadankan dengan aturan","motif":"parser","narration":"Parser membaca token dan memilih aturan yang cocok. Recursive descent dan LR memakai strategi berbeda, tetapi keduanya bergantung pada grammar yang konsisten."},
{"id":17,"title":"Concrete Syntax Tree","short":"Detail sintaks dipertahankan","motif":"cst","narration":"Concrete Syntax Tree atau CST mempertahankan tanda kurung dan pemisah. Detail tersebut membantu alat menganalisis dan merekonstruksi bentuk sumber, misalnya dalam editor kode."},
{"id":18,"title":"Abstract Syntax Tree","short":"Struktur diringkas, hubungan dipertahankan","motif":"ast","narration":"Abstract Syntax Tree atau AST membuang tanda baca yang tidak diperlukan, sambil mempertahankan operator dan hubungan antar nilai untuk analisis lanjutan."},
{"id":19,"title":"AST untuk pengurangan","short":"Operator dan dua operand","motif":"ast_sub","narration":"Untuk harga dikurangi diskon, AST memiliki simpul pengurangan dengan dua anak: harga dan diskon. Hubungan ini menyatakan operasi utama secara langsung."},
{"id":20,"title":"Evaluasi mengikuti struktur","short":"Anak dihitung sebelum induknya","motif":"evaluate","narration":"Evaluator menghitung nilai anak, lalu menerapkan operator. Struktur AST menjaga urutan eksplisit; hasil transaksi harus tetap empat puluh delapan ribu enam ratus."},
{"id":21,"title":"Dari parser menuju compiler","short":"Parsing hanyalah satu tahap","motif":"pipeline","narration":"Parsing hanya satu tahap compiler. Setelah AST terbentuk, sistem memeriksa tipe, mengoptimalkan operasi, lalu menghasilkan bytecode atau instruksi target dengan aturan sesuai."},
{"id":22,"title":"Sintaks benar belum tentu bermakna","short":"Semantik memeriksa aturan lain","motif":"semantic","narration":"Sintaks valid belum menjamin program benar. Variabel tak terdefinisi, tipe tak cocok, atau operasi yang salah adalah masalah semantik berbeda dari kesalahan tanda baca."},
{"id":23,"title":"Seluruh pipeline","short":"Setiap tahap punya kontrak keluaran","motif":"pipeline","narration":"Karakter menjadi token, token membentuk struktur, lalu AST merangkum operasi. Tahap lanjutan menafsirkan atau menerjemahkan program melalui keluaran yang teruji."},
{"id":24,"title":"Kembali ke struk kasir","short":"Dari angka menuju hasil teruji","motif":"receipt_flow","narration":"Kembali ke struk kasir. Simbol dan angka masuk ke alur terstruktur, sehingga program menghitung hasil yang dapat diperiksa, bukan menebak."},
{"id":25,"title":"Empat konsep, empat tugas","short":"Jangan mencampur istilah","motif":"recap","narration":"Tokenisasi mengenali unit; CFG menjelaskan aturan; parse tree merekam pembentukan; AST merangkum operasi. Konsep ini berkaitan, tetapi tugasnya berbeda dan tidak boleh dicampur."},
{"id":26,"title":"Periksa setiap batas tahap","short":"Masukan jelas, keluaran dapat diuji","motif":"pipeline","narration":"Kesalahan tahap awal dapat merambat. Setiap batas pipeline memerlukan masukan jelas, keluaran terukur, serta regression test untuk menjaga konsistensi hasil."},
{"id":27,"title":"Teks menjadi pikiran komputasional","short":"Struktur menjembatani teks dan eksekusi","motif":"end","narration":"Bayangkan mesin yang membangun struktur, bukan hanya melihat huruf. Token, CFG, parse tree, dan AST menghubungkan teks dengan komputasi teruji."}
]
MOTIFS={s["motif"] for s in SCENES}
_FONTS={}; _BG=None

def font(size,kind="regular"):
    key=(size,kind)
    if key not in _FONTS:
        options={"regular":["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf","/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"],
                 "bold":["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"],
                 "mono":["/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf","/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf"]}
        path=next((p for p in options[kind] if Path(p).exists()),None)
        if not path: raise RuntimeError("Install fonts-dejavu-core.")
        _FONTS[key]=ImageFont.truetype(path,size)
    return _FONTS[key]
def tw(d,s,f):
    b=d.textbbox((0,0),s,font=f); return b[2]-b[0]
def center(d,x,y,s,f,c):
    d.text((x-tw(d,s,f)/2,y),s,font=f,fill=c)
def rounded(d,box,fill,outline=None,r=18,w=2):
    d.rounded_rectangle(box,radius=r,fill=fill,outline=outline,width=w)
def label(d,x,y,s,c=MUTED,size=14):
    d.text((x,y),s,font=font(size,"mono"),fill=c)
def chip(d,x,y,w,h,s,c=CYAN,size=17,fill=PANEL):
    rounded(d,(x,y,x+w,y+h),(*fill,245),(*c,220),13,2)
    f=font(size,"mono"); d.text((x+(w-tw(d,s,f))/2,y+(h-size)/2-2),s,font=f,fill=(*c,255))
def panel(d,box,c=BLUE):
    rounded(d,box,(*PANEL,245),(*c,150),21,2)
def arrow(d,x1,y1,x2,y2,c=CYAN,thick=3):
    d.line((x1,y1,x2,y2),fill=(*c,235),width=thick)
    a=math.atan2(y2-y1,x2-x1); n=12
    d.polygon(((x2,y2),(x2-n*math.cos(a-.55),y2-n*math.sin(a-.55)),(x2-n*math.cos(a+.55),y2-n*math.sin(a+.55))),fill=(*c,245))
def wrap(d,s,f,maxw):
    out=[]; cur=""
    for word in s.split():
        nxt=word if not cur else cur+" "+word
        if cur and tw(d,nxt,f)>maxw: out.append(cur); cur=word
        else: cur=nxt
    if cur: out.append(cur)
    return out
def background():
    global _BG
    if _BG is not None: return _BG
    im=Image.new("RGB",(W,H)); d=ImageDraw.Draw(im)
    for y in range(H):
        p=y/(H-1); c=tuple(round(BG0[i]*(1-p)+BG1[i]*p) for i in range(3))
        d.line((0,y,W,y),fill=c)
    halo=Image.new("RGBA",(W,H),(0,0,0,0)); h=ImageDraw.Draw(halo,"RGBA")
    h.ellipse((720,-260,1470,420),fill=(*BLUE,28)); h.ellipse((-360,340,420,1050),fill=(*VIOLET,23))
    h.ellipse((430,220,970,760),fill=(*CYAN,12))
    im=Image.alpha_composite(im.convert("RGBA"),halo.filter(ImageFilter.GaussianBlur(85))).convert("RGB")
    d=ImageDraw.Draw(im)
    for x in range(0,W,40): d.line((x,0,x,H),fill=(18,29,49))
    for y in range(0,H,40): d.line((0,y,W,y),fill=(18,29,49))
    rng=random.Random(23018)
    for _ in range(90):
        x=rng.randrange(12,W-12); y=rng.randrange(12,H-12); r=rng.choice((1,1,1,2))
        d.ellipse((x-r,y-r,x+r,y+r),fill=(44,67,101))
    _BG=im; return im

def draw_receipt(d,t,eq=False):
    x,y,w,h=335,207,600,295; dy=int(12*(1-min(1,t)))
    rounded(d,(x+8,y+dy+9,x+w+8,y+h+dy+9),(0,0,0,90),None,10)
    rounded(d,(x,y+dy,x+w,y+h+dy),(*PAPER,255),None,10)
    label(d,x+26,y+dy+18,"KASIR / STRUK TRANSAKSI",PAPER_INK,14)
    d.line((x+26,y+dy+48,x+w-26,y+dy+48),fill=(*PAPER_INK,150),width=2)
    d.text((x+30,y+dy+61),"Belanja",font=font(22,"bold"),fill=PAPER_INK)
    for yy,name,val in ((y+dy+108,"Subtotal","Rp 54.000"),(y+dy+145,"Diskon","− Rp 5.400")):
        d.text((x+30,yy),name,font=font(18),fill=(*PAPER_INK,220))
        d.text((x+w-220,yy),val,font=font(18,"mono"),fill=PAPER_INK)
    d.line((x+26,y+dy+180,x+w-26,y+dy+180),fill=(*PAPER_INK,150),width=2)
    d.text((x+30,y+dy+196),"TOTAL",font=font(19,"bold"),fill=PAPER_INK)
    d.text((x+w-255,y+dy+193),"Rp 48.600",font=font(25,"mono"),fill=(19,119,98))
    for xx in range(x+18,x+w-10,20): d.ellipse((xx,y+h+dy-1,xx+7,y+h+dy+6),fill=(*BG1,255))
    if eq:
        rounded(d,(x+128,y+dy+241,x+w-24,y+dy+275),(220,247,240,255),None,8)
        center(d,x+w/2+40,y+dy+247,"54.000 − 5.400 = 48.600",font(15,"mono"),(12,95,80))

def draw_tree(d,pts,edges,c=CYAN,hi=None):
    hi=hi or set()
    for a,b in edges:
        xa,ya,_=pts[a]; xb,yb,_=pts[b]
        d.line((xa,ya+18,xb,yb-18),fill=(*c,180),width=3)
    for i,(x,y,s) in enumerate(pts):
        cc=AMBER if i in hi else c; w=max(82,int(tw(d,s,font(16,"mono"))+24))
        chip(d,x-w//2,y-21,w,42,s,cc,16)

def visual(d,s,t,dur):
    m=s["motif"]; p=max(0,min(1,t/dur)); reveal=min(1,t/1.7); bounce=int(7*math.sin(min(t,3)*2)*math.exp(-min(t,3)*.8))
    if m in ("receipt","math","receipt_flow"):
        draw_receipt(d,t,m=="math")
        chip(d,464,174,350,32,"KARAKTER → DATA TERSTRUKTUR",BLUE,13)
        if m=="math":
            arrow(d,950,329,1005,329,AMBER,4); panel(d,(1008,277,1193,391),AMBER)
            center(d,1100,294,"HASIL",font(14,"mono"),MUTED); center(d,1100,331,"48.600",font(23,"mono"),GREEN)
        if m=="receipt_flow": chip(d,428,249,424,38,"INPUT → STRUKTUR → HASIL TERUJI",GREEN,14)
    elif m=="transform":
        for i,(title,desc,c) in enumerate((("TEKS","total = 54000",BLUE),("TOKEN","IDENT · NUMBER",CYAN),("STRUKTUR","Expr → Expr − Term",VIOLET))):
            x=72+i*384+int((1-min(1,t))*((-1)**i)*22); panel(d,(x,286,x+330,420),c)
            label(d,x+20,305,title,c,14); d.text((x+20,350),desc,font=font(17,"mono"),fill=WHITE)
        arrow(d,414,352,447,352,AMBER,4); arrow(d,798,352,831,352,AMBER,4)
    elif m=="code":
        panel(d,(92,248,748,455),BLUE); label(d,124,269,"INPUT / SOURCE",CYAN,14)
        d.text((127,318),"total = 54000 - 5400",font=font(25,"mono"),fill=WHITE)
        d.text((127,371),"masih berupa rangkaian teks",font=font(17),fill=MUTED)
        arrow(d,766,351,836,351,VIOLET,4); panel(d,(866,248,1185,455),GREEN)
        center(d,1025,280,"HASIL TERUJI",font(14,"mono"),GREEN); center(d,1025,326,"48.600",font(32,"mono"),WHITE)
        center(d,1025,385,"nilai final",font(15),MUTED)
    elif m in ("tokens","stream"):
        if m=="tokens": center(d,W/2,236,"total = 54000 - 5400",font(27,"mono"),WHITE)
        toks=[("IDENT",BLUE),("=",AMBER),("54000",CYAN),("−",CORAL),("5400",VIOLET)] if m=="tokens" else [("IDENTIFIER",BLUE),("EQUALS",AMBER),("NUMBER",CYAN),("MINUS",CORAL),("NUMBER",VIOLET)]
        for i,(txt,c) in enumerate(toks):
            if p*5.8>=i:
                x=117+i*213; chip(d,x,340+bounce,194,70,txt,c,17)
                if i<4 and p*5.8>=i+1: arrow(d,x+196,375+bounce,x+210,375+bounce,MUTED,2)
        if m=="tokens":
            label(d,380,442,"IDENTIFIER",BLUE,13); label(d,610,442,"OPERATOR",AMBER,13); label(d,830,442,"NUMBER LITERAL",VIOLET,13)
    elif m=="syntax":
        panel(d,(88,275,618,432),GREEN); panel(d,(660,275,1192,432),CORAL)
        center(d,352,292,"VALID",font(15,"mono"),GREEN); center(d,925,292,"INVALID",font(15,"mono"),CORAL)
        center(d,352,340,"total = 54000 - 5400",font(17,"mono"),WHITE); center(d,925,340,"total = - 5400 54000",font(17,"mono"),WHITE)
        center(d,352,391,"aturan terpenuhi",font(15),MUTED); center(d,925,391,"urutan tak cocok",font(15),MUTED)
    elif m=="grammar":
        chip(d,96,318,194,65,"NONTERMINAL",VIOLET,14); center(d,351,331,"+",font(30,"bold"),AMBER)
        chip(d,408,318,170,65,"TERMINAL",CYAN,15); arrow(d,595,350,671,350,AMBER,4); panel(d,(700,266,1179,435),BLUE)
        center(d,940,287,"SIMBOL AWAL",font(14,"mono"),MUTED); center(d,940,329,"Expr",font(32,"mono"),WHITE)
        center(d,940,385,"aturan produksi",font(15),CYAN)
    elif m=="rule":
        panel(d,(135,251,1145,444),VIOLET); center(d,W/2,276,"ATURAN PRODUKSI CFG",font(15,"mono"),MUTED)
        center(d,W/2,320,"Expr → Expr + Term  |  Term",font(25,"mono"),WHITE); center(d,W/2,375,"Term → Number",font(24,"mono"),CYAN)
    elif m in ("tree","tree_deep","cst","ast","ast_sub"):
        if m=="tree":
            pts=[(640,258,"Expr"),(430,345,"Expr"),(640,345,"−"),(850,345,"Term"),(430,431,"Term"),(430,483,"Number"),(850,431,"Number")]
            edges=[(0,1),(0,2),(0,3),(1,4),(4,5),(3,6)]
        elif m=="tree_deep":
            pts=[(640,244,"Expr"),(400,330,"Expr"),(640,330,"+"),(880,330,"Term"),(300,420,"Term"),(492,420,"Term"),(300,478,"Number"),(492,478,"Number"),(880,420,"Number")]
            edges=[(0,1),(0,2),(0,3),(1,4),(1,5),(4,6),(5,7),(3,8)]
        elif m=="cst":
            pts=[(640,242,"Expr"),(340,332,"("),(470,332,"Expr"),(640,332,"+"),(805,332,"Term"),(940,332,")"),(470,427,"Number"),(805,427,"Number")]
            edges=[(0,1),(0,2),(0,3),(0,4),(0,5),(2,6),(4,7)]
        else:
            pts=[(640,278,"SUB"),(445,390,"PRICE"),(835,390,"DISCOUNT")]; edges=[(0,1),(0,2)]
        draw_tree(d,pts,edges,VIOLET if m in ("ast","ast_sub") else CYAN,{0})
        if m=="cst": label(d,86,472,"TANDA KURUNG DAN SIMBOL DIPERTAHANKAN",AMBER,13)
        if m=="ast": label(d,86,472,"STRUKTUR DISEDERHANAKAN",GREEN,13)
    elif m in ("precedence","parentheses"):
        panel(d,(88,242,1192,500),BLUE if m=="precedence" else VIOLET)
        if m=="precedence":
            center(d,640,254,"2 + 3 × 4",font(33,"mono"),WHITE)
            draw_tree(d,[(640,342,"+"),(457,425,"2"),(790,425,"×"),(700,482,"3"),(883,482,"4")],[(0,1),(0,2),(2,3),(2,4)],AMBER,{2})
            chip(d,1000,404,132,54,"HASIL 14",GREEN,15)
        else:
            center(d,640,254,"(2 + 3) × 4",font(33,"mono"),WHITE)
            draw_tree(d,[(640,342,"×"),(457,425,"+"),(852,425,"4"),(366,482,"2"),(548,482,"3")],[(0,1),(0,2),(1,3),(1,4)],VIOLET,{1})
            chip(d,1000,404,132,54,"HASIL 20",GREEN,15)
    elif m=="error":
        panel(d,(96,266,1184,443),CORAL); label(d,126,283,"INPUT",MUTED,14); center(d,640,322,"(2 + 3 × 4",font(33,"mono"),WHITE)
        rounded(d,(775,312,950,369),(0,0,0,0),(*CORAL,255),8,3)
        chip(d,155,383,265,40,"EXPECTED: )",CORAL,14); chip(d,780,383,354,40,"PARSER ERROR @ END",CORAL,14)
    elif m=="parser":
        for i,(txt,c,desc) in enumerate((("TOKEN",BLUE,"aliran simbol"),("PARSER",VIOLET,"terapkan CFG"),("TREE",CYAN,"struktur hasil"))):
            x=(102,500,898)[i]; panel(d,(x,298,x+278,422),c); center(d,x+139,324,txt,font(22,"mono"),WHITE)
            center(d,x+139,370,desc,font(15),MUTED)
            if i<2: arrow(d,x+285,360,x+390,360,AMBER,4)
        x=int(190+760*p); d.ellipse((x-9,276,x+9,294),fill=(*AMBER,255))
    elif m=="evaluate":
        for i,(txt,c,wid,x) in enumerate((("54.000",BLUE,210,88),("−",AMBER,140,342),("5.400",VIOLET,210,532),("48.600",GREEN,250,786))):
            if p>i*.19:
                panel(d,(x,319+bounce,x+wid,410+bounce),c); center(d,x+wid/2,343+bounce,txt,font(24,"mono"),WHITE)
                if i in (0,2): arrow(d,x+wid+5,364+bounce,(342 if i==0 else 786)-10,364+bounce,MUTED if i==0 else GREEN,3)
        label(d,410,446,"ANAK DIEVALUASI → OPERATOR DIHITUNG",CYAN,13)
    elif m in ("pipeline","semantic","recap"):
        if m=="semantic":
            panel(d,(94,270,698,438),GREEN); panel(d,(728,270,1186,438),CORAL)
            center(d,396,288,"SINTAKS VALID",font(15,"mono"),GREEN); center(d,396,338,"total = harga - diskon",font(19,"mono"),WHITE)
            center(d,396,391,"bentuk sesuai aturan",font(14),MUTED)
            center(d,956,288,"SEMANTIK GAGAL",font(15,"mono"),CORAL); center(d,956,338,"harga belum didefinisikan",font(16,"mono"),WHITE)
            center(d,956,391,"makna tidak dapat dibuktikan",font(13),MUTED)
        elif m=="recap":
            for i,(a,b,c) in enumerate((("TOKENISASI","unit",BLUE),("CFG","aturan",CYAN),("PARSE TREE","pembentukan",VIOLET),("AST","operasi",AMBER))):
                x=70+i*290; panel(d,(x,287,x+260,420),c); center(d,x+130,316,a,font(15,"mono"),c); center(d,x+130,362,b,font(21,"bold"),WHITE)
        else:
            items=[("KARAKTER",BLUE),("TOKEN",CYAN),("PARSE TREE",VIOLET),("AST",AMBER),("EVALUASI",GREEN)]
            for i,(txt,c) in enumerate(items):
                x=47+i*246
                if p>i*.16:
                    panel(d,(x,320,x+220,419),c); center(d,x+110,343,txt,font(16,"mono"),WHITE)
                    center(d,x+110,382,("masukan","kelompokkan","bangun aturan","ringkas operasi","verifikasi")[i],font(12),MUTED)
                    if i<4: arrow(d,x+224,369,x+240,369,AMBER,3)
    elif m=="end":
        for i,c in enumerate((BLUE,CYAN,VIOLET,AMBER,GREEN)):
            x=170+i*235; y=315+int(13*math.sin(t*1.2+i)); d.ellipse((x-25,y-25,x+25,y+25),outline=(*c,240),width=4)
            d.ellipse((x-7,y-7,x+7,y+7),fill=(*c,255))
            if i<4: arrow(d,x+35,y,x+190,315+int(13*math.sin(t*1.2+i+1)),AMBER,3)
        center(d,W/2,390,"STRUKTUR ADALAH JEMBATAN",font(23,"mono"),WHITE)
    else: raise ValueError("Unknown motif "+m)

def frame(scene,local,duration):
    im=background().copy(); d=ImageDraw.Draw(im,"RGBA")
    phase=local*.65
    for i in range(12):
        x=int((i*109+80+22*math.sin(phase+i))%W); y=int(210+(i*27)%290+5*math.sin(phase*.8+i))
        c=(CYAN,BLUE,VIOLET)[i%3]; d.ellipse((x-2,y-2,x+2,y+2),fill=(*c,110))
    label(d,66,31,"MOTION STUDY / EDUCATIONAL FILM",CYAN,13)
    rounded(d,(1082,27,1212,64),(*HI,245),(*BLUE,150),13,1); center(d,1147,36,f"{scene['id']:02d} / 27",font(14,"mono"),WHITE)
    d.text((66,69),scene["title"],font=font(38,"bold"),fill=WHITE)
    d.text((68,124),scene["short"],font=font(18),fill=MUTED); d.line((66,166,1214,166),fill=(65,87,125,175),width=2)
    visual(d,scene,local,duration)
    rounded(d,(66,548,1214,670),(7,13,26,230),(65,87,125,145),18,1); label(d,88,560,"NARASI",CYAN,12)
    cf=font(20); lines=wrap(d,scene["narration"],cf,1085)
    if len(lines)>3: cf=font(18); lines=wrap(d,scene["narration"],cf,1085)
    if len(lines)>4: cf=font(16); lines=wrap(d,scene["narration"],cf,1085)
    for j,line in enumerate(lines[:4]): d.text((88,583+j*(cf.size+4)),line,font=cf,fill=WHITE)
    elapsed=sum(DURATIONS[:scene["id"]-1]); gp=min(1,(elapsed+local)/TOTAL)
    d.rounded_rectangle((66,694,1214,700),radius=3,fill=(34,48,73,255))
    d.rounded_rectangle((66,694,66+int(1148*gp),700),radius=3,fill=(*CYAN,255))
    d.text((66,674),f"{int(elapsed+local):03d}s / {TOTAL}s",font=font(12,"mono"),fill=MUTED)
    d.text((1047,674),"PROCEDURAL / NO REFERENCE IMAGES",font=font(11,"mono"),fill=MUTED)
    fade=min(1.0,local/.40,(duration-local)/.40)
    if fade<1: im=Image.blend(im,Image.new("RGB",im.size,(3,6,14)),max(0,1-fade))
    return im

def run(cmd):
    p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if p.returncode: raise RuntimeError(f"Command failed ({p.returncode}): {' '.join(cmd[:7])}\n{p.stderr.decode('utf-8','replace')[-5000:]}")
    return p
def duration(ffprobe,path):
    return float(run([ffprobe,"-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",str(path)]).stdout.decode().strip())
def tc(sec):
    ms=int(round(sec*1000)); return f"{ms//3600000:02d}:{ms%3600000//60000:02d}:{ms%60000//1000:02d},{ms%1000:03d}"
def write_srt(path):
    rows=[]; start=0
    for s,dur in zip(SCENES,DURATIONS):
        rows.extend([str(s["id"]),f"{tc(start)} --> {tc(start+dur)}",s["narration"],""]); start+=dur
    path.write_text("\n".join(rows),encoding="utf-8")

async def make_edge(s,path,sem):
    import edge_tts
    async with sem:
        err="no response"
        for n in range(3):
            try:
                await edge_tts.Communicate(s["narration"],VOICE,rate="+0%",volume="-4%").save(str(path))
                if path.exists() and path.stat().st_size>1000: return s["id"],True,"edge-tts:"+VOICE
                err="empty audio"
            except Exception as e: err=f"{type(e).__name__}: {e}"
            if n<2: await asyncio.sleep(1.2*(n+1))
        return s["id"],False,err
def fallback_tts(s,path):
    exe=shutil.which("espeak-ng") or shutil.which("espeak")
    if not exe: raise RuntimeError("No speech engine available.")
    for lang in ("id","en-us"):
        try:
            run([exe,"-v",lang,"-s","143","-p","48","-a","165","-w",str(path),s["narration"]])
            if path.exists() and path.stat().st_size>1000: return "espeak-fallback:"+lang
        except RuntimeError: pass
    raise RuntimeError(f"Local TTS fallback failed for scene {s['id']:02d}.")

def make_audio(ffmpeg,ffprobe,work,out):
    raw=work/"tts-raw"; seg=work/"audio-segments"; raw.mkdir(parents=True,exist_ok=True); seg.mkdir(parents=True,exist_ok=True)
    try: import edge_tts; have_edge=True
    except Exception: have_edge=False
    states={}
    if have_edge:
        async def all_tasks(): return await asyncio.gather(*(make_edge(s,raw/f"scene-{s['id']:02d}.mp3",asyncio.Semaphore(2)) for s in []))
        async def tasks():
            sem=asyncio.Semaphore(2)
            return await asyncio.gather(*(make_edge(s,raw/f"scene-{s['id']:02d}.mp3",sem) for s in SCENES))
        for i,ok,why in asyncio.run(tasks()): states[i]=(ok,why)
    providers={}; audio_segments=[]; details=[]
    for s,dur in zip(SCENES,DURATIONS):
        i=s["id"]; mp3=raw/f"scene-{i:02d}.mp3"
        if have_edge and states.get(i,(False,""))[0] and mp3.exists(): source=mp3; provider=states[i][1]
        else:
            source=raw/f"scene-{i:02d}-fallback.wav"; provider=fallback_tts(s,source)
            why=states.get(i,(False,"edge-tts unavailable"))[1]
            print(f"::warning::Scene {i:02d} uses {provider}; neural TTS unavailable: {why}",flush=True)
        source_dur=duration(ffprobe,source); target=dur-.45; speed=max(1.0,source_dur/target)
        if speed>1.25: raise RuntimeError(f"Scene {i:02d} narration needs {speed:.2f}x to fit {dur}s; shorten text before rendering.")
        wav=seg/f"scene-{i:02d}.wav"
        run([ffmpeg,"-y","-hide_banner","-loglevel","error","-i",str(source),
             "-af",f"atempo={speed:.5f},aresample=48000,apad,atrim=duration={dur},asetpts=PTS-STARTPTS",
             "-ar","48000","-ac","2","-c:a","pcm_s16le",str(wav)])
        if abs(duration(ffprobe,wav)-dur)>.06: raise RuntimeError(f"Scene {i:02d} audio duration mismatch.")
        providers[provider]=providers.get(provider,0)+1; audio_segments.append(wav)
        details.append({"scene_id":i,"duration_sec":dur,"source_audio_duration_sec":round(source_dur,3),"tempo_factor":round(speed,4),"provider":provider,"voice_qc":"PENDING_HUMAN_LISTENING"})
    listing=work/"narration-concat.txt"; listing.write_text("".join(f"file '{p.as_posix()}'\n" for p in audio_segments),encoding="utf-8")
    narration=work/"narration.wav"
    run([ffmpeg,"-y","-hide_banner","-loglevel","error","-f","concat","-safe","0","-i",str(listing),"-ar","48000","-ac","2","-c:a","pcm_s16le",str(narration)])
    if abs(duration(ffprobe,narration)-TOTAL)>.12: raise RuntimeError("Narration is not 390 seconds.")
    bed=work/"procedural-ambient.wav"; ds=str(TOTAL)
    run([ffmpeg,"-y","-hide_banner","-loglevel","error","-f","lavfi","-i",f"sine=frequency=110:sample_rate=48000:duration={ds}",
         "-f","lavfi","-i",f"sine=frequency=164.81:sample_rate=48000:duration={ds}","-f","lavfi","-i",f"sine=frequency=220:sample_rate=48000:duration={ds}",
         "-filter_complex","[0:a]tremolo=f=0.07:d=0.22,volume=0.12[a0];[1:a]tremolo=f=0.055:d=0.18,volume=0.055[a1];[2:a]tremolo=f=0.045:d=0.15,volume=0.025[a2];[a0][a1][a2]amix=inputs=3:duration=longest:normalize=0,afade=t=in:st=0:d=4,afade=t=out:st=386:d=4,aresample=48000[bed]",
         "-map","[bed]","-ar","48000","-ac","2","-c:a","pcm_s16le",str(bed)])
    mixed=work/"master-audio.wav"
    run([ffmpeg,"-y","-hide_banner","-loglevel","error","-i",str(narration),"-i",str(bed),"-filter_complex",
         "[0:a]loudnorm=I=-17:TP=-2:LRA=9[vo];[1:a]volume=0.65[bed];[bed][vo]sidechaincompress=threshold=0.025:ratio=7:attack=25:release=450[ducked];[ducked][vo]amix=inputs=2:duration=first:weights='0.55 1.0':normalize=0,alimiter=limit=0.92,aresample=48000[a]",
         "-map","[a]","-ar","48000","-ac","2","-c:a","pcm_s16le",str(mixed)])
    if abs(duration(ffprobe,mixed)-TOTAL)>.12: raise RuntimeError("Mixed audio is not 390 seconds.")
    out.mkdir(parents=True,exist_ok=True); write_srt(out/"narration-id.srt")
    (out/"narration-transcript-id.txt").write_text("\n\n".join(f"SCENE {s['id']:02d} — {s['title']}\n{s['narration']}" for s in SCENES),encoding="utf-8")
    return {"mixed":mixed,"providers":providers,"scenes":details,"mix":"Indonesian narration + generated harmonic ambient bed, sidechain ducking and loudness normalization","voice_qc":"PENDING_HUMAN_LISTENING"}

def render_video(ffmpeg,path,sheet):
    cmd=[ffmpeg,"-y","-hide_banner","-loglevel","warning","-f","rawvideo","-pixel_format","rgb24","-video_size",f"{W}x{H}","-framerate",str(FPS),"-i","-",
         "-vf",f"scale={OW}:{OH}:flags=lanczos,format=yuv420p","-an","-c:v","libx264","-preset","medium","-crf","19","-profile:v","high","-level","4.1","-threads","2","-movflags","+faststart",str(path)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    if proc.stdin is None: raise RuntimeError("FFmpeg frame pipe unavailable.")
    start=time.time(); count=0; thumbs=[]
    try:
        for s,dur in zip(SCENES,DURATIONS):
            thumbs.append(frame(s,dur*.52,dur).resize((320,180),Image.Resampling.LANCZOS))
            for k in range(dur*FPS):
                proc.stdin.write(frame(s,k/FPS,dur).tobytes()); count+=1
                if count%1200==0: print(f"Render progress: {count/FPS:.0f}/{TOTAL}s ({count}/{TOTAL*FPS} frames)",flush=True)
        proc.stdin.close(); stderr=proc.stderr.read() if proc.stderr else b""; code=proc.wait()
        if code: raise RuntimeError(f"Video render failed: {stderr.decode('utf-8','replace')[-5000:]}")
    except Exception:
        try:
            if proc.stdin and not proc.stdin.closed: proc.stdin.close()
        except Exception: pass
        proc.kill(); proc.wait(); raise
    contact=Image.new("RGB",(960,540),(5,9,18))
    for i,thumb in enumerate(thumbs): contact.paste(thumb,((i%3)*320,(i//3)*180))
    contact.save(sheet,quality=93,optimize=True)
    return {"frame_count":count,"render_seconds":round(time.time()-start,2),"source_canvas":f"{W}x{H}","output_canvas":f"{OW}x{OH}","fps":FPS,"contact_sheet":sheet.name}

def validate(ffmpeg,ffprobe,path):
    p=run([ffprobe,"-v","error","-show_streams","-show_format","-of","json",str(path)])
    data=json.loads(p.stdout.decode()); streams=data.get("streams",[])
    v=next((x for x in streams if x.get("codec_type")=="video"),None); a=next((x for x in streams if x.get("codec_type")=="audio"),None)
    if not v or not a: raise RuntimeError("Final MP4 must contain both video and audio.")
    dur=float(data.get("format",{}).get("duration",0))
    checks={"duration":abs(dur-TOTAL)<=.08,"resolution":v.get("width")==OW and v.get("height")==OH,
      "fps":v.get("r_frame_rate")==f"{FPS}/1","h264":v.get("codec_name")=="h264","aac":a.get("codec_name")=="aac",
      "audio_48k":str(a.get("sample_rate"))=="48000","stereo":int(a.get("channels",0))==2,
      "audio_duration":abs(float(a.get("duration",dur))-TOTAL)<=.15}
    failed=[k for k,vv in checks.items() if not vv]
    if failed: raise RuntimeError("Media checks failed: "+", ".join(failed)+" "+json.dumps(checks))
    stats=run([ffmpeg,"-hide_banner","-i",str(path),"-map","0:a:0","-af","volumedetect","-f","null","-"])
    err=stats.stderr.decode("utf-8","replace"); mean=re.search(r"mean_volume:\s*(-?[\d.]+)\s*dB",err); peak=re.search(r"max_volume:\s*(-?[\d.]+)\s*dB",err)
    levels={"mean_volume_db":float(mean.group(1)) if mean else None,"max_volume_db":float(peak.group(1)) if peak else None}
    if levels["max_volume_db"] is None or levels["max_volume_db"]>-0.05 or levels["max_volume_db"]<-40: raise RuntimeError("Audio level gate failed: "+json.dumps(levels))
    return {"file":path.name,"size_bytes":path.stat().st_size,"duration_sec":dur,
      "video":{"codec":v.get("codec_name"),"width":v.get("width"),"height":v.get("height"),"frame_rate":v.get("r_frame_rate"),"frame_count":v.get("nb_frames")},
      "audio":{"codec":a.get("codec_name"),"sample_rate":a.get("sample_rate"),"channels":a.get("channels"),"duration_sec":float(a.get("duration",dur)),**levels},
      "checks":checks,"technical_gate":"PASS"}

def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument("--ffmpeg",default="ffmpeg"); ap.add_argument("--ffprobe",default="ffprobe")
    ap.add_argument("--output-dir",required=True); ap.add_argument("--work-dir",default="")
    args=ap.parse_args(); out=Path(args.output_dir).resolve(); out.mkdir(parents=True,exist_ok=True)
    work=Path(args.work_dir).resolve() if args.work_dir else out/".work"; work.mkdir(parents=True,exist_ok=True)
    visual=work/"visual-only.mp4"; final=out/"Dari_Kasir_Prosedural_Motion_Master_v1.mp4"; sheet=out/"procedural-contact-sheet.jpg"
    print("Procedural-only art direction: reference images = 0; imported visual assets = 0.",flush=True)
    print("1/5 Preflight and synthesize all narration plus ambient audio.",flush=True)
    audio=make_audio(args.ffmpeg,args.ffprobe,work,out)
    print("2/5 Validate scene IDs, timing and canonical arithmetic.",flush=True)
    if [s["id"] for s in SCENES]!=list(range(1,28)) or len({s["title"] for s in SCENES})!=27: raise RuntimeError("Scene uniqueness gate failed.")
    if TOTAL!=390 or 54000-5400!=48600 or any(not s["narration"] or s["motif"] not in MOTIFS for s in SCENES): raise RuntimeError("Storyboard contract failed.")
    print("3/5 Render 9,360 procedural frames.",flush=True); render=render_video(args.ffmpeg,visual,sheet)
    print("4/5 Mux voice-over and generated score into final MP4.",flush=True)
    run([args.ffmpeg,"-y","-hide_banner","-loglevel","warning","-i",str(visual),"-i",str(audio["mixed"]),"-map","0:v:0","-map","1:a:0",
         "-c:v","copy","-c:a","aac","-b:a","192k","-ar","48000","-ac","2","-t",str(TOTAL),"-movflags","+faststart",str(final)])
    print("5/5 Validate codecs, duration, audio presence and signal levels.",flush=True)
    media=validate(args.ffmpeg,args.ffprobe,final)
    manifest={"project":"Dari Kasir ke Dalam Pikiran Komputer","version":"procedural-motion-master-v1.0.0",
      "created_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
      "concept":"Receipt → tokens → CFG → parse tree → AST → evaluation/compiler pipeline",
      "method":"Pillow-generated geometric motion graphics streamed to FFmpeg H.264; no imported images",
      "reference_images_used":0,"external_visual_assets_used":0,"scene_count":27,"scene_durations_sec":DURATIONS,
      "target_duration_sec":TOTAL,"target_frames":TOTAL*FPS,
      "audio":{"voice":VOICE,"provider_counts":audio["providers"],"mix":audio["mix"],"voice_qc":audio["voice_qc"],
        "voice_qc_note":"Technical checks passed; human listening approval remains pending.",
        "fallback_note":"Any eSpeak fallback is recorded per scene. Naturalness and pronunciation require listening QC."},
      "render":render,"validation":media,"production_acceptance":"TECHNICAL_PASS_HUMAN_VISUAL_AND_LISTENING_QC_PENDING",
      "scenes":[{"id":s["id"],"title":s["title"],"motif":s["motif"],"narration":s["narration"],"duration_sec":DURATIONS[i]} for i,s in enumerate(SCENES)]}
    (out/"production-manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    (out/"concept.md").write_text("# Procedural Motion Master v1\n\nA motion-graphics treatment transforming a receipt into tokens, CFG rules, a parse tree, an AST and a tested computation pipeline.\n\n- All visuals are procedurally drawn; no reference, stock, storyboard or imported images are used.\n- Indonesian neural TTS is attempted first; any local fallback is recorded in the manifest.\n- Procedural ambient audio is mixed with narration using sidechain ducking and loudness normalization.\n- Delivery: 390 seconds, 1920×1080 at 24 fps, H.264 video and AAC stereo at 48 kHz.\n- Technical validation does not replace human visual and listening QC.\n",encoding="utf-8")
    print(json.dumps({"status":"TECHNICAL_PASS","output":str(final),"duration_sec":media["duration_sec"],"video":media["video"],"audio":media["audio"],
      "voice_provider_counts":audio["providers"],"size_bytes":media["size_bytes"],"acceptance":manifest["production_acceptance"],"reference_images_used":0},
      ensure_ascii=False,indent=2),flush=True)
    return 0
if __name__=="__main__": raise SystemExit(main())
