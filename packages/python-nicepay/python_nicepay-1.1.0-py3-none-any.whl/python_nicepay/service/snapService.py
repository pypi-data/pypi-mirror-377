import json
from python_nicepay.constants.constantsGeneral import ConstantsGeneral
from python_nicepay.constants.constantsEndpoint import ConstantsEndpoints
from python_nicepay.data.builder.snap.dataGenerator import dataGenerator
from python_nicepay.config.apiClient import apiClient
from python_nicepay.util.utilGeneral import General
from python_nicepay.util.utilLogging import Log

log = Log()
# host = ConstantsGeneral.getSandboxBaseUrl()  # ENVIRONMENT


class SnapService:
    log.headers("Initialization")
    @staticmethod
    def serviceOAUTH(body, environment):
        host = environment.getHost()

        headers = dataGenerator.getOAUTHHeader()
        endpoint = ConstantsEndpoints.accessToken()
        response = apiClient.send(host,
                                  headers,
                                  body,
                                  endpoint)
        infoClass = General.endpointChecker(endpoint)

        a = json.dumps(response)
        data = json.loads(a)
        accessToken = data["accessToken"]

        log.info(f"{infoClass} - Endpoint : " + endpoint)
        log.info(f"{infoClass} - FullUrl : " + host + endpoint)
        log.info(f"{infoClass} - Headers : " + json.dumps(headers))
        log.info(f"{infoClass} - Body : " + json.dumps(body))
        log.info(f"{infoClass} - Response : " + json.dumps(response))
        log.info(f"{infoClass} - AccessToken : " + accessToken)

        return accessToken

    @staticmethod
    def serviceTransaction(bodyAccessToken, body, endpoint, environment, httpMethod="POST"):

        global receiveResponse
        host = environment.getHost()
        receiveAccessToken = SnapService.serviceOAUTH(bodyAccessToken, environment)
        log.headers("Services Init")
        headerTransaction = dataGenerator.getTransactionHeader(receiveAccessToken,
                                                               body,
                                                               endpoint,httpMethod)

        infoClass = General.endpointChecker(endpoint)
        if httpMethod == "POST":
            receiveResponse = apiClient.send(host,
                                         headerTransaction,
                                         body,
                                         endpoint)
        elif httpMethod == "DELETE":
            receiveResponse = apiClient.sendDelete(host,
                                                   headerTransaction,
                                                   body,
                                                   endpoint)

        log.info(f"{infoClass} - Endpoint : " + endpoint)
        log.info(f"{infoClass} - FullUrl : " + host + endpoint)
        log.info(f"{infoClass} - Headers : " + json.dumps(headerTransaction))
        log.info(f"{infoClass} - Body : " + json.dumps(body))
        log.info(f"{infoClass} - Response : " + json.dumps(receiveResponse))

        return
