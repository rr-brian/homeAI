# HomeAI - AI-Powered Real Estate Search

A unified full-stack application combining a React frontend with a Python Flask backend for AI-powered real estate document search using Azure Cognitive Search and Azure OpenAI.

## Features

- AI-powered document search using Azure Cognitive Search
- Enhanced search results with Azure OpenAI
- Modern React frontend with Material-UI and Framer Motion
- Search history tracking with localStorage
- Responsive design for all devices
- AG Grid for efficient data display

## Project Structure

- `/src` - React frontend code
- `/backend` - Python Flask backend code
  - `/rt_search` - Search client implementation
- `/public` - Static assets

## Setup Instructions

### Prerequisites

- Node.js and npm
- Python 3.8+
- Azure Cognitive Search account
- Azure OpenAI account

### Environment Setup

1. Copy `backend/.env.example` to `backend/.env` and fill in your Azure credentials
2. Install frontend dependencies: `npm install`
3. Install backend dependencies: `cd backend && pip install -r requirements.txt`

### Running Locally

1. Start the backend: `cd backend && python wsgi.py`
2. In a separate terminal, start the frontend: `npm start`
3. Access the application at http://localhost:3001

### Deployment

The application is designed to be deployed as a unified service where the Flask backend serves the React frontend static files.

1. Build the React app: `npm run build`
2. Deploy using the provided `_startup.sh` script

## License

MIT
