# flask-tabler-icons

flask-tabler-icons is a collection of Jinja macros for [tabler-icons](https://tabler-icons.io/) and Flask.

## Installation

```bash
pip install -U flask-tabler-icons
```

## Example (check examples folder for details)

Register the extension:

```python
from flask import Flask
from flask_tabler_icons import TablerIcons

app = Flask(__name__)
tabler_icons = TablerIcons(app)
```

```html

{% from "tabler_icons/helper.html" import render_icon %}

<html>
  <head>
    <!-- css area -->
    <style>
        .custom-css {
          color: red;
        }
    </style>
  </head>
  <body>
    <h2>tabler icon</h2>
    {{ render_icon("helicopter", class="custom-css") }}
    {{ render_icon("helicopter", animation="pulse", color="blue") }}
    {{ render_icon("helicopter", animation="tada", color="blue") }}
    {{ render_icon("helicopter", animation="rotate", color="blue") }}
  </body>
</html>
```
