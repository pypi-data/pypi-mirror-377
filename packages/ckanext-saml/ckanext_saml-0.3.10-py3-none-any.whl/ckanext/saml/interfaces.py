from typing import Optional

from onelogin.saml2.auth import OneLogin_Saml2_Auth

from ckan.plugins import Interface


class ICKANSAML(Interface):
    """Implement custom SAML response modification."""

    def after_mapping(self, mapped_data, auth):
        """Return dictonary mapped fields.

        :returns: dictonary
        :rtype: dict

        """

        return mapped_data

    def roles_and_organizations(self, mapped_data, auth, user):
        """Map Roles and assign User to Organizations."""
        pass

    def saml_auth_class(self) -> Optional[OneLogin_Saml2_Auth]:
        """Custom SamlAuthenticator(subclass of OneLogin_Saml2_Auth)."""
        pass

    def saml_before_user_create(self, mapped_data, user_dict):
        """Update User data before creating the User."""
        return user_dict
