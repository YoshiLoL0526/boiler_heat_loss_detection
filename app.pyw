import os
import time
import threading
import flet as ft
from PIL import Image
from functools import wraps
from processor import ThermalImageProcessor
from utils import generate_pdf_report, load_image_file, load_config_file, celsius_to_kelvin

ASSETS_PATH = './assets'


def exception_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            self.show_error(f"Error: {ex}")

    return wrapper


def loading_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]

        bubble1 = ft.Container(animate=ft.animation.Animation(600, "bounceOut"), width=50, height=50,
                               border_radius=100,
                               bgcolor="#B932FD")
        bubble2 = ft.Container(animate=ft.animation.Animation(600, "bounceOut"), width=50, height=50,
                               border_radius=100,
                               bgcolor="#B932FD")
        bubble3 = ft.Container(animate=ft.animation.Animation(600, "bounceOut"), width=50, height=50,
                               border_radius=100,
                               bgcolor="#B932FD")
        bubble4 = ft.Container(animate=ft.animation.Animation(600, "bounceOut"), width=50, height=50,
                               border_radius=100,
                               bgcolor="#B932FD")
        loading = ft.Stack([
            ft.Container(expand=True, bgcolor=ft.colors.BLACK, opacity=0.8),
            ft.Column([
                ft.Row([
                    bubble1,
                    bubble2,
                    bubble3,
                    bubble4
                ], alignment='center'),
            ], alignment='center')
        ])

        def change():
            start = -1
            while is_loading:
                if start == -1:
                    bubble1.width = 50
                    bubble1.height = 50
                    self.page.update()
                    start = 1
                else:
                    time.sleep(0.5)
                    bubble4.width = 20
                    bubble4.height = 20
                    bubble1.width = 50
                    bubble1.height = 50
                    self.page.update()
                time.sleep(0.5)
                bubble1.width = 20
                bubble1.height = 20
                bubble2.width = 50
                bubble2.height = 50
                self.page.update()
                time.sleep(0.5)
                bubble2.width = 20
                bubble2.height = 20
                bubble3.width = 50
                bubble3.height = 50
                self.page.update()
                time.sleep(0.5)
                bubble3.width = 20
                bubble3.height = 20
                bubble4.width = 50
                bubble4.height = 50
                self.page.update()

        self.page.overlay.append(loading)
        self.page.update()
        is_loading = True

        thread = threading.Thread(target=change)
        thread.start()

        result = func(*args, **kwargs)

        is_loading = False
        self.page.overlay.clear()
        self.page.update()

        return result

    return wrapper


