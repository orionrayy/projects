# Cinematic Motion Master V2 — Dari Kasir ke Dalam Pikiran Komputer

## Revisi kreatif
V1 terlalu statis: 27 adegan berisi panel diagram yang ditahan 14–15 detik, caption satu blok, dan ambient tanpa SFX yang terhubung dengan tindakan. V2 menjaga satu narasi berkelanjutan: melihat toko dari luar, masuk lewat pintu otomatis, mengambil keranjang, menyusuri rak, membandingkan dan memilih produk, menimbang buah, menuju antrean, memindai barang, memahami pemrosesan POS, membayar, mengambil struk, mengemas barang, lalu benar-benar keluar ke trotoar.

## Ritme dan animasi
37 scene blocks, 390 detik pada 24 fps; 20 adegan berdurasi 11 detik dan 17 adegan 10 detik. Setiap adegan mempunyai tiga micro-beat terjadwal. Visual berubah melalui parallax rak, push-in/pullback kamera, tracking, motion trails, scan laser, product arcs, progressive CFG/tree reveal, value wipe, ripple NFC, paper-feed mekanis, status flash, dan transisi keluar toko.

## Narasi dan audio
Caption dibagi menjadi cue pendek sesuai estimasi durasi ucapan per scene, bukan menahan seluruh narasi pada layar. Sound effect disintesis secara prosedural dari waveform, tanpa sample luar: bunyi pintu, langkah, roda keranjang, barang mendarat, timbangan, printer label, barcode scan, POS ticks, token/node reveals, konfirmasi diskon/total, NFC, status approved, printer struk, rustle tas dan closing chime.

Semua cue memakai timeline absolut yang sama. Setiap cue mencantumkan aksi visual, nama efek, timestamp, jenis SFX dan gain dalam sound-effect-cue-sheet.json serta visual-effect-cue-sheet.md. Sound-effects-only.wav disertakan sebagai stem tersendiri.

## Urutan 37 adegan
- 01 Minimarket di depan kita — Mulai di luar, masuk ke dalam
- 02 Pintu otomatis terbuka — Pintu dan cahaya menandai transisi
- 03 Ambil keranjang — Orientasi ruang belanja
- 04 Menyusuri lorong — Parallax memperjelas kedalaman
- 05 Temukan produk — Sorot pilihan pada rak
- 06 Bandingkan label — Harga dan ukuran dibandingkan
- 07 Masukkan pilihan ke keranjang — Gerak barang terasa berbobot
- 08 Pilih buah — Buah dipilih satu per satu
- 09 Timbang buah — Berat stabil sebelum label dicetak
- 10 Tempel label harga — Label mengikuti jalur cetak
- 11 Menuju kasir — Perpindahan lokasi yang dinamis
- 12 Antrean kasir — Fokus berpindah ke kasir
- 13 Barang ke konveyor — Setiap produk punya ruang
- 14 Bip pemindai — SFX dan sinar serentak
- 15 Layar POS terisi — Setiap bip menambah satu baris
- 16 Tokenisasi transaksi — Karakter berubah menjadi unit
- 17 Aliran token — Urutan token tetap terbaca
- 18 Aturan CFG — Node aturan mengikuti narasi
- 19 Parse tree terbentuk — Akar, cabang, lalu daun
- 20 Prioritas operator — Prioritas jadi visual
- 21 Subtotal Rp54.000 — Wipe ke nilai yang benar
- 22 Diskon Rp5.400 — Diskon sebagai operasi
- 23 Total Rp48.600 — Total muncul setelah hitung
- 24 Validasi transaksi — Pemeriksaan satu per satu
- 25 AST pengurangan — Operasi diringkas menjadi struktur
- 26 Evaluasi total — Operand mengalir ke hasil
- 27 Ketuk kartu — Gelombang pada titik sentuh
- 28 Pembayaran disetujui — Status dan chime selaras
- 29 Struk tercetak — Kertas mengikuti suara printer
- 30 Kemas belanjaan — Barang masuk tas secara berurutan
- 31 Terima kasih — Interaksi manusia singkat
- 32 Keluar melalui pintu — Pintu terbuka ke dunia luar
- 33 Kembali ke trotoar — Langkah melewati ambang
- 34 Empat konsep inti — Ringkas istilah saat perjalanan berakhir
- 35 Struk untuk audit — Angka pada struk konsisten
- 36 Perjalanan selesai — Wide shot menutup kisah
- 37 Perjalanan berakhir — Transaksi dapat diaudit

## Acceptance criteria
1. Jalur cerita complete dari exterior entry sampai pembeli keluar ke trotoar.
2. 37 scene IDs unik, durasi tepat 390 detik, 9.360 frame.
3. 3 beat per scene dengan petunjuk VFX dan timestamp SFX di jam yang sama.
4. H.264 1920×1080/24 fps, AAC stereo 48 kHz, stream video/audio tepat 390 detik.
5. Paket hasil mencakup MP4, SRT phrase cues, transkrip, SFX WAV stem, JSON cue sheet, VFX guide, contact sheet dan manifest.
6. Technical pass terpisah dari artistic pass; review manusia tetap perlu menilai sinkronisasi, keterbacaan, pacing, suara, dan komposisi.
