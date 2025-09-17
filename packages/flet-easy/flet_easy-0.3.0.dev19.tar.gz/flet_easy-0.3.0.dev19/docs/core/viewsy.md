# View System (Viewsy)

The `Viewsy` class provides a comprehensive view template system for Flet-Easy applications, allowing you to define consistent layouts, navigation elements, and responsive designs across your entire application.

## Overview

`Viewsy` enables you to:

- **Global Layout**: Define consistent app-wide layout templates
- **Navigation Components**: Configure app bars, drawers, and navigation bars
- **Responsive Design**: Create adaptive layouts for different screen sizes
- **Theme Management**: Apply consistent styling and theming
- **Component Reusability**: Share common UI elements across pages

## Class Definition

```python
class Viewsy(ft.View):
    def __init__(
        self,
        route: str = "/",
        controls: Optional[List[ft.Control]] = None,
        appbar: Optional[ft.AppBar] = None,
        drawer: Optional[ft.NavigationDrawer] = None,
        end_drawer: Optional[ft.NavigationDrawer] = None,
        floating_action_button: Optional[ft.FloatingActionButton] = None,
        navigation_bar: Optional[ft.NavigationBar] = None,
        bgcolor: Optional[str] = None,
        spacing: Optional[float] = None,
        padding: Optional[ft.Padding] = None,
        vertical_alignment: Optional[ft.MainAxisAlignment] = None,
        horizontal_alignment: Optional[ft.CrossAxisAlignment] = None,
        scroll: Optional[ft.ScrollMode] = None,
        auto_scroll: Optional[bool] = None,
        fullscreen_dialog: Optional[bool] = None,
        on_scroll_interval: Optional[int] = None,
        on_scroll: Optional[Callable] = None
    )
```

## Basic Usage

### Simple Global View

```python
import flet as ft
import flet_easy as fs

app = fs.FletEasy()

@app.view
def main_view(data: fs.Datasy):
    return fs.Viewsy(
        appbar=ft.AppBar(
            title=ft.Text("My Application"),
            center_title=True,
            bgcolor=ft.Colors.BLUE,
            actions=[
                ft.IconButton(ft.Icons.SETTINGS, on_click=data.go("/settings")),
                ft.IconButton(ft.Icons.LOGOUT, on_click=lambda _: data.logout("auth_token"))
            ]
        ),
        drawer=ft.NavigationDrawer(
            controls=[
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.HOME),
                    title=ft.Text("Home"),
                    on_click=data.go("/")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.PERSON),
                    title=ft.Text("Profile"),
                    on_click=data.go("/profile")
                ),
                ft.Divider(),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.SETTINGS),
                    title=ft.Text("Settings"),
                    on_click=data.go("/settings")
                )
            ]
        ),
        bgcolor=ft.Colors.BLACK12,
        padding=ft.padding.all(20)
    )

@app.page("/")
def home_page(data: fs.Datasy):
    return ft.View(
        controls=[
            ft.Text("Welcome to the Home Page!", size=24),
            ft.ElevatedButton("Go to Profile", on_click=data.go("/profile"))
        ],
        appbar=data.view.appbar,  # Use global appbar
        drawer=data.view.drawer,  # Use global drawer
        bgcolor=data.view.bgcolor,  # Use global background
        padding=data.view.padding   # Use global padding
    )

if __name__ == "__main__":
    app.run()
```

## Advanced View Configurations

### Responsive Navigation

