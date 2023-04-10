# GIT Database Search
Made with Django for GIT Database Search, to create, update and query the database containing all images taken by Growth India Telescope.

## Setup
Create a virtual environment and install the necessary packages from requirements.txt
- `python manage.py migrate` to create a new database.
- `python manage.py createsuperuser` will let you create a new user to use the admin panel for testing.
- `python manage.py runserver` to start a local server.

## API endpoints
- `api/images` to query images
- `api/pi` to get the list project in charges (PI)
- `api/pid` to get a list of project IDs
- `api/propnums` to get a list of proposal numbers
- `api/api-token/` to get JWT token (authentication)
- `api/api-token-refresh/` to refresh JWT token (authentication)

All endpoints require authentication
