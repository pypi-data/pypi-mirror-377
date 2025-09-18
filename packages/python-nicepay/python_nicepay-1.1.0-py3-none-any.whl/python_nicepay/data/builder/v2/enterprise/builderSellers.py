class Sellers:
    def __init__(self,
                 sellersId,
                 sellersNm,
                 sellersEmail,
                 sellersUrl,
                 sellersAddress):
        self.sellersId = sellersId
        self.sellersNm = sellersNm
        self.sellersEmail = sellersEmail
        self.sellersUrl = sellersUrl
        self.sellersAddress = sellersAddress

    def jsonSellers(self):
        return ([{
            "sellersId": self.sellersId,
            "sellersNm": self.sellersNm,
            "sellersEmail": self.sellersEmail,
            "sellersUrl": self.sellersUrl,
            "sellersAddress": self.sellersAddress,
        }])


class BuilderSellers:
    def __init__(self):
        self.sellersId = None
        self.sellersNm = None
        self.sellersEmail = None
        self.sellersUrl = None
        self.sellersAddress = None

    def setSellerId(self, sellerId):
        self.sellersId = sellerId
        return self

    def setSellerNm(self, sellerNm):
        self.sellersNm = sellerNm
        return self

    def setSellerEmail(self, sellerEmail):
        self.sellersEmail = sellerEmail
        return self

    def setSellerUrl(self, sellerUrl):
        self.sellersUrl = sellerUrl
        return self

    def setSellerAddress(self, sellerAddress):
        self.sellersAddress = sellerAddress
        return self


class BuildSeller(BuilderSellers):
    def build(self):
        return Sellers(
            self.sellersId,
            self.sellersNm,
            self.sellersEmail,
            self.sellersUrl,
            self.sellersAddress
        )
