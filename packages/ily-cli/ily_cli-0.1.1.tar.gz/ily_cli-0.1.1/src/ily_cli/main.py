import typer
import requests
import os

app = typer.Typer()
API_URL = os.getenv("API_URL", "https://ily-cli.onrender.com/api")

def get_user_id():
    try:
        with open(".ily_config", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        typer.echo("User not authenticated. Please run 'ily register' or 'ily auth'.")
        raise typer.Exit(code=1)

def save_user_id(user_id):
    with open(".ily_config", "w") as f:
        f.write(user_id)
        
@app.command()
def register():
    """Generates a unique code to share with your partner."""
    response = requests.post(f"{API_URL}/register")
    data = response.json()
    typer.echo(data["message"])
    typer.echo(f"Your code is: {data['code']}")
    save_user_id(response.json()['user_id'])

@app.command()
def pair(code: str):
    """Pairs your account with your partner's code."""
    user_id = get_user_id()
    response = requests.post(
        f"{API_URL}/pair", 
        json={"code": code, "user1_id": user_id}
    )
    typer.echo(response.json()['message'])

@app.command()
def send(message: str):
    """Sends a message to your partner."""
    user_id = get_user_id()
    response = requests.post(
        f"{API_URL}/messages/send", 
        json={"sender_id": user_id, "content": message}
    )
    typer.echo(response.json()['message'])

@app.command()
def unread():
    """Checks for and displays unread messages."""
    user_id = get_user_id()
    response = requests.get(f"{API_URL}/messages/unread", params={"user_id": user_id})
    messages = response.json()
    if not messages:
        typer.echo("No new messages.")
    else:
        for msg in messages:
            typer.echo(f"Partner says: {msg['content']}")
            
if __name__ == "__main__":
    app()