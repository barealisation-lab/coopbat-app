import os
import requests

from kivy.lang import Builder
from kivy.resources import resource_add_path
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, BooleanProperty, ListProperty, DictProperty
from kivy.uix.popup import Popup

from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.menu import MDDropdownMenu


# -------------------------
# Screens
# -------------------------
class AccueilScreen(Screen):
    pass

class ArtisansScreen(Screen):
    """
    Écran "Nous les artisans"
    Les cards et contenus sont dans le KV.
    """
    pass

class LoginScreen(Screen):
    pass

class RegisterScreen(Screen):
    pass

class ArtisanLoginScreen(Screen):
    pass

class ArtisanRegisterScreen(Screen):
    pass

class ArtisanMenuScreen(Screen):
    """
    Liste des demandes pour artisan.
    """
    def on_pre_enter(self, *args):
        app = MDApp.get_running_app()
        self.refresh_requests()

    def refresh_requests(self):
        app = MDApp.get_running_app()
        if not app.artisan_logged_in:
            return
        try:
            r = requests.get(f"{app.API_BASE}/artisan/requests/{app.artisan_id}", timeout=15)
            if r.status_code != 200:
                toast(r.text)
                return
            app.artisan_requests = r.json()
            app.render_artisan_requests()
        except Exception as e:
            toast(f"Erreur réseau: {e}")

    def open_request_actions(self, req):
        """
        Popup traiter / plus tard
        """
        app = MDApp.get_running_app()

        content_kv = f"""
MDBoxLayout:
    orientation: "vertical"
    padding: "14dp"
    spacing: "12dp"
    size_hint_y: None
    height: self.minimum_height

    MDLabel:
        text: "Traiter cette demande ?"
        halign: "center"
        font_style: "H6"
        adaptive_height: True

    MDLabel:
        text: "{req.get('nature','')}"
        halign: "center"
        theme_text_color: "Secondary"
        adaptive_height: True

    MDBoxLayout:
        orientation: "horizontal"
        spacing: "10dp"
        adaptive_height: True

        MDRaisedButton:
            text: "Traiter ce chantier"
            on_release: app.set_request_status('{req["kind"]}', {req["id"]}, "in_progress"); app._popup.dismiss()

        MDRectangleFlatButton:
            text: "Ne pas traiter pour le moment"
            on_release: app._popup.dismiss()
"""
        content = Builder.load_string(content_kv)
        app._popup = Popup(title="Demande", content=content, size_hint=(0.9, 0.45))
        app._popup.open()


class MenuTravauxScreen(Screen):
    def on_pre_enter(self, *args):
        app = MDApp.get_running_app()
        if not app.is_logged_in:
            toast("Veuillez vous connecter.")
            app.change_screen("login")

    def select_work(self, work_type: str):
        app = MDApp.get_running_app()
        app.selected_work = work_type
        app.change_screen("estimation")


class EstimationScreen(Screen):
    options = ListProperty([])

    def on_pre_enter(self, *args):
        app = MDApp.get_running_app()
        type_travaux = app.selected_work
        base_type = type_travaux.replace("Lot ", "", 1) if type_travaux.startswith("Lot ") else type_travaux

        if base_type == "Charpente":
            self.options = ["Nouveau projet", "Rénovation", "Extension", "Autre"]
        elif base_type == "Couverture":
            self.options = ["Réfection de couverture", "Rénovation de toiture", "Isolation", "Autre"]
        elif base_type == "Zinguerie":
            self.options = ["Rénovation", "Couverture", "Habillage", "Autre"]
        else:
            self.options = ["Autre projet"]

        self.ids.work_label.text = f"Type de travaux : {type_travaux}"
        self.ids.option_item.text = "Choisissez une option"
        self.ids.name_field.text = ""
        self.ids.email_field.text = ""
        self.ids.surface_field.text = ""
        self.ids.budget_field.text = ""
        self.ids.message_field.text = ""
        self.build_option_menu()

    def build_option_menu(self):
        if hasattr(self, "_menu") and self._menu:
            self._menu.dismiss()
            self._menu = None
        items = [{"text": opt, "on_release": (lambda x=opt: self.set_option(x))} for opt in self.options]
        self._menu = MDDropdownMenu(caller=self.ids.option_item, items=items, width_mult=5)

    def open_option_menu(self):
        if not hasattr(self, "_menu") or self._menu is None:
            self.build_option_menu()
        self._menu.open()

    def set_option(self, value: str):
        self.ids.option_item.text = value
        if hasattr(self, "_menu") and self._menu:
            self._menu.dismiss()

    def get_selected_option(self) -> str:
        txt = self.ids.option_item.text.strip()
        if txt == "" or txt.lower().startswith("choisissez"):
            return ""
        return txt