class App(ft.UserControl):
    def __init__(self):
        super().__init__()

        # Crear carpeta de assets
        if not os.path.exists(os.path.join(ASSETS_PATH, "empty_image.jpg")):
            if not os.path.exists(ASSETS_PATH):
                os.makedirs(ASSETS_PATH)
            img = Image.new("RGB", (240, 240), (255, 255, 255))
            img.save(os.path.join(ASSETS_PATH, "empty_image.png"), "PNG")

        self.image = ft.Image(src=os.path.join(ASSETS_PATH, "empty_image.png"),
                              width=240,
                              height=240,
                              fit=ft.ImageFit.CONTAIN,
                              visible=False)
        self.image_name = ft.Text(value='Empty', visible=False)

        self.temp_min = ft.TextField(label="Temperatura Mínima (ºC)")
        self.temp_max = ft.TextField(label="Temperatura Máxima (ºC)")
        self.boiler_width_px = ft.TextField(label="Ancho de Caldera (px)")
        self.boiler_width_m = ft.TextField(label="Ancho de Caldera (m)")
        self.fuel_flow = ft.TextField(label="Flujo de Combustible (kg/h)")
        self.heat_transfer_coeff = ft.TextField(label="Coef. Transferencia de Calor por Convección (W/m²K)")
        self.ambient_temp = ft.TextField(label="Temperatura Ambiente (ºC)")
        self.stefan_boltzmann_const = ft.TextField(
            label="Constante de Stefan Boltzmann (W/m²K^4)",
            value="5.670374419e-8",
            # disabled=True,
            read_only=True,
        )
        self.threshold = ft.TextField(label="Umbral de zona caliente", value="200")

        self.config_file_picker = ft.FilePicker(on_result=self.load_config)
        self.image_file_picker = ft.FilePicker(on_result=self.load_image)

        self.load_image_button = ft.ElevatedButton(
            text="Cargar Imagen",
            icon="image",
            on_click=lambda _: self.image_file_picker.pick_files(allow_multiple=False,
                                                                 allowed_extensions=["jpg", "png"])
        )
        self.load_config_button = ft.ElevatedButton(
            text="Cargar Configuración",
            icon="upload_file",
            on_click=lambda _: self.config_file_picker.pick_files(allow_multiple=False, allowed_extensions=["ini"])
        )
        self.generate_report_button = ft.ElevatedButton(
            text="Generar Reporte PDF",
            icon="picture_as_pdf",
            on_click=self.generate_pdf_report
        )

        # Create a Dialog for showing errors
        self.error_dialog = ft.AlertDialog(
            open=False,
            modal=True,
            title=ft.Text("Error"),
            content=ft.Text(""),
            actions=[ft.ElevatedButton("Cerrar", on_click=self.close_dialog)]
        )

    def show_error(self, message):
        self.error_dialog.content = ft.Text(message)
        self.error_dialog.open = True
        self.page.update()

    def show_info(self, message):
        info = ft.SnackBar(ft.Text(value=message))
        self.page.snack_bar = info
        info.open = True
        self.page.update()

    def close_dialog(self, e):
        self.error_dialog.open = False
        self.page.update()

    @loading_handler
    @exception_handler
    def load_config(self, e: ft.FilePickerResultEvent):
        if e.files:
            parameters = load_config_file(e.files[0].path)

            # Update fields
            self.temp_min.value = parameters.get('min_temp', 30)
            self.temp_max.value = parameters.get('max_temp', 250)
            self.boiler_width_px.value = parameters.get('boiler_width_px', 1)
            self.boiler_width_m.value = parameters.get('boiler_width_m', 1)
            self.fuel_flow.value = parameters.get('fuel_flow', 1)
            self.heat_transfer_coeff.value = parameters.get('heat_transfer_coeff', 1)
            self.ambient_temp.value = parameters.get('ambient_temp', 30)
            self.update()
            self.show_info('El archivo de configuración se ha cargado correctamente!')

    @loading_handler
    @exception_handler
    def load_image(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.image.src = e.files[0].path
            self.image.visible = True
            self.image_name.value = e.files[0].name
            self.image_name.visible = True
            self.update()
            self.show_info('La imagen se ha cargado correctamente!')

    @loading_handler
    @exception_handler
    def generate_pdf_report(self, e):
        if not self.image.visible:
            self.show_error('Debe abrir una imagen!')
            return

        # Check fields
        if not self.temp_min.value:
            self.temp_min.error_text = "Debe ingresar un valor"
            self.temp_min.update()
            return

        if not os.path.exists('./output'):
            os.makedirs('./output')

        thermal_processor = ThermalImageProcessor()
        data, histogram = thermal_processor.process(
            load_image_file(self.image.src),
            float(self.fuel_flow.value),
            float(self.heat_transfer_coeff.value),
            celsius_to_kelvin(float(self.ambient_temp.value)),
            float(self.stefan_boltzmann_const.value),
            float(self.boiler_width_m.value),
            int(self.boiler_width_px.value),
            celsius_to_kelvin(float(self.temp_min.value)),
            celsius_to_kelvin(float(self.temp_max.value)),
            int(self.threshold.value),
        )
        generate_pdf_report(data, histogram, './output/')
        self.show_info("Operación completada!")

    def build(self):
        self.page.vertical_alignment = 'start'
        self.page.horizontal_alignment = 'center'
        self.page.dialog = self.error_dialog
        return ft.Row([
            ft.Column([
                self.image,
                self.image_name,
            ], alignment='center'),
            ft.Column([
                ft.Row([
                    self.load_image_button,
                    self.load_config_button,
                ]),
                ft.Row([
                    self.temp_min,
                    self.temp_max,
                ]),
                ft.Row([
                    self.boiler_width_px,
                    self.boiler_width_m,
                ]),
                ft.Row([
                    self.fuel_flow,
                    self.heat_transfer_coeff,
                ]),
                ft.Row([
                    self.stefan_boltzmann_const,
                    self.ambient_temp,
                ]),
                ft.Row([
                    self.threshold,
                    self.generate_report_button,
                ])
                # self.load_image_button,
                # self.load_config_button,
                # self.temp_min,
                # self.temp_max,
                # self.boiler_width_px,
                # self.boiler_width_m,
                # self.fuel_flow,
                # self.heat_transfer_coeff,
                # self.stefan_boltzmann_const,
                # self.ambient_temp,
                # self.threshold,
                # self.generate_report_button,
            ]),
            self.config_file_picker,
            self.image_file_picker,
        ], alignment='center')


def main(page: ft.Page):
    page.title = "Heat Loss Detection"
    page.theme_mode = "light"
    # page.window_always_on_top = True
    page.vertical_alignment = "start"

    # set the width and height of the window.
    page.window_width = 1024
    page.window_height = 640

    page.horizontal_alignment = "center"
    page.scroll = 'auto'

    def change_theme(e):
        """
        Changes the app's theme_mode, from dark to light or light to dark.

        :param e: The event that triggered the function
        :type e: ControlEvent
        """

        page.theme_mode = "light" if page.theme_mode == "dark" else "dark"  # changes the page's theme_mode
        theme_icon_button.selected = not theme_icon_button.selected  # changes the icon
        page.update()

    theme_icon_button = ft.IconButton(
        ft.icons.DARK_MODE,
        selected=False,
        selected_icon=ft.icons.LIGHT_MODE,
        icon_size=35,
        tooltip="change theme",
        on_click=change_theme,
        style=ft.ButtonStyle(color={"": ft.colors.BLACK, "selected": ft.colors.WHITE}, ),
    )

    page.appbar = ft.AppBar(
        title=ft.Text(
            "Heat Loss Detection",
            color="white"
        ),
        center_title=True,
        bgcolor="blue",
        actions=[theme_icon_button],
        # leading=ft.IconButton(
        #     icon=ft.icons.CODE,
        #     icon_color=ft.colors.YELLOW_ACCENT,
        #     on_click=lambda e: page.launch_url(
        #         "https://github.com/ndonkoHenri/Flet-Samples/tree/master/Flet-Utils"),
        #     tooltip="View Code"
        # ),
    )

    page.add(App())


ft.app(target=main, assets_dir=ASSETS_PATH)
