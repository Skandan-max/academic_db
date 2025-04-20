# Academic_DB
1. Ensure MySQL Server (or MariaDB) is installed and running.

2. Install mysql-connector-python:
    pip install mysql-connector-python

3. Make sure tkinter is available (usually comes pre-installed).
   If not, install it based on your OS:
    - Fedora: sudo dnf install python3-tkinter
    - Ubuntu/Debian: sudo apt-get install python3-tk
    - macOS (Homebrew): brew install python-tk

4. Update the MySQL credentials int he first few lines in the program to match your setup.

5. Ensure your MySQL database (`academic_databse`) is already set up with the required tables.

6. Run this file :
    python acadDB.py
