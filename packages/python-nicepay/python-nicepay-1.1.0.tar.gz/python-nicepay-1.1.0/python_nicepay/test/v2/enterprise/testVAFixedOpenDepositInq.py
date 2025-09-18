from python_nicepay.data.builder import builderEnvironment
from python_nicepay.data.builder.v2.enterprise import builderVirtualAccount
from python_nicepay.data.builder.v2.enterprise.dataGenerator import DataGenerator
from python_nicepay.service.v2EnterpriseService import ServiceNicepay


class testVAFixedOpenDepositInq:
    bodyVAFixedOpenDepositInq = (
        builderVirtualAccount.BuildVAFixedOpenDepositInq()
        .setVacctNo("7007216100123458")
        .setStartDt("20241102")
        .setEndDt("20241103")
        .build()
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    response = ServiceNicepay.serviceVAFixedOpenDepositInq(DataGenerator
                                                           .getVAFixedOpenDepositInq(bodyVAFixedOpenDepositInq
                                                                                     .jsonVAFixedOpenDepositInq()),environment)
