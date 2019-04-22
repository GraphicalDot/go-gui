# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.image import Image
import pickle
import time
from kivymd.bottomsheet import MDListBottomSheet, MDGridBottomSheet
from kivymd.button import MDIconButton
from kivymd.date_picker import MDDatePicker
from kivymd.dialog import MDDialog
from kivymd.label import MDLabel
from kivymd.list import ILeftBody, ILeftBodyTouch, IRightBodyTouch, BaseListItem
from kivymd.material_resources import DEVICE_TYPE
from kivymd.navigationdrawer import MDNavigationDrawer, NavigationDrawerHeaderBase
from kivymd.selectioncontrols import MDCheckbox
from kivymd.snackbar import Snackbar
from kivymd.theming import ThemeManager
from kivymd.time_picker import MDTimePicker
import requests
import hashlib
from kivy.storage.jsonstore import JsonStore
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.factory import Factory
from EncryptionModule.symmetric import generate_scrypt_key, aes_encrypt, aes_decrypt
from instagram_api import instagram_login, get_all_posts, save_instagram,  get_instagram_thumbnails, INSTAGRAM_DIR
from kivy.properties import ObjectProperty, ListProperty, StringProperty
from kivy.logger import Logger
from kivy.uix.image import AsyncImage
from kivymd.list import TwoLineAvatarIconListItem
from kivymd.selectioncontrols import MDCheckbox
from kivy.clock import Clock
import database_calls
import datetime
import time
import sys




#store = JsonStore('config.json')






# class HackedDemoNavDrawer(MDNavigationDrawer):
#     # DO NOT USE
#     def add_widget(self, widget, index=0):
#         if issubclass(widget.__class__, BaseListItem):
#             self._list.add_widget(widget, index)
#             if len(self._list.children) == 1:
#                 widget._active = True
#                 self.active_item = widget
#             # widget.bind(on_release=lambda x: self.panel.toggle_state())
#             widget.bind(on_release=lambda x: x._set_active(True, list=self))
#         elif issubclass(widget.__class__, NavigationDrawerHeaderBase):
#             self._header_container.add_widget(widget)
#         else:
#             super(MDNavigationDrawer, self).add_widget(widget, index)



class ContactPhoto(ILeftBody, AsyncImage):
        pass

class MessageButton(IRightBodyTouch, MDCheckbox):
    #phone_number = StringProperty()
    id = StringProperty()
    def on_release(self):
        # sample code:
        #Dialer.send_sms(phone_number, "Hey! What's up?")
        return 

