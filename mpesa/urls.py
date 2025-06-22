from django.urls import path
from mpesa import views as mpesa_views

urlpatterns = [
    # ✅ STK Push initiation (via JS fetch call)
    path("mpesa/initiate/", mpesa_views.initiate_mpesa_payment, name="initiate_mpesa_payment"),

    # 🔁 Poll transaction status
    path("mpesa/poll/<int:transaction_id>/", mpesa_views.poll_payment_status, name="poll_payment_status"),

    # ✅ Complete order once payment succeeds
    path("mpesa/complete/<int:transaction_id>/", mpesa_views.complete_mpesa_order, name="complete_mpesa_order"),

    # 📥 Safaricom callback (from STK push)
    path("mpesa/callback/", mpesa_views.mpesa_callback, name="mpesa_callback"),

    # 🎉 Optional thank-you page
    path("thank-you/", mpesa_views.mpesa_thank_you, name="mpesa_thank_you"),
    
    # ⚠️ REMOVE if not used:
    # path("mpesa/", mpesa_views.mpesa_checkout_view, name="mpesa_checkout"),
]
