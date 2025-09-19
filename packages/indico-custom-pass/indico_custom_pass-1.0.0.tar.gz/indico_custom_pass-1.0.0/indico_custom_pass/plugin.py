from indico.core.db import db
from indico.core.plugins import IndicoPlugin
from indico.modules.events.registration import GoogleWalletManager
from indico.modules.events.registration.models.forms import RegistrationForm
from indico.modules.events.registration.wallets.apple import AppleWalletManager
from indico_patcher import patch

from indico_custom_pass.settings import CustomPassSettingsForm


@patch(RegistrationForm)
class _RegistrationFormMixin:
    extra_fee_for_guests = db.Column(
        db.Numeric(11, 2),  # max. 999999999.99
        nullable=False,
        default=0
    )


settings = {}


class CustomPassPlugin(IndicoPlugin):
    """Custom pass plugin.

    Grants admins the ability to customize Indico Google Wallet & Apple Pay passes.
    """
    configurable = True
    settings_form = CustomPassSettingsForm
    default_settings = {
        'apple_pass_background_color': '#007cac',
        'apple_pass_foreground_color': '#ffffff',
        'apple_pass_label_color': '#ffffff',
        'apple_pass_organization_name': 'Indico',
        'google_pass_background_color': '#007cac'
    }

    def init(self):
        super().init()
        global settings
        settings = self.settings


@patch(AppleWalletManager)
class AppleWalletManagerMixin(AppleWalletManager):
    def build_pass_object(self, registration):
        p = super().build_pass_object(registration)
        p.backgroundColor = settings.get('apple_pass_background_color')
        p.foregroundColor = settings.get('apple_pass_foreground_color')
        p.labelColor = settings.get('apple_pass_label_color')
        p.organizationName = settings.get('apple_pass_organization_name')
        return p


@patch(GoogleWalletManager)
class GoogleWalletManagerMixin(GoogleWalletManager):
    def build_ticket_object_data(self, registration):
        data = super().build_ticket_object_data(registration)
        data['hexBackgroundColor'] = settings.get('google_pass_background_color')
        return data