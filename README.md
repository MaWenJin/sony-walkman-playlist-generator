# 🎵 Sony Walkman MP3 Playlist Generator

专为 **Sony Walkman (NW-A45/A40/A30 等)** 优化的 M3U 播放列表生成工具。

完美解决索尼播放器“能识别列表但找不到歌曲”的痛点。脚本强制使用 **UTF-8 无 BOM 编码**，并仅写入 **纯文件名**，确保在 Walkman 上 100% 兼容。

---

## ✨ 核心特性

- 🎯 **索尼专属优化**：自动处理路径格式与文件编码，拒绝“列表为空”或“找不到文件”。
- 📊 **音乐库统计**：一键扫描，快速查看总时长、总大小、歌手/专辑数量。
- 🎤 **多维度生成**：
  - `--latest`：按导入时间，生成最新导入的播放列表（支持 `-n` 自定义数量）。
  - `--artist`：按歌手分类，支持 `-n` 截取 Top N 歌手。
  - `--album`：按专辑分类，支持 `-n` 截取 Top N 专辑。
  - `--random`：随机抽取播放列表（支持 `-n` 自定义数量）。
- 🛡️ **999首安全护栏**：针对索尼 Walkman 硬件限制，`--latest` 和 `--random` 模式自动检测并拦截超过 999 首的请求，防止播放器无法加载。
- 🚀 **一键部署**：`--deploy` 参数自动将生成的列表覆盖拷贝到音乐根目录，省去手动复制步骤。
- 🛡️ **安全防错**：自动检测源文件与目标文件是否相同，避免 `SameFileError`。

---

## 📦 安装

1. 克隆或下载本仓库：
   ```bash
   git clone https://github.com/你的用户名/sony-walkman-playlist-generator.git
   cd sony-walkman-playlist-generator
   ```

2. 安装依赖（仅需 `mutagen`）：
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 快速开始

### 1. 查看音乐库统计
```bash
python mp3_to_m3u.py /path/to/your/music --stats
```
*输出示例：*
```text
📊 Music Library Statistics:
------------------------------
🎵 Total Tracks: 1500
💾 Total Size:   12450.67 MB
⏱️ Total Length: 105:23:45
🎤 Artists:      320
💿 Albums:       185
------------------------------
```

### 2. 生成最新 300 首并自动部署
```bash
python mp3_to_m3u.py /path/to/your/music --latest -n 300 --deploy
```

### 3. 生成 Top 10 歌手播放列表
```bash
python mp3_to_m3u.py /path/to/your/music --artist -n 10 -o ./playlists
```

### 4. 随机抽取 200 首并部署
```bash
python mp3_to_m3u.py /path/to/your/music --random -n 200 --deploy
```

---

## ⚙️ 参数说明

| 参数 | 说明 |
| :--- | :--- |
| `directory` | **必填**，包含 MP3 文件的根目录路径 |
| `--latest` | 生成最新导入的播放列表 |
| `--artist` | 按歌手生成多个播放列表 |
| `--album` | 按专辑生成多个播放列表 |
| `--random` | 随机生成播放列表 |
| `--stats` | 仅统计并打印音乐库信息，不生成文件 |
| `-n N` | 配合上述四种模式使用。指定数量或截取 Top N（默认值：latest=100, random=50） |
| `-o DIR` | 指定 M3U 文件的输出目录（默认与音乐目录相同） |
| `--deploy` | 自动将生成的 M3U 拷贝到音乐根目录，强制覆盖同名文件 |

⚠️ **硬件限制提示**：当 `--latest` 或 `--random` 配合 `-n` 使用时，若指定数量超过 999，脚本会自动将其截断为 999 并输出警告日志。

---

## 💡 索尼 Walkman 使用须知

1. **文件位置**：生成的 `.m3u` 文件必须放在 Walkman 的 `Music` 文件夹内（根目录或子目录均可）。
2. **文件对齐**：如果使用 `--latest` 或 `--random`，请确保 `.m3u` 和 `.mp3` 在**同一文件夹**内。
3. **刷新媒体库**：拷贝完成后，请在 Walkman 设置中点击“刷新媒体库”或重启设备。
4. **编码问题**：请勿使用记事本手动编辑 `.m3u` 文件，以免被自动添加 BOM 头导致索尼无法识别。

---

## 📄 License

MIT License. Feel free to use and modify!