```python
import flet as ft
import flet_easy as fs

app = fs.FletEasy()


@app.view
def responsive_view(data: fs.Datasy):
    # Create adaptive navigation based on screen size
    def create_navigation():
        # This will be called when the view is created
        # You can access screen size through data.page properties

        if data.page.window.width < 600:
            # Mobile: Use bottom navigation
            return {
                "navigation_bar": ft.NavigationBar(
                    destinations=[
                        ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
                        ft.NavigationBarDestination(icon=ft.Icons.SEARCH, label="Search"),
                        ft.NavigationBarDestination(icon=ft.Icons.PERSON, label="Profile"),
                    ],
                    on_change=lambda e: data.go_navigation_bar(e.control.selected_index),
                ),
                "drawer": None,
            }
        else:
            # Desktop: Use side drawer
            return {
                "drawer": ft.NavigationDrawer(
                    controls=[
                        ft.Container(height=20),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.HOME),
                            title=ft.Text("Home"),
                            on_click=data.go("/home"),
                        ),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.SEARCH),
                            title=ft.Text("Search"),
                            on_click=data.go("/search"),
                        ),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.PERSON),
                            title=ft.Text("Profile"),
                            on_click=data.go("/profile"),
                        ),
                    ]
                ),
                "navigation_bar": None,
            }

    nav_config = create_navigation()

    return fs.Viewsy(
        appbar=ft.AppBar(
            title=ft.Text("Responsive App"),
            leading=ft.IconButton(
                ft.Icons.MENU, on_click=lambda _: setattr(data.page.drawer, "open", True)
            )
            if nav_config["drawer"]
            else None,
            actions=[
                ft.IconButton(ft.Icons.NOTIFICATIONS),
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(text="Settings", on_click=data.go("/settings")),
                        ft.PopupMenuItem(text="Logout", on_click=lambda _: data.logout("token")),
                    ]
                ),
            ],
        ),
        drawer=nav_config["drawer"],
        navigation_bar=nav_config["navigation_bar"],
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        padding=ft.padding.symmetric(horizontal=20, vertical=10),
    )


@app.page("/")
def home_page(data: fs.Datasy):
    return ft.View(
        controls=[
            ft.Text("Welcome to the Home Page!", size=24),
            ft.ElevatedButton("Go to Profile", on_click=data.go("/profile")),
        ],
        appbar=data.view.appbar,  # Use global appbar
        drawer=data.view.drawer,  # Use global drawer
        bgcolor=data.view.bgcolor,  # Use global background
        padding=data.view.padding,  # Use global padding
        navigation_bar=data.view.navigation_bar,
    )


if __name__ == "__main__":
    app.run() # <600
    # app.run(view=ft.AppView.WEB_BROWSER)
```

### Theme-Based View

```python
class ThemeManager:
    @staticmethod
    def get_theme(theme_name: str):
        themes = {
            "light": {
                "bgcolor": ft.Colors.WHITE,
                "appbar_color": ft.Colors.BLUE,
                "text_color": ft.Colors.BLACK,
                "surface_color": ft.Colors.GREY_100
            },
            "dark": {
                "bgcolor": ft.Colors.GREY_900,
                "appbar_color": ft.Colors.BLUE_GREY_800,
                "text_color": ft.Colors.WHITE,
                "surface_color": ft.Colors.GREY_800
            },
            "custom": {
                "bgcolor": ft.Colors.PURPLE_50,
                "appbar_color": ft.Colors.PURPLE,
                "text_color": ft.Colors.PURPLE_900,
                "surface_color": ft.Colors.PURPLE_100
            }
        }
        return themes.get(theme_name, themes["light"])

@app.view
def themed_view(data: fs.Datasy):
    # Get current theme from user preferences
    current_theme = data.page.client_storage.get("theme", "light")
    theme = ThemeManager.get_theme(current_theme)
    
    def toggle_theme(_):
        new_theme = "dark" if current_theme == "light" else "light"
        data.page.client_storage.set("theme", new_theme)
        data.page.window_reload()  # Reload to apply new theme
    
    return fs.Viewsy(
        appbar=ft.AppBar(
            title=ft.Text("Themed Application", color=ft.Colors.WHITE),
            bgcolor=theme["appbar_color"],
            actions=[
                ft.IconButton(
                    ft.Icons.BRIGHTNESS_6,
                    tooltip="Toggle Theme",
                    on_click=toggle_theme,
                    icon_color=ft.Colors.WHITE
                ),
                ft.IconButton(
                    ft.Icons.SETTINGS,
                    on_click=data.go("/settings"),
                    icon_color=ft.Colors.WHITE
                )
            ]
        ),
        drawer=ft.NavigationDrawer(
            bgcolor=theme["surface_color"],
            controls=[
                ft.Container(
                    content=ft.Text(
                        "Navigation",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=theme["text_color"]
                    ),
                    padding=ft.padding.all(20)
                ),
                ft.Divider(),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.HOME, color=theme["text_color"]),
                    title=ft.Text("Home", color=theme["text_color"]),
                    on_click=data.go("/home")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.DASHBOARD, color=theme["text_color"]),
                    title=ft.Text("Dashboard", color=theme["text_color"]),
                    on_click=data.go("/dashboard")
                ),
            ]
        ),
        bgcolor=theme["bgcolor"],
        padding=ft.padding.all(15)
    )
```

