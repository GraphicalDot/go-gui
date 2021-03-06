#!/usr/bin/env python3
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
import json
from kivy.properties import StringProperty
from kivy.clock import Clock
import time
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from user_registration import UserRegistration
from forgot_password import ForgotPassword
from kivy.storage.jsonstore import JsonStore
import hashlib
import six
import os
import sys
import requests
from SettingsModule.settings import api_server
from SettingsModule import global_variables
#from DecentralizeFileSystem.ipfs_decentralize_filesystem import IPFS
from alert import Alert
from kivy.config import Config
from LoggingModule.logging import logger_log
#https://www.colorcombos.com/color-schemes/192/ColorCombo192.html
from kivy.core.window import Window
from EncryptionModule.symmetric import aes_decrypt, generate_scrypt_key

"""
import coloredlogs, verboselogs, logging
verboselogs.install()
coloredlogs.install()
logger = logging.getLogger(__name__)
"""

store = JsonStore('config.json')

class LoginPage(Screen):
    def do_login(self, passwordText):

            
        app = App.get_running_app()
        print (app.get_application_config())

        

        if  app.password == "":
            Alert(title='Error messege', text='Password cannot be left blank')
            return             

        encrypted = store.get("mnemonic")
        encrypted_mnemonic = encrypted["value"]
        salt = encrypted["salt"]

        
        scrypt_key, salt = generate_scrypt_key(passwordText, bytes.fromhex(salt))
        print (f"scrypt_key from password {scrypt_key.hex()} and salt is {salt.hex()}")

        print (f"Encrypted Mnemonic is {encrypted_mnemonic}")

        try:
            result = aes_decrypt(scrypt_key, bytes.fromhex(encrypted_mnemonic))
        except Exception as e:
            print ("Error ")
            print (e)
            Alert(title='Error messege', text='Password entered is wrong')

        
        store.put("password", value=passwordText)
        print (result)


        ##This iwll check if the vm has runing ipfs connection or not, 
        ##if its running global_variables.ipfs_node_id is not None
    
        """
        try:
            r = requests.post("%slogin"%api_server, data={"username": app.username, "password": app.password, "ipfs_node_id": global_variables.ipfs_node_id})
            global_variables.app_token = r.json()["data"]["token"]

        except Exception as e:
            logger_log.debug(str(e))
            Alert(title='Feynmen error message', text="Remote server id not responding")

        if not r.json()["success"]:
            logger_log.error("The user doesnt exists")
            content = Button(text='Close me!')
            popup = Popup(content=content, auto_dismiss=False)

            # bind the on_press event of the button to the dismiss function
            content.bind(on_press=popup.dismiss)

            # open the popup
            popup.open()
        
            popup.open()
            
        try:
            r.json()["data"]["user"]
        except Exception as e:
            logger_log.debug(e)
            Alert(title='Feynmen error message', text=r.json()["message"])

        global_variables.username = app.username
        global_variables.password = app.password  
        global_variables.user_id = r.json()["data"]["user"]["user_id"]

        _class = IPFS()
        _class.check_filesystem()


        #logger_log.debug("This is the ipfs config file present on the node %s"%global_variables.ipfs_config)
        #logger_log.debug("This is the ipfs config file deleivered from the central server %s"%r.json()["data"]["user"]["ipfs_config"])


        


        if not r.json()["data"]["user"]["ipfs_config"]: #first time user
            _class.new_user()
        else:
            _class.repeated_user(r.json()["data"]["user"])

        ##Now we will get all the files that were stored by this user
        r = requests.get("http://localhost:8888/storage", params={"user_id": global_variables.user_id})    
        
        self.manager.add_widget(UserPage(name='User'))
        

        logger_log.debug(r.json()["data"])
        self.manager.get_screen('User').data = r.json()["data"]

        self.manager.get_screen('User').encryption_public_key = global_variables.encryption_public_key
        self.manager.get_screen('User').ipfs_node_id = global_variables.ipfs_node_id
        self.manager.get_screen('User').passphrase = global_variables.passphrase


 

        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = 'User'
        """


    def do_registration(self):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = 'UserRegistration'    



    def resetForm(self):
        self.ids['password'].text = ""


class MainApp(App):
    password = StringProperty(None)
    
    def build(self, **kwargs):
    
        super(MainApp, self).__init__(**kwargs)
        manager = ScreenManager()
        manager.add_widget(UserRegistration(name='UserRegistration'))
        manager.add_widget(ForgotPassword(name='ForgotPassword'))
        manager.add_widget(LoginPage(name='Login'))

        self.title = "Decentralize computation framework"

        try:
            store.get("mnemonic")
        except:
            #manager.transition = SlideTransition(direction="left")
            manager.current = 'UserRegistration'

        
        return manager
  
    def on_start(self):
        print ('App: I\'m alive!')
 
    def on_stop(self):
        print('App: Aaaargh I\'m dying!')


from kivy import utils


def main():

    Config.set('graphics', 'width', '1000')
    Config.set('graphics', 'height', '600')
    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
    Config.write()
    Window.borderless = False
    Window.clearcolor = utils.rgba("#1E1F26")
    app = MainApp()
    app.run()


if __name__ == "__main__":
    #logger_logger.debug("This is the password text %s"%"passwordText")
    #logger_logger.info("This is the password text %s"%"passwordText")
    #logger_logger.error("This is the password text %s"%"passwordText")
    #logger_logger.warning("This is the password text %s"%"passwordText")
    main()    


