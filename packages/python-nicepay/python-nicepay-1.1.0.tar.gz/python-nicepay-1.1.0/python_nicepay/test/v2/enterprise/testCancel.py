from python_nicepay.constants.constantsGeneral import ConstantsGeneral
from python_nicepay.data.builder import builderEnvironment
from python_nicepay.data.builder.v2.enterprise import builderCancel
from python_nicepay.data.builder.v2.enterprise.dataGenerator import DataGenerator
from python_nicepay.service.v2EnterpriseService import ServiceNicepay


class testCancel:
    bodyCancel = (
        builderCancel.BuildCancel()
        .setPayMethod(ConstantsGeneral.getPayMethodPayloan())
        .setTxid("_YOUR_TRANSACTION_ID")
        .setReferenceNo("OrdNo20250113082212")
        .setCancelUserId("Admin")
        .setCancelType("1")
        .setCancelMsg("Testing Cancellation - n1tr0")
        .setAmt("10000")
        .build()
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(True)
                   .isProduction(False)
                   .build())

    response = ServiceNicepay.serviceCancel(DataGenerator.getCancelBody(bodyCancel.jsonCancel()), environment)
