"""Consolidated initial migration for admin_dashboard app.

This migration creates the admin dashboard models:
- AuditLog: Track admin actions for audit purposes

Depends on users app for the CustomUser model.
"""
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """Initial migration for admin dashboard app."""

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('USER_SEARCH', 'User Search'), ('USER_VIEW', 'User View'), ('USER_EDIT', 'User Edit'), ('CREDIT_ADJUSTMENT', 'Credit Adjustment'), ('SERVICE_TOGGLE', 'Service Toggle'), ('PRODUCT_SYNC', 'Product Sync'), ('ADMIN_LOGIN', 'Admin Login'), ('ADMIN_LOGOUT', 'Admin Logout'), ('PAYMENT_INVESTIGATION', 'Payment Investigation'), ('PAYMENT_REFUND', 'Payment Refund'), ('OTHER', 'Other Action')], max_length=50)),
                ('description', models.TextField()),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Audit Log Entry',
                'verbose_name_plural': 'Audit Log Entries',
                'ordering': ['-timestamp'],
            },
        ),
    ]
