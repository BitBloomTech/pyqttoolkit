"""
http://code.activestate.com/recipes/511443-cross-platform-startfile-and-mailto-functions/
"""
import os

class EmailService:
    def send_mail(self, address, subject, body, attachements=None):
        mailto_string = f'mailto:{address}?subject={subject}&body={body[:2000]}'
        os.startfile(mailto_string)
