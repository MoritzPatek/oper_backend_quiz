# Quiz Management API - Detailed Function Documentation

This section provides a detailed overview of the functions available in the Quiz Management API, including their purpose, behavior, and any specific conditions or logic applied.

## User Management

### `create_user`

- **Method**: `POST`
- **Description**: This function creates a new user in the system.
- **Behavior**: 
  - It validates the user data against the `UserSerializer`.
  - If the data is valid, the user is saved to the database.
  - Returns the created user's data with a `201 Created` status on success, or validation errors with a `400 Bad Request` status on failure.

## Quiz Management

### `create_quiz`

- **Method**: `POST`
- **Description**: Creates a new quiz, but only if the user has the `Creator` role.
- **Behavior**:
  - Validates the quiz data using the `QuizSerializer`.
  - Saves the quiz with the current user as the creator.
  - Returns the created quiz data with a `201 Created` status on success, or validation errors with a `400 Bad Request` status on failure.

### `set_quiz_status`

- **Method**: `POST`
- **Description**: Updates the status of a quiz, such as setting it to "Published" or "Draft".
- **Behavior**:
  - The function checks if the requested status exists in the `QuizStatus` model.
  - If setting the status to "Published", it ensures that all questions in the quiz have at least one answer. If any questions are missing answers, it returns an error with a `400 Bad Request` status.
  - Updates the quiz status if all conditions are met and returns a success message.

### `get_user_quizzes`

- **Method**: `GET`
- **Description**: Retrieves all quizzes created by the current user.
- **Behavior**: 
  - Filters quizzes by the currently authenticated user.
  - Returns a list of quizzes in JSON format.

## Question and Answer Management

### `create_question`

- **Method**: `POST`
- **Description**: Creates a new question for a specific quiz, requiring the user to have the `Creator` role.
- **Behavior**:
  - Validates the question data using the `QuestionSerializer`.
  - Saves the question to the associated quiz.
  - Returns the created question data on success or validation errors on failure.

### `create_answer`

- **Method**: `POST`
- **Description**: Creates a new answer for a specific question within a quiz.
- **Behavior**:
  - Verifies that the current user is the creator of the quiz to which the question belongs.
  - Validates and saves the answer if the user has the necessary permissions.
  - Returns the created answer data on success, or an error if the user does not have permission.

### `get_questions_by_quiz`

- **Method**: `GET`
- **Description**: Retrieves all questions associated with a specific quiz.
- **Behavior**:
  - Filters questions by the provided quiz ID.
  - Returns a list of questions associated with the quiz in JSON format.

### `get_answers_by_question`

- **Method**: `GET`
- **Description**: Retrieves all possible answers for a specific question.
- **Behavior**:
  - Validates that the quiz containing the question is published.
  - Ensures that the current user has access to the quiz.
  - Returns a list of answers for the specified question.

## User Quiz Progress

### `create_answered_question`

- **Method**: `POST`
- **Description**: Records a user's answer to a specific question within a quiz.
- **Behavior**:
  - Ensures that the question and answer exist.
  - Checks if the user has access to the quiz.
  - Verifies whether the question has already been answered; if it has, the existing answer is returned.
  - If not, a new answered question record is created, and the user's progress is updated.
  - Returns the newly recorded answer on success.

### `set_accepted_status`

- **Method**: `POST`
- **Description**: Allows a user to accept or reject an assigned quiz.
- **Behavior**:
  - Checks if the quiz exists and if the user is assigned to it.
  - If the quiz is accepted, a `UserQuizProgress` entry is created for the user.
  - If rejected, any existing progress for the quiz is deleted.
  - Updates the `accepted` status of the assigned quiz and returns a success message.

### `get_participant_quiz_progress`

- **Method**: `GET`
- **Description**: Retrieves the current progress of the user for a specific quiz.
- **Behavior**:
  - Calculates how many questions have been answered and the correctness of the answers.
  - Summarizes the quiz progress, including the number of questions answered, total questions, and the number of correct answers.
  - Returns this progress summary in JSON format.

### `get_next_question`

- **Method**: `GET`
- **Description**: Retrieves the next unanswered question for a user in a specific quiz.
- **Behavior**:
  - Finds the last answered question for the user and determines the next one in sequence.
  - If all questions have been answered, it marks the quiz as completed.
  - Returns the next question to be answered or a completion message if the quiz is finished.

## Role Management

### `get_available_user_roles`

- **Method**: `GET`
- **Description**: Retrieves all roles that can be assigned to users.
- **Behavior**:
  - Returns a list of roles in JSON format.

### `get_all_users`

- **Method**: `GET`
- **Description**: Retrieves a list of all users in the system.
- **Behavior**:
  - Returns user data for all users in the system, only accessible by users with the `Creator` role.

## Assigned Quizzes

### `set_quiz_to_user`

- **Method**: `POST`
- **Description**: Assigns a quiz to a specific user, requiring the `Creator` role.
- **Behavior**:
  - Validates the existence of both the quiz and the user.
  - Ensures the quiz is not in "Draft" status.
  - Assigns the quiz to the user unless it has already been assigned.
  - Returns the assignment data on success or an error if the quiz is already assigned.

### `get_assigned_quizzes`

- **Method**: `GET`
- **Description**: Retrieves all quizzes that are assigned to the current user.
- **Behavior**:
  - Filters quizzes by the current user and returns the list of assigned quizzes in JSON format.

## Score and Progress Tracking

### `get_quiz_scores`

- **Method**: `GET`
- **Description**: Retrieves scores for all participants in a specific quiz.
- **Behavior**:
  - Verifies that the current user is the creator of the quiz.
  - Summarizes the progress and scores for each participant in the quiz.
  - Returns this data in JSON format.

## Utility Endpoints

### `get_quiz_statuses`

- **Method**: `GET`
- **Description**: Retrieves all possible statuses for a quiz.
- **Behavior**:
  - Returns a list of quiz statuses in JSON format.

Each of these functions implements specific logic to handle various aspects of quiz management, ensuring data integrity and enforcing user permissions where necessary. For a complete API reference and testing, refer to the Swagger documentation available at `[url:port]/swagger`.
