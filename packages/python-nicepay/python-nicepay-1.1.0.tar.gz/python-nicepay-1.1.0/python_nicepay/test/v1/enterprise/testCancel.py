from python_nicepay.constants.constantsGeneral import ConstantsGeneral
from python_nicepay.data.builder import builderEnvironment
from python_nicepay.data.builder.v1.enterprise.dataGenerator import DataGeneratorV1
from python_nicepay.data.builder.v1.enterprise import builderCancel
from python_nicepay.service.v1EnterpriseService import ServiceNicepayV1



class testCancel:
    bodyCancel = (
        builderCancel.BuildCancelV1()
        .setPayMethod(ConstantsGeneral.getPayMethodVirtualAccount())
        .setTxid("_YOUR_TRANSACTION_ID")
        .setReferenceNo("Nice20250814220800")
        .setCancelUserId("Admin")
        .setCancelType("1")
        .setCancelMsg("Testing Cancellation - n1tr0")
        .setAmt("10000")
        .build()
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    response = ServiceNicepayV1.serviceCancelV1(DataGeneratorV1.getCancelBodyV1(    bodyCancel.jsonCancelV1()), environment)
