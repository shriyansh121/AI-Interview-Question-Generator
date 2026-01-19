import os

current_dir = os.getcwd()

structure = [
    'requirements.txt',
    'config',
    'config/__init__.py',
    'config/config.yaml',
    'config/settings.py',
    'src',
    'src/__init__.py',
    'src/agent',
    'src/agent/__init__.py',
    'src/agent/interview_agent.py',
    'src/parsers',
    'src/parsers/__init__.py',
    'src/parsers/resume_parser.py',
    'src/generators',
    'src/generators/__init__.py',
    'src/generators/question_generator.py',
    'src/utils/__init__.py',
    'src/utils/logger.py',
    'data',
    'output',
    'main.py',
    'test.py',
    'setup.sh',
    'setup.py',
    'QUICKSTART.md',
    'ARCHITECTURE.md',
    'logs'
]

for i in structure:
    path = os.path.join(current_dir,i)
    if os.path.splitext(i)[1]:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, 'w').close()
    else:  
        os.makedirs(path, exist_ok=True)
print("Folder structure created successfully.")