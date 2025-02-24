FROM ollama/ollama:latest

# Set the correct entrypoint for Ollama
ENTRYPOINT ["/usr/bin/ollama", "serve"]
