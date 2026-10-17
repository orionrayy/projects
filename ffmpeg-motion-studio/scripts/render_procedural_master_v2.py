#!/usr/bin/env python3
"""V2 cinematic, sound-effect-guided procedural supermarket-to-exit explainer."""
from __future__ import annotations
import argparse, json, math, random, subprocess, time, wave
from array import array
from pathlib import Path
from PIL import ImageDraw
import render_procedural_master as base

SCENES = [{"id":1,"motif":"store_front","title":"Minimarket di depan kita","short":"Mulai di luar, masuk ke dalam","narration":"Perjalanan dimulai dari luar minimarket. Kamera mengikuti pembeli dari trotoar hingga pintu masuk toko."},{"id":2,"motif":"door_entry","title":"Pintu otomatis terbuka","short":"Pintu dan cahaya menandai transisi","narration":"Pintu otomatis terbuka; cahaya dan bunyi pintu menandai perpindahan dari jalan ke ruang belanja."},{"id":3,"motif":"basket_pickup","title":"Ambil keranjang","short":"Orientasi ruang belanja","narration":"Pembeli mengambil keranjang dan mendorongnya ke lorong, menetapkan orientasi sebelum memilih barang."},{"id":4,"motif":"aisle_wide","title":"Menyusuri lorong","short":"Parallax memperjelas kedalaman","narration":"Kamera menyusuri lorong; rak depan dan belakang bergerak berbeda untuk memberi kedalaman."},{"id":5,"motif":"shelf_search","title":"Temukan produk","short":"Sorot pilihan pada rak","narration":"Pembeli mencari produk. Sorotan mengarahkan mata dari rak ke label harga yang relevan."},{"id":6,"motif":"price_compare","title":"Bandingkan label","short":"Harga dan ukuran dibandingkan","narration":"Dua produk dibandingkan berdasarkan harga dan ukuran. Label berdampingan membuat selisih terlihat jelas."},{"id":7,"motif":"product_pick","title":"Masukkan pilihan ke keranjang","short":"Gerak barang terasa berbobot","narration":"Produk terpilih bergerak melengkung dari rak ke keranjang, lalu mendarat dengan gerak berbobot."},{"id":8,"motif":"produce_select","title":"Pilih buah","short":"Buah dipilih satu per satu","narration":"Buah dipilih dari rak; warna dan sorotan muncul hanya saat pilihan terjadi."},{"id":9,"motif":"weigh_produce","title":"Timbang buah","short":"Berat stabil sebelum label dicetak","narration":"Buah ditimbang. Angka berat distabilkan lebih dahulu, kemudian printer mengeluarkan label harga."},{"id":10,"motif":"label_attach","title":"Tempel label harga","short":"Label mengikuti jalur cetak","narration":"Kamera mengikuti label dari printer ke kemasan agar urutan tindakan tetap terbaca."},{"id":11,"motif":"cart_walk","title":"Menuju kasir","short":"Perpindahan lokasi yang dinamis","narration":"Keranjang bergerak menuju kasir. Parallax rak dan tracking camera mempercepat perpindahan lokasi."},{"id":12,"motif":"checkout_queue","title":"Antrean kasir","short":"Fokus berpindah ke kasir","narration":"Pembeli masuk antrean; fokus kamera beralih ke konveyor dan layar kasir."},{"id":13,"motif":"conveyor_load","title":"Barang ke konveyor","short":"Setiap produk punya ruang","narration":"Barang masuk konveyor satu per satu, diberi jarak agar setiap proses scan terlihat."},{"id":14,"motif":"barcode_scan","title":"Bip pemindai","short":"SFX dan sinar serentak","narration":"Garis laser menyapu barcode. Setiap bip muncul bersama sorot dan perubahan status barang."},{"id":15,"motif":"pos_line_items","title":"Layar POS terisi","short":"Setiap bip menambah satu baris","narration":"Setiap pemindaian menambah satu baris POS dengan nama, identitas, dan harga produk."},{"id":16,"motif":"tokenize_sale","title":"Tokenisasi transaksi","short":"Karakter berubah menjadi unit","narration":"Teks transaksi di layar dipecah menjadi token: nama item, operator, angka, dan diskon."},{"id":17,"motif":"token_stream","title":"Aliran token","short":"Urutan token tetap terbaca","narration":"Token disusun dalam aliran berurutan. Identitas dan urutan membatasi bagaimana parser membaca input."},{"id":18,"motif":"cfg_rules","title":"Aturan CFG","short":"Node aturan mengikuti narasi","narration":"CFG menetapkan aturan produksi. Terminal, nonterminal, dan simbol awal menjelaskan bentuk ekspresi yang sah."},{"id":19,"motif":"parse_tree","title":"Parse tree terbentuk","short":"Akar, cabang, lalu daun","narration":"Parser membangun parse tree dari akar ke cabang lalu daun, merekam hubungan sintaks."},{"id":20,"motif":"precedence","title":"Prioritas operator","short":"Prioritas jadi visual","narration":"Perkalian diproses lebih dahulu. Struktur pohon menjelaskan prioritas, sehingga hasilnya empat belas."},{"id":21,"motif":"subtotal","title":"Subtotal Rp54.000","short":"Wipe ke nilai yang benar","narration":"POS menampilkan subtotal Rp54.000 setelah seluruh barang dipindai dan harga diverifikasi."},{"id":22,"motif":"discount_apply","title":"Diskon Rp5.400","short":"Diskon sebagai operasi","narration":"Kupon mengurangi Rp5.400 dari subtotal. Garis pengurangan menunjukkan operasi yang diterapkan."},{"id":23,"motif":"total_due","title":"Total Rp48.600","short":"Total muncul setelah hitung","narration":"Total Rp48.600 muncul setelah subtotal dan diskon dikunci, bukan melalui angka perantara yang menyesatkan."},{"id":24,"motif":"semantic_check","title":"Validasi transaksi","short":"Pemeriksaan satu per satu","narration":"Sebelum pembayaran, sistem memeriksa identitas item, kecocokan harga, dan validitas diskon."},{"id":25,"motif":"ast_build","title":"AST pengurangan","short":"Operasi diringkas menjadi struktur","narration":"AST merangkum subtotal dikurangi diskon menjadi satu operator dengan dua operand."},{"id":26,"motif":"evaluate_total","title":"Evaluasi total","short":"Operand mengalir ke hasil","narration":"Kedua operand mengalir ke operator. Evaluasi menghasilkan total Rp48.600 yang dapat diuji."},{"id":27,"motif":"payment_tap","title":"Ketuk kartu","short":"Gelombang pada titik sentuh","narration":"Kartu mendekati terminal. Ripple NFC muncul setelah sentuhan, sedangkan layar menunggu respons."},{"id":28,"motif":"payment_approved","title":"Pembayaran disetujui","short":"Status dan chime selaras","narration":"Terminal menyatakan pembayaran disetujui. Status hijau, centang, dan chime muncul serempak."},{"id":29,"motif":"receipt_print","title":"Struk tercetak","short":"Kertas mengikuti suara printer","narration":"Printer mengeluarkan struk secara bertahap. Kamera menahan frame ketika total dan barcode terbaca."},{"id":30,"motif":"bag_items","title":"Kemas belanjaan","short":"Barang masuk tas secara berurutan","narration":"Barang dipindahkan ke tas melalui lintasan terpisah; tas turun sedikit saat menerima beban."},{"id":31,"motif":"cashier_thanks","title":"Terima kasih","short":"Interaksi manusia singkat","narration":"Kasir dan pembeli saling mengangguk. Ucapan singkat mengakhiri interaksi sebelum menuju pintu."},{"id":32,"motif":"exit_door","title":"Keluar melalui pintu","short":"Pintu terbuka ke dunia luar","narration":"Pintu membuka ke luar, pembeli melewati ambang, dan cahaya jalan masuk ke frame."},{"id":33,"motif":"walk_outside","title":"Kembali ke trotoar","short":"Langkah melewati ambang","narration":"Kamera mengikuti langkah ke trotoar; perubahan latar memastikan pembeli benar-benar sudah keluar."},{"id":34,"motif":"concept_recap","title":"Empat konsep inti","short":"Ringkas istilah saat perjalanan berakhir","narration":"Empat konsep dirangkum: tokenisasi mengenali unit, CFG memberi aturan, parse tree mencatat pembentukan, AST merangkum operasi."},{"id":35,"motif":"receipt_audit","title":"Struk untuk audit","short":"Angka pada struk konsisten","narration":"Struk memastikan hasil transaksi dapat diaudit."},{"id":36,"motif":"store_recede","title":"Perjalanan selesai","short":"Wide shot menutup kisah","narration":"Pembeli terus berjalan menjauh. Kamera mundur memperlihatkan pintu toko makin kecil di belakang."},{"id":37,"motif":"end_walk","title":"Perjalanan berakhir","short":"Transaksi dapat diaudit","narration":"Perjalanan berakhir di trotoar. Struktur data membuat transaksi dapat dijelaskan, dihitung, dan diaudit."}]
DURATIONS = [11] * 20 + [10] * 17
TOTAL = sum(DURATIONS)
BEAT_GUIDE = {"1":[{"at":0.8,"action":"sign_glow","fx":"sign_glow","sfx":"store_chime","gain":0.58},{"at":3.5,"action":"approach_parallax","fx":"approach_parallax","sfx":"footsteps","gain":0.45},{"at":7.3,"action":"camera_push","fx":"camera_push","sfx":"whoosh","gain":0.52}],"2":[{"at":0.8,"action":"door_split","fx":"door_split","sfx":"door_chime","gain":0.58},{"at":3.5,"action":"light_sweep","fx":"light_sweep","sfx":"whoosh","gain":0.45},{"at":7.3,"action":"threshold_cross","fx":"threshold_cross","sfx":"footsteps","gain":0.52}],"3":[{"at":0.8,"action":"pickup_arc","fx":"pickup_arc","sfx":"basket_pick","gain":0.58},{"at":3.5,"action":"impact_bounce","fx":"impact_bounce","sfx":"basket_drop","gain":0.45},{"at":7.3,"action":"wheel_roll","fx":"wheel_roll","sfx":"cart_roll","gain":0.52}],"4":[{"at":0.8,"action":"forward_push","fx":"forward_push","sfx":"whoosh","gain":0.58},{"at":3.5,"action":"shelf_parallax","fx":"shelf_parallax","sfx":"cart_roll","gain":0.45},{"at":7.3,"action":"rack_glow","fx":"rack_glow","sfx":"price_tick","gain":0.52}],"5":[{"at":0.8,"action":"selection_glow","fx":"selection_glow","sfx":"token_pop","gain":0.58},{"at":3.5,"action":"light_sweep","fx":"light_sweep","sfx":"price_tick","gain":0.45},{"at":7.3,"action":"focus_hold","fx":"focus_hold","sfx":None,"gain":0}],"6":[{"at":0.8,"action":"label_pop_left","fx":"label_pop_left","sfx":"token_pop","gain":0.58},{"at":3.5,"action":"label_pop_right","fx":"label_pop_right","sfx":"token_pop","gain":0.45},{"at":7.3,"action":"compare_lock","fx":"compare_lock","sfx":"price_tick","gain":0.52}],"7":[{"at":0.8,"action":"pickup_arc","fx":"pickup_arc","sfx":"product_pick","gain":0.58},{"at":3.5,"action":"motion_trail","fx":"motion_trail","sfx":"whoosh","gain":0.45},{"at":7.3,"action":"basket_impact","fx":"basket_impact","sfx":"basket_drop","gain":0.52}],"8":[{"at":0.8,"action":"fruit_pop","fx":"fruit_pop","sfx":"token_pop","gain":0.58},{"at":3.5,"action":"pickup_arc","fx":"pickup_arc","sfx":"product_pick","gain":0.45},{"at":7.3,"action":"focus_lock","fx":"focus_lock","sfx":None,"gain":0}],"9":[{"at":0.8,"action":"scale_pulse","fx":"scale_pulse","sfx":"scale_beep","gain":0.58},{"at":3.5,"action":"meter_settle","fx":"meter_settle","sfx":"scale_beep","gain":0.45},{"at":7.3,"action":"label_feed","fx":"label_feed","sfx":"label_print","gain":0.52}],"10":[{"at":0.8,"action":"paper_feed","fx":"paper_feed","sfx":"label_print","gain":0.58},{"at":3.5,"action":"label_arc","fx":"label_arc","sfx":"paper_rip","gain":0.45},{"at":7.3,"action":"label_snap","fx":"label_snap","sfx":"token_pop","gain":0.52}],"11":[{"at":0.8,"action":"motion_streaks","fx":"motion_streaks","sfx":"cart_roll","gain":0.58},{"at":3.5,"action":"shelf_parallax","fx":"shelf_parallax","sfx":"whoosh","gain":0.45},{"at":7.3,"action":"checkout_reveal","fx":"checkout_reveal","sfx":"checkout_tick","gain":0.52}],"12":[{"at":0.8,"action":"queue_step","fx":"queue_step","sfx":"footsteps","gain":0.58},{"at":3.5,"action":"belt_start","fx":"belt_start","sfx":"cart_roll","gain":0.45},{"at":7.3,"action":"focus_push","fx":"focus_push","sfx":"whoosh","gain":0.52}],"13":[{"at":0.8,"action":"belt_move","fx":"belt_move","sfx":"basket_drop","gain":0.58},{"at":3.5,"action":"belt_move","fx":"belt_move","sfx":"basket_drop","gain":0.45},{"at":7.3,"action":"scanner_reveal","fx":"scanner_reveal","sfx":"whoosh","gain":0.52}],"14":[{"at":0.8,"action":"scan_laser","fx":"scan_laser","sfx":"scan_beep","gain":0.58},{"at":3.5,"action":"scan_flash","fx":"scan_flash","sfx":"scan_beep","gain":0.45},{"at":7.3,"action":"scan_flash","fx":"scan_flash","sfx":"scan_beep","gain":0.52}],"15":[{"at":0.8,"action":"row_reveal","fx":"row_reveal","sfx":"register_tick","gain":0.58},{"at":3.5,"action":"price_align","fx":"price_align","sfx":"register_tick","gain":0.45},{"at":7.3,"action":"count_snap","fx":"count_snap","sfx":"checkout_tick","gain":0.52}],"16":[{"at":0.8,"action":"glyph_sweep","fx":"glyph_sweep","sfx":"token_pop","gain":0.58},{"at":3.5,"action":"token_split","fx":"token_split","sfx":"token_pop","gain":0.45},{"at":7.3,"action":"operator_flash","fx":"operator_flash","sfx":"parser_click","gain":0.52}],"17":[{"at":0.8,"action":"token_pop","fx":"token_pop","sfx":"token_pop","gain":0.58},{"at":3.5,"action":"stream_connect","fx":"stream_connect","sfx":"parser_click","gain":0.45},{"at":7.3,"action":"token_pan","fx":"token_pan","sfx":"whoosh","gain":0.52}],"18":[{"at":0.8,"action":"rule_reveal","fx":"rule_reveal","sfx":"parser_click","gain":0.58},{"at":3.5,"action":"rule_branch","fx":"rule_branch","sfx":"parser_click","gain":0.45},{"at":7.3,"action":"root_pulse","fx":"root_pulse","sfx":"token_pop","gain":0.52}],"19":[{"at":0.8,"action":"tree_root","fx":"tree_root","sfx":"tree_assemble","gain":0.58},{"at":3.5,"action":"tree_branch","fx":"tree_branch","sfx":"tree_assemble","gain":0.45},{"at":7.3,"action":"tree_leaf","fx":"tree_leaf","sfx":"token_pop","gain":0.52}],"20":[{"at":0.8,"action":"precedence_glow","fx":"precedence_glow","sfx":"calculator_tick","gain":0.58},{"at":3.5,"action":"focus_dimmer","fx":"focus_dimmer","sfx":"whoosh","gain":0.45},{"at":7.3,"action":"result_snap","fx":"result_snap","sfx":"total_chime","gain":0.52}],"21":[{"at":0.7,"action":"value_wipe","fx":"value_wipe","sfx":"register_tick","gain":0.58},{"at":3.1,"action":"value_lock","fx":"value_lock","sfx":"calculator_tick","gain":0.45},{"at":6.5,"action":"equation_link","fx":"equation_link","sfx":"parser_click","gain":0.52}],"22":[{"at":0.7,"action":"coupon_pop","fx":"coupon_pop","sfx":"discount_ping","gain":0.58},{"at":3.1,"action":"discount_outline","fx":"discount_outline","sfx":"calculator_tick","gain":0.45},{"at":6.5,"action":"equation_link","fx":"equation_link","sfx":"parser_click","gain":0.52}],"23":[{"at":0.7,"action":"total_reveal","fx":"total_reveal","sfx":"total_chime","gain":0.58},{"at":3.1,"action":"total_pulse","fx":"total_pulse","sfx":"token_pop","gain":0.45},{"at":6.5,"action":"reading_hold","fx":"reading_hold","sfx":None,"gain":0}],"24":[{"at":0.7,"action":"check_tick","fx":"check_tick","sfx":"validation_tick","gain":0.58},{"at":3.1,"action":"check_tick","fx":"check_tick","sfx":"validation_tick","gain":0.45},{"at":6.5,"action":"check_tick","fx":"check_tick","sfx":"approved_chime","gain":0.52}],"25":[{"at":0.7,"action":"ast_root","fx":"ast_root","sfx":"tree_assemble","gain":0.58},{"at":3.1,"action":"ast_operand","fx":"ast_operand","sfx":"token_pop","gain":0.45},{"at":6.5,"action":"ast_operand","fx":"ast_operand","sfx":"token_pop","gain":0.52}],"26":[{"at":0.7,"action":"value_flow","fx":"value_flow","sfx":"whoosh","gain":0.58},{"at":3.1,"action":"operator_flash","fx":"operator_flash","sfx":"calculator_tick","gain":0.45},{"at":6.5,"action":"result_snap","fx":"result_snap","sfx":"total_chime","gain":0.52}],"27":[{"at":0.7,"action":"card_slide","fx":"card_slide","sfx":"whoosh","gain":0.58},{"at":3.1,"action":"nfc_ripple","fx":"nfc_ripple","sfx":"nfc_tap","gain":0.45},{"at":6.5,"action":"terminal_wait","fx":"terminal_wait","sfx":None,"gain":0}],"28":[{"at":0.7,"action":"status_flash","fx":"status_flash","sfx":"approved_chime","gain":0.58},{"at":3.1,"action":"check_pop","fx":"check_pop","sfx":"token_pop","gain":0.45},{"at":6.5,"action":"confetti_burst","fx":"confetti_burst","sfx":"cash_register","gain":0.52}],"29":[{"at":0.7,"action":"printer_start","fx":"printer_start","sfx":"receipt_printer","gain":0.58},{"at":3.1,"action":"paper_feed","fx":"paper_feed","sfx":"receipt_printer","gain":0.45},{"at":6.5,"action":"receipt_hold","fx":"receipt_hold","sfx":"paper_rip","gain":0.52}],"30":[{"at":0.7,"action":"bag_open","fx":"bag_open","sfx":"bag_rustle","gain":0.58},{"at":3.1,"action":"bag_arc","fx":"bag_arc","sfx":"bag_rustle","gain":0.45},{"at":6.5,"action":"weight_settle","fx":"weight_settle","sfx":"basket_drop","gain":0.52}],"31":[{"at":0.7,"action":"speech_pop","fx":"speech_pop","sfx":"farewell_chime","gain":0.58},{"at":3.1,"action":"bag_lift","fx":"bag_lift","sfx":"bag_rustle","gain":0.45},{"at":6.5,"action":"turn_exit","fx":"turn_exit","sfx":"whoosh","gain":0.52}],"32":[{"at":0.7,"action":"door_split","fx":"door_split","sfx":"door_chime","gain":0.58},{"at":3.1,"action":"threshold_cross","fx":"threshold_cross","sfx":"footsteps","gain":0.45},{"at":6.5,"action":"outside_sweep","fx":"outside_sweep","sfx":"whoosh","gain":0.52}],"33":[{"at":0.7,"action":"walk_cycle","fx":"walk_cycle","sfx":"footsteps","gain":0.58},{"at":3.1,"action":"follow_pullback","fx":"follow_pullback","sfx":"whoosh","gain":0.45},{"at":6.5,"action":"store_recede","fx":"store_recede","sfx":None,"gain":0}],"34":[{"at":0.7,"action":"recap_pop","fx":"recap_pop","sfx":"token_pop","gain":0.58},{"at":3.1,"action":"recap_stagger","fx":"recap_stagger","sfx":"parser_click","gain":0.45},{"at":6.5,"action":"recap_lock","fx":"recap_lock","sfx":"total_chime","gain":0.52}],"35":[{"at":0.7,"action":"receipt_wipe","fx":"receipt_wipe","sfx":"paper_rip","gain":0.58},{"at":3.1,"action":"receipt_link","fx":"receipt_link","sfx":"parser_click","gain":0.45},{"at":6.5,"action":"receipt_total","fx":"receipt_total","sfx":"total_chime","gain":0.52}],"36":[{"at":0.7,"action":"camera_pullback","fx":"camera_pullback","sfx":"whoosh","gain":0.58},{"at":3.1,"action":"walk_off","fx":"walk_off","sfx":"footsteps","gain":0.45},{"at":6.5,"action":"soft_fade","fx":"soft_fade","sfx":None,"gain":0}],"37":[{"at":0.7,"action":"walk_off","fx":"walk_off","sfx":"footsteps","gain":0.58},{"at":3.1,"action":"concept_merge","fx":"concept_merge","sfx":"whoosh","gain":0.45},{"at":6.5,"action":"final_lock","fx":"final_lock","sfx":"farewell_chime","gain":0.52}]}
VOICE=base.VOICE
REFERENCE_IMAGES_USED=0
EXTERNAL_VISUAL_ASSETS_USED=0
base.SCENES=SCENES; base.DURATIONS=DURATIONS; base.TOTAL=TOTAL; base.MOTIFS={s["motif"] for s in SCENES}

