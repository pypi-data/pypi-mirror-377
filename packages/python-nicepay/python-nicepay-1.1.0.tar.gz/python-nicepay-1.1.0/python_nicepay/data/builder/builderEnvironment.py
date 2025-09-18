from python_nicepay.constants.constantsGeneral import ConstantsGeneral

class Environment:
    def __init__(self,
                 isProduction,
                 isCloud):
        self.isProduction = isProduction
        self.isCloud = isCloud

    def getHost(self):
        if self.isProduction:
            if self.isCloud:
                return ConstantsGeneral.CLOUD_PRODUCTION_BASE_URL
            else:
                return ConstantsGeneral._PRODUCTION_BASE_URL

        else:
            if self.isCloud:
                return ConstantsGeneral.CLOUD_SANDBOX_BASE_URL
            else:
                return ConstantsGeneral._SANDBOX_BASE_URL


    def getDefault(self):
        return "DEFAULT"

class BuilderEnvironment:
    def __init__(self):
        self.setProduction = None
        self.setCloud = None

    def isProduction(self, isProduction):
        self.setProduction = isProduction
        return self

    def isCloud(self, isCloud):
        self.setCloud = isCloud
        return self

class BuildEnvironment(BuilderEnvironment):
    def build(self):
        return (Environment
                (self.setProduction, self.setCloud
                 ))
