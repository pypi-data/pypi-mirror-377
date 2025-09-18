import json

from python_nicepay.config.apiClient import apiClient
from python_nicepay.constants.constantsEndpoint import ConstantsEndpoints
from python_nicepay.constants.constantsGeneral import ConstantsGeneral
from python_nicepay.util.utilLogging import Log

log = Log()
host = ConstantsGeneral.getSandboxBaseUrl()  # Environment

class ServiceNicepayV1:
    log.headers("Initialization")

    # REGISTRATION REQUEST
    @staticmethod
    def serviceRequestV1(body, environment):
        host = environment.getHost()

        endpoint = ConstantsEndpoints.requestRegistrationV1()
        data = apiClient.sendUrl(host,
                              body,
                              endpoint)

        response = json.dumps(data)
        log.info("Request Data : " + json.dumps(body))
        log.info("Response Data : " + json.dumps(data))
        return response

    @staticmethod
    def serviceCancelV1(data, environment):

        host = environment.getHost()
        endpoint = ConstantsEndpoints.cancelV1()
        response = apiClient.sendUrl(host,
                                  data,
                                  endpoint)
        log.info("Request Data : " + json.dumps(data))
        log.info("Response Data : " + json.dumps(response))
        return response

    # INQUIRY REQUEST
    @staticmethod
    def serviceInquiryV1(data, environment):
        host = environment.getHost()

        endpoint = ConstantsEndpoints.inquiryV1()
        response = apiClient.sendUrl(host,
                                  data,
                                  endpoint)
        log.info("Request Data : " + json.dumps(data))
        log.info("Response Data : " + json.dumps(response))

    @staticmethod
    def serviceEwalletRequestV1(body, environment):
        host = environment.getHost()

        endpoint = ConstantsEndpoints.requestRegistrationV1Ewallet()
        data = apiClient.get(host,
                             body,
                             endpoint)

        response = json.dumps(data)
        log.info("Request Data : " + json.dumps(body))
        log.info("Response Data : " + json.dumps(data))
        return response

    # CREDIT CARD REGISTRATION (ONE PASS TOKEN)
    @staticmethod
    def serviceCardRegistrationV1(body, environment):
        host = environment.getHost()

        endpoint = ConstantsEndpoints.requestOnePassToken()
        data = apiClient.sendUrl(host,
                              body,
                              endpoint)

        response = json.dumps(data)
        log.info("Request Data : " + json.dumps(body))
        log.info("Response Data : " + json.dumps(data))
        return response

    @staticmethod
    def serviceCard3dsV1(body, environment):
        host = environment.getHost()

        endpoint = ConstantsEndpoints.request3DSToken()
        data = apiClient.get(host,
                             body,
                             endpoint)

        response = json.dumps(data)
        log.info("Request Data : " + json.dumps(body))
        log.info("Response Data : " + json.dumps(data))
        return response

    @staticmethod
    def serviceCardMigsV1(body, environment):
        host = environment.getHost()

        endpoint = ConstantsEndpoints.requestMigsToken()
        data = apiClient.sendUrl(host,
                                 body,
                                 endpoint)

        response = json.dumps(data)
        log.info("Request Data : " + json.dumps(body))
        log.info("Response Data : " + json.dumps(data))
        return response