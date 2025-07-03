# Windows Agent Versiyon Sistemi

Windows Agent artık versiyon kontrolü ve otomatik güncelleme özelliklerine sahip!

## Özellikler

### 1. Versiyon Kontrolü
- Agent'ın hangi versiyonda olduğunu gösterir
- Her versiyonun özelliklerini listeler
- Son güncelleme zamanını gösterir

### 2. Otomatik Güncelleme
- GitHub'dan yeni versiyonları kontrol eder
- Güncellemeyi indirir ve yedek alır
- Agent'ı yeniden başlatarak günceller

## Kullanım

### Windows Tarafında
1. **Yeni Agent'ı Başlatın:**
   ```powershell
   cd C:\Users\Uptake\WindowsAgent
   python windows_agent.py
   ```
   
   Artık şunu göreceksiniz:
   ```
   ==================================================
   Windows Agent for Claude Code v3.0
   ==================================================
   Starting on 0.0.0.0:8765
   API Token: claude-agent-2024
   Features: Added window management (focus, maximize, minimize, restore)
   Listening on ALL interfaces for WSL access
   ==================================================
   ```

### WSL Tarafında

#### Versiyon Kontrolü
```bash
# Mevcut versiyon
win version

# Detaylı versiyon bilgisi
curl -H "Authorization: Bearer claude-agent-2024" http://192.168.0.15:8765/version | jq
```

#### Güncelleme Kontrolü
```bash
# Güncelleme var mı kontrol et
win update check

# Güncelleme durumu
win update status
```

#### Güncelleme Yapma
```bash
# 1. Güncellemeyi indir
win update download

# 2. Güncellemeyi uygula (agent yeniden başlar)
win update apply
```

## Yeni Özellikler

### Version 2.0
- Temel Windows kontrolü (mouse, keyboard, screenshot)
- PowerShell komutları
- Process yönetimi

### Version 3.0
- **Window Management** eklendi:
  - `win windows` - Tüm pencereleri listele
  - `win focus "Steam"` - Pencereyi öne getir
  - `win maximize "Steam"` - Pencereyi büyüt
  - `win minimize "Steam"` - Pencereyi küçült
  - `win restore "Steam"` - Normal boyuta getir
  - `win window "Steam"` - Öne getir + büyüt

### Version 3.1 (Planlanan)
- Otomatik güncelleme sistemi
- GitHub entegrasyonu
- Changelog otomatik gösterimi

## Teknik Detaylar

### Versiyon Bilgisi
```python
__version__ = "3.0"
__features__ = {
    "2.0": "Basic Windows control (mouse, keyboard, screenshot, powershell)",
    "3.0": "Added window management (focus, maximize, minimize, restore)"
}
```

### Güncelleme Akışı
1. `/update/check` - GitHub'dan son versiyonu kontrol eder
2. `/update/download` - Yeni versiyonu temp dizinine indirir
3. `/update/apply` - Mevcut dosyayı yedekler, yenisini koyar, restart eder

### API Endpoints
- `GET /version` - Detaylı versiyon bilgisi
- `GET /health` - Sağlık kontrolü (versiyon dahil)
- `GET /update/check` - Güncelleme kontrolü
- `POST /update/download` - Güncelleme indir
- `POST /update/apply` - Güncellemeyi uygula
- `GET /update/status` - Güncelleme durumu

## Sorun Giderme

### "404 Not Found" Hatası
Eski versiyon çalışıyor demektir. Windows Agent'ı yeniden başlatın.

### Versiyon Numarasını Göremiyorum
```bash
# Health endpoint'ini kontrol edin
curl -H "Authorization: Bearer claude-agent-2024" http://192.168.0.15:8765/health | jq
```

### Güncelleme Başarısız
1. Yedek dosyayı kontrol edin: `windows_agent.py.bak`
2. Temp dosyasını kontrol edin: `%TEMP%\windows_agent_update.py`
3. Manuel olarak güncelleyin ve yeniden başlatın