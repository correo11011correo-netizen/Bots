#!/bin/bash
curl http://localhost:8000/v1/chat/completions -H "Content-Type: application/json" -d '{"messages": [{"content": "dime 3 lenguajes de programacion", "role": "user"}]}'
