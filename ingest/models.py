from django.db import models
from django.contrib.auth.models import User


class ImportBatch(models.Model):
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    file_name = models.CharField(max_length=255)
    upload_time = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')

    def __str__(self):
        return f"{self.file_name} ({self.status})"


class RawUtilityRecord(models.Model):
    import_batch = models.ForeignKey(ImportBatch, on_delete=models.CASCADE, related_name='raw_records')
    row_number = models.PositiveIntegerField()
    meter_id = models.CharField(max_length=50, blank=True)
    facility_name = models.CharField(max_length=120, blank=True)
    billing_start_date = models.CharField(max_length=50, blank=True)
    billing_end_date = models.CharField(max_length=50, blank=True)
    usage_value = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    usage_unit = models.CharField(max_length=20, blank=True)
    tariff_type = models.CharField(max_length=50, blank=True)
    total_cost = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    cost_unit = models.CharField(max_length=30, blank=True)
    currency = models.CharField(max_length=10, blank=True)
    supplier_name = models.CharField(max_length=120, blank=True)
    raw_row = models.JSONField()
    ingested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Row {self.row_number} - {self.meter_id}"


class NormalizedUtilityRecord(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    import_batch = models.ForeignKey(ImportBatch, on_delete=models.CASCADE, related_name='normalized_records')
    raw_record = models.OneToOneField(RawUtilityRecord, on_delete=models.CASCADE, related_name='normalized')
    meter_id = models.CharField(max_length=50)
    facility_name = models.CharField(max_length=120)
    billing_start = models.DateField(null=True, blank=True)
    billing_end = models.DateField(null=True, blank=True)
    usage_kwh = models.DecimalField(max_digits=14, decimal_places=3, null=True, blank=True)
    original_energy_value = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    original_energy_unit = models.CharField(max_length=20, blank=True)
    normalized_mwh = models.DecimalField(max_digits=14, decimal_places=6, null=True, blank=True)
    tariff_type = models.CharField(max_length=50, blank=True)
    total_cost = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    original_cost_value = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    original_cost_unit = models.CharField(max_length=30, blank=True)
    normalized_thousand_dollars = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    currency = models.CharField(max_length=10, blank=True)
    supplier_name = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.meter_id} {self.billing_start} - {self.total_cost}"


class ValidationIssue(models.Model):
    SEVERITY_CHOICES = [
        ('error', 'Error'),
        ('warning', 'Warning'),
    ]

    record = models.ForeignKey(NormalizedUtilityRecord, on_delete=models.CASCADE, related_name='issues')
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.severity.upper()}: {self.message}"


class NormalizationLog(models.Model):
    REVIEW_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('flagged', 'Flagged'),
    ]

    record = models.ForeignKey(NormalizedUtilityRecord, on_delete=models.CASCADE, related_name='normalization_logs')
    original_value = models.DecimalField(max_digits=14, decimal_places=6, null=True, blank=True)
    original_unit = models.CharField(max_length=30, blank=True)
    normalized_value = models.DecimalField(max_digits=14, decimal_places=6, null=True, blank=True)
    normalized_unit = models.CharField(max_length=30, blank=True)
    conversion_formula = models.CharField(max_length=120)
    review_status = models.CharField(max_length=20, choices=REVIEW_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.original_value} {self.original_unit} -> {self.normalized_value} {self.normalized_unit}"


# SAP Fuel & Procurement Models
class SAPImportBatch(models.Model):
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    file_name = models.CharField(max_length=255)
    upload_time = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    total_records = models.PositiveIntegerField(default=0)
    failed_records = models.PositiveIntegerField(default=0)
    suspicious_records = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.file_name} ({self.status})"


class RawSAPRecord(models.Model):
    import_batch = models.ForeignKey(SAPImportBatch, on_delete=models.CASCADE, related_name='raw_records')
    row_number = models.PositiveIntegerField()
    raw_data = models.JSONField()
    ingested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Row {self.row_number}"


class NormalizedSAPRecord(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    import_batch = models.ForeignKey(SAPImportBatch, on_delete=models.CASCADE, related_name='normalized_records')
    raw_record = models.OneToOneField(RawSAPRecord, on_delete=models.CASCADE, related_name='normalized')

    # Core fields
    material_number = models.CharField(max_length=50, blank=True)
    plant_code = models.CharField(max_length=50, blank=True)
    vendor_id = models.CharField(max_length=50, blank=True)
    vendor_name = models.CharField(max_length=200, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    invoice_number = models.CharField(max_length=100, blank=True)

    # Fuel data
    fuel_type = models.CharField(max_length=50, blank=True)
    original_quantity = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    original_unit = models.CharField(max_length=20, blank=True)
    normalized_quantity = models.DecimalField(max_digits=14, decimal_places=3, null=True, blank=True)
    normalized_unit = models.CharField(max_length=20, default='liters', blank=True)

    # Cost data
    total_cost = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    cost_per_unit = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    currency = models.CharField(max_length=10, default='USD', blank=True)

    # Location data
    country = models.CharField(max_length=50, blank=True)
    location_city = models.CharField(max_length=100, blank=True)
    location_state = models.CharField(max_length=50, blank=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sap_approvals')
    approved_at = models.DateTimeField(null=True, blank=True)
    locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.material_number} - {self.plant_code} - {self.total_cost}"


class SAPValidationIssue(models.Model):
    SEVERITY_CHOICES = [
        ('error', 'Error'),
        ('warning', 'Warning'),
    ]

    ISSUE_TYPES = [
        ('missing_plant', 'Missing Plant Code'),
        ('invalid_date', 'Invalid Date'),
        ('unknown_vendor', 'Unknown Vendor'),
        ('negative_amount', 'Negative Amount'),
        ('invalid_unit', 'Invalid Unit'),
        ('duplicate_invoice', 'Duplicate Invoice'),
        ('price_spike', 'Price Spike Detected'),
        ('quantity_anomaly', 'Quantity Anomaly'),
        ('suspicious_vendor', 'Suspicious Vendor Activity'),
    ]

    record = models.ForeignKey(NormalizedSAPRecord, on_delete=models.CASCADE, related_name='sap_issues')
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    issue_type = models.CharField(max_length=30, choices=ISSUE_TYPES)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.severity.upper()}: {self.message}"


class SAPApprovalLog(models.Model):
    ACTION_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('locked', 'Locked for Audit'),
        ('unlocked', 'Unlocked'),
        ('note_added', 'Note Added'),
    ]

    record = models.ForeignKey(NormalizedSAPRecord, on_delete=models.CASCADE, related_name='approval_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    notes = models.TextField(blank=True)
    previous_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.record} - {self.action} by {self.user}"