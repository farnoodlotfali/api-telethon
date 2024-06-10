

def returnSearchValue(val):
    return val.group(1) if val else None

def sizeAmount(price):
    prices = [
        { 'price':0.01, 'size':2000 },
        { 'price':0.1, 'size':200 },
        { 'price':1, 'size':20 },
        { 'price':5, 'size':2 },
        ]
    
    length = len(prices) - 1
    for i in range(len(prices)):
        if i == length: return prices[0]["size"]
        if prices[i]["price"] <= float(price) < prices[i+1]["price"]:
            return prices[i+1]["size"]
        
