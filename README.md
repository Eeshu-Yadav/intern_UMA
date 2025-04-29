# Action Suggester API

A Django REST API that analyzes text messages using OpenAI's GPT model and suggests relevant actions based on the detected tone and intent.

## Features

- Text analysis using OpenAI GPT-3.5-turbo
- Action suggestions based on tone and intent
- PostgreSQL database logging
- RESTful endpoint with JSON responses

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/action-suggester-api.git
cd action-suggester-api
```

### 2. Set up virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your_openai_api_key_here
DB_NAME=action_suggester
DB_USER=your_db_username
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Start the development server

```bash
python manage.py runserver
```

## Example Output

![API Response Example 1](output/Screenshot%202025-04-29%20125323.png)

![API Response Example 2](output/Screenshot%202025-04-29%20134850.png)

![API Response Example 3](output/Screenshot%202025-04-29%20134937.png)

![Postgres DB](output/Screenshot%202025-04-29%20135308.png)