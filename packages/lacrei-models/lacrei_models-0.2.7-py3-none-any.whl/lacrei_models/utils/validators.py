import re

try:
    import dns.exception
    import dns.resolver

    DNS_AVAILABLE = True  # pragma: no cover
except ImportError:  # pragma: no cover
    DNS_AVAILABLE = False  # pragma: no cover

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .email_verifier import get_email_verifier

from .constants import CONDITIONALLY_REQUIRED_FIELD_ERROR


class BRCPFValidator(RegexValidator):
    """
    Based on django-localflavor:
    https://github.com/django/django-localflavor/blob/master/localflavor/br/validators.py
    """

    regex = re.compile(r"^(\d{3})\.(\d{3})\.(\d{3})-(\d{2})$")
    message = _("CPF Inválido.")

    @staticmethod
    def calculate_verification_digit(value, _range):
        calculated_digit = (
            sum([i * int(value[idx]) for idx, i in enumerate(_range)]) % 11
        )

        if calculated_digit >= 2:
            return 11 - calculated_digit
        return 0

    def __call__(self, value):
        if not value.isdigit():
            cpf = self.regex.search(value)
            if cpf:
                value = "".join(cpf.groups())
            else:
                raise ValidationError(self.message, code="invalid")

        if len(value) != 11:
            raise ValidationError(self.message, code="max_digits")

        original_verification_digit = value[-2:]

        first_digit = self.calculate_verification_digit(value, range(10, 1, -1))
        value = value[:-2] + str(first_digit) + value[-1]

        second_digit = self.calculate_verification_digit(value, range(11, 1, -1))
        value = value[:-1] + str(second_digit)

        if value[-2:] != original_verification_digit:
            raise ValidationError(self.message, code="invalid")
        if value.count(value[0]) == 11:
            raise ValidationError(self.message, code="invalid")


class NumberValidator(object):
    """
    Based on six feet up:
    https://sixfeetup.com/blog/custom-password-validators-in-django
    """

    def validate(self, password, user=None):
        if not re.findall("\\d", password):
            raise ValidationError(
                self.get_help_text(),
                code="password_no_number",
            )

    def get_help_text(self):
        return _("A senha precisa conter pelo menos um número, 0-9.")


class UppercaseValidator(object):
    """
    Based on six feet up:
    https://sixfeetup.com/blog/custom-password-validators-in-django
    """

    def validate(self, password, user=None):
        if not re.findall("[A-Z]", password):
            raise ValidationError(
                self.get_help_text(),
                code="password_no_upper",
            )

    def get_help_text(self):
        return _("A senha precisa conter pelo menos uma letra maiúscula, A-Z.")


class LowercaseValidator(object):
    """
    Based on six feet up:
    https://sixfeetup.com/blog/custom-password-validators-in-django
    """

    def validate(self, password, user=None):
        if not re.findall("[a-z]", password):
            raise ValidationError(
                self.get_help_text(),
                code="password_no_lower",
            )

    def get_help_text(self):
        return _("A senha precisa conter pelo menos uma letra minúscula, a-z.")


class SymbolValidator(object):
    """
    Based on six feet up:
    https://sixfeetup.com/blog/custom-password-validators-in-django
    """

    def validate(self, password, user=None):
        password = password.encode("unicode_escape").decode()
        if not re.findall(r"[()[\]{}|`~!@#$%^&*_\-+=;:'\",<>.\/?\\]", password):
            raise ValidationError(
                self.get_help_text(),
                code="password_no_symbol",
            )

    def get_help_text(self):
        return _(
            "A senha precisa conter pelo menos um caractere especial, "
            "()[]{}|\\`~!@#$%^&*_-+=;:'\",<>./?"
        )


