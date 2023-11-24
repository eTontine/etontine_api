from Transaction.Cron import Cron

def startCron():
    Cron.checkAbonnementTransactionValidation()
    Cron.checkCarteBuyTransactionValidation()
    Cron.checkParticipationTontineTransactionValidation()