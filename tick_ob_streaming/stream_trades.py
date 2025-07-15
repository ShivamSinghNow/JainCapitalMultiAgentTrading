from kafka import KafkaProducer
from kafka.errors import KafkaError
import websocket
import json
import time
import threading
import pytz
from datetime import datetime
from secret import COINAPI_KEY, REDPANDA_PASS, REDPANDA_USER

def stream_trades(ticker, duration):
    print(f'\nStreaming trades for {ticker}...')

    # launching kafka producer object
    producer = KafkaProducer(
    bootstrap_servers="d0lhgbluksd069p01f90.any.us-west-2.mpx.prd.cloud.redpanda.com:9092",
    security_protocol="SASL_SSL",
    sasl_mechanism="SCRAM-SHA-512",
    sasl_plain_username=REDPANDA_USER,
    sasl_plain_password=REDPANDA_PASS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    key_serializer=lambda v: v.encode("utf-8"),
    linger_ms=0
    )

    # Kafka sucess and error functions
    def on_success(metadata):
        print(f"    -Sent to topic '{metadata.topic}' at offset {metadata.offset}")

    def on_error_kafka(e):
        print(f"Error sending message: {e}")




    # websocket message functions
    def on_message(ws, message):
        # loading and timestamping message
        data = json.loads(message)
        data["time_ingested"] = datetime.now(pytz.UTC).isoformat().replace('+00:00', 'Z')

        # sending data to redpanda
        future = producer.send(
        f"{ticker}_trades_v1",
        key=ticker,
        value=data
        )

        # outcome handling
        future.add_callback(on_success)
        future.add_errback(on_error_kafka)


    def on_error_ws(ws, error):
        print(f"Error: {error}")

    def on_close(ws, close_status_code, close_msg):
        print("\n### conection to trades closed ###")

    def on_open(ws):
        print('\n###  connection to trades opened ###')

        # streaming message
        hello_message = {
            "type": "hello",
            "apikey": COINAPI_KEY,  
            "subscribe_data_type": ["trade"],
            "subscribe_filter_exchange_id": ['COINBASE'],
            "subscribe_filter_symbol_id": ["BTC"]
        }

        # sending data
        ws.send(json.dumps(hello_message))




    # creating webscoket
    ws = websocket.WebSocketApp(
        "wss://ws.coinapi.io/v1",
        header=[f"X-CoinAPI-Key: {COINAPI_KEY}"],
        on_open=on_open,
        on_message=on_message,
        on_error=on_error_ws,
        on_close=on_close
    )

    if duration == 'forever':
        # running forever
        ws.run_forever()
    
    else:
        # threading webscoket
        wst = threading.Thread(target=ws.run_forever)
        wst.start()

        # sleeping for set time 
        time.sleep(duration)

        # closing websocket
        print(f"\nClosing WebSocket after {duration} seconds...")
        ws.close()
        producer.close()
