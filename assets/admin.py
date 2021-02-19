from django.contrib import admin

from .models import Asset
from .models import AssetPrice

# Register your models here.

admin.site.register(Asset)
admin.site.register(AssetPrice)

