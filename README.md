# Text Interface for Mistral Models

This project provides a text interface to interact with [Mistral AI](https://mistral.ai/) models using a local script. The script allows users to select a model, input a
question, and receive the model's response.

## Disclaimer
This project is not affiliated, associated, authorized, endorsed by, or in any way officially connected with Mistral AI, or any of its subsidiaries or its affiliates. The official Mistral AI website can be found at https://mistral.ai/. The name "Mistral AI" as well as related names, marks, emblems, and images are registered trademarks of their respective owners.

## Prerequisites
To use this project successfully, an API key from Mistral AI is required. Obtaining this API key may incur a financial cost and must be acquired directly from Mistral AI. Please visit the official Mistral AI website for more information on how to obtain your API key.

## Installation

### Using `poetry` (recomended)

Ensure you have installed [Poetry](https://python-poetry.org/docs/#installation).

To install the required Python packages for this project, run:

```
poetry install
```

### Using `pip`

Install the required Python packages: `mistralai` and `rich`. You can install them using pip, either globally or inside a virtual environment:

```
pip install mistralai rich
```

This command will install the necessary dependencies.

## Usage

**Before using this script**, ensure you have set your `MISTRAL_API_KEY` environment variable:

On Linux:

```
export MISTRAL_API_KEY=<your_api_key>
```
On Windows:

```
set MISTRAL_API_KEY=<your_api_key>
```


**To run the script**, execute the `src/main.py` file.

Using poetry:

```
poetry run python src/main.py
```

Or, if installed using pip:

```
python src/main.py
```

The script allows you to interact with it in a conversational manner by inputting questions. After launching the script, it will prompt you to choose from the available models or to proceed with the default model. Once a model is selected, you can begin typing your question. If your query spans multiple lines, simply continue typing until you've finished formulating your question.

To indicate that you have finished entering your question, type `end` on a new line. The model will then process your input and provide a response. After receiving a response, you are free to initiate a new query by following the same process.

If your query includes *placeholders* (e.g., `$0concept`), you can introduce a line using the format `/for value1,value2,value3`, allowing the script to replace these placeholders with the indicated values before processing the query. This enables you to efficiently conduct multiple related queries in a single execution.

To exit the program, simply leave the question blank and write `exit` in the next menu.

### Example of a query with placeholder substitution:

```
Please enter your query (or press Enter to see more options). Type
'end' as the sole content of a line when you have finished.
> What is $0concept? Define it briefly.
end

Please indicate the value of $0concept
> /for the enlightenment,the baroque,the renaissance
Placeholders substituted successfully

...processing query
```

This functionality is particularly useful for performing multiple related queries without the need to restart the process for each new input, thus enhancing the user experience and efficiency when interacting with the system.


### Features

This script offers the following features:

- Interactive model selection
- Input validation and error handling
- Display of model interactions with time-stamps and role indicators
- Support for entering debug mode.

### Debugging

The script includes debugging functionalities in the `src.debug` module.

This feature will display the debug information when you enter the debug mode by typing 'd'. This allows inspect the `response` object returned by the Mistral API.

### Development

⚠️ **Warning: Risk of force push!** If you have local changes that you do not wish to lose, we strongly recommend avoiding the use of `git pull` or `git fetch` without first making sure you understand the implications. These commands can cause your local changes to be overwritten if not handled carefully. ⚠️

This project uses [Poetry](https://python-poetry.org/) for package management and dependency handling. To set up the development environment and
install required tools, run:

```
poetry install --with dev
```

The development dependencies include `mypy` for static type checking.

### License

This project is licensed under the [GPLv3 License](https://www.gnu.org/licenses/quick-guide-gplv3.html).



### Acknowledgements

This project is built using the following open-source libraries:

- [Mistral AI](https://github.com/mistralai/client-python)
- [Rich](https://github.com/Textualize/rich)

We are grateful to their respective maintainers and contributors.
