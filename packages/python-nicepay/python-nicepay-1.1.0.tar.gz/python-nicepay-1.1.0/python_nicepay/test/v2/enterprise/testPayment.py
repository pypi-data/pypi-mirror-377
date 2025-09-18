from datetime import datetime

from python_nicepay.data.builder import builderEnvironment
from python_nicepay.data.builder.v2.enterprise import builderPayment
from python_nicepay.data.builder.v2.enterprise.dataGenerator import DataGenerator
from python_nicepay.service.v2EnterpriseService import ServiceNicepay


class testPayment:
    bodyPayment = (
        builderPayment.BuildPayment()
        .setTimestamp(datetime.now().strftime("%Y%m%d%H%M%S"))
        .setTxid("_YOUR_TRANSACTION_ID")
        .setReferenceNo("OrdNo20250821112103")
        .setCashtag("")
        .setCardNo("5123450000000008")
        .setCardExpYymm("3901")
        .setCardCvv("100")
        .setRecurringToken("")
        .setPreAuthToken("")
        .setAmt("1000")
        .build()
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    response = ServiceNicepay.servicePayment(DataGenerator.getPaymentBody(bodyPayment.dataPayment()), environment)
