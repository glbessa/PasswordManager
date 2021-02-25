from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button

class Gerenciador(ScreenManager):
	pass

class Acesso(Screen):
	pass

class Menu(Screen):
	pass

class main(App):
	def build(self):
		return Gerenciador()

main().run()