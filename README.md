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
```bash
git clone https://github.com/argalusmp/skripsia.git
cd <repository-folder>
```

### 2. Install Dependencies
Create a virtual environment and install the required Python packages:
```bash
python -m venv venv
source venv/bin/activate
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
```bash
alembic upgrade head
```

### 5. Start the Application
Run the FastAPI application:
```bash
uvicorn app.main:app --reload
```

### 6. Access the API
Open your browser and navigate to:
```
http://localhost:8000/docs
```
This will display the interactive API documentation.

---

## Deployment on DigitalOcean

### Prerequisites
1. A DigitalOcean account with sufficient credits.
2. SSH key added to your DigitalOcean account for secure server access.
3. Basic knowledge of Linux commands.

### Steps to Deploy

#### 1. Create a Droplet
- Log in to your DigitalOcean account.
- Create a new Droplet with the following specifications:
  - **Image**: Ubuntu 22.04 LTS
  - **Plan**: Basic (at least 2GB RAM, 1 CPU)
  - **Region**: Closest to your target audience
  - **SSH Key**: Add your SSH key for secure access

#### 2. Connect to the Droplet
Use SSH to connect to your Droplet:
```bash
ssh root@<your-droplet-ip>
```

#### 3. Update the System
Update the system packages:
```bash
apt update && apt upgrade -y
```

#### 4. Install Dependencies
Install required packages:
```bash
apt install -y python3-pip python3-venv nginx supervisor git
```

#### 5. Clone the Repository
Navigate to the `/var/www` directory and clone your repository:
```bash
mkdir -p /var/www
cd /var/www
git clone https://github.com/argalusmp/skripsia.git
cd skripsia
```

#### 6. Set Up Python Environment
Create a virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### 7. Configure Environment Variables
Create a `.env` file in the project directory with your production environment variables:
```bash
cat > .env << 'EOF'
DATABASE_URL=postgresql://<user>:<password>@<host>/<database>
JWT_SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-api-key
GROQ_API_KEY=your-groq-api-key
MISTRAL_API_KEY=your-mistral-api-key
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_INDEX_NAME=ragv2
UPLOAD_DIR=uploads
DO_SPACE_REGION=sgp1
DO_SPACE_ENDPOINT=https://skripsia-uploads.sgp1.digitaloceanspaces.com
DO_SPACE_KEY=your-space-key
DO_SPACE_SECRET=your-space-secret
DO_SPACE_NAME=skripsia-uploads
USE_SPACES=true
EOF
```

#### 8. Run Database Migrations
Apply database migrations:
```bash
source venv/bin/activate
alembic upgrade head
```

#### 9. Configure Supervisor
Create a Supervisor configuration file to manage the application:
```bash
cat > /etc/supervisor/conf.d/skripsia.conf << 'EOF'
[program:skripsia]
command=/var/www/skripsia/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000 app.main:app
directory=/var/www/skripsia
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/skripsia/err.log
stdout_logfile=/var/log/skripsia/out.log
EOF
```
Reload Supervisor:
```bash
supervisorctl reread
supervisorctl update
```

#### 10. Configure Nginx
Create an Nginx configuration file:
```bash
cat > /etc/nginx/sites-available/skripsia << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    client_max_body_size 50M;
}
EOF
```
Enable the site and restart Nginx:
```bash
ln -s /etc/nginx/sites-available/skripsia /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

#### 11. Test the Deployment
Access your application using the Droplet's public IP:
```
http://<your-droplet-ip>
```

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
