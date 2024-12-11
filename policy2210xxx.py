from policy import Policy
import numpy as np

class ProdObj:
    def __init__(self, insize, indemand):
        self.size = insize      # list of 2 int
        self.demand = indemand  # int
    def __init__(self, indict): # indict is dict
        self.size = indict["size"]
        self.demand = indict["quantity"]
    def __lt__(self, other):
        return (self.size[0] * self.size[1] < other.size[0] * other.size[1])

class StockObj:
    def __init__(self, instock, original_index): # instock is numpy array
        self.arr = instock
        self.height = np.sum(np.any(instock != -2, axis=0))
        self.width = np.sum(np.any(instock != -2, axis=1))
        self.rmarea = self.height * self.width
        self.orgidx = original_index
    def __lt__(self, other):
        return (self.rmarea < other.rmarea)

class Policy2210xxx(Policy):    
    def __init__(self):
        # Student code here
        self.used_stocks = list()    # used stocks are kept in ascending order
        self.unused_stocks = list()  # while unused stocks are kept in descending order
        self.previous_stock_states = None  # To store the previous state of all stocks
        self.first_stock = None  # this var is used to track the first used stock
    
    def reset(self):
        # Student code here
        self.used_stocks.clear()
        self.unused_stocks.clear()
        self.first_stock = None
        self.previous_stock_states = None
    
    def get_action(self, observation, info):
        print("get_action called")
        # Check for environment reset using stock array contents
        current_stock_states = [stock.copy() for stock in observation["stocks"]]
        # Stock array content reset detection
        if self.previous_stock_states is not None:
            # Compare current stock arrays with previous ones
            for prev_stock, curr_stock in zip(self.previous_stock_states, current_stock_states):
                if not np.array_equal(prev_stock, curr_stock):
                    print("Environment reset detected: Stock contents have changed.")
                    self.reset()
                    break #for some reason having this leads to the code sometimes enterring a brief loop; they dont actually place any product and eventually exit, but i am not sure if this messes with the product demands (and thus making the algorithm not able to actually fulfill the specification were the demands manually specified). However it if doesn't then this program works flawlessly except for the log.
        self.previous_stock_states = current_stock_states
        
        # Preparing products
        list_prods = list()
        for prod in observation["products"]:
            prod_obj = ProdObj(prod)
            list_prods.append(prod_obj)
        list_prods.sort(reverse=True)

        prod_size = [0, 0]
        stock_idx = -1
        pos_x, pos_y = 0, 0

        # Preparing stocks
        if self.first_stock is None:
            print("Initializing stocks...")
            for i, stock in enumerate(observation["stocks"]):
                stock_obj = StockObj(stock, i)
                if self.first_stock is None:
                    self.first_stock = stock_obj
                    print(f"Initialized first_stock with rmarea: {self.first_stock.rmarea}")
                self.unused_stocks.append(stock_obj)
            self.unused_stocks.sort(reverse=True)

        # Debug: Update the `previous_rmarea` for the first_stock
        if self.first_stock is not None:
            self.previous_rmarea = self.first_stock.rmarea
        # ACTUAL PLACING PRODUCTS INTO STOCKS
        print("Placing Products...")
        # Ensure product has demand > 0
        for prod in list_prods:
            if prod.demand > 0:
                prod_size = prod.size
                # Iterate through used stocks
                pos_x = None
                pos_y = None
                best_fit_area = 10001
                best_fit_idx = -1
                for stock in self.used_stocks:
                    stock_w = stock.width
                    stock_h = stock.height
                    prod_w, prod_h = prod.size
                    if stock_w >= prod_w and stock_h >= prod_h:
                        pos_x, pos_y = None, None
                        for x in range(stock_w - prod_w + 1):
                            for y in range(stock_h - prod_h + 1):
                                if self._can_place_(stock.arr, (x, y), prod_size) and stock.rmarea < best_fit_area:
                                    best_fit_area = stock.rmarea
                                    best_fit_idx = stock.orgidx
                                    pos_x, pos_y = x, y
                                    break
                            if pos_x is not None and pos_y is not None:
                                break
                        if pos_x is None and pos_y is None:
                            for x in range(stock_w - prod_h + 1):
                                for y in range(stock_h - prod_w + 1):
                                    if self._can_place_(stock.arr, (x, y), prod_size[::-1]) and stock.rmarea < best_fit_area:
                                        prod_size = prod_size[::-1]
                                        best_fit_area = stock.rmarea
                                        best_fit_idx = stock.orgidx
                                        pos_x, pos_y = x, y
                                        break
                                if pos_x is not None and pos_y is not None:
                                    break
                        
                        if pos_x is not None and pos_y is not None:
                            stock_idx = best_fit_idx
                            stock.rmarea -= prod_w * prod_h
                            #self.used_stocks.sort()
                            break
                if pos_x is not None and pos_y is not None:
                    # if stock is placed, stop
                    break
                else:
                    # if not, use a new stock, place the product into it and update rmarea
                    new_stock = self.unused_stocks.pop(0)
                    stock_idx = new_stock.orgidx
                    pos_x = 0
                    pos_y = 0
                    self.used_stocks.append(new_stock)
                    #self.used_stocks.sort()

        return {"stock_idx": stock_idx, "size": prod_size, "position": (pos_x, pos_y)}

    # Student code here
    # You can add more functions if needed
