#!/bin/bash
echo "Starting Ollama server..."
ollama serve &  

sleep 3

echo "Ollama is ready, creating the model..."
ollama run llama3.2
