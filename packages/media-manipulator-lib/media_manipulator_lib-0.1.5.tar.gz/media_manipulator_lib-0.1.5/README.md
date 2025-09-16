# 🎬 Media Manipulator Library

A modular, pluggable video editing library built with Python and FFmpeg. 
Supports programmatic video transformations like text (watermark) overlay and audio merging using strategy and interpreter design patterns.

---

## 🚀 Features

- Add watermark (text overlay) to videos
- Overlay audio tracks onto videos
- Process nested JSON editing instructions
- In-memory and tempfile-based FFmpeg pipelines
- Clean, extendable strategy-based architecture
- Custom command interpreter for complex video editing workflows
- Developer-friendly logging

---

## 📦 Installation

### From PyPI (coming soon)
```bash
pip install media-manipulator-lib==0.1.5
```
https://pypi.org/project/media-manipulator-lib/0.1.5/

### From source
```bash
git clone https://github.com/angel-one/media-manipulator-library
cd media-manipulator-library
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

---

## 🧪 Testing

```bash
pytest            # all tests
pytest tests/unit         # only unit tests
pytest tests/integration  # only integration tests
```

---

## 🔧 Usage Example

```python
from video_editor import process_json_command

command = {
    "operation": "overlay",
    "left": {
        "operation": "overlay",
        "left": {
            "type": "video",
            "value": base64.b64encode(open("video.mp4", "rb").read())
        },
        "right": {
            "type": "text",
            "value": "Aditya Sharma",
            "style": {
                "position_x":380,
                "position_y":380,
                "size": 52,
                "style": ""
            }
        }
    },
    "right": {
        "type": "audio",
        "value": base64.b64encode(open("audio.mp3", "rb").read())
    }
}

result = process_json_command(command)

with open("output.mp4", "wb") as f:
    f.write(result["bytes"].getvalue())
```

---

## 📂 Project Structure

```
media-manipulator-lib/
├── media_manipulator/                  # Main package
│   ├── __init__.py
│   ├── cli.py                          # CLI entry point (if used)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── interpreter.py             # JSON → command parser
│   │   ├── processor.py               # Operation executor
│   │   ├── strategy_registry.py       # Registers available strategies
│   │   └── strategies/                # Strategy pattern implementations
│   │       ├── __init__.py
│   │       ├── add.py
│   │       ├── base.py
│   │       ├── clip.py
│   │       ├── concat.py
│   │       ├── overlay.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── audio.py                   # Audio processing helpers
│   │   ├── helpers.py                 # Generic utilities
│   │   ├── logger.py                  # Logger setup
│   │   └── video.py                   # Video processing helpers
├── tests/                              # Unit and integration tests
├── .gitignore
├── LICENSE
├── MANIFEST.in
├── pyproject.toml
├── README.md
├── requirements.txt                   # Optional (for dev setup)
└── setup.py
```

---

## 🛠️ Built With

- **Python 3.11+**
- **FFmpeg + ffmpeg-python**
- **pytest** for testing
- **json** for colored logging

---

## 📜 License

MIT License © 2025 Aditya Sharma / AngelOne

---

## 🙋‍♂️ Contributing

Contributions welcome! Please submit issues or pull requests for improvements or new features.

---

## 📫 Contact

For questions or support, open a GitHub issue or reach out to aditya.3sharma@angelone.in