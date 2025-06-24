from django.apps import AppConfig


class PaypalPaymentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'paypal_payment'

    def ready(self):
        import paypal_payment.signals  # noqa
