"""
Data migration: Remap legacy document types to 'other'.

The lab_tests system now handles xray, mri, ct_scan, lab_report, and ecg.
Documents with those types are remapped to 'other' so the choices can be
removed safely.
"""
from django.db import migrations

LEGACY_TYPES = ["xray", "mri", "ct_scan", "lab_report", "ecg"]


def remap_legacy_types(apps, schema_editor):
    MedicalDocument = apps.get_model("documents", "MedicalDocument")
    updated = MedicalDocument.objects.filter(
        document_type__in=LEGACY_TYPES
    ).update(document_type="other")
    if updated:
        print(f"\n  → Remapped {updated} document(s) from legacy types to 'other'")


def noop(apps, schema_editor):
    """Reverse is a no-op — can't restore original types automatically."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0004_medicaldocument_idx_doc_type_and_more"),
    ]

    operations = [
        migrations.RunPython(remap_legacy_types, noop),
    ]
