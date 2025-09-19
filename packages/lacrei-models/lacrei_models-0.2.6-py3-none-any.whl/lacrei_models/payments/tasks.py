import logging

from celery import shared_task

from lacrei_models.payments.clients.asaas import AsaasClient
from lacrei_models.payments.clients.brasil_api import BrasilAPIClient

from .models import AsaasWebhookLog, Bank

logger = logging.getLogger(__name__)
task_logger = logging.getLogger("webhook_auditor")


@shared_task(name="fetch_and_store_banks_task")
def fetch_and_store_banks():
    try:
        retval = "Nenhum dado encontrado."
        data = BrasilAPIClient().get_banks()
        for bank in data:
            if bank.get("code"):
                Bank.objects.update_or_create(
                    code=bank["code"],
                    defaults={
                        "name": bank["name"],
                        "ispb": bank["ispb"],
                    },
                )
        return f"{len(data)} bancos atualizados." if data else retval
    except Exception as e:
        logger.error(f"Erro ao atualizar bancos: {str(e)}", exc_info=True)


@shared_task(name="delete_customer_on_asaas_task")
def delete_customer_on_asaas(id: str):
    try:
        client = AsaasClient()
        client.delete_customer_account(id)
    except Exception as e:
        logger.error(f"Erro ao deletar cliente no asaas: {str(e)}", exc_info=True)


@shared_task(bind=True)
def process_asaas_webhook_task(self, log_id: str):
    log_entry = None
    try:
        log_entry = AsaasWebhookLog.objects.get(id=log_id)

        log_entry.status = AsaasWebhookLog.PROCESSING
        log_entry.save(update_fields=["status"])

        event_type = log_entry.event_type
        asaas_event_id = log_entry.event_id

        if event_type in [
            "PAYMENT_RECEIVED",
            "PAYMENT_CONFIRMED",
            "PAYMENT_OVERDUE",
            "PAYMENT_DELETED",
        ]:
            task_logger.info(
                f"Log de auditoria: Evento '{event_type}' recebido para o Asaas Event ID '{asaas_event_id}'."
            )
            log_entry.status = AsaasWebhookLog.PROCESSED
        else:
            task_logger.warning(
                f"Log de auditoria: Evento não mapeado '{event_type}' para o Asaas Event ID '{asaas_event_id}'. Marcando como ignorado."
            )
            log_entry.status = AsaasWebhookLog.IGNORED

        log_entry.save(update_fields=["status"])
        return f"Log de webhook {log_id} (Evento: {event_type}) processado com sucesso para auditoria."

    except AsaasWebhookLog.DoesNotExist:
        task_logger.error(
            f"Log de webhook com ID {log_id} não encontrado para processamento."
        )
        return f"Falha: Log {log_id} não encontrado."
    except Exception as e:
        if log_entry:
            log_entry.status = AsaasWebhookLog.FAILED
            log_entry.save(update_fields=["status"])
        task_logger.error(f"Erro inesperado no webhook {log_id}: {e}", exc_info=True)
        raise self.retry(exc=e)


@shared_task
def enqueue_pending_webhooks_task():
    """
    Busca webhooks que foram recebidos mas ainda não enfileirados
    e os dispara para processamento.
    """
    pending_logs = AsaasWebhookLog.objects.filter(status=AsaasWebhookLog.RECEIVED)
    count = 0
    for log in pending_logs:
        log.status = AsaasWebhookLog.QUEUED
        log.save(update_fields=["status"])
        process_asaas_webhook_task.delay(log_id=str(log.id))
        count += 1

    if count > 0:
        logger.info(
            f"📥 {count} webhooks pendentes foram enfileirados para processamento."
        )
    return f"{count} webhooks enfileirados."
