import json

from python_nicepay.config.apiClient import apiClient
from python_nicepay.constants.constantsEndpoint import ConstantsEndpoints
from python_nicepay.constants.constantsGeneral import ConstantsGeneral
from python_nicepay.data.builder.v2.professional.dataGenerator import DataGenerator
from python_nicepay.util.utilLogging import Log

log = Log()

host = ConstantsGeneral.getSandboxBaseUrl()


class ServiceNicepayV1:
    log.headers("Initialization")


    @staticmethod
    def serviceRequestV1(body, environment):

        host = environment.getHost()
        headers = DataGenerator.getTransactionHeader()
        endpoint = ConstantsEndpoints.registrationRedirectV1()
        response = apiClient.sendUrl(host,
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
    def serviceRedirectV1(body, environment):
        host = environment.getHost()
        tXid = ServiceNicepayV1.serviceRequestV1(body, environment)
        endpoint = ConstantsEndpoints.inquiryRedirectV1()
        response = apiClient.redirect(host,
                                      tXid,
                                      endpoint)
        log.info("Request To Redirect NICEPAY Secure Payment Page")
        log.info("Full URL   : " + response)
        log.info("Redirect To NICEPAY Secure Payment Page")

