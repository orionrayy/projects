#!/usr/bin/env python3
"""Cashier-first V3: three question hooks, direct concept teaching, and beat-specific motion design."""
from __future__ import annotations
import argparse, json, math, random, time, zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import render_procedural_master_v2 as v2

base = v2.base
W, H = base.W, base.H
FPS = base.FPS
TOTAL_DURATION = 240
SCENES = [
 {"id":1,"motif":"hook_storefront","title":"Kok total belanja bisa dipercaya?","short":"Dari toko menuju satu pertanyaan","narration":"Dari keranjang, bagaimana kasir tahu total?"},
 {"id":2,"motif":"hook_scan","title":"Dari barang, bagaimana jadi angka?","short":"Satu bunyi bip belum berarti paham","narration":"Apa arti satu bip bagi komputer?"},
 {"id":3,"motif":"hook_total","title":"Siapa memastikan totalnya benar?","short":"Angka harus mengikuti struktur dan aturan","narration":"Siapa menjamin total ini benar?"},
 {"id":4,"motif":"counter_formula","title":"Mulai dari layar kasir","short":"Satu transaksi ditulis sebagai ekspresi","narration":"Di layar kasir, total sama dengan lima puluh empat ribu dikurangi lima ribu empat ratus. Ini ekspresi, belum hasil."},
 {"id":5,"motif":"tokenization","title":"Tokenisasi: pecah teks menjadi unit","short":"Kenali identifier, angka, dan operator","narration":"Tokenisasi memecah teks menjadi lima token: identifier total, sama dengan, angka subtotal, minus, dan angka diskon. Jenis token belum memastikan urutan valid."},
 {"id":6,"motif":"cfg_rules","title":"CFG: aturan yang membentuk ekspresi","short":"Grammar menentukan susunan yang sah","narration":"Context-Free Grammar atau CFG menjelaskan aturan susunan ekspresi. Assignment berisi identifier, tanda sama dengan, dan ekspresi; pengurangan dibentuk dari ekspresi dan term."},
 {"id":7,"motif":"syntax_check","title":"Urutan token harus valid","short":"Tokenisasi tidak sama dengan parsing","narration":"Parser mencocokkan urutan token dengan grammar. Total, sama dengan, angka, minus, angka diterima; dua angka berdempetan tanpa operator ditolak."},
 {"id":8,"motif":"parse_tree","title":"Parse tree menunjukkan pembentukan","short":"Akar, cabang, lalu nilai","narration":"Parse tree menunjukkan cara aturan membentuk input. Akar mewakili ekspresi, cabang menunjukkan hubungan, dan daun berisi token akhir."},
 {"id":9,"motif":"precedence","title":"Prioritas operator mengubah hasil","short":"Perkalian dikelompokkan lebih dahulu","narration":"Dua tambah tiga kali empat: perkalian berprioritas lebih tinggi. Tiga kali empat dulu, lalu tambah dua: hasil empat belas, bukan dua puluh."},
 {"id":10,"motif":"parentheses","title":"Tanda kurung mengubah kelompok","short":"Ekspresi yang berbeda, hasil yang berbeda","narration":"Tanda kurung mengubah kelompok: dua tambah tiga dihitung lebih dulu, lalu dikali empat. Hasilnya dua puluh; struktur tree pun berubah."},
 {"id":11,"motif":"semantic_check","title":"Sintaks valid belum tentu bermakna","short":"Semantik memeriksa definisi dan nilai","narration":"Sintaks valid belum menjamin makna. Semantik memastikan harga tersedia, item bernilai numerik, dan diskon berlaku pada subtotal yang tepat."},
 {"id":12,"motif":"subtotal","title":"Harga barang membentuk subtotal","short":"Rp18.500 + Rp21.500 + Rp14.000","narration":"Harga Rp18.500, Rp21.500, dan Rp14.000 dijumlahkan menjadi subtotal Rp54.000. Setiap item dihitung sekali, dengan harga valid."},
 {"id":13,"motif":"discount","title":"Diskon sepuluh persen","short":"10% × Rp54.000 = Rp5.400","narration":"Diskon sepuluh persen dari subtotal Rp54.000 adalah Rp5.400. Sistem menghitung diskon setelah subtotal diketahui, lalu menerapkannya sesuai aturan."},
 {"id":14,"motif":"ast","title":"AST merangkum operasi inti","short":"Operator pengurangan, dua operand","narration":"Abstract Syntax Tree atau AST merangkum operasi. Node SUB memiliki dua operand: SUBTOTAL Rp54.000 dan DISKON Rp5.400."},
 {"id":15,"motif":"evaluate","title":"Evaluasi menghasilkan total","short":"54.000 − 5.400 = 48.600","narration":"Evaluator menghitung anak sebelum induk. Subtotal Rp54.000 dikurangi diskon Rp5.400 menghasilkan total Rp48.600, yang bisa diuji ulang."},
 {"id":16,"motif":"payment","title":"Baru kemudian pembayaran","short":"Hasil yang sudah dihitung masuk ke terminal","narration":"Setelah total Rp48.600 tervalidasi, kartu ditempelkan ke terminal NFC. Ripple muncul saat kontak; terminal menunggu respons sebelum menyetujui."},
 {"id":17,"motif":"receipt","title":"Struk membuat hasil dapat diaudit","short":"Subtotal, diskon, total harus konsisten","narration":"Struk mencatat subtotal Rp54.000, diskon Rp5.400, dan total Rp48.600. Subtotal dikurangi diskon harus sama dengan total agar transaksi bisa diaudit."},
 {"id":18,"motif":"exit_recap","title":"Dari teks menuju hasil yang dapat diuji","short":"Token → CFG dan parser → tree → AST → evaluasi","narration":"Tokenisasi: unit. CFG: aturan. Parse tree: struktur. AST: operasi. Evaluator: total."}
]
DURATIONS = [4,4,4,15,16,17,15,18,15,15,16,16,16,17,17,13,14,8]
TOTAL = sum(DURATIONS)
assert TOTAL == TOTAL_DURATION

