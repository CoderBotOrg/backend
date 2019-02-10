# backend

> CoderBot is a RaspberryPI-based programmable robot for educational purposes. Check the [project website](https://www.coderbot.org) for more information.
>
> For further information about development and technical documentation, see the [Wiki](https://github.com/CoderBotOrg/coderbot/wiki).

This repository contains the backend, exposing the [CoderBot API](https://github.com/CoderBotOrg/backend/wiki/API-v2).

### Quickstart

Prerequisites:

```bash
sudo apt install python3 python3-venv
```

Be sure you have Python **3.6**. You may need to use `python3.6` and `python3.6-venv` packages on some repositories with python3 already pointing to **3.7** (e.g. debian unstable/sid).



```bash
git clone https://github.com/CoderBotOrg/coderbot.git
cd coderbot
python3 -m venv .
source bin/activate

# Install the basic requirements
pip3 install -r requirements_stub.txt
# Additional packages if you are running the real thing
pip3 install -r requirements.txt

# Start the backend in stub mode
PYTHONPATH=stub python3 init.py

# or, run the real thing if you're on a physical RPi
python3 init.py
```

Once started, the backend will expose a number of endpoints:

- Legacy API: [localhost:5000/`<LEGACY_METHOD>`](http://localhost:5000/);
- Legacy JQuery web application: [localhost:5000/old](http://localhost:5000/old);
- API v2: [localhost:5000/v2](http://localhost:5000/v2);
- New Vue web application: [localhost:5000/](http://localhost:5000/) (assuming a [vue-app](https://github.com/coderbotorg/vue-app) build is placed in the `dist/` folder);
- Documentation: [localhost:5000/docs](http://localhost:5000/docs) assuming a [docs](https://github.com/coderbotorg/docs) build is placed in the `cb_docs/` folder);
- Swagger UI dynamic documentation of the API v2: [localhost:5000/v2/ui/index.html](http://localhost:5000/v2/ui/index.html) (once you cloned the [swagger-ui](https://github.com/coderbotorg/swagger-ui) repository inside the backend folder).

