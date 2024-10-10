from datetime import datetime
import re
import textwrap
from django.utils import timezone
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from demands.models import Activity, Demands
from django.core.paginator import Paginator
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.contrib.auth.models import User


@login_required()
def index(request):
    context = getContext(request)
    return render(request, 'index.html', context)

@login_required()
def createDemand(request):
    if request.method == 'POST':
        demand = getRequestData(request)               
        # Validação dos campos obrigatórios
        if not demand['title'] or not demand['demand'] or not demand['status'] or not demand['objective'] or not demand['dueDate']:
            messages.add_message(request, messages.WARNING, 'Todos os campos são obrigatórios.')
            return redirect('/')

        # Validação da data (se é válida e futura)
        try:
            demand['dueDate'] = timezone.datetime.strptime(demand['dueDate'], '%Y-%m-%d').date()
            if demand['dueDate'] < timezone.now().date():
                messages.add_message(request, messages.WARNING, 'A data deve ser uma data futura válida.')
                return redirect('/')
        except ValueError:
            messages.add_message(request, messages.WARNING, 'Formato de data inválido.')
            return redirect('/')

        # Criar a demanda se tudo for válido
        Demands.objects.create(
            title=demand['title'],
            demand=demand['demand'],
            url=demand['url'],
            status=demand['status'],
            objective=demand['objective'],
            summary=demand['summary'],
            dueDate=demand['dueDate'],
            demand_type=demand['demand_type'],
            user=request.user
        )
        messages.add_message(request, messages.SUCCESS, 'Demanda cadastrada com sucesso!')
        return redirect('/')  # Redireciona após a criação

@login_required()
def view(request, id):
    if request.method == 'GET':
        if not id:
            messages.add_message(request, messages.WARNING, 'Insira um ID válido')
            return redirect('/')
        try:
            demand = Demands.objects.get(pk=id)
            context = getContext(request)
            activities = Activity.objects.filter(demand=demand).order_by('-createdAt')  # Busca as atividades relacionadas à demanda
            total_time = sum_times(activities)
            context = getContext(request)
            context.update({'demand': demand, 'activities': activities, 'total_time': total_time})  # Adiciona as atividades ao contexto
            return render(request, 'index.html', context)
        except Demands.DoesNotExist:
            # Se a demanda não for encontrada, mostra mensagem de erro
            messages.add_message(request, messages.WARNING, 'Demanda não encontrada')
            return redirect('/')
        
@login_required()
def editUser(request, id):
    if request.method == 'POST':
        if not id:
            messages.add_message(request, messages.WARNING, 'Insira um ID válido')
            return redirect('/')
        try:
            user = User.objects.get(pk=id)
            user.first_name = request.POST.get('first_name').strip()
            user.last_name = request.POST.get('last_name').strip()
            user.email = request.POST.get('email').strip()
            if request.POST.get("password") != "":
                user.set_password(request.POST.get("password"))
            user.save()
            if request.POST.get("password") != "":
                request.session.flush()
            messages.add_message(request, messages.SUCCESS, 'Usuário alterado com sucesso!')
            return redirect('/')
        except User.DoesNotExist:
            # Se a demanda não for encontrada, mostra mensagem de erro
            messages.add_message(request, messages.WARNING, 'Usuário não existe')
            return redirect('/')

@login_required()
def edit(request, id):
    if request.method == 'POST':
        if not id:
            messages.add_message(request, messages.WARNING, 'Insira um ID válido')
            return redirect('/')
        try:
            demand = getRequestData(request)
            demandUpdate = Demands.objects.get(pk=id)
            demandUpdate.title = demand['title']
            demandUpdate.demand = demand['demand']
            demandUpdate.url = demand['url']
            demandUpdate.status = demand['status']
            demandUpdate.objective = demand['objective']
            demandUpdate.summary = demand['summary']
            demandUpdate.dueDate = demand['dueDate']
            demandUpdate.demand_type = demand['demand_type']
            demandUpdate.save()
            messages.add_message(request, messages.SUCCESS, 'Demanda alterada')
            return redirect('/')
        except Demands.DoesNotExist:
            # Se a demanda não for encontrada, mostra mensagem de erro
            messages.add_message(request, messages.WARNING, 'Demanda não encontrada')
            return redirect('/')

