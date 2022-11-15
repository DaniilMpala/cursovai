from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import *
from .serializers import *
from sqlQuery.func import *
from drf_spectacular.utils import extend_schema, OpenApiParameter

@extend_schema(
    parameters=[
        OpenApiParameter(name='fullName', required=True, type=str),
        OpenApiParameter(name='course', required=True, type=int),
        OpenApiParameter(name='group', required=True, type=str),
    ]
)
@api_view(['POST',])
def queryAddStudent(request):
    newStudent = addStudent(request.data.get('fullName'), request.data.get('course'), request.data.get('group'))
    studentSerializer = StudentSerializer(instance=newStudent)
    return Response(studentSerializer.data)

@extend_schema(
    parameters=[
        OpenApiParameter(name='fullName', required=True, type=str),
        OpenApiParameter(name='course', required=True, type=int),
        OpenApiParameter(name='group', required=True, type=str),
    ]
)
@api_view(['GET',])
def queryGetStudent(request):
    students = getStudent(request.query_params.get('fullName'), request.query_params.get('course'), request.query_params.get('group'))

    if(students is None):
        return Response([])

    studentsSerializer = (StudentSerializer(instance=st).data for st in students) if students is not None else []

    return Response(studentsSerializer)

@extend_schema(
    parameters=[
        OpenApiParameter(name='title', required=True, type=str),
        OpenApiParameter(name='subject', required=True, type=str),
    ]
)
@api_view(['POST',])
def queryAddPracticalWork(request):
    newStudent = addPracticalWork(request.data.get('title'), request.data.get('subject'))
    workSerializer = PracticalWorkSerializer(instance=newStudent)
    return Response(workSerializer.data)

@extend_schema(
    parameters=[
        OpenApiParameter(name='title', required=True, type=str),
        OpenApiParameter(name='subject', required=True, type=str),
    ]
)
@api_view(['GET',])
def queryGetPracticalWork(request):
    works = getPracticalWork(request.query_params.get('title'), request.query_params.get('subject'))

    if(works is None):
        return Response([])

    worksSerializer = (PracticalWorkSerializer(instance=st).data for st in works) if works is not None else []

    return Response(worksSerializer)

@extend_schema(
    parameters=[
        OpenApiParameter(name='idStudent', required=True, type=int),
        OpenApiParameter(name='idPracticalWork', required=True, type=int),
    ]
)
@api_view(['POST',])
def queryAddCompletedWork(request):
    work = addCompletedWork(request.data.get('idStudent'), request.data.get('idPracticalWork'))
    workSerializer = AddCompletedWorkSerializer(instance=work)
    return Response(workSerializer.data)

@extend_schema(
    parameters=[
        OpenApiParameter(name='idStudent', required=True, type=int)
    ]
)
@api_view(['GET',])
def queryGetCompletedWork(request):
    works = getCompletedWork(request.query_params.get('idStudent'))

    print(works)
    if(works is None):
        return Response([])

    worksSerializer = (CompletedWorkSerializer(instance=st).data for st in works) if works is not None else []

    return Response(worksSerializer)