import flet as ft
import flet_easy as fs
import time

app = fs.FletEasy(route_init="/counter")

@app.page(route="/counter", title="Counter")
def counter_page(data: fs.Datasy):
    page = data.page

    txt_number = ft.TextField(value="0", text_align="right", width=100)

    def add(e):
        for i in range(100):
            txt_number.value = str(int(txt_number.value) + 1)
            time.sleep(1)
            page.update()

    def reload(e):
        data.page_reload()

    return ft.View(
        controls=[
            ft.Row(
                [
                    ft.IconButton(ft.Icons.REPLAY_OUTLINED, on_click=reload),
                    txt_number,
                    ft.IconButton(ft.Icons.ADD, on_click=add),
                ],
                alignment="center",
            ),
        ],
        vertical_alignment="center",
        horizontal_alignment="center",
    )

# We run the application
app.run(view=ft.AppView.WEB_BROWSER)