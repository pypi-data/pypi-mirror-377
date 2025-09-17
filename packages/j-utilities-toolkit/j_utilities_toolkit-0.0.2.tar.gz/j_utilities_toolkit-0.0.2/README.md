# jtoolkit

A collection of lightweight, reusable Python utilities designed for everyday development tasks.  

The goal of **jtoolkit** is to provide a consistent set of building blocks — logging, configuration, timing, debugging, and more — so you can focus on writing your applications instead of rewriting boilerplate.

---

## ✨ Features (more coming soon)

- **jLogging** – Simplified logging setup with sensible defaults.
- **jConfig** – Load configuration from environment variables, JSON, or YAML.
- **jSplunk** – A very basic wrapper around splunk-sdk that supports querying Splunk.
- **jDateTime** – A few basic date/time functions
---

## 📦 Installation

Once published to PyPI:

```bash
pip install jtoolkit
```

---

## 🚀 Usage Example

```python
from jtoolkit import jConfig, jLogging

config = Config()
logging_info = LoggingInfo(**config.get("logging_info", {}))
logger = Logger(logging_info)

transaction = logger.transaction_event(EventType.TRANSACTION_START)

# ... your code ...
# capture some results
payload = {
    'total_records': total_records,
    'total_deleted': total_deleted,
    'total_errors': total_errors
}

logger.transaction_event(EventType.TRANSACTION_END, transaction=transaction, payload=payload, return_code=200)
```

---

## 📊 Version History

| Version | Date       | Changes                                                |
|---------|------------|--------------------------------------------------------|
| 0.0.1   | 2025-09-14 | Initial release just to define structure and register. |
| 0.0.2   | 2025-09-16 | Adding jSplunk and jDateTime.                          |


---

## ⚠️ Breaking Changes

This section tracks **major breaking changes** between versions.

- *None yet – under development.*

---

## 🔧 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests with improvements and new utilities.

---

## 📄 License

This project is licensed under the MIT License – see the [LICENSE](https://github.com/jaysuzi5/jToolkit/blob/main/LICENSE) file for details.
