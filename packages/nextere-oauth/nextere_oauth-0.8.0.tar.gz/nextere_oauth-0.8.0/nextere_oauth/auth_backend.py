import logging
from social_core.backends.open_id_connect import OpenIdConnectAuth

logger = logging.getLogger(__name__)

class NextereOIDCBackend(OpenIdConnectAuth):
    """
    Subclass of OpenIdConnectAuth that ensures fullname is set
    from given_name + family_name for Nextere OAuth.
    Keeps backend name as 'oidc' to match existing provider.
    """

    name = "oidc"

    def get_user_details(self, response):
        details = super().get_user_details(response)

        logger.info("[NextereOIDCBackend] user details: %s", details)
        details['first_name'] = response.get("given_name", "").strip()
        details['last_name'] = response.get("family_name", "").strip()

        if details['first_name'] or details['last_name']:
            details["fullname"] = f"{given_name} {family_name}".strip()
        else:
            details["fullname"] = details.get("email").split("@", 1)[0]
        logger.info("[NextereOIDCBackend] response: %s", response)
        logger.info("[NextereOIDCBackend] Final user details: %s", details)
        return details
