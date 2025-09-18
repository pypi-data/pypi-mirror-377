class CartData:
    def __init__(self,
                 count,
                 item):
        self.count = count
        self.item = item

    def jsonCartData(self):
        return ({
            "count": self.count,
            "item": [self.item]
        })


class BuilderCartData:
    def __init__(self):
        self.count = None
        self.item = None

    def setCount(self, count):
        self.count = count
        return self

    def setItem(self, item):
        self.item = item
        return self


class BuildCartData(BuilderCartData):
    def build(self):
        return CartData(
            self.count,
            self.item
        )
