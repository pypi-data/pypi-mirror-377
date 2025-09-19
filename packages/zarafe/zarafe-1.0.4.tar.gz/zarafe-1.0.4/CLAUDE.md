# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Git Commit Guidelines
- NEVER mention AI generation in git commit messages (no "Generated with AI", "AI-assisted", etc.)

## Development Environment

- **Python Version**: Requires Python ≥3.9
- **Virtual Environment**: Uses uv for dependency management

## Commit Message Style

Follow the conventional commit format used in this repository:
- **fix**: Bug fixes (e.g., "fix: handle invalid reflection geometry instead of crashing")
- **feature**: New features (e.g., "feature: calculate the 3D position of the fovea on the retinal surface")  
- **enhance**: Improvements to existing functionality (e.g., "enhance: better plot")
- **refactor**: Code restructuring without changing functionality (e.g., "refactor: making the code more pythonic")
- **chore**: Maintenance tasks (e.g., "chore: better error message")
- **add**: Adding new components (e.g., "add: step by step angle kappa calculation")

Keep messages concise but descriptive. Focus on what the change accomplishes rather than how it was implemented.

## Code Comments Guidelines

When writing code comments, follow the same principle as good commit messages - only write them when the code needs explanation. Only add comments when the logic is non-trivial, has business context, or needs explanation that isn't obvious from reading the code. Keep comments concise and only explain what actually needs explaining.
It's ok to have comments for block of the code so we know this section is for that and finding things becomes easear. 

## Python Import Guidelines

- **NEVER import modules in the middle of functions or code blocks**
- **ALL imports must be at the top level of the file** (after module docstring)
- Group imports in standard order: standard library, third-party packages, local modules
- Use absolute imports when possible
- Avoid importing inside functions unless absolutely necessary for lazy loading or circular imports
