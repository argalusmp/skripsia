# Skripsi Chatbot Backend

## Project Overview
This project is a backend application for a chatbot system designed to assist users with information related to thesis (skripsi) guidelines and processes. It is built using **FastAPI** and incorporates modern technologies like **Pinecone**, **LangChain**, **Mistral**, and **Groq** for advanced features such as vector search, text extraction, and audio transcription.

---

## Key Features
1. **Authentication and Authorization**:
   - User login and registration with JWT-based authentication.
   - Role-based access control (e.g., admin vs. student).

2. **Knowledge Base Management**:
   - Upload and process various file types (PDF, images, audio).
   - Extract text from files using OCR and transcription services.
   - Store and retrieve knowledge chunks using Pinecone vector database.

3. **Chatbot Functionality**:
   - RAG (Retrieval-Augmented Generation) model for generating responses.
   - Context-aware conversation history.
   - Manage user conversations and messages.

4. **Database Management**:
   - SQLAlchemy ORM for database interactions.
   - Alembic for database migrations.

5. **Middleware**:
   - Role-based access validation.
   - Rate limiting for API endpoints.

---

## Project Structure
```
.
├── alembic/                # Database migration scripts
├── app/                    # Main application code
│   ├── auth/               # Authentication and authorization
│   ├── chat/               # Chatbot-related functionality
│   ├── knowledge/          # Knowledge base management
│   ├── middleware/         # Custom middleware
│   ├── users/              # User management
│   ├── vector_store/       # Pinecone vector database integration
│   ├── config.py           # Application configuration
│   ├── database.py         # Database connection setup
│   └── main.py             # FastAPI application entry point
├── uploads/                # Directory for uploaded files
├── requirements.txt        # Python dependencies
└── alembic.ini             # Alembic configuration
```

---

## Setup Instructions

### 1. Clone the Repository
```powershell
git clone https://github.com/argalusmp/skripsia.git
cd <repository-folder>
```

### 2. Install Dependencies
Create a virtual environment and install the required Python packages:
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the root directory with the following variables:
```
DATABASE_URL=postgresql://<user>:<password>@<host>/<database>
JWT_SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-api-key
GROQ_API_KEY=your-groq-api-key
MISTRAL_API_KEY=your-mistral-api-key
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_INDEX_NAME=ragv2
UPLOAD_DIR=uploads
```

### 4. Run Database Migrations
Initialize the database schema using Alembic:
```powershell
alembic upgrade head
```

### 5. Start the Application
Run the FastAPI application:
```powershell
uvicorn app.main:app --reload
```

### 6. Access the API
Open your browser and navigate to:
```
http://localhost:8000/docs
```
This will display the interactive API documentation.

---

## API Endpoints

### **Authentication**
- `POST /auth/token`: Login and obtain an access token.
- `POST /auth/register`: Register a new user.

### **Users**
- `GET /users/me`: Get the current user's profile.
- `PUT /users/me`: Update the current user's profile.
- `GET /users/`: List all users (admin only).

### **Knowledge Base**
- `POST /knowledge/upload`: Upload a new knowledge source.
- `GET /knowledge/`: List all knowledge sources.
- `GET /knowledge/{knowledge_id}`: Get details of a specific knowledge source.
- `DELETE /knowledge/{knowledge_id}`: Delete a knowledge source (admin only).

### **Chat**
- `POST /chat/send`: Send a message to the chatbot.
- `GET /chat/conversations`: List all user conversations.
- `GET /chat/conversations/{conversation_id}`: Get details of a specific conversation.
- `DELETE /chat/conversations/{conversation_id}`: Delete a conversation.

---

## Technologies Used
- **FastAPI**: Web framework for building APIs.
- **SQLAlchemy**: ORM for database interactions.
- **Alembic**: Database migrations.
- **Pinecone**: Vector database for storing and retrieving embeddings.
- **LangChain**: Framework for building RAG pipelines.
- **Mistral**: OCR for text extraction from documents and images.
- **Groq**: Audio transcription service.

---

## Contributing
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request with a detailed description of your changes.

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.
