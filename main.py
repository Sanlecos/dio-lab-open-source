from kivymd.app import MDApp
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.clock import Clock

from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.tab import MDTabsBase, MDTabs
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import OneLineListItem
from kivy.uix.anchorlayout import AnchorLayout

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re

# --- Estilos ---
COLOR_BG = "#e6f2e6"
COLOR_BTN = "#4caf50"

# --- Google Sheets ---
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "proposta-466714-795c452fd856.json", scope
)
client = gspread.authorize(creds)
spreadsheet = client.open_by_key("1mlqHUKuy9dWHY6Pa7IZsOOIG2gghz3nz6NvGac7V0qg")

# --- Campos globais ---
campos = {}
dropdowns = {}


def show_dialog(title, text):
    MDDialog(title=title, text=text, size_hint=(0.8, None), height=dp(200)).open()


def salvar_formulario(instance):
    try:
        dados_pessoais = [
            campos["nome"].text,
            campos["data_nascimento"].text,
            campos["nacionalidade"].text,
            campos["naturalidade"].text,
            campos["endereco"].text,
            campos["bairro"].text,
            campos["cidade"].text,
            campos["cep"].text,
            campos["telefone"].text,
            campos["identidade"].text,
            campos["cpf"].text,
            campos["estado_civil"].text,
            campos["pai"].text,
            campos["mae"].text,
            campos["data_admissao"].text,
        ]

        dados_respostas = [
            campos["nome"].text,
            campos["motivo"].text,
            campos["opiniao"].text,
            campos["objetivo"].text,
            campos["espirita"].text,
            campos["bom_espirita"].text,
            campos["porque"].text,
            campos["indicacao"].text,
        ]

        dados_espirituais = [
            campos["nome"].text,
            campos["funcao"].text,
            campos["cargo"].text,
            campos["padrinho"].text,
            campos["madrinha"].text,
            campos["pai_orixa"].text,
            campos["mae_orixa"].text,
            campos["caboclo"].text,
            campos["preto_velho"].text,
            campos["crianca"].text,
            campos["exu"].text,
            campos["pomba_gira"].text,
        ]

        spreadsheet.worksheet("Dados Pessoais").append_row(dados_pessoais)
        spreadsheet.worksheet("Respostas").append_row(dados_respostas)
        spreadsheet.worksheet("Dados Espirituais").append_row(dados_espirituais)

        show_dialog("Sucesso", "Dados salvos com sucesso!")

    except Exception as e:
        show_dialog("Erro", f"Erro ao salvar: {str(e)}")


class MaskedTextField(MDTextField):
    def __init__(self, mask_type=None, **kwargs):
        super().__init__(**kwargs)
        self.mask_type = mask_type
        self.bind(text=self.on_text_change)

    def on_text_change(self, instance, text):
        if self.mask_type == "date":
            self.apply_date_mask(text)
        elif self.mask_type == "cpf":
            self.apply_cpf_mask(text)
        elif self.mask_type == "phone":
            self.apply_phone_mask(text)

    def apply_date_mask(self, text):
        # Remove tudo que não for número
        numbers_only = re.sub(r'\D', '', text)
        
        # Aplica a máscara DD/MM/YYYY
        if len(numbers_only) <= 2:
            masked = numbers_only
        elif len(numbers_only) <= 4:
            masked = f"{numbers_only[:2]}/{numbers_only[2:]}"
        elif len(numbers_only) <= 8:
            masked = f"{numbers_only[:2]}/{numbers_only[2:4]}/{numbers_only[4:]}"
        else:
            masked = f"{numbers_only[:2]}/{numbers_only[2:4]}/{numbers_only[4:8]}"
        
        if masked != text:
            self.text = masked

    def apply_cpf_mask(self, text):
        # Remove tudo que não for número
        numbers_only = re.sub(r'\D', '', text)
        
        # Aplica a máscara XXX.XXX.XXX-XX
        if len(numbers_only) <= 3:
            masked = numbers_only
        elif len(numbers_only) <= 6:
            masked = f"{numbers_only[:3]}.{numbers_only[3:]}"
        elif len(numbers_only) <= 9:
            masked = f"{numbers_only[:3]}.{numbers_only[3:6]}.{numbers_only[6:]}"
        elif len(numbers_only) <= 11:
            masked = f"{numbers_only[:3]}.{numbers_only[3:6]}.{numbers_only[6:9]}-{numbers_only[9:]}"
        else:
            masked = f"{numbers_only[:3]}.{numbers_only[3:6]}.{numbers_only[6:9]}-{numbers_only[9:11]}"
        
        if masked != text:
            self.text = masked

    def apply_phone_mask(self, text):
        # Remove tudo que não for número
        numbers_only = re.sub(r'\D', '', text)
        
        # Aplica a máscara (XX)XXXXX-XXXX
        if len(numbers_only) <= 2:
            masked = f"({numbers_only}"
        elif len(numbers_only) <= 7:
            masked = f"({numbers_only[:2]}){numbers_only[2:]}"
        elif len(numbers_only) <= 11:
            masked = f"({numbers_only[:2]}){numbers_only[2:7]}-{numbers_only[7:]}"
        else:
            masked = f"({numbers_only[:2]}){numbers_only[2:7]}-{numbers_only[7:11]}"
        
        if masked != text:
            self.text = masked


def styled_field(hint_text, key, multiline=False, mask_type=None, width=None):
    if mask_type:
        field = MaskedTextField(
            hint_text=hint_text,
            multiline=multiline,
            mode="rectangle",
            size_hint_x=None if width else 1,
            width=width if width else dp(0),
            mask_type=mask_type,
        )
    else:
        field = MDTextField(
            hint_text=hint_text,
            multiline=multiline,
            mode="rectangle",
            size_hint_x=None if width else 1,
            width=width if width else dp(0),
        )
    campos[key] = field
    return field


