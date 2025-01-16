from confluent_kafka import Consumer
import time, requests, json, logging, sys, os
from settings import KAFKA_BOOTSTRAP_SERVER, KAFKA_TOPIC_SOURCE, REAL_TIME_TRAIN_URL, NUMBER_OF_RETRIES, HEADER, KAFKA_MESSAGE_SIZE_MAX, KAFKA_BATCH_SIZE, KAFKA_COMPRESSION_TYPE, KAFKA_LINGER, log_path_consumer, data_folder
from models import TrainDataModel
from datetime import datetime

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s', 
    handlers=[
        logging.FileHandler(log_path_consumer), 
        logging.StreamHandler()
    ]
)

c = Consumer({
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVER,
    'message.max.bytes': KAFKA_MESSAGE_SIZE_MAX,
    'group.id': 'demo',
    'auto.offset.reset': 'earliest'
})

c.subscribe([KAFKA_TOPIC_SOURCE])

while True:
    msg = c.poll(1.0)

    if msg is None:
        continue
    if msg.error():
        logging.error("Consumer error: {}".format(msg.error()))
        continue
    
    message_value = msg.value().decode('utf-8')
    data_for_report = TrainDataModel(**{"missing_required_fields":[], "duplicated_trainid":[], "num_records":0, "columns_with_issues": [], "data": json.loads(message_value)})
    
    current_datetime = datetime.now()
    current_datetime = current_datetime.strftime("%Y_%m_%d %H_%M_%S")
    temp_file_path = os.path.join(data_folder, f"train_data {current_datetime}.json")
    with open(temp_file_path, 'w') as json_file:
        json.dump(data_for_report.model_dump(), json_file)
    logging.info(f"JSON data saved to: {temp_file_path}")

    logging.info('Received message')

c.close()