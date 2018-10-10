# CoderBot

A RaspberryPI-based programmable robot for educational purposes. Check the [project website](https://coderbot.org) for more information.

For further information about development and technical documentation, see the [Wiki](https://github.com/CoderBotOrg/coderbot/wiki).

This repository contains the backend, along with some configuration applied on the base system image.

### Quickstart

```bash
git clone https://github.com/CoderBotOrg/coderbot.git
cd coderbot
python3 -m venv .
source bin/activate
pip3 install -r requirements.txt

# Start the backend in stub mode
PYTHONPATH=stub python3 init.py

# or, run the real thing if you're on a physical RPi
python3 init.py
```

The legacy API and frontend application is available at `localhost:5000`.

The new API is at `localhost:5000/v2`, while the new application is served at `localhost:5000/vue` (assuming the [vue-app](https://github.com/coderbotorg/vue-app) build is placed in the `dist/` folder).

To see the dynamic documentation of the new API, clone the [swagger-ui](https://github.com/coderbotorg/swagger-ui) repository inside the `coderbot/` folder and it'll be live at `localhost:5000/v2/ui/index.html`.

