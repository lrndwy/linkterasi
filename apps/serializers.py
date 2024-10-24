from rest_framework import serializers
from .models.sptModel import pengumuman as pengumuman_model
from .models.mainModel import master as master_model

class PengumumanSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = pengumuman_model
        fields = ['id_chat', 'pesan', 'waktu', 'kategori', 'user']
        
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = master_model
        fields = '__all__'

class CustomerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = master_model
        fields = '__all__'
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {key: value for key, value in representation.items() if value is not None}
