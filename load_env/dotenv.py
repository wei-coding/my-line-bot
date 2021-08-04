import os

def load_env():
    try:
        dot_env_file = open(".env", "r")
        lines = dot_env_file.readlines()
        for line in lines:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            assert type(value) == str
            os.environ[key] = value[1:-1]
    except IOError:
        print("No .env file.")
        exit(1)
