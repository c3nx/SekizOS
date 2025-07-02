# SekizOS - Windows Agent Tool

Windows üzerinde Claude Code'un tam kontrolünü sağlayan agent sistemi.

## 🚀 Özellikler

- 📸 Ekran görüntüsü alma
- 🖱️ Mouse kontrolü (hareket, tıklama)
- ⌨️ Klavye kontrolü (metin yazma, tuş kombinasyonları)
- 💻 PowerShell komut çalıştırma
- 📊 Process yönetimi
- 📁 Dosya işlemleri
- 🔄 WSL-Windows entegrasyonu

## 📦 Kurulum

### Windows'da:
1. `windows-agent-tool` klasörünü Windows'a kopyala
2. `install.bat` dosyasını **yönetici olarak** çalıştır
3. Agent otomatik başlayacak

### WSL'de:
```bash
# Tool'u kur
cp windows-agent-tool/win ~/.local/bin/
chmod +x ~/.local/bin/win

# Alias'ları ekle
cat windows-agent-tool/windows_aliases.sh >> ~/.windows_aliases
echo "source ~/.windows_aliases" >> ~/.bashrc
source ~/.bashrc
```

## 🎯 Kullanım

### Komut Satırı:
```bash
# Screenshot
win screenshot
win screenshot desktop.png

# Mouse kontrolü
win click 500 300
win move 100 200

# Klavye
win type "Hello World"
win key enter
win key ctrl+c

# PowerShell
win ps "Get-Date"
win ps "dir C:\\"

# Process yönetimi
win processes
win kill 1234
```

### Python'da:
```python
from windows_control import WindowsControl

win = WindowsControl()
win.screenshot("screen.png")
win.click(500, 300)
win.type("Test")
win.powershell("notepad")
```

## 🔧 Claude Code Entegrasyonu

Projenizde `CLAUDE.md` oluşturun:
```markdown
## Windows Agent Tool
- `win screenshot` - Ekran görüntüsü al
- `win click <x> <y>` - Tıkla
- `win type "text"` - Yaz
- `win ps "command"` - PowerShell
```

## 📁 Dosya Yapısı

```
windows-agent-tool/
├── windows_agent.py      # Ana agent (Flask server)
├── windows_control.py    # Python kontrol kütüphanesi
├── win                   # CLI komutu
├── install.bat          # Windows kurulum
├── uninstall.bat        # Kaldırma
├── requirements.txt     # Python bağımlılıkları
└── README.md           # Detaylı dokümantasyon
```

## 🛡️ Güvenlik

- Sadece localhost ve WSL subnet'lerinden erişim
- Bearer token authentication
- Port: 8765

## 📝 Lisans

MIT License

---
Created for Claude Code integration 🤖