@login_required()
def search(request):
    user = request.user
    if request.method == 'GET':
        startDate = request.GET.get('startDate')
        endDate = request.GET.get('endDate')
        search_type = request.GET.get('search_type')
        action = request.GET.get('action')
        demand_id = request.GET.get('demand_id')
        
        if demand_id != "":
            try:
                demands = Demands.objects.filter(user=user, demand=demand_id)
                if demands.exists():
                    # Visualiza as demandas
                    for demand in demands:
                        activities = Activity.objects.filter(demand=demand)  # Obtém as atividades relacionadas
                        demand.activity_count = activities.count()
                        demand.total_time = sum_times(activities)  # Adiciona o total de tempo como um atributo na demanda
                    messages.add_message(request, messages.SUCCESS, 'Demandas encontradas')
                    context = getContextWithoutQuery(request)
                    context.update({'demands': demands})
                    return render(request, 'index.html', context)
            except Demands.DoesNotExist:
                # Caso a demanda não seja encontrada
                messages.add_message(request, messages.WARNING, 'Demandas não encontradas')
                return redirect('/')
        else:
            if not startDate or not endDate or not search_type or not action:
                messages.add_message(request, messages.WARNING, 'Preencha com data inicial, data final, tipo e ação')
                return redirect('/')
            try:
                # Converte as strings de data para objetos datetime
                start_date = datetime.strptime(startDate, '%Y-%m-%d')
                end_date = datetime.strptime(endDate, '%Y-%m-%d')
                
                # Ajusta o final do intervalo para incluir o final do dia
                end_date = end_date.replace(hour=23, minute=59, second=59)
                
                # Pesquisa por Demanda
                if search_type == '1':
                    # Filtra as demandas no intervalo de datas
                    demands = Demands.objects.filter(user=user, createdAt__range=(start_date, end_date))
                    if demands.exists():
                        # Visualiza as demandas
                        if  action == '1':
                            for demand in demands:
                                activities = Activity.objects.filter(demand=demand)  # Obtém as atividades relacionadas
                                demand.activity_count = activities.count()
                                demand.total_time = sum_times(activities)  # Adiciona o total de tempo como um atributo na demanda
                            messages.add_message(request, messages.SUCCESS, 'Demandas encontradas')
                            context = getContextWithoutQuery(request)
                            context.update({'demands': demands})
                            return render(request, 'index.html', context)
                        if action == '2':
                            return download_pdf(demands, request.user, startDate, endDate)   
                    else:
                        messages.add_message(request, messages.WARNING, 'Demandas não encontradas')
                        return redirect('/')
                    
                # Pesquisa por Atividade
                if search_type == '2':
                    # Filtra as demandas no intervalo de datas
                    activities = Activity.objects.filter(createdAt__range=(start_date, end_date))
                    # Obtem as demandas relacionadas a essas atividades                
                    demands = Demands.objects.filter(user=user, createdAt__range=(start_date, end_date)).distinct()
                    for demand in demands:
                        activities = Activity.objects.filter(demand=demand)  # Obtém as atividades relacionadas
                        demand.activity_count = activities.count()
                        demand.total_time = sum_times(activities)  # Adiciona o total de tempo como um atributo na demanda
                    # Visualiza as demandas
                    if  action == '1':
                        messages.add_message(request, messages.SUCCESS, 'Demandas encontradas')
                        context = getContextWithoutQuery(request)
                        context.update({'demands': demands})
                        return render(request, 'index.html', context)
                    if action == '2':
                        return download_pdf(demands, request.user, startDate, endDate)               

            except ValueError:
                # Caso as datas estejam em um formato incorreto
                messages.add_message(request, messages.WARNING, 'Formato de data inválido')
                return redirect('/')

            except Demands.DoesNotExist:
                # Caso a demanda não seja encontrada
                messages.add_message(request, messages.WARNING, 'Demandas não encontradas')
                return redirect('/')

@login_required()
def createActivity(request):
    if request.method == 'POST':
        id = request.POST.get('id').strip()
        title = request.POST.get('title').strip()
        date = request.POST.get('date').strip()     
        time = request.POST.get('time').strip()
        print(id, title, date, time)     
        # Validação dos campos obrigatórios
        if not title or not date or not time:
            messages.add_message(request, messages.WARNING, 'Todos os campos são obrigatórios.')
            return redirect('/')
        # Expressão regular para verificar o formato HH:MM
        time_pattern = r'^([01][0-9]|2[0-3]):[0-5][0-9]$'

        # Verificar se o campo 'time' está no formato HH:MM
        if not re.match(time_pattern, time):
            messages.add_message(request, messages.WARNING, 'O campo "Tempo" deve estar no formato HH:MM.')
            return redirect('/')
        
        try:
            demand = Demands.objects.get(pk=id)
            Activity.objects.create(
                title=title,
                date=date,
                time=time,
                demand=demand
            )
            return redirect('/demands/view/'+id)
        except Demands.DoesNotExist:
            # Se a demanda não for encontrada, mostra mensagem de erro
            messages.add_message(request, messages.WARNING, 'Demanda não encontrada')
            return redirect('/')
        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Ocorreu um erro: {str(e)}')
            return redirect('/')

