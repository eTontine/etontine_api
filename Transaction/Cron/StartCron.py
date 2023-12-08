from Transaction.Cron import Cron
from Transaction.Cron import CronDISB
import threading
import time

def startCron():
    Cron.checkAbonnementTransactionValidation()
    Cron.checkCarteBuyTransactionValidation()
    Cron.checkParticipationTontineTransactionValidation()
    CronDISB.makeDisbursement()

    # Exécution de setTransferToTontinierStatus après 3 minutes
    threading.Timer(180, CronDISB.setTransferToTontinierStatus).start()