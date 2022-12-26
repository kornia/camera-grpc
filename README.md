# Camera grpc

Small example to create a webcam based grpc server

## Setup

Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Re-generate proto definitions (just in case)

```bash
python3 run_codegen.py
```

## Run server

In terminal #1. Play with fps, or the port.

```bash
python3 camera_service.py
```

## Run client

In another terminal #2. Change `address` to connect over wifi.

```bash
python3 camera_client.py
```