class ChiffrageLotsScreen(Screen):
    couverture_types = [
        "Tuile mécanique faible pente (25-35%)",
        "Tuile mécanique forte pente (35-45%)",
        "Ardoise",
        "Zinc",
        "Autre",
    ]

    def on_pre_enter(self, *args):
        self.ids.couv_type_item.text = "Type de couverture"
        self.ids.couv_surface.text = ""
        self.ids.sw_isolation.active = False
        self.ids.sw_sarking.active = False
        self.ids.sw_ecran.active = True

        for cbid in [
            "cb_zing_gout", "cb_zing_chem", "cb_zing_coul", "cb_zing_solins",
            "cb_zing_rives", "cb_zing_desc", "cb_zing_hab", "cb_zing_noues"
        ]:
            if cbid in self.ids:
                self.ids[cbid].active = False

        for cbid in ["cb_charp_reno", "cb_charp_ext", "cb_charp_sur", "cb_charp_new", "cb_charp_other"]:
            if cbid in self.ids:
                self.ids[cbid].active = False

        self.ids.contact_name.text = ""
        self.ids.contact_commune.text = ""
        self.ids.contact_email.text = ""
        self.ids.contact_message.text = ""
        self.build_couv_menu()

    def build_couv_menu(self):
        if hasattr(self, "_couv_menu") and self._couv_menu:
            self._couv_menu.dismiss()
            self._couv_menu = None
        items = [{"text": t, "on_release": (lambda x=t: self.set_couv_type(x))} for t in self.couverture_types]
        self._couv_menu = MDDropdownMenu(caller=self.ids.couv_type_item, items=items, width_mult=6)

    def open_couv_menu(self):
        if not hasattr(self, "_couv_menu") or self._couv_menu is None:
            self.build_couv_menu()
        self._couv_menu.open()

    def set_couv_type(self, value: str):
        self.ids.couv_type_item.text = value
        if hasattr(self, "_couv_menu") and self._couv_menu:
            self._couv_menu.dismiss()

    def collect_choices(self):
        zing = []
        zing_map = [
            ("cb_zing_gout", "Gouttières"),
            ("cb_zing_chem", "Tour de cheminée"),
            ("cb_zing_coul", "Couloir"),
            ("cb_zing_solins", "Solins"),
            ("cb_zing_rives", "Frontons / rives"),
            ("cb_zing_desc", "Descentes"),
            ("cb_zing_hab", "Habillages"),
            ("cb_zing_noues", "Noues"),
        ]
        for cid, label in zing_map:
            if self.ids.get(cid) and self.ids[cid].active:
                zing.append(label)

        charp = []
        if self.ids.cb_charp_reno.active: charp.append("Rénovation")
        if self.ids.cb_charp_ext.active: charp.append("Extension")
        if self.ids.cb_charp_sur.active: charp.append("Sur-élévation")
        if self.ids.cb_charp_new.active: charp.append("Nouveau projet")
        if self.ids.cb_charp_other.active: charp.append("Autre")

        return zing, charp


class AfterSendScreen(Screen):
    pass


class AdvancedChiffrageScreen(Screen):
    pass


