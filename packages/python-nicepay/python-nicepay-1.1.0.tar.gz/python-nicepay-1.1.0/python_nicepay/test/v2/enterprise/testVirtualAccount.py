from python_nicepay.constants.constantsGeneral import ConstantsGeneral
from python_nicepay.data.builder import builderEnvironment
from python_nicepay.data.builder.v2.enterprise import builderVirtualAccount, builderCartData
from python_nicepay.data.builder.v2.enterprise.dataGenerator import DataGenerator
from python_nicepay.service.v2EnterpriseService import ServiceNicepay


class testVirtualAccount:
    amt = 10000
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

    bodyVirtualAccount = (
        builderVirtualAccount.BuildVirtualAccount()
        .setPayMethod(ConstantsGeneral.getPayMethodVirtualAccount())
        .setBankCd("BRIN")
        .setVacctValidDt("")
        .setVacctValidTm("")
        .setMerFixAcctId("")
        .setAmt(amt)
        .build()
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    response = ServiceNicepay.serviceRequest(DataGenerator.getTransactionBody(bodyVirtualAccount.jsonVirtualAccount(),
                                                                              bodyCartData.jsonCartData()), environment)