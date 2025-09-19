# wt-django-tools
[![Pytest](https://github.com/ian-wt/wt-django-tools/actions/workflows/pytest.yaml/badge.svg?branch=master)](https://github.com/ian-wt/wt-django-tools/actions/workflows/pytest.yaml)
[![codecov](https://codecov.io/gh/ian-wt/wt-django-tools/graph/badge.svg?token=9MHTDPGG1N)](https://codecov.io/gh/ian-wt/wt-django-tools)

Tools and abstractions for Django projects.

## Installation
This project isn't yet published on PyPI. To install directly from GitHub using pip:
```shell
pip install "wt-django-tools @ git+https://github.com/ian-wt/wt-django-tools.git@master"
```
Once installed, add ```wt_tools``` to ```INSTALLED_APPS``` in your settings module.
```shell
INSTALLED_APPS = [
  ...
  'wt_tools',
]
```

## Use
### Pagination Tags
To use the ```pagination_tags``` templatetags library in your project,
first load the tags with ```{% load pagination_tags %}.```

To use the ```relative_url``` tag, you need to pass to the tag a page index.
This could be a number or the string ```'last'``` if the index is in the final
position of the paginated ```QuerySet```. The tag additionally accepts optional
arguments for ```field_name``` and ```urlencode```.

Most often, you'll leave the ```field_name``` parameter alone since the default
value of ```'page'``` is fairly semantic as it is. But, this value can be
overridden in your views so make sure your views and the ```field_name``` arg
passed to the tag are consistent.

Last, the ```urlencode``` parameter is used when a query string may be present.
If your view won't ever handle a query string, then you can leave the default
value of ```None``` alone.

#### Example
```html
{% extends 'base.html' %}
{% load pagination_tags %}
<h1>Hello World!</h1>
<a href="{% relative_url page_obj.next_page_number %}"
```
To extend this example further we can supply values to override the defaults:
```html
{% extends 'base.html' %}
{% load pagination_tags %}
<h1>Hello World!</h1>
<a href="{% relative_url page_obj.next_page_number 'page' request.GET.urlencode %}"
```

#### Note
To use this tag alone, adding ```wt_tools``` to ```INSTALLED_APPS``` isn't
completely necessary. You could alternatively update ```TEMPLATES``` to
include ```pagination_tags``` directly:
```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                ...
            ],
            'libraries': {
                'pagination_tags': 'wt_tools.templatetags.pagination_tags',
            }
        },
    },
]
```
However, I only recommend taking this approach if you're certain you'll use no
other features (which may need explicit installation) from this package.