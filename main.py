from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

import json
import os
import threading

class ChatBubble(Label):
    def __init__(self, text, is_user=False, **kwargs):
        super(ChatBubble, self).__init__(**kwargs)
        self.text = text
        self.is_user = is_user
        self.size_hint_y = None
        self.bind(texture_size=self.setter('size'))
        self.padding = [15, 15, 15, 15]
        self.markup = True
        
        if is_user:
            self.background_color = get_color_from_hex('#4CAF50')
            self.color = get_color_from_hex('#FFFFFF')
            self.halign = 'right'
        else:
            self.background_color = get_color_from_hex('#E0E0E0')
            self.color = get_color_from_hex('#333333')
            self.halign = 'left'

class PersonaSelector(DropDown):
    def __init__(self, persona_manager, **kwargs):
        super(PersonaSelector, self).__init__(**kwargs)
        self.persona_manager = persona_manager
        self.update_personas()
    
    def update_personas(self):
        self.clear_widgets()
        personas = self.persona_manager.list_personas()
        if not personas:
            btn = Button(text='暂无人格', size_hint_y=None, height=44)
            btn.disabled = True
            self.add_widget(btn)
        else:
            for persona in personas:
                btn = Button(
                    text=persona.name, 
                    size_hint_y=None, 
                    height=44,
                    on_release=lambda btn, p=persona: self.select(p.persona_id)
                )
                self.add_widget(btn)

class MobilePersona:
    def __init__(self, persona_id, name, description=""):
        self.persona_id = persona_id
        self.name = name
        self.description = description
        self.traits = {}
    
    def add_trait(self, trait, value):
        self.traits[trait] = min(1.0, max(0.0, value))
    
    def to_dict(self):
        return {
            "persona_id": self.persona_id,
            "name": self.name,
            "description": self.description,
            "traits": self.traits
        }
    
    @classmethod
    def from_dict(cls, data):
        p = cls(data["persona_id"], data["name"], data.get("description", ""))
        p.traits = data.get("traits", {})
        return p

