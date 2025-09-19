import os

if os.environ.get('IS_LAN', 'false') != 'true':
    from bomiot.cmd.cmd import cmd