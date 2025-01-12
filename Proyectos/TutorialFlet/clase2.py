import flet as ft

def main(page: ft.Page):

        page.bgcolor = ft.colors.BLUE_GREY_800
        page.title = "Mi app mejorada con filas y columnas"
        texto1 = ft.Text("Texto1", size=24, color=ft.colors.WHITE)
        texto2 = ft.Text("Texto2", size=24, color=ft.colors.WHITE)
        texto3 = ft.Text("Texto3", size=24, color=ft.colors.WHITE)
       # page.add(texto1, texto2, texto3)

        fila_textos = ft.Row(
                controls=[texto1, texto2, texto3],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=50
        )
        page.add(fila_textos)

        boton1 = ft.FilledButton(text="Botón 1")
        boton2 = ft.FilledButton(text="Botón 2")
        boton3 = ft.FilledButton(text="Botón 3")

        fila_botones = ft.Row(
                controls=[boton1, boton2, boton3],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=50
        )
        page.add(fila_botones)

        textos_columnas1=[
            ft.Text("Columna 1 Fila 1", size=18, color=ft.colors.WHITE),
            ft.Text("Columna 1 Fila 2", size=18, color=ft.colors.WHITE),
            ft.Text("Columna 1 Fila 3", size=18, color=ft.colors.WHITE)]

        columna_texto1 = ft.Column(
                controls=textos_columnas1
        )
        #page.add(columna_texto1)

        textos_columnas2=[
            ft.Text("Columna 2 Fila 1", size=18, color=ft.colors.WHITE),
            ft.Text("Columna 2 Fila 2", size=18, color=ft.colors.WHITE),
            ft.Text("Columna 2 Fila 3", size=18, color=ft.colors.WHITE)]

        columna_texto2 = ft.Column(
                controls=textos_columnas2
        )

        fila_columnas = ft.Row(
                controls=[columna_texto1, columna_texto2],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=50
        )

        page.add(fila_columnas)

ft.app(target=main)