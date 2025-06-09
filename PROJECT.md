s# Shoes Shop eCommerce
In this project, we are building an ecommerce application for selling and buying shoes. We will be using Django for Backend and React Js and Tailwind for frontend,  and Django Rest Framework and APIs. During development and for MVP, we will use Bootstrap and CSS3 for the frontend.

## Step 1 : Set up
At this stage, we set up our development environment, create the project and the `main` app. We then run the development server and open the project in our browser to confirm the setup success.

- Create virtual environment

```
python -m venv venv
```

- Activate virtual environment

```
venv/scripts/activate
```

- Install django

```
pip install django
```

- Create project

```
django-admin startproject config .
```

- Create `main` app

```
py manage.py startapp main
```

- Run server

```
py manage.py runserver
```

- Open project in the browser at:

<a href="http://127.0.0.1:8000/" target="_blanck">http://127.0.0.1:8000/</a>

## Step 2: Application configuration
At this stage we will configure our `main` up to the project settings. We will create app urls and include it in the projects main urls configuration. We will create our first view `home` and route it in the app's url. We will return HTTPResponse to the server.

- Add `main` app to the INSTALLED_APPS in `settings.py`

```
# config/settings.py

INSTALLED_APPS = [
    ...
    'main',
]
```

- Create `home` view

```
# main/views.py

from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse("Hello world")

```

- Create app urls.py

In the `main` app create `urls.py` file. Import the views and urls path

```
# main/urls.py

from django.urls import path
from . import views
    
urlpatterns = [
    path('', views.home, name="home"),
]
```

- Include the app `urls` to the projects `urls.py`

Ensure you import `include` from `django.urls`

``` 
# config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    ...
    path('', include('main.urls')),
]
```

- Run the server and open the project at:
 <a href="http://127.0.0.1:8000/" target="_blanck">http://127.0.0.1:8000/</a>

You should now see **Hello world** in your screen

## Step 3: Django templates
In this step, we will create and render django templates. We will also create a base templates (template inheritance) that will be extended in many or most of the template files.

- Create a `templates` directory (folder)

In the `main` app create a directory and name it `templates`.

We will also add a nother folder in the `templates` folder called `main` (Since we will be having many other apps and templates, to differentiate these template files, we create a the `main` folder similar to the `main` app. If we have `store` app, this folder will be `store`)

In the `templates/main` directory, create a html file `home.html`.

Add a few lines of html code:

```
# templates/main/home.html

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    <h1>Hello world. This is from a template file</h1>
</body>
</html>
```

- Update `home` view to now render the template

You can remove the HttpResponse

```
# main/views.py

from django.shortcuts import render
def home(request):
    return render(request, 'main/home.html')
```

- Run the server and check your screen for:

**Hello world. This is from a template file**


### Template inheritance
Django template inheritance is a powerful feature that allows you to create a base template with common structure and design, and then extend it in other templates to avoid repetition. This makes your code cleaner, more maintainable, and easier to update.

- Create `base.html` file in `templates/main` folder

Add the base html files: 
```
# main/base.html

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <title>{% block title %}{% endblock %}</title>
</head>
<body>
    {% block content %}
    {% endblock %}
</body>
</html>
```

Do you see Django block Tag inside the `<title>` element, and the `<body>` element?

They are placeholders, telling Django to replace this block with content from other sources.

- Modify `home.html`

We start by extending the `base.html` template

`{% extends "main/base.html" %}`

Using the tags defined in the base template you can now extend the html structures to the home template:

```
# main/home.html
{% extends "main/base.html" %}
    {% block title %}
        Shoe Shop Ecommerce
    {% endblock %}

    {% block content %}
        <h1> Shoe Shop Ecommerce </h1>
        <p>Hello world. This is from a template file</p>
    {% endblock %}
```

- Run the server and confirm that the new title and html texts are now displayed

We will be extending this base template in most if not all of the templates that requires that html structure. 

Other links such as external css and js will also be added to this base template once and reused in any other template extending the base template.


## Step 4: Static files (CSS, JS & Media files)

- Add `static` folder

In the root directory (same as `config`), create a new folder 'static`

Add other folders - `css, js, images`

Create files in these folders - main.css in css folder, main.js in js folder and add some images in the images folder


### CSS

Add some css to style our `home.html`:

```
body {
    background-color: blue;
    color: white;
}

p { 
    font-size: 40px;
}
```

- Load static

In `base.html` add `{% load static %}` at the beggining

In the head section, add the link to the css

`<link rel="stylesheet" href="{% static 'css/main.css' %}">`

```
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>{% block title %}{% endblock %}</title>
    <link rel="stylesheet" href="{% static 'css/main.css' %}">
</head>
<body>
    {% block content %}
    {% endblock %}
</body>
</html>
```

- Configure static directory

```
config/settings.py
---
STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

```

- Run the server and see that the styles have been added

### JavaScript
JavaScript is added the same way we added **CSS**

```
#main/base.html

<script src="{% static 'js/main.js' %}"></script>
```

```
# static/js/main.js

document.getElementById('clickme').addEventListener('click', () => {
    document.body.style.backgroundColor = "Red";
})
```

### Images

Add `<img src="{% static 'images/shoes.jpg' %}" alt="" width="200px">` to `home.html`

Add `{% load static %}` after  `{% extends "main/base.html" %}` (We are loading a static file directly to this template)

Ensure you have `shoes.jpg` or any image in `static/images` folder

```
# main/home.html

{% extends "main/base.html" %}
{% load static %}

---

{% block content %}
---
<img src="{% static 'images/shoes.jpg' %}" alt="" width="200px">
{% endblock %}
```

- Run the server and observe the image displayed in the browser