SFX_INFO={
 "store_chime":"soft two-note shop entry chime","door_chime":"automatic-door chime","footsteps":"short paired footsteps",
 "whoosh":"short air sweep for camera movement","basket_pick":"plastic basket lift click","basket_drop":"soft weighted basket landing",
 "cart_roll":"quiet trolley-wheel roll","token_pop":"small bright token reveal tick","price_tick":"short price-label tick",
 "product_pick":"soft package pickup and landing","scale_beep":"digital scale confirmation beep","label_print":"short label-printer motor",
 "paper_rip":"soft paper/label tear","checkout_tick":"checkout confirmation click","scan_beep":"barcode scan chirp",
 "register_tick":"POS line-item click","parser_click":"small syntax-node click","tree_assemble":"structure-node tap",
 "calculator_tick":"subtle calculator key tick","discount_ping":"discount confirmation ping","total_chime":"short resolved total chime",
 "validation_tick":"three-stage validation tick","approved_chime":"pleasant payment-approved triad","nfc_tap":"contactless terminal tap",
 "receipt_printer":"receipt motor and paper feed","bag_rustle":"grocery-bag rustle","farewell_chime":"soft friendly closing chime",
 "cash_register":"subtle register ka-chink"
}
SFX_DURATION={"store_chime":.58,"door_chime":.42,"footsteps":.38,"whoosh":.46,"basket_pick":.22,"basket_drop":.24,
 "cart_roll":.48,"token_pop":.14,"price_tick":.12,"product_pick":.30,"scale_beep":.25,"label_print":.72,"paper_rip":.24,
 "checkout_tick":.14,"scan_beep":.22,"register_tick":.13,"parser_click":.12,"tree_assemble":.19,"calculator_tick":.10,
 "discount_ping":.38,"total_chime":.52,"validation_tick":.25,"approved_chime":.65,"nfc_tap":.19,
 "receipt_printer":.85,"bag_rustle":.42,"farewell_chime":.52,"cash_register":.36}
