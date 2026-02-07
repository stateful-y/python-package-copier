"""Nox sessions for the python-package-copier."""

import nox

# Require Nox version 2024.3.2 or newer to support the 'default_venv_backend' option
nox.needs_version = ">=2024.3.2"

# Set 'uv' as the default backend for creating virtual environments
nox.options.default_venv_backend = "uv|virtualenv"

# Default sessions to run when nox is called without arguments
nox.options.sessions = ["fix", "test_fast", "serve_docs"]


@nox.session(python=["3.11", "3.12", "3.13", "3.14"], venv_backend="uv")
def test(session: nox.Session) -> None:
    """Run the tests with pytest."""
    # Install dependencies
    session.run_install(
        "uv",
        "sync",
        "--group",
        "tests",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )

    # Run tests with parallel execution
    session.run(
        "pytest",
        "tests/",
        "-n",
        "auto",
        "-v",
        *session.posargs,
    )


@nox.session(python=["3.11", "3.12", "3.13", "3.14"], venv_backend="uv")
def test_fast(session: nox.Session) -> None:
    """Run fast tests (excludes slow and integration tests)."""
    # Install dependencies
    session.run_install(
        "uv",
        "sync",
        "--group",
        "tests",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )

    # Run fast tests only with parallel execution
    session.run(
        "pytest",
        "tests/",
        "-m",
        "not slow and not integration",
        "-n",
        "auto",
        "-v",
        *session.posargs,
    )


@nox.session(python=["3.11", "3.12", "3.13", "3.14"], venv_backend="uv")
def test_slow(session: nox.Session) -> None:
    """Run slow and integration tests."""
    # Install dependencies
    session.run_install(
        "uv",
        "sync",
        "--group",
        "tests",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )

    # Run slow/integration tests only with parallel execution
    session.run(
        "pytest",
        "tests/",
        "-m",
        "slow or integration",
        "-n",
        "auto",
        "-v",
        "-v",
        *session.posargs,
    )


@nox.session(venv_backend="uv")
def fix(session: nox.Session) -> None:
    """Format the code base to adhere to our styles, and complain about what we cannot do automatically."""
    # Install dependencies
    session.run_install(
        "uv",
        "sync",
        "--no-default-groups",
        "--group",
        "fix",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )

    # Run pre-commit
    session.run("pre-commit", "run", "--all-files", "--show-diff-on-failure", *session.posargs, external=True)


@nox.session(venv_backend="uv")
def lint(session: nox.Session) -> None:
    """Run linters."""
    # Install dependencies
    session.run_install(
        "uv",
        "sync",
        "--no-default-groups",
        "--group",
        "lint",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )

    # Run ruff check
    session.run("ruff", "check", "tests/", external=True)


@nox.session(venv_backend="uv")
def build_docs(session: nox.Session) -> None:
    """Build the documentation."""
    # Install dependencies
    session.run_install(
        "uv",
        "sync",
        "--group",
        "docs",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )

    # Build the docs
    session.run("mkdocs", "build", "--clean", external=True)


@nox.session(venv_backend="uv")
def serve_docs(session: nox.Session) -> None:
    """Run a development server for working on documentation."""
    # Install dependencies
    session.run_install(
        "uv",
        "sync",
        "--group",
        "docs",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )

    # Build and serve the docs
    session.run("mkdocs", "build", "--clean", external=True)
    session.log("###### Starting local server. Press Control+C to stop server ######")
    session.run("mkdocs", "serve", "-a", "localhost:8080", external=True)
