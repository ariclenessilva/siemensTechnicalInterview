import os

KAFKA_BOOTSTRAP_SERVER = 'broker:9092'
KAFKA_TOPIC_SOURCE = 'live_train_data_source'
KAFKA_TOPIC_SINK = 'live_train_data_sink'
KAFKA_MESSAGE_SIZE_MAX = 20971520
KAFKA_BATCH_SIZE = 16384
KAFKA_COMPRESSION_TYPE = 'zstd'
KAFKA_LINGER = 10

FAUST_APP_NAME = "siemensTIfaust"

REAL_TIME_TRAIN_URL = "https://rata.digitraffic.fi/api/v1/live-trains/"
HEADER = {"Digitraffic-User": "DemoInterview"}

NUMBER_OF_RETRIES = 5

log_folder = "/tmp/logs"
if not os.path.exists(log_folder):
    os.makedirs(log_folder)
log_path_producer = os.path.join(log_folder, "dailylogProducer.log")
log_path_consumer = os.path.join(log_folder, "dailylogConsumer.log")


data_folder = "/tmp/data"
if not os.path.exists(data_folder):
    os.makedirs(data_folder)