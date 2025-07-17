# Neurologix Smart Search POV

## Project Overview

This Proof of Value (PoV) is focused on developing a streamlined query interface for Neurologix's C3Logix concussion management platform. The goal is to enable medical professionals—especially team physicians and athletic trainers—to ask Natural Language questions about patient assessments and receive accurate insights.

## Architecture

- **Frontend**: Streamlit chat interface for natural language queries
- **Backend**: FastAPI-based REST API for query processing
- **Data Sources**: 
  - Amazon RDS (MySQL) for structured data
  - Amazon S3 for JSON assessment data
- **Query Engine**: AWS services for natural language processing
- **Vector Database**: Amazon OpenSearch for embeddings

## Target Modules

1. **Symptom Checklist**: Patient-reported symptoms and severity scores
2. **Reaction Time Tests**: Cognitive assessment results

## Quick Start

### Prerequisites
- Python 3.8+
- AWS CLI configured
- Docker (optional)

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your AWS credentials and database settings
   ```

4. Run the frontend:
   ```bash
   streamlit run frontend.py
   ```

5. Run the backend (in a separate terminal):
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

## Project Structure

```
├── frontend.py              # Streamlit chat interface
├── backend/                 # Backend API and services
│   ├── main.py             # FastAPI application
│   ├── api/                # API endpoints
│   ├── services/           # Business logic services
│   ├── models/             # Data models and schemas
│   └── utils/              # Utility functions
├── config/                 # Configuration files
├── data/                   # Sample data and schemas
├── deployment/             # AWS deployment configurations
├── tests/                  # Test files
└── docs/                   # Documentation
```

## Features

- Natural language query processing
- Real-time streaming responses
- Integration with AWS services
- Secure data access with user scoping
- Clinical workflow optimization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is proprietary to Neurologix and Akuna Technologies.
