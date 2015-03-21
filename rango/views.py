from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForms, PageForm, UserForm, UserProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from datetime import datetime
from rango.bing_search import run_query
# Create your views here.
def index(request):
    category_list=Category.objects.order_by('-likes')[:5]
    pages_list=Page.objects.order_by('-views')[:5]
    context_dict={'boldmessage': "I am bold content from context!",'categories':category_list,
                  'pages':pages_list}
    
    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False
    
    last_visit = request.session.get('last_visit')
   
    if last_visit:
       last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")
       
       if (datetime.now() - last_visit_time).seconds > 0:
           visits = visits + 1
           reset_last_visit_time = True
    else:
        reset_last_visit_time = True
    
    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    context_dict['visits'] = visits
    
    response = render(request, 'rango/index.html', context_dict)
    return response

def about(request):
    if request.session.get('visits'):
        count = request.session.get('visits')
    else:
        count = 0
    context_dict={'boldmessage': "This is the about page!", 'visits': count}
    return render(request, 'rango/about.html', context_dict)

def home(request):
    return HttpRespone("You are home.")

def category(request, category_name_slug):
    context_dict={}
    result_list = []
    
    try:
        category=Category.objects.get(slug=category_name_slug)
        context_dict['category_name']=category.name
        
        pages=Page.objects.filter(category=category)
        
        context_dict['pages']=pages
        
        context_dict['category']=category
        
        if request.method == 'POST':
            query = request.POST['query'].strip()
        
            if query:
                result_list = run_query(query)
        context_dict['result_list']=result_list
    except Category.DoesNotExist:
        pass
    
    return render(request, 'rango/category.html', context_dict)

def add_category(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/rango/login/')
        
    if request.method == 'POST':
        form = CategoryForms(request.POST)
        
        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print(form.errors)
    else:
        form = CategoryForms()
        
    return render(request, 'rango/add_category.html', {'form': form})

def add_page(request, category_name_slug):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/rango/category/{0}'.format(category_name_slug))
    
    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat = None
        
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()
                return category(request, category_name_slug)
        else:
            print(form.errors)
    else:
        form = PageForm()
        
    context_dict = {'form':form, 'category':cat}
    
    return render(request, 'rango/add_page.html', context_dict)
"""
def register(request):
    registered = False
    
    if request.method =='POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            
            profile = profile_form.save(commit=False)
            profile.user = user
            
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
                
            profile.save()
            
            registered= True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
        
    return render(request, 'rango/register.html',
                  {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

def user_login(request):
    if request.method =='POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(username=username, password=password)
        
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                return HttpResponse("Your account is disabled.")
        else:
            print("Invalid login details: {0}, {1}".format(username,password))
            return HttpResponse("Invalid login details supplied.<a href='/rango/'>Go back</a>")
    else:
        return render(request, 'rango/login.html',{})
"""

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html',{})
"""                
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/rango/')
"""  

def search(request):
    result_list = []
    
    if request.method == 'POST':
        query = request.POST['query'].strip()
        
        if query:
            result_list = run_query(query)
            
    return render(request, 'rango/search.html', {'result_list': result_list})
      
def track_url(request):  
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            page=Page.objects.get(id=page_id)
            page.views+=1
            page.save()
            return redirect(page.url)
        else:
            return HttpResponseRedirect('/rango/')  

def register_profile(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/rango/')
    
    if request.method=='POST':
        form=UserProfileForm(request.POST, request.FILES or None)
        if form.is_valid():
            profile=form.save(commit=False)
            profile.user=User.objects.get(id=request.user.id)
            profile.save()
        else:
            print(form.errors)
    else:
        form=UserProfileForm()
    
    return render(request, 'rango/profile_registration.html', {'form':form})
        
def profile(request):
    user=User.objects.get(id=request.user.id)
    profile=UserProfile.objects.get(user=user)        
        
    return render(request, 'rango/profile.html', {'user':user, 'profile':profile})
    
def userslist(request):
    users=User.objects.all()
    render(request, 'rango/users.html', {'users':users})