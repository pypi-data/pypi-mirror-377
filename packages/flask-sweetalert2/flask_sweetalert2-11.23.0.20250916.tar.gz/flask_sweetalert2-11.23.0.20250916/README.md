# flask-sweetalert2

a package to use sweetalert2 in flask

## installation

```bash
pip install flask_sweetalert2
```

## usage

```python
from flask_sweetalert2 import Sweetalert2

c = Sweetalert2()
c.init_app(app)
# or
# Sweetalert2(app)

# in templates to include css file
{{ sweetalert2.get_path("css") }}

# in templates to include js file
{{ sweetalert2.get_path("js") }}
{{ sweetalert2.get_path("helpers", "js") }}

```
