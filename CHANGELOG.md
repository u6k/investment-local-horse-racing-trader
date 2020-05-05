# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Changed
- [#8364: 予測結果の記録と投票結果の記録を分ける](https://redmine.u6k.me/issues/8364)
- [#8362: ブラウザ操作で、ページを開いた時とページ遷移直前でスクリーンショットを取得する](https://redmine.u6k.me/issues/8362)
- [#8359: 最終資金を取得する](https://redmine.u6k.me/issues/8359)

## [1.2.1] - 2020-05-05
### Fixed
- [#8347: 実際に投票する](https://redmine.u6k.me/issues/8347)
    - `vote_cost_limit`を引数に追加

## [1.2.0] - 2020-05-05
### Added
- [#8347: 実際に投票する](https://redmine.u6k.me/issues/8347)

## [1.1.0]
### Added
- [#8348: 排他制御して、処理が1本しか実行されないようにする](https://redmine.u6k.me/issues/8348)

## [1.0.0]
### Changed
- [#8265: Flaskアプリに変更して、ジョブ登録はFlaskで定義したWebAPIで受け付ける](https://redmine.u6k.me/issues/8265)
- [#8339: 投票ページを開かずに、トレード処理を仮実行する](https://redmine.u6k.me/issues/8339)

## [0.6.0] - 2020-04-14
### Changed
- [#8222: ジョブ同時実行量を1に制限する](https://redmine.u6k.me/issues/8222)

### Added
- [#8218: ジョブ実行結果をSlackで通知する](https://redmine.u6k.me/issues/8218)

## [0.5.0] - 2020-04-14
### Fixed
- [#8212: ".env"が混入してしまっている](https://redmine.u6k.me/issues/8212)

### Changed
- [#8215: タイムゾーンを日本時間帯に設定する](https://redmine.u6k.me/issues/8215)

### Added
- [#8214: 投票の予約実行を外部から受け付けられるようにする](https://redmine.u6k.me/issues/8214)

## [0.4.0] - 2020-04-13
### Added
- [#8211: デモ投票時のデータをDBに記録する](https://redmine.u6k.me/issues/8211)

## [0.3.0] - 2020-04-10
### Added
- [#8163: 指定したレースについて着順予測・投票予測を行い、実際に投票する(ふりをする)](https://redmine.u6k.me/issues/8163)

## [0.2.0] - 2020-04-08
### Added
- [#8162: 一度ログインした後、ログイン状態が途切れないようにする](https://redmine.u6k.me/issues/8162)

## [0.1.0] - 2020-04-08
### Added
- [#8160: 楽天競馬トップページを取得するだけのオートメーターを構築する](https://redmine.u6k.me/issues/8160)
