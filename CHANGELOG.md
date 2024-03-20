- Renamed the project to LLM-chat as it now allows connecting not only with Mistral models but also with OpenAI models.

- Code refactoring to make room for using OpenAI models in addition to Mistral models. To achieve this, we will now use `Model` instead of `ModelName` for the model, with a field for the `Platform`. Additionally, the `model` will be None when the conversation's origin is not directly from the program, but may have been edited by the user (loading saved conversations).
