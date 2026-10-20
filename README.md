# 🔬 Laboratuvar Malzemeleri ve Ölçüm Cihazları

**Ön lisans "Laboratuvar Malzemeleri ve Ölçüm Cihazları" dersi için etkileşimli, Türkçe öğretim uygulaması**

© 2026 Emine Dilşat Yeğenoğlu & Tevfik Hasan Can. Tüm hakları saklıdır.

---

## Nedir?

Gıda, toprak, yaprak ve su laboratuvarlarında güvenli çalışmayı, doğru malzeme seçimini ve
güvenilir ölçümü şemalar, etkileşimli hesaplayıcılar ve bol alıştırmayla anlatan bir web
uygulamasıdır. Bilgisayardan ve telefondan tarayıcıyla açılır. Bütün şemalar bu uygulama için
özgün olarak çizilmiştir.

## İçerik

| Bölüm | Konu ve etkileşimli öğeler |
|---|---|
| 1 · Laboratuvar güvenliği | Laboratuvar planında güvenlik olanakları (seçince vurgulanır), çalışma kuralları, asit seyreltme şeması, "kural mı hata mı" mini oyunu |
| 2 · Güvenlik ve tehlike işaretleri | Şekil–renk–anlam tablosu; uyarı, zorunluluk, yasak, acil durum ve yangın işaretleri (ISO 7010 benzeri çizimler); GHS kimyasal işaretleri; etkileşimli NFPA 704 elması |
| 3 · Kimyasallar ve kazalar | Tehlikeli kimyasallar tablosu, kaza senaryolarına güncel ilk müdahale adımları |
| 4 · Metrik sistem ve birimler | Temel birimler, ön ek tablosu (kilo…piko), etkileşimli birim çevirme merdiveni, hacim eşitlikleri, kelvin, bilimsel gösterim; %, ppm, ppb; ppm hesaplayıcı, C₁V₁ = C₂V₂ seyreltme ve % (w/v) çözelti hesaplayıcı |
| 5 · Cam, plastik ve diğer malzemeler | 33 malzemenin çizimi üç grupta (cam; plastik ve lastik; porselen, metal ve diğer), cam–plastik karşılaştırması, plastik türleri, temizlik |
| 6 · Hacim okuma ve kullanım | Menisküs türleri ve okuma kartı, paralaks hatası (mezür ve bürette ters etki), ölçek okuma adımları, rastgele mezür/büret okuma alıştırması, büret–pipet–balon joje–mikropipet doğru kullanım adımları, mikropipet durak şeması, Ex/In (TD/TC) ve etiket kodları, malzemelerin hata payları |
| 7 · Ölçümün temelleri | Doğruluk–kesinlik hedefleri, sistematik/rastgele hata deneyi, hata türleri, birimler, iletkenlik birim çevirici, kalibrasyon ve izlenebilirlik |
| 8 · Terazi ve nem | Terazi türleri, adım adım analitik tartım (dara, sıcak numune hatası), kurut–soğut–tart döngüsü, nem / kuru madde / kül hesaplayıcı |
| 9 · pH, EC ve su cihazları | pH metre kalibrasyon simülatörü, elektrot bakımı, EC sıcaklık düzeltme hesaplayıcı, DO metre, türbidimetre |
| 10 · Optik cihazlar | Refraktometre görüş alanı (Brix), spektrofotometre şeması ve Beer–Lambert, kalibrasyon eğrisi laboratuvarı |
| 11 · İleri analiz cihazları | AAS ve ICP-OES, Kjeldahl aşamaları ve protein hesaplayıcı, kül fırını, Soxhlet, kromatografi |
| 12 · Laboratuvar türleri | Toprak, yaprak (adımlar, SPAD), gıda (su aktivitesi, L*a*b* renk, viskozimetre), özet tablo |
| 13 · Örnek alma | Numune alma akışı, parti ve çift örnek, karıştırma süresi rehberi, etiket hazırlama, taşıma ve koruyucu |
| 14 · Kalite ve terimler | Kayıt, ISO/IEC 17025, TÜRKAK; hafıza kartları ve aranabilir sözlük |
| 15 · Genel tekrar | Tüm konulardan karışık sorular |

Her bölümün sonunda **10, 20 ya da 30 soruluk seçmeli alıştırma** vardır (öğrenci seçer). Yanıt
seçilince kilitlenir, doğru/yanlış ve adım adım çözüm o zaman açılır. "Yeni sorular" düğmesiyle
sınırsız soru üretilir.

## Kurulum ve çalıştırma

```bash
pip install -r requirements.txt
streamlit run lab_streamlit.py
```

Linux / WSL'de kısaca: `bash baslat.sh`. Ardından tarayıcıda http://localhost:8501

## Yayına alma

GitHub reposuna `lab_streamlit.py` ve `requirements.txt` yüklenir; share.streamlit.io'da
"Create app" ile ana dosya olarak `lab_streamlit.py` seçilir.

## Bilinen sınırlamalar

- Şemalar öğretim amaçlı ve ölçeksizdir; GHS, ISO 7010 ve NFPA işaretleri sadeleştirilerek yeniden çizilmiştir.
- Kalibrasyon, tartım ve kromatografi örneklerindeki sayılar kurgusaldır.
- İlk yardım bilgileri genel eğitim amaçlıdır; kurumun acil durum planı ve Güvenlik Bilgi
  Formları esas alınmalıdır.
- Öğrenci yanıtları kaydedilmez; uygulama öğrenmek için tasarlanmıştır.

## Telif ve kullanım

© 2026 Emine Dilşat Yeğenoğlu & Tevfik Hasan Can. Tüm hakları saklıdır. Ayrıntılar için
`LICENSE` dosyasına bakın.

İletişim ve izin talepleri: dilsat.yegenoglu@cbu.edu.tr
