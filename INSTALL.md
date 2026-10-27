# Jenbina Installation Guide

This guide provides detailed step-by-step instructions to install and run Jenbina on your local machine.

## Prerequisites

Before starting, ensure you have the following installed:

- **Python 3.10 or higher**
- **Git** (for cloning the repository)
- **An OpenAI API key**
- **Neo4j Database** (optional, for advanced relationship tracking)

## Step 1: Clone the Repository

```bash
git clone https://github.com/motya770/jenbina
cd jenbina
```

## Step 2: Set Up Python Environment

### Create Virtual Environment
```bash
python3 -m venv .venv
```

### Activate Virtual Environment

**macOS/Linux:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 3: Install Neo4j (Optional)

For advanced relationship tracking and graph-based memory, you can install Neo4j:

### Using Docker (Recommended)
```bash
docker run \
    --name neo4j \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/password \
    -e NEO4J_PLUGINS='["apoc"]' \
    -v neo4j_data:/data \
    -v neo4j_logs:/logs \
    neo4j:5.17.0
```

### Using Neo4j Desktop
1. Download Neo4j Desktop from [https://neo4j.com/download/](https://neo4j.com/download/)
2. Install and create a new project
3. Create a new database with password "password"
4. Start the database

### Verify Neo4j Installation
- **Browser**: http://localhost:7474 (username: neo4j, password: password)
- **Bolt**: bolt://localhost:7687

**Note**: The application will work without Neo4j, but graph-based relationship tracking will be disabled.

## Step 4: Configure Environment Variables

Set your OpenAI API key (required):

```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

Optional environment variables for debugging:

```bash
export LANGSMITH_TRACING="true"
export LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
export LANGSMITH_API_KEY="your_key_here"
export LANGSMITH_PROJECT="jenbina"
```

## Step 5: Start the Application

### Navigate to Core Directory
```bash
cd core
```

### Launch Streamlit App
```bash
streamlit run app.py
```

### Access the Application
- **Local URL**: http://localhost:8501
- **Network URL**: http://your-ip:8501 (for access from other devices on your network)

## Step 6: Verify Installation

1. **Test the Application**:
   - Open your browser and go to http://localhost:8501
   - You should see the Jenbina interface with a chat window
   - Try sending a message to verify the LLM is responding

## Troubleshooting

### Common Issues

#### 1. "ModuleNotFoundError: No module named 'chromadb'"
- Ensure you're in the virtual environment
- Run `pip install -r requirements.txt` again
- Check that `chromadb` is in requirements.txt

#### 2. "Connection refused" when starting Streamlit
- Check if port 8501 is already in use
- Kill existing processes: `pkill -f streamlit`
- Try a different port: `streamlit run app.py --server.port 8502`

#### 3. LLM not responding
- Verify your `OPENAI_API_KEY` is set correctly
- Check your OpenAI account has available credits

#### 4. Memory issues
- Ensure you have at least 4GB of RAM available
- Close other memory-intensive applications

### Performance Optimization

#### For Better Performance:
1. **Use SSD storage** for faster database access
2. **Close unnecessary applications** while running Jenbina

#### For Development:
1. **Enable LangSmith tracing** for debugging
2. **Set up API keys** for external services (Eventbrite, Yelp, etc.)

## API Keys (Optional)

For enhanced features like real-time events and venue information, you can add API keys to `core/environment_simulator.py`:

```python
api_keys = {
    'eventbrite': 'your_eventbrite_token',
    'ticketmaster': 'your_ticketmaster_key',
    'yelp': 'your_yelp_token',
    'google_places': 'your_google_places_key'
}
```

**Note**: The application works without these keys, but some features will use fallback data.

## Stopping the Application

1. **Stop Streamlit**: Press `Ctrl+C` in the terminal running Streamlit

## Uninstalling

To completely remove Jenbina:

1. **Delete the repository**:
   ```bash
   cd ..
   rm -rf jenbina
   ```

2. **Remove Python virtual environment**:
   ```bash
   deactivate  # if virtual environment is active
   rm -rf .venv
   ```

## Support

If you encounter issues not covered in this guide:

1. Check the [GitHub Issues](https://github.com/yourusername/jenbina/issues)
2. Join our [Discord Community](https://discord.gg/e6sRPpyc)
3. Review the main [README.md](README.md) for additional information

## System Requirements Summary

- **OS**: macOS 10.14+, Ubuntu 18.04+, Windows 10+
- **Python**: 3.8+
- **RAM**: 4GB minimum, 8GB recommended
- **Network**: Internet connection (for OpenAI API calls)
