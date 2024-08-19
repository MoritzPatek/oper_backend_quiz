# Project Setup Documentation

This guide will walk you through setting up the Quiz Management API project.

## Setup Steps

### 1. Clone the Repository

Clone the GitHub repository to your local machine:

bash
```
git clone https://github.com/MoritzPatek/oper_backend_quiz.git
```

### 2. Navigate to the Project Directory

Move into the project directory:

bash
```
cd oper_backend_quiz
cd backend-engineering-assessment
```
### 3. Start the Application with Docker

Run the following command to start the application:

bash
```
docker compose up
```
Docker will:

- Install all necessary dependencies.
- Initialize the database and populate it with standard data such as user roles and quiz statuses.
- Create two initial users:
  - **Creator**: 
    - **Username**: Moritz
    - **Password**: Patek
  - **Participant**:
    - **Username**: Oper
    - **Password**: Oper

### 4. Access the Admin Panel

Once the application is running, access the Django admin panel:

- **URL**: http://localhost:8000/admin
- **Admin User**: Moritz
- **Password**: Patek

Log in with the above credentials to manage the application's data.

## Notes

- The setup process is fully automated by Docker, including dependency installation and database initialization.
- The pre-created users allow immediate testing and use of the application.

## Next Steps

Navigate to the **example_usage.md** file to get a walk through of the process.
