from root.flask import create_app
from dotenv import load_dotenv
from root.flask.utils import popular_banco_command

load_dotenv()

app = create_app()
app.cli.add_command(popular_banco_command)

if __name__ == "__main__":
    app.run(debug=True)

