"""
Passenger WSGI file for deployment
Este arquivo é usado pelo Passenger (comum em painéis cPanel/ICP)
"""
import sys
import os

# Adicionar diretório do projeto ao path
INTERP = os.path.join(os.environ['HOME'], 'virtualenv', 'api_svegpa', '3.13', 'bin', 'python')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.insert(0, os.path.dirname(__file__))

from main import app as application
