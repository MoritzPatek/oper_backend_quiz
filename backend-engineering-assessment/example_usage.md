# Step-by-Step API Usage Guide

This guide provides step-by-step instructions for interacting with the API using Postman. All API endpoints are also documented with Swagger, accessible via http://localhost:8000/swagger.

## Step 1: User Login

The first step is to log in as a user to obtain an authentication token. You can use any tool for testing, such as Postman. 

### Request

- **URL:** http://localhost:8000/auth/
- **Method:** POST
- **Content-Type:** application/json
- **Body:** 

```json
{
  "username": "Moritz",
  "password": "Patek"
}
```

### Response

This request will return a token in the response, which you'll need to include in the headers for all subsequent requests.

### Example Response

```json
{
  "token": "your-authentication-token"
}
```

### Notes

- There are two users created by default when the app is started. For this example, you will log in as the **Creator** user with the username Moritz and password Patek.
- Remember to use this token for authorization in all future API requests.

## Step 2: Add Authorization Token and Create a New Quiz

Before making any further requests, you'll need to include the authentication token in your request headers.

### Adding the Token to Headers

- **Key:** Authorization
- **Value:** Token `<token>`

Replace `<token>` with the token you received in the previous step.

### Creating a New Quiz

Now that the token is set in the headers, you can create a new quiz.

### Request

- **URL:** http://localhost:8000/quiz/create_quiz/ 
- **Method:** POST
- **Content-Type:** application/json
- **Body:** 

```json
{
  "title": "Example Quiz",
  "description": "Example Description"
}
```

### Response

Upon a successful request, you will receive a response like this:

```json
{
  "id": 1,
  "title": "Example Quiz",
  "description": "Example Description"
}
```

## Step 3: Create a New Question for the Quiz

If you've forgotten which quizzes your user has created, you can retrieve them first.

### Retrieve User's Quizzes

To get a list of quizzes that the user has created, make the following request:

### Request

- **URL:** http://localhost:8000/quiz/get_user_quizzes/
- **Method:** GET
- **Authorization:** Token `<token>` (Include this in the headers)

### Response

The response will be a list of quizzes created by the user:

```json
[
  {
    "id": 1,
    "title": "Example Quiz",
    "description": "Example Description"
  }
]
```

### Create a Question for the Quiz

Now, with the quiz ID in hand, you can create a new question for the quiz.

### Request

- **URL:** http://localhost:8000/quiz/create_question/
- **Method:** POST
- **Content-Type:** application/json
- **Authorization:** Token `<token>` (Include this in the headers)
- **Body:** 

```json
{
  "question": "Example Question",
  "quiz_id": 1
}
```

### Response

Upon a successful request, you will receive a response like this:

```json
{
  "id": 1,
  "question": "Example Question"
}
```


## Step 4: Create Answers for the Question

### Retrieve Questions for the Quiz

If you've forgotten which questions you've already created for the quiz, you can retrieve them with the following request:

### Request

- **URL:** http://localhost:8000/quiz/get_questions_by_quiz/?quiz_id=1
- **Method:** GET
- **Authorization:** Token `<token>` (Include this in the headers)

### Response

The response will be a list of questions for the specified quiz:

```json
[
  {
    "id": 1,
    "question": "Example Question"
  }
]
```

### Create an Answer for the Question

Now, with the question ID in hand, you can create a new answer for the question.

### Request

- **URL:** http://localhost:8000/quiz/create_answer/
- **Method:** POST
- **Content-Type:** application/json
- **Authorization:** Token `<token>` (Include this in the headers)
- **Body:** 

```json
{
  "answer": "Example Answer True",
  "is_correct": true,
  "question_id": 1
}
```
### Response

Upon a successful request, you will receive a response like this:

```json
{
  "id": 1,
  "answer": "Example Answer True",
  "is_correct": true,
  "question_id": 1
}
```

## Step 5: Set the Quiz Status to Published

Before assigning a user to a quiz, you need to ensure that the quiz status is set to "Published". If you're unsure what statuses are available, you can retrieve them first.

### Retrieve Quiz Statuses

To get a list of available quiz statuses, make the following request:

### Request

- **URL:** http://localhost:8000/quiz/get_quiz_statuses/
- **Method:** GET
- **Authorization:** Token `<token>` (Include this in the headers)

### Response

The response will be a list of possible quiz statuses:

```json
[
  {
    "id": 1,
    "name": "Draft",
    "description": "Quiz is still being created"
  },
  {
    "id": 2,
    "name": "Published",
    "description": "Quiz is published and available for participants"
  },
  {
    "id": 3,
    "name": "Closed",
    "description": "Quiz is closed and no longer available"
  }
]
```
### Set the Quiz Status to Published

Once you know the available statuses, you can set the status of the quiz to "Published" using the following request:

### Request

- **URL:** http://localhost:8000/quiz/set_quiz_status/
- **Method:** POST
- **Content-Type:** application/json
- **Authorization:** Token `<token>` (Include this in the headers)
- **Body:** 

```json
{
  "quiz_id": 1,
  "status": "Published"
}
```

### Response

Upon a successful request, you will receive a response like this:

```json
{
  "message": "Quiz status updated successfully."
}
```

## Step 6: Inviting a User to a Quiz

To invite a user to participate in a quiz, you first need to know the list of users available.

### Retrieve All Users

You can get a list of all users by making the following request:

### Request

- **URL:** http://localhost:8000/quiz/get_all_users/
- **Method:** GET
- **Authorization:** Token `<token>` (Include this in the headers)

