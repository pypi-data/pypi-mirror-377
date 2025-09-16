# flask-topassets

a package on top of flask-assets for plugin

## installation

```bash
pip install flask_topassets
```

## usage

```python
# e.g. in flask-tomselect

from flask_topassets import TopAssets

# used in flask-tabler import
CLASS_NAME = "TomSelect"

class TomSelect(TopAssets):
    def __init__(self, app=None) -> None:
        if app:
            self.init_app(app)

    def init_app(self, app) -> None:
        self.prepare(app, "tomselect")
        self.bundle_js("tom-select.complete.min.js")
        self.bundle_css("tom-select.tabler.min.css")


# in templates head
{{ tomselect.get_path("css") }}
# output is:
# <link rel="stylesheet" href="/tomselect/select/tom-select.tabler.min.css" />

# for javascript
{{ tomselect.get_path("js") }}
# output is:
# <script type="text/javascript" src="/tomselect/select/tom-select.complete.min.js"></script>

{% from "tomselect/helpers.html" import js_tomselect %}

<div class="mb-3">
  <div class="form-label">Select</div>
  <select class="form-select" id="demo" name="demo">
    <option value="1">One</option>
    <option value="2">Two</option>
    <option value="3">Three</option>
  </select>
</div>
{{ js_tomselect("demo", plugins=["remove_button", "clear_button"]) }}
```
