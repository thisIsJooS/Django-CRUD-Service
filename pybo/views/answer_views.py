from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404, redirect, resolve_url
from django.utils import timezone
from ..forms import AnswerForm
from django.core.paginator import Paginator
from ..models import Question, Answer
from django.db.models import Q

@login_required(login_url='common:login')
def answer_create(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author = request.user # author 속성에 로그인계정 저장
            answer.create_date = timezone.now()
            answer.question = question
            answer.save()
            return redirect('{}#answer_{}'.format(
                resolve_url('pybo:question_detail', question_id=question.id), answer.id
            ))
    else:
        return HttpResponseNotAllowed('Only POST is possible')
    context = {'question': question, 'form': form}
    return render(request, 'pybo/question_detail.html', context)


@login_required(login_url='common:login')
def answer_modify(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    if request.user!=answer.author:
        messages.error(request, '수정권한이 없습니다.')
        return redirect('pybo:question_detail', question_id=answer.question.id)
    
    if request.method == 'POST':
        form = AnswerForm(request.POST, instance=answer)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.modify_date = timezone.now()
            answer.save()
            return redirect('{}#answer_{}'.format(
                resolve_url('pybo:question_detail', question_id=answer.question.id), answer.id
            ))
    
    else:
        form = AnswerForm(instance=answer)            
    context = {'answer':answer, 'form':form}
    return render(request, 'pybo/answer_form.html', context)


@login_required(login_url='common:login')
def answer_delete(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    if request.user != answer.author:
        messages.error(request, '삭제권한이 없습니다.')
    else:
      answer.delete()
    return redirect('pybo:question_detail', question_id=answer.question.id)


@login_required(login_url='common:login')
def answer_vote(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    if request.user == answer.author:
        messages.error(request, '본인이 작성한 글은 추천할 수 없습니다.')
    else:
        answer.voter.add(request.user)
    return redirect('{}#answer_{}'.format(
        resolve_url('pybo:question_detail', question_id=answer.question.id), answer.id
    ))
    

def answer_list(request):
    page = request.GET.get('page', '1')
    kw = request.GET.get('kw', '')
    answer_list = Answer.objects.order_by('-create_date')
    if kw:
        answer_list = answer_list.filter(
        Q(question__subject__icontains=kw) | # 제목 검색
        Q(question__content__icontains=kw) | # 내용 검색
        Q(content__icontains=kw) | # 답변 내용
        Q(question__author__username__icontains=kw) | # 질문 글쓴이 검색
        Q(author__username__icontains=kw)  # 답변 글쓴이
    ).distinct()
        
    paginator = Paginator(answer_list, 10)
    page_obj = paginator.get_page(page)
    context = {'answer_list': page_obj, 'page': page, 'kw':kw}
    return render(request, 'pybo/answer_list.html', context)