from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_job_model():
    """
    Return the Job model that is active in this project.
    """
    try:
        return django_apps.get_model(settings.JOB_MODEL, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured(
            "JOB_MODEL must be of the form 'app_label.model_name'"
        )
    except LookupError:
        raise ImproperlyConfigured(
            "JOB_MODEL refers to model '%s' that has not been installed"
            % settings.JOB_MODEL
        )