RAW_BEATS = {
 1:[("store_approach","truck_in","footsteps",.48),("warm_light_rake","light_rake","store_chime",.35),("question_punch","title_punch","whoosh",.42)],
 2:[("barcode_sweep","scan_sweep","scan_beep",.55),("data_breakout","data_burst","token_pop",.40),("token_echo","token_echo","parser_click",.32)],
 3:[("digit_count","digit_count","register_tick",.35),("arithmetic_lock","result_lock","total_chime",.44),("match_cut","match_cut_flash","whoosh",.32)],
 4:[("screen_reflection","screen_sheen","whoosh",.24),("focus_rack","focus_rack","parser_click",.24),("formula_draw","formula_draw","calculator_tick",.26)],
 5:[("characters_separate","character_split","token_pop",.34),("tokens_magnetize","token_magnet","parser_click",.34),("sequence_lock","sequence_lock","checkout_tick",.30)],
 6:[("production_one","rule_type_reveal","parser_click",.32),("production_two","syntax_glow","tree_assemble",.30),("start_symbol_lock","root_lock","token_pop",.28)],
 7:[("valid_input","valid_compare","validation_tick",.35),("invalid_order","error_blink","checkout_tick",.32),("semantic_shift","focus_shift","whoosh",.25)],
 8:[("root_appears","tree_grow","tree_assemble",.34),("branches_draw","branch_draw","tree_assemble",.30),("leaves_snap","leaf_snap","token_pop",.28)],
 9:[("multiply_ignites","operator_ignite","calculator_tick",.35),("branch_isolated","branch_isolate","whoosh",.23),("result_stamp","result_stamp","total_chime",.38)],
 10:[("bracket_wrap","bracket_wrap","whoosh",.28),("tree_rewire","tree_rewire","tree_assemble",.32),("answer_swap","answer_swap","total_chime",.34)],
 11:[("undefined_warn","semantic_warn","validation_tick",.30),("field_validate","field_validate","register_tick",.28),("status_resolve","status_resolve","approved_chime",.34)],
 12:[("rows_stagger","line_item_stagger","register_tick",.28),("sum_roll","subtotal_roll","calculator_tick",.30),("price_lock","price_lock","total_chime",.35)],
 13:[("coupon_drop","coupon_drop","discount_ping",.35),("number_wipe","discount_wipe","calculator_tick",.28),("math_confirm","math_confirm","total_chime",.35)],
 14:[("tree_collapse","ast_collapse","tree_assemble",.32),("operands_pull","operand_pull","whoosh",.24),("minimal_ast_lock","minimal_node_lock","parser_click",.30)],
 15:[("operand_travel","operand_travel","whoosh",.28),("operator_solve","operator_solve","calculator_tick",.30),("total_snap","total_snap","total_chime",.42)],
 16:[("card_slide","card_slide","whoosh",.27),("nfc_ripple","nfc_ripple","nfc_tap",.42),("green_confirm","green_confirm","approved_chime",.38)],
 17:[("paper_feed","paper_feed","receipt_printer",.35),("receipt_audit","receipt_audit","paper_rip",.32),("bag_settle","bag_settle","bag_rustle",.24)],
 18:[("dolly_out","dolly_out","footsteps",.28),("concept_link","concept_link","parser_click",.28),("final_stamp","final_stamp","farewell_chime",.36)]
}
BEAT_GUIDE = {
 str(s["id"]): [
  {"at": DURATIONS[s["id"]-1]*f, "action": a, "fx": fx, "sfx": sound, "gain": gain}
  for f,(a,fx,sound,gain) in zip((.17,.53,.84), RAW_BEATS[s["id"]])
 ] for s in SCENES
}
SFX_INFO = v2.SFX_INFO
SFX_DURATION = v2.SFX_DURATION
BACKGROUND_CACHE = {}
SPEECH_LIMITS = {}
INK=(8,13,25); INK2=(13,24,42); WHITE=(243,247,252); MUTED=(160,177,197)
CYAN=(69,222,219); BLUE=(83,147,255); VIOLET=(174,125,255); AMBER=(255,185,83)
CORAL=(255,108,122); GREEN=(92,227,164); PAPER=(247,244,234); PAPER_INK=(37,48,61)
WARM=(255,190,112)
def clamp(x,a=0.0,b=1.0): return max(a,min(b,x))
def ease(x):
 x=clamp(x); return x*x*(3-2*x)
def out_cubic(x):
 x=clamp(x); return 1-(1-x)**3
def fmt_num(n): return f"{int(round(n)):,}".replace(",",".")

def center(d,x,y,text,size,color=WHITE,kind="regular"):
 f=base.font(size,kind)
 d.text((int(x-base.tw(d,text,f)/2),int(y)),text,font=f,fill=color)
def text(d,x,y,text,size,color=WHITE,kind="regular"):
 d.text((int(x),int(y)),text,font=base.font(size,kind),fill=color)
def line(d,coords,color,width=2): d.line(tuple(int(v) for v in coords),fill=color,width=width)
def card(d,box,fill=(16,30,51,245),outline=(68,96,132,210),r=20,w=2):
 d.rounded_rectangle(tuple(int(v) for v in box),radius=r,fill=fill,outline=outline,width=w)
def glow_text(d,x,y,s,size,color=CYAN):
 f=base.font(size,"bold"); d.text((x,y),s,font=f,fill=color)
def bg(style):
 if style in BACKGROUND_CACHE: return BACKGROUND_CACHE[style]
 if style=="retail": top=(21,28,43); bottom=(8,15,28); a=(244,166,80); b=(59,173,206)
 elif style=="paper": top=(39,44,52); bottom=(12,18,29); a=(255,196,106); b=(87,167,190)
 else: top=(16,24,43); bottom=(5,10,22); a=(59,191,214); b=(145,90,224)
 im=Image.new("RGB",(W,H)); d=ImageDraw.Draw(im)
 for y in range(H):
  p=y/(H-1); col=tuple(int(top[k]*(1-p)+bottom[k]*p) for k in range(3))
  d.line((0,y,W,y),fill=col)
 haze=Image.new("RGBA",(W,H),(0,0,0,0)); h=ImageDraw.Draw(haze)
 h.ellipse((760,-200,1450,460),fill=(*a,44))
 h.ellipse((-350,230,500,980),fill=(*b,30))
 h.ellipse((280,180,980,790),fill=(*a,13))
 im=Image.alpha_composite(im.convert("RGBA"),haze.filter(ImageFilter.GaussianBlur(95))).convert("RGB")
 # restrained film grain/dust, deliberately no full-frame grid or random flashing
 dust=ImageDraw.Draw(im)
 rng=random.Random(20261018 + {"retail":1,"paper":2,"tech":3}[style])
 for _ in range(66):
  x=rng.randrange(12,W-12); y=rng.randrange(12,H-12); r=rng.choice((1,1,2))
  dust.ellipse((x-r,y-r,x+r,y+r),fill=(35,55,79))
 BACKGROUND_CACHE[style]=im
 return im

def figure(d,x,ground,scale=1.0,phase=0.0,bag=False):
 # Small illustrated shopper with articulated arm/leg motion; limb phase is continuous across frames.
 x=float(x); g=float(ground); s=scale
 bob=math.sin(phase*2.8)*2.4*s
 skin=(235,187,145); hair=(38,32,36); shirt=(65,163,171); trousers=(42,58,81)
 hx=x; hy=g-109*s+bob; hr=12*s
 d.ellipse((int(hx-hr),int(hy-hr),int(hx+hr),int(hy+hr)),fill=(*skin,255))
 d.pieslice((int(hx-hr-1),int(hy-hr-3),int(hx+hr+1),int(hy+hr+8)),180,360,fill=(*hair,255))
 d.rounded_rectangle((int(x-15*s),int(g-91*s+bob),int(x+15*s),int(g-46*s+bob)),radius=max(3,int(7*s)),fill=(*shirt,255))
 swing=math.sin(phase*3.4)*13*s
 line(d,(x-9*s,g-83*s+bob,x-25*s-swing*.45,g-55*s+bob),(*shirt,255),max(2,int(5*s)))
 line(d,(x+9*s,g-83*s+bob,x+24*s+swing*.45,g-60*s+bob),(*shirt,255),max(2,int(5*s)))
 line(d,(x-7*s,g-47*s+bob,x-10*s-swing,g-18*s),(*trousers,255),max(3,int(7*s)))
 line(d,(x+7*s,g-47*s+bob,x+10*s+swing,g-18*s),(*trousers,255),max(3,int(7*s)))
 line(d,(x-15*s-swing,g-18*s,x-2*s-swing,g-18*s),(*INK,255),max(3,int(7*s)))
 line(d,(x+15*s+swing,g-18*s,x+28*s+swing,g-18*s),(*INK,255),max(3,int(7*s)))
 if bag:
  bx=x+31*s; by=g-52*s+bob
  d.rounded_rectangle((int(bx),int(by),int(bx+31*s),int(by+33*s)),radius=4,fill=(*AMBER,245),outline=(*PAPER,245),width=2)
  d.arc((int(bx+5*s),int(by-7*s),int(bx+26*s),int(by+12*s)),180,350,fill=(*AMBER,255),width=2)

def product_box(d,x,y,w=104,h=132,phase=0.0):
 card(d,(x,y,x+w,y+h),(29,47,66,255),(121,164,188,255),12,2)
 d.rounded_rectangle((x+12,y+14,x+w-12,y+38),radius=5,fill=(*AMBER,235))
 center(d,x+w/2,y+52,"ITEM",14,WHITE,"mono")
 for k in range(3): line(d,(x+20,y+83+k*9,x+w-20,y+83+k*9),(*CYAN,180),2)
 d.line((x+10,y+8,x+w-10,y+8),fill=(*PAPER,140),width=2)

