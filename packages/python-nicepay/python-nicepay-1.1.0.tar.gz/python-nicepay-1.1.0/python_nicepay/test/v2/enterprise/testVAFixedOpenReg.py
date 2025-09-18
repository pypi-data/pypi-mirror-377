from python_nicepay.data.builder import builderEnvironment
from python_nicepay.data.builder.v2.enterprise import builderVirtualAccount
from python_nicepay.data.builder.v2.enterprise.dataGenerator import DataGenerator
from python_nicepay.service.v2EnterpriseService import ServiceNicepay


class testVAFixedOpenReg:
    bodyVAFixedOpen = (
        builderVirtualAccount.BuildVAFixedOpenReg()
        .setCustomerId("123459100") # Use new customerId
        .setCustomerNm("TEST VA_FIX_OPEN")
        .build()
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    response = ServiceNicepay.serviceVAFixedOpenRegist(DataGenerator.getVAFixedOpenReg(bodyVAFixedOpen
                                                                                       .jsonVAFixedOpenReg()),environment)
