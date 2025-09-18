import abc

import environ
import requests

env = environ.Env()


class AbstractEmailVerifier(abc.ABC):
    @abc.abstractmethod
    def verify(self, email: str) -> bool:
        """Verifica um e-mail. Retorna True se válido/ok, False se inválido."""
        raise NotImplementedError  # pragma: no cover


class MockVerifier(AbstractEmailVerifier):
    def verify(self, email: str) -> bool:
        # Apenas aprova todos os e-mails sem verificação
        return True


class ZeroBounceVerifier(AbstractEmailVerifier):  # pragma: no cover
    def verify(self, email: str) -> bool:
        email_verification_key = env.str("ZB_API", default="sua_chave_aqui")
        if not email_verification_key or email_verification_key == "sua_chave_aqui":
            raise ValueError("A chave da API do ZeroBounce não está configurada.")

        url = f"https://api.zerobounce.net/v2/validate?api_key={email_verification_key}&email={email}"

        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            return data.get("status") not in ["invalid", "spamtrap", "abuse"]
        except requests.RequestException as e:
            print(f"Erro ao verificar o e-mail: {e}")
            return True


def get_email_verifier() -> AbstractEmailVerifier:
    """
    Retorna a instância do verificador de e-mails correta com base nas variáveis de ambiente.
    """
    is_enabled = (
        env.str("ENABLE_EMAIL_VERIFICATION_SERVICE", default="false").lower() == "true"
    )

    if not is_enabled:
        return MockVerifier()

    provider = env.str(
        "EMAIL_VERIFICATION_PROVIDER", default="ZeroBounce"
    )  # pragma: no cover

    if provider == "ZeroBounce":  # pragma: no cover
        return ZeroBounceVerifier()

    return MockVerifier()  # pragma: no cover
