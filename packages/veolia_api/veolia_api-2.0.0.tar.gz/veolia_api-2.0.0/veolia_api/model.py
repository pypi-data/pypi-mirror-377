"""Veolia API model."""

from dataclasses import dataclass


@dataclass
class AlertSettings:
    """Alert settings.
    daily_enabled: bool = To enable or disable daily alerts
    daily_threshold: int = Daily threshold in liters (minimum 100)
    daily_notif_email: bool = To enable or disable daily
        alerts by email (Can't be disabled)
    daily_notif_sms: bool = To enable or disable daily alerts by SMS
    monthly_enabled: bool = To enable or disable monthly alerts
    monthly_threshold: int = Monthly threshold in M3 (minimum 1)
    monthly_notif_email: bool = To enable or disable monthly
        alerts by email (Can't be disabled)
    monthly_notif_sms: bool = To enable or disable monthly alerts by SMS
    """

    daily_enabled: bool
    daily_threshold: int
    daily_notif_email: bool
    daily_notif_sms: bool
    monthly_enabled: bool
    monthly_threshold: int
    monthly_notif_email: bool
    monthly_notif_sms: bool


@dataclass
class VeoliaAccountData:
    """Data for the Veolia integration."""

    access_token: str | None = None
    token_expiration: float = 0
    code: str | None = None
    verifier: str | None = None
    id_abonnement: str | None = None
    numero_pds: str | None = None
    contact_id: str | None = None
    tiers_id: str | None = None
    numero_compteur: str | None = None
    date_debut_abonnement: str | None = None
    monthly_consumption: list[dict] | None = None
    daily_consumption: list[dict] | None = None
    alert_settings: AlertSettings | None = None
    billing_plan: dict | None = None
