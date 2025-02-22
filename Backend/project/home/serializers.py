from rest_framework import serializers
from .models import ClintReview


class ReviewSerializer(serializers.ModelSerializer):
    user_full_name = serializers.SerializerMethodField()

    class Meta:
        model = ClintReview
        fields = [ 'user_full_name', 'review', 'date', 'image']
        read_only_fields = ['user']  # المستخدم سيتم تعيينه تلقائيًا

    def get_user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    


from rest_framework import serializers
from .models import Contact

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'
