#!/usr/bin/env bash
export IS_DEBUG=${DEBUG:-false}

if [ "$IS_DEBUG" = "true" ]; then
    echo "DEBUG!"
    uvicorn --host 0.0.0.0 --port 5000 app:app --reload
else
    echo "PRODUCTION!"
    uvicorn --workers 4 --host 0.0.0.0 --port 5000 app:app
fi
