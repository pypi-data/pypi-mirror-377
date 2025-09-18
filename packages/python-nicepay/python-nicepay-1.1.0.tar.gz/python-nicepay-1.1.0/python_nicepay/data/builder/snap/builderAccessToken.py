class AccessToken:
    def __init__(self,
                 grantType,
                 additionalInfo):
        self.grantType = grantType
        self.additionalInfo = additionalInfo

    def jsonAccessToken(self):
        return ({
            "grantType": self.grantType,
            "additionalInfo": self.additionalInfo
        })


class BuilderAccessToken:
    def __init__(self):
        self.grantType = None
        self.additionalInfo = None

    def setGrantType(self, grantType):
        self.grantType = grantType

        return self

    def setAdditionalInfo(self, additionalInfo):
        self.additionalInfo = additionalInfo
        return self


class BuildAccessToken(BuilderAccessToken):
    def build(self):
        return AccessToken(
            self.grantType,
            self.additionalInfo
        )