def headline(d,s,question=False):
 f=base.font(35 if question else 27,"bold")
 maxw=1100
 lines=[]; cur=""
 for word in s["title"].split():
  nxt=word if not cur else cur+" "+word
  if cur and base.tw(d,nxt,f)>maxw: lines.append(cur); cur=word
  else: cur=nxt
 if cur: lines.append(cur)
 y=58 if question else 45
 c=AMBER if question else WHITE
 for j,l in enumerate(lines[:2]): d.text((66,y+j*43),l,font=f,fill=c)
 if not question:
  d.text((68,y+47),"KASIR / STRUK / PEMROSESAN EKSPRESI",font=base.font(12,"mono"),fill=MUTED)

def cashier_screen(d,box=(115,186,1165,533),label_text="POINT OF SALE"):
 x1,y1,x2,y2=box
 card(d,box,(9,17,31,255),(73,118,160,255),20,3)
 d.rounded_rectangle((x1+15,y1+15,x2-15,y1+54),radius=9,fill=(22,39,61,255))
 text(d,x1+38,y1+27,label_text,13,CYAN,"mono")
 d.ellipse((x2-45,y1+27,x2-31,y1+41),fill=(*GREEN,255))

def draw_shop(d,t):
 # Three visual depth planes and sliding entrance doors.
 d.rectangle((0,520,W,H),fill=(14,23,33,255))
 for k in range(6):
  xx=(k*245-int(t*28))%1500-100
  line(d,(xx,522,xx+145,522), (69,81,89,170),2)
 card(d,(115,208,1165,526),(21,36,54,255),(76,122,150,255),16,3)
 card(d,(190,174,1090,253),(25,48,69,255),(89,205,206,225),13,2)
 center(d,640,193,"MINIMARKET",33,WHITE,"bold")
 for x in (205,395,860,1050):
  card(d,(x,277,x+118,471),(7,19,31,255),(69,106,133,230),5,2)
  for row,y in enumerate((314,363,412)):
   line(d,(x+7,y+18,x+110,y+18),(77,106,128,240),3)
   for j in range(4):
    cc=(CYAN,AMBER,CORAL,VIOLET)[(j+row+int(t*1.4))%4]
    d.rounded_rectangle((x+12+j*25,y-5,x+29+j*25,y+18),radius=3,fill=(*cc,235))
 gap=int(61*ease((t-.55)/1.6))
 card(d,(526-gap,268,636-gap,480),(5,16,28,255),(97,135,157,255),3,2)
 card(d,(644+gap,268,754+gap,480),(5,16,28,255),(97,135,157,255),3,2)
 d.ellipse((628-gap,377,639-gap,388),fill=(*AMBER,255))
 for i in range(3):
  d.line((510+i*13,270,510+i*13,476),fill=(65,119,147,45),width=2)
 x=130+min(1,t/3.5)*420
 figure(d,x,565,.85,t,bag=True)
 # warm shop light spill widens as the doors open
 for k in range(5):
  alpha=int(30*ease((t-.4)/2.2))
  line(d,(640-k*17,477,430-k*23,585),(*AMBER,alpha),3)

def draw_barcode(d,t):
 # Product comes into a scanner lane; a beam passes over the bars, not a permanent laser.
 d.rectangle((90,491,1190,545),fill=(19,31,46,255))
 for i in range(11):
  x=120+i*99-int(t*16)
  d.rounded_rectangle((x,484,x+72,512),radius=6,fill=(37,53,70,255),outline=(73,104,130,170),width=1)
 product_box(d,330+int(22*math.sin(t*2)),300,142,166,t)
 # package barcode panel
 d.rounded_rectangle((350,408,453,449),radius=4,fill=(*PAPER,255))
 for i in range(13):
  xx=356+i*7
  line(d,(xx,415,xx,442 if i%3 else 434),(*PAPER_INK,255),2 if i%4 else 4)
 # scanner housing and grip
 card(d,(760,345,1048,428),(24,42,61,255),(111,160,183,255),22,3)
 d.rounded_rectangle((895,407,948,500),radius=11,fill=(35,50,67,255),outline=(111,160,183,255),width=2)
 d.rounded_rectangle((789,363,864,404),radius=8,fill=(7,16,28,255),outline=(*CYAN,210),width=2)
 sy=325+int(115*((t*1.45)%1))
 # softened laser core and fast tracer
 d.line((350,sy,870,sy-36),fill=(255,86,112,75),width=12)
 d.line((350,sy,870,sy-36),fill=(255,102,121,255),width=3)
 for k in range(4):
  xx=350+int(((t*180+k*78)%520))
  line(d,(xx,sy-8,xx+36,sy-8),(255,173,179,110),2)
 center(d,977,368,"SCAN",17,CYAN,"mono")
 # small data fragments travel away from package into the display lane
 for i in range(5):
  x=492+((int(t*90)+i*82)%290); y=310+(i%3)*24
  d.rounded_rectangle((x,y,x+38,y+8),radius=4,fill=(*(CYAN if i%2 else AMBER),170))

def draw_pos_hook(d,t):
 cashier_screen(d,(155,210,1125,548),"REGISTER / TOTAL")
 # Screen reflection moves gently across glass.
 d.text((205,285),"TOTAL BELANJA",font=base.font(16,"mono"),fill=MUTED)
 d.text((205,318),"54.000  −  5.400",font=base.font(25,"mono"),fill=WHITE)
 value=int(48600*ease(t/2.45))
 d.text((205,390),"Rp",font=base.font(22,"mono"),fill=GREEN)
 d.text((260,368),fmt_num(value),font=base.font(54,"mono"),fill=GREEN)
 d.text((205,457),"HASIL HARUS BISA DITELUSURI",font=base.font(15,"mono"),fill=CYAN)
 # reflected light strip across screen
 x=int(250+800*((t/4)%1))
 d.polygon(((x,225),(x+100,225),(x+255,527),(x+155,527)),fill=(180,229,242,17))
 for r in range(3):
  rr=20+r*22+int((t*26)%20)
  d.ellipse((930-rr,390-rr,930+rr,390+rr),outline=(92,227,164,max(0,110-r*27)),width=2)

def draw_formula(d,t):
 cashier_screen(d,(95,190,1185,530),"CHECKOUT INPUT")
 card(d,(135,268,1145,452),(15,28,47,255),(61,91,125,200),14,1)
 text(d,175,291,"EXPRESSION",13,CYAN,"mono")
 code="total = 54000 - 5400"
 f=base.font(34,"mono")
 x=175; y=345
 d.text((x,y),code,font=f,fill=WHITE)
 active=int(clamp(t/4.7)*len(code))
 prefix=code[:active]
 hi_x=x+base.tw(d,prefix,f)
 token=code[active:active+1]
 if token.strip():
  tw=max(13,base.tw(d,token,f))
  d.rounded_rectangle((hi_x-2,y-3,hi_x+tw+3,y+42),radius=4,fill=(69,222,219,50),outline=(*CYAN,190),width=1)
 d.line((x,y+52,x+base.tw(d,code[:active],f),y+52),fill=(*AMBER,220),width=3)
 text(d,176,411,"BELUM DIEVALUASI • BARU TULISAN",13,MUTED,"mono")
 card(d,(840,220,1105,254),(30,53,74,220),(*AMBER,130),9,1)
 center(d,972,226,"INPUT → STRUKTUR",13,AMBER,"mono")

def draw_tokens(d,t):
 card(d,(100,198,1180,535),(8,17,31,240),(68,110,149,230),20,2)
 text(d,142,221,"TOTAL = 54000 - 5400",24,WHITE,"mono")
 labels=[("IDENTIFIER","total",BLUE),("EQUALS","=",AMBER),("NUMBER","54000",CYAN),("MINUS","−",CORAL),("NUMBER","5400",VIOLET)]
 xs=[95,322,520,733,940]
 active=min(4,int(clamp(t/6.5)*5))
 for i,(kind,val,col) in enumerate(labels):
  x=xs[i]; y=344+int(9*math.sin(t*2.6+i*.7)) if i<=active else 360
  if i<=active:
   # split fragments converge into a token chip with a short overshoot
   settle=out_cubic(clamp((t-i*.72)/.75))
   yy=int(y+(1-settle)*(-20 if i%2==0 else 20))
   card(d,(x,yy,x+178,yy+83),(*col,35),(*col,245),16,3)
   center(d,x+89,yy+14,kind,12,col,"mono")
   center(d,x+89,yy+43,val,23,WHITE,"mono")
  if i<4 and i<active:
   ax=xs[i]+180; bx=xs[i+1]-8
   line(d,(ax,390,bx,390),(*MUTED,185),2)
   d.polygon(((bx,390),(bx-8,385),(bx-8,395)),fill=(*MUTED,220))
 text(d,165,475,"TOKENISASI MENGENALI UNIT, BUKAN VALIDITAS SUSUNAN",13,MUTED,"mono")
 # Brief cyan pulse sweeps through active token as spoken labels are introduced.
 if active<5:
  x=xs[active]+89
  d.ellipse((x-42,310,x+42,394),outline=(*CYAN,95),width=2)

