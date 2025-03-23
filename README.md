# Patent-Research-Assistant  
**RAG × LLM | AI-Powered Patent Search**

A full-stack application that simplifies and enhances patent research using Retrieval-Augmented Generation (RAG), Large Language Models (LLMs), and vector search — all wrapped in a user-friendly, cloud-hosted chatbot interface.

## Overview  
The **Patent Research Assistant** is an intelligent, scalable tool that streamlines patent exploration. It integrates advanced NLP, domain-specific LLMs, and a vector database to retrieve, analyze, and contextualize patent data using natural language queries.

## Features  
- Natural language patent search interface  
- Voice recognition for patent queries  
- Light/Dark theme support  
- Responsive design for all devices  
- User authentication system  
- Real-time analysis with RAG + vector embeddings  
- Semantic similarity search with vector databases  
- Relevance-scored patent results

## Technology Stack  
**Frontend:** HTML, CSS, JavaScript, Bootstrap for responsive design  
**Backend:** Python, AWS Lambda (Serverless)  
**AI/ML:** PatentSBERTa for embeddings, Falcon-7B for text generation, RAG implementation with LangChain  
**Cloud Services (AWS):** S3 – Static hosting, Lambda – Backend logic, API Gateway – REST endpoints, OpenSearch – Vector search & retrieval, CloudWatch – Monitoring & logging

## Project Structure  
```
project/
├── frontend/
│   ├── index.html          # Main landing page
│   ├── signup.html         # User registration
│   ├── app.js              # Frontend logic
│   └── styles/             # CSS styles
├── backend/
│   ├── lambda_function.py  # AWS Lambda handler
│   └── requirements.txt    # Python dependencies
└── data_processing/
    ├── XMLSplitter.py      # XML file parsing
    ├── utility_parquet.py  # Data transformation
    └── embeddings.py       # Embedding generation
```

## Setup & Installation  
**Prerequisites:**  
- AWS account with necessary permissions  
- Python 3.8+  
- Node.js and npm  
- AWS CLI configured  

**Frontend Setup:**  
```bash
# Clone the repo
git clone https://github.com/your-username/Patent-Research-Assistant.git
cd Patent-Research-Assistant/frontend

# Configure API endpoints in app.js

# Deploy to S3
aws s3 sync . s3://your-bucket-name
```

**Backend Setup:**  
```bash
# Navigate to backend
cd ../backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENSEARCH_ENDPOINT=your-opensearch-endpoint
export REGION=your-region

# Deploy Lambda via AWS Console or CLI
```

**OpenSearch Setup:**  
- Create a new OpenSearch domain  
- Configure vector index mappings  
- Set IAM roles and security policies  

## Usage  
1. Access the app via the S3 static website URL  
2. Register or log in  
3. Enter your patent query using voice or text  
4. View top-ranked patent results with summaries  
5. Toggle dark/light mode as preferred  

## Data Processing Pipeline  
1. XML patent file splitting  
2. Utility patent extraction  
3. Parquet transformation  
4. Embedding generation using PatentSBERTa  
5. OpenSearch indexing  

## Monitoring & Security  
- Monitor logs via AWS CloudWatch  
- Review Lambda execution metrics  
- Secure API calls with HTTPS & authentication  
- Update dependencies and embeddings regularly  
- Follow AWS security best practices  

## Contributing  
1. Fork the repo  
2. Create a new feature branch  
3. Commit your changes  
4. Push to your fork  
5. Submit a Pull Request  