SR=48000

def cue_samples(kind,duration,gain,seed):
    n=max(1,int(duration*SR)); out=array('h'); rng=random.Random(seed)
    for i in range(n):
        t=i/SR; p=i/max(1,n-1); noise=rng.uniform(-1,1)
        if kind in ("store_chime","door_chime","farewell_chime","discount_ping","total_chime","approved_chime"):
            tunes={"approved_chime":[(784,0),(988,.16),(1175,.32)],"farewell_chime":[(660,0),(880,.17)],
             "door_chime":[(920,0),(1240,.13)],"store_chime":[(880,0),(1320,.18)],
             "discount_ping":[(1046,0),(1568,.08)],"total_chime":[(660,0),(990,.14)]}
            signal=sum(.5*math.sin(2*math.pi*f*(t-st))*math.exp(-(t-st)*5.5) for f,st in tunes[kind] if t>=st)
            env=min(1,t*55)*max(0,1-p*.15)
        elif kind=="scan_beep":
            signal=math.sin(2*math.pi*(920*t+1750*t*t)); env=min(1,t*80)*max(0,1-p)**1.5
        elif kind in ("scale_beep","checkout_tick","register_tick","parser_click","calculator_tick","validation_tick","nfc_tap","token_pop","basket_pick"):
            f={"scale_beep":1130,"checkout_tick":1650,"register_tick":1250,"parser_click":1380,"calculator_tick":980,
               "validation_tick":1460,"nfc_tap":720,"token_pop":1760,"basket_pick":480}.get(kind,600)
            signal=.62*math.sin(2*math.pi*f*t)+.2*noise; env=min(1,t*100)*max(0,1-p)**(2.2 if kind!="nfc_tap" else 1.2)
        else:
            env=min(1,t*30)*max(0,1-p)
            if kind=="whoosh": env*=min(1,p*3)
            elif kind=="footsteps": env*=max(0,math.sin(p*math.pi*2.6))**3
            elif kind=="cart_roll": env*=.55+.12*math.sin(t*23)
            elif kind in ("receipt_printer","label_print"): env*=.45+.55*(math.sin(t*47)>0)
            elif kind=="paper_rip": env*=max(0,math.sin(p*math.pi))
            signal=.48*noise
            if kind in ("cart_roll","receipt_printer","label_print","cash_register"):
                signal+=.25*math.sin(2*math.pi*(85 if kind=="cart_roll" else 130)*t)
            if kind=="cash_register": signal+=.25*math.sin(2*math.pi*1120*t)*math.exp(-t*8)
        out.append(max(-32767,min(32767,int(32767*.31*gain*max(0,env)*max(-1,min(1,signal))))))
    return out

