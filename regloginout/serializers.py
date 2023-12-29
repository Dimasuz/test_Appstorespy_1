from rest_framework import serializers
from regloginout.models import User


class UserSerializer(serializers.ModelSerializer):
    # contacts = ContactSerializer(read_only=True, many=True)
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email',)
        read_only_fields = ('id',)

