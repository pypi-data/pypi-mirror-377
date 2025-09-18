import json

from python_nicepay.config.apiClient import apiClient
from python_nicepay.constants.constantsEndpoint import ConstantsEndpoints
from python_nicepay.constants.constantsGeneral import ConstantsGeneral
from python_nicepay.data.builder.v2.professional.dataGenerator import DataGenerator
from python_nicepay.util.utilLogging import Log

log = Log()

host = ConstantsGeneral.getSandboxBaseUrl()


class ServiceNicepay:
    log.headers("Initialization")

    @staticmethod
    def serviceRequest(body, environment):

        host = environment.getHost()
        headers = DataGenerator.getTransactionHeader()
        endpoint = ConstantsEndpoints.registrationRedirect()
        response = apiClient.send(host,
                                  headers,
                                  body,
                                  endpoint)

        a = json.dumps(response)
        data = json.loads(a)
        tXid = data["tXid"]

        log.info("Request Registration Transaction")
        log.info("Request Headers : " + json.dumps(headers))
        log.info("Request Data    : " + json.dumps(body))
        log.info("Response Data   : " + json.dumps(response))

        return tXid

    @staticmethod
    def serviceRedirect(body, environment):
        host = environment.getHost()
        tXid = ServiceNicepay.serviceRequest(body, environment)
        endpoint = ConstantsEndpoints.paymentRedirect()
        response = apiClient.redirect(host,
                                      tXid,
                                      endpoint)
        log.info("Request To Redirect NICEPAY Secure Payment Page")
        log.info("Full URL   : " + response)
        log.info("Redirect To NICEPAY Secure Payment Page")

    @staticmethod
    def serviceCancel(data):
        headers = DataGenerator.getTransactionHeader()
        endpoint = ConstantsEndpoints.cancel()
        response = apiClient.send(host,
                                  headers,
                                  data,
                                  endpoint)
        log.info("Request Cancel Transaction")
        log.info("Request Headers : " + json.dumps(headers))
        log.info("Request Data    : " + json.dumps(data))
        log.info("Response Data   : " + json.dumps(response))

        return response

    @staticmethod
    def serviceInquiry(data):
        headers = DataGenerator.getTransactionHeader()
        endpoint = ConstantsEndpoints.inquiry()
        response = apiClient.send(host,
                                  headers,
                                  data,
                                  endpoint)
        log.info("Request Inquiry Transaction")
        log.info("Request Headers : " + json.dumps(headers))
        log.info("Request Data    : " + json.dumps(data))
        log.info("Response Data   : " + json.dumps(response))

        return response