@login_required()
def deleteActivity(request, id):
    if request.method == 'POST':
        demand_id = request.POST.get('demand_id')
        if not id:
            messages.add_message(request, messages.WARNING, 'Insira um ID válido')
            return redirect('/')
        try:
            activity = Activity.objects.get(pk=id)
            activity.delete()
            messages.add_message(request, messages.SUCCESS, 'Atividade removida com sucesso!')
            return redirect('/demands/view/'+demand_id)
        except Demands.DoesNotExist:
            # Se a demanda não for encontrada, mostra mensagem de erro
            messages.add_message(request, messages.WARNING, 'Demanda não encontrada')
            return redirect('/')
            
# INTERNAL
        
def getContext(request):
    user = request.user
    demands_all = Demands.objects.filter(user=user).order_by('-createdAt')
    status_choices = Demands.STATUS_CHOICES
    demand_types = Demands.DEMAND_CHOICES
    today = timezone.now().date().strftime('%Y-%m-%d')
    limit = request.GET.get('limit', 10)
    paginator = Paginator(demands_all, limit)  # Paginar com 10 itens por página
    page_number = request.GET.get('page')
    demands = paginator.get_page(page_number)
    # Itera sobre cada demanda e calcula o total de tempo de suas atividades
    for demand in demands:
        activities = Activity.objects.filter(demand=demand)  # Obtém as atividades relacionadas
        demand.activity_count = activities.count()
        demand.total_time = sum_times(activities)  # Adiciona o total de tempo como um atributo na demanda
        
    context = {
        'pagina': 'demands/demands.html',
        'page_name': 'Minhas demandas',
        'demands': demands,
        'status_choices': status_choices,
        'demand_types': demand_types,
        'today': today,
        'limit': limit
    }
    return context

def getContextWithoutQuery(request):
    status_choices = Demands.STATUS_CHOICES
    demand_types = Demands.DEMAND_CHOICES
    today = timezone.now().date().strftime('%Y-%m-%d')
    limit = request.GET.get('limit', 10)
    context = {
        'pagina': 'demands/demands.html',
        'page_name': 'Minhas demandas',
        'status_choices': status_choices,
        'demand_types': demand_types,
        'today': today,
        'limit': limit
    }
    return context

def getRequestData(request):
        title = request.POST.get('title').strip()
        demand = request.POST.get('demand').strip()
        status = request.POST.get('status').strip()
        demand_type = request.POST.get('demand_type').strip()
        objective = request.POST.get('objective').strip()
        dueDate = request.POST.get('dueDate').strip()
        summary = request.POST.get('summary').strip()
        url = request.POST.get('url').strip()
        dueDate = request.POST.get('dueDate')
        
        return {
            'title': title,
            'demand': demand,
            'status': status,
            'dueDate': dueDate,
            'objective': objective,
            'summary': summary,
            'url': url,
            'dueDate': dueDate,
            'demand_type': demand_type
        }
        
def sum_times(activities):
    total_minutes = 0
    
    # Expressão regular para capturar o formato HH:MM
    time_pattern = re.compile(r'(\d{2}):(\d{2})')

    for activity in activities:
        match = time_pattern.match(activity.time)
        if match:
            hours = int(match.group(1))  # Captura as horas
            minutes = int(match.group(2))  # Captura os minutos
            
            # Converte horas para minutos e soma
            total_minutes += hours * 60 + minutes

    # Converte o total de minutos de volta para o formato HH:MM
    total_hours = total_minutes // 60
    remaining_minutes = total_minutes % 60

    return f"{total_hours:02}:{remaining_minutes:02}"  # Formato HH:MM

