import flet as ft

def main(page:ft.Page):
    page.bgcolor = ft.colors.BLUE_GREY_800
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.title = "Título de la aplicación"
    texto = ft.Text("Mi primera aplicación con Flet")
    texto2 = ft.Text("Este es un ejemplo para mi canal de Youtube")

    def cambiar_texto(e):
        texto2.value = "Suscribete para mas tutoriales"
        page.update()

    boton = ft.FilledButton(text="Cambiar texto", on_click=cambiar_texto)
    page.add(texto, texto2, boton)

ft.app(target=main)   
#ft.app(target=main) #, view=ft.Web_Browser)
