# Election Management System

A modern, efficient, and interactive election management system built with Django. This system facilitates the management of candidates, polling stations, votes, and election results with a responsive and user-friendly interface.

## Features
- **Candidate Management**: Add, edit, and delete candidates with party and image details.
- **Polling Station Management**: Manage polling stations and registered voters.
- **Vote Management**: Record, update, and delete votes for candidates at polling stations.
- **Dashboard**: Visualize results with interactive charts and summary statistics.
- **Authentication**: Secure login with constituency-specific credentials.

## Technologies Used
- **Backend**: Django, Python
- **Frontend**: Bootstrap, HTML5, CSS3
- **Database**: MySQL
- **Version Control**: Git & GitHub

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/mmanueljoe/election_system.git
   cd election_system
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Linux/Mac
   venv\Scripts\activate     # For Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**:
   Update the `DATABASES` settings in `settings.py` and run:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

6. **Access the app**:
   Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

## Deployment
Follow the [deployment guide](https://docs.djangoproject.com/en/stable/howto/deployment/) to deploy the project on platforms like Heroku, PythonAnywhere, or any cloud provider.

## License
This project is licensed under the [MIT License](LICENSE).

## Acknowledgments
- Built with ❤️ using Django and Bootstrap.
