# Windows Agent Tool - Claude Code Integration

Windows Agent'ı farklı projelerde Claude Code'a tanıtmak için:

## 1. Proje CLAUDE.md Dosyası

Her projede `.claude/CLAUDE.md` veya kök dizinde `CLAUDE.md` oluştur:

```markdown
## Windows Agent Available

This project has access to Windows control via the Windows Agent tool.

Commands:
- `win screenshot` - Capture Windows screen
- `win click 500 300` - Click at coordinates
- `win type "Hello"` - Type text
- `win ps "dir"` - Run PowerShell

Python:
```python
from windows_control import WindowsControl
win = WindowsControl()
```
```

## 2. Global Kurulum (Tüm Projeler)

`~/.claude/CLAUDE.md` dosyası zaten güncellendi ve tüm projelerde geçerli.

## 3. Proje .gitignore

Windows Agent kullanılan projelerde `.gitignore` içine ekle:
```
.claude_agent_info
*.screenshot.png
```

## 4. VS Code Settings

`.vscode/settings.json`:
```json
{
  "claude.customTools": {
    "windowsAgent": {
      "command": "win",
      "description": "Control Windows from WSL"
    }
  }
}
```

## 5. Örnek Kullanımlar

### Web Geliştirme
```bash
# Browser'ı aç ve test et
win ps "start chrome http://localhost:3000"
win screenshot browser_test.png
```

### Automation
```python
# Windows uygulaması otomasyonu
win.powershell("start notepad")
win.type("Automated text entry")
win.key("ctrl+s")
```

### Debugging
```bash
# Windows process'lerini kontrol et
win processes | grep python
win ps "Get-Process | Where-Object {$_.CPU -gt 50}"
```

## Kurulum Kontrolü

```bash
# Agent çalışıyor mu?
curl -s -H "Authorization: Bearer claude-agent-2024" \
  http://172.29.32.1:8765/health

# Tool kullanılabilir mi?
win screenshot test.png && echo "✓ Windows Agent working!"
```

## Sorun Giderme

1. **Agent bulunamıyor**: Windows'da `C:\Users\Uptake\WindowsAgent\install.bat` çalıştır
2. **Bağlantı hatası**: Firewall'da 8765 portunu kontrol et
3. **Permission denied**: Windows'da admin olarak çalıştır

---
Windows Agent v2.0 | Port: 8765