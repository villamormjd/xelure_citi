from django.db import models

class Certificate(models.Model):
    title = models.CharField(max_length=100)
    csv_file = models.FileField('LoanData', upload_to='certificate/')

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title}"


class LoanData(models.Model):
    package_date = models.CharField(max_length=100, default=None)
    transaction_id = models.CharField(max_length=50, default=None)
    investor_loan_number = models.CharField(max_length=50, default=None)
    insurance_fee = models.DecimalField(decimal_places=2, max_digits=11, default=0)
    schedule_principal = models.DecimalField(decimal_places=2, max_digits=11, default=0)
    curtailments = models.DecimalField(decimal_places=2, max_digits=11, default=0)
    prepayment = models.DecimalField(decimal_places=2, max_digits=11, default=0)
    liquidation_principal = models.DecimalField(decimal_places=2, max_digits=11, default=0)

    class Meta:
        ordering = ['package_date']

    def __str__(self):
        return f"{self.package_date}-{self.investor_loan_number}"
