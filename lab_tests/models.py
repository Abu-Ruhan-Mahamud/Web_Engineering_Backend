from django.db import models


class LabTest(models.Model):
    """Lab test order created by a doctor for a patient."""

    class TestCategory(models.TextChoices):
        BLOOD = "blood", "Blood Test"
        URINE = "urine", "Urine Test"
        IMAGING = "imaging", "Imaging"
        CARDIAC = "cardiac", "Cardiac"
        PATHOLOGY = "pathology", "Pathology"
        MICROBIOLOGY = "microbiology", "Microbiology"
        OTHER = "other", "Other"

    class Priority(models.TextChoices):
        ROUTINE = "routine", "Routine"
        URGENT = "urgent", "Urgent"
        STAT = "stat", "STAT"

    class Status(models.TextChoices):
        ORDERED = "ordered", "Ordered"
        SAMPLE_COLLECTED = "sample_collected", "Sample Collected"
        PROCESSING = "processing", "Processing"
        RESULTS_AVAILABLE = "results_available", "Results Available"
        REVIEWED = "reviewed", "Reviewed"

    patient = models.ForeignKey(
        "users.Patient",
        on_delete=models.PROTECT,
        related_name="lab_tests",
    )
    doctor = models.ForeignKey(
        "users.Doctor",
        on_delete=models.PROTECT,
        related_name="lab_tests_ordered",
    )
    appointment = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.SET_NULL,
        related_name="lab_tests",
        null=True,
        blank=True,
    )
    test_name = models.CharField(max_length=200)
    test_category = models.CharField(
        max_length=15,
        choices=TestCategory.choices,
        default=TestCategory.BLOOD,
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.ROUTINE,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ORDERED,
    )
    clinical_notes = models.TextField(blank=True, default="")
    ordered_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        "users.Doctor",
        on_delete=models.SET_NULL,
        related_name="lab_tests_reviewed",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "lab_tests"
        ordering = ["-ordered_at"]
        indexes = [
            models.Index(fields=["-ordered_at"], name="idx_labtest_ordered"),
            models.Index(fields=["status"], name="idx_labtest_status"),
        ]

    def __str__(self):
        return f"{self.test_name} for {self.patient} ({self.get_status_display()})"


class LabTestResult(models.Model):
    """Result uploaded by a lab technician for a lab test."""

    class Interpretation(models.TextChoices):
        NORMAL = "normal", "Normal"
        ABNORMAL = "abnormal", "Abnormal"
        CRITICAL = "critical", "Critical"

    lab_test = models.OneToOneField(
        LabTest,
        on_delete=models.CASCADE,
        related_name="result",
    )
    # ── Structured results (blood, urine, cardiac) ──
    result_value = models.TextField(
        blank=True,
        default="",
        help_text="Primary result value or summary (structured tests)",
    )
    reference_range = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text='e.g. "70-100 mg/dL"',
    )
    unit = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text='e.g. "mg/dL", "mmol/L"',
    )

    # ── Narrative results (imaging, pathology, microbiology) ──
    findings = models.TextField(
        blank=True,
        default="",
        help_text="Detailed narrative findings (imaging/pathology reports)",
    )
    impression = models.TextField(
        blank=True,
        default="",
        help_text="Summary conclusion / diagnostic impression",
    )

    # ── Common fields ──
    interpretation = models.CharField(
        max_length=10,
        choices=Interpretation.choices,
        default=Interpretation.NORMAL,
    )
    result_file = models.FileField(
        upload_to="lab_results/",
        blank=True,
        null=True,
        help_text="Uploaded result document (PDF, image, etc.)",
    )
    notes = models.TextField(blank=True, default="")
    uploaded_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="uploaded_lab_results",
        null=True,
        blank=True,
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "lab_test_results"

    def __str__(self):
        return f"Result for {self.lab_test.test_name}"
