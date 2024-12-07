from policy import Policy

class ProdObj:
    size = [0,0]    # list of 2
    demand = 0      # int
    def __init__(self, insize, indemand):
        self.size = insize
        self.demand = indemand
    def __init__(self, indict): # indict is dict
        self.size = indict["size"]
        self.demand = indict["quantity"]
    def __lt__(self, other):
        return (self.size[0] * self.size[1] < other.size[0] * other.size[1])
class StockObj: #used to handle stocks that are used, and to manage the area that is used of each used stock
    def __init__(self, instock, original_index):
        """
        Initialize a StockObj instance.

        Args:
            instock (numpy array): 2D array representing the stock. Unused areas are typically marked as -2.
            original_index (int): The original index of the stock in the observation for tracking purposes.
        """
        self.arr = instock  # 2D numpy array representing the stock layout
        self.height = np.sum(np.any(instock != -2, axis=0))  # Effective height of stock
        self.width = np.sum(np.any(instock != -2, axis=1))   # Effective width of stock
        self.rarea = instock.size  # Total area of the stock
        self.used = np.any(instock != -2)  # Mark as used if any product is placed
        self.orgidx = original_index  # Original index for reference

    def __lt__(self, other):
        """Compare StockObj instances by remaining area (for sorting)."""
        return self.rarea < other.rarea

    def can_fit(self, prod_size):
        """
        Check if a product of given size can fit in the stock.

        Args:
            prod_size (tuple): (width, height) of the product.

        Returns:
            bool: True if the product can fit, False otherwise.
        """
        prod_w, prod_h = prod_size
        return self.width >= prod_w and self.height >= prod_h

    def find_position(self, prod_size):
        """
        Find a valid position for the product within the stock.

        Args:
            prod_size (tuple): (width, height) of the product.

        Returns:
            tuple or None: (x, y) position where the product can fit, or None if it doesn't fit.
        """
        prod_w, prod_h = prod_size
        for x in range(self.width - prod_w + 1):
            for y in range(self.height - prod_h + 1):
                # Check if all positions within the product's dimensions are free
                if np.all(self.arr[y:y+prod_h, x:x+prod_w] == -2):
                    return x, y
        return None

    def place_product(self, position, prod_size):
        """
        Place the product in the stock and update its state.

        Args:
            position (tuple): (x, y) position to place the product.
            prod_size (tuple): (width, height) of the product.

        Returns:
            None
        """
        x, y = position
        prod_w, prod_h = prod_size
        self.arr[y:y+prod_h, x:x+prod_w] = 1  # Mark the area as used
        self.rarea -= prod_w * prod_h  # Update remaining area
        self.used = True  # Mark stock as used
    
class Policy2310561(Policy):
    def __init__(self):
        # Student code here
        pass

    def get_action(self, observation, info):
        # Student code here
        aux_list = observation["products"]  # tuple of dicts
        # Create a list of ProdObj instances
        list_prods = [ProdObj(prod) for prod in aux_list]
        list_prods.sort(reverse=True)  # Sort products by area, largest to smallest

        # Create a list of StockObj instances
        stocks = [StockObj(stock, idx) for idx, stock in enumerate(observation["stocks"])]
        used_stocks = sorted([s for s in stocks if s.used], key=lambda s: s.rarea)
        unused_stocks = sorted([s for s in stocks if not s.used], key=lambda s: -s.rarea)

        # Combine stocks in priority order: used stocks first, then unused stocks
        ordered_stocks = used_stocks + unused_stocks
        
        # Sort the products in ascending order by area
        list_prods = list()  # list of ProdObj
        for prod in aux_list:
            #prod is tuple
            prod_obj = ProdObj(prod)
            list_prods.append(prod_obj)
        list_prods.sort(reverse=True)
    
        prod_size = [0, 0]
        stock_idx = -1
        pos_x, pos_y = None, None
    
        # Pick a product that has demand > 0
        for prod in list_prods:
            if prod.demand > 0:
                prod_size = prod.size
    
                # Loop through all stocks (this will be changed to using StockObj classes; the algorithm will try to use ordered_used_stocks before getting a new stock.)
                for i, stock in orderer_stocks:
                    stock_w = stock.width
                    stock_h = stock.height
                    prod_w, prod_h = prod_size
    
                    # Check both original and rotated sizes
                    possible_orientations = [(prod_w, prod_h), (prod_h, prod_w)]

                    for orientation in possible_orientations:
                        prod_w, prod_h = orientation #prod_w and _h can now be either orientation
    
                        if stock_w < prod_w or stock_h < prod_h:
                            continue
    
                        pos_x, pos_y = None, None
                        for x in range(stock_w - prod_w + 1):
                            for y in range(stock_h - prod_h + 1):
                                if stock.can_fit((prod_w, prod_h)):
                                    x, y = stock.find_position((prod_w, prod_h))
                                    #valid position found
                                    pos_x, pos_y = x, y #place in either orientation
                                    stock_idx = i
                                    prod_size = [prod_w, prod_h] #update prod_size
                                    stock.place_product((pos_x, pos_y), (prod_w, prod_h))
                                    used_stocks = sorted([s for s in stocks if s.used], key=lambda s: s.rarea)
                                    unused_stocks = sorted([s for s in stocks if not s.used], key=lambda s: -s.rarea)
                                    ordered_stocks = used_stocks + unused_stocks
                                    break
                            if pos_x is not None and pos_y is not None:
                                break
    
                        if pos_x is not None and pos_y is not None:
                            break
    
                    if pos_x is not None and pos_y is not None:
                        break
    
            if pos_x is not None and pos_y is not None:
                break
    
        return {"stock_idx": stock_idx, "size": prod_size, "position": (pos_x, pos_y)}



    # Student code here
    # You can add more functions if needed
