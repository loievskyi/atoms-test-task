import os
import sys
import django

PROJECT_NAME = "braincomua_project"
file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(file_dir, "..", PROJECT_NAME)))

os.environ["DJANGO_SETTINGS_MODULE"] = f"{PROJECT_NAME}.settings"

django.setup()
