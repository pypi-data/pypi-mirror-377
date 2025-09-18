from python_nicepay.constants.constantsGeneral import ConstantsGeneral
from python_nicepay.data.builder import builderEnvironment
from python_nicepay.data.builder.v2.enterprise import builderQris, builderCartData
from python_nicepay.data.builder.v2.enterprise.dataGenerator import DataGenerator
from python_nicepay.service.v2EnterpriseService import ServiceNicepay


class testQris:
    amt = 10000
    itemCartData = {
        "img_url": "https://cdn.eraspace.com/pub/media/catalog/product/i/p/iphone_13_pro_max_silver_1_5.jpg",
        "goods_name": "iPhone13ProMax",
        "goods_detail": "1TB-White",
        "goods_amt": amt,
        "goods_quantity": "1"
    }

    bodyCartData = (
        builderCartData.BuildCartData()
        .setCount("1")
        .setItem(itemCartData)
        .build()
    )

    bodyQris = (
        builderQris.BuildQris()
        .setPayMethod(ConstantsGeneral.getPayMethodQris())
        .setMitraCd("QSHP")
        .setShopId(ConstantsGeneral.getShopId())
        .setPaymentExpDt("")
        .setPaymentExpTm("")
        .setAmt(amt)
        .build()
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    response = ServiceNicepay.serviceRequest(DataGenerator.getTransactionBody(bodyQris.jsonQris(),
                                                                              bodyCartData.jsonCartData())
                                                                            , environment)
