from python_nicepay.data.builder import builderEnvironment
from python_nicepay.data.builder.v2.professional import builderCancel
from python_nicepay.data.builder.v2.professional.dataGenerator import DataGenerator
from python_nicepay.service.v2EnterpriseService import ServiceNicepay


class testCancel:
    bodyCancel = (
        builderCancel.BuildCancel()
        .setPayMethod("01")
        .setTxid("_YOUR_TRANSACTION_ID")
        .setReferenceNo("OrdNo20250113093420")
        .setCancelUserId("admin")
        .setCancelType("1")
        .setCancelMsg("Test Cancel Python V2 Pro - n1tr0")
        .setAmt("10000")
        .build()
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    response = ServiceNicepay.serviceCancel(DataGenerator.getCancelBody(bodyCancel.jsonCancel()), environment)