def draw_cfg(d,t):
 card(d,(95,192,1185,541),(8,17,31,235),(73,112,152,220),18,2)
 text(d,138,215,"CONTOH PRODUKSI CFG",14,CYAN,"mono")
 rows=[
  ("Assignment","→","IDENTIFIER  =  Expr",BLUE),
  ("Expr","→","Expr  −  Term  |  Term",VIOLET),
  ("Term","→","NUMBER",AMBER)
 ]
 for i,(lhs,arrow, rhs,col) in enumerate(rows):
  y=268+i*82
  progress=out_cubic(clamp((t-i*.8)/1.1))
  xx=int(137+(1-progress)*120)
  card(d,(xx,y,xx+1000,y+58),(*col,28 if i>int(t/1.9) else 42),(*col,210 if t>i*.8 else 80),12,2)
  text(d,xx+26,y+15,lhs,20,col,"mono")
  text(d,xx+145,y+15,arrow,21,AMBER,"mono")
  text(d,xx+194,y+15,rhs,20,WHITE,"mono")
  if t>i*.8:
   d.rounded_rectangle((xx+6,y+5,xx+13,y+53),radius=3,fill=(*col,220))
 text(d,145,516,"NONTERMINAL DI KIRI • SIMBOL / TOKEN DI KANAN",13,MUTED,"mono")

def draw_syntax(d,t):
 # Paired layouts make the distinction between token classification and parse validity immediate.
 card(d,(85,220,620,510),(11,29,39,245),(*GREEN,210),18,2)
 card(d,(660,220,1195,510),(35,23,36,245),(*CORAL,220),18,2)
 center(d,350,244,"VALID",19,GREEN,"mono")
 center(d,925,244,"URUTAN INVALID",19,CORAL,"mono")
 center(d,350,306,"total = 54000 - 5400",18,WHITE,"mono")
 center(d,925,306,"total = - 5400 54000",18,WHITE,"mono")
 # token rails
 for side,xs,valid in ((0,[139,236,333,430],True),(1,[713,810,907,1004],False)):
  colors=(BLUE,AMBER,CYAN,CORAL) if valid else (CORAL,AMBER,VIOLET,BLUE)
  for i,x in enumerate(xs):
   y=367+int(3*math.sin(t*3+i))
   card(d,(x,y,x+68,y+49),(*colors[i%len(colors)],40),(*colors[i%len(colors)],230),8,2)
   center(d,x+34,y+13,("ID","=","NUM","−")[i],13,WHITE,"mono")
   if i<3: line(d,(x+70,y+24,x+94,y+24),(*colors[i%len(colors)],210),2)
 center(d,350,448,"GRAMMAR COCOK",14,GREEN,"mono")
 center(d,925,448,"PARSER MENOLAK",14,CORAL,"mono")
 text(d,174,478,"Token dikenal",13,MUTED)
 text(d,750,478,"Urutan tak sesuai aturan",13,MUTED)

def draw_tree(d,nodes,edges,t,highlight=()):
 # Nodes appear after their parent; edges draw before child chips.
 for idx,(a,b) in enumerate(edges):
  if t < .45+idx*.48: continue
  xa,ya,_=nodes[a]; xb,yb,_=nodes[b]
  q=clamp((t-(.45+idx*.48))/.32)
  xend=xa+(xb-xa)*q; yend=ya+24+(yb-ya-48)*q
  line(d,(xa,ya+20,xend,yend),(*CYAN,215),3)
 for i,(x,y,label) in enumerate(nodes):
  if t < .22+i*.42: continue
  q=out_cubic(clamp((t-(.22+i*.42))/.38))
  yy=int(y+(1-q)*-26)
  col=AMBER if i in highlight else (VIOLET if label in ("Expr","Term","Assignment") else CYAN)
  width=max(88,base.tw(d,label,base.font(16,"mono"))+29)
  card(d,(x-width/2,yy-22,x+width/2,yy+24),(*col,35),(*col,245),12,2)
  center(d,x,yy-9,label,16,WHITE,"mono")
def draw_parse_tree(d,t):
 center(d,640,190,"54.000  −  5.400",25,WHITE,"mono")
 nodes=[(640,277,"Expr"),(415,378,"Expr"),(640,378,"−"),(865,378,"Term"),(415,482,"54000"),(865,482,"5400")]
 edges=[(0,1),(0,2),(0,3),(1,4),(3,5)]
 draw_tree(d,nodes,edges,t,highlight=(2,))
 text(d,400,534,"SETIAP CABANG MENYATAKAN RELASI SINTAKS",13,MUTED,"mono")

def draw_precedence(d,t,parentheses=False):
 expr="(2 + 3) × 4" if parentheses else "2 + 3 × 4"
 center(d,640,188,expr,37,WHITE,"mono")
 if not parentheses:
  nodes=[(640,285,"+"),(410,385,"2"),(850,385,"×"),(750,483,"3"),(950,483,"4")]
  edges=[(0,1),(0,2),(2,3),(2,4)]
  draw_tree(d,nodes,edges,t,highlight=(2,))
  if t>3.8:
   card(d,(970,282,1145,344),(*GREEN,45),(*GREEN,240),14,2)
   center(d,1057,298,"HASIL 14",18,GREEN,"mono")
   d.arc((704,435,1000,560),190,345,fill=(*AMBER,220),width=4)
 else:
  nodes=[(640,285,"×"),(430,385,"+"),(850,385,"4"),(350,483,"2"),(510,483,"3")]
  edges=[(0,1),(0,2),(1,3),(1,4)]
  draw_tree(d,nodes,edges,t,highlight=(1,))
  if t>3.6:
   card(d,(970,282,1145,344),(*GREEN,45),(*GREEN,240),14,2)
   center(d,1057,298,"HASIL 20",18,GREEN,"mono")
   # Brackets animate around the addition group, not around the entire screen.
   q=clamp((t-2.1)/1.4)
   d.arc((290,330,580,545),95,265,fill=(*AMBER,int(240*q)),width=4)
 text(d,130,539,"CABANG YANG DISOROT MENENTUKAN OPERASI LEBIH DAHULU",12,MUTED,"mono")

def draw_semantic(d,t):
 card(d,(85,218,625,516),(12,35,39,245),(*GREEN,205),16,2)
 card(d,(655,218,1195,516),(39,21,32,245),(*CORAL,215),16,2)
 center(d,355,241,"SINTAKS VALID",18,GREEN,"mono")
 center(d,925,241,"SEMANTIK GAGAL",18,CORAL,"mono")
 center(d,355,296,"total = 54000 - 5400",17,WHITE,"mono")
 center(d,925,296,"total = item - ?",17,WHITE,"mono")
 checks=[("identifier ada",GREEN),("harga terdefinisi",GREEN),("diskon numerik",GREEN)]
 for i,(s,c) in enumerate(checks):
  y=350+i*44
  if t>.55+i*.6:
   d.ellipse((155,y,179,y+24),outline=(*c,240),width=2)
   line(d,(161,y+12,167,y+18),(*c,255),3); line(d,(167,y+18,174,y+7),(*c,255),3)
   text(d,196,y+2,s,15,WHITE)
 for i,s in enumerate(("identifier ada","harga ???","diskon tidak dikenal")):
  y=350+i*44
  col=CORAL if i>0 else GREEN
  d.ellipse((722,y,746,y+24),outline=(*col,240),width=2)
  if i>0: line(d,(728,y+7,740,y+18),(*CORAL,255),3); line(d,(740,y+7,728,y+18),(*CORAL,255),3)
  else: line(d,(728,y+12,734,y+18),(*GREEN,255),3); line(d,(734,y+18,741,y+7),(*GREEN,255),3)
  text(d,762,y+2,s,15,WHITE)

