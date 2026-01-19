# AI-Interview-Question-Generator
This project focuses on generating ai based questions for interview preperation. It uses rag and scraping of linkedin profile and generates question based on multiple factors provided.

# Project Structure

```
Task 2/
│
├── config/                          # Configuration files
│   ├── __init__.py
│   ├── config.yaml                  # Main configuration (LLM, interview settings)
│   └── settings.py                  # Settings manager with env var support
│
├── src/                             # Source code
│   ├── __init__.py
│   │
│   ├── agent/                       # LangGraph agent
│   │   ├── __init__.py
│   │   └── interview_agent.py       # Main interview agent with state machine
│   │
│   ├── parsers/                     # Data extraction modules
│   │   ├── __init__.py
│   │   ├── resume_parser.py         # Parse PDF/DOCX/TXT resumes
│   │
│   ├── generators/                  # Content generation
│   │   ├── __init__.py
│   │   └── question_generator.py    # LLM-based question generation
│   │
│   └── utils/                       # Utilities
│       ├── __init__.py
│       └── logger.py                # Logging configuration
│
├── data/                            # Data directory
│   └── interviews/                  # Saved interview results (JSON)
│
├── logs/                            # Log files
│   └── interview_agent.log          # Application logs
|
├── examples/                        # Example files
│   └── sample_resume.txt            # Sample resume for testing
│
├── main.py                          # Main application entry point
├── test.py                          # Test suite
├── setup.sh                         # Setup script
│
├── requirements.txt                 # Python dependencies
├── .env                             # Environment variables 
├── .gitignore                       # Git ignore rules
│
├── README.md                        # Main documentation
```

## File Descriptions

### Configuration Layer

| File | Purpose |
|------|---------|
| `config/config.yaml` | Central configuration for LLM settings, interview parameters, logging, etc. |
| `config/settings.py` | Settings manager that loads YAML config and handles environment variables |

### Application Layer

| File | Purpose |
|------|---------|
| `main.py` | CLI interface and main entry point with argument parsing |
| `test.py` | Test suite for validating components and workflow |
| `setup.sh` | Automated setup script for installation |

### Agent Layer

| File | Purpose |
|------|---------|
| `src/agent/interview_agent.py` | LangGraph state machine orchestrating the interview workflow |

### Processing Layer

| File | Purpose |
|------|---------|
| `src/parsers/resume_parser.py` | Extract information from resume files (PDF, DOCX, TXT) |
| `src/generators/question_generator.py` | Generate personalized interview questions using LLM |

### Utility Layer

| File | Purpose |
|------|---------|
| `src/utils/logger.py` | Logging configuration with file rotation and console output |

## Features

- 📄 **Resume Parsing**: Extracts information from PDF, DOCX, and TXT resumes
- 🤖 **AI Question Generation**: Generates personalized interview questions based on candidate profile
- ⚙️ **Production-Ready**: Modular architecture with configuration management

## Production Consideration

### Security
- Never commit `.env` file with API keys
- Use environment variables for sensitive data
- Implement proper access controls

### Scalability
- Add database for storing interview results
- Implement caching for resume parsing
- Add queue system for batch processing


