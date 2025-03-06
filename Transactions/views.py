from django.shortcuts import render, redirect
from django.views.generic import CreateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Transaction
from .forms import DepositeForm, WithdrawForm, LoanRequestForm, TransferMoneyForm
from .constants import TRANSACTION_TYPE, DEPOSITE, WITHDRAWAL, LOAN, LOAN_PAID, TRANSFER_MONEY, RECEIVE_MONEY
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime
from django.db.models import Sum
from django.views import View
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from Accounts.models import UserBankAccount
# Create your views here.


def send_transaction_mail(user, amount, subject, template, account_number=None):
    context = {
        'user': user,
        'amount': amount,
    }
    
    if account_number is not None:
        context['account_number'] = account_number

    message = render_to_string(template, context)
    send_email = EmailMultiAlternatives(subject, '', to=[user.email])
    send_email.attach_alternative(message, "text/html")
    send_email.send()


class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transactions/transaction_form.html'
    model = Transaction
    title = ''
    success_url = reverse_lazy('transaction_report')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title
        })
        return context


class DepositeMoneyView(TransactionCreateMixin):
    form_class = DepositeForm
    title = 'Deposite'

    def get_initial(self):
        initial = {'transaction_type': DEPOSITE}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        account.balance += amount
        account.save(
            update_fields=['balance']
        )

        messages.success(self.request, f'Amount {amount} deposite successful')
        send_transaction_mail(self.request.user, amount,
                              'Deposite Successful', 'transactions/deposite_email.html')
        return super().form_valid(form)


class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = 'Withdraw Money'

    def get_initial(self):
        initial = {'transaction_type': WITHDRAWAL}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        account.balance -= amount
        account.save(
            update_fields=['balance']
        )

        messages.success(self.request, f'Amount {amount} withdrawn successful')
        send_transaction_mail(self.request.user, amount,
                              'Withdraw Successful', 'transactions/withdrawal_email.html')
        return super().form_valid(form)


class LoanRequestView(TransactionCreateMixin):
    form_class = LoanRequestForm
    title = 'Loan Request'

    def get_initial(self):
        initial = {'transaction_type': LOAN}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        loan_count = Transaction.objects.filter(
            account=self.request.user.account, transaction_type=3, loan_approve=True).count()

        if loan_count >= 3:
            return HttpResponse('You have an outstanding loan')

        messages.success(
            self.request, f'Loan request for {amount} has been sent')
        send_transaction_mail(self.request.user, amount,
                              'Loan Request Successful', 'transactions/loan_request_email.html')
        return super().form_valid(form)


class TransactionReportView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'transactions/transaction_report.html'
    balance = 0

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            account=self.request.user.account
        )
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            queryset = queryset.filter(
                timestamp__date__gte=start_date, timestamp__date__lte=end_date)
            self.balance = Transaction.objects.filter(
                timestamp__date__gte=start_date, timestamp__date__lte=end_date).aggregate(Sum('amount'))['amount__sum']
        else:
            self.balance = self.request.user.account.balance

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user.account,
        })
        return context


class PayLoanView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan = get_object_or_404(Transaction, id=loan_id)

        if loan.loan_approve:
            user_account = loan.account
            if loan.amount < user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()
                loan.transaction_type = LOAN_PAID
                loan.save()
                return redirect('loan_list')
            else:
                messages.error(request, 'Insufficient balance')
                return redirect('loan_list')


class LoanListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'transactions/loan_request.html'
    context_object_name = 'loans'

    def get_queryset(self):
        user_account = self.request.user.account
        queryset = Transaction.objects.filter(
            account=user_account, transaction_type=3
        )
        return queryset
        # return super().get_queryset().filter(
        #     account=self.request.user.account, transaction_type=3
        # )


class TransferMoneyView(TransactionCreateMixin):
    title = "Transfer Money"
    form_class = TransferMoneyForm

    def get_initial(self):
        initial = {
            'transaction_type': TRANSFER_MONEY,
        }
        return initial

    def form_valid(self, form):
        to_account = form.cleaned_data.get('to_account')
        amount = form.cleaned_data.get('amount')

        send_account = self.request.user.account
        send_account.balance -= amount

        receive_account = UserBankAccount.objects.get(
            account_number=to_account)
        receive_account.balance += amount

        send_account.save(update_fields=['balance'])
        receive_account.save(update_fields=['balance'])

        Transaction.objects.create(
            account=receive_account,
            amount=amount,
            balance_after_transaction=receive_account.balance,
            transaction_type=RECEIVE_MONEY
        )
        send_transaction_mail(self.request.user, amount,
                              'Send Money Successful', 'transactions/send_money_email.html', receive_account.account_number)
        send_transaction_mail(receive_account.user, amount,
                              'Received Money', 'transactions/received_money_email.html', send_account.account_number)

        messages.success(
            self.request, f'Successfully transferred {amount} from {send_account.account_number} to {to_account}'
        )

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Something went wrong.")
        return super().form_invalid(form)
