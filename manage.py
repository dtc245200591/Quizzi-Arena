from django.core.management import execute_from_command_line
import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "quizzi.settings")
execute_from_command_line(sys.argv)
