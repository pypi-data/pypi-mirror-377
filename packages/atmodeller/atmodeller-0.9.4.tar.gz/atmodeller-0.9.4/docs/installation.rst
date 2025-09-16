.. _InstallationFile:

Installation
============

*Atmodeller* is a Python package that can be installed on a variety of platforms (e.g. Mac, Windows, Linux).

Python environment
------------------
It is recommended to install *Atmodeller* in a virtual environment, whether you proceed with a quick install or a full developer setup. This helps isolate dependencies and maintain reproducibility.

For more information, see the `Python documentation on venv <https://docs.python.org/3/library/venv.html>`_.

We recommend using a modern dependency manager such as `uv <https://docs.astral.sh/uv>`_, which offers fast installs and reproducible environments by default (See section '2b. Install *Atmodeller*' below).

1. Quick install
----------------

Use pip::

    pip install atmodeller

Downloading the source code is also recommended if you'd like access to the example notebooks in ``notebooks/``.

.. _developer_install:

2. Developer install
--------------------

2a. Fork and clone the repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you plan to contribute to *Atmodeller* or want to work independently, it's recommended to first fork the repository to your personal account or to an organisation you belong to. This gives you full control over your changes and the ability to manage your own branches.

Follow these steps:

- Visit the main repository on GitHub: https://github.com/ExPlanetology/atmodeller
- Click the **Fork** button (usually in the top-right corner of the page).
- Choose whether to fork the repository to your personal account or to an organisation account.

After forking the repository, you should **clone your fork** (not the original) to begin development.

Cloning your fork:

- Using SSH::

    git clone git@github.com:<your-account>/atmodeller.git
    cd atmodeller

- Using HTTPS::

    git clone https://github.com/<your-account>/atmodeller.git
    cd atmodeller

Replace ``<your-account>`` with your actual **GitHub username or organisation name**. You can now work on your fork independently, create branches, and make changes as needed.

To keep your fork in sync with the original repository---or to submit changes via pull requests---you can follow the instructions in the `GitHub documentation <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/configuring-a-remote-repository-for-a-fork>`_ on configuring a remote upstream. This setup allows you to fetch updates from the main repository and integrate them into your fork.

To reduce the complexity of future merges, it is **strongly recommended to keep your fork's main branch closely aligned with the upstream repository**. Avoid letting your fork diverge significantly. Submit bug fix pull requests as soon as possible. New features can be submitted at any time, as long as they are self-contained and do not break any existing infrastructure. This strategy helps ensure a smoother integration process and minimises maintenance burdens.

.. note::

    You can also clone the main repository directly without forking, but this approach provides less flexibility and does not allow you to submit pull requests unless you have write access to the main repository.

2b. Install *Atmodeller*
^^^^^^^^^^^^^^^^^^^^^^^^

To install the package, you may use a Python project/package manager such as `uv <https://docs.astral.sh/uv>`_, `poetry <https://python-poetry.org>`_, or the standard `pip <https://pip.pypa.io/en/stable/getting-started/>`_ tool. These tools manage dependencies using the project's ``pyproject.toml`` file.

Recommended: use ``uv`` or ``poetry`` or similar for reproducible and locked environments.  
Alternatively, ``pip`` can be used for simpler workflows.

Option 1: uv (recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^

This requires `uv <https://docs.astral.sh/uv>`_ to be installed.

In the directory of the source code repository (where ``pyproject.toml`` is located), run::

    uv sync

``uv`` will create a virtual environment in a ``.venv`` directory inside the source repository and install the package along with its development tools and dependencies.

To activate the virtual environment the command is different depending on your operating system:

Mac/Linux::

    source .venv/bin/activate

Windows::

    .venv\Scripts\Activate.ps1

For all operating systems you can deactivate (exit) the virtual environment by running::

    deactivate

Optional extras:

- To install documentation dependencies only::

      uv sync --extra docs

- To install everything (core + dev + docs)::

      uv sync --extra docs

.. note::

    If you're using VS Code, you may need to restart the editor for the virtual environment to be detected automatically. In some cases, additional configuration may be required---see the `official guidance 
    <https://code.visualstudio.com/docs/python/environments>`_.

    As a fallback, prefixing any command with ``uv`` will ensure it runs in the local (uv-created) environment, even if the virtual environment is not activated manually.

Option 2: pip
^^^^^^^^^^^^^

Create a virtual environment (if you haven't already), typically at the uppermost level of the source code repository.  
Make sure that the Python version used is compatible with *Atmodeller*'s requirements::

    python -m venv .venv

Activate the virtual environment::

    source .venv/bin/activate

You may use the ``-e`` option for an `editable install <https://setuptools.pypa.io/en/latest/userguide/development_mode.html>`_::

    pip install -e .

To install additional dependencies:

- For development tools::

      pip install -e .[dev]

- For documentation tools::

      pip install -e .[docs]

- For both::

      pip install -e .[dev,docs]

.. note::

    Zsh treats square brackets (`[ ]`) as globbing characters. You must quote or escape them when using `pip`. Use either of the following::

        pip install -e '.[dev]'
        # or
        pip install -e .\[dev\]

.. _DependencyNotes:

3. Dependency notes
-------------------
The dependencies in *Atmodeller* are defined in the ``pyproject.toml`` file, with special handling for JAX:

- **Apple Intel (x86_64)**: JAX is pinned to version ``0.4.38``, the last release that supports this architecture.
- **All other platforms**: JAX is pinned to the most recent tested version. The pinned version is incremented whenever *Atmodeller* is validated against a new JAX release.

This approach balances stability and reliability on older systems with the latest features and performance improvements from JAX and related libraries on supported platforms.

When working directly with the source code, it may be necessary to update the packages in your virtual environment so they match the versions specified in the latest ``pyproject.toml``. This ensures compatibility with the current development state of *Atmodeller* and avoids conflicts caused by outdated dependencies.

If you encounter issues installing *Atmodeller*, work through the usual checks:

1. Is the Python version at least the required minimum?
2. Is the correct environment activated?
3. Is a lock file preventing dependency updates? (E.g., see `uv project sync docs <https://docs.astral.sh/uv/concepts/projects/sync/>`_)

Error messages from the resolver are often helpful in diagnosing dependency conflicts. If you suspect the problem is specific to *Atmodeller*, please open an issue on GitHub.