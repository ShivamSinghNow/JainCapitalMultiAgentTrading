from threading import Thread
from create_topics import create_topics
from stream_tick import stream_tick
from stream_ob import stream_ob
from stream_trades import stream_trades

# set ticker here
ticker = 'BTC'

# duration of time running (set to 'forever' if forever)
duration = 10

if __name__ == '__main__':
    # checking if topics are created in redpanda already, creating if not
    create_topics(ticker)

    # creating individual threads per websocket stream
    #t1 = Thread(target = stream_tick, args = (ticker, duration))
    t2 = Thread(target = stream_ob, args = (ticker, duration)) 

    # starting and joining threads
    #t1.start()
    t2.start()

    #t1.join()
    t2.join()
