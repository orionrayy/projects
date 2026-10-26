# DR2C VORENYX — Whole-Project Deep Static Audit v2.67

**Tanggal:** 26 Oktober 2026  
**Status:** audit statis lintas paket selesai; belum ada APK baru. Runtime Android dan akar masalah instalasi/Start belum terverifikasi.

## Ringkasan keputusan

Audit membandingkan APK dasar dengan kandidat v2.57 ber-hash SHA-256 **a1f566d35b9b3cd7c5513cc72f19c5aca9e5fed881394df4c3ef66eb05a474a7**, menelusuri source Deathforth beserta patch yang tersedia, membandingkan native library, dan memvalidasi aset.

## Temuan prioritas

1. **Label splash tertinggal — terkonfirmasi, prioritas sedang.** Gambar splash masih memuat label **V2.43**, sedangkan kandidat bernama v2.57 dan checkpoint audit saat ini v2.67. File valid dan berukuran 2560×1600, tetapi identitas visual tidak sinkron.
2. **Artwork judul tambahan kemungkinan tidak digunakan — belum pasti, prioritas sedang.** Aset vorenyx_title_screen.png (1672×941, sekitar 2.23 MB) juga berlabel V2.43. Pencarian referensi literal di skrip, DEX, resource table dan string native tidak menemukan pemanggilnya; loader dinamis masih mungkin.
3. **Terminologi atribut tidak konsisten — terkonfirmasi sebagai inkonsistensi label.** Kedua libmain.so ABI memuat penggantian string statis seperti fitness → bugar, sementara helper id-name-localize pada boot.df memberi fitness → fisik. Ini mungkin menghasilkan label berbeda pada permukaan UI yang berbeda. Jangan ganti identifier mesin secara massal.
4. **Start tidak menunjukkan penghapusan handler yang jelas pada source statis.** Jumlah deklarasi cyoa: 823, cyoa-choice: 928, cyoa-blank: 100 dan cyoa-bridge: 190 cocok dengan paket dasar. Alur token kontrol inti terjaga dalam pemeriksaan heuristik; helper pelokalan ditambahkan pada enam skrip. Ini bukan bukti bahwa tombol merespons saat runtime.
5. **Satu include wajib yang tidak ditemukan, kemungkinan lama/dormant.** paul/camping-region.df menunjuk ke paul/camping-tent-events.df yang tidak ada dalam kedua paket. Tidak ditemukan referensi ke region file tersebut dari jalur boot utama; belum terbukti menyebabkan startup/gameplay saat ini.
6. **Aset lulus pemeriksaan decode statis.** 167 PNG dapat dibuka dengan Pillow dan 21 MP3 dapat diperiksa oleh ffprobe; tidak ditemukan aset PNG/MP3 rusak pada kumpulan kandidat yang diperiksa.

## Integritas source dan paket

- APK kandidat: 1.015 entri ZIP, CRC pass, nol path duplikat; base APK: 1.014 entri, CRC pass.
- Candidate memuat 509 skrip Deathforth, sama dengan base. Rekonstruksi source ZIP + patch v2.43, v2.45 corrective, v2.45 Startfix dan v2.61 menghasilkan kecocokan persis **509/509** skrip, tanpa file hilang, ekstra, atau berbeda dari kandidat.
- Sebanyak 269 skrip berubah dari base; 240 tetap identik.
- Deklarasi CYOA utama memiliki hitungan yang sama dengan base. Pemeriksaan lexical/control-token merupakan pemeriksaan heuristik, bukan parser Deathforth lengkap.
- Dua libmain.so masing-masing berbeda 89 byte dari base dalam rentang data ELF .rodata; tidak terdeteksi perubahan byte kode mesin pada rentang yang dibandingkan. Ini tidak membuktikan native code secara semantik bebas bug, hanya bahwa perubahan yang teramati berupa penggantian data/string.
- Semua temuan statis merujuk ke hash APK kandidat di atas, bukan APK yang belum diidentifikasi pada perangkat pengguna.

## Gap verifikasi penting

- Android SDK apksigner resmi tidak tersedia saat audit; pemeriksaan v1/v2 independen tidak menggantikan verifikasi resmi.
- Tidak ada trace PackageManager dari kegagalan instalasi, logcat saat tombol Start ditekan, atau rekaman perangkat baru.
- Paket memakai package ID com.noodlecake.drtc dan sertifikat lokal, bukan sertifikat penerbit asli. Ini dapat memengaruhi upgrade di atas instalasi yang ditandatangani penerbit atau pemeriksaan integritas runtime, tetapi **tidak cukup untuk menjelaskan sendiri kegagalan fresh install** setelah aplikasi dihapus.
- Tidak ada klaim bahwa kandidat sudah stabil. Tidak dibuat APK baru dalam checkpoint ini.

## Langkah perbaikan yang disarankan

1. Ambil log kegagalan PackageManager untuk hash APK yang tepat. Jika gagal install, hentikan dulu perubahan source.
2. Jika bisa dipasang, ambil trace logcat saat menekan Start sekali. Klasifikasikan apakah tap tidak diterima, event tidak didispatch, runtime Forth gagal, atau aplikasi berhenti/crash.
3. Setelah jalur install/runtime terbukti, perbaiki sinkronisasi badge splash/title dan satu peta istilah atribut dalam patch terpisah.
4. Uji menu, Start/tutorial, beberapa event, trade, combat, save/load, orientasi, serta UI overflow sebelum memberi label stabil.

## Artefak lokal

- Laporan JSON lengkap: DR2C_VORENYX_WHOLE_PROJECT_AUDIT_v2.67.json
- Skrip audit ulang: DR2C_VORENYX_WHOLE_PROJECT_AUDIT_v2.67.py
- Toolkit: DR2C_VORENYX_WHOLE_PROJECT_AUDIT_v2.67_TOOLKIT.zip

**Kesimpulan:** audit statis mengidentifikasi bug konsistensi visual dan label serta satu referensi include lama yang patut ditelusuri. Namun tidak ada bukti statis yang cukup untuk menetapkan akar masalah gagal instalasi atau tombol Start. Gerbang berikutnya adalah log dari perangkat, bukan APK rebuild spekulatif.
