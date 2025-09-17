oak - An Agentic ToolThis is the core library for our agentic tool. It is structured to be modular and scalable, with a clear separation of concerns, and is designed to be installed and used by other services, such as our LangChain agents.Project Structureoak/
├── src/
│   └── oak/                    # Main Python package
│       ├── __init__.py         # Makes `oak` a Python package
│       ├── celery_app.py       # Celery application instance for task management
│       ├── config.py           # Configuration manager loaded from .env
│       ├── data/               # Data models and structures
│       │   ├── __init__.py
│       │   └── modules/        # Domain-specific data modules
│       │       ├── __init__.py
│       │       ├── analytics/
│       │       ├── current_events/
│       │       ├── market_data/
│       │       └── stocks/
│       ├── prompts/            # Agent prompts and templates
│       │   └── __init__.py
│       ├── services/           # Core business logic and data fetchers
│       │   ├── __init__.py
│       │   └── data_fetcher/
│       │       ├── __init__.py
│       │       ├── database_service.py
│       │       └── exceptions.py
│       ├── tasks/              # Celery task definitions
│       │   ├── __init__.py
│       │   └── task_manager.py
│       └── utils/              # Utility functions and helpers
│           └── __init__.py
├── pyproject.toml              # Project and dependency management
├── docker-compose.yml          # Docker services configuration
└── .env.example                # Example file for environment variables
ConfigurationFor security, sensitive data is stored in a .env file, which is loaded by the config.py module. This setup keeps credentials out of your codebase and makes it easy to manage different environments (development, testing, production).Key Componentsoak/src/oak/config.pyThis module defines a Config class that reads environment variables and provides them to the application. It ensures that required variables are present, and it allows for type casting, such as converting a string to a boolean or integer..env and .env.exampleThe .env file holds your actual secret credentials. It should be added to your .gitignore to prevent it from being committed to version control. The .env.example file is a template that shows other developers what environment variables your application expects.oak/src/oak/services/data_fetcher/database_service.pyThis module uses the new config.py file to get its database connection string, further centralizing the application's configuration.Setup and UsagePrerequisitesDocker and Docker Compose installed.InstallationInstall Poetry:If you don't have Poetry, install it following the official instructions.Clone the Repository:git clone <your-repo-url>
cd <your-repo-name>
Create and Fill .env file:Create a .env file in the root directory and copy the contents from .env.example. Fill in your specific credentials.Install Dependencies:From the oak/ directory, run:poetry install
Running the SystemThe docker-compose.yml file has been updated to use Redis and Celery.docker-compose up --build
This will start:The PostgreSQL database.A Redis service to act as a message broker.A Celery worker that listens for and executes tasks.The main application container, which will soon house your orchestrator.Running TestsTo run the unit tests, you will need Docker and Docker Compose installed. From the oak/ directory, simply run:poetry run pytest