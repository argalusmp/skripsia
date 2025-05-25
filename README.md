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

This application is configured for deployment on a DigitalOcean Droplet with automatic deployments via GitHub Actions. Follow these steps to deploy the application.

### Prerequisites
- A DigitalOcean account
- A domain name (optional, but recommended)
- GitHub repository with your code

### 1. Create a DigitalOcean Droplet

1. Sign in to your DigitalOcean account
2. Click on "Create" and select "Droplets"
3. Choose the following configuration:
   - **Image**: Ubuntu 22.04 LTS
   - **Plan**: Basic (Shared CPU)
   - **Size**: Regular with 2GB RAM / 1 CPU
   - **Region**: Singapore (SGP1) or closest to your target users
   - **Authentication**: SSH Key (recommended)
   - **Hostname**: skripsia-backend (or your preferred name)

### 2. Initial Server Setup

Connect to your droplet via SSH and run these commands:

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required dependencies
sudo apt install -y python3-pip python3-venv nginx supervisor git

# Configure firewall
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 3. Clone the Repository

```bash
# Clone repository to /var/www
git clone https://github.com/yourusername/skripsia.git /var/www/skripsia
cd /var/www/skripsia
```

### 4. Set Up Environment

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file with your environment variables
nano .env
```

Add your environment variables to the `.env` file:
```
DATABASE_URL=postgresql://username:password@localhost/dbname
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
```

### 5. Set Up PostgreSQL Database

```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql -c "CREATE DATABASE dbname;"
sudo -u postgres psql -c "CREATE USER username WITH PASSWORD 'password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE dbname TO username;"

# Run migrations
source venv/bin/activate
alembic upgrade head

# Create admin user
python create_admin_user.py
```

### 6. Configure Supervisor

Create a Supervisor configuration file to manage the FastAPI application:

```bash
sudo nano /etc/supervisor/conf.d/skripsia.conf
```

Add the following configuration:

```
[program:skripsia]
command=/var/www/skripsia/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000 app.main:app
directory=/var/www/skripsia
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/skripsia/err.log
stdout_logfile=/var/log/skripsia/out.log
```

Create log directory and update permissions:

```bash
sudo mkdir -p /var/log/skripsia
sudo chown -R www-data:www-data /var/log/skripsia
sudo chown -R www-data:www-data /var/www/skripsia
```

### 7. Configure Nginx

Create an Nginx configuration file:

```bash
sudo nano /etc/nginx/sites-available/skripsia
```

Add the following configuration:

```
server {
    listen 80;
    server_name yourdomain.com;  # Replace with your domain or server IP

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    client_max_body_size 50M;
}
```

Enable the site and restart Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/skripsia /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 8. Set Up GitHub Actions for CI/CD

This repository already includes a GitHub Actions workflow file (`.github/workflows/deploy.yml`) for automatic deployment.

To enable it, you need to add these secrets to your GitHub repository:
- `DO_HOST`: Your DigitalOcean droplet IP
- `DO_USERNAME`: SSH username (usually 'root')
- `DO_SSH_KEY`: Your private SSH key for connecting to the droplet

The GitHub Actions workflow will:
1. Connect to your server via SSH
2. Pull the latest code changes
3. Update dependencies
4. Run database migrations
5. Restart the application

### 9. SSL Configuration with Let's Encrypt (Optional)

For HTTPS support:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### 10. Monitoring and Maintenance

Check service status:
```bash
sudo supervisorctl status skripsia
sudo systemctl status nginx
```

View logs:
```bash
sudo tail -f /var/log/skripsia/err.log
sudo tail -f /var/log/skripsia/out.log
```

Restart services:
```bash
sudo supervisorctl restart skripsia
sudo systemctl restart nginx
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
