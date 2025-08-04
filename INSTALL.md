# Jenbina Installation Guide

This guide provides detailed step-by-step instructions to install and run Jenbina on your local machine.

## Prerequisites

Before starting, ensure you have the following installed:

- **Python 3.10 or higher**
- **Git** (for cloning the repository)
- **At least 16GB of RAM** (for running the LLM)
- **8GB of free disk space** (for the model and dependencies)

## Step 1: Install Ollama

Ollama is required to run the local LLM (Llama 3.2 3B).

### macOS
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Windows
1. Download the installer from [https://ollama.ai/download](https://ollama.ai/download)
2. Run the downloaded `.exe` file
3. Follow the installation wizard

### Verify Ollama Installation
```bash
ollama --version
```

## Step 2: Pull the Llama Model

Download the required LLM model (this may take several minutes depending on your internet connection):

```bash
ollama pull llama3.2:3b-instruct-fp16
```

**Note**: The model is approximately 2GB. Ensure you have sufficient disk space and a stable internet connection.

## Step 3: Clone the Repository

```bash
git clone https://github.com/motya770/jenbina
cd jenbina
```

## Step 4: Set Up Python Environment

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

## Step 5: Configure Environment Variables (Optional)

For advanced features and debugging, you can set these environment variables:

```bash
export OLLAMA_HOST="http://localhost:11434"
export LANGSMITH_TRACING="true"
export LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
export LANGSMITH_API_KEY="your_key_here"
export LANGSMITH_PROJECT="jenbina"
```

**Note**: These are optional and the application will work without them.

## Step 6: Start the Application

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

## Step 7: Verify Installation

1. **Check Ollama Status**: Ensure Ollama is running
   ```bash
   ollama list
   ```
   You should see `llama3.2:3b-instruct-fp16` in the list.

2. **Test the Application**: 
   - Open your browser and go to http://localhost:8501
   - You should see the Jenbina interface with a chat window
   - Try sending a message to verify the LLM is responding

## Troubleshooting

### Common Issues

#### 1. "Command not found: ollama"
- Ensure Ollama is properly installed
- Restart your terminal after installation
- Add Ollama to your PATH if necessary

#### 2. "ModuleNotFoundError: No module named 'chromadb'"
- Ensure you're in the virtual environment
- Run `pip install -r requirements.txt` again
- Check that `chromadb==0.4.24` is in requirements.txt

#### 3. "Connection refused" when starting Streamlit
- Check if port 8501 is already in use
- Kill existing processes: `pkill -f streamlit`
- Try a different port: `streamlit run app.py --server.port 8502`

#### 4. LLM not responding
- Verify Ollama is running: `ollama list`
- Check if the model is downloaded: `ollama pull llama3.2:3b-instruct-fp16`
- Restart Ollama: `ollama serve`

#### 5. Memory issues
- Ensure you have at least 4GB of RAM available
- Close other memory-intensive applications
- Consider using a smaller model if available

### Performance Optimization

#### For Better Performance:
1. **Use SSD storage** for faster model loading
2. **Allocate more RAM** to Ollama if available
3. **Use a wired internet connection** for initial model download
4. **Close unnecessary applications** while running Jenbina

#### For Development:
1. **Enable LangSmith tracing** for debugging
2. **Set up API keys** for external services (Eventbrite, Yelp, etc.)
3. **Use a larger model** for better responses (if available)

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
2. **Stop Ollama**: `pkill -f ollama` (if you want to completely stop the LLM service)

## Uninstalling

To completely remove Jenbina:

1. **Delete the repository**:
   ```bash
   cd ..
   rm -rf jenbina
   ```

2. **Remove Ollama** (optional):
   ```bash
   # macOS/Linux
   rm -rf ~/.ollama
   
   # Windows
   # Uninstall via Control Panel or use the uninstaller
   ```

3. **Remove Python virtual environment**:
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
- **Storage**: 8GB free space
- **Network**: Internet connection for initial setup 