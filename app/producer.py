from confluent_kafka import Producer
import time, requests, json, logging, sys
from settings import KAFKA_BOOTSTRAP_SERVER, KAFKA_TOPIC_SOURCE, REAL_TIME_TRAIN_URL, NUMBER_OF_RETRIES, HEADER, KAFKA_MESSAGE_SIZE_MAX, KAFKA_BATCH_SIZE, KAFKA_COMPRESSION_TYPE, KAFKA_LINGER, log_path_producer

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s', 
    handlers=[
        logging.FileHandler(log_path_producer), 
        logging.StreamHandler()
    ]
)

producer = Producer({'bootstrap.servers': KAFKA_BOOTSTRAP_SERVER, 
        'message.max.bytes': KAFKA_MESSAGE_SIZE_MAX,
        'compression.type': KAFKA_COMPRESSION_TYPE,
        'batch.size': KAFKA_BATCH_SIZE,  # Maximum batch size in bytes (16 KB)
        'linger.ms': KAFKA_LINGER,  # Wait up to 10 ms to accumulate messages before sending the batch
        'acks': 'all', # aknologe all replicas
    })


def delivery_report(err: any, msg) -> None:
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        logging.error(f'Message delivery failed: {err}')
    else:
        logging.info(f'Message delivered to topic: {msg.topic()} [{msg.partition()}]')

def fetch_train_data() -> any:
    """ Fetch real-time train data from the API """
    
    response = requests.get(REAL_TIME_TRAIN_URL, headers=HEADER)
    if response.status_code == 200:
        return response.json()

    logging.info(f"Failed to fetch data: {response.status_code}")
    return None

def send_data_to_kafka(data: dict) -> None:
    """ Send fetched train data to Kafka """

    try:
        data_str = json.dumps(data)
        logging.info(f"Message size: {str(sys.getsizeof(data_str)/ (1024 * 1024))}")
        producer.produce(KAFKA_TOPIC_SOURCE, data_str, callback=delivery_report)
        producer.flush()
        logging.info("message sent")
    except Exception as e:
        logging.error(f"Error sending data to Kafka: {e}")

tries = 0
while True:
    logging.info("Fetching train data...")

    train_data = fetch_train_data()
    if train_data:
        send_data_to_kafka(train_data)

        logging.info(" ------------  Waiting for 2 minute... -------------------")
        tries = 0
        time.sleep(120)
    else:
        tries += 1
        logging.info(f"No data fetched. Retrying ({tries})...")
        time.sleep(30)

    if tries > NUMBER_OF_RETRIES:
        break
