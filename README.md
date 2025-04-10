# AI Chat Platform
![GitHub Repo stars](https://img.shields.io/github/stars/yushiran/ELEC0138Coursework_Group5?style=social)
![GitHub contributors](https://img.shields.io/github/contributors/yushiran/ELEC0138Coursework_Group5)
![GitHub last commit](https://img.shields.io/github/last-commit/yushiran/ELEC0138Coursework_Group5)

## Features

This is an AI chat platform built with Flask and the OpenAI API, offering the following features:

### Core Features

1. **User Authentication System**
      - Account registration and login
      - GitHub OAuth integration
      - Secure password encryption
      - User session management

2. **Chat Functionality**
      - Support for multiple AI models (GPT-4, GPT-4o, GPT-4-Turbo, GPT-3.5-Turbo)
      - Real-time model switching
      - Message history and conversation management
      - New conversation creation

3. **File Processing**
      - Support for uploading TXT, PDF, DOC, DOCX files
      - Automatic content extraction for AI analysis
      - File storage in MongoDB database
      - Download functionality for uploaded files

4. **Interface Features**
      - Responsive design
      - Collapsible sidebar
      - Dark theme interface
      - File attachment display and management

## Setup

### System Requirements

- Python 3.8+
- MongoDB server
- NodeJS (optional, for frontend development)

### Installation Steps

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/ELEC0138Coursework_Group5.git
cd ELEC0138Coursework_Group5
```
2. **Create and Activate Virtual Environment**
```bash
cd flask_backend/env
conda env create -f environment.yml
conda activate security
```
3. **Configure Environment Variables**

Create a `.env` file in the `flask_backend` directory with the following content:
```bash
# Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key for accessing GPT models.
- `MONGODB_URI`: The connection string for your MongoDB database.
- `GITHUB_CLIENT_ID`: The client ID for GitHub OAuth integration.
- `GITHUB_CLIENT_SECRET`: The client secret for GitHub OAuth integration.
- `FLASK_SECRET_KEY`: A secret key used for Flask session management and security.

# Email Settings

- `EMAIL_USERNAME`: The email address used for sending emails.
- `EMAIL_PASSWORD`: The app-specific password for the email account.
- `EMAIL_FROM`: The sender's email address for outgoing emails.
```
For more details on apply for github's OAuth ID&Secert key, you could refer [this guide](https://testdriven.io/blog/flask-social-auth/#user-management).

## Usage Guide
Starting the Application
1. **Launch the Server**
```bash
cd flask_backend
python app.py
```

## Technology Stack
- **Backend**: Flask, Python  
- **Database**: MongoDB  
- **AI**: OpenAI API (GPT models)  
- **Frontend**: HTML, CSS, JavaScript  
- **Authentication**: Flask-Bcrypt, OAuth  