def create_dropdown_field(hint_text, key, items):
    field = MDTextField(
        hint_text=hint_text,
        mode="rectangle",
        readonly=True,
    )
    campos[key] = field
    
    menu_items = []
    for item in items:
        menu_items.append({
            "viewclass": "OneLineListItem",
            "text": item,
            "height": dp(56),
            "on_release": lambda x=item: set_dropdown_value(key, x),
        })
    
    dropdown = MDDropdownMenu(
        caller=field,
        items=menu_items,
        width_mult=4,
    )
    dropdowns[key] = dropdown
    
    field.bind(on_focus=lambda instance, focus: dropdown.open() if focus else None)
    
    return field


def set_dropdown_value(key, value):
    campos[key].text = value
    dropdowns[key].dismiss()


class Aba(BoxLayout, MDTabsBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(10)
        self.spacing = dp(10)
        self.size_hint_y = 1
        self.size_hint_x = 1


class FormularioApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Green"
        self.icon = "./RM.png"  # Altere se desejar
        Window.clearcolor = get_color_from_hex(COLOR_BG)

        root = MDFloatLayout()
        
        # Configurar tabs para ocupar toda a largura
        tabs = MDTabs(
            size_hint=(1, 0.9),
            pos_hint={"center_x": 0.5, "top": 1}
        )

        root.add_widget(tabs)

        tabs.add_widget(self.aba_dados_pessoais())
        tabs.add_widget(self.aba_perguntas())
        tabs.add_widget(self.aba_dados_espirituais())

        btn_salvar = MDRaisedButton(
            text="SALVAR",
            md_bg_color=COLOR_BTN,
            pos_hint={"center_x": 0.5, "y": 0.02},
            on_release=salvar_formulario,
        )
        root.add_widget(btn_salvar)
        return root

    def base_layout(self):
        layout = GridLayout(cols=1, spacing=dp(12), padding=dp(20), size_hint_y=None)
        layout.bind(minimum_height=layout.setter("height"))
        return layout

    def aba_dados_pessoais(self):
        aba = Aba(title="Dados Pessoais")
        layout = self.base_layout()

        layout.add_widget(styled_field("Nome", "nome"))
        layout.add_widget(styled_field("Data de Nascimento (DD/MM/AAAA)", "data_nascimento", mask_type="date"))
        layout.add_widget(styled_field("Nacionalidade", "nacionalidade"))
        layout.add_widget(styled_field("Naturalidade", "naturalidade"))
        layout.add_widget(styled_field("Endereço", "endereco"))
        layout.add_widget(styled_field("Bairro", "bairro"))
        layout.add_widget(styled_field("Cidade", "cidade"))
        layout.add_widget(styled_field("CEP", "cep"))
        layout.add_widget(styled_field("Telefone (XX)XXXXX-XXXX", "telefone", mask_type="phone"))
        layout.add_widget(styled_field("Identidade", "identidade"))
        layout.add_widget(styled_field("CPF (XXX.XXX.XXX-XX)", "cpf", mask_type="cpf"))
        
        # Estado Civil dropdown
        layout.add_widget(create_dropdown_field("Estado Civil", "estado_civil", 
                                               ["Solteiro", "Casado", "Viúvo"]))
        
        layout.add_widget(styled_field("Pai", "pai"))
        layout.add_widget(styled_field("Mãe", "mae"))
        layout.add_widget(styled_field("Data de Admissão (DD/MM/AAAA)", "data_admissao", mask_type="date"))

        scroll = ScrollView()
        scroll.add_widget(layout)
        aba.add_widget(scroll)
        return aba

    def aba_perguntas(self):
        aba = Aba(title="Perguntas")
        layout = self.base_layout()

        perguntas = [
            ("Motivo para ser sócio", "motivo"),
            ("Opinião sobre a tenda", "opiniao"),
            ("Objetivo espiritual", "objetivo"),
            ("É espírita?", "espirita"),
            ("O que é ser um bom espírita?", "bom_espirita"),
            ("Por que deseja participar?", "porque"),
            ("Quem indicou?", "indicacao"),
        ]

        for hint, key in perguntas:
            layout.add_widget(styled_field(hint, key, multiline=True))

        scroll = ScrollView()
        scroll.add_widget(layout)
        aba.add_widget(scroll)
        return aba

    def aba_dados_espirituais(self):
        aba = Aba(title="Dados Espirituais")
        layout = self.base_layout()

        # Função dropdown
        layout.add_widget(create_dropdown_field("Função", "funcao", 
                                               ["Médium", "Ogan", "Cambone", "Assistência"]))
        
        # Cargo dropdown
        layout.add_widget(create_dropdown_field("Cargo", "cargo", 
                                               ["Abian", "Quartinha", "Yao", "Baba"]))

        espirituais = [
            ("Padrinho", "padrinho"),
            ("Madrinha", "madrinha"),
            ("Pai Orixá", "pai_orixa"),
            ("Mãe Orixá", "mae_orixa"),
            ("Caboclo", "caboclo"),
            ("Preto Velho", "preto_velho"),
            ("Criança", "crianca"),
            ("Exu", "exu"),
            ("Pomba Gira", "pomba_gira"),
        ]

        for hint, key in espirituais:
            layout.add_widget(styled_field(hint, key))

        scroll = ScrollView()
        scroll.add_widget(layout)
        aba.add_widget(scroll)
        return aba


if __name__ == "__main__":
    FormularioApp().run()