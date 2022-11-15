from rest_framework import serializers

class StudentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    fullName = serializers.CharField()
    course = serializers.IntegerField()
    group = serializers.CharField()
    

class PracticalWorkSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    subject = serializers.CharField()

class CompletedWorkSerializer(serializers.Serializer):
    date = serializers.DateField()
    fullName = serializers.CharField()
    course = serializers.IntegerField()
    group = serializers.CharField()
    subject = serializers.CharField()
    title = serializers.CharField()
    
class AddCompletedWorkSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    idStudent = serializers.IntegerField()
    idPracticalWork = serializers.IntegerField()