# -------------------------
# App
# -------------------------
class CoopApp(MDApp):
    API_BASE = "http://127.0.0.1:8000"

    # pro/user (client)
    selected_work = StringProperty("")
    is_logged_in = BooleanProperty(False)
    current_user_id = StringProperty("")
    current_user_name = StringProperty("")
    current_user_email = StringProperty("")

    # artisan
    artisan_token = StringProperty("")
    artisan_logged_in = BooleanProperty(False)
    artisan_id = StringProperty("")
    artisan_name = StringProperty("")
    artisan_email = StringProperty("")
    artisan_commune = StringProperty("")
    artisan_radius = StringProperty("30")
    artisan_phone = StringProperty("")
    artisan_zone_note = StringProperty("")
    artisan_requests = ListProperty([])

    def build(self):
        project_root = os.path.dirname(os.path.abspath(__file__))
        resource_add_path(project_root)
        self.title = "Coop'Bat"
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Light"
        kv_path = os.path.join(project_root, "coop.kv")
        return Builder.load_file(kv_path)

    def change_screen(self, name: str):
        self.root.current = name

    # -------------------------
    # Accueil buttons
    # -------------------------
    def open_discover(self):
        self.change_screen("artisans")

    def open_artisan_account(self):
        self.change_screen("artisan_login")

    def start_estimation_flow(self):
        if not self.is_logged_in:
            self.change_screen("login")
        else:
            self.change_screen("menu_travaux")

    # -------------------------
    # PRO auth
    # -------------------------
    def register_user(self):
        screen = self.root.get_screen("register")
        name = screen.ids.reg_name.text.strip()
        email = screen.ids.reg_email.text.strip()
        password = screen.ids.reg_password.text.strip()
        if not name or not email or not password:
            toast("Veuillez remplir tous les champs.")
            return
        try:
            r = requests.post(f"{self.API_BASE}/register", json={"name": name, "email": email, "password": password}, timeout=10)
            if r.status_code == 200:
                toast("Compte créé ✅")
                self.change_screen("login")
            else:
                toast(r.json().get("detail", r.text))
        except Exception as e:
            toast(f"Erreur réseau : {e}")

    def login_user(self):
        screen = self.root.get_screen("login")
        email = screen.ids.login_email.text.strip()
        password = screen.ids.login_password.text.strip()
        if not email or not password:
            toast("Veuillez saisir email et mot de passe.")
            return
        try:
            r = requests.post(f"{self.API_BASE}/login", json={"email": email, "password": password}, timeout=10)
            if r.status_code == 200:
                data = r.json()
                self.is_logged_in = True
                self.current_user_id = str(data.get("user_id", ""))
                self.current_user_name = data.get("name", "")
                self.current_user_email = data.get("email", email)
                toast(f"Bienvenue {self.current_user_name} ✅")
                self.change_screen("menu_travaux")
            else:
                toast(r.json().get("detail", "Identifiants incorrects"))
        except Exception as e:
            toast(f"Erreur réseau : {e}")

    def logout(self):
        self.is_logged_in = False
        self.current_user_id = ""
        self.current_user_name = ""
        self.current_user_email = ""
        toast("Déconnecté")
        self.change_screen("accueil")

    # -------------------------
    # Artisan auth
    # -------------------------
    def artisan_go_register(self):
        self.change_screen("artisan_register")

    def artisan_register(self):
        s = self.root.get_screen("artisan_register")
        contact_name = s.ids.a_name.text.strip()
        email = s.ids.a_email.text.strip()
        phone = s.ids.a_phone.text.strip()
        commune = s.ids.a_commune.text.strip()
        radius = s.ids.a_radius.text.strip()
        zone_note = s.ids.a_zone_note.text.strip()
        password = s.ids.a_password.text.strip()

        if not contact_name or not email or not commune or not password:
            toast("Nom / Email / Commune / Mot de passe obligatoires.")
            return

        try:
            rk = int(radius) if radius else 30
        except Exception:
            rk = 30

        payload = {
            "contact_name": contact_name,
            "email": email,
            "phone": phone,
            "commune": commune,
            "radius_km": rk,
            "zone_note": zone_note,
            "password": password
        }

        try:
            r = requests.post(f"{self.API_BASE}/artisan/register", json=payload, timeout=12)
            if r.status_code == 200:
                toast("Compte artisan créé ✅")
                self.change_screen("artisan_login")
            else:
                toast(r.json().get("detail", r.text))
        except Exception as e:
            toast(f"Erreur réseau : {e}")

    def artisan_login(self):
        s = self.root.get_screen("artisan_login")
        email = s.ids.a_login_email.text.strip()
        password = s.ids.a_login_password.text.strip()
        if not email or not password:
            toast("Email + mot de passe requis.")
            return
        try:
            r = requests.post(f"{self.API_BASE}/artisan/login", json={"email": email, "password": password}, timeout=12)
            if r.status_code == 200:
                data = r.json()
                self.artisan_token = data.get("artisan_token", "")
                self.artisan_logged_in = True
                self.artisan_id = str(data.get("artisan_id", ""))
                self.artisan_name = data.get("contact_name", "")
                self.artisan_email = data.get("email", "")
                self.artisan_commune = data.get("commune", "")
                self.artisan_radius = str(data.get("radius_km", 30))
                self.artisan_phone = data.get("phone", "")
                self.artisan_zone_note = data.get("zone_note", "")
                toast(f"Bienvenue {self.artisan_name} ✅")
                self.change_screen("artisan_menu")
            else:
                toast(r.json().get("detail", "Identifiants incorrects"))
        except Exception as e:
            toast(f"Erreur réseau : {e}")

    def artisan_logout(self):
        self.artisan_logged_in = False
        self.artisan_token = ""
        self.artisan_id = ""
        self.artisan_name = ""
        self.artisan_email = ""
        self.artisan_commune = ""
        self.artisan_radius = "30"
        self.artisan_phone = ""
        self.artisan_zone_note = ""
        self.artisan_requests = []
        toast("Déconnecté")
        self.change_screen("accueil")
        try:
            if self.artisan_id and self.artisan_token:
                requests.post(
                    f"{self.API_BASE}/artisan/logout/{int(self.artisan_id)}",
                    headers={"X-ARTISAN-TOKEN": self.artisan_token},
                    timeout=8
                )
        except Exception:
            pass


    # -------------------------
    # Artisan requests UI
    # -------------------------
    def render_artisan_requests(self):
        try:
            screen = self.root.get_screen("artisan_menu")
        except Exception:
            return

        box = screen.ids.requests_box
        box.clear_widgets()

        from kivymd.uix.card import MDCard
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel

        for req in self.artisan_requests:
            status = (req.get("status") or "new").lower()
            status_text = "EN TRAITEMENT" if status == "in_progress" else "NOUVEAU"

            title = f"{req.get('nature','Demande')}"
            date = (req.get("date") or "")[:10]
            budget = req.get("budget", "")
            surf = req.get("surface_m2", "")
            email = req.get("email", "")
            commune = req.get("commune", "")

            line2 = f"{date} | {commune} | {email}".strip()
            line3 = ""
            if surf:
                line3 += f"{surf} m²  "
            if budget:
                line3 += f"Budget: {budget}"

            card = MDCard(orientation="vertical", padding="12dp", size_hint_y=None, height="120dp", radius=[16,])
            inner = MDBoxLayout(orientation="vertical", spacing="4dp")
            inner.add_widget(MDLabel(text=f"[b]{title}[/b]  —  {status_text}", markup=True))
            inner.add_widget(MDLabel(text=line2, theme_text_color="Secondary"))
            inner.add_widget(MDLabel(text=line3.strip(), theme_text_color="Secondary"))
            card.add_widget(inner)

            # click => popup
            def _make_cb(rq):
                return lambda *a: self.root.get_screen("artisan_menu").open_request_actions(rq)

            card.bind(on_release=_make_cb(req))
            box.add_widget(card)

    def set_request_status(self, kind: str, request_id: int, status: str):
        if not self.artisan_logged_in:
            return
        try:
            headers = {"X-ARTISAN-TOKEN": self.artisan_token}
            r = requests.post(
            f"{self.API_BASE}/artisan/requests/{int(self.artisan_id)}/{kind}/{int(request_id)}/status",
            json={"status": status},
            headers=headers,
            timeout=12
        )

            if r.status_code == 200:
                toast("Statut mis à jour ✅")
                # refresh list
                self.root.get_screen("artisan_menu").refresh_requests()
            else:
                toast(r.text)
        except Exception as e:
            toast(f"Erreur réseau: {e}")


if __name__ == "__main__":
    CoopApp().run()
