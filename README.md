# otaku-info

Website providing information on Japanese entertainment media

|master|develop|
|:----:|:-----:|
|[![build status](https://gitlab.namibsun.net/namibsun/python/otaku-info/badges/master/build.svg)](https://gitlab.namibsun.net/namibsun/python/otaku-info/commits/master)|[![build status](https://gitlab.namibsun.net/namibsun/python/otaku-info/badges/develop/build.svg)](https://gitlab.namibsun.net/namibsun/python/otaku-info/commits/develop)|

![Logo](resources/logo-readme.png)

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
* [Gitlab](https://gitlab.namibsun.net/namibsun/python/otaku-info)
* [Github](https://github.com/otaku-info)
* [Progstats](https://progstats.namibsun.net/projects/otaku-info)
* [PyPi](https://pypi.org/project/otaku-info)