### Response

The response will be a list of users, including their IDs, usernames, emails, and roles:

```json
[
  {
    "id": 1,
    "username": "Moritz",
    "email": "patekmoritz@yahoo.at",
    "role_name": "Creator"
  },
  {
    "id": 2,
    "username": "Oper",
    "email": "oper@example.com",
    "role_name": "Participant"
  }
]
```
### Invite a User to the Quiz

With the user ID and quiz ID in hand, you can now invite the user to the quiz using the following request:

### Request

- **URL:** http://localhost:8000/quiz/set_quiz_to_user/
- **Method:** POST
- **Content-Type:** application/json
- **Authorization:** Token `<token>` (Include this in the headers)
- **Body:** 

```json
{
  "quiz_id": 1,
  "user_id": 2
}
```

### Response

Upon a successful request, you will receive a response like this:
```json
{
  "id": 1,
  "accepted": false,
  "quiz_id": 1,
  "user_id": 2
}
```

## Step 7: Accepting a Quiz Invitation as a Participant

Now that the work with the Creator user is done, you can log in with the Participant user to accept the quiz invitation.

### Login as the Participant

Follow the same login process described in Step 1, but use the Participant's credentials:

- **Username:** Oper
- **Password:** Oper

### Check Assigned Quizzes

To see what quizzes the Participant user has been assigned to, make the following request:

### Request

- **URL:** http://localhost:8000/quiz/get_assigned_quizzes/
- **Method:** GET
- **Authorization:** Token `<token>` (Include this in the headers)

### Response

The response will be a list of quizzes that the user is assigned to:

```json
[
  {
    "id": 1,
    "accepted": false,
    "quiz_id": 1,
    "user_id": 2
  }
]
```

### Accept the Quiz Invitation

With the quiz ID in hand, the Participant can accept the quiz invitation by making the following request:

### Request

- **URL:** http://localhost:8000/quiz/set_accepted_status/
- **Method:** POST
- **Content-Type:** application/json
- **Authorization:** Token `<token>` (Include this in the headers)
- **Body:** 

```json
{
  "quiz_id": 1,
  "accepted": true
}
```

### Response

Upon a successful request, you will receive a response like this:

```json
{
  "message": "Accepted status updated successfully."
}
```

## Step 8: Retrieving and Answering Questions in a Quiz

After accepting a quiz invitation, the Participant user can now proceed to retrieve and answer questions in the quiz.

### Retrieve the Next Question

To get the next question in the quiz, make the following request:

### Request

- **URL:** http://localhost:8000/quiz/get_next_question/?quiz_id=1
- **Method:** GET
- **Authorization:** Token `<token>` (Include this in the headers)

### Response

The response will contain the next question in the quiz:

```json
{
  "id": 1,
  "question": "Example Question"
}
```

### Retrieve Answers for the Question

Once you have the question ID, you can retrieve all the answers for that question by making the following request:

### Request

- **URL:** http://localhost:8000/quiz/get_answers_by_question/?question_id=1
- **Method:** GET
- **Authorization:** Token `<token>` (Include this in the headers)

### Response

The response will contain a list of answers for the question:

```json
[
  {
    "id": 1,
    "answer": "Example Answer True",
    "is_correct": true,
    "question_id": 1
  }
]
```

## Step 9: Answering a Question in the Quiz

After retrieving a question and its possible answers, the Participant user can now submit their answer.

### Answer the Question

To submit an answer for a question, make the following request:

### Request

- **URL:** http://localhost:8000/quiz/create_answered_question/
- **Method:** POST
- **Content-Type:** application/json
- **Authorization:** Token `<token>` (Include this in the headers)
- **Body:** 
```json
{
  "question_id": 1,
  "answer_id": 1
}
```

### Response

The response will contain details about the answered question, including whether the selected answer was correct:

```json
{
  "id": 1,
  "user_progress_id": 1,
  "question_id": 1,
  "answer_id": 1,
  "is_correct": true
}
```

## Step 10: Completing the Quiz and Checking Progress

### Retrieve More Questions

After answering a question, you can continue to retrieve the next question by calling the `get_next_question` function again. If there are no more questions left, you will receive a message indicating that the quiz is complete.

### Example Response When Quiz is Complete

```json
{
  "message": "Quiz completed."
}
```

### Check Participant's Quiz Progress

To check the progress of the quiz you took as a Participant, you can make the following request:

### Request

- **URL:** http://localhost:8000/quiz/get_participant_quiz_progress/?quiz_id=1
- **Method:** GET
- **Authorization:** Token `<token>` (Include this in the headers)

### Response

The response will provide details about your progress in the quiz:

```json
{
  "quiz": "Example Quiz",
  "completed": true,
  "questions_answered": 1,
  "total_questions": 1,
  "correct_answers": 1,
  "total_answers": 1
}
```

### Check Quiz Scores as the Creator

As the Creator, you can check the progress and scores of all users for a given quiz by making the following request:

### Request

- **URL:** http://localhost:8000/quiz/get_quiz_scores/?quiz_id=1
- **Method:** GET
- **Authorization:** Token `<token>` (Include this in the headers)

### Response

The response will be a list of users who have taken the quiz, along with their scores and completion status:
```json
[
  {
    "user": "Oper",
    "completed": true,
    "questions_answered": 1,
    "total_questions": 1,
    "correct_answers": 1,
    "total_answers": 1
  }
]
```