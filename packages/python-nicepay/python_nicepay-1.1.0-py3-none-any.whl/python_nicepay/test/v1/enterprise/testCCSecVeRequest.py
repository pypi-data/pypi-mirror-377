from datetime import datetime

from python_nicepay.constants.constantsGeneral import ConstantsGeneral
from python_nicepay.data.builder import builderEnvironment
from python_nicepay.data.builder.v1.enterprise.dataGenerator import DataGeneratorV1
from python_nicepay.data.builder.v2.enterprise import builderCartData
from python_nicepay.data.model.ccOnePassDo import CCOnePassDo
from python_nicepay.data.model.ccSecureVeRequest import CCSecureVeRequest
from python_nicepay.service.v1EnterpriseService import ServiceNicepayV1
from python_nicepay.util.utilMerchantToken import MerchantToken


class testCCOnePassDo:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    merchantKey = ConstantsGeneral.getMerchantKey()
    amt = 1000

    request = CCSecureVeRequest(
        onePassToken="878b864f158512110f63b057ed581f15644ea37e0561c5438b0cbf01ea2c1774",
        callbackUrl="https://www.nicepay.co.id/IONPAY_CLIENT/paymentResult.jsp",
        country="360"
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    response = ServiceNicepayV1.serviceCard3dsV1(request.__dict__, environment)
