import uuid
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.translation import gettext as _

from lacrei_models.appointments.models import Appointment
from lacrei_models.notification.signals import notification
from lacrei_models.utils.models import BaseModel, HashedAutoField


class Bank(BaseModel):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    ispb = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        app_label = 'payments'


class Payment(BaseModel):
    PENDING = "pending"
    PAYED = "payed"
    FAILED = "failed"
    PAYMENT_STATUS = [
        (PENDING, _("Pendente")),
        (PAYED, _("Pago")),
        (FAILED, _("Falhou")),
    ]
    CREDIT_CARD = "credit_card"
    PIX = "pix"
    PAYMENT_METHOD = [
        (CREDIT_CARD, _("Cartão de Crédito")),
        (PIX, _("PIX")),
    ]
    id = HashedAutoField(primary_key=True)
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name=_("Consulta"),
    )
    asaas_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_("ID da Cobrança na Asaas"),
    )
    value = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal(0.00))],
        verbose_name=_("Valor da consulta"),
    )
    status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS,
        default=PENDING,
        verbose_name=_("Status do Pagamento"),
    )
    method = models.CharField(
        max_length=15,
        choices=PAYMENT_METHOD,
        default=CREDIT_CARD,
        verbose_name=_("Método do Pagamento"),
    )

    class Meta:
        app_label = 'payments'

    def pre_update_instance(self, *args, **kwargs):
        if self.pk:
            try:
                previous = Payment.objects.get(pk=self.pk)
                self._previous_status = previous.status
            except Payment.DoesNotExist:
                self._previous_status = None
        else:
            self._previous_status = None

    def _send_payment_confirmation_emails(self):
        """Envia emails de confirmação de pagamento para usuário e profissional."""
        from lacrei_models.appointments.utils import AppointmentEmailContextBuilder

        # Envia email para o usuário
        context = AppointmentEmailContextBuilder(
            self.appointment
        ).build_context_to_user()
        notification.send(
            sender=self.__class__,
            template_prefix="appointments/user_appointment_particular_confirmation",
            email=self.appointment.user.email,
            context=context,
            recipient=self.appointment.user,
        )

        # Envia email para a pessoa profissional
        context = AppointmentEmailContextBuilder(
            self.appointment
        ).build_context_to_professional()
        context.update(
            {
                "payment_value": self.value,
                "payment_method": self.get_method_display(),
            }
        )
        notification.send(
            sender=self.__class__,
            template_prefix="appointments/professional_confirm_payment_sucess",
            email=self.appointment.professional.user.email,
            context=context,
            recipient=self.appointment.professional.user,
        )

    def post_create_instance(self, *args, **kwargs):
        # Envia confirmação se já nascer como PAYED
        if self.status == self.PAYED and self.appointment and self.appointment.user:
            self._send_payment_confirmation_emails()

    def post_update_instance(self, *args, **kwargs):
        # Dispara emails somente quando houver transição para PAYED
        changed_to_payed = (
            getattr(self, "_previous_status", None) != self.PAYED
            and self.status == self.PAYED
        )
        if changed_to_payed and self.appointment and self.appointment.user:
            self._send_payment_confirmation_emails()


class Customer(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    id_user = models.ForeignKey("lacreiid.User", on_delete=models.CASCADE)

    class Meta:
        app_label = 'payments'


class BillingStatus(BaseModel):
    PENDING = "PENDING"
    RECEIVED = "RECEIVED"
    CONFIRMED = "CONFIRMED"
    OVERDUE = "OVERDUE"
    REFUNDED = "REFUNDED"
    RECEIVED_IN_CASH = "RECEIVED_IN_CASH"
    REFUND_REQUESTED = "REFUND_REQUESTED"
    REFUND_IN_PROGRESS = "REFUND_IN_PROGRESS"
    CHARGEBACK_REQUESTED = "CHARGEBACK_REQUESTED"
    CHARGEBACK_DISPUTE = "CHARGEBACK_DISPUTE"
    AWAITING_CHARGEBACK_REVERSAL = "AWAITING_CHARGEBACK_REVERSAL"
    DUNNING_REQUESTED = "DUNNING_REQUESTED"
    DUNNING_RECEIVED = "DUNNING_RECEIVED"
    AWAITING_RISK_ANALYSIS = "AWAITING_RISK_ANALYSIS"

    STATUS_CHOICES = [
        (PENDING, _("Pendente")),
        (RECEIVED, _("Recebido")),
        (CONFIRMED, _("Confirmado")),
        (OVERDUE, _("Vencido")),
        (REFUNDED, _("Reembolsado")),
        (RECEIVED_IN_CASH, _("Recebido em dinheiro")),
        (REFUND_REQUESTED, _("Reembolso solicitado")),
        (REFUND_IN_PROGRESS, _("Reembolso em andamento")),
        (CHARGEBACK_REQUESTED, _("Chargeback solicitado")),
        (CHARGEBACK_DISPUTE, _("Disputa de chargeback")),
        (AWAITING_CHARGEBACK_REVERSAL, _("Aguardando reversão de chargeback")),
        (DUNNING_REQUESTED, _("Cobrança judicial solicitada")),
        (DUNNING_RECEIVED, _("Cobrança judicial recebida")),
        (AWAITING_RISK_ANALYSIS, _("Aguardando análise de risco")),
    ]

    id = HashedAutoField(primary_key=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES)
    payment_id = models.ForeignKey("Payment", on_delete=models.CASCADE)

    class Meta:
        app_label = 'payments'

    def __str__(self):
        return f"BillingStatus {self.id} - {self.status}"


@receiver(post_delete, sender=Customer)
def trigger_asaas_customer_delete(sender, instance, **kwargs):
    from .tasks import delete_customer_on_asaas

    delete_customer_on_asaas.delay(instance.id)


class AsaasWebhookLog(models.Model):
    """
    Modelo para registrar cada webhook recebido da Asaas, servindo como
    trilha de auditoria e controle de idempotência.
    """

    RECEIVED = "RECEIVED"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PROCESSED = "PROCESSED"
    IGNORED = "IGNORED"

    STATUS_CHOICES = [
        (RECEIVED, "Recebido"),
        (QUEUED, "Enfileirado"),
        (PROCESSING, "Processando"),
        (SUCCESS, "Sucesso"),
        (FAILED, "Falhou"),
        (PROCESSED, "Processado"),
        (IGNORED, "Ignorado"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_id = models.CharField(
        max_length=255, unique=True, help_text="ID do evento da Asaas para idempotência"
    )
    event_type = models.CharField(max_length=100, db_index=True)
    payload = models.JSONField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=RECEIVED, db_index=True
    )
    received_at = models.DateTimeField(auto_now_add=True)
    processing_log = models.TextField(
        blank=True, null=True, help_text="Log de erros ou observações do processamento."
    )

    class Meta:
        verbose_name = "Log de Webhook da Asaas"
        verbose_name_plural = "Logs de Webhooks da Asaas"
        ordering = ["-received_at"]
        app_label = 'payments'

    def __str__(self):
        return f"{self.event_type} ({self.id}) - {self.status}"