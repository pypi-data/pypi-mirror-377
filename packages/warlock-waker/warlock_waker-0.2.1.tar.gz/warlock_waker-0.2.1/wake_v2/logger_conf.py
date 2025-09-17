import json
import os
import socket


def extract_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP


ip_address = extract_ip()

REDIS_CONF_STR = os.getenv('LOG_REDIS_CONF', "{}")
REDIS_CONF = json.loads(REDIS_CONF_STR)
SERVICE_NAME = os.getenv('SERVICE_NAME', 'service')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
LOGGER_PATH = os.getenv('LOGGER_PATH', f'/tmp/usr/logger/{SERVICE_NAME}')
LOG_VERSION = os.getenv('LOG_VERSION', "0.0.2")
LOG_CONSUMER_KEY = os.getenv('LOG_CONSUMER_KEY', "warlock-wake_v2-v1")
LOG_ENABLE_STR = os.environ.get("LOG_TOOTLE")
LOG_ENABLE = True if LOG_ENABLE_STR is None else LOG_ENABLE_STR == "True"
KAFKA_BOOTSTRAP = os.getenv('KAFKA_BOOTSTRAP', '10.10.10.1:9092')
LOG_TO_REDIS_VAL = os.environ.get("LOG_TO_REDIS")
LOG_TO_REDIS = True if LOG_TO_REDIS_VAL is None else LOG_TO_REDIS_VAL == "True"
LOG_TYPE = os.environ.get("LOG_TYPE")
LOG_TYPE = "REDIS" if LOG_TYPE is None else LOG_TYPE
