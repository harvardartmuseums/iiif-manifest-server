#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "metadata_server.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
