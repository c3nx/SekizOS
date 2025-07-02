# Windows Agent for Claude Code v2.0

Windows üzerinde Claude Code'un tam kontrolü için geliştirilmiş bir agent sistemi.

## 🚀 Hızlı Kurulum

### **Windows'da:**

1. **Yönetici olarak** `install.bat` dosyasını çalıştırın
   - Sağ tık → "Yönetici olarak çalıştır"
   - Tüm adımlar otomatik tamamlanacak

2. Kurulum tamamlandığında agent otomatik başlayacak

## 📋 Özellikler

- 📸 **Ekran Görüntüsü**: Tam ekran veya belirli alan
- 🖱️ **Mouse Kontrolü**: Hareket, tıklama, sürükleme
- ⌨️ **Klavye Kontrolü**: Metin yazma, kısayollar
- 💻 **PowerShell**: Windows komutları çalıştırma
- 📊 **Process Yönetimi**: İşlemleri listeleme/sonlandırma
- 📁 **Dosya İşlemleri**: Okuma, yazma, silme
- 🔄 **Otomatik Başlangıç**: Windows açılışında otomatik başlar

## 🔧 Kullanım

### **WSL/Claude Code'da:**

```python
import requests
import json

# Agent bilgilerini oku
with open('/mnt/c/Users/Uptake/.claude_agent_info') as f:
    info = json.load(f)

# Bağlan
url = f"http://{info['host']}:{info['port']}"
headers = {'Authorization': f"Bearer {info['token']}"}

# Ekran görüntüsü al
response = requests.post(f"{url}/screenshot", headers=headers)
screenshot = response.json()['image']  # Base64 encoded
```

## 📡 API Endpoints

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/health` | GET | Sağlık kontrolü |
| `/screenshot` | POST | Ekran görüntüsü |
| `/mouse/move` | POST | Mouse hareket |
| `/mouse/click` | POST | Mouse tıklama |
| `/keyboard/type` | POST | Metin yazma |
| `/keyboard/key` | POST | Tuş basma |
| `/powershell` | POST | PowerShell komutu |
| `/process/list` | GET | İşlem listesi |
| `/process/kill` | POST | İşlem sonlandır |
| `/file/read` | POST | Dosya oku |
| `/file/write` | POST | Dosya yaz |
| `/file/delete` | POST | Dosya sil |

## 🛡️ Güvenlik

- Sadece localhost ve WSL subnet'lerinden erişim
- Bearer token authentication
- Firewall kuralları otomatik yapılandırılır

## 🧪 Test

Agent'ı test etmek için:
- `start_agent_visible.bat` çalıştırın (konsol görünür)
- Veya PowerShell'de: `python windows_agent.py`

## ❌ Kaldırma

1. **Yönetici olarak** `uninstall.bat` çalıştırın
2. Python paketlerini kaldırmak isterseniz 'Y' seçin
3. Klasörü silebilirsiniz

## 🔍 Sorun Giderme

**Agent başlamıyor:**
- Python 3.8+ yüklü mü? (`python --version`)
- PATH'e Python ekli mi?
- Yönetici olarak kurulum yaptınız mı?

**WSL bağlanamıyor:**
- Windows Firewall'da 8765 portu açık mı?
- Agent çalışıyor mu? (Task Manager → python.exe)
- `.claude_agent_info` dosyası var mı?

**PowerShell hataları:**
- Execution Policy: `Get-ExecutionPolicy`
- RemoteSigned olmalı

## 📊 Teknik Detaylar

- **Port**: 8765
- **Host**: 0.0.0.0 (tüm interface'ler)
- **Token**: claude-agent-2024
- **Python**: 3.8+
- **Dependencies**: Flask, pyautogui, Pillow, psutil, pywin32

## 💡 İpuçları

1. Agent Windows başlangıcında otomatik başlar
2. WSL IP'si değişirse `.claude_agent_info` dosyası güncellenir
3. Yüksek DPI ekranlarda pyautogui koordinatları farklı olabilir

## 📝 Lisans

Claude Code için özel olarak geliştirilmiştir.

---
Version: 2.0 | Port: 8765 | Token: claude-agent-2024