## Component Integration

### Advanced Drawer with User Info

```python
import flet as ft
import flet_easy as fs

app = fs.FletEasy(route_init="/home")


@app.view
def user_drawer_view(data: fs.Datasy):
    # Get user information
    username = data.page.client_storage.get("username") or "Guest"
    user_email = data.page.client_storage.get("user_email") or ""
    user_avatar = data.page.client_storage.get("user_avatar") or ""

    return fs.Viewsy(
        appbar=ft.AppBar(title=ft.Text("My Application"), bgcolor=ft.Colors.INDIGO),
        drawer=ft.NavigationDrawer(
            controls=[
                # User header
                ft.Container(
                    content=ft.Column(
                        [
                            ft.CircleAvatar(
                                foreground_image_src=user_avatar if user_avatar else None,
                                content=ft.Text(username[0].upper()) if not user_avatar else None,
                                radius=30,
                            ),
                            ft.Text(username, size=18, weight=ft.FontWeight.BOLD),
                            ft.Text(user_email, size=12, color=ft.Colors.GREY_600),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=ft.Colors.INDIGO_100,
                    padding=ft.padding.all(20),
                    margin=ft.margin.only(bottom=10),
                ),
                # Navigation items
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.HOME), title=ft.Text("Home"), on_click=data.go("/home")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.DASHBOARD),
                    title=ft.Text("Dashboard"),
                    on_click=data.go("/dashboard"),
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.FAVORITE),
                    title=ft.Text("Favorites"),
                    on_click=data.go("/favorites"),
                ),
                ft.Divider(),
                # Settings and logout
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.SETTINGS),
                    title=ft.Text("Settings"),
                    on_click=data.go("/settings"),
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.HELP), title=ft.Text("Help"), on_click=data.go("/help")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.LOGOUT, color=ft.Colors.RED),
                    title=ft.Text("Logout", color=ft.Colors.RED),
                    on_click=lambda _: [data.logout("auth_token"), data.go("/login")],
                ),
            ]
        ),
    )
```

### Page-Specific View Modifications

```python
@app.page("/home", title="Home")
def home_page(data: fs.Datasy):
    # Use global view with modifications
    view = data.view
    view.appbar.title = ft.Text("Home - Welcome!")
    view.appbar.actions.append(
        ft.IconButton(ft.Icons.REFRESH, on_click=lambda _: data.page.update())
    )

    return ft.View(
        controls=[
            ft.Text("Welcome to the Home Page!", size=24),
            ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Quick Actions", size=18, weight=ft.FontWeight.BOLD),
                            ft.Row(
                                [
                                    ft.ElevatedButton(
                                        "New Project", on_click=data.go("/projects/new")
                                    ),
                                    ft.ElevatedButton("View Reports", on_click=data.go("/reports")),
                                ]
                            ),
                        ]
                    ),
                    padding=ft.padding.all(20),
                )
            ),
        ],
        appbar=view.appbar,
        drawer=view.drawer,
        bgcolor=view.bgcolor,
        padding=view.padding,
    )


@app.page("/profile", title="My Profile")
def profile_page(data: fs.Datasy):
    # Modify view for profile page
    view = data.view
    view.appbar.title = ft.Text("My Profile")
    view.appbar.bgcolor = ft.Colors.GREEN

    # Add profile-specific action
    view.appbar.actions = [
        ft.IconButton(ft.Icons.EDIT, on_click=data.go("/profile/edit")),
        ft.IconButton(ft.Icons.SETTINGS, on_click=data.go("/settings")),
    ]

    return ft.View(
        controls=[
            ft.Text("User Profile", size=24),
            # Profile content here
        ],
        appbar=view.appbar,
        drawer=view.drawer,
    )


if __name__ == "__main__":
    app.run()
```
