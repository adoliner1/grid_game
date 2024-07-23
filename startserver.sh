#!/bin/bash
export PYTHONPATH=$(pwd)/fast_api_server
uvicorn fast_api_server.main:app --reload
