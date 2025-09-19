from django.utils.translation import gettext as _

PERMISSION_EMAIL_NOT_VALIDATED = _(
    "Por favor, verifique seu email antes de realizar essa operação"
)
PERMISSION_PROFESSIONAL_NOT_CREATED_YET = _(
    "Por favor, crie um perfil profissional antes de realizar essa operação"
)
PERMISSION_PROFILE_IN_REVIEW = _(
    "Não é permitido fazer alterações no perfil durante a análise. "
    "Por favor aguarde o retorno da equipe para prosseguir."
)

CONDITIONALLY_REQUIRED_FIELD_ERROR = _("Este campo é obrigatório.")

INVALID_PERMISSION_FOR_APPOINTMENT = _(
    "Você não tem permissão para acessar os dados desta consulta."
)
