from kafka import KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError
from secret import REDPANDA_PASS, REDPANDA_USER

def create_topics(ticker):
    print(f'Creating RedPanda topics for {ticker}...')

    # launching admin object
    admin = KafkaAdminClient(
    bootstrap_servers="d0lhgbluksd069p01f90.any.us-west-2.mpx.prd.cloud.redpanda.com:9092",
    security_protocol="SASL_SSL",
    sasl_mechanism="SCRAM-SHA-512",
    sasl_plain_username=REDPANDA_USER,
    sasl_plain_password=REDPANDA_PASS,
    )

    # creating order book topic in redpanda
    try:
        topic = NewTopic(name=f"{ticker}_ob_v1", num_partitions=1, replication_factor=-1, replica_assignments=[])
        admin.create_topics(new_topics=[topic])
        print(f"    -Created topic {ticker}_ob_v1")

    except TopicAlreadyExistsError as e:
        print(f"    -Topic {ticker}_ob_v1 already exists")

    # creating order book topic in redpanda
    try:
        topic = NewTopic(name=f"{ticker}_trades_v1", num_partitions=1, replication_factor=-1, replica_assignments=[])
        admin.create_topics(new_topics=[topic])
        print(f"    -Created topic {ticker}_trades_v1")

    except TopicAlreadyExistsError as e:
        print(f"    -Topic {ticker}_trades_v1 already exists")

    # creating tick topic in redpanda
    try: 
        topic = NewTopic(name=f"{ticker}_tick_v1", num_partitions=1, replication_factor=-1, replica_assignments=[])
        admin.create_topics(new_topics=[topic])
        print(f"    -Created topic {ticker}_tick_v1")

    except TopicAlreadyExistsError as e:
        print(f"    -Topic {ticker}_tick_v1 already exists")

    # closing admin
    finally:
        admin.close()
