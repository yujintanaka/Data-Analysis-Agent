# Data Analysis AI Assistant Built with LangGraph

Connect to your database and ask your Assistant to do anything!

## 🚀 Features

- **Interactive AI Assistant**: Natural language interface for data analysis and visualization
- **Multi-Database Support**: Connect to SQLite, MySQL, or PostgreSQL databases
- **Smart SQL Generation**: AI-powered SQL query generation with safety checks
- **Advanced Data Analysis**: Automated data exploration and statistical analysis
- **Interactive Visualizations**: Dynamic Plotly charts with automatic storage and retrieval
- **Debug Mode**: View intermediate steps and thought process of the AI
- **Persistent State**: Maintains conversation history and analysis context
- **Secure Operations**: Read-only database access with automatic resource cleanup

## 🤖 Agent Architecture

This application utilizes a custom langgraph agent built with a ReAct (Reasoning and Acting) architecture. The agent is designed to help users understand, analyze, and visualize their data through an interactive conversation.

### Graph Implementation
The agent is built using LangGraph's `StateGraph` with the following components:

1. **Nodes**:
   - `get_table_schema`: Initial node that retrieves database schema
   - `agent`: Core brain node for decision making
   - `tools`: Executes selected tools (SQL queries and Python tasks)
   - `handle_tool_output`: Processes tool outputs and updates state

2. **Graph Flow**:
   ```
   get_table_schema → agent → tools → handle_tool_output → agent
   ```
   - Conditional routing from agent to tools based on decision
   - Recursive execution with a limit of 15 iterations
   - Streaming support for real-time updates

3. **State Management**:
   - Maintains conversation history
   - Tracks intermediate outputs for debugging
   - Manages visualization paths
   - Handles database configuration

### Core Tools
The agent has access to two specialized tools:

1. **SQL Query Tool (`make_sql_query`)**
   - Executes SQL queries against connected databases
   - Supports multiple database types (SQLite, MySQL, PostgreSQL)
   - Implements safety measures (read-only operations)
   - Stores query results in a dataframe store for further analysis

2. **Python Task Tool (`complete_python_task`)**
   - Executes Python code for data analysis and visualization
   - Supports pandas for data manipulation
   - Integrates with plotly for interactive visualizations
   - Maintains persistent variables between executions
   - Automatically saves generated visualizations

### Database Integration
- Supports multiple database types:
  - SQLite
  - MySQL
  - PostgreSQL
- Implements secure connection management
- Provides schema inspection capabilities
- Uses SQLAlchemy for database operations

### Visualization Capabilities
- Interactive Plotly visualizations
- Automatic figure storage and retrieval
- Support for various chart types
- Persistent storage of generated plots

### Safety Features
- Read-only SQL operations
- Query result previewing
- Automatic resource cleanup
- Secure database connection handling

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package installer)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/eda-app.git
cd eda-app
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## 🔧 Configuration

1. Create a `.env` file in the root directory with your configuration settings:
```
# Add your environment variables here
```

## 🚀 Usage

To run the application:

```bash
streamlit run main.py
```

The application will be available at `http://localhost:8501` by default.

## 📦 Dependencies

### Core Dependencies
- streamlit >= 1.24.0
- langchain-core >= 0.1.0
- langgraph >= 0.0.10
- pandas >= 2.0.0
- plotly >= 5.18.0
- scikit-learn >= 1.3.0

### Database Dependencies
- sqlalchemy >= 2.0.0
- mysql-connector-python >= 8.0.0
- psycopg2-binary >= 2.9.0
- sqlite3 (built-in)

### Development Dependencies
- python-dotenv >= 1.0.0
- typing-extensions >= 4.7.0

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by and built upon concepts from [AgenticDataAnalysis](https://github.com/whitew1994WW/AgenticDataAnalysis) by whitew1994WW 