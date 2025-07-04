# Generated by Django 5.2.3 on 2025-07-02 10:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('rentals', '0001_initial'),
        ('users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='rental',
            name='hotel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rentals', to='users.hotel'),
        ),
        migrations.AddField(
            model_name='rental',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='room',
            name='hotel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rooms', to='users.hotel'),
        ),
        migrations.AddField(
            model_name='roomavailability',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='availability', to='rentals.room'),
        ),
        migrations.AddField(
            model_name='roomfee',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fees', to='rentals.room'),
        ),
        migrations.AddField(
            model_name='roomimage',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='rentals.room'),
        ),
        migrations.AddField(
            model_name='roompricing',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pricing', to='rentals.room'),
        ),
        migrations.AddField(
            model_name='roomtax',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='taxes', to='rentals.room'),
        ),
        migrations.AddIndex(
            model_name='room',
            index=models.Index(fields=['hotel', 'is_available'], name='rentals_roo_hotel_i_a93f94_idx'),
        ),
        migrations.AddIndex(
            model_name='room',
            index=models.Index(fields=['room_type', 'is_active'], name='rentals_roo_room_ty_a343b6_idx'),
        ),
        migrations.AddIndex(
            model_name='room',
            index=models.Index(fields=['base_price'], name='rentals_roo_base_pr_69ec63_idx'),
        ),
        migrations.AddIndex(
            model_name='roomavailability',
            index=models.Index(fields=['room', 'date'], name='rentals_roo_room_id_5a2305_idx'),
        ),
        migrations.AddIndex(
            model_name='roomavailability',
            index=models.Index(fields=['status', 'date'], name='rentals_roo_status_0756fe_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='roomavailability',
            unique_together={('room', 'date')},
        ),
        migrations.AddIndex(
            model_name='roomimage',
            index=models.Index(fields=['room', 'is_primary'], name='rentals_roo_room_id_93b1ba_idx'),
        ),
    ]
