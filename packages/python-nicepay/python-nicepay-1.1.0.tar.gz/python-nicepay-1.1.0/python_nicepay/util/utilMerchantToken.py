import hashlib

from python_nicepay.util.utilLogging import Log

log = Log()


class MerchantToken:

    @staticmethod
    def getMerchantToken(data):
        merchantToken = hashlib.sha256(data.encode('utf-8')).hexdigest()
        log.info(f"util - Generated MerchantToken : {merchantToken}")
        return merchantToken
