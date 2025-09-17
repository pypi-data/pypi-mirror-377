import flet as ft
import flet_easy as fs

app = fs.FletEasy(route_init="/")


@app.page("/", title="Home")
def home_page(data: fs.Datasy):
    page = data.page

    def save_data():
        page.session.set("name", "anonymous")

    def go_about(e):
        data.go_route("/about")

    return ft.View(
        controls=[
            ft.Text("Home Page"),
            ft.ElevatedButton("Save data", on_click=save_data),
            ft.ElevatedButton("Go to About", on_click=go_about),
            ft.ElevatedButton("Go to About", on_click=data.go("/about")),

        ]
    )


@app.page("/about", title="About")
def about_page(data: fs.Datasy):
    page = data.page

    name = page.session.get("name")

    if not name:
        #return data.go("/forbidden")()
        return data.redirect("/forbidden")

    return ft.View(
        controls=[
            ft.Text("About Page"),
            ft.Text(name),
            ft.ElevatedButton("Go to Home", on_click=lambda : data.go("/")),
        ]
    )


@app.page("/forbidden", title="Forbidden")
def forbidden_page(data: fs.Datasy):

    def _go_back(e):
        data.go_back()

    def _go_route(e):
        data.go_route("/forbidden2")

    return ft.View(
        controls=[
            ft.Text("Forbidden Page"),
            ft.ElevatedButton("Go to Home- go_back", on_click=data.go_back),
            ft.ElevatedButton("Go to forbidden2 - go_route", on_click=_go_route),
        ]
    )
@app.page("/forbidden2", title="Forbidden2")
def forbidden_page2(data: fs.Datasy):

    def _go_back(e):
        data.go_back()

    def _go_route(e):
        data.go_route("/")

    return ft.View(
        controls=[
            ft.Text("Forbidden Page"),
            ft.ElevatedButton("Go to Home- go_back", on_click=data.go_back),
            ft.ElevatedButton("Go to Home - go_route", on_click=_go_route),
        ]
    )


app.run()
