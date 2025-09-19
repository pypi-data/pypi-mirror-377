# ILY CLI

A command-line interface (CLI) tool for couples to send messages to each other. This CLI interacts with a self-hostable ILY server, allowing you to send and receive messages securely and privately.

## Features

- Send messages to your partner from the command line.
- Receive real-time message notifications (requires server configuration).
- Self-host your own ILY server for complete privacy and control.

## Prerequisites

- Python 3.7+
- An ILY server instance. See the [ILY Server](https://github.com/your-repo/ily-server) repository for deployment instructions.

## Installation

1.  **Install the CLI:**

    ```bash
    pip install ily-cli
    ```

2.  **Configure the CLI:**

    After installation, you need to configure the CLI with your ILY server's URL and your user credentials.

    ```bash
    ily configure
    ```

    This will prompt you to enter the following information:

    - **Server URL:** The URL of your ILY server (e.g., `https://ily.example.com`).
    - **Username:** Your username on the ILY server.
    - **Partner's Username:** Your partner's username on the ILY server.
    - **API Key:** Your API key for authentication.

## Usage

### Sending a Message

To send a message, use the `send` command:

```bash
ily send "Your message here"
```

For example:

```bash
ily send "I'm thinking of you! ❤️"
```

### Viewing Message History

To view your message history, use the `history` command:

```bash
ily history
```

This will display a list of your past messages.

## Development

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-repo/ily-cli.git
    cd ily-cli
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -e .
    ```

## Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.