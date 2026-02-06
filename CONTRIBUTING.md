# Contributing to DataGate

Thank you for your interest in contributing to DataGate! We welcome contributions to make this data platform better.

## How to Contribute

### Reporting Bugs

If you find a bug, please create a GitHub Issue including:
1.  **Steps to reproduce**: How we can see the error ourselves.
2.  **Expected behavior**: What you expected to happen.
3.  **Actual behavior**: What actually happened.
4.  **Screenshots/Logs**: Any visual or text aid.

### Feature Requests

Have an idea? Open an Issue tagged as `enhancement`. Describe the feature and why it would be useful.

### Pull Requests

1.  **Fork the repository**.
2.  **Create a branch**: `git checkout -b feature/my-new-feature` or `fix/my-bug-fix`.
3.  **Commit your changes**: `git commit -m 'feat: Add some feature'`.
    -   Please follow [Conventional Commits](https://www.conventionalcommits.org/).
4.  **Push to the branch**: `git push origin feature/my-new-feature`.
5.  **Open a Pull Request**.

### Development Guidelines

-   **Code Style**: Follow standard Python (PEP 8) and Shell scripting best practices.
-   **Documentation**: Update READMEs or docstrings if you change functionality.
-   **Testing**: Ensure that your changes do not break existing platform components. Docker containers should build and start successfully.

## Architecture Decisions

If you are proposing a major architectural change (e.g., swapping a core component like Trino), please open an Issue for discussion first.
