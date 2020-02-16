# otaku-info-web

Flask Application Template - For Fast Initial Project Develoment

|master|develop|
|:----:|:-----:|
|[![build status](https://gitlab.namibsun.net/namboy94/otaku-info-web/badges/master/build.svg)](https://gitlab.namibsun.net/namboy94/otaku-info-web/commits/master)|[![build status](https://gitlab.namibsun.net/namboy94/otaku-info-web/badges/develop/build.svg)](https://gitlab.namibsun.net/namboy94/otaku-info-web/commits/develop)|

![Logo](otaku_info_web/static/logo.png)

# Usage
To start the web application, you can simply call ```python server.py``` after
installing it using ```python setup.py install```.

To run the application in docker, make sure all necessary environment
variables are stored in the ```.env``` file. Also make sure that the
```HTTP_PORT``` and ```DEPLOY_MODE``` environment variables are set.
If this is the case, simply run ```docker-compose up -d``` to start the
application.

## Further Information

* [Changelog](CHANGELOG)
* [License (GPLv3)](LICENSE)
* [Gitlab](https://gitlab.namibsun.net/namibsun/python/otaku-info-web)
* [Github](namboy94/otaku-info-web)
* [Progstats](https://progstats.namibsun.net/projects/otaku-info-web)
* [PyPi](https://pypi.org/project/otaku-info-web)
