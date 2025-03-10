# Generated by Django 5.1.5 on 2025-03-05 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Transactions', '0002_rename_load_approve_transaction_loan_approve'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='to_account',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.IntegerField(choices=[(1, 'Deposit'), (2, 'Withdrawal'), (3, 'Loan'), (4, 'Loan Paid'), (5, 'Transfer Money'), (6, 'Receive Money')]),
        ),
    ]
