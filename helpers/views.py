from django.shortcuts import render

#Manage errors
def handle_not_found(request, exception, template_name="404.html"):
    return render(request,'404.html')