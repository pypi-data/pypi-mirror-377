from django.utils.translation import gettext as _

PROFESSIONAL_ALREDY_CREATED = _("Um perfil professional já foi criado em sua conta. ")
CLINIC_ALREDY_CREATED = _("Uma clínica já foi criada para sua conta. ")
PROFESSIONAL_CLINIC_SCHEDULE_VALIDATION = _(
    "Horário de abertura não pode ser maior que o horário de fechamento"
)
PROFESSIONAL_CLINIC_SCHEDULE_ALREADY_EXISTS = _(
    "Já existe um horário cadastrado para o período selecionado"
)
PROFESSIONAL_CLINIC_MUST_SELECT_TYPE = _(
    "É necessário selecionar pelo menos um tipo de clínica (online ou presencial)"
)
PROFESSIONAL_CLINIC_SCHEDULE_CONFLICT = _(
    "Os horários inválidos no período "
    "de {} {:%H:%M}-{:%H:%M} e {:%H:%M}-{:%H:%M}. "
    "Remova as sobreposições nos horários para prosseguir."
)
ZIP_CODE_NOT_AVAILABLE = _(
    "Esse cep ainda não está disponível na plataforma. "
    "Por favor entre em contato com o suporte."
)

PROFESSIONAL_LAST_NAME_REQUIRED = _("Informe pelo menos um sobrenome")


VERIFICATION_CODE_ALREADY_CONFIRMED = _("Código já foi confirmado")
VERIFICATION_CODE_INVALID = _("Código de verificação inválido")

CONTACT_REQUEST_SMS_MESSAGE = "Código Lacrei Saúde: {validation_code}. Não compartilhe."
CONTACT_REQUEST_SMS_FAIL = "Não foi possível enviar o código de verificação no momento. Tente novamente mais tarde."
CONTACT_USER_QUESTIONNAIRE_FORM_URL = "https://forms.office.com/r/CkVeqZsfhy"
CONTACT_PROFESSIONAL_QUESTIONNAIRE_FORM_URL = (
    "https://forms.office.com/r/ProfessionalQuestionnaireForm"
)
APPOINTMENT_USER_QUESTIONNAIRE_FORM_URL = (
    "https://forms.office.com/r/AppointmentUserQuestionnaireForm"
)

PROFESSIONAL_VALIDATION_PENDING_ADMIN = _("Pendente Lacrei")
