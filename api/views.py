from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import *
from .serializers import *
from sqlQuery.func import *
from drf_spectacular.utils import extend_schema, OpenApiParameter
import re

@extend_schema(
    parameters=[
        OpenApiParameter(name='fullName', required=False, type=str),
        OpenApiParameter(name='course', required=False, type=int),
        OpenApiParameter(name='group', required=False, type=str),
    ]
)
@api_view(['POST',])
def queryAddStudent(request):
    if( 
        re.search("[a-zA-Zа-яА-Я ]*", request.data.get('fullName'))[0] != request.data.get('fullName') or
        re.search("[\d]*", request.data.get('course'))[0] != request.data.get('course') or
        re.search("[a-zA-Zа-яА-Я \d-]*", request.data.get('group'))[0] != request.data.get('group')
    ): return Response({'error':'Ошибка вводе параметра'})

    newStudent = addStudent(request.data.get('fullName'), request.data.get('course'), request.data.get('group'))
    studentSerializer = StudentSerializer(instance=newStudent)
    return Response(studentSerializer.data)

@extend_schema(
    parameters=[
        OpenApiParameter(name='fullName', required=False, type=str),
        OpenApiParameter(name='course', required=False, type=int),
        OpenApiParameter(name='group', required=False, type=str),
    ]
)
@api_view(['GET',])
def queryGetStudent(request):
    if( 
        re.search("[a-zA-Zа-яА-Я ]*", request.query_params.get('fullName') or '')[0] != (request.query_params.get('fullName') or '') or
        re.search("[\d]*", request.query_params.get('course') or '')[0] != (request.query_params.get('course') or '') or
        re.search("[a-zA-Zа-яА-Я \d-]*", request.query_params.get('group') or '')[0] != (request.query_params.get('group') or '')
    ): return Response({'error':'Ошибка вводе параметра'})
    
    students = getStudent(request.query_params.get('fullName') or '', request.query_params.get('course') or '', request.query_params.get('group') or '')

    if(students is None):
        return Response([])

    studentsSerializer = (StudentSerializer(instance=st).data for st in students) if students is not None else []

    return Response(studentsSerializer)

@extend_schema(
    parameters=[
        OpenApiParameter(name='title', required=False, type=str),
        OpenApiParameter(name='subject', required=False, type=str),
    ]
)
@api_view(['POST',])
def queryAddPracticalWork(request):
    if( 
        re.search("[a-zA-Zа-яА-Я \-,.\d]*", request.data.get('title'))[0] != request.data.get('title') or
        re.search("[a-zA-Zа-яА-Я \-,.\d]*", request.data.get('subject'))[0] != request.data.get('subject')
    ): return Response({'error':'Ошибка вводе параметра'})

    newStudent = addPracticalWork(request.data.get('title'), request.data.get('subject'))
    workSerializer = PracticalWorkSerializer(instance=newStudent)
    return Response(workSerializer.data)

@extend_schema(
    parameters=[
        OpenApiParameter(name='title', required=False, type=str),
        OpenApiParameter(name='subject', required=False, type=str),
    ]
)
@api_view(['GET',])
def queryGetPracticalWork(request):
    if( 
        re.search("[a-zA-Zа-яА-Я \-,.\d]*", request.query_params.get('title') or '')[0] != (request.query_params.get('title') or '') or
        re.search("[a-zA-Zа-яА-Я \-,.\d]*", request.query_params.get('subject') or '')[0] != (request.query_params.get('subject') or '')
    ): return Response({'error':'Ошибка вводе параметра'})

    works = getPracticalWork(request.query_params.get('title') or '', request.query_params.get('subject') or '')

    if(works is None):
        return Response([])

    worksSerializer = (PracticalWorkSerializer(instance=st).data for st in works) if works is not None else []

    return Response(worksSerializer)

@extend_schema(
    parameters=[
        OpenApiParameter(name='idStudent', required=False, type=int),
        OpenApiParameter(name='idPracticalWork', required=False, type=int),
    ]
)
@api_view(['POST',])
def queryAddCompletedWork(request):
    if( 
        re.search("[\d]*", request.data.get('idStudent'))[0] != request.data.get('idStudent') or
        re.search("[\d]*", request.data.get('idPracticalWork'))[0] != request.data.get('idPracticalWork')
    ): return Response({'error':'Ошибка вводе параметра'})

    work = addCompletedWork(request.data.get('idStudent'), request.data.get('idPracticalWork'))
    workSerializer = AddCompletedWorkSerializer(instance=work)
    return Response(workSerializer.data)

@extend_schema(
    parameters=[
        OpenApiParameter(name='idStudent', required=False, type=int)
    ]
)
@api_view(['GET',])
def queryGetCompletedWork(request):
    if( 
        re.search("[\d]*", request.query_params.get('idStudent') or '')[0] != (request.query_params.get('idStudent') or '')
    ): return Response({'error':'Ошибка вводе параметра'})

    works = getCompletedWork(request.query_params.get('idStudent') or '')

    print(works)
    if(works is None):
        return Response([])

    worksSerializer = (CompletedWorkSerializer(instance=st).data for st in works) if works is not None else []

    return Response(worksSerializer)