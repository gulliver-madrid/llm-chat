# Code Conventions

1. **Docstrings**: Functions and methods must have docstrings that briefly describe their purpose. These docstrings should be enclosed in triple double quotes (`"""`) and written in English.

2. **Types**: Functions and methods should use type annotations to specify the types of their arguments and return values.

3. **Variable and Method Names**: Variables and methods should use descriptive lowercase names, separated by underscores (`_`) if necessary.

4. **Uppercase for Constants**: Constants such as `NEUTRAL_MSG`, `CHANGE_MODEL`, and `EXIT` should be written in uppercase, with words separated by underscores.

5. **Naming Conventions for Functions, Methods, and Classes**:
   - Functions and methods should use `lower_snake_case` naming. For example, `print_interaction`, `execute`, `get_simple_response`.
   - Classes should use `UpperCamelCase` naming. For example, `Main`, `MenuManager`, `ClientWrapper`.

6. **Imports**: Imports should be grouped by third-party packages, standard libraries, and local modules. Within each group, imports should be sorted alphabetically.

7. **Use of Assertions**: Assertions should be used to verify conditions that must be true during program execution, such as the presence of a variable or the type of a variable.

8. **Direct Execution Block**: Code that should be executed when the module is run directly (not when imported) should be inside an `if __name__ == "__main__":` block.

9. **Use of Dataclasses**: Classes that are primarily used for storing data should be defined as dataclasses, reducing the need for writing repetitive code.

10. **Error Handling**: The `RuntimeError` exception should be used for handling runtime errors.

These conventions aim to maintain clean, readable, and maintainable code, promoting good software development practices.
