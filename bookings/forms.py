from decimal import Decimal, ROUND_HALF_UP
from django import forms
from .models import DailyRoomPrice

class DailyRoomPriceForm(forms.ModelForm):
    kes_price = forms.DecimalField(
        label='Price (KES)', required=False, help_text='Enter price in KES (auto-converts to USD)')

    class Meta:
        model = DailyRoomPrice
        fields = ['room', 'date', 'price', 'rate_used']
        widgets = {
            'price': forms.NumberInput(attrs={'readonly': 'readonly'}),
            'rate_used': forms.NumberInput(attrs={'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['price'].label = 'Price (USD)'
        self.fields['price'].help_text = 'Auto-calculated from KES using the current exchange rate.'
        self.fields['price'].required = False
        self.fields['rate_used'].label = 'KES to USD Rate Used'
        self.fields['rate_used'].help_text = 'Exchange rate used for conversion.'
        self.fields['rate_used'].required = False

    def clean(self):
        cleaned_data = super().clean()
        kes_price = cleaned_data.get('kes_price')
        if kes_price:
            room = cleaned_data.get('room')
            if room:
                rental = room.rental
                try:
                    rate = Decimal(str(rental.exchange_rate.rate))
                except Exception:
                    rate = Decimal('130')  # fallback default
                usd = Decimal(str(kes_price)) / rate
                cleaned_data['price'] = usd.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                cleaned_data['rate_used'] = rate.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        kes_price = self.cleaned_data.get('kes_price')
        if kes_price:
            room = self.cleaned_data.get('room')
            if room:
                rental = room.rental
                try:
                    rate = Decimal(str(rental.exchange_rate.rate))
                except Exception:
                    rate = Decimal('130')
                usd = Decimal(str(kes_price)) / rate
                instance.price = usd.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                instance.rate_used = rate.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
        if commit:
            instance.save()
        return instance
