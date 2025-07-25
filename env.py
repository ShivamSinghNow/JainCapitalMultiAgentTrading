import uuid
from datetime import datetime as dt

class Order:
    """
    Order object to keep track of all orders and their atributes
    """
    def __init__(self, side, price, size, timestamp, strategy):
        self.id = uuid.uuid4()
        self.side = side # side of trade e.g. buy/sell
        self.price = price # price of order
        self.size = size # size of order
        self.timestamp = timestamp # timestamp when the order was submitted
        self.strategy = strategy # strategy that created the orderr

class TradingEnvironment():
    """
    Environment where all trades and balances are kept track of
    """
    def __init__(self, backtester, starting_cash=10000):
        self.inventory = 0 # number of shares currently owned (will typically be a decimal
        self.cash = starting_cash # starting balance
        self.trade_log = [] # trade log of all completed trades
        self.orders = [] # list of all active orders
        self.bt = backtester # backtester that created the orde


    def market_buy(self, price, size):
        """
        Buys at given price and then updates inventory and cash respectively
        Appends trade log with timestamp, buy, price bought at and # of shares bought
        """
        cost = price * size
        if self.cash >= cost:
            self.inventory += size
            self.cash -= cost
            self.trade_log.append((dt.now().timestamp(), 'buy', price, size))
        else:
            print("Insufficient cash")


    def market_sell(self, price, size):
        """
        Sells at given price and then updates inventory and cash respectively
        Appends trade log with timestamp, sell, price bought at and # of shares bought
        """
        if self.inventory >= size:
            self.cash += price * size
            self.inventory -= size
            self.trade_log.append((dt.now().timestamp(), 'sell', price, size))
        else:
            print("Not enough inventory")


    def limit_order(self, side, price, size, strategy):
        """
        Creates order object and appends orders list
        """
        self.orders.append(Order(side=f'{side}', price=price, size=size, timestamp=dt.now().timestamp(), strategy=strategy))
        print(f"Order created: {side} {size} at {price} for {strategy}")
        print(f"Current orders: {len(self.orders)}")


    def cancel_order(self, order):
        """
        Removes a given order from thew active orders list
        """
        self.orders.remove(order)
        return


    def update_orders(self, current_price):
        """
        Updates all orders in current orders list and executes them respectively
        Then deletes filled orders from the order list
        """
        filled_orders = []
        canceled_orders = []

        for order in self.orders:
            if not any(t[0] == order.strategy for t in self.bt.active_strategies):
                canceled_orders.append(order)
                continue

            if order.price >= current_price and order.side == 'buy':
                self.market_buy(order.price, order.size)
                filled_orders.append(order)
                print(f"Order filled: {order.side} {order.size} at {order.price}")
            elif order.price <= current_price and order.side == 'sell':
                self.market_sell(order.price, order.size)
                filled_orders.append(order)
                print(f"Order filled: {order.side} {order.size} at {order.price}")

        for order in filled_orders + canceled_orders:
            if order in self.orders:
                self.cancel_order(order)
            else:
                print(f"Order {order.id} already removed")


    def current_value(self, price):
        """
        Retrieves the current value of cash + shares
        """
        return self.cash + self.inventory * price
