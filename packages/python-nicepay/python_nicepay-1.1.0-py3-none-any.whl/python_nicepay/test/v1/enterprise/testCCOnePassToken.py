from datetime import datetime

from python_nicepay.constants.constantsGeneral import ConstantsGeneral
from python_nicepay.data.builder import builderEnvironment
from python_nicepay.data.model.ccOnePassToken import CCOnePassToken
from python_nicepay.service.v1EnterpriseService import ServiceNicepayV1
from python_nicepay.util.utilMerchantToken import MerchantToken


class testCCOnePassToken:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    merchantKey = ConstantsGeneral.getMerchantKey()
    amt = 1000

    request = CCOnePassToken(
        iMid=ConstantsGeneral.getImid(),
        referenceNo="_YOUR_REFERENCE_NO_",
        amt=amt,
        cardNo="5123450000000008",
        cardExpYymm="3901",
    )

    request.merchantToken = MerchantToken.getMerchantToken(f"{request.iMid}{request.referenceNo}{amt}{merchantKey}")

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    response = ServiceNicepayV1.serviceCardRegistrationV1(request.to_form_payload(),
                                                          environment)
