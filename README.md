# otaku-info

|master|develop|
|:----:|:-----:|
|[![build status](https://gitlab.namibsun.net/namibsun/python/otaku-info/badges/master/build.svg)](https://gitlab.namibsun.net/namibsun/python/otaku-info/commits/master)|[![build status](https://gitlab.namibsun.net/namibsun/python/otaku-info/badges/develop/build.svg)](https://gitlab.namibsun.net/namibsun/python/otaku-info/commits/develop)|

![Logo](resources/logo-readme.png)

otaku-info is a website that provides information on various forms of
Japanese entertainment media, including anime, manga and light novels.

A live version of the website is running here:
[otaku-info.eu](https://otaku-info.eu)

# Features

## Manga Updates

The website can display the amount of unread manga chapters for a connected
[anilist.co](https://anilist.co) account.
It also support telegram notifications for when new chapters are released.

## Light Novel Releases

The website collects light novel releases from reddit.com's /r/lightnovels
and displays them.

## API

The website offers a REST API with various endpoints:

* ```/media_ids``` maps IDs for one service like Anilist oder Myanimelist to
                   other service IDs

# Deployment

All deployments assume the existence of a ```.env``` file in the project's
root directory.
This file must contain all environment variables used by the website.

The supported environment variables can be seen in [env.sample](env.sample).

## Without Docker

To start the web application without docker, you can simply call
```python server.py``` after installing it using ```python setup.py install```.
This will run the application using the cherry WSGI server on the port
specified in the ```.env``` file.

## With docker (and docker-compose)

This project provides a Dockerfile as well as a docker-compose file.
Do get up and running, simply type in the following commands:

```shell script
docker-compose build
docker-compose up -d
```

## Further Information

* [Changelog](CHANGELOG)
* [License (GPLv3)](LICENSE)
* [Gitlab](https://gitlab.namibsun.net/namibsun/python/otaku-info)
* [Github](https://github.com/otaku-info)
* [Progstats](https://progstats.namibsun.net/projects/otaku-info)
* [PyPi](https://pypi.org/project/otaku-info)