def draw_subtotal(d,t):
 cashier_screen(d,(100,190,1180,535),"ITEMIZED CHECKOUT")
 items=[("Beras","18.500"),("Susu","21.500"),("Roti","14.000")]
 for i,(name,price) in enumerate(items):
  y=260+i*58
  if t>.5+i*.8:
   card(d,(145,y,835,y+43),(17,34,51,240),(*(CYAN if i==0 else BLUE),125),9,1)
   d.ellipse((162,y+13,177,y+28),fill=(*((CYAN,AMBER,VIOLET)[i]),255))
   text(d,194,y+11,name,18,WHITE)
   text(d,650,y+11,"Rp "+price,18,MUTED,"mono")
 d.line((160,447,830,447),fill=(*MUTED,140),width=2)
 text(d,160,468,"SUBTOTAL",17,CYAN,"mono")
 value=int(54000*ease(t/4.2))
 text(d,840,450,"Rp "+fmt_num(value),29,WHITE,"mono")
 card(d,(900,263,1127,409),(12,25,41,245),(*GREEN,180),14,2)
 center(d,1013,286,"3 ITEMS",15,GREEN,"mono")
 center(d,1013,329,"54.000",25,WHITE,"mono")
 center(d,1013,374,"CHECKED",13,MUTED,"mono")

def draw_discount(d,t):
 card(d,(104,225,1175,526),(9,18,33,245),(75,115,150,215),20,2)
 card(d,(154,285,365,437),(*AMBER,28),(*AMBER,240),17,3)
 center(d,260,310,"KUPON",15,AMBER,"mono")
 center(d,260,353,"−10%",35,AMBER,"bold")
 center(d,260,407,"DISKON",13,MUTED,"mono")
 center(d,535,315,"54.000",26,WHITE,"mono")
 center(d,535,369,"× 10%",19,AMBER,"mono")
 line(d,(416,400,658,400),(*AMBER,220),3)
 # Result number rolls in and then stops on the mathematically correct value.
 value=int(5400*ease((t-1.3)/2.8))
 card(d,(755,278,1105,441),(*GREEN,28),(*GREEN,225),16,2)
 center(d,930,303,"POTONGAN",15,GREEN,"mono")
 center(d,930,346,fmt_num(value),32,WHITE,"mono")
 center(d,930,401,"Rp",14,MUTED,"mono")
 if t>4.5:
  center(d,640,474,"54.000 × 0,10 = 5.400",18,CYAN,"mono")

def draw_ast(d,t):
 center(d,640,193,"AST • ABSTRACT SYNTAX TREE",15,CYAN,"mono")
 nodes=[(640,290,"SUB"),(420,405,"SUBTOTAL"),(860,405,"DISKON")]
 edges=[(0,1),(0,2)]
 draw_tree(d,nodes,edges,t,highlight=(0,))
 card(d,(90,475,1190,542),(13,25,42,230),(74,102,139,180),12,1)
 center(d,640,492,"POHON SINTAKS: DETAIL SUSUNAN   →   AST: OPERASI INTI",15,WHITE,"mono")

def draw_evaluate(d,t):
 card(d,(85,246,1195,494),(9,18,32,245),(73,109,143,210),17,2)
 parts=[("54.000",BLUE),("−",AMBER),("5.400",VIOLET),("=",MUTED),("48.600",GREEN)]
 xs=[174,390,525,706,918]
 for i,(value,col) in enumerate(parts):
  if t>.32+i*.72:
   q=out_cubic(clamp((t-(.32+i*.72))/.6))
   y=int(321+(1-q)*(-24)+3*math.sin(t*2+i))
   card(d,(xs[i],y,xs[i]+(150 if i not in (1,3) else 80),y+76),(*col,35),(*col,230),13,2)
   center(d,xs[i]+(75 if i not in (1,3) else 40),y+22,value,22,WHITE,"mono")
 text(d,180,434,"OPERAND",12,BLUE,"mono"); text(d,515,434,"OPERAND",12,VIOLET,"mono")
 text(d,916,434,"NILAI HASIL",12,GREEN,"mono")
 # particles follow the arithmetic left-to-right at a restrained speed
 px=int(150+min(1,t/6.5)*920)
 for k in range(3):
  rr=4+(k%2)*2
  d.ellipse((px-k*18-rr,289-rr,px-k*18+rr,289+rr),fill=(*(CYAN if k%2 else AMBER),170))

def draw_payment(d,t):
 cashier_screen(d,(360,205,1120,500),"PAYMENT TERMINAL")
 d.rounded_rectangle((420,282,667,433),radius=17,fill=(20,35,52,255),outline=(*CYAN,170),width=2)
 for row in range(3):
  for col in range(3):
   xx=455+col*58; yy=318+row*34
   d.ellipse((xx,yy,xx+20,yy+20),fill=(68,94,115,220))
 card(d,(770,295,1015,420),(36,55,74,255),(144,180,198,255),18,2)
 d.rounded_rectangle((790,315,995,400),radius=11,fill=(5,16,28,255))
 center(d,892,336,"TAP",16,CYAN,"mono")
 # card follows a smooth curve, arrives on the tap area, then settles
 q=ease(t/3.0); cx=250+q*570; cy=385-42*math.sin(q*math.pi)
 d.rounded_rectangle((int(cx),int(cy),int(cx+132),int(cy+76)),radius=10,fill=(27,51,79,255),outline=(*AMBER,245),width=3)
 d.rounded_rectangle((int(cx+14),int(cy+14),int(cx+44),int(cy+34)),radius=4,fill=(*AMBER,245))
 if t>2.4:
  for i in range(3):
   r=22+i*24+int((t-2.4)*33)%18
   d.arc((895-r,350-r,895+r,350+r),190,350,fill=(*CYAN,max(0,210-i*45)),width=3)
 if t>4.2:
  card(d,(801,445,1068,482),(*GREEN,45),(*GREEN,230),8,2)
  center(d,934,454,"DISETUJUI",15,GREEN,"mono")

def draw_receipt(d,t):
 # A physical paper object feeds downward; details appear only as they become available.
 x=420; y=213; w=440
 feed=int(min(1,t/2.9)*118)
 card(d,(x+8,y+9,x+w+8,y+292+feed),(0,0,0,70),None,4,1)
 d.rounded_rectangle((x,y,x+w,y+284+feed),radius=4,fill=(*PAPER,255))
 text(d,x+27,y+18,"MINIMARKET • STRUK",13,PAPER_INK,"mono")
 line(d,(x+22,y+49,x+w-22,y+49),(*PAPER_INK,160),1)
 rows=[("Subtotal","54.000"),("Diskon","−5.400"),("Total","48.600")]
 for i,(name,val) in enumerate(rows):
  yy=y+65+i*43
  if t>.45+i*.55:
   text(d,x+27,yy,name,17,PAPER_INK,"regular")
   text(d,x+w-175,yy,val,17,(15,113,85) if i==2 else PAPER_INK,"mono")
 line(d,(x+22,y+190,x+w-22,y+190),(*PAPER_INK,130),1)
 if t>2.4:
  for i in range(34):
   xx=x+28+i*11
   height=27 if i%4 else 18
   line(d,(xx,y+210,xx,y+210+height),(*PAPER_INK,245),2 if i%3 else 4)
 if t>4.4:
  card(d,(x+25,y+250+feed,x+w-25,y+275+feed),(221,244,237,255),None,4,1)
  center(d,x+w/2,y+253+feed,"TOTAL TERVERIFIKASI",11,(15,113,85),"mono")
 # subtle edge shadow gives paper its own plane
 d.line((x+w+3,y+9,x+w+3,y+282+feed),fill=(0,0,0,65),width=5)

