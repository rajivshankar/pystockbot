from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.

class Asset(models.Model):
    symbol = models.CharField(_("Symbol"), max_length=10)
    market_symbol = models.CharField(_("Market Symbol"), max_length=10, default='^GSPC')
    security_name = models.CharField(_("Security Name"), max_length=64)
    gics_industry = models.CharField(_("GICS Industry"), max_length=64, blank=True, null=True)
    gics_sub_industry = models.CharField(_("GICS Sub-Industry"), max_length=64, blank=True, null=True)

    class Meta:
        verbose_name = _("Asset")
        verbose_name_plural = _("Assets")
        unique_together = ['symbol', 'market_symbol']

    def __str__(self):
        return f'{self.security_name} [{self.symbol}]'

    def get_absolute_url(self):
        return reverse("asset_detail", kwargs={"pk": self.pk})


class AssetPrice(models.Model):
    asset = models.ForeignKey('Asset', related_name='asset', on_delete=models.CASCADE)
    datetime = models.DateTimeField(_("Date and Time"), auto_now=False, auto_now_add=False)
    high = models.DecimalField(_("High"), max_digits=15, decimal_places=10)
    low = models.DecimalField(_("Low"), max_digits=15, decimal_places=10)
    open = models.DecimalField(_("Open"), max_digits=15, decimal_places=10)
    close = models.DecimalField(_("Close"), max_digits=15, decimal_places=10)
    volume = models.DecimalField(_("Volume"), max_digits=20, decimal_places=4)
    adj_close = models.DecimalField(_("Adjusted Close"), max_digits=15, decimal_places=10)

    class Meta:
        verbose_name = _("Asset Price")
        verbose_name_plural = _("Asset Prices")
        unique_together = ['asset', 'datetime']

    def __str__(self):
        return f'{self.asset}: {self.datetime}'

    def get_absolute_url(self):
        return reverse("asset_price_detail", kwargs={"pk": self.pk})
    
