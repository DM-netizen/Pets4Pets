# Pets4Pets - A Flask-Based Social Media Platform for Pet Enthusiasts

## Overview

Pets4Pets is an innovative social media web application designed for pet owners to connect, share updates, and discover fellow pet enthusiasts. This platform leverages Object-Oriented Design principles, a real database (SQLite), and modern web technologies to deliver a seamless user experience.

---

## Features

* **User Authentication:** Secure user registration, login, and logout functionalities.
* **Pet Profile Management:** Users can add pet details (name, type, age, breed, and description) during signup.
* **Dynamic Home Feed:** Users can view real-time posts from the people they follow.
* **Post Updates:** Users can share updates/posts about their pets.
* **Advanced Pet Search:** Search functionality based on pet type, displaying matching pet owners.
* **Follow/Unfollow System:** Option to follow/unfollow pet owners directly from search results.
* **Profile Page:** Displays user information, pet details, follower and following lists.
* **Flash Messaging:** Informative messages for user actions like following/unfollowing.
* **Dynamic Feed Refresh:** Auto-updates the feed every 10 seconds using JavaScript.
* **Modern UI:** Responsive and intuitive interface powered by Bootstrap 5.
* **Add Pet Feature:** Users can add more pets to their profile through a dedicated form in the navigation bar.

---

## Technology Stack

* **Backend:** Python, Flask, SQLAlchemy (ORM)
* **Frontend:** HTML5, CSS3 (Bootstrap 5), JavaScript (AJAX)
* **Database:** SQLite

---

## Project Structure

```
Pets4Pets/
│
├── app.py               # Flask backend logic
├── pets4pets.db         # SQLite database (excluded via .gitignore)
├── requirements.txt     # Python package dependencies
├── .gitignore           # Git ignore rules
│
├── /templates/          # HTML templates (Jinja2)
│   ├── base.html
│   ├── home.html
│   ├── login.html
│   ├── signup.html
│   ├── profile.html
│   └── search.html
│
├── /static/             # Static files
│   ├── main.js          # JavaScript for dynamic feed refresh
│
└── README.md            # Project documentation
```

---

## Setup Instructions

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/your-username/Pets4Pets.git
   cd Pets4Pets
   ```

2. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the Database:**

   ```bash
   python
   >>> from app import db
   >>> db.create_all()
   >>> exit()
   ```

4. **Run the Application:**

   ```bash
   python app.py
   ```

5. **Visit:** [http://127.0.0.1:5000](http://127.0.0.1:5000)

