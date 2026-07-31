# Pardus Sistem Servisleri Yöneticisi

**Pardus üzerinde systemd servislerini ve otomatik başlatma (autostart) uygulamalarını yönetmek için geliştirilmiş sade bir GUI uygulaması.**

[🇬🇧 Click for English README](README.md)

![License](https://img.shields.io/badge/lisans-GPL--3.0-blue.svg)
![Python](https://img.shields.io/badge/python-3-blue.svg)
![Qt](https://img.shields.io/badge/PySide6-Qt%20for%20Python-41cd52.svg)
![Platform](https://img.shields.io/badge/platform-Pardus%20%2F%20Debian%20t%C3%BCrevleri-orange.svg)

---

## Hakkında

**Pardus Sistem Servisleri Yöneticisi**, **PySide6 (Qt for Python)** ile geliştirilmiş, terminale hiç dokunmadan `systemd` servislerini görüntülemenizi ve yönetmenizi, ayrıca oturum açılışında otomatik başlayan uygulamaları düzenlemenizi sağlayan basit bir masaüstü aracıdır.

Servis yönetimini (etkinleştirme, devre dışı bırakma, başlatma, durdurma, log görüntüleme) ve autostart yapılandırmasını, grafik arayüz tercih eden Pardus kullanıcıları için daha erişilebilir hale getirmek amacıyla oluşturulmuştur.

## Özellikler

### 🧩 systemd Servis Yönetimi
- Tüm systemd birimlerini (unit) aranabilir ve sıralanabilir bir tabloda listeleme (isim, yükleme durumu, aktiflik durumu, preset)
- Anlık durum göstergeleri — aktif (yeşil), pasif (sarı), başarısız/failed (kırmızı)
- Servis adına göre anında arama/filtreleme
- Seçilen servis için ayrıntılı bilgi görüntüleme (açıklama, yükleme durumu, aktiflik durumu)
- Servisleri **etkinleştirme / devre dışı bırakma**
- Servisleri **başlatma / yeniden başlatma / durdurma**
- Seçilen servisin loglarını varsayılan log/metin görüntüleyicinizde açma
- İlgili unit dosyasını manuel düzenleme için açma (unit dosyalarını doğrudan düzenlemenin sistem kararlılığını etkileyebileceğine dair bir onay/uyarı penceresiyle birlikte)
- Arka planda çalışan işçi thread'ler sayesinde, arayüzü kilitlemeden servis listesinin otomatik yenilenmesi (her 5 saniyede bir)

### 🚀 Otomatik Başlatma (Autostart) Uygulama Yönetimi
- Şu anda otomatik başlayacak şekilde ayarlanmış tüm uygulamaları listeleme (`~/.config/autostart`)
- Sistemde kurulu tüm uygulamaları tarama (`/usr/share/applications`, `/usr/local/share/applications` ve `~/.local/share/applications` dizinlerinden) ve autostart listesine ekleme
- Uygulama detaylarını görüntüleme (isim, açıklama, simge, `.desktop` dosya yolu)
- `.desktop` giriş dosyasını doğrudan düzenleme
- Bir uygulamayı autostart listesinden kaldırma

### ⚙️ Teknik Detaylar
- Kilitlenmeyen arayüz: Ağır işlemler (servis listeleme, açıklama çekme) ayrı `QThread`'lerde çalışır
- Verimli filtreleme ve sıralama için Qt Model/View mimarisi (`QStandardItemModel` + `QSortFilterProxyModel`) kullanımı
- Qt Linguist çeviri dosyaları (`.ts` / `.qm`) üzerinden çoklu dil desteği
- Debian tabanlı sistemler için yerel bir `.deb` paketi olarak paketlenip dağıtılabilir

## Gereksinimler

- Python 3
- `dpkg` (`.deb` paketi oluşturmak için)
- systemd tabanlı bir Linux dağıtımı (**Pardus** için geliştirilmiş ve test edilmiştir)

Python bağımlılıkları (build sürecinde bir sanal ortama otomatik olarak kurulur):

```
altgraph
packaging
pyinstaller
pyinstaller-hooks-contrib
PySide6
PySide6_Addons
PySide6_Essentials
pyxdg
setuptools
shiboken6
```

Ayrıntılar için [`requirements.txt`](requirements.txt) (tam, sabit sürümlü) ve [`requirements-lite.txt`](requirements-lite.txt) (build sistemi tarafından kullanılır) dosyalarına bakabilirsiniz.

## Kurulum

### Yöntem 1 — `.deb` paketi oluşturup kurma (önerilen)

```bash
git clone https://github.com/V6lhost/pardus-system-services-manager.git
cd pardus-system-services-manager
make build
sudo dpkg -i output_deb/pardus-system-services-manager-*.deb
```

Bu komut şunları yapar:
1. İzole bir Python sanal ortamı oluşturur ve bağımlılıkları kurar
2. Çeviri dosyalarını derler
3. Uygulamayı PyInstaller ile paketler
4. Her şeyi `output_deb/` altında bir `.deb` dosyası haline getirir

### Yöntem 2 — Kaynak koddan doğrudan çalıştırma (geliştirme için)

```bash
git clone https://github.com/V6lhost/pardus-system-services-manager.git
cd pardus-system-services-manager
make run
```

Bu komut (yoksa) bir sanal ortam oluşturur, çevirileri derler ve uygulamayı doğrudan Python ile başlatır — herhangi bir paketleme adımı gerekmez.

### Build dosyalarını temizleme

```bash
make clean
```

Sanal ortamı, build/dist klasörlerini, derlenmiş çevirileri ve oluşturulan `.deb` çıktısını siler.

## Kullanım

Kurulumdan sonra **Pardus Sistem Servisleri Yöneticisi**'ni uygulama menünüzden başlatabilir veya doğrudan terminalden çalıştırabilirsiniz.

- **Servisler** sekmesinden systemd servislerini arayabilir, inceleyebilir ve kontrol edebilirsiniz.
- **Otomatik Başlatma Uygulamaları** sekmesinden oturum açılışında hangi uygulamaların otomatik başlayacağını yönetebilirsiniz.
- Listeden herhangi bir öğeyi seçtiğinizde, ilgili işlemlerin bulunduğu detay paneli açılır.

## Proje Yapısı

```
pardus-system-services-manager/
├── debian/          # Debian paketleme metadata'sı ve dosya düzeni
├── src/             # Uygulama kaynak kodu (main.py, helper_functions.py, ...)
├── translations/    # Qt Linguist çeviri kaynak (.ts) ve derlenmiş (.qm) dosyaları
├── ui/               # Qt Designer .ui dosyaları (MainWindow, dialoglar)
├── Makefile          # Build, çalıştırma ve paketleme otomasyonu
├── requirements.txt
├── requirements-lite.txt
└── LICENSE
```

## Katkıda Bulunma

Katkılar, hata bildirimleri ve özellik önerileri her zaman memnuniyetle karşılanır!

1. Depoyu fork'layın
2. Bir özellik dalı oluşturun (`git checkout -b feature/ozelligim`)
3. Değişikliklerinizi commit'leyin
4. Ne değiştirdiğinizi ve nedenini açıklayan bir pull request açın

Uygulamayı başka bir dile çevirmek isterseniz, `translations/` dizinindeki `.ts` dosyalarına göz atabilir ve Qt Linguist (veya `pyside6-linguist` aracını) kullanarak kendi dilinizi ekleyebilirsiniz.

## Lisans

Bu proje **GNU General Public License v3.0** lisansı ile lisanslanmıştır. Tam metin için [`LICENSE`](LICENSE) dosyasına bakınız.

## Sorumluluk Reddi

Bu araç **resmi olmayan, topluluk tarafından geliştirilmiş** bir projedir. TÜBİTAK veya resmi Pardus projesi tarafından geliştirilmemekte, sürdürülmemekte veya onaylanmamaktadır. Özellikle sistem açısından kritik servisleri düzenlerken veya durdururken kendi sorumluluğunuzda kullanınız.

## Teşekkürler
- [Furkan Çolak](https://github.com/furkanclk3180) - Testler
- [topraklanbudev](https://github.com/Topraklanbudev) - Testler ve motivasyon
- [ilgilenmek](https://github.com/keenon63) - Motivasyon
