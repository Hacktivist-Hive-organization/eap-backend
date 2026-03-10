# File Path Header Script

## Overview

This script automatically inserts a file path comment at the top of Python files.
The path is written relative to the project root.

Example result:

# app/services/auth_service.py

import asyncio
import time

The script removes existing path-like header comments at the beginning of the file before inserting the updated one.

This keeps file headers consistent across the project.


## Features

- Adds a file path comment as the first line of Python files
- The path is always relative to the project root
- Removes existing path-like comments at the beginning of the file
- Removes leading empty lines before inserting the header
- Safe for repeated execution
- Supports processing a folder or a single file
- Prevents concurrent execution using a lock file
- Skips common directories such as `.venv`, `.git`, and `__pycache__`


## Script Location

Place the script inside the project, for example:

scripts/add_file_path_header.py

Run the script from the project root directory.

Example project structure:

project_root/
│
├─ app/
├─ tests/
├─ scripts/
│  └─ add_file_path_header.py
│
└─ pyproject.toml


## Basic Usage

Run the script from the project root.

Default behavior processes the `app` directory.

python scripts/add_file_path_header.py


## Processing a Specific Directory

You can pass a directory path relative to the project root.

Example:

python scripts/add_file_path_header.py tests

python scripts/add_file_path_header.py tests/integration


## Processing a Single File

You can also pass a specific Python file.

Example:

python scripts/add_file_path_header.py tests/integration/auth/test_auth_email_verification.py


## Example Transformation

Before:

from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship


After running the script:

# app/models/db_request_type.py

from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship


If an old header already exists, it will be replaced.

Before:

# old/path/file.py

from sqlalchemy import Column


After:

# app/models/db_request_type.py

from sqlalchemy import Column


## Lock Protection

To prevent concurrent execution, the script creates a lock file:

.add_path_header.lock

If the script is already running, another execution will exit with a message:

Script already running. Exiting.

If the script crashes unexpectedly, you may need to remove the lock file manually.


Linux / macOS:

rm .add_path_header.lock


Windows:

del .add_path_header.lock


## Notes

- The script processes only `.py` files.
- File paths are always written relative to the project root.
- The script should always be executed from the root directory of the project.
- The script is safe to run multiple times.
- Existing headers that look like file paths are automatically removed and replaced.