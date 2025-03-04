from django.urls import path
from .views import DepositeMoneyView, WithdrawMoneyView, LoanRequestView, TransactionReportView, PayLoanView, LoanListView

urlpatterns = [
    path('deposite/', DepositeMoneyView.as_view(), name='deposite_money'),
    path('withdraw/', WithdrawMoneyView.as_view(), name='withdraw_money'),
    path('loan_request/', LoanRequestView.as_view(), name='loan_request'),
    path('report/', TransactionReportView.as_view(), name='transaction_report'),
    path('loan/<int:loan_id>/', PayLoanView.as_view(), name='pay_loan'),
    path('loans/', LoanListView.as_view(), name='loan_list'),
]
