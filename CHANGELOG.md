# Changelog

(work in progress, not totally updated)

## [Unreleased]
- Use of Raw, EscapedStr, StyledStr to handle strings that may be contaminated by style brackets or escapes. Several things are sought:
  - not to pass directly to `rich` functions text of which it is unknown if it has non-style brackets
  - not to apply style without first escaping the text
  - not to escape already escaped text, as it would generate unwanted backslashes
- Text that obviously does not risk having received style through brackets (such as a pure response from the model, and strings processed from this response before entering the view circuit) does not need to be marked as Raw until it is going to enter the view circuit.


## [Unreleased]
- [BREAKING CHANGES] Change the chat directory. The transition should happen automatically.
- Finding directories or files with an invalid chat name in the chat directory generates a warning but does not stop the program.


## [Unreleased]

### Added

- Add system prompt customization.
- Add `/show` command to display current model name.
- Add a description of every command in inline help.
- Add option to load API keys from `.env` file.

## [0.6.0]

### Changed

- Renamed the project to LLM-chat as it now allows connecting not only with Mistral models but also with OpenAI models.
- Code refactoring to make room for using OpenAI models in addition to Mistral models. To achieve this, we will now use `Model` instead of `ModelName` for the model, with a field for the `Platform`. Additionally, the `model` will be None when the conversation's origin is not directly from the program, but may have been edited by the user (loading saved conversations).
- Add `openai` library as dependency.
- Manage mistral connection error with a expresive exception.
- Update disclaimers to include references to OpenAI.
- Unifica debug para mistray y openai.
- Hace más consistente la identificación de los placeholders, de acuerdo con los casos de uso implementados en `test_find_placeholders`.

## [0.5.1]

### Added

- add spanish translation of README
- add a section to README about versioning and changelog strategy.

### Changed

- improve documentation using 'application' instead of 'script' to reference the project.
- add links to sections in README


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
