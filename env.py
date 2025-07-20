import uuid

class Order:
    def __init__(self, side, price, size, timestamp):
        self.id = uuid.uuid4()
        self.side = side
        self.price = price
        self.size = size
        self.timestamp = timestamp

class TradingEnvironment():
    def __init__(self, starting_cash=10000):
        self.inventory = 0
        self.cash = starting_cash
        self.trade_log = []
        self.orders = []

    def market_buy(self, price, size, timestamp):
        cost = price * size
        if self.cash >= cost:
            self.inventory += size
            self.cash -= cost
            self.trade_log.append((timestamp, 'buy', price, size))
        else:
            print("Insufficient cash")

    def market_sell(self, price, size, timestamp):
        if self.inventory >= size:
            self.cash += price * size
            self.inventory -= size
            self.trade_log.append((timestamp, 'sell', price, size))
        else:
            print("Not enough inventory")

    def limit_order(self, price, side, size, timestamp):
        self.orders.append(Order(f'{side}', price, size, timestamp))

    def cancel_order(self):
        return

    def update_orders(self, current_price, timestamp):
        filled_orders = []

        for order in self.orders:
            if order.price >= current_price and order.side == 'buy':
                self.market_buy(order.price, order.size, timestamp)
            elif order.price <= current_price and order.side == 'sell':
                self.market_sell(order.price, order.size)
            filled_orders.append(order)
        
        for order in filled_orders:
            self.orders.remove(order)

    def current_value(self, price):
        return self.cash + self.inventory * price