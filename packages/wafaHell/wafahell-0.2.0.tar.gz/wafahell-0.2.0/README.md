# WafHell

Middleware WAF for Flask, to detect SQLi and XSS.

## Instalation

```bash
pip install wafahell
```

## Usage
```python
from flask import Flask
from wafahell import WafaHell

app = Flask(__name__)
waf = WafaHell(app)
```