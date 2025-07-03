from rest_framework import serializers
from .models import Rental, Room, RoomImage, RoomFee, RoomTax  # Added RoomFee, RoomTax

WSL_IP = '172.24.73.89'  # <-- Set your WSL IP here

class RoomImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = RoomImage
        fields = ['id', 'image']
    
    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request:
                url = request.build_absolute_uri(obj.image.url)
                # Replace localhost or 127.0.0.1 with WSL IP for production
                url = url.replace('localhost', WSL_IP).replace('127.0.0.1', WSL_IP)
                return url
            return obj.image.url
        return None

class RoomFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomFee
        fields = ['name', 'amount']

class RoomTaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomTax
        fields = ['name', 'rate']  # Changed 'amount' to 'rate'

class RoomSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    base_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True, required=False)
    nights = serializers.IntegerField(read_only=True, required=False)
    features = serializers.CharField(read_only=True)
    amenities = serializers.CharField(read_only=True)
    fees = RoomFeeSerializer(many=True, read_only=True)
    taxes = RoomTaxSerializer(many=True, read_only=True)
    rental_slug = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ['id', 'name', 'description', 'base_price', 'max_occupancy', 'images', 'total_price', 'nights', 'features', 'amenities', 'fees', 'taxes', 'rental_slug']  # Replaced 'capacity' with 'max_occupancy'
    
    def get_images(self, obj):
        request = self.context.get('request')
        images = obj.images.all()
        return RoomImageSerializer(images, many=True, context={'request': request}).data

    def get_rental_slug(self, obj):
        return obj.rental.slug if obj.rental else None

class RentalSerializer(serializers.ModelSerializer):
    rooms = RoomSerializer(many=True, read_only=True)

    class Meta:
        model = Rental
        fields = ['id', 'name', 'slug', 'description', 'rooms']