import socket
import threading
import pickle
import time

FORMAT = "UTF-8"
PORT = 5050
HEADER = 64
SERVER = "192.168.1.34"
#SERVER = "85.108.195.254"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def Networking():
    client.connect(ADDR)

    while True:
        msglen = client.recv(HEADER).decode(FORMAT)
        if msglen:
            msglen = int(msglen)
            message = client.recv(msglen)

            global incoming_data
            incoming_data = pickle.loads(message)
        
        for team in incoming_data:
            for item in list_items:
                if(item.text == team):
                    item.secondary_text = incoming_data[team][0]
                    if(incoming_data[team][0] == "Waiting For Input"):
                        item.secondary_text_color = (1, 0, 0, 0.5)
                    elif(incoming_data[team][0] == "Writing"):
                        item.secondary_text_color = (1, 0.58, 0, 0.5)
                    elif(incoming_data[team][0] == "Saved"):
                        item.secondary_text_color = (0, 0.58, 0, 0.5)

        for team in incoming_data:
            try:
                tooltips[team].tooltip_text = incoming_data[team][2]
            except: pass
                
                

from kivymd.app import MDApp
from kivymd.uix.screen import Screen
from kivymd.uix.button import MDRectangleFlatButton

from kivy.lang import Builder
from kivymd.uix.list import TwoLineAvatarIconListItem, IconLeftWidget

from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.snackbar import Snackbar
from kivy.properties import StringProperty
from kivymd.uix.list import IconRightWidget

from kivymd.uix.button import MDIconButton, MDTooltip

class TooltipMDIconButton(MDIconButton, MDTooltip):
    pass

class TeamsPage(Screen):
    pass

class FormPage(Screen):
    pass

class LoginPage(Screen):
    pass

class PageManager(ScreenManager):
    pass


KV = '''
PageManager:
    LoginPage:
    TeamsPage:
    FormPage:

<LoginPage>
    name: "login"

    FloatLayout:
        MDTextField:
            id: username
            hint_text: "Enter Username"
            pos_hint: {"center_x":0.5, "center_y":0.6}
            size_hint: (0.7, None)

        MDRectangleFlatButton:
            text: "Connect"
            pos_hint: {"center_x":0.5, "center_y":0.4}
            on_release: app.ConstructTeamsList()
    

<TeamsPage>:
    name: "teams"

    BoxLayout:
        orientation: "vertical"

        MDToolbar:
            title: "Teams"

        ScrollView:
            MDList:
                id: container
    
<FormPage>:
    name: "form"

    BoxLayout:
        orientation: "vertical"

        MDToolbar:
            title: "Form"
            left_action_items: [["keyboard-backspace", lambda x: app.GoBack()]]

        ScrollView:
            MDList:
                id: container

                OneLineAvatarIconListItem:
                    text: "Ball Throw"

                    IconLeftWidget:
                        icon: "plus"

                    IconRightWidget:
                        icon: "remove_icon.png"
                        MDCheckbox:
                            id: ball_state

                OneLineAvatarIconListItem:
                    text: "Wheel Spin"

                    IconLeftWidget:
                        icon: "plus"

                    IconRightWidget:
                        icon: "remove_icon.png"
                        MDCheckbox:
                            id: wheel_state

                OneLineAvatarIconListItem:
                    text: "Climbing"

                    IconLeftWidget:
                        icon: "plus"

                    IconRightWidget:
                        icon: "remove_icon.png"
                        MDCheckbox:
                            id: climb_state
                    
    MDFloatingActionButton:
        icon: "check"
        md_bg_color: app.theme_cls.primary_color
        pos_hint: {'x': 0.8, 'y': 0.05}

        on_release:
            app.SaveForm()

'''

list_items = []
tooltips = {}

class DemoApp(MDApp):
    global currently_editing
    currently_editing = "Team 0"

    global USERNAME
    USERNAME = ''

    def build(self):
        return Builder.load_string(KV)

    def SendUpdate(self, state, entry): 
        # "entry" defines entry type. Possible values are "sta" stands for state, "val" stands for value and "und" for undefined.
        if(entry == "sta"):
            outgoing_data = {
                self.currently_editing: [
                    state,
                    entry,
                ]
            }
        elif(entry == "val"):
            outgoing_data = {
                self.currently_editing: [
                    state,
                    entry,
                    self.USERNAME,
                    self.root.current_screen.ids.ball_state.active,
                    self.root.current_screen.ids.wheel_state.active,
                    self.root.current_screen.ids.climb_state.active
                ]
            }

        msg = pickle.dumps(outgoing_data)
        client.send(msg)

    def GoBack(self):
        if(incoming_data[self.currently_editing][0] != "Saved"):
            self.SendUpdate("Waiting For Input", "sta")
        self.root.current = "teams"
        self.root.transition.direction = "right"

    def ListItemPressed(self, item):
        self.currently_editing = item.text
        if(incoming_data[self.currently_editing][0] == "Waiting For Input" or incoming_data[self.currently_editing][0] == "Saved"):
            self.root.current = "form"
            self.root.transition.direction = "left"

            if(incoming_data[self.currently_editing][0] == "Waiting For Input"):
                self.SendUpdate("Writing", "sta")

        if(incoming_data[self.currently_editing][0] == "Waiting For Input"):
            self.root.current_screen.ids.ball_state.active = False
            self.root.current_screen.ids.wheel_state.active = False
            self.root.current_screen.ids.climb_state.active = False
        elif(incoming_data[self.currently_editing][0] == "Saved"):
            self.root.current_screen.ids.ball_state.active = incoming_data[self.currently_editing][3]
            self.root.current_screen.ids.wheel_state.active = incoming_data[self.currently_editing][4]
            self.root.current_screen.ids.climb_state.active = incoming_data[self.currently_editing][5]

    def SaveForm(self):
        if(incoming_data[self.currently_editing][0] != "Saved"): 
            self.SendUpdate("Saved", "val")
            self.root.current = "teams"
            self.root.transition.direction = "right"

    def ConstructTeamsList(self):
        self.USERNAME = self.root.current_screen.ids.username.text
        self.root.current = "teams"
        self.root.transition.direction = "left"

        network = threading.Thread(target=Networking)
        network.start()
        time.sleep(2)

        if incoming_data:
            for team_name in incoming_data:
                button = IconRightWidget(icon="remove_icon.png")
                info = TooltipMDIconButton(icon="information", tooltip_text=incoming_data[team_name][2], pos_hint={"center_x": .5, "center_y": .5})
                button.add_widget(info)

                item = TwoLineAvatarIconListItem(text=team_name, secondary_text=incoming_data[team_name][0], secondary_theme_text_color='Custom', secondary_text_color=(1,0,0,0.6), on_release=self.ListItemPressed)
                item.add_widget(button)

                tooltips[team_name] = info 

                self.root.current_screen.ids.container.add_widget(item)
                list_items.append(item)

            

    def on_start(self):
        pass
        
DemoApp().run()




