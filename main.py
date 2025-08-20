import requests
from kivy.lang import Builder
from kivy.properties import StringProperty, ListProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem, TwoLineListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout

# Server configuration
SERVER_URL = "http://127.0.0.1:5000"

class Content(MDBoxLayout):
    """Content for the add user dialog"""
    pass

class HomeScreen(Screen):
    status_text = StringProperty("Not connected")
    users = ListProperty([])

    def on_enter(self):
        self.check_connection()

    def check_connection(self):
        try:
            response = requests.get(f"{SERVER_URL}/", timeout=5)
            if response.status_code == 200:
                self.status_text = "Connected to server"
                self.load_users()
            else:
                self.status_text = f"Server error: {response.status_code}"
        except requests.exceptions.RequestException as e:
            self.status_text = f"Connection failed: {str(e)}"

    def load_users(self):
        try:
            response = requests.get(f"{SERVER_URL}/api/users", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.users = data.get('users', [])
                self.update_user_list()
                self.status_text = f"Loaded {len(self.users)} users"
            else:
                self.status_text = f"Failed to load users: {response.status_code}"
        except requests.exceptions.RequestException as e:
            self.status_text = f"Error loading users: {str(e)}"

    def update_user_list(self):
        # Clear existing list items
        user_list = self.ids.user_list
        user_list.clear_widgets()

        # Add users to list
        for user in self.users:
            item = TwoLineListItem(
                text=f"{user['name']}",
                secondary_text=f"Email: {user['email']}",
                on_release=lambda x, u=user: self.show_user_details(u)
            )
            user_list.add_widget(item)

    def show_user_details(self, user):
        dialog = MDDialog(
            title="User Details",
            text=f"ID: {user['id']}\nName: {user['name']}\nEmail: {user['email']}",
            buttons=[
                MDFlatButton(
                    text="DELETE",
                    on_release=lambda x: self.delete_user(user['id'])
                ),
                MDFlatButton(
                    text="CLOSE",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()

    def delete_user(self, user_id):
        try:
            response = requests.delete(f"{SERVER_URL}/api/users/{user_id}")
            if response.status_code == 200:
                self.status_text = "User deleted successfully"
                self.load_users()  # Refresh the list
            else:
                self.status_text = f"Failed to delete user: {response.status_code}"
        except requests.exceptions.RequestException as e:
            self.status_text = f"Error deleting user: {str(e)}"

    def show_add_user_dialog(self):
        self.dialog = MDDialog(
            title="Add New User",
            type="custom",
            content_cls=Content(),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDFlatButton(
                    text="ADD",
                    on_release=self.add_user
                )
            ]
        )
        self.dialog.open()

    def add_user(self, instance):
        content = self.dialog.content_cls
        name = content.ids.name_field.text
        email = content.ids.email_field.text

        if not name or not email:
            self.status_text = "Please fill in all fields"
            return

        try:
            response = requests.post(
                f"{SERVER_URL}/api/users",
                json={"name": name, "email": email},
                timeout=5
            )
            
            if response.status_code == 201:
                self.status_text = "User added successfully"
                self.dialog.dismiss()
                self.load_users()  # Refresh the list
            else:
                self.status_text = f"Failed to add user: {response.status_code}"
        except requests.exceptions.RequestException as e:
            self.status_text = f"Error adding user: {str(e)}"

class UserApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        
        # Create screen manager
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        return sm

    def on_start(self):
        # Set window size for better appearance
        Window.size = (400, 600)

# KV String for the UI
KV = '''
<Content>:
    orientation: "vertical"
    spacing: "12dp"
    size_hint_y: None
    height: "120dp"

    MDTextField:
        id: name_field
        hint_text: "Full Name"
        required: True

    MDTextField:
        id: email_field
        hint_text: "Email Address"
        required: True

<HomeScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '10dp'
        spacing: '10dp'

        MDLabel:
            text: "User Management App"
            halign: 'center'
            font_style: 'H4'
            size_hint_y: None
            height: self.texture_size[1]

        MDLabel:
            text: root.status_text
            halign: 'center'
            theme_text_color: 'Secondary'
            size_hint_y: None
            height: self.texture_size[1]

        ScrollView:
            id: scroll_view
            MDList:
                id: user_list

        MDRaisedButton:
            text: "Refresh Users"
            on_release: root.load_users()
            size_hint_y: None
            height: '48dp'

        MDRaisedButton:
            text: "Add New User"
            on_release: root.show_add_user_dialog()
            size_hint_y: None
            height: '48dp'

        MDRaisedButton:
            text: "Check Connection"
            on_release: root.check_connection()
            size_hint_y: None
            height: '48dp'
'''

if __name__ == '__main__':
    # Load KV string
    Builder.load_string(KV)
    UserApp().run()