class MainApp(App):
    theme_cls = ThemeManager()
    previous_date = ObjectProperty()
    title = "Decentralize oil field"
    mnemonic = StringProperty()
    address = StringProperty()    
    passphrase = StringProperty()    
    repeat_passphrase = StringProperty()    
    enabled_mnemonic = BooleanProperty(True)
    enabled_address = BooleanProperty(True)
    instagram_last_fetched = StringProperty()

    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)
        #Window.bind(on_close=self.on_stop)

    def stop(self, *largs):
        # Open the popup you want to open and declare callback if user pressed `Yes`
        # popup = ExitPopup(title=TEXT_ON_CLOSE_APPLICATION,
        #                   content=Button(text=TEXT_ON_CLOSE_APPLICATION_BUTTON_CLOSE),
        #                   size=(400, 400), size_hint=(None, None)
        #                   )
        # popup.bind(on_confirm=partial(self.close_app, *largs))
        # popup.open()
        return 

    def build(self):
        print ("App done")
        if getattr(sys, 'frozen', False):
            # frozen
            dir_ = os.path.dirname(sys.executable)
        else:
            # unfrozen
            dir_ = os.getcwd()
        self.main_widget =Builder.load_file(
            os.path.join(dir_, "./latest.kv")
        )
        self.theme_cls.theme_style = 'Light'

        # self.theme_cls.theme_style = 'Dark'

        # self.main_widget.ids.text_field_error.bind(
        #     on_text_validate=self.set_error_message,
        #     on_focus=self.set_error_message)
        
        """
        if database_calls.get("instagram"):
            self.update_instagram_images_list()
        self.bottom_navigation_remove_mobile(self.main_widget)
        """
        #__list = Factory.Lists()
        print ("App done")
        return self.main_widget



    def on_start(self):
        print ("App Start")
        if not os.path.join(os.getcwd(),  INSTAGRAM_DIR):
            Logger.warning("%s doesnt exists, Creating one"%INSTAGRAM_DIR)
            os.mkdir(INSTAGRAM_DIR)
        else:
            #Logger.warning("%s exists at {os.path.join(os.getcwd(),  INSTAGRAM_DIR)}")
            pass


        password_found = database_calls.get("password")
        print ("App Check one")
        
        #Logger.info(f"This is the password i found {password_found}")
        if password_found:
            Logger.info("Password found")
            self.main_widget.ids.login_grid_layout.remove_widget(self.main_widget.ids.button_login)
            self.main_widget.ids.login_box.remove_widget(self.main_widget.ids.passphrase)
            #self.main_widget.ids.login_box.add_widget(self.main_widget.ids.mnemonic)
            time.sleep(0.1)
            
            self.decrypt_mnemonic(password_found)

        else:
            self.main_widget.ids.login_grid_layout.remove_widget(self.main_widget.ids.button_logout)

        print ("App Check Two")

        if database_calls.get("mnemonic"):
            self.main_widget.ids.login_grid_layout.remove_widget(self.main_widget.ids.button_mnemonic)
            self.main_widget.ids.login_grid_layout.remove_widget(self.main_widget.ids.button_save_mnemonic)
            self.main_widget.ids.login_grid_layout.remove_widget(self.main_widget.ids.button_show_mnemonic)
            #self.main_widget.ids.login_box.remove_widget(self.main_widget.ids.address)
            self.main_widget.ids.login_box.remove_widget(self.main_widget.ids.repeat_passphrase)

            #self.main_widget.ids.login_box.remove_widget(self.main_widget.ids.mnemonic)
            

            address = database_calls.get("address")
            #Logger.info(f"YOur address on the blockchain is {address}")
            self.address = str(address)
            #self.main_widget.ids.login_box.add_widget(self.main_widget.ids.repeat_passphrase)
        else:
            self.main_widget.ids.login_box.remove_widget(self.main_widget.ids.button_login)

        return 

    def update_instagram_images_list(self):
        thumbnails = get_instagram_thumbnails()
        for image in thumbnails:

            item = TwoLineAvatarIconListItem(
            text="Top Liker [%s]"%image['top_likers'][0],
            secondary_text="Total likes %s"%image['likes'])
            item.add_widget(ContactPhoto(source =image["disk_name"]))
            item.add_widget(MessageButton(id=image["id"]))
            self.main_widget.ids.scroll.add_widget(item)

            # new_widget = Factory.ThreeLineAvatarIconListItemCheckbox(
            #         text=f'id-{image["id"]}')
            # new_widget.add_widget(AvatarSampleWidget(source=image["disk_name"]))



        self.instagram_last_fetched = "Last Fetched from Instagram " + self.instagram_last()
        return 



    def bottom_navigation_remove_mobile(self, widget):
        # Removes some items from bottom-navigation demo when on mobile
        if DEVICE_TYPE == 'mobile':
            widget.ids.bottom_navigation_demo.remove_widget(widget.ids.bottom_navigation_desktop_2)
        if DEVICE_TYPE == 'mobile' or DEVICE_TYPE == 'tablet':
            widget.ids.bottom_navigation_demo.remove_widget(widget.ids.bottom_navigation_desktop_1)

    def show_example_snackbar(self, snack_type):
        if snack_type == 'simple':
            Snackbar(text="This is a snackbar!").show()
        elif snack_type == 'button':
            Snackbar(text="This is a snackbar", button_text="with a button!", button_callback=lambda *args: 2).show()
        elif snack_type == 'verylong':
            Snackbar(text="This is a very very very very very very very long snackbar!").show()

    def show_example_dialog(self):
        content = MDLabel(font_style='Body1',
                          theme_text_color='Secondary',
                          text="This is a dialog with a title and some text. "
                               "That's pretty awesome right!",
                          size_hint_y=None,
                          valign='top')
        content.bind(texture_size=content.setter('size'))
        self.dialog = MDDialog(title="This is a test dialog",
                               content=content,
                               size_hint=(.8, None),
                               height=dp(200),
                               auto_dismiss=False)

        self.dialog.add_action_button("Dismiss",
                                      action=lambda *x: self.dialog.dismiss())
        self.dialog.open()

    def loading_box(self):
        content = MDLabel(font_style='Body1',
                          theme_text_color='Primary',
                          text="Please wait while we are fetching your instagram, Hang tight!!!",
                          size_hint_y=None,
                          valign='top')
        content.bind(texture_size=content.setter('size'))
        self.dialog = MDDialog(title="This is a long test dialog",
                               content=content,
                               size_hint=(.8, None),
                               height=dp(200),
                               auto_dismiss=True)

        # self.dialog.add_action_button("Dismiss",
        #                               action=lambda *x: self.dialog.dismiss())
        self.dialog.open()
        return 

    def short_dialog_box(self, text):
        content = MDLabel(font_style='Body1',
                          theme_text_color='Secondary',
                          text=text,
                          size_hint_y=None,
                          valign='top')
        content.bind(texture_size=content.setter('size'))
        self.dialog = MDDialog(title="Error box",
                               content=content,
                               size_hint=(.8, None),
                               height=dp(200),
                               auto_dismiss=False)

        self.dialog.add_action_button("Dismiss",
                                      action=lambda *x: self.dialog.dismiss())
        self.dialog.open()


    def get_time_picker_data(self, instance, time):
        self.root.ids.time_picker_label.text = str(time)
        self.previous_time = time

    def show_example_time_picker(self):
        self.time_dialog = MDTimePicker()
        self.time_dialog.bind(time=self.get_time_picker_data)
        if self.root.ids.time_picker_use_previous_time.active:
            try:
                self.time_dialog.set_time(self.previous_time)
            except AttributeError:
                pass
        self.time_dialog.open()

    def set_previous_date(self, date_obj):
        self.previous_date = date_obj
        self.root.ids.date_picker_label.text = str(date_obj)

    def show_example_date_picker(self):
        if self.root.ids.date_picker_use_previous_date.active:
            pd = self.previous_date
            try:
                MDDatePicker(self.set_previous_date,
                             pd.year, pd.month, pd.day).open()
            except AttributeError:
                MDDatePicker(self.set_previous_date).open()
        else:
            MDDatePicker(self.set_previous_date).open()

    def show_example_bottom_sheet(self):
        bs = MDListBottomSheet()
        bs.add_item("Here's an item with text only", lambda x: x)
        bs.add_item("Here's an item with an icon", lambda x: x,
                    icon='clipboard-account')
        bs.add_item("Here's another!", lambda x: x, icon='nfc')
        bs.open()

    def show_example_grid_bottom_sheet(self):
        bs = MDGridBottomSheet()
        bs.add_item("Facebook", lambda x: x,
                    icon_src='./assets/facebook-box.png')
        bs.add_item("YouTube", lambda x: x,
                    icon_src='./assets/youtube-play.png')
        bs.add_item("Twitter", lambda x: x,
                    icon_src='./assets/twitter.png')
        bs.add_item("Da Cloud", lambda x: x,
                    icon_src='./assets/cloud-upload.png')
        bs.add_item("Camera", lambda x: x,
                    icon_src='./assets/camera.png')
        bs.open()

    def set_error_message(self, *args):
        if len(self.root.ids.text_field_error.text) == 2:
            self.root.ids.text_field_error.error = True
        else:
            self.root.ids.text_field_error.error = False

    def on_close(self):
        print ("Clicked on closing application")
        Window.close()
        return True




    def on_instagram_login(self, username, password):
        try:
            #Logger.info(f"Instagram username is {username.text}")
            #Logger.info(f"Instagram password is {password.text}")
            instagram_object = instagram_login(username.text, password.text)
            #self.loading_box()
            #Snackbar(text="Please wait for sometime, lets us fetch your Insta Handle").show()

            max_id, posts = get_all_posts(instagram_object)

            
            Logger.info("Now fetching images from instagram")
            save_instagram(posts)
            # with open("instagram.data","wb") as f:
            #     pickle.dump(posts, f)
            database_calls.insert("instagram_max_id", max_id)
            database_calls.insert("instagram_last_fetch_utc", datetime.datetime.utcnow().timestamp())
            database_calls.insert("instagram_last_fetch_local", datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat())

        except Exception as e:
            Logger.error(e)
            Snackbar(text="Please check your instragram username and password again").show()
        return
        
    def instagram_last(self):
            try:
                data = database_calls.get("instagram_last_fetch_utc")
                #Logger.info(f"Instagram data stored in local storage {data}")
                #Logger.info(f"Instagram Last fectehd locally is {data}")

                result = datetime.datetime.fromtimestamp(data).strftime("%d %B, %Y")
                #Logger.info(f"Human readable last fecthed {result}")
                return result
            except Exception as e:
                #Logger.info(f"Error in lest fecthed dtiem stamp UTC {e.__str__()}")
                return ""




    def on_show_mnemonic(self):
        """
        Show mnemonic after fetching it from local storage 
        """
        self.main_widget.ids.login_box.add_widget(self.main_widget.ids.mnemonic)


    def on_logout(self):
        """
        When a user clicks on the logout button on the login page
        """
        Logger.info("Logout button has been clicked")
        database_calls.delete("password")
        self.main_widget.ids.login_grid_layout.add_widget(self.main_widget.ids.button_login)
        self.main_widget.ids.login_box.add_widget(self.main_widget.ids.passphrase)
        self.password = None
        self.main_widget.ids.login_grid_layout.remove_widget(self.main_widget.ids.button_logout)
        self.main_widget.ids.login_box.remove_widget(self.main_widget.ids.mnemonic)

        return 

    def decrypt_mnemonic(self, password):
        encrypted_mnemonic = database_calls.get("mnemonic")
        #Logger.info(f"Encrypted Mnemonic is {encrypted_mnemonic}")
        salt = database_calls.get("password_salt")
        #Logger.info(f"Password salt is {salt}")

        
        scrypt_key, salt = generate_scrypt_key(password, bytes.fromhex(salt))
        time.sleep(0.1)

        #Logger.info(f"scrypt_key from password {scrypt_key.hex()} and salt is {salt.hex()}")


        try:
            mnemonic = aes_decrypt(scrypt_key, bytes.fromhex(encrypted_mnemonic))
            #Logger.info(f"State of Mnemonic widget {self.main_widget.ids.mnemonic}")
            if not self.main_widget.ids.mnemonic:
                self.main_widget.ids.login_box.add_widget(self.main_widget.ids.mnemonic)
            self.mnemonic = mnemonic.decode()           

        except Exception as e:
            self.short_dialog_box("Passphrase you entered is incorrect, Please try with correct password")
            Logger.error(e)
            return False
        return True



    def on_login(self, passphrase):
        """
        When a user clicks on the login button on the login page
        """
        self.decrypt_mnemonic(passphrase.text)
        time.sleep(0.1)
        Snackbar(text="Login is successful").show()
        database_calls.insert("password", passphrase.text, db_instance=None)

        ##remove login button from the gridlayout on the login page
        self.main_widget.ids.login_grid_layout.remove_widget(self.main_widget.ids.button_login)

        ##remove passphrase text box from the gridlayout on the login page
        self.main_widget.ids.login_box.remove_widget(self.main_widget.ids.passphrase)
        
        ##add logout button on the logn page once login is successful
        self.main_widget.ids.login_grid_layout.add_widget(self.main_widget.ids.button_logout)

        return 

    def on_save_mnemonic(self, passphrase, repeat_passphrase):
        if not self.mnemonic:
            Snackbar(text="PLease generate a New mnemonic").show()
            return 
        if passphrase.text != repeat_passphrase.text or not passphrase.text:
            Snackbar(text="Passphrases must match").show()
            return  

        if len(passphrase.text) <  8:
            Snackbar(text="Passphrases must be at least 8 characters long").show()
            return  


        scrypt_key, salt = generate_scrypt_key(passphrase.text)
        encrypted_mnemonic = aes_encrypt(scrypt_key, self.mnemonic)

        database_calls.insert("mnemonic", encrypted_mnemonic.hex(), db_instance=None)
        database_calls.insert("password_salt", salt.hex(), db_instance=None)
        database_calls.insert("address", self.address, db_instance=None)
        return

    def generate_mnemonic(self):
        """
        Make an api request with the data to confirm the user registraion
        After succesful registration reset the form 
        """
        #TODO form validation with cerberus
        #TODO Check if macid is available from the host or not
        #TODO check if ip address

        r = requests.get("http://%s/get_mnemonic"%store.get('GO_API'))
        mnemonic = r.json()["data"]["mnemonic"]
        zeroth_private_key = r.json()["data"]["zeroth_private_key"]
        zeroth_public_key = r.json()["data"]["zeroth_public_key"]

        master_private_key = r.json()["data"]["master_private_key"]
        master_public_key = r.json()["data"]["master_public_key"]

        self.mnemonic = mnemonic 
        self.address = hashlib.sha256(zeroth_public_key.encode()).hexdigest()
        return 





class IconLeftSampleWidget(ILeftBodyTouch, MDIconButton):
    pass


class IconRightSampleWidget(IRightBodyTouch, MDCheckbox):
    pass

def main():

    Config.set('graphics', 'width', '1000')
    Config.set('graphics', 'height', '600')
    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
    Config.write()
    Window.borderless = True
    #Window.clearcolor = utils.rgba("#1E1F26")
    app = MainApp()
    app.run()


if __name__ == "__main__":
    #logger_logger.debug("This is the password text %s"%"passwordText")
    #logger_logger.info("This is the password text %s"%"passwordText")
    #logger_logger.error("This is the password text %s"%"passwordText")
    #logger_logger.warning("This is the password text %s"%"passwordText")
    from kivy.config import Config
    import os
    from kivy.core.window import Window
    main() 

