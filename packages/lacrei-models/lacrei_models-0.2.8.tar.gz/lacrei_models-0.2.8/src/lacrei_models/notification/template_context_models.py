from pydantic import BaseModel as PydanticBaseModel
from pydantic import HttpUrl

from lacrei_models.utils.template_context_models import static_path_to_url


class BaseEmailContext(PydanticBaseModel):
    icon_png_url: HttpUrl | str = static_path_to_url("images/icon.png")
    Ilustration_e_mail_svg_url: HttpUrl | str = static_path_to_url(
        "images/Ilustration-e-mail.svg"
    )
    facebook_svg_url: HttpUrl | str = static_path_to_url("images/facebook.svg")
    instagram_svg_url: HttpUrl | str = static_path_to_url("images/instagram.svg")
    linkedin_svg_url: HttpUrl | str = static_path_to_url("images/linkedin.svg")
    e_mail_svg_url: HttpUrl | str = static_path_to_url("images/e-mail.svg")


BASE_EMAIL_CONTEXT = BaseEmailContext().model_dump(mode="json")
