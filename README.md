# Relationship Survey App

A web application that helps people understand their relationship dynamics through a structured survey. The app allows two people to take the survey independently and then compares their answers to find common ground and potential areas for growth.

## Features

- Two-part survey structure (Current Status and Future Wishes)
- Real-time progress tracking
- Skip option for sensitive questions
- Shareable results with unique links
- Modern, responsive UI with theme support
- Secure answer comparison

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Technology Stack

- Backend: Python FastAPI
- Frontend: HTML, TailwindCSS
- Database: SQLite (for development)

## Project Structure

- `main.py`: Main application file
- `questions.json`: Survey questions and choices
- `templates/`: HTML templates
  - `base.html`: Base template with common elements
  - `form.html`: Survey form template
  - `result.html`: Results display template
  - `share.html`: Share link template
  - `waiting.html`: Waiting page template

## License

MIT License 