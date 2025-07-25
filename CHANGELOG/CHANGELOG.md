## [2.3.2](https://github.com/rapyuta-robotics/rapyuta-io-sdk/compare/v2.3.1...v2.3.2) (2025-06-27)


### Bug Fixes

* **rest_client:** configure default request timeouts ([cb9ae03](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/cb9ae035dbe886657544e194e38e37716c7a391f)), closes [rapyuta-robotics/rapyuta_io#853](https://github.com/rapyuta-robotics/rapyuta_io/issues/853)

## [2.3.2](https://github.com/rapyuta-robotics/rapyuta-io-sdk/compare/v2.3.1...v2.3.2) (2025-06-27)


### Bug Fixes

* **rest_client:** configure default request timeouts ([cb9ae03](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/cb9ae035dbe886657544e194e38e37716c7a391f)), closes [rapyuta-robotics/rapyuta_io#853](https://github.com/rapyuta-robotics/rapyuta_io/issues/853)

## [2.3.1](https://github.com/rapyuta-robotics/rapyuta-io-sdk/compare/v2.3.0...v2.3.1) (2025-04-09)


### Bug Fixes

* **paramserver:** raise exception on binary file upload failure ([73816fb](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/73816fb3cdac8b8c45ea34aaf7d7d3388a8e95e5))

# [2.3.0](https://github.com/rapyuta-robotics/rapyuta-io-sdk/compare/v2.2.2...v2.3.0) (2025-03-20)


### Features

* adds method to exec on multiple devices ([e47d02b](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/e47d02b3263b062a20e240a5f99cec68c1a98784))

## [2.2.2](https://github.com/rapyuta-robotics/rapyuta-io-sdk/compare/v2.2.1...v2.2.2) (2024-12-11)


### Bug Fixes

* **device:** fix timeout interval ([7c6a1ae](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/7c6a1ae638152e3d6737f3f88bcfa04e8f51b8bb))

## [2.2.1](https://github.com/rapyuta-robotics/rapyuta-io-sdk/compare/v2.2.0...v2.2.1) (2024-12-11)


### Bug Fixes

* **device:** update execute to accept query parameters ([928147d](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/928147d7d638f9047575a68d79dc649d8bbd0d22))

# [2.2.0](https://github.com/rapyuta-robotics/rapyuta-io-sdk/compare/v2.1.1...v2.2.0) (2024-11-22)


### Features

* add support for background command executes ([db34d48](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/db34d48bdbcd545837c659a1566e84a94f8c6502))

## [2.1.1](https://github.com/rapyuta-robotics/rapyuta-io-sdk/compare/v2.1.0...v2.1.1) (2024-11-12)


### Bug Fixes

* **paramserver:** file is too large error ([#98](https://github.com/rapyuta-robotics/rapyuta-io-sdk/issues/98)) ([3f379ee](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/3f379eef86e3fd8aa9e77fab44f5df5fae519a59)), closes [AB#33921](https://github.com/AB/issues/33921)

# [2.1.0](https://github.com/rapyuta-robotics/rapyuta-io-sdk/compare/v2.0.0...v2.1.0) (2024-10-23)


### Features

* **device:** implement RefreshPollerMixin for Device class ([#84](https://github.com/rapyuta-robotics/rapyuta-io-sdk/issues/84)) ([f0ebeb3](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/f0ebeb3ffbc9aaf036fc6b7315d43cad0ba951c9))

# [2.0.0](https://github.com/rapyuta-robotics/rapyuta-io-sdk/compare/v1.17.1...v2.0.0) (2024-10-14)


* fix!: remove unsupported APIs ([fd05053](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/fd0505337ffc25a9105d8ac00d5cb9f0f0ac9446))


### BREAKING CHANGES

* The SDK methods for unsupported APIs are dropped

## [1.17.1](https://github.com/rapyuta-robotics/rapyuta-io-sdk/compare/v1.17.0...v1.17.1) (2024-09-12)


### Bug Fixes

* force bump release version ([dfd78f0](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/dfd78f0ad84a96a72748f20d1f58924b4cccc416))

# [1.17.0](https://github.com/rapyuta-robotics/rapyuta-io-sdk/compare/v1.16.0...v1.17.0) (2024-08-01)


### Features

* **devices:** filter device list by name ([#87](https://github.com/rapyuta-robotics/rapyuta-io-sdk/issues/87)) ([8be2eaf](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/8be2eaf4a24c9c1e3508967a2561af1763e63f58))

# [1.16.0](https://github.com/rapyuta-robotics/rapyuta-io-sdk/compare/v1.15.1...v1.16.0) (2024-06-27)


### Features

* **device:** allow custom config variables and labels during creation ([#80](https://github.com/rapyuta-robotics/rapyuta-io-sdk/issues/80)) ([5834b1e](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/5834b1ec4dd969142021c7b6d8e44f0b63e2757a))

## [1.15.1](https://github.com/rapyuta-robotics/rapyuta-io-sdk/compare/v1.15.0...v1.15.1) (2024-06-04)


### Bug Fixes

* **package:** removes parameter value validation ([df2f0dc](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/df2f0dcf2874759775929557285053b0191f6d0a))
* **paramserver:** validates yaml or json data ([#77](https://github.com/rapyuta-robotics/rapyuta-io-sdk/issues/77)) ([a543f71](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/a543f71a1fefde347f8721187b7094a161b2dc50))
* **utils:** corrects exception handling in parse_json ([c16d229](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/c16d22972d544e35464f64073cb6cab9fb69fb87))

# [1.15.0](https://github.com/rapyuta-robotics/rapyuta-io-sdk/compare/v1.14.0...v1.15.0) (2024-02-27)


### Features

* **deployment:** adds support for host subpath uid/gid/perm ([d2ee458](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/d2ee458f2ff1e51b9718059e07a57b4f18614d8c))

# [1.14.0](https://github.com/rapyuta-robotics/rapyuta-io-sdk/compare/v1.13.0...v1.14.0) (2024-01-22)


### Bug Fixes

* **paramserver:** raise exception during download when trees not found ([#73](https://github.com/rapyuta-robotics/rapyuta-io-sdk/issues/73)) ([42f2c41](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/42f2c4100e1383fea7bae1ff63b7aaf9f64c17a1))


### Features

* **params:** use binary file-upload if file is large ([f276b33](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/f276b33cf4dedc7a5d7271fe1daada9ef8f4849e))

# [1.13.0](https://github.com/rapyuta-robotics/rapyuta-io-sdk/compare/v1.12.0...v1.13.0) (2023-12-13)


### Features

* **device:** accepts feature config in toggle_features ([#70](https://github.com/rapyuta-robotics/rapyuta-io-sdk/issues/70)) ([a293787](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/a2937874d500633c79497cfc8414ed5f09e32137))

# [1.12.0](https://github.com/rapyuta-robotics/rapyuta-io-sdk/compare/v1.11.1...v1.12.0) (2023-09-26)


### Features

* **usergroup:** supports user group role in projects ([4f6c34f](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/4f6c34fd713cb493c6b44225d566e90afe8f88fa))

## [1.11.1](https://github.com/rapyuta-robotics/rapyuta-io-sdk/compare/v1.11.0...v1.11.1) (2023-07-27)


### Bug Fixes

* **package:** makes dependent deployment ready phase configurable ([e0df4ec](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/e0df4ecab55a2defd47cae6446dda7f48e7e9f42))

# [1.11.0](https://github.com/rapyuta-robotics/rapyuta-io-sdk/compare/v1.10.0...v1.11.0) (2023-07-14)

### Features

* **deployment**: adds update_deployment API ([51c14af74c3377585c56c025cb99af12bc90910d](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/51c14af74c3377585c56c025cb99af12bc90910d))
* **deployment**: made poll deployment till ready phase configurable ([763716c](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/763716c47c426a513f4f9eb522419086a37349bc))
* **usergroup**: implements usergroup APIS ([6d9037e](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/6d9037eb162e8854e0595dcf4caf3caf11c7980a))

# [1.10.0](https://github.com/rapyuta-robotics/rapyuta-io-sdk/compare/v1.9.0...v1.10.0) (2023-05-31)


### Features

* **rip:** adds support for token_level in get_auth_token ([88fcc69](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/88fcc697842de856a031a370f8ab630047532f49))

# [1.9.0](https://github.com/rapyuta-robotics/rapyuta-io-sdk/compare/v1.8.0...v1.9.0) (2023-04-19)


### Bug Fixes

* **metrics:** tags schema and its unit tests ([6cf652b](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/6cf652b177fb7c722a037ff9498c845ee12a6ff1))
* **rosbags:** integration-test for throttling ([3cd2cd6](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/3cd2cd6d1ed1ca3a6b4beb050865dcedb56b4c45))


### Features

* **device:** adds API to toggle features ([39860fc](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/39860fc05a7a261862a2738ca1d9c7af546a0f6f))
* **network:** allows custom resource limits for cloud networks ([e58f0c5](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/e58f0c5c33ddd0f860210cc9a74cb6e6cf9ef6b9))
* **parameters:** adds the option to upload arbitrary directories as config ([4c95e96](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/4c95e96db054bbc5fba615edafd586d65a9b7a5a))

# [1.8.0](https://github.com/rapyuta-robotics/rapyuta-io-sdk/compare/v1.7.0...v1.8.0) (2023-02-07)


### Features

* **rosbag:** fetches rosbag job by guid ([3d93c6e](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/3d93c6e2f8c1d4e6bda7de2815b1ec3a1001bdc9))

# [1.7.0](https://github.com/rapyuta-robotics/rapyuta-io-sdk/compare/v1.6.1...v1.7.0) (2022-12-14)


### Features

* **rosbags:** adds support for splitting rosbags by duration ([3770e00](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/3770e00a7d95d6ca8699185a96bf6941a29c3875))

# [1.6.0](https://github.com/rapyuta-robotics/rapyuta-io-sdk/compare/v1.5.0...v1.6.0) (2022-10-27)
### Features
- **device:** Added support for throttling and latching of rosbags

# [1.5.0](https://github.com/rapyuta-robotics/rapyuta-io-sdk/compare/v1.4.0...v1.5.0) (2022-09-16)


### Features

* **device:** added support to enable both runtimes on a device ([6bca6f1](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/6bca6f16f9bf9cfb7fb3d36915c8b017ed73e57c))

# [1.4.0](https://github.com/rapyuta-robotics/rapyuta-io-sdk/compare/v1.3.0...v1.4.0) (2022-06-23)


### Features

* **build:** added support for webhooks in build update ([d7f53f5](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/d7f53f50b552686c67a533946ee4207264e10911))

# [1.3.0](https://github.com/rapyuta-robotics/rapyuta-io-sdk/compare/v1.2.0...v1.3.0) (2022-05-26)


### Features

* **user:** adding user to multiple organizations ([5072307](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/507230787c32aca96ded2cd0eb0a62c88b085ca5))

# [1.2.0](https://github.com/rapyuta-robotics/rapyuta-io-sdk/compare/v1.1.0...v1.2.0) (2022-05-09)


### Features

* **secret:** add method to update secrets ([21eaeb8](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/21eaeb844a988ae7487782243b003b905d8aa278))

# [1.1.0](https://github.com/rapyuta-robotics/rapyuta-io-sdk/compare/v1.0.0...v1.1.0) (2022-03-24)


### Features

* **build:** trigger a dispatch event on build completion ([ecf3da5](https://github.com/rapyuta-robotics/rapyuta-io-sdk/commit/ecf3da59b4b6ec85d6acbb61fc4c74d36cc20bd3))

# 1.0.0 (2022-02-14)
