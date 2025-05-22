# Contributing to Flask Authentication App

We welcome contributions to Flask Authentication App! Whether it's bug reports, feature suggestions, or code contributions, your help is appreciated.

## How to Contribute

### Reporting Bugs
    - **Check existing issues**: Before submitting a bug report, please search the existing issues on GitHub to see if the bug has already been reported or addressed.
    - **Open a new issue**: If the bug hasn't been reported, open a new issue.
        - Provide a clear and descriptive title.
        - Include a detailed description of the bug, including:
            - Steps to reproduce the behavior.
            - Expected behavior.
            - Actual behavior.
        - Specify your environment details, such as Operating System, Python version, and browser version if the issue is frontend-related.

### Suggesting Enhancements/Features
    - **Open an issue**: If you have an idea for an enhancement or a new feature, please open an issue to discuss it first. This allows us to ensure that the proposed change aligns with the project's goals and to coordinate efforts.
    - Provide a clear title and a detailed description of the proposed enhancement and its potential benefits.

### Code Contributions
    1.  **Fork the Repository**: Start by forking the main repository to your own GitHub account.
    2.  **Create a Branch**: Create a new branch in your forked repository for your feature or bugfix. Use a descriptive name, for example:
        ```bash
        git checkout -b feature/your-awesome-feature
        ```
        or
        ```bash
        git checkout -b bugfix/fix-that-annoying-bug
        ```
    3.  **Development Setup**:
        - Ensure you have a working development environment. Refer to the [Development Setup Guide](docs/setup.md) for detailed instructions on setting up Python, virtual environments, and installing dependencies.
    4.  **Coding Standards**:
        - **PEP 8**: All Python code should adhere to PEP 8 style guidelines.
        - **Formatting**: Use Black for code formatting and isort for sorting imports. It's recommended to run these tools before committing:
            ```bash
            black src tests
            isort src tests
            ```
        - **Clarity**: Write clear, understandable, and maintainable code.
        - **Comments**: Add comments to your code where necessary to explain complex logic or non-obvious decisions.
    5.  **Testing**:
        - **Write Tests**: New features must be accompanied by new unit and/or integration tests. Bug fixes should ideally include a test that demonstrates the bug and verifies the fix.
        - **Run Tests**: Ensure all tests pass before submitting your contribution. Run tests using Pytest:
            ```bash
            pytest
            ```
        - **Test Coverage**: Aim to maintain or improve the existing test coverage. Check coverage with:
            ```bash
            pytest --cov=src
            ```
    6.  **Commit Messages**:
        - Follow the Conventional Commits specification for your commit messages. This helps in creating a more readable commit history and can be used for automated changelog generation.
        - Examples:
            - `feat: add user profile page`
            - `fix: correct email validation logic in registration`
            - `docs: update setup instructions`
            - `test: add tests for new password strength criteria`
            - `refactor: simplify database query in auth service`
    7.  **Pull Requests (PRs)**:
        - Push your changes to your forked repository on the branch you created.
        - Open a Pull Request (PR) from your branch to the `main` branch of the original `Flask Authentication App` repository.
        - **PR Description**: Provide a clear and descriptive title for your PR. In the description, explain the changes you've made and link to any relevant issues (e.g., "Closes #123").
        - **CI Checks**: Ensure your PR passes all automated CI checks (linting, formatting, tests, coverage) configured for the project.
        - **Code Review**: Be prepared to respond to feedback and review comments from maintainers.

## Code of Conduct
Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms.
_(Note: A `CODE_OF_CONDUCT.md` file would need to be created for this section to be fully effective.)_

## Questions?
If you have any questions about contributing, feel free to open an issue on GitHub and label it with 'question'. We'll do our best to help you out.
```
