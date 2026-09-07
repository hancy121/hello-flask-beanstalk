from flask import Flask

application = Flask(__name__)


@application.route("/")
def hello():
    return """
    <html>
        <head>
            <title>Hello AWS</title>
        </head>
        <body>
            <h1>Hello flask 2!</h1>
            <p>Flask is running on AWS Elastic Beanstalk.</p>
        </body>
    </html>
    """


if __name__ == "__main__":
    application.run()