def create_sfx_track(out):
    samples=array('h',[0])*(TOTAL*SR); events=[]; elapsed=0; serial=0
    for scene,dur in zip(SCENES,DURATIONS):
        for beat in BEAT_GUIDE[str(scene["id"])]:
            typ=beat.get("sfx")
            if typ:
                absolute=elapsed+beat["at"]; start=round(absolute*SR)
                pulse=cue_samples(typ,SFX_DURATION[typ],beat.get("gain",.5),scene["id"]*1000+serial)
                for k in range(min(len(pulse),len(samples)-start)):
                    samples[start+k]=max(-32767,min(32767,samples[start+k]+pulse[k]))
                events.append({"scene_id":scene["id"],"scene_title":scene["title"],"time_sec":round(absolute,3),
                    "offset_sec":beat["at"],"sfx":typ,"description":SFX_INFO[typ],"gain":beat.get("gain",.5),
                    "visual_action":beat["action"],"visual_effect":beat["fx"]})
                serial+=1
        elapsed+=dur
    path=Path(out)/"sound-effects-only.wav"
    with wave.open(str(path),"wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(samples.tobytes())
    return path,events

def caption_chunks(text):
    words=text.split(); result=[]; current=[]
    for word in words:
        current.append(word)
        if len(current)>=8 and (word.endswith((".",",",";",":")) or len(current)>=9):
            result.append(current); current=[]
    if current: result.append(current)
    return result or [[]]

def phrase_at(text,local,duration):
    chunks=caption_chunks(text); total=max(1,sum(len(c) for c in chunks))
    target=max(0,min(.999,local/max(.1,duration-.7)))*total; upto=0
    for c in chunks:
        upto+=len(c)
        if target<upto: return " ".join(c)
    return " ".join(chunks[-1])

def write_srt_v2(path,details=None):
    data={x["scene_id"]:x for x in (details or [])}; rows=[]; start=0; cue=1
    for scene,dur in zip(SCENES,DURATIONS):
        chunks=caption_chunks(scene["narration"]); det=data.get(scene["id"],{})
        speech=min(dur-.1,max(1.,float(det.get("source_audio_duration_sec",dur-.7))/max(1.,float(det.get("tempo_factor",1.)))))
        words=max(1,sum(map(len,chunks))); used=0
        for c in chunks:
            a=start+speech*used/words; used+=len(c); b=start+speech*used/words
            rows.extend([str(cue),f"{base.tc(a)} --> {base.tc(b)}"," ".join(c),""]); cue+=1
        start+=dur
    Path(path).write_text("\n".join(rows),encoding="utf-8")

def write_cue_sheets(out,events):
    out=Path(out); events=sorted(events,key=lambda x:x["time_sec"])
    (out/"sound-effect-cue-sheet.json").write_text(json.dumps({"project":"Dari Kasir ke Dalam Pikiran Komputer","version":"v2",
      "duration_sec":TOTAL,"sample_rate_hz":SR,"reference_images_used":0,"generated_effect_events":len(events),
      "sound_design_note":"All effects are synthesized procedurally; no external audio samples.",
      "events":events},ensure_ascii=False,indent=2),encoding="utf-8")
    def ts(x):
        ms=round(x*1000); return f"{ms//60000:02d}:{ms%60000//1000:02d}.{ms%1000:03d}"
    lines=["# V2 Sound + Visual Effect Cue Sheet","",
      "Absolute times use one master clock. Each scene has three visual beats; SFX start on the same beat. ",
      "Use the cue timestamp as edit guidance, then human-review pronunciation, event impact, and mix level.",""]
    start=0
    for s,dur in zip(SCENES,DURATIONS):
        lines.extend([f"## {s['id']:02d} — {s['title']} ({ts(start)}–{ts(start+dur)})","",
          "| Time | Beat action | Visual effect | Sound effect |","|---:|---|---|---|"])
        for b in BEAT_GUIDE[str(s["id"])]:
            desc=SFX_INFO.get(b.get("sfx"),"—") if b.get("sfx") else "—"
            lines.append(f"| {ts(start+b['at'])} | {b['action']} | {b['fx']} | {desc} |")
        lines.append(""); start+=dur
    (out/"visual-effect-cue-sheet.md").write_text("\n".join(lines),encoding="utf-8")

def person(d,x,y,scale=1,color=None,phase=0):
    c=color or base.AMBER; r=13*scale; bob=int(2*math.sin(phase*3))
    d.ellipse((x-r,y-102*scale+bob,x+r,y-76*scale+bob),fill=(*c,255))
    base.rounded(d,(x-16*scale,y-75*scale+bob,x+16*scale,y-30*scale+bob),(*c,235),None,9,1)
    stride=math.sin(phase*3.2)*11*scale
    d.line((x-8*scale,y-30*scale+bob,x-13*scale-stride,y),fill=(*c,255),width=max(3,int(5*scale)))
    d.line((x+8*scale,y-30*scale+bob,x+13*scale+stride,y),fill=(*c,255),width=max(3,int(5*scale)))
    d.line((x-9*scale,y-64*scale+bob,x-25*scale,y-42*scale+bob),fill=(*c,245),width=max(3,int(5*scale)))
    d.line((x+9*scale,y-64*scale+bob,x+24*scale,y-45*scale+bob),fill=(*c,245),width=max(3,int(5*scale)))

def cart(d,x,y,scale=1,count=3):
    col=(115,165,190)
    d.line((x,y-42*scale,x+90*scale,y-42*scale),fill=(*col,255),width=max(3,int(4*scale)))
    d.line((x,y-42*scale,x+12*scale,y-2*scale),fill=(*col,255),width=max(3,int(4*scale)))
    d.line((x+12*scale,y-2*scale,x+89*scale,y-2*scale),fill=(*col,255),width=max(3,int(4*scale)))
    d.line((x+85*scale,y-42*scale,x+99*scale,y-12*scale),fill=(*col,255),width=max(3,int(4*scale)))
    for xx in (x+22*scale,x+80*scale):
        d.ellipse((xx-6*scale,y+2*scale,xx+8*scale,y+16*scale),fill=(33,48,65,255),outline=(*base.CYAN,230),width=2)
    colors=(base.AMBER,base.CORAL,base.GREEN,base.VIOLET)
    for i in range(count):
        xx=x+(17+i*19)*scale; yy=y-(18+(i%2)*5)*scale
        base.rounded(d,(int(xx),int(yy-22*scale),int(xx+16*scale),int(yy+2*scale)),(*colors[i%4],235),None,3,1)

def shelf(d,t,offset=0,highlight=-1):
    base.panel(d,(90,245,1190,480),base.BLUE)
    for row,y in enumerate((288,355,422)):
        d.line((112,y+24,1168,y+24),fill=(92,121,157,220),width=4)
        for i,x0 in enumerate(range(125,1145,62)):
            x=x0-int(offset)%62
            if x<112: x+=1040
            c=(base.BLUE,base.CYAN,base.AMBER,base.CORAL,base.VIOLET,base.GREEN)[(i+row*2)%6]
            h=22+((i+row)%3)*5
            base.rounded(d,(x,y-h,x+34,y+16),(*c,210),(*c,220),4,1)
            if highlight==i and row==1: base.rounded(d,(x-5,y-h-7,x+39,y+21),(*c,38),(*base.AMBER,255),7,3)

def storefront(d,t,walk_x=0):
    base.rounded(d,(190,204,1090,504),(19,33,54,255),(76,122,159,255),14,3)
    base.rounded(d,(248,183,1032,249),(29,52,78,255),(*base.CYAN,190),10,2)
    base.center(d,640,199,"MINIMARKET",base.font(29,"bold"),base.WHITE)
    for x in (265,420,860,1015):
        base.rounded(d,(x,270,x+122,453),(7,18,33,255),(75,112,145,255),7,2)
        for yy in (306,353,400):
            d.line((x+8,yy+17,x+114,yy+17),fill=(49,75,101,255),width=3)
            for j in range(4):
                c=(base.CYAN,base.AMBER,base.CORAL,base.VIOLET)[(j+int(t*2))%4]
                base.rounded(d,(x+12+j*26,yy-7,x+29+j*26,yy+17),(*c,235),None,3,1)
    op=min(1,max(0,(t-1)/2.3)); gap=int(86*op)
    base.rounded(d,(549-gap,260,635-gap,468),(8,19,32,255),(84,129,163,255),4,2)
    base.rounded(d,(645+gap,260,731+gap,468),(8,19,32,255),(84,129,163,255),4,2)
    person(d,int(700+walk_x),460,.72,base.AMBER,t)

def fx_flash(d,t,sid):
    for b in BEAT_GUIDE.get(str(sid),[]):
        delta=t-b["at"]
        if -.02<=delta<=.22:
            fx=b["fx"]; alpha=int(185*(1-max(0,delta)/.25))
            if any(w in fx for w in ("glow","flash","pulse","scan","sweep","ripple","flare","pop","snap","lock","total","reveal")):
                x=640+int(145*math.sin(t*2+sid)); y=350; r=12+int(max(0,delta)*165)
                c=base.AMBER if any(w in fx for w in ("price","total","coupon","discount","receipt")) else base.CYAN
                d.ellipse((x-r,y-r,x+r,y+r),outline=(*c,alpha),width=3)
            if any(w in fx for w in ("sweep","laser","wipe")):
                x=int(110+((delta+.02)/.24)*1000); d.line((x,211,x,510),fill=(*base.CYAN,alpha),width=4)
            if any(w in fx for w in ("trail","streak","parallax")):
                for k in range(4): d.line((180+k*37,500-k*4,208+k*37,500-k*4),fill=(*base.BLUE,max(0,alpha-k*30)),width=2)

def visual_v2(d,s,t,dur):
    m=s["motif"]; p=max(0,min(1,t/dur)); e=p*p*(3-2*p); shift=int(t*38)%180
    if m=="store_front":
        storefront(d,t,-int(min(t,8)*8)); base.label(d,305,474,"MASUK → PILIH → BAYAR → KELUAR",base.CYAN,13)
    elif m=="door_entry":
        shelf(d,t,shift); gap=int(115*min(1,max(0,(t-.7)/2)))
        d.rectangle((90,214,640-gap,235),fill=(9,17,31,255)); d.rectangle((640+gap,214,1190,235),fill=(9,17,31,255))
        person(d,int(340+min(t,8)*45),480,.9,base.AMBER,t)
    elif m=="basket_pickup":
        shelf(d,t,shift//3); person(d,350,482,1,base.AMBER,t)
        y=int(410-35*math.sin(min(1,t/2)*math.pi/2)); base.rounded(d,(500,y,690,y+54),(*base.BLUE,215),(*base.CYAN,255),10,3)
        for x in range(515,685,20): d.line((x,y+6,x,y+48),fill=(169,214,232,200),width=2)
        cart(d,760,462,1.05,min(4,int(t/2)+1))
    elif m in ("aisle_wide","shelf_search"):
        shelf(d,t,shift if m=="aisle_wide" else 0,int(t*1.5)%10 if m=="shelf_search" else -1)
        cart(d,830,470,.83,2); person(d,770,460,.88,base.AMBER,t)
        if m=="shelf_search":
            x=130+int(t/dur*980); d.line((x,257,x,437),fill=(*base.CYAN,130),width=3)
            d.ellipse((x-14,315,x+14,343),outline=(*base.AMBER,230),width=3)
            base.chip(d,470,220,340,29,"MENCARI PRODUK",base.CYAN,12)
    elif m=="price_compare":
        shelf(d,t,highlight=3)
        for box,c,title,price,desc in [((170,262,544,437),base.CYAN,"PRODUK A","Rp18.000 / 500 g","harga per gram"),((736,262,1110,437),base.AMBER,"PRODUK B","Rp24.000 / 800 g","diskon tersedia")]:
            base.panel(d,box,c); x=(box[0]+box[2])/2; base.chip(d,box[0]+35,283,130,31,title,c,14)
            base.center(d,x,334,price,base.font(18,"mono"),base.WHITE); base.center(d,x,383,desc,base.font(14),base.MUTED)
        if t>5: base.chip(d,478,448,324,36,"PILIH DENGAN INFORMASI",base.GREEN,13)
    elif m=="product_pick":
        shelf(d,t,highlight=5); x=int(715+e*125); y=int(300+e*126-80*math.sin(math.pi*e))
        base.rounded(d,(x,y,x+48,y+60),(*base.VIOLET,240),(*base.WHITE,230),7,2); base.label(d,x+7,y+20,"ITEM",base.WHITE,10)
        for k in range(5): d.line((x-42-k*7,y+18-k*5,x-15-k*7,y+18-k*5),fill=(*base.CYAN,100),width=2)
        cart(d,810,475,.9,2)
    elif m=="produce_select":
        base.panel(d,(110,240,1170,484),base.GREEN)
        for i,(x,y,c) in enumerate(((230,330,base.CORAL),(320,360,base.GREEN),(425,322,base.AMBER),(523,365,base.CORAL),(625,325,base.GREEN),(735,360,base.AMBER),(845,325,base.CORAL))):
            r=30+int(3*math.sin(t*2+i)); d.ellipse((x-r,y-r,x+r,y+r),fill=(*c,225),outline=(255,255,255,110),width=2)
            d.arc((x-14,y-20,x+14,y+6),180,350,fill=(26,94,56,230),width=3)
        base.chip(d,455,436,370,32,"PRODUK SEGAR / PILIHAN TERUKUR",base.GREEN,12)
    elif m=="weigh_produce":
        base.panel(d,(180,250,1100,484),base.BLUE); base.rounded(d,(365,293,725,462),(13,24,42,255),(108,145,177,255),14,3)
        d.rectangle((405,320,685,386),fill=(4,11,23,255)); base.center(d,545,329,"0.650 kg",base.font(28,"mono"),base.GREEN)
        base.rounded(d,(425,397,665,433),(87,113,137,255),None,8)
        for i in range(5): d.ellipse((465+i*35,397,491+i*35,419),fill=(*(base.CORAL if i%2==0 else base.GREEN),235))
        base.rounded(d,(770,310,1005,448),(*base.PAPER,255),None,6)
        base.center(d,886,325,"LABEL HARGA",base.font(15,"mono"),base.PAPER_INK); base.center(d,886,362,"Rp 12.500",base.font(19,"mono"),(24,100,76))
        for i in range(19): d.line((802+i*8,405,802+i*8,421 if i%3 else 413),fill=base.PAPER_INK,width=2)
    elif m=="label_attach":
        base.rounded(d,(200,270,490,470),(16,33,53,255),(*base.BLUE,255),9,3); base.label(d,225,290,"PRINTER TIMBANGAN",base.CYAN,12)
        base.rounded(d,(250,335,440,452),(*base.PAPER,255),None,4); base.center(d,345,349,"BUAH 0.650 kg",base.font(13,"mono"),base.PAPER_INK)
        base.center(d,345,375,"Rp 12.500",base.font(18,"mono"),(13,98,73)); q=min(1,t/5); x=int(600+q*170); y=int(380+25*math.sin(q*math.pi))
        base.rounded(d,(x,y,x+220,y+90),(*base.GREEN,65),(*base.GREEN,240),10,3)
        base.chip(d,x+21,y+25,178,36,"LABEL MENEMPEL",base.GREEN,12); base.arrow(d,510,355,x-15,395,base.CYAN,3)
    elif m=="cart_walk":
        shelf(d,t,shift); person(d,610,468,.9,base.AMBER,t); cart(d,720,470,1.15,4)
        for i in range(6): d.line((560-i*19,427-i*4,580-i*19,427-i*4),fill=(*base.CYAN,max(0,130-i*19)),width=2)
        base.chip(d,430,216,420,32,"CAMERA TRACKING → CHECKOUT",base.CYAN,12)
    elif m in ("checkout_queue","conveyor_load","barcode_scan","pos_line_items"):
        base.panel(d,(100,218,1180,486),base.BLUE); base.rounded(d,(820,242,1134,383),(5,12,25,255),(*base.CYAN,255),10,3)
        base.label(d,850,255,"POINT OF SALE",base.CYAN,13)
        if m=="checkout_queue":
            for i in range(4): person(d,170+i*120,450,.72,base.AMBER if i==3 else base.MUTED,t+i)
            d.line((125,464,585,464),fill=(*base.MUTED,170),width=4); base.chip(d,860,311,230,39,"ANTREAN → KASIR",base.GREEN,13)
        elif m=="conveyor_load":
            d.rectangle((145,387,785,442),fill=(27,45,62,255))
            for i in range(18):
                x=155+i*34-int(t*26)%34; d.line((x,391,x+20,438),fill=(64,95,122,220),width=2)
            for i in range(4):
                x=int(190+i*142-(t*39)%570)
                if 150<x<780: base.rounded(d,(x,344,x+70,390),(*(base.CORAL,base.AMBER,base.GREEN,base.VIOLET)[i],235),None,5,1)
            base.chip(d,856,311,224,39,"BARANG MENUJU SCAN",base.CYAN,12)
        elif m=="barcode_scan":
            d.rectangle((145,383,785,443),fill=(26,43,60,255)); x=int(170+(t*90)%500)
            base.rounded(d,(x,321,x+130,401),(*base.AMBER,235),None,7,2)
            for j in range(12): d.line((x+12+j*8,343,x+12+j*8,373 if j%3 else 362),fill=(18,28,39,255),width=2)
            laser=int(150+t/dur*620); d.line((laser,306,laser,447),fill=(*base.CORAL,230),width=4)
            d.ellipse((laser-12,330,laser+12,354),fill=(*base.CORAL,45),outline=(*base.CORAL,255),width=3); base.chip(d,845,310,238,38,"SCAN / BIP",base.AMBER,15)
        else:
            base.chip(d,850,306,240,33,"ITEM  HARGA",base.CYAN,13)
            for i,(name,price) in enumerate((("Susu","18.000"),("Roti","12.000"),("Buah","12.500"),("Sabun","11.500"))):
                if t>i*1.8:
                    y=346+i*30; d.text((850,y),name,font=base.font(14),fill=base.WHITE); d.text((1050,y),price,font=base.font(14,"mono"),fill=base.GREEN)
                    d.line((846,y+23,1111,y+23),fill=(56,82,113,180),width=1)
    elif m=="tokenize_sale":
        base.panel(d,(110,250,1170,462),base.VIOLET); base.center(d,640,276,"item=54000-5400",base.font(27,"mono"),base.WHITE)
        for i,(txt,c) in enumerate((("item",base.BLUE),("=",base.AMBER),("54000",base.CYAN),("−",base.CORAL),("5400",base.VIOLET))):
            if t>i*1.4:
                x=110+i*216; base.chip(d,x,357,194,61,txt,c,18)
                if t>i*1.4+.3: base.arrow(d,x+196,387,x+210,387,base.MUTED,2)
        if t>4.5:
            x=128+int((t%2)*460); d.line((x,305,x+90,305),fill=(*base.CYAN,190),width=4)
    elif m=="token_stream":
        base.panel(d,(90,250,1190,466),base.CYAN)
        for i,(txt,c) in enumerate((("IDENTIFIER",base.BLUE),("EQUALS",base.AMBER),("NUMBER",base.CYAN),("MINUS",base.CORAL),("NUMBER",base.VIOLET))):
            x=105+i*216-int(t*18)%90; base.chip(d,x,329,188,69,txt,c,15)
            if i<4: base.arrow(d,x+190,365,x+210,365,base.MUTED,2)
        base.label(d,270,424,"URUTAN TOKEN ADALAH BAGIAN DARI STRUKTUR",base.MUTED,12)
    elif m=="cfg_rules":
        base.panel(d,(110,238,1170,476),base.VIOLET)
        for i,(a,op,b) in enumerate((("Expr","→","Expr + Term | Term"),("Term","→","Number"),("Start","=","Expr"))):
            if t>i*1.9:
                y=272+i*62; base.chip(d,175,y,150,44,a,base.VIOLET,15); base.center(d,395,y+9,op,base.font(22,"mono"),base.AMBER)
                d.text((450,y+10),b,font=base.font(21,"mono"),fill=base.WHITE); d.line((163,y+52,1100,y+52),fill=(74,94,128,145),width=1)
    elif m in ("parse_tree","precedence","ast_build"):
        if m=="parse_tree":
            pts=[(640,257,"Expr"),(420,337,"Expr"),(640,337,"−"),(860,337,"Term"),(420,413,"Term"),(420,470,"NUMBER"),(860,413,"NUMBER")]
            edges=[(0,1),(0,2),(0,3),(1,4),(4,5),(3,6)]
        elif m=="precedence":
            pts=[(640,257,"Expr"),(440,340,"NUMBER"),(640,340,"+"),(845,340,"Term"),(780,421,"×"),(730,476,"3"),(860,476,"4")]
            edges=[(0,1),(0,2),(0,3),(3,4),(4,5),(4,6)]
        else: pts=[(640,285,"SUB"),(440,398,"54.000"),(840,398,"5.400")]; edges=[(0,1),(0,2)]
        edge_count=int(1+min(len(edges),t/dur*len(edges)+.2))
        for a,b in edges[:edge_count]:
            xa,ya,_=pts[a]; xb,yb,_=pts[b]; d.line((xa,ya+18,xb,yb-18),fill=(*base.VIOLET,200),width=3)
        node_count=int(1+min(len(pts)-1,t/dur*len(pts)+.2))
        for i,(x,y,txt) in enumerate(pts[:node_count]):
            c=base.AMBER if (m=="precedence" and txt=="×") or i==0 else base.CYAN
            ww=max(84,int(base.tw(d,txt,base.font(16,"mono"))+32)); base.chip(d,x-ww//2,y-21,ww,42,txt,c,16)
        if m=="precedence":
            base.center(d,640,217,"MULTIPLIKASI DIBENTUK LEBIH DAHULU",base.font(13,"mono"),base.AMBER)
            if t>5: base.chip(d,1000,438,140,43,"HASIL 14",base.GREEN,14)
    elif m=="subtotal":
        base.panel(d,(110,244,1170,474),base.BLUE); base.chip(d,150,269,236,37,"SUBTOTAL",base.CYAN,15)
        base.center(d,640,330,"Rp 54.000",base.font(39,"mono"),base.WHITE); base.label(d,262,405,"ITEM TERPINDAI",base.MUTED,13)
        base.label(d,830,405,"4 ITEM / HARGA VALID",base.GREEN,13)
        wipe=int(180+min(1,t/2.5)*820); d.rectangle((180,386,min(1000,wipe),393),fill=(*base.CYAN,255))
    elif m=="discount_apply":
        base.panel(d,(110,244,1170,474),base.AMBER); base.chip(d,160,266,230,39,"KUPON DISKON",base.AMBER,14)
        base.rounded(d,(235,328,1050,402),(32,47,68,255),(*base.AMBER,210),11,2)
        for x,txt,c in ((400,"54.000",base.WHITE),(635,"−",base.AMBER),(830,"5.400",base.CORAL)):
            base.center(d,x,343,txt,base.font(25 if txt!="−" else 30,"mono"),c)
        if t>4: base.arrow(d,910,382,910,432,base.GREEN,4)
        if t>5: base.chip(d,760,425,290,35,"DISKON DITERAPKAN",base.GREEN,12)
    elif m=="total_due":
        base.panel(d,(205,246,1075,474),base.GREEN); base.label(d,290,271,"JUMLAH YANG HARUS DIBAYAR",base.GREEN,14)
        base.center(d,640,323,"Rp 48.600",base.font(43,"mono"),base.WHITE)
        if int(t*3)%3==0: base.rounded(d,(310,317,970,385),(*base.GREEN,24),(*base.GREEN,95),10,1)
        base.chip(d,435,421,410,30,"54.000 − 5.400 = 48.600",base.CYAN,14)
    elif m=="semantic_check":
        base.panel(d,(160,244,1120,480),base.GREEN); base.center(d,640,263,"VALIDASI SEBELUM PEMBAYARAN",base.font(15,"mono"),base.WHITE)
        for i,(txt,c) in enumerate((("IDENTITAS ITEM",base.BLUE),("HARGA KATALOG",base.CYAN),("ATURAN DISKON",base.AMBER))):
            y=311+i*51; base.chip(d,250,y,480,37,txt,c,13)
            if t>1+i*2:
                d.ellipse((795,y+4,828,y+37),fill=(*base.GREEN,240)); d.line((802,y+20,811,y+28),fill=(6,32,22,255),width=3); d.line((811,y+28,822,y+11),fill=(6,32,22,255),width=3)
            else: d.ellipse((795,y+4,828,y+37),outline=(*base.MUTED,180),width=2)
    elif m=="evaluate_total":
        base.panel(d,(95,252,1185,470),base.VIOLET)
        for i,(x,txt,c) in enumerate(((205,"54.000",base.BLUE),(500,"−",base.AMBER),(710,"5.400",base.CORAL),(1000,"48.600",base.GREEN))):
            y=339+int(5*math.sin(t*2+i)); base.chip(d,x-87,y-30,174,60,txt,c,18)
            if i in (0,2): base.arrow(d,x+94,y,x+117,y,c,3)
        base.label(d,381,430,"OPERAND → OPERATOR → NILAI",base.MUTED,12)
    elif m=="payment_tap":
        base.panel(d,(115,242,1165,478),base.BLUE); base.rounded(d,(715,280,1050,438),(28,45,63,255),(*base.CYAN,235),14,3)
        base.rounded(d,(772,304,993,365),(4,14,28,255),None,8); base.center(d,882,318,"TEMPELKAN KARTU",base.font(13,"mono"),base.CYAN)
        cx=int(265+min(1,t/5)*405); base.rounded(d,(cx,320,cx+190,426),(*base.VIOLET,240),(*base.WHITE,220),12,2)
        d.rectangle((cx+19,341,cx+65,374),fill=(*base.AMBER,255))
        for i in range(4): d.line((cx+85,345+i*12,cx+165,345+i*12),fill=(255,255,255,150),width=2)
        if t>3:
            for r in (36,60,84): d.arc((884-r,359-r,884+r,359+r),210,330,fill=(*base.CYAN,max(20,190-int(t*9))),width=3)
    elif m=="payment_approved":
        base.panel(d,(210,254,1070,468),base.GREEN); base.rounded(d,(395,274,885,448),(10,33,28,255),(*base.GREEN,245),16,3)
        base.center(d,640,301,"PEMBAYARAN",base.font(16,"mono"),base.MUTED); base.center(d,640,339,"DISETUJUI",base.font(29,"bold"),base.GREEN)
        r=22+int(8*math.sin(t*3)); d.ellipse((608-r,401-r,608+r,401+r),outline=(*base.GREEN,255),width=4)
        d.line((596,401,605,410),fill=(*base.GREEN,255),width=5); d.line((605,410,621,389),fill=(*base.GREEN,255),width=5)
        rng=random.Random(s["id"])
        for i in range(14):
            x=360+rng.randint(0,560); y=285+((i*37+int(t*35))%152)
            d.ellipse((x,y,x+5,y+5),fill=(*(base.CYAN if i%2 else base.AMBER),180))
    elif m=="receipt_print":
        base.panel(d,(200,244,1080,480),base.BLUE); base.rounded(d,(400,256,880,337),(29,43,59,255),(*base.MUTED,220),12,3)
        base.center(d,640,273,"PRINTER KASIR",base.font(15,"mono"),base.WHITE); base.rounded(d,(470,312,810,343),(3,8,17,255),None,4)
        amount=int(min(1,max(0,(t-1)/5))*156); top=351-amount; d.rectangle((465,top,815,471),fill=(*base.PAPER,255))
        if amount>28: d.text((495,top+11),"MINIMARKET",font=base.font(12,"bold"),fill=base.PAPER_INK)
        if amount>51: d.text((495,top+34),"Subtotal      54.000",font=base.font(11,"mono"),fill=base.PAPER_INK)
        if amount>75: d.text((495,top+55),"Diskon         -5.400",font=base.font(11,"mono"),fill=base.PAPER_INK)
        if amount>96: d.text((495,top+77),"TOTAL          48.600",font=base.font(13,"bold"),fill=(10,95,66))
        if amount>120:
            for i in range(28): d.line((495+i*10,top+104,495+i*10,top+(124 if i%4 else 114)),fill=base.PAPER_INK,width=2)
        d.rectangle((465,351,815,max(351,471-amount)),fill=(7,13,24,255))
    elif m=="bag_items":
        base.panel(d,(100,247,1180,479),base.GREEN)
        for i in range(3):
            x=220+i*300; base.rounded(d,(x,340,x+205,463),(*base.BLUE,90),(*base.CYAN,230),10,3)
            d.line((x+35,340,x+63,312,x+143,312,x+170,340),fill=(*base.CYAN,230),width=4)
            if t>i*2:
                q=min(1,max(0,(t-i*2)/3)); iy=int(275+q*55); c=(base.AMBER,base.CORAL,base.VIOLET)[i]
                base.rounded(d,(x+69,iy,x+124,iy+61),(*c,230),None,6,1)
        base.label(d,430,273,"BARANG DITATA, BUKAN DILOMPATKAN",base.MUTED,12)
    elif m=="cashier_thanks":
        base.panel(d,(110,252,1170,475),base.CYAN); person(d,350,463,.95,base.AMBER,t); person(d,885,463,.95,base.GREEN,t+1)
        base.rounded(d,(435,273,788,340),(239,246,249,255),None,14); base.center(d,611,292,"Terima kasih!",base.font(22,"bold"),base.PAPER_INK)
        d.polygon(((500,337),(523,337),(500,356)),fill=(239,246,249,255)); cart(d,520,467,.72,3)
    elif m=="exit_door":
        storefront(d,t,int(min(t,8)*26))
        for k in range(6): d.line((645+k*8,275,645+k*8,457),fill=(*base.CYAN,max(20,120-k*15)),width=2)
    elif m in ("walk_outside","store_recede","end_walk"):
        sc=max(.56,1-.038*t) if m in ("store_recede","end_walk") else 1
        x0=int(640-450*sc); x1=int(640+450*sc)
        base.rounded(d,(x0,230,x1,465),(17,34,53,255),(*base.BLUE,190),10,2)
        base.center(d,640,247,"MINIMARKET",base.font(max(14,int(20*sc)),"bold"),base.WHITE)
        d.line((100,474,1180,474),fill=(87,117,147,220),width=4)
        for i in range(9):
            x=100+i*130-int(t*32)%130; d.line((x,485,x+52,485),fill=(66,96,127,200),width=3)
        xx=int(580+min(t,9)*48); person(d,xx,466,.86,base.AMBER,t); base.rounded(d,(xx+22,371,xx+73,412),(*base.VIOLET,230),None,5,1)
        if t<4:
            for k in range(5): d.line((xx-60-k*10,437-k*4,xx-38-k*10,437-k*4),fill=(*base.CYAN,max(10,130-k*22)),width=2)
    elif m=="concept_recap":
        base.rounded(d,(130,245,1150,492),(8,18,33,225),(*base.BLUE,180),18,2)
        for i,(title,desc,c) in enumerate((("TOKENISASI","unit",base.BLUE),("CFG","aturan",base.CYAN),("PARSE TREE","struktur",base.VIOLET),("AST","operasi",base.AMBER))):
            x=160+i*245
            if t>i*1.4:
                base.panel(d,(x,301,x+214,416),c); base.center(d,x+107,327,title,base.font(14,"mono"),c); base.center(d,x+107,369,desc,base.font(21,"bold"),base.WHITE)
                if t>i*1.4+.35:
                    for k in range(3): d.ellipse((x+75+k*31,392,x+83+k*31,400),fill=(*c,210))
        base.label(d,365,447,"KOMPONEN BERBEDA, SATU TRANSAKSI",base.MUTED,12)
    elif m=="receipt_audit":
        base.panel(d,(265,227,1015,492),base.AMBER); base.rounded(d,(408,243,872,477),(*base.PAPER,255),None,8)
        base.center(d,640,257,"MINIMARKET",base.font(17,"bold"),base.PAPER_INK)
        d.text((445,293),"Subtotal             54.000",font=base.font(16,"mono"),fill=base.PAPER_INK)
        d.text((445,327),"Diskon                -5.400",font=base.font(16,"mono"),fill=base.PAPER_INK)
        d.line((442,363,838,363),fill=(35,51,55,220),width=2)
        base.center(d,640,377,"TOTAL                48.600",base.font(19,"bold"),(12,96,67))
        for i in range(34): d.line((450+i*11,426,450+i*11,448 if i%4 else 438),fill=base.PAPER_INK,width=2)
        if t>3: base.chip(d,474,452,332,30,"SUBTOTAL − DISKON = TOTAL",base.GREEN,11)
    else:
        base.panel(d,(105,245,1175,480),base.BLUE); base.center(d,640,330,s["title"].upper(),base.font(20,"mono"),base.WHITE)
    fx_flash(d,t,s["id"])

SPEECH_DURATION_BY_ID={}

def caption_frame(scene,local,duration):
    display_duration=SPEECH_DURATION_BY_ID.get(scene["id"],duration-.7)
    edited=dict(scene)
    edited["narration"]="" if local>display_duration+.12 else phrase_at(scene["narration"],local,display_duration)
    return legacy_frame(edited,local,duration)

legacy_make_audio=base.make_audio
legacy_frame=base.frame
def align_beats_to_speech(scene_id,speech_duration):
    beats=BEAT_GUIDE[str(scene_id)]
    fractions=(0.14,0.52,0.86)
    limit=DURATIONS[scene_id-1]-.25
    previous=-.1
    for i,beat in enumerate(beats):
        at=min(limit,max(previous+.12,speech_duration*fractions[i]))
        beat["at"]=round(at,3)
        previous=at
    return [b["at"] for b in beats]

def make_audio_v2(ffmpeg,ffprobe,work,out):
    result=legacy_make_audio(ffmpeg,ffprobe,work,out)
    for item in result["scenes"]:
        sid=item["scene_id"]
        raw=float(item.get("source_audio_duration_sec",DURATIONS[sid-1]-.7))
        tempo=max(1.0,float(item.get("tempo_factor",1.0)))
        SPEECH_DURATION_BY_ID[sid]=min(DURATIONS[sid-1]-.1,max(1.0,raw/tempo))
        align_beats_to_speech(sid,SPEECH_DURATION_BY_ID[sid])
    write_srt_v2(Path(out)/"narration-id.srt",result["scenes"])
    sfx,events=create_sfx_track(out)
    mixed=Path(work)/"master-audio-v2.wav"
    base.run([ffmpeg,"-y","-hide_banner","-loglevel","error","-i",str(result["mixed"]),"-i",str(sfx),
      "-filter_complex","[1:a]volume=0.92[sfx];[0:a][sfx]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.93,aresample=48000,apad,atrim=duration=390,asetpts=PTS-STARTPTS[a]",
      "-map","[a]","-ar","48000","-ac","2","-c:a","pcm_s16le",str(mixed)])
    if abs(base.duration(ffprobe,mixed)-TOTAL)>.12: raise RuntimeError("V2 narration/music/SFX duration mismatch.")
    result["mixed"]=mixed; result["sfx_track"]=sfx; result["sfx_events"]=events
    write_cue_sheets(out,events)
    return result
base.visual=visual_v2
base.frame=caption_frame
base.write_srt=lambda path: write_srt_v2(path)
base.render_video.__globals__["frame"]=caption_frame

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ffmpeg",default="ffmpeg"); ap.add_argument("--ffprobe",default="ffprobe")
    ap.add_argument("--output-dir",required=True); ap.add_argument("--work-dir",default="")
    args=ap.parse_args(); out=Path(args.output_dir).resolve(); out.mkdir(parents=True,exist_ok=True)
    work=Path(args.work_dir).resolve() if args.work_dir else out/".work"; work.mkdir(parents=True,exist_ok=True)
    visual_only=work/"visual-v2-only.mp4"; final=out/"Dari_Kasir_Interactive_Cinematic_Motion_Master_v2.mp4"; contact=out/"procedural-contact-sheet-v2.jpg"
    print("V2: 37 scenes; entire store trip; three visual/audio beats per scene; no reference images.",flush=True)
    audio=make_audio_v2(args.ffmpeg,args.ffprobe,work,out)
    if [s["id"] for s in SCENES]!=list(range(1,38)) or len({s["title"] for s in SCENES})!=37: raise RuntimeError("Scene IDs/titles invalid.")
    if TOTAL!=390 or 54000-5400!=48600 or len(BEAT_GUIDE)!=37: raise RuntimeError("Timeline/story contract invalid.")
    print("Render 9,360 1080p frames.",flush=True)
    render=base.render_video(args.ffmpeg,visual_only,contact)
    base.run([args.ffmpeg,"-y","-hide_banner","-loglevel","warning","-i",str(visual_only),"-i",str(audio["mixed"]),
      "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","192k","-ar","48000","-ac","2","-t",str(TOTAL),
      "-movflags","+faststart",str(final)])
    media=base.validate(args.ffmpeg,args.ffprobe,final)
    manifest={"project":"Dari Kasir ke Dalam Pikiran Komputer","version":"procedural-cinematic-motion-master-v2.0.0",
      "created_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
      "concept":"Continuous trip: storefront entry → browsing → weighing → checkout → POS processing → payment → receipt/bagging → exit → sidewalk close.",
      "method":"Procedurally drawn geometry, typography and diagram animation; no reference images or external assets.",
      "reference_images_used":0,"external_visual_assets_used":0,"scene_count":37,"scene_durations_sec":DURATIONS,
      "target_duration_sec":TOTAL,"target_frames":TOTAL*base.FPS,
      "audio":{"voice":base.VOICE,"provider_counts":audio["providers"],"mix":audio["mix"],"voice_qc":audio["voice_qc"],
        "generated_sfx_events":len(audio["sfx_events"]),"sfx_stem":"sound-effects-only.wav",
        "sfx_cue_sheet":"sound-effect-cue-sheet.json","visual_effect_cue_sheet":"visual-effect-cue-sheet.md",
        "human_listening_qc":"PENDING"},
      "render":render,"validation":media,
      "beat_guidance":{"beats_per_scene":3,"cue_clock":"single absolute 390-second timeline"},
      "production_acceptance":"TECHNICAL_PASS_HUMAN_VISUAL_AND_LISTENING_QC_PENDING",
      "scenes":[{"id":s["id"],"title":s["title"],"motif":s["motif"],"narration":s["narration"],"duration_sec":DURATIONS[i],
        "beats":BEAT_GUIDE[str(s["id"])]} for i,s in enumerate(SCENES)]}
    (out/"production-manifest-v2.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    (out/"concept-v2.md").write_text("# Cinematic Motion Master V2\n\n37 short blocks form a complete store visit: exterior, entry, aisle browsing, price comparison, product selection, weighing, checkout, barcode scanning, POS parsing, subtotal/discount/total, semantic checks, payment, receipt printing, bagging, and exit onto the sidewalk.\n\n- Runtime: 390 seconds at 24 fps; 9,360 frames.\n- Three scheduled micro-beats per scene, each with visual action, effect instruction, and synchronized SFX when required.\n- VFX: parallax, camera push/pull, tracking streaks, scan laser, product arc, progressive rule/tree reveal, value wipe, NFC ripple, receipt paper feed, status flash and exit transition.\n- Narration is captioned in short phrase cues. SFX stem, JSON cue map and human-readable VFX guide are exported separately.\n- All graphics and sound effects are generated procedurally; no external visual or audio samples are used.\n- Technical validation is distinct from human review of pace, readability, pronunciation, sync, and mix balance.\n",encoding="utf-8")
    print(json.dumps({"status":"TECHNICAL_PASS","output":str(final),"duration_sec":media["duration_sec"],"video":media["video"],
      "audio":media["audio"],"sfx_events":len(audio["sfx_events"]),"reference_images_used":0,"size_bytes":media["size_bytes"],
      "acceptance":manifest["production_acceptance"]},ensure_ascii=False,indent=2),flush=True)
    return 0

if __name__=="__main__": raise SystemExit(main())
