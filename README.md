# Quizy

Quizy is a web-based application designed to create, manage, and participate in quizzes. It provides features such as user authentication, quiz creation, leaderboard tracking, and performance analysis.

## Features

- User authentication and profile management.
- Create and manage quizzes.
- View available quizzes and participate.
- Track performance and results.
- Leaderboard for competitive ranking.

## Technologies Used

- **Backend**: Django (Python)
- **Frontend**: HTML, CSS, JavaScript, TailwindCSS
- **Database**: SQLite (default)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Quizy
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Apply migrations:
   ```bash
   python manage.py migrate
   ```

4. Run the development server:
   ```bash
   python manage.py runserver
   ```

5. Access the application at `http://127.0.0.1:8000`.

## Project Structure

- `core`: Contains the main application logic and homepage.
- `quiz`: Handles quiz-related functionality.
- `account`: Manages user accounts and authentication.
- `static`: Contains static files like CSS, JavaScript, and images.
- `templates`: Contains HTML templates for the application.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.


