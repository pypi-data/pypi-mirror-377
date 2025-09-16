# flask-autosize

a package to use autosize in flask

## installation

```bash
pip install flask_autosize
```

## usage

```python
from flask_autosize import Autosize

a = Autosize()
a.init_app(app)
# or
# Autosize(app)

# in templates
{% assets "autosize_js" %}
    {{ autosize.get_path("js") }}
{% endassets %}

```
