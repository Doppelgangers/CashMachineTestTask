from rest_framework import serializers

from cash_machine.models import Item


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


class ItemsListSerializer(serializers.Serializer):
    items = serializers.ListField(child=serializers.IntegerField())
