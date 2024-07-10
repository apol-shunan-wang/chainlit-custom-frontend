import os
from os.path import dirname, join
from dotenv import load_dotenv


def set_env_params():
    dotenv_path = join(dirname(__file__), '../', '.env')
    load_dotenv(dotenv_path)

