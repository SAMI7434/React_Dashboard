from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ingest', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rawutilityrecord',
            name='cost_unit',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='normalizedutilityrecord',
            name='normalized_mwh',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=14, null=True),
        ),
        migrations.AddField(
            model_name='normalizedutilityrecord',
            name='normalized_thousand_dollars',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=14, null=True),
        ),
        migrations.AddField(
            model_name='normalizedutilityrecord',
            name='original_cost_unit',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='normalizedutilityrecord',
            name='original_cost_value',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True),
        ),
        migrations.AddField(
            model_name='normalizedutilityrecord',
            name='original_energy_unit',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='normalizedutilityrecord',
            name='original_energy_value',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=14, null=True),
        ),
        migrations.CreateModel(
            name='NormalizationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_value', models.DecimalField(blank=True, decimal_places=6, max_digits=14, null=True)),
                ('original_unit', models.CharField(blank=True, max_length=30)),
                ('normalized_value', models.DecimalField(blank=True, decimal_places=6, max_digits=14, null=True)),
                ('normalized_unit', models.CharField(blank=True, max_length=30)),
                ('conversion_formula', models.CharField(max_length=120)),
                ('review_status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('flagged', 'Flagged')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='normalization_logs', to='ingest.normalizedutilityrecord')),
            ],
        ),
    ]
