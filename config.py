import environ

env = environ.Env()
environ.Env.read_env()

API_TOKEN = env("API_KEY")