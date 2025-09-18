from datetime import datetime

from python_nicepay.constants.constantsGeneral import ConstantsGeneral
from python_nicepay.data.builder import builderEnvironment
from python_nicepay.data.model.ccMigsRequest import CCMigsRequest
from python_nicepay.service.v1EnterpriseService import ServiceNicepayV1


class testCCOnePassDo:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    merchantKey = ConstantsGeneral.getMerchantKey()
    amt = 1000

    request = CCMigsRequest(
        instmntType="1",
        instmntMon="1",
        referenceNo="",
        onePassToken="",
        callbackUrl="",
        cardCvv=""
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    response = ServiceNicepayV1.serviceCardMigsV1(request.__dict__, environment)
