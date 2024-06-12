from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .models import Question, Choice,Tag
from django.views.decorators.csrf import csrf_exempt
import json


def my_view(request):
    # Your view logic here
    response = JsonResponse({'key': 'value'})
    response['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    return response

class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))




@csrf_exempt
def poll(request, id=None):
    if request.method == 'POST':
        data = json.loads(request.body)

        q = Question(question_text=data["Question"], pub_date=timezone.now())
        q.save()
        
        for choice, vote in data["OptionVote"].items():
            q.choice_set.create(choice_text=choice, votes=vote)
        
        for tag in data["Tags"]:
            t = Tag.objects.get_or_create(name=tag)[0]
            q.tags.add(t)
        
        res = {"msg": "Inserted polls successfully"}
        return JsonResponse(res)
    
    
    elif request.method == 'GET':
        id = request.GET.get('id')
    if id is not None:
        data = {}
        try:
            q = Question.objects.get(id=id)
            data["Question"] = q.question_text
            choice = {}
            for c in q.choice_set.all():
                choice[c.choice_text] = c.votes
            data["OptionVote"] = choice
            data["QuestionId"] = id
            tags = []

            for tag in q.tags.all():
                tags.append(tag.name)
            data["Tags"] = tags
            res = {"msg": "Fetched polls successfully", "data": data}
        except Question.DoesNotExist:
            res = {"msg": f"Question with id {id} not found"}

        return JsonResponse(res)
    else:
        tags_string = request.GET.get('tags')
        if tags_string:
            tags = tags_string.split(',')
            filtered_questions = Question.objects.filter(tags__name=tags[0])
            for tag in tags[1:]:
                filtered_questions = filtered_questions | Question.objects.filter(tags__name=tag)
                filtered_questions = filtered_questions.distinct()
        else:
            filtered_questions = Question.objects.all()
    
    polls_data = []
    for question in filtered_questions:
        question_data = {
            "Question": question.question_text,
            "OptionVote": {choice.choice_text: choice.votes for choice in question.choice_set.all()},
            "QuestionId": question.id,
            "Tags": [tag.name for tag in question.tags.all()]
        }
        polls_data.append(question_data)

    return JsonResponse({"msg": "Fetched polls successfully", "data": polls_data})

#update poll vote
@csrf_exempt
def update_poll_vote(request, id):
    if request.method == 'PUT':
        data = json.loads(request.body)
        increment_option = data.get("incrementOption")

        if increment_option:
            try:
                question = Question.objects.get(id=id)
                choice_to_increment = question.choice_set.get(choice_text=increment_option)
                choice_to_increment.votes += 1
                choice_to_increment.save()
                res = {"msg": "Poll vote updated successfully"}
            except (Question.DoesNotExist, Choice.DoesNotExist):
                res = {"msg": f"Question or choice with id {id} not found"}
        else:
            res = {"msg": "Please provide 'incrementOption' in the payload"}

        return JsonResponse(res)
    else:
        return JsonResponse({"msg": "Invalid request method"}, status=405)
    
#get a poll
@csrf_exempt
def get_poll_details(request, id):
    if request.method == 'GET':
        try:
            question = Question.objects.get(id=id)
            options = {}
            for choice in question.choice_set.all():
                options[choice.choice_text] = choice.votes

            tags = [tag.name for tag in question.tags.all()]
            
            poll_details = {
                "Question": question.question_text,
                "OptionVote": options,
                "QuestionID": question.id,
                "Tags": tags
            }
            
            response = JsonResponse({"msg": "Fetched poll details successfully", "data": poll_details})
            # Allow CORS for the response
            response["Access-Control-Allow-Origin"] = "*"
            return response
        except Question.DoesNotExist:
            return JsonResponse({"error": f"Question with ID {id} not found"}, status=404)
    else:
        return JsonResponse({"error": "Only GET requests are allowed"}, status=405)
 
#list tags
@csrf_exempt
def list_tags(request):
    if request.method == 'GET':
        unique_tags = set(Tag.objects.values_list('name', flat=True))
        response = JsonResponse({"Tags": list(unique_tags)})
        response["Access-Control-Allow-Origin"] = "*"
        return response
    else:
        return JsonResponse({"error": "Only GET requests are allowed"}, status=405)
