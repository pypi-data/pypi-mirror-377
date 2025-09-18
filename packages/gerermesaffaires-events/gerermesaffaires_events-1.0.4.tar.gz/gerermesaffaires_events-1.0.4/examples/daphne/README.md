# Daphne 🐍

This folder shows how to use the event server with [Daphne](https://github.com/django/daphne), a production-ready ASGI server for Python.

## Getting started

### What is Daphne?

Daphne is an ASGI (Asynchronous Server Gateway Interface) server developed as part of the Django Channels project. It is designed for running asynchronous Python web applications and is suitable for:

- Applications requiring WebSockets, long-lived connections, or asynchronous tasks.
- Deploying Django Channels and other ASGI-compatible frameworks.
- Running event-driven servers like the one provided in this project.

In the context of `gerermesaffaires-events`, Daphne exposes the event emitter as an ASGI application, allowing you to receive and emit events in real time.

### Example usage

Below you will find practical examples to help you get started with Daphne and the event server.

#### Command line usage

You can run the event server directly from the command line using Daphne. This is useful for quick testing or deployment without writing additional code.

```bash
uv run --with daphne daphne main:emitter.app -b 127.0.0.1 -p 8002
```

#### Programmatic usage

To use Daphne programmatically, first install it in your environment. This step ensures that Daphne is available for your Python scripts.

```bash
uv add daphne
```

The following Python code demonstrates how to set up an event emitter, register event handlers, and launch the ASGI application using Daphne. This approach gives you more control and flexibility for integrating event-driven logic into your application.

```python
# examples/daphne/test.py

from daphne.cli import CommandLineInterface
from gerermesaffaires_events import EventEmitter

emitter = EventEmitter(signature="secret")

@emitter.on("ping")
def handle_ping(data):
    print(f"Received ping event: {data}")

@emitter.on("error")
def handle_error(data):
    print(f"Received error event: {data}")

if __name__ == "__main__":
    cli = CommandLineInterface()
    cli.run(["main:emitter.app", "-b", "127.0.0.1", "-p", "8002"])
```

Once your script is ready, you can start the server using the following command. This will launch your event server and make it accessible for handling events.

```bash
uv run test.py
```