def draw_exit(d,t):
 d.rectangle((0,505,W,H),fill=(13,24,35,255))
 for k in range(6):
  xx=(k*280-int(t*35))%1600-100
  line(d,(xx,506,xx+178,506),(65,79,91,175),2)
 # Store recedes behind the character as the camera eases out.
 scale=1.0-.14*ease(t/4.5)
 bx=790; by=210
 card(d,(bx-145*scale,by,bx+145*scale,by+286*scale),(19,34,52,255),(87,142,167,220),8,2)
 center(d,bx,by+22*scale,"MINIMARKET",int(19*scale),WHITE,"bold")
 gap=int(35*scale)
 card(d,(bx-40*scale-gap,by+61*scale,bx+0*scale-gap,by+245*scale),(6,17,29,255),(77,117,140,220),2,1)
 card(d,(bx+7*scale+gap,by+61*scale,bx+47*scale+gap,by+245*scale),(6,17,29,255),(77,117,140,220),2,1)
 x=300+int(115*ease(t/4.8))
 figure(d,x,590,.93,t,bag=True)
 # Concept path builds left to right in small, separated stages.
 labels=[("TOKEN",BLUE),("CFG",VIOLET),("PARSE TREE",CYAN),("AST",AMBER),("EVALUASI",GREEN)]
 for i,(lab,col) in enumerate(labels):
  x0=65+i*237
  if t>i*.56:
   card(d,(x0,342,x0+196,396),(*col,30),(*col,215),11,2)
   center(d,x0+98,358,lab,13,WHITE,"mono")
   if i<4 and t>(i+1)*.56:
    line(d,(x0+199,369,x0+224,369),(*MUTED,210),2)
    d.polygon(((x0+224,369),(x0+217,364),(x0+217,374)),fill=(*MUTED,230))

