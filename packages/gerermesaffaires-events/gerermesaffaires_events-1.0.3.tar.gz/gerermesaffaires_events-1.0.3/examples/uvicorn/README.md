# Uvicorn 🦄

This folder shows how to use the event server with [Uvicorn](https://github.com/kludex/uvicorn), a fast and lightweight ASGI server for Python.

## Getting started

### What is Uvicorn?

Uvicorn is an ASGI (Asynchronous Server Gateway Interface) server that allows you to run asynchronous web applications in Python. It is especially useful for:

- Fast microservices and APIs.
- Applications requiring WebSockets, streaming, or asynchronous tasks.
- Developing and deploying event servers like the one provided in this project.

In the context of `gerermesaffaires-events`, Uvicorn exposes the event emitter as an ASGI application, making it easy to receive and emit events in real time.

### Example usage

Below you will find practical examples to help you get started with Uvicorn and the event server.

#### Command line usage

You can run the event server directly from the command line using Uvicorn. This is useful for quick testing or deployment without writing additional code.

```bash
uv run --with uvicorn uvicorn main:emitter.app --host 127.0.0.1 --port 8001
```

#### Programmatic usage

To use Uvicorn programmatically, first install it in your environment. This step ensures that Uvicorn is available for your Python scripts.

```bash
uv add uvicorn
```

The following Python code demonstrates how to set up an event emitter, register event handlers, and launch the ASGI application using Uvicorn. This approach gives you more control and flexibility for integrating event-driven logic into your application.

```python
# examples/uvicorn/test.py

import uvicorn
from gerermesaffaires_events import EventEmitter

emitter = EventEmitter(signature="secret")

@emitter.on("ping")
def handle_ping(data):
    print(f"Received ping event: {data}")

@emitter.on("error")
def handle_error(data):
    print(f"Received error event: {data}")

if __name__ == "__main__":
    uvicorn.run(emitter.app, host="127.0.0.1", port=8001)
```

Once your script is ready, you can start the server using the following command. This will launch your event server and make it accessible for handling events.

```bash
uv run test.py
```
