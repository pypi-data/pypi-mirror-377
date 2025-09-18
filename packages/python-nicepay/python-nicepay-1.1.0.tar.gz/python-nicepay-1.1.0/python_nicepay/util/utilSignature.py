import base64
import hashlib
import hmac

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

from python_nicepay.util.utilLogging import Log

class Signature:
    log = Log()

    @staticmethod
    def signSHA256RSA(stringToSign, privateKey):
        try:
            b1 = base64.b64decode(privateKey)
            key = RSA.importKey(b1)
            signer = PKCS1_v1_5.new(key)
            digest = SHA256.new()
            digest.update(stringToSign.encode('utf-8'))
            signature = signer.sign(digest)
            hexSignature = base64.b64encode(signature).decode('utf-8')
            return hexSignature
        except Exception as e:
            Signature.log.error("Error Generate Signature:" + e)
            return ''

    @staticmethod
    def getSignature(accessToken, requestBody, endpoint, timestamp, staticKey, httpMethod):
        Signature.log.info("util - Request Endpoint : " + endpoint)
        data = f"{httpMethod}:{endpoint}:{accessToken}:{requestBody}:{timestamp}"
        Signature.log.info("util - StringDataToSign: " + data)
        try:
            sign = Signature.hmacSHA512EncodeBase64(staticKey, data)
            Signature.log.info("util - Signature: " + sign)
            return sign
        except:
            Signature.log.error("Error Generate Signature - getSignature")

    @staticmethod
    def hmacSHA512EncodeBase64(key, data):
        hmacObj = hmac.new(key.encode('utf-8'), data.encode('utf-8'), hashlib.sha512)
        hmacBytes = hmacObj.digest()
        base64Encoded = base64.b64encode(hmacBytes).decode('utf-8')
        return base64Encoded

    @staticmethod
    def sha256EncodeHex(data):
        sha256Hash = hashlib.sha256(data.encode('utf-8')).digest()
        hexEncoded = sha256Hash.hex()
        return hexEncoded
