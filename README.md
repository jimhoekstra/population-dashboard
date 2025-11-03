# Population Dashboard

A simple showcase for the NewsFlash dashboard framework.

## Run It Yourself

The easiest way to run the app is with `uv`.

Start by cloning the repository.

To install the dependencies, run:

`uv sync`

Then, setup your local sqlite database by running:

`uv run newsflash setup`

When the setup has completed you can start the app by running:

`uv run newsflash dev main:app`

The `main:app` part refers to the `main.py` file and the `app` object
within that file.

To see the app in action, navigate to `http://localhost:8000` in your browser. Enjoy!