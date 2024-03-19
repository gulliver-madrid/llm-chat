# Changelog

## [Unreleased]

- Code refactoring to make room for using OpenAI models in addition to Mistral models. To achieve this, we will now use `Model` instead of `ModelName` for the model, with a field for the `Platform`. Additionally, the `model` will be None when the conversation's origin is not directly from the program, but may have been edited by the user (loading saved conversations).

## [0.5.0]

### Added

- implement `/new` command.
- add conversations loading using `/load` command.

### Changed

- conversations now continue by default. [BREAKING CHANGE]
- improve schema with model information (schema v0.2).

## [Unreleased]

### Changed

- improve schema (v0.1).

## [0.4.0]

### Added

- implement automatic saving of conversations.

### Changed

- add warning for too many queries.
- implement commands from the main prompt. [BREAKING CHANGE]

## [0.3.0]

### Added

-  improve help message
-  implement iterative placeholders.
-  allow to change model.

## [0.2.0]

### Added

- add README.
- add model choice by the user.
- multiline messages
