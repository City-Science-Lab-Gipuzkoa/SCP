# Sustainable Commuting Platform (SCP) code
This is a Python-based code for simulating the effect of different interventions on the CO<sub>2</sub> emissions associated with commuting in the Gipuzkoa region.

You are welcome to contribute to this project!

Here is a high-level overview of the directory structure:
```markdown
├── app.py
├── templates
│   └── login.html
├── layout
│   └── layout.py
├── components
│   ├── calcroutes_module.py
│   ├── find_stops_module.py
│   ├── generate_GTFS_module.py
│   ├── misc_functions.py
│   ├── pp.py
│   ├── prediction.py
│   ├── models
│   │   └── model.pkl (scikit-learn Random Forest classifier model file)
│   └── __pycache__
├── callbacks
│   └── callbacks.py
├── assets
│   ├── data
│   └── images