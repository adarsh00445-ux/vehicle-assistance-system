# 🚗 Vehicle Assistance System

A web-based Vehicle Assistance System developed using **Python, Flask, HTML, CSS, JavaScript, and SQLite**. The application is designed to help vehicle owners access breakdown assistance, connect with mechanics, and manage service bookings through a centralized platform.

---

## 📌 Project Overview

Vehicle breakdowns can happen unexpectedly, leaving vehicle owners struggling to find nearby mechanics and reliable assistance. The Vehicle Assistance System aims to simplify this process by providing an online platform for requesting vehicle assistance and managing service bookings.

The application follows a modular architecture with separate functionalities for users, staff, and administrators. It provides a structured way to handle assistance requests and manage booking-related activities.

---

## ✨ Key Features

### 👤 User Module

* User registration and login.
* OTP-based verification, where configured.
* User dashboard.
* Request vehicle assistance from mechanics.
* Book mechanic services.
* View and manage bookings.
* Access booking information and status.

### 🛠️ Staff Module

* Staff login and authentication.
* Staff dashboard.
* View and manage assigned jobs.
* Access booking details.
* Update service-related information.

### 🔐 Admin Module

* Administrator login.
* Admin dashboard.
* Staff registration and management.
* View staff information.
* Manage and review bookings.
* Access service history and booking statistics.

### 🌐 General Features

* User-friendly web interface.
* Separate interfaces for users, staff, and administrators.
* Database integration.
* Organized application routes.
* Reusable HTML templates.
* Form validation and error handling.

---

## 🛠️ Technology Stack

| Technology | Purpose                        |
| ---------- | ------------------------------ |
| Python     | Backend programming            |
| Flask      | Web application framework      |
| SQLite     | Database management            |
| HTML5      | Page structure                 |
| CSS3       | Styling and responsive layouts |
| JavaScript | Client-side interactivity      |
| Jinja2     | Dynamic HTML templates         |

---

## 📂 Project Structure

```text
vehicle_assistance/
│
├── modules/
│
├── routes/
│   ├── __init__.py
│   ├── admin_routes.py
│   ├── staff_routes.py
│   └── user_routes.py
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
│   ├── admin/
│   ├── staff/
│   ├── user/
│   ├── _auth_macros.html
│   ├── base.html
│   ├── error.html
│   └── home.html
│
├── app.py
├── config.py
├── create_admin.py
├── quickstart.py
├── requirements.txt
├── setup_database.sql
├── test_setup.py
├── run.bat
├── .gitignore
└── README.md
```

*The structure above is illustrative. Keep the README aligned with the actual files in your repository.*

---

## ⚙️ Installation and Setup

Follow these steps to run the application locally.

### 1. Clone the Repository

```bash
git clone https://github.com/adarsh00445-ux/vehicle-assistance-system.git
```

Navigate to the project folder:

```bash
cd vehicle-assistance-system/vehicle_assistance
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

**Windows:**

```powershell
venv\Scripts\activate
```

**Linux or macOS:**

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure the Database

Review `config.py` and `setup_database.sql` to understand the database configuration.

Initialize the database using the method supported by your application. Ensure the required tables are created before starting the application.

### 6. Run the Application

```bash
python app.py
```

Open the local URL displayed in the terminal. For example:

```text
http://127.0.0.1:5000
```

---

## 📸 Application Screenshots

Add screenshots of your actual application here.

Suggested screenshots:

* Home page
* User registration and login
* User dashboard
* Mechanic booking page
* Booking management page
* Staff dashboard
* Administrator dashboard

Example:

```markdown
![Vehicle Assistance Home Page](screenshots/home.png)
```

Create a `screenshots` folder and replace the example path with your actual screenshot files.

---

## 🎯 Project Objectives

* Develop a web-based vehicle breakdown assistance platform.
* Simplify the process of requesting mechanic services.
* Provide a centralized system for managing service bookings.
* Implement separate functionalities for users, staff, and administrators.
* Integrate a database for storing and managing application information.
* Apply Python and Flask concepts to a real-world problem.
* Develop a modular and maintainable web application.

---

## 🔮 Future Enhancements

* GPS-based identification of nearby mechanics.
* Real-time location tracking during assistance requests.
* Online payment integration.
* SMS and email notifications for booking updates.
* Advanced search and filtering for mechanics.
* AI-powered chatbot for basic vehicle troubleshooting.
* Improved mobile responsiveness.

*These are proposed enhancements, not claims about existing functionality.*

---

## 👨‍💻 Author

**Adarsh Shinde**

GitHub: [adarsh00445-ux](https://github.com/adarsh00445-ux)

Project: [Vehicle Assistance System](https://github.com/adarsh00445-ux/vehicle-assistance-system)

---

## 📄 License

This project was developed for academic and educational purposes as a final-year project.
