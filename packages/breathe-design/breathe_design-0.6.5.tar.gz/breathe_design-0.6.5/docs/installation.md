# <h1 id="installation">Installation</h1>

## Prerequisites

Python 3.11 or later is required to use the `breathe_design` package.

## Installation steps

- Open your terminal or command prompt.
- Navigate to the directory where you want to create the virtual environment.
- Run the following command to create the virtual environment:

  ```bash
  python -m venv myvenv
  ```

  Replace `myvenv` with the desired name for your virtual environment.

- Activate the virtual environment:
  - On **Windows**:
    ```cmd
    myvenv\Scripts\activate
    ```
  - On **macOS/Linux**:
    ```bash
    source myvenv/bin/activate
    ```
    After activating the virtual environment, you'll see `(myenv)` in your terminal prompt to indicate that the environment is active.
- Install the `breathe_design` package in the virtual environment:

  ```
  pip install breathe_design
  ```

## Verifying your installation

Once the installation is complete, you can verify that the package is installed correctly by running the following command in your terminal:

```
python -m pip show breathe_design
```

This will display information about the `breathe_design` package, including its version number.

You can also import the package in a Python script to ensure that it's working correctly:

```python
import breathe_design
```

If there are no errors, the package is imported successfully.
Now you can start using the breathe_design package in your Python projects!