def draw_effects(d,s,t):
 sid=s["id"]; motif=s["motif"]
 target={
  1:(640,360),2:(565,365),3:(930,390),4:(650,373),5:(610,389),6:(650,365),
  7:(900,380),8:(640,380),9:(850,420),10:(490,420),11:(920,392),
  12:(820,470),13:(930,365),14:(640,370),15:(880,360),16:(895,356),17:(640,390),18:(640,370)
 }.get(sid,(640,360))
 for beat in BEAT_GUIDE[str(sid)]:
  delta=t-beat["at"]
  if delta < 0 or delta > .42: continue
  q=delta/.42; alpha=int(190*(1-q)); fx=beat["fx"]; cx,cy=target
  if any(k in fx for k in ("scan","sweep","rake","wipe","sheen")):
   xx=int(120+((delta/.42)*1040))
   col=CORAL if "scan" in fx else CYAN
   d.polygon(((xx-10,190),(xx+5,190),(xx+120,525),(xx+105,525)),fill=(*col,max(0,alpha//5)))
   line(d,(xx,190,xx+115,525),(*col,alpha),3)
  elif any(k in fx for k in ("tree","branch","root","node","ast","lock","result","total","price","coupon","discount","status","confirm","snap","stamp","nfc","ripple","focus","formula","token","rule","syntax","semantic","valid","digit","sequence","production","leaf")):
   r=int(10+delta*110)
   col=AMBER if any(k in fx for k in ("result","total","price","coupon","discount","digit","stamp")) else CYAN
   d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(*col,alpha),width=2)
   if "token" in fx or "character" in fx:
    for j in range(3):
     ox=int(math.cos(j*2.1+delta*5)*r*1.5); oy=int(math.sin(j*2.1+delta*5)*r*.8)
     d.rounded_rectangle((cx+ox-3,cy+oy-3,cx+ox+3,cy+oy+3),radius=1,fill=(*col,alpha))
  elif "flash" in fx or "match_cut" in fx or "title" in fx:
   line(d,(0,185,W,185),(*AMBER,alpha),3)
   line(d,(0,190,W,190),(*WHITE,alpha//2),1)
  elif any(k in fx for k in ("truck","dolly","approach","card_slide","paper_feed","line_item","operand","travel","rewire","bracket","error","warn","bag","settle","green")):
   for j in range(3):
    yy=cy-18+j*18
    line(d,(cx-45-int(delta*48),yy,cx+20-int(delta*16),yy),(*(AMBER if j==1 else CYAN),max(0,alpha-j*40)),2)

def draw_caption(im,s,t):
 speech=v2.SPEECH_DURATION_BY_ID.get(s["id"],DURATIONS[s["id"]-1]-.7)
 caption="" if t>speech+.08 else v2.phrase_at(s["narration"],t,speech)
 if not caption: return im
 d=ImageDraw.Draw(im,"RGBA")
 # fixed lower-third stays outside the main information stage; two lines maximum.
 d.rounded_rectangle((52,625,1228,706),radius=13,fill=(4,10,20,222),outline=(80,111,145,100),width=1)
 f=base.font(17,"regular")
 lines=[]; cur=""
 for word in caption.split():
  nxt=word if not cur else cur+" "+word
  if cur and base.tw(d,nxt,f)>1110: lines.append(cur); cur=word
  else: cur=nxt
 if cur: lines.append(cur)
 for j,l in enumerate(lines[:2]):
  d.text((75,640+j*25),l,font=f,fill=WHITE)
 return im

def frame_v3(s,local,duration):
 style="retail" if s["id"] in (1,2,3,16,18) else ("paper" if s["id"]==17 else "tech")
 im=bg(style).copy(); d=ImageDraw.Draw(im,"RGBA")
 t=max(0,min(duration,local)); p=t/max(.01,duration)
 motion_t = t if s["id"] <= 3 else t * (8.8 / max(0.1, duration))
 # clean art direction per shot; no universal banner/panel framework
 if s["motif"]=="hook_storefront":
  draw_shop(d,t)
  # question sits in clear sky-space, outside the store silhouette
  d.rounded_rectangle((55,40,1225,149),radius=17,fill=(5,12,24,142),outline=(255,185,83,145),width=1)
  headline(d,s,True)
 elif s["motif"]=="hook_scan":
  draw_barcode(d,t)
  d.rounded_rectangle((55,40,1225,149),radius=17,fill=(5,12,24,152),outline=(255,185,83,145),width=1)
  headline(d,s,True)
  # readable one-word consequence follows the scan beam
  center(d,640,560,"BIP  →  DATA  →  ?",19,CYAN,"mono")
 elif s["motif"]=="hook_total":
  draw_pos_hook(d,t)
  d.rounded_rectangle((55,40,1225,149),radius=17,fill=(5,12,24,152),outline=(255,185,83,145),width=1)
  headline(d,s,True)
 else:
  headline(d,s,False)
  motif=s["motif"]
  if motif=="counter_formula": draw_formula(d,motion_t)
  elif motif=="tokenization": draw_tokens(d,motion_t)
  elif motif=="cfg_rules": draw_cfg(d,motion_t)
  elif motif=="syntax_check": draw_syntax(d,motion_t)
  elif motif=="parse_tree": draw_parse_tree(d,motion_t)
  elif motif=="precedence": draw_precedence(d,motion_t,False)
  elif motif=="parentheses": draw_precedence(d,motion_t,True)
  elif motif=="semantic_check": draw_semantic(d,motion_t)
  elif motif=="subtotal": draw_subtotal(d,motion_t)
  elif motif=="discount": draw_discount(d,motion_t)
  elif motif=="ast": draw_ast(d,motion_t)
  elif motif=="evaluate": draw_evaluate(d,motion_t)
  elif motif=="payment": draw_payment(d,motion_t)
  elif motif=="receipt": draw_receipt(d,motion_t)
  elif motif=="exit_recap": draw_exit(d,motion_t)
 draw_effects(d,s,t)
 # Shot-specific camera movement: gentle push for details, slight pull for the exit.
 zoom=(1.0+0.032*ease(p)) if s["id"] not in (3,18) else (1.045-0.035*ease(p))
 pan_x=int(8*math.sin(p*math.pi)*(1 if s["id"]%2 else -1))
 pan_y=int(3*math.sin(p*math.pi*1.3))
 if zoom>1.002:
  nw=int(W*zoom); nh=int(H*zoom)
  im=im.resize((nw,nh),Image.Resampling.BICUBIC)
  left=max(0,min(nw-W,(nw-W)//2+pan_x)); top=max(0,min(nh-H,(nh-H)//2+pan_y))
  im=im.crop((left,top,left+W,top+H))
 return draw_caption(im,s,t)

def write_director_guide(out):
 out=Path(out); elapsed=0
 detail={
 1:("4s exterior-to-door dolly; shopper walk cycle, sliding-door panels, warm spill light.","Question title enters once with a 6-frame ease-out; parallax pavement moves slower than foreground. SFX footfall at walk contact; door chime at light-rake cue.","Match cut on the door seam toward the scanner; do not linger on store geography."),
 2:("4s close-up: package, barcode, scanner housing, moving scan beam.","Laser crosses barcode once, thin red core with short glow; only on crossing, trigger the scan chirp. Small data fragments move toward frame right after scan, not before.","Cut on the direction of the beam toward POS screen. No full-screen glitch or persistent laser."),
 3:("4s POS screen close-up; digits count to Rp48.600 while equation stays readable.","Numeric count eases and settles; one green lock ring follows the total-chime. Match-cut the screen edge into the teaching screen.","This is the final hook. Start explaining the formula in the next shot; do not add an extra journey montage."),
 4:("8s front-on POS screen with formula and moving focus cursor.","A restrained glass reflection crosses once; formula is revealed by token-sized groups. Cursor underlines the active symbol, then holds long enough to read.","Keep narration caption below the display. Formula remains high contrast and never moves with the reflection."),
 5:("8s characters split into five token chips and settle in one horizontal reading order.","Letters separate, magnetize into token blocks with slight overshoot, then arrows connect left-to-right. Pulse only the token currently named by voiceover.","No floating token confetti. Preserve exact order: IDENTIFIER, EQUALS, NUMBER, MINUS, NUMBER."),
 6:("9s three CFG productions enter sequentially.","Each rule slides 120 px, eases, and settles; underline left-hand nonterminal then reveal right-hand production. The active rule gets a small cyan edge, not an all-card glow.","Keep each rule on a fixed row. Do not animate all rows at identical speed or obscure the grammar with captions."),
 7:("7s split-screen valid versus invalid token order.","Valid line draws left-to-right with green ticks. Invalid line briefly misaligns at the first violating position and returns to a stable red state.","Use the distinction token kinds versus grammar acceptance; do not label tokenization itself as the parser."),
 8:("9s parse tree grows root-first, edges before child nodes, leaves last.","Draw connectors progressively from parent to child; node chips arrive with a 3–5 px overshoot and damped settle. Highlight minus only while discussing the relation.","Keep parent/child alignment consistent; no branch should pass through a label. Hold the final tree at least one second."),
 9:("9s precedence tree for 2 + 3 × 4 = 14.","Illuminate multiplication branch first, dim non-active sibling slightly, then stamp 14 at the end. Short amber arc follows the multiplication subtree.","The visual grouping must make multiplication subordinate to addition. Do not animate 2+3 first."),
 10:("7s parentheses example (2 + 3) × 4 = 20; tree structure changes.","Amber bracket traces the left subtree, then root changes to multiplication. Result swaps from prior value to 20 only after branch settles.","Use the same node positions as scene 9 where possible so the structural change is comparable."),
 11:("7s semantic validation, passing fields on left and undefined reference on right.","Checks appear one at a time beside their field. One red cross marks the missing value; stop movement during the verdict.","Do not conflate syntax errors with undefined names or incompatible values."),
 12:("8s item rows reveal 18.500, 21.500, 14.000; subtotal rolls to 54.000.","Rows stagger by 6–8 frames; each register tick coincides with row arrival. Sum rolls once and then locks to Rp54.000.","The three prices must sum exactly to Rp54.000. Avoid continuous number wobble after the value resolves."),
 13:("8s coupon drops beside 54.000; discount resolves to 5.400.","Coupon uses one downward move and a slight elastic settle. A horizontal wipe converts 10% × 54.000 to 5.400; total-chime only on final value.","Arithmetic callout is explicit: 54.000 × 0,10 = 5.400. No discount animation before the subtotal is visible."),
 14:("8s parse tree simplifies to AST: SUB with SUBTOTAL and DISKON operands.","Parent node forms first, then operands travel inward and snap to fixed left/right anchors. Fade punctuation details without removing operator or values.","Keep AST semantic children distinct; do not turn nodes into decorative particles."),
 15:("8s operands move toward subtraction operator, result settles at 48.600.","Inputs travel on curved, eased paths; operator activates only after both operands arrive. Result snaps once and remains still for reading.","Equation is invariant: 54.000 − 5.400 = 48.600. Do not show a wrong intermediate final answer."),
 16:("6s close-up payment terminal; card approaches and touches the NFC zone.","Card accelerates into place, decelerates at contact; concentric NFC ripple starts at touch, then approved status and chime occur together.","No approval green before terminal response. Keep tap action and status as separate beats."),
 17:("7s receipt paper feeds vertically; row details print in order.","Paper grows downward with a subtle shadow. Subtotal, discount, total reveal as three discrete lines; barcode draws last. End with a short held audit frame.","Receipt totals must match the lesson. Paper motion should feel continuous, not like a panel popping in."),
 18:("5s brief exit shot; store recedes while shopper walks out with a bag; concept chain closes.","Camera eases back, shopper limbs continue a walk cycle, concept chips appear left-to-right. Final title locks only after the last connector arrives.","This is a short visual punctuation, not a second opening or a return to a long store journey.")
 }
 guide=["# Director's VFX and Motion Guide — Cashier-first V3","",
 "## Creative correction","",
 "V2's principal failure was structural: almost every scene reused the same frame template and narration slab. This version uses a different composition for each visual task. The exterior-to-cashier opening is exactly three short hook clips (12 seconds total); scene 4 begins the explanation at the register.",
 "",
 "## Global animation rules","",
 "- Output canvas: 1920×1080 at 24 fps. Procedural drawing source: 1280×720, enlarged with Lanczos scaling.",
 "- Motion uses eased acceleration and deceleration; moving products and UI nodes need a short overshoot followed by a stable hold. A hold is deliberate, not a frozen scene.",
 "- Use camera push or pull only 2–4%, with a separate short pan. Foreground moves faster than background when simulating parallax.",
 "- Keep one primary focal point and at most one secondary effect at a time. Glow is an accent, not a permanent outline around every object.",
 "- Synchronize scan beam to scan chirp, item-row arrival to register tick, formula/result lock to confirmation sound, NFC ripple to card tap, and paper advance to printer audio.",
 "- Reserve the lower 95 px for subtitles. Never cover formulas, tree leaves, totals, or the relevant scanner/contact point with captions.",
 "- Prefer match-on-action cuts at the scan beam, POS screen edge, token stream direction, and receipt paper edge. Avoid decorative transition packs, perpetual particles, generic grid overlays, excessive flashes, or unrelated zooms.",
 "- Mathematical truth gate: 54.000 − 5.400 = 48.600; 10% of 54.000 = 5.400; 2 + 3 × 4 = 14; (2 + 3) × 4 = 20. Hold the final value still long enough to read.",
 "- Artistic acceptance is separate from render/codec validation. Review human silhouette quality, pose readability, TTS pronunciation, cue timing, mix balance, and subtitle overlap before calling the film final.",
 "",
 "## Shot-by-shot plan",""]
 for s,dur in zip(SCENES,DURATIONS):
  title,fx,cut=detail[s["id"]]
  start=elapsed; end=elapsed+dur
  def stamp(sec):
   mm=int(sec//60); ss=sec-mm*60
   return f"{mm:02d}:{ss:05.2f}"
  guide.extend([f"### {s['id']:02d}. {s['title']} — {stamp(start)}–{stamp(end)}","",
   f"**Narration:** {s['narration']}",
   f"**Blocking and movement:** {title}",
   f"**Effects and sound sync:** {fx}",
   f"**Edit and legibility:** {cut}","",
   "| Relative beat | Action | Effect | SFX |","|---:|---|---|---|"])
  for b in BEAT_GUIDE[str(s["id"])]:
   sec=start+b["at"]; sound=b.get("sfx")
   guide.append(f"| {stamp(sec)} | {b['action']} | {b['fx']} | {SFX_INFO.get(sound,'silent hold') if sound else 'silent hold'} |")
  guide.append("")
  elapsed=end
 (out/"visual-effect-cue-sheet.md").write_text("\n".join(guide),encoding="utf-8")
 (out/"motion-direction-v3.md").write_text("\n".join(guide),encoding="utf-8")
 (out/"README-V3.txt").write_text(
  "DARI KASIR KE DALAM PIKIRAN KOMPUTER — V3\n\n"
  "Hook: 3 shots / 12 seconds. Directly after the third question, the lesson starts at the POS register.\n"
  "Duration: 240 seconds; 18 scenes; 1920x1080 at 24 fps; H.264 + AAC stereo 48 kHz.\n"
  "Included: MP4, SRT, transcript, generated SFX stem, SFX cue JSON, shot-by-shot VFX guide, contact sheet, manifest.\n"
  "Source visuals and SFX are generated procedurally. No external reference images are imported.\n"
  "Technical QA does not substitute for full human visual and listening QA.\n",encoding="utf-8")

def configure():
 v2.SCENES=SCENES; v2.DURATIONS=DURATIONS; v2.TOTAL=TOTAL; v2.BEAT_GUIDE=BEAT_GUIDE
 base.SCENES=SCENES; base.DURATIONS=DURATIONS; base.TOTAL=TOTAL
 base.MOTIFS={s["motif"] for s in SCENES}
 base.frame=frame_v3
 base.render_video.__globals__["frame"]=frame_v3
 base.write_srt=lambda path: v2.write_srt_v2(path)

def main():
 configure()
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument("--ffmpeg",default="ffmpeg"); ap.add_argument("--ffprobe",default="ffprobe")
 ap.add_argument("--output-dir",required=True); ap.add_argument("--work-dir",default="")
 args=ap.parse_args()
 out=Path(args.output_dir).resolve(); out.mkdir(parents=True,exist_ok=True)
 work=Path(args.work_dir).resolve() if args.work_dir else out/".work"; work.mkdir(parents=True,exist_ok=True)
 final=out/"Dari_Kasir_Cashier_First_Motion_Master_v3.mp4"
 visual_only=work/"visual-v3-only.mp4"; contact=out/"cashier-first-contact-sheet-v3.jpg"
 if len(SCENES)!=18 or sum(DURATIONS)!=240: raise RuntimeError("V3 scene/runtime contract failed.")
 if 54000-5400!=48600 or round(54000*.10)!=5400: raise RuntimeError("Canonical transaction arithmetic failed.")
 print("V3: 3 hook clips / 12 seconds; cashier lesson starts in scene 4; 18 scenes / 240 seconds.",flush=True)
 audio=v2.make_audio_v2(args.ffmpeg,args.ffprobe,work,out)
 # Apply a bounded fade on the actual 240-second V3 timeline after mixing.
 faded=work/"master-audio-v3-faded.wav"
 base.run([args.ffmpeg,"-y","-hide_banner","-loglevel","error","-i",str(audio["mixed"]),
  "-af",f"afade=t=out:st={TOTAL-1.5:.3f}:d=1.5,alimiter=limit=0.93,aresample=48000",
  "-ar","48000","-ac","2","-c:a","pcm_s16le",str(faded)])
 if abs(base.duration(args.ffprobe,faded)-TOTAL)>.12: raise RuntimeError("Faded V3 audio timeline mismatch.")
 audio["mixed"]=faded
 cue_path=out/"sound-effect-cue-sheet.json"
 cue_data=json.loads(cue_path.read_text(encoding="utf-8"))
 cue_data["version"]="v3"
 cue_data["duration_sec"]=TOTAL
 cue_data["opening_structure"]="three 4-second question hooks, then cashier explanation"
 cue_path.write_text(json.dumps(cue_data,ensure_ascii=False,indent=2),encoding="utf-8")
 write_director_guide(out)
 if abs(base.duration(args.ffprobe,audio["mixed"])-TOTAL)>.12: raise RuntimeError("V3 audio timeline is not 240 seconds.")
 print("Render scene-specific movement and camera timing.",flush=True)
 render=base.render_video(args.ffmpeg,visual_only,contact)
 base.run([args.ffmpeg,"-y","-hide_banner","-loglevel","warning","-i",str(visual_only),"-i",str(audio["mixed"]),
  "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","192k","-ar","48000","-ac","2","-t",str(TOTAL),
  "-movflags","+faststart",str(final)])
 media=base.validate(args.ffmpeg,args.ffprobe,final)
 manifest={
  "project":"Dari Kasir ke Dalam Pikiran Komputer","version":"cashier-first-motion-v3.0.0",
  "created_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
  "creative_revision":{"hook_scene_count":3,"hook_duration_sec":12,"lesson_starts_scene":4,
    "opening":"Storefront question → barcode question → total-validity question → immediate POS lesson"},
  "method":"Scene-specific Pillow vector illustration and animated diagrams streamed to FFmpeg; no external visual assets.",
  "reference_images_used":0,"external_visual_assets_used":0,"scene_count":len(SCENES),
  "scene_durations_sec":DURATIONS,"target_duration_sec":TOTAL,"target_frames":TOTAL*FPS,
  "audio":{"voice":base.VOICE,"provider_counts":audio["providers"],"mix":audio["mix"],"voice_qc":"PENDING_HUMAN_LISTENING",
    "generated_sfx_events":len(audio["sfx_events"]),"sfx_stem":"sound-effects-only.wav",
    "sfx_cue_sheet":"sound-effect-cue-sheet.json","vfx_director_guide":"visual-effect-cue-sheet.md"},
  "render":render,"validation":media,
  "motion_design":{"shot_specific_composition":True,"camera_push_pull":True,"ease_and_settle":True,
    "three_sync_beats_per_scene":True,"beat_clock":"aligned to measured voice duration"},
  "acceptance":"TECHNICAL_PASS_HUMAN_VISUAL_AND_LISTENING_QC_PENDING",
  "scenes":[{"id":s["id"],"title":s["title"],"motif":s["motif"],"narration":s["narration"],
    "duration_sec":DURATIONS[i],"beats":BEAT_GUIDE[str(s["id"])]} for i,s in enumerate(SCENES)]
 }
 (out/"production-manifest-v3.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
 (out/"concept-v3.md").write_text("# Cashier-first V3\n\nThree short question hooks move from the store exterior to barcode scanning to the POS total, then the lesson begins immediately at the cashier. It explains tokenization, CFG, syntax validation, parse trees, operator precedence, semantic validation, subtotal/discount arithmetic, AST, evaluation, payment, and receipt audit.\n\nRuntime: 240 seconds, 18 scenes, 24 fps. Visual compositions and motions are authored per scene, and the shot-by-shot VFX sheet supplies blocking, movement, timing, sync, transitions, and legibility constraints.\n",encoding="utf-8")
 # Full package contains render, subtitle, voice transcript, SFX stem/cues, and the shot-by-shot direction.
 package=out/"Dari_Kasir_Cashier_First_V3_Full_Package.zip"
 with zipfile.ZipFile(package,"w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(out.iterdir()):
   if p.is_file() and p!=package and not p.name.startswith("."):
    z.write(p,p.name)
 print(json.dumps({"status":"TECHNICAL_PASS","output":str(final),"package":str(package),
  "duration_sec":media["duration_sec"],"video":media["video"],"audio":media["audio"],
  "sfx_events":len(audio["sfx_events"]),"scene_count":len(SCENES),"hook_duration_sec":12,
  "size_bytes":media["size_bytes"],"acceptance":manifest["acceptance"]},ensure_ascii=False,indent=2),flush=True)
 return 0

configure()

if __name__ == "__main__":
 raise SystemExit(main())