class ConditionallyRequiredFieldsValidator:
    """
    Add flexibility to require fields depending on another field value.

    For example:
        conditionally_required_fields = [
            (
                "is_presential_clinic",
                {
                    "require_fields_if": True,
                    "required_fields": [
                        "address",
                        "city",
                    ],
                },
            ),
            (
                "is_online_clinic",
                {
                    "require_fields_if": True,
                    "required_fields": [
                        "online_clinic_phone",
                        "online_clinic_phone_whatsapp",
                    ],
                },
            ),
        ]
    """

    def __init__(
        self,
        conditionally_required_fields,
        required_message=CONDITIONALLY_REQUIRED_FIELD_ERROR,
    ):
        self.conditionally_required_fields = conditionally_required_fields
        self.required_message = required_message

    def validate(self, data):
        errors = {}

        for base_field_name, conditions in self.conditionally_required_fields:
            should_require_fields = (
                data.get(base_field_name) == conditions["require_fields_if"]
            )
            if not should_require_fields:
                continue

            conditionally_required_fields = conditions["required_fields"]
            missing_fields = [
                field_name
                for field_name in conditionally_required_fields
                if data.get(field_name) is None or data.get(field_name) == ""
            ]
            if missing_fields:
                errors.update(
                    {field_name: self.required_message for field_name in missing_fields}
                )

        if errors:
            raise serializers.ValidationError(errors)

        return data


class OnlyAlphabeticValidator(RegexValidator):
    regex = re.compile(
        r"^[A-Za-záàâåãäéëèêíìïîóôòõöüùúûçñÁÀÂÃÄÅÉÈËÊÍÌÏÎÓÔÕÖÒÙÚÛÜýÿÝŸÇÑèìîòûÈÌÎÒÛ ]+$"
    )
    message = "O campo não pode incluir números ou caracteres especiais"

    def __call__(self, value: str) -> None:
        if not self.regex.search(value):
            raise ValidationError(self.message, code="invalid")


class OnlyUpperCaseAndNumbersValidator(RegexValidator):
    regex = r"^[A-Z0-9]*$"
    message = "O código do cupom só pode conter números e letras maiúsculas"

    def __call__(self, value: str) -> None:
        if not re.search(self.regex, value):
            raise ValidationError(self.message, code="invalid")


class EmailValidator:
    """
    Validador de e-mail completo que verifica o formato (Regex)
    e a existência de registros MX (DNS) para o domínio.
    """

    message_invalid_format = _(
        "Por favor, utilize um formato de e-mail válido. Por exemplo: email@dominio.com.br"
    )
    message_invalid_domain = _(
        "O domínio do e-mail parece não existir ou não pode receber e-mails."
    )
    message_service_invalid = _(
        "Este endereço de e-mail não foi aprovado pelo nosso serviço de verificação."
    )
    message_disposable_domain = _(
        "E-mails de domínios descartáveis não são permitidos."
    )

    email_regex = re.compile(
        r"(^[a-zA-Z0-9_+-][a-zA-Z0-9_.+-]*@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    )

    def __call__(self, value):
        """Executa a validação."""
        if not self._is_valid_format(value):
            raise ValidationError(self.message_invalid_format, code="invalid_format")

        domain = value.split("@")[1].lower()

        # Validação de domínio descartável
        if self._is_disposable_domain(domain):
            raise ValidationError(
                self.message_disposable_domain, code="disposable_domain"
            )

        # Validação de MX/DNS (se habilitada)
        if getattr(settings, "EMAIL_CHECK_MX", True):
            if not self._domain_has_mx_records(domain):
                raise ValidationError(
                    self.message_invalid_domain, code="invalid_domain"
                )

        # O código abaixo só roda se a feature estiver LIGADA
        verifier = get_email_verifier()
        if not verifier.verify(value):  # pragma: no cover
            raise ValidationError(self.message_service_invalid, code="service_invalid")

    def _is_valid_format(self, value):
        """Verifica o formato do e-mail com Regex."""
        return self.email_regex.match(value) is not None

    def _is_disposable_domain(self, domain):
        """Verifica se o domínio está na lista de descartáveis."""
        # Se permitir e-mails descartáveis em staging, retorna False
        if getattr(settings, "ALLOW_DISPOSABLE_EMAILS", False):
            return False

        # Verifica na lista customizada das configurações
        custom_denylist = getattr(settings, "DISPOSABLE_DOMAIN_DENYLIST", set())
        return domain in custom_denylist

    def _domain_has_mx_records(self, domain):
        """Verifica se o domínio possui registros MX."""
        if not DNS_AVAILABLE:
            # Se o DNS não estiver disponível, assume que o domínio é válido
            return True

        try:
            dns.resolver.resolve(domain, "MX")
            return True
        except (
            dns.resolver.NoAnswer,
            dns.resolver.NXDOMAIN,
            dns.exception.Timeout,
            dns.resolver.NoNameservers,
        ):
            return False
        except Exception:
            return False
