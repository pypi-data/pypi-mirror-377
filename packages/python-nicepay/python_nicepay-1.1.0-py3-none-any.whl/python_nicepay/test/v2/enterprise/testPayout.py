from python_nicepay.data.builder import builderEnvironment
from python_nicepay.data.builder.v2.enterprise import builderPayout
from python_nicepay.data.builder.v2.enterprise.dataGenerator import DataGenerator
from python_nicepay.service.v2EnterpriseService import ServiceNicepay


class testPayout:
    bodyPayout = (
        builderPayout.BuildPayout()
        .setAccountNo("5930696651")
        .setBenefNm("John Doe")
        .setBenefPhone("012345678910")
        .setBenefStatus("1")
        .setBenefType("1")
        .setBankCd("CENA")
        .setPayoutMethod("1")
        .setReferenceNo("NITRO0001X")
        .setReservedDt("") # Mandatory for CANCEL
        .setReservedTm("") # Mandatory for CANCEL
        .setAmt("10000")
        .setDescription("Testing Payout - n1tr0")
        .build()
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    response = ServiceNicepay.servicePayoutReg(DataGenerator.getPayoutRegBody(bodyPayout.jsonPayout()),environment)