class PersonaManager:
    def __init__(self):
        self.storage_path = os.path.expanduser('~/.aipeiban/personas')
        os.makedirs(self.storage_path, exist_ok=True)
    
    def create_persona(self, name, description=""):
        persona_id = name.lower().replace(" ", "_")
        persona = MobilePersona(persona_id, name, description)
        self._save(persona)
        return persona
    
    def load_persona(self, persona_id):
        path = os.path.join(self.storage_path, f"{persona_id}.json")
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return MobilePersona.from_dict(json.load(f))
        return None
    
    def _save(self, persona):
        path = os.path.join(self.storage_path, f"{persona.persona_id}.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(persona.to_dict(), f, ensure_ascii=False, indent=2)
    
    def list_personas(self):
        personas = []
        for f in os.listdir(self.storage_path):
            if f.endswith('.json'):
                p = self.load_persona(f[:-5])
                if p:
                    personas.append(p)
        return personas

class MockChatEngine:
    def chat(self, persona_name, persona_desc, traits, message):
        responses = [
            f"你好啊，我是{persona_name}。{persona_desc}",
            "听到你这么说，我很开心",
            "谢谢你愿意和我聊天",
            "我也很想念你",
            "要多保重身体哦",
            "记得按时吃饭休息",
            "有什么想聊的都可以跟我说",
            "天气冷了，记得添衣服",
            "你今天过得怎么样？",
            "慢慢来，一切都会好起来的"
        ]
        import random
        return random.choice(responses)

class AICompanionApp(App):
    def build(self):
        Window.clearcolor = get_color_from_hex('#F5F5F5')
        self.persona_manager = PersonaManager()
        self.chat_engine = MockChatEngine()
        self.current_persona = None
        self.chat_history = []
        
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        top_bar = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        self.persona_btn = Button(
            text='选择人格',
            size_hint=(0.4, 1),
            background_color=get_color_from_hex('#2196F3'),
            color=get_color_from_hex('#FFFFFF')
        )
        self.persona_dropdown = PersonaSelector(self.persona_manager)
        self.persona_btn.bind(on_release=self.persona_dropdown.open)
        self.persona_dropdown.bind(on_select=self.on_persona_selected)
        
        new_persona_btn = Button(
            text='+ 新建',
            size_hint=(0.2, 1),
            background_color=get_color_from_hex('#FF9800'),
            color=get_color_from_hex('#FFFFFF')
        )
        new_persona_btn.bind(on_release=self.show_new_persona_popup)
        
        top_bar.add_widget(self.persona_btn)
        top_bar.add_widget(new_persona_btn)
        
        self.chat_scroll = ScrollView(size_hint=(1, 0.8))
        self.chat_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.chat_scroll.add_widget(self.chat_layout)
        
        input_layout = BoxLayout(size_hint_y=None, height=60, spacing=10)
        self.message_input = TextInput(
            hint_text='输入你想说的话...',
            size_hint=(0.8, 1),
            multiline=False
        )
        send_btn = Button(
            text='发送',
            size_hint=(0.2, 1),
            background_color=get_color_from_hex('#4CAF50'),
            color=get_color_from_hex('#FFFFFF')
        )
        send_btn.bind(on_release=self.send_message)
        self.message_input.bind(on_text_validate=self.send_message)
        
        input_layout.add_widget(self.message_input)
        input_layout.add_widget(send_btn)
        
        main_layout.add_widget(top_bar)
        main_layout.add_widget(self.chat_scroll)
        main_layout.add_widget(input_layout)
        
        self.add_initial_message()
        
        return main_layout
    
    def add_initial_message(self):
        welcome_label = Label(
            text='💝 AI陪伴 - 与思念的人温暖对话\n\n请先选择或创建一个人格开始对话',
            size_hint_y=None,
            height=100,
            color=get_color_from_hex('#666666'),
            halign='center'
        )
        self.chat_layout.add_widget(welcome_label)
    
    def on_persona_selected(self, instance, persona_id):
        self.current_persona = self.persona_manager.load_persona(persona_id)
        if self.current_persona:
            self.persona_btn.text = self.current_persona.name
            self.clear_chat()
            self.add_message(f"你好，我是{self.current_persona.name}。{self.current_persona.description}", is_user=False)
    
    def show_new_persona_popup(self, instance):
        content = GridLayout(cols=1, spacing=10, padding=20)
        name_input = TextInput(hint_text='人格名称')
        desc_input = TextInput(hint_text='描述（可选）', multiline=True, height=80)
        
        def create_persona(instance):
            if name_input.text.strip():
                self.persona_manager.create_persona(name_input.text.strip(), desc_input.text.strip())
                self.persona_dropdown.update_personas()
                popup.dismiss()
        
        create_btn = Button(text='创建', background_color=get_color_from_hex('#4CAF50'), color=get_color_from_hex('#FFFFFF'))
        create_btn.bind(on_release=create_persona)
        
        content.add_widget(Label(text='创建新人格'))
        content.add_widget(name_input)
        content.add_widget(desc_input)
        content.add_widget(create_btn)
        
        popup = Popup(title='新建人格', content=content, size_hint=(0.8, 0.6))
        popup.open()
    
    def send_message(self, instance):
        message = self.message_input.text.strip()
        if not message or not self.current_persona:
            return
        
        self.add_message(message, is_user=True)
        self.message_input.text = ''
        
        def generate_response():
            response = self.chat_engine.chat(
                self.current_persona.name,
                self.current_persona.description,
                self.current_persona.traits,
                message
            )
            Clock.schedule_once(lambda dt: self.add_message(response, is_user=False), 0)
        
        threading.Thread(target=generate_response, daemon=True).start()
    
    def add_message(self, text, is_user=False):
        bubble = ChatBubble(text, is_user=is_user)
        self.chat_layout.add_widget(bubble)
        Clock.schedule_once(lambda dt: self.scroll_to_bottom(), 0.1)
    
    def clear_chat(self):
        self.chat_layout.clear_widgets()
    
    def scroll_to_bottom(self):
        self.chat_scroll.scroll_y = 0

if __name__ == '__main__':
    AICompanionApp().run()