def download_pdf(demands, user, startDate, endDate):
    startDateObj = datetime.strptime(startDate, "%Y-%m-%d")
    startDateFormated = startDateObj.strftime("%d-%m-%Y")
    endDateObj = datetime.strptime(endDate, "%Y-%m-%d")
    endDateFormated = endDateObj.strftime("%d-%m-%Y")

    # Criação da resposta HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Relatório {user.first_name} {user.last_name} - {startDateFormated} a {endDateFormated}.pdf"'

    # Criação do PDF
    p = canvas.Canvas(response, pagesize=letter)
    p.setTitle("Relatório de atividades")  # Define o título do documento

    width, height = letter
    y_position = height - 60

    # Adicionar o título principal no início do documento
    p.setFont("Helvetica-Bold", 20)
    title = f"Relatório {user.first_name} {user.last_name} - {startDateFormated} a {endDateFormated}"
    p.drawString(60, y_position, title)

    # Adicionar uma linha abaixo do título
    y_position -= 30
    p.setLineWidth(1.5)
    p.line(60, y_position, width - 60, y_position)

    # Espaçamento maior antes de continuar o documento
    y_position -= 50

    # Agrupar demandas por demand_type
    grouped_demands = {}
    for demand in demands:
        if demand.demand_type not in grouped_demands:
            grouped_demands[demand.demand_type] = []
        grouped_demands[demand.demand_type].append(demand)

    # Obter a ordem de demand_type de acordo com DEMAND_CHOICES
    demand_type_order = [choice[0] for choice in Demands.DEMAND_CHOICES]

    # Iterar sobre os tipos de demandas na ordem de DEMAND_CHOICES
    for demand_type in demand_type_order:
        if demand_type in grouped_demands:
            # Adicionar o título da categoria (demand_type) no PDF
            p.setFont("Helvetica-Bold", 18)
            p.drawString(60, y_position, demand_type)
            y_position -= 20

            # Adicionar uma linha abaixo do demand_type
            p.setLineWidth(1)
            p.line(60, y_position, width - 60, y_position)
            y_position -= 30

            # Iterar sobre as demandas de cada tipo
            for demand in grouped_demands[demand_type]:
                p.setFont("Helvetica-Bold", 15)
                p.drawString(60, y_position, demand.demand + " - " + demand.title.upper())
                y_position -= 30

                p.setFont("Helvetica-Bold", 12)
                p.drawString(60, y_position, "Objetivo:")
                y_position -= 15

                p.setFont("Helvetica", 12)
                wrapped_text_objective = textwrap.wrap(demand.objective, width=80)
                for line in wrapped_text_objective:
                    p.drawString(60, y_position, line)
                    y_position -= 15
                    if y_position < 50:
                        p.showPage()
                        y_position = height - 60

                y_position -= 10
                p.setFont("Helvetica-Bold", 12)
                p.drawString(60, y_position, "Status:")
                p.setFont("Helvetica", 12)
                p.drawString(120, y_position, f" {demand.status}")
                y_position -= 15

                p.setFont("Helvetica-Bold", 12)
                p.drawString(60, y_position, "Previsão:")
                dueDateFormatted = demand.dueDate.strftime("%d/%m")
                p.setFont("Helvetica", 12)
                p.drawString(120, y_position, f" {dueDateFormatted}")
                y_position -= 20

                p.setFont("Helvetica-Bold", 12)
                p.drawString(60, y_position, "Resumo:")
                y_position -= 15

                wrapped_text_summary = textwrap.wrap(demand.summary, width=80)
                p.setFont("Helvetica", 12)
                for line in wrapped_text_summary:
                    p.drawString(60, y_position, line)
                    y_position -= 15
                    if y_position < 50:
                        p.showPage()
                        y_position = height - 60

                y_position -= 20
                p.setFont("Helvetica-Bold", 12)
                p.drawString(60, y_position, "Atividades:")
                y_position -= 15

                # Agrupando as atividades pela data para evitar repetição de datas
                activities = Activity.objects.filter(demand=demand, date__range=[startDateObj, endDateObj]).order_by('date')
                grouped_activities = {}

                for activity in activities:
                    activity_date_formatted = activity.date.strftime("%d/%m/%Y")
                    if activity_date_formatted not in grouped_activities:
                        grouped_activities[activity_date_formatted] = []
                    grouped_activities[activity_date_formatted].append(activity.title)

                for date, titles in grouped_activities.items():
                    p.setFont("Helvetica-Bold", 12)
                    p.drawString(70, y_position, "- " + date)
                    y_position -= 15

                    p.setFont("Helvetica", 12)
                    for title in titles:
                        p.drawString(78, y_position, title)
                        y_position -= 15

                        if y_position < 50:
                            p.showPage()
                            y_position = height - 60

                p.setLineWidth(1)
                p.line(60, y_position, width - 60, y_position)
                y_position -= 30

                if y_position < 50:
                    p.showPage()
                    y_position = height - 60

    p.showPage()
    p.save()

    return response