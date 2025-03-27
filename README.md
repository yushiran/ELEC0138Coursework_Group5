# AI Chat Platform
![GitHub Repo stars](https://img.shields.io/github/stars/yourusername/ELEC0138Coursework_Group5?style=social)
![GitHub contributors](https://img.shields.io/github/contributors/yourusername/ELEC0138Coursework_Group5)
![GitHub last commit](https://img.shields.io/github/last-commit/yourusername/ELEC0138Coursework_Group5)

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
cd env
conda env create -f environments.yml
conda activate security
```
3. **Configure Environment Variables**

Create a `.env` file in the `flask_backend` directory with the following content:
```bash
OPENAI_API_KEY=your_openai_api_key
MONGODB_URI=mongodb://localhost:27017/
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
FLASK_SECRET_KEY=your_secret_key
```

## Usage Guide
Starting the Application
1. **Launch the Server**
```bash
python app.py
```

## Technology Stack
- **Backend**: Flask, Python  
- **Database**: MongoDB  
- **AI**: OpenAI API (GPT models)  
- **Frontend**: HTML, CSS, JavaScript  
- **Authentication**: Flask-Bcrypt, OAuth  
