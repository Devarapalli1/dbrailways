# Railway Management System

This project is a Railway Management System implemented in Python Flask with a MySQL database backend.

---

## Prerequisites

- **Python** (version 3.7+)
- **MySQL Server**
- **pip** (Python package installer)

---


## Setup Instructions
1. Navigate to the project directory:
   ```bash
   cd <project-directory>
2. Set up and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

3. Install the required Python packages:
```bash
pip install -r requirements.txt
```

4. Configure the database connection:
   Open `database/config.py` file and update the `Config` class with your MySQL server details:

Ensure you have the following SQL files in the config directory:
- DDL.sql: Contains the database schema
- smallRelationsInsertFile.sql: Contains initial data to seed the database

### Setting up the initial database
Navigate to the project directory in your terminal.
Run the main Python script:

```python database/setup.py```

### Finally Start the application
```python app.py```