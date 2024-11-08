# apps/authentication/views.py
from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib import messages

class CustomLoginView(LoginView):
   template_name = 'authentication/login.html'
   redirect_authenticated_user = True
   success_url = reverse_lazy('home')

   def get_success_url(self):
       return self.success_url

   def form_invalid(self, form):
       messages.error(self.request, 'Usuario o contraseña incorrectos')
       return super().form_invalid(form)

@login_required 
def home(request):
   return render(request, 'home.html', {
       'title': 'Dashboard'
   })