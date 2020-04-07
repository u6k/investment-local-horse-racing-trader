# 地方競馬トレーダー _(investment-local-horse-racing-trader)_

[![Build Status](https://travis-ci.org/u6k/investment-local-horse-racing-trader.svg?branch=master)](https://travis-ci.org/u6k/investment-local-horse-racing-trader)
[![license](https://img.shields.io/github/license/u6k/investment-local-horse-racing-trader.svg)](https://github.com/u6k/investment-local-horse-racing-trader/blob/master/LICENSE)
[![GitHub release](https://img.shields.io/github/release/u6k/investment-local-horse-racing-trader.svg)](https://github.com/u6k/investment-local-horse-racing-trader/releases)
[![WebSite](https://img.shields.io/website-up-down-green-red/https/shields.io.svg?label=u6k.Redmine)](https://redmine.u6k.me/projects/investment-local-horse-racing-trader)
[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)

> 地方競馬投資における、投資資金管理、および馬券投票を行う

__Table of Contents__

- [Install](#Install)
- [Usage](#Usage)
- [Other](#Other)
- [Maintainer](#Maintainer)
- [Contributing](#Contributing)
- [License](#License)

## Install

Dockerを使用します。

```
$ docker version
Client: Docker Engine - Community
 Version:           19.03.8
 API version:       1.40
 Go version:        go1.12.17
 Git commit:        afacb8b7f0
 Built:             Wed Mar 11 01:26:02 2020
 OS/Arch:           linux/amd64
 Experimental:      false

Server: Docker Engine - Community
 Engine:
  Version:          19.03.8
  API version:      1.40 (minimum version 1.12)
  Go version:       go1.12.17
  Git commit:       afacb8b7f0
  Built:            Wed Mar 11 01:24:36 2020
  OS/Arch:          linux/amd64
  Experimental:     false
 containerd:
  Version:          1.2.13
  GitCommit:        7ad184331fa3e55e52b890ea95e65ba581ae3429
 runc:
  Version:          1.0.0-rc10
  GitCommit:        dc9208a3303feef5b3839f4323d9beb36df0a9dd
 docker-init:
  Version:          0.18.0
  GitCommit:        fec3683
```

`docker pull`します。

```
docker pull u6kapps/investment-local-horse-racing-trader
```

前提

- Selenium Hub
- Google Chrome

コンポーネント構成、環境変数などは[docker-compose.yml](https://github.com/u6k/investment-local-horse-racing-trader/blob/master/docker-compose.yml)を参照してください。

## Usage

`selenium-hub`コンテナ、`chrome`コンテナを起動する。

Chromeを起動して、ターゲット・サイトのトップページを開く。事前にログインするために使用する。

```
docker run --rm u6kapps/investment-local-horse-racing-crawler pipenv run web-init
```

Chromeを起動して、対象レースに投票する。

```
docker run --rm u6kapps/investment-local-horse-racing-crawler pipenv run web-vote
```

## Other

最新情報は[Wiki](https://redmine.u6k./projects/investment-local-horse-racing-trader/wiki)をご覧ください。

## Maintainer

- u6k
    - [Twitter](https://twitter.com/u6k_yu1)
    - [GitHub](https://github.com/u6k)
    - [Blog](https://blog.u6k.me/)

## Contributing

当プロジェクトに興味を持っていただき、ありがとうございます。[既存のチケット](https://redmine.u6k.me/projects/investment-local-horse-racing-trader/issues/)をご覧ください。

当プロジェクトは、[Contributor Covenant](https://www.contributor-covenant.org/version/1/4/code-of-conduct)に準拠します。

## License

[MIT License](https://github.com/u6k/investment-local-horse-racing-trader/blob/master/LICENSE)
