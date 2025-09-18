from datetime import datetime

from python_nicepay.constants.constantsGeneral import ConstantsGeneral
from python_nicepay.data.builder import builderEnvironment
from python_nicepay.data.builder.v1.enterprise.dataGenerator import DataGeneratorV1
from python_nicepay.data.builder.v2.enterprise import builderCartData
from python_nicepay.data.model.ccOnePassDo import CCOnePassDo
from python_nicepay.service.v1EnterpriseService import ServiceNicepayV1
from python_nicepay.util.utilMerchantToken import MerchantToken


class testCCOnePassDo:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    merchantKey = ConstantsGeneral.getMerchantKey()
    amt = 1000

    itemCartData = {
        "goods_id": "BB12345678",
        "goods_detail": "BB12345678",
        "goods_name": "Market",
        "goods_amt": amt,
        "goods_type": "Nice",
        "goods_url": "https://merchant.com/cellphones/iphone5s_64g",
        "goods_quantity": "1",
        "goods_sellers_id": "SEL123",
        "goods_sellers_name": "Sellers 1"
    }

    bodyCartData = (
        builderCartData.BuildCartData()
        .setCount("1")
        .setItem(itemCartData)
        .build()
    )

    bodyCCOnePassDo = CCOnePassDo(
        amt=amt,
        referenceNo="_YOUR_REFERENCE_NO_",
        instmntType="1",
        instmntMon="1",
        onePassToken="29f7b5f0d76728dfc8e40d48693ecf64f5c3eb97393a637c5031fa4c05a091f3",
        cardCvv="123",
        recurrOpt="1",
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    requestBody = DataGeneratorV1.getTransactionBodyV1(bodyCCOnePassDo.to_dict(), bodyCartData.jsonCartData())

    response = ServiceNicepayV1.serviceRequestV1(requestBody, environment)
