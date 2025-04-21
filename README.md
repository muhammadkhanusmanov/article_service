# article_service

## API Documentation

### Authentication Endpoints

#### 1. User Registration
- **URL**: `/api/auth/register/`
- **Method**: `POST`
- **Payload**:
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string",
    "first_name": "string",
    "last_name": "string",
    "phone": "string"
  }
  ```
- **Purpose**: Register a new user.

#### 2. User Login
- **URL**: `/api/auth/login/`
- **Method**: `POST`
- **Payload**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Purpose**: Authenticate a user and return a token.

#### 3. User Logout
- **URL**: `/api/auth/logout/`
- **Method**: `POST`
- **Headers**: `Authorization: Token <user_token>`
- **Purpose**: Logout the authenticated user.

#### 4. User Profile
- **URL**: `/api/profile/`
- **Methods**:
  - `GET`: Retrieve the authenticated user's profile.
  - `PUT`: Update the authenticated user's profile.
- **Payload for `PUT`**:
  ```json
  {
    "first_name": "string",
    "last_name": "string",
    "phone": "string"
  }
  ```

---

### Author Endpoints

#### 1. List My Articles
- **URL**: `/api/articles/my/`
- **Method**: `GET`
- **Headers**: `Authorization: Token <user_token>`
- **Purpose**: Retrieve all articles authored by the authenticated user.

#### 2. Download Article
- **URL**: `/api/articles/<int:pk>/download/`
- **Method**: `GET`
- **Headers**: `Authorization: Token <user_token>`
- **Purpose**: Download the edited version of an article.

---

### Editor Endpoints

#### 1. List Available Articles
- **URL**: `/api/editor/articles/available/`
- **Method**: `GET`
- **Headers**: `Authorization: Token <editor_token>`
- **Purpose**: Retrieve articles available for editing based on the editor's specialization.

#### 2. Take an Article
- **URL**: `/api/editor/articles/<int:pk>/take/`
- **Method**: `POST`
- **Headers**: `Authorization: Token <editor_token>`
- **Purpose**: Assign an article to the editor.

#### 3. Submit an Article
- **URL**: `/api/editor/articles/<int:pk>/submit/`
- **Method**: `POST`
- **Headers**: `Authorization: Token <editor_token>`
- **Payload**:
  ```json
  {
    "edited_file": "file",
    "comments": "string"
  }
  ```
- **Purpose**: Submit the edited article.

#### 4. List Assigned Articles
- **URL**: `/api/editor/articles/assigned/`
- **Method**: `GET`
- **Headers**: `Authorization: Token <editor_token>`
- **Purpose**: Retrieve articles currently assigned to the editor.

---

### Admin Endpoints

#### 1. List Pending Articles
- **URL**: `/api/admin/articles/pending/`
- **Method**: `GET`
- **Headers**: `Authorization: Token <admin_token>`
- **Purpose**: Retrieve articles awaiting admin approval.

#### 2. Approve an Article
- **URL**: `/api/admin/articles/<int:pk>/approve/`
- **Method**: `POST`
- **Headers**: `Authorization: Token <admin_token>`
- **Purpose**: Approve an article for editing.

#### 3. Reject an Article
- **URL**: `/api/admin/articles/<int:pk>/reject/`
- **Method**: `POST`
- **Headers**: `Authorization: Token <admin_token>`
- **Payload**:
  ```json
  {
    "reason": "string"
  }
  ```
- **Purpose**: Reject an article with a reason.

---

### General Endpoints

#### 1. Articles
- **URL**: `/api/articles/`
- **Methods**:
  - `GET`: Retrieve all articles (admin/staff only).
  - `POST`: Create a new article (authenticated users).
- **Payload for `POST`**:
  ```json
  {
    "title": "string",
    "original_file": "file",
    "edit_type": "string"
  }
  ```

#### 2. Article Details
- **URL**: `/api/articles/<int:pk>/`
- **Methods**:
  - `GET`: Retrieve details of a specific article.
  - `PUT`: Update an article (author only).
  - `DELETE`: Delete an article (author only).

---

### Feedback Endpoints

#### 1. List Feedbacks
- **URL**: `/api/feedbacks/`
- **Method**: `GET`
- **Headers**: `Authorization: Token <user_token>`
- **Purpose**: Retrieve feedbacks for articles.

#### 2. Submit Feedback
- **URL**: `/api/feedbacks/`
- **Method**: `POST`
- **Headers**: `Authorization: Token <user_token>`
- **Payload**:
  ```json
  {
    "article": "int",
    "rating": "int",
    "comment": "string"
  }
  ```
- **Purpose**: Submit feedback for an article.

---

### Statistics Endpoints

#### 1. View Statistics
- **URL**: `/api/statistics/`
- **Method**: `GET`
- **Headers**: `Authorization: Token <admin_token>`
- **Purpose**: Retrieve system statistics (admin only).