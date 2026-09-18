from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello from GitLab CI/CD!\n"


@app.route("/health")
def health():
    return "Helth is OK!!!\n"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
