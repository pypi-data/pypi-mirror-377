# dsd-flyio-nanodjango

A proof-of-concept django-simple-deploy plugin that deploys nanodjango projects to Fly.io.

Sample nanodjango project
---

This is taken from the [nanodjango docs](https://docs.nanodjango.dev/en/latest/). I'm recreating my steps here, so anyone can try this out without looking at a variety of docs.

Make a directory for the nanodjango project, install `nanodjango`, and create the main project file:
```sh
$ mkdir my_nd_project
$ cd my_nd_project
my_nd_project$ uv venv .venv
my_nd_project$ source .venv/bin/activate
(.venv) my_nd_project$ uv pip install nanodjango
(.venv) my_nd_project$ touch counter.py
```

Here's what goes in `counter.py`:

```python
from django.db import models
from nanodjango import Django

app = Django()

@app.admin
class CountLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)

@app.route("/")
def count(request):
    # Standard Django function view
    CountLog.objects.create()
    return f"<p>Number of requests: {CountLog.objects.count()}</p>"

@app.api.get("/add")
def count(request):
    # Django Ninja API
    CountLog.objects.create()
    return {"count": CountLog.objects.count()}
```

Add `.gitignore`, commit the project, and run the project locally:

```sh
(.venv) my_nd_project$ ls -l
.gitignore
counter.py
(.venv) my_nd_project$ git init
(.venv) my_nd_project$ git add .
(.venv) my_nd_project$ git commit -am "Initial nanodjango project."
(.venv) my_nd_project$ nanodjango run counter.py
Starting development server at http://0.0.0.0:8000/
...
```

You should visit the locally-served project, and make sure it works.

Calling `run` creates the initial migrations, so let's commit:

```sh
(.venv) my_nd_project$ git add .
(.venv) my_nd_project$ git commit -am "Initial migration."
```

Configuration-only deployment
---

Now we're ready for deployment. We'll install this plugin, which will also install `django-simple-deploy`. We'll also freeze requirements:

```sh
$ uv pip install dsd-flyio-nanodjango
 + django-simple-deploy==1.3.0
 + dsd-flyio-nanodjango==0.1.0
 (.venv) my_nd_project$ uv pip freeze > requirements.txt
```

Now we'll add `django_simple_deploy` to the project script:

```python
from django.db import models
from nanodjango import Django

app = Django(
    EXTRA_APPS=["django_simple_deploy"],
)

@app.admin
class CountLog(models.Model):
    ...
```

We'll commit all these changes:

```sh
(.venv) my_nd_project$ git add .
(.venv) my_nd_project$ git commit -am "Initial setup, and added django-simple-deploy."
```


Now we'll make an empty project on Fly.io that we can deploy to:

```sh
(.venv) my_nd_project$ fly apps create --generate-name
New app created: nameless-bird-5390
```

We're ready to call `deploy`, which will configure for deployment to Fly:

```sh
(.venv) my_nd_project$ nanodjango manage counter.py deploy
...
Deployment target: Fly.io
  Using plugin: dsd_flyio_nanodjango`
...
--- Your project is now configured for deployment on Fly.io ---
...
```

We can inspect the changes, and commit them:

```sh
(.venv) my_nd_project$ git status
On branch main
Changes not staged for commit:
	modified:   .gitignore
Untracked files:
	.dockerignore
	Dockerfile
	fly.toml
(.venv) my_nd_project$ git add .
(.venv) my_nd_project$ git commit -am "Configured for deployment to Fly."
```

Now we make the actual push to Fly:

```sh
(.venv) my_nd_project$ fly deploy
...
```

Once the push finishes, you can open the deployed version of your project:

```sh
(.venv) my_nd_project$ fly apps open
opening https://nameless-bird-5390.fly.dev/ ...
```

The counter will increment. In the 0.1.0 release of this plugin, the count will jump around because we're using SQLite on an ephemeral machine. Later releases will configure a persistent database.

When you're satisfied it works, make sure to destroy the deployed app if you don't want to accrue charges:

```sh
(.venv) my_nd_project$ fly apps destroy nameless-bird-5390
Destroying an app is not reversible.
? Destroy app nameless-bird-5390? Yes
Destroyed app nameless-bird-5390
```

Fully-automated deployment
---

You can deploy the project in just a few steps using the `--automate-all` flag from `django-simple-deploy`.

Install this plugin:

```sh
$ uv pip install dsd-flyio-nanodjango
 + django-simple-deploy==1.3.0
 + dsd-flyio-nanodjango==0.1.0
 (.venv) my_nd_project$ uv pip freeze > requirements.txt
```

Add `django_simple_deploy` to the project script:

```python
from django.db import models
from nanodjango import Django

app = Django(
    EXTRA_APPS=["django_simple_deploy"],
)

@app.admin
class CountLog(models.Model):
    ...
```

Commit all these changes:

```sh
(.venv) my_nd_project$ git add .
(.venv) my_nd_project$ git commit -am "Initial setup, and added django-simple-deploy."
```

Call `deploy`, with the `--automate-all` flag:

We're ready to call `deploy`, which will configure for deployment to Fly:

```sh
(.venv) my_nd_project$ nanodjango manage counter.py deploy --automate-all
...
Deployment target: Fly.io
  Using plugin: dsd_flyio_nanodjango`
...
--- Your project should now be deployed on Fly.io ---

It should have opened up in a new browser tab. If you see a
  "server not available" message, wait a minute or two and
  refresh the tab. It sometimes takes a few minutes for the
  server to be ready.
- You can also visit your project at https://billowing-leaf-3573.fly.dev/
...
```

When you're satisfied it works, make sure to destroy the deployed app if you don't want to accrue charges:

```sh
(.venv) my_nd_project$ fly apps destroy nameless-bird-5390
Destroying an app is not reversible.
? Destroy app nameless-bird-5390? Yes
Destroyed app nameless-bird-5390
```











