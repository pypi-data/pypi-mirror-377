from python_nicepay.constants.constantsGeneral import ConstantsGeneral
from python_nicepay.data.builder import builderEnvironment
from python_nicepay.data.builder.v1.enterprise.dataGenerator import DataGeneratorV1
from python_nicepay.data.builder.v2.enterprise import builderCartData
from python_nicepay.data.builder.v1.enterprise import builderCreditCard
from python_nicepay.service.v1EnterpriseService import ServiceNicepayV1


class testCreditCard:
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

    bodyCreditCard = (
        builderCreditCard.BuildCreditCardV1()
        .setPayMethod(ConstantsGeneral.getPayMethodCreditCard())
        .setRecurrOpt("")
        .setInstmntMon("1")
        .setInstmntType("1")
        .setAmt(amt)
        .build()
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    response = ServiceNicepayV1.serviceRequestV1(DataGeneratorV1.getTransactionBodyV1(bodyCreditCard.jsonCreditCardV1(),
                                                                              bodyCartData.jsonCartData()),
                                                                              environment)



