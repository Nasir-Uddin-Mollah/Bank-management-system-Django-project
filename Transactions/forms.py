from django import forms
from .models import Transaction
from Accounts.models import UserBankAccount
from django.db.models import Sum


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_type']

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()

    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save()


class DepositeForm(TransactionForm):
    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        min_deposit_amount = 500
        if amount < min_deposit_amount:
            raise forms.ValidationError(
                f"Minimum deposit amount is {min_deposit_amount}"
            )
        return amount


class WithdrawForm(TransactionForm):
    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        min_withdraw_amount = 500
        max_withdraw_amount = 20000
        account = self.account
        balance = self.account.balance

        bank_balance = UserBankAccount.objects.aggregate(
            Sum('balance'))['balance__sum']
        if bank_balance is None or bank_balance < amount:
            raise forms.ValidationError("This bank is bankrupt")


        if amount < min_withdraw_amount:
            raise forms.ValidationError(
                f"Minimum withdraw amount is {min_withdraw_amount}"
            )
        if amount > max_withdraw_amount:
            raise forms.ValidationError(
                f"Maximum withdraw amount is {max_withdraw_amount}"
            )
        if amount > balance:
            raise forms.ValidationError("Insufficient balance")

        return amount



class LoanRequestForm(TransactionForm):
    def clean_amount(self):
        amount = self.cleaned_data.get("amount")

        return amount


class TransferMoneyForm(TransactionForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_type', 'to_account']

    def clean_to_account(self):
        to_account = self.cleaned_data.get('to_account')
        if UserBankAccount.objects.filter(account_number=to_account).exists():
            return to_account
        raise forms.ValidationError("This account doesn't exist.")

    def clean_amount(self):
        account = self.account
        amount = self.cleaned_data.get('amount')
        if account.balance < amount:
            raise forms.ValidationError("Insufficient balance")

        return amount
