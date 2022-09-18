import os.path
import dotenv

dotenv_path = "website/database/.env"
db_path = "website/database/data.db"


def init_dotenv():
    dotenv.load_dotenv(dotenv_path)


def is_database():
    return os.path.exists(db_path)


def is_config():
    return os.path.exists(dotenv_path)


def set_dotenv(request):
    dotenv.set_key(dotenv_path, "GOOGLE_CLIENT_ID",
                   request.form['GOOGLE_CLIENT_ID'])

    dotenv.set_key(dotenv_path, "GOOGLE_CLIENT_SECRET",
                   request.form['GOOGLE_CLIENT_SECRET'])

    dotenv.set_key(dotenv_path, "MAIL_USERNAME", request.form['MAIL_USERNAME'])
    dotenv.set_key(dotenv_path, "OAUTHLIB_INSECURE_TRANSPORT",
                   request.form['GOOGLE_INSECURE_AUTH'])

    dotenv.set_key(dotenv_path, "MAIL_PASSWORD", request.form['MAIL_PASSWORD'])
    dotenv.set_key(dotenv_path, "MAIL_DEFAULT_SENDER",
                   request.form['MAIL_USERNAME'])
