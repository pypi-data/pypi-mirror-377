# Examples Gallery

This gallery showcases practical examples of Flet-Easy applications, from simple demos to complex real-world scenarios.

## Basic Examples

### Hello World App

```python
import flet as ft
import flet_easy as fs

app = fs.FletEasy()


@app.page("/")
def home_page(data: fs.Datasy):
    page = data.page

    # add snack bar
    def add_snack_bar(e):
        page.open(ft.SnackBar(content=ft.Text("Hello World!"), open=True))

    return ft.View(
        controls=[
            ft.Text("Hello, Flet-Easy!", size=30),
            ft.ElevatedButton("Click me!", on_click=add_snack_bar),
        ]
    )


if __name__ == "__main__":
    app.run()
```

### Counter App

```python
import flet as ft
import flet_easy as fs

app = fs.FletEasy()

# ==========================
# Reusable Components (OOP)
# ==========================
class Header(ft.Container):
    def __init__(self, title: str):
        super().__init__(
            content=ft.Text(title, size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            alignment=ft.alignment.center,
            padding=ft.padding.symmetric(vertical=14, horizontal=16),
            border_radius=12,
            gradient=ft.LinearGradient(
                begin=ft.alignment.center_left,
                end=ft.alignment.center_right,
                colors=[ft.Colors.INDIGO_700, ft.Colors.BLUE_700],
            ),
        )


class NavButton(ft.ElevatedButton):
    def __init__(self, text: str, color: str, on_click):
        super().__init__(
            text,
            on_click=on_click,
            width=140,
            height=48,
            style=ft.ButtonStyle(
                bgcolor=color,
                color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=24),
                elevation=6,
            ),
        )


class IconButtonPill(ft.ElevatedButton):
    def __init__(self, text: str, color: str, on_click):
        super().__init__(
            text,
            on_click=on_click,
            width=80,
            height=50,
            style=ft.ButtonStyle(
                bgcolor=color,
                color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=25),
                elevation=4,
            ),
        )


class InfoText(ft.Text):
    def __init__(self, value: str):
        super().__init__(value, size=14, weight=ft.FontWeight.W_500, color=ft.Colors.GREY_700, text_align=ft.TextAlign.CENTER)


class CounterCard(ft.Container):
    def __init__(self, value: int = 0):
        self._label = ft.Text(str(value), size=70, weight=ft.FontWeight.BOLD)
        super().__init__(
            content=self._label,
            alignment=ft.alignment.center,
            padding=ft.padding.all(24),
            border_radius=16,
            bgcolor=ft.Colors.with_opacity(0.10, ft.Colors.BLUE_200),
            border=ft.border.all(2, ft.Colors.BLUE_200),
        )
        self.set_value(value)

    def set_value(self, value: int):
        self._label.value = str(value)
        if value > 0:
            self._label.color = ft.Colors.TEAL_900
            self.bgcolor = ft.Colors.with_opacity(0.12, ft.Colors.TEAL_200)
            self.border = ft.border.all(2, ft.Colors.TEAL_300)
        elif value < 0:
            self._label.color = ft.Colors.RED_900
            self.bgcolor = ft.Colors.with_opacity(0.12, ft.Colors.RED_200)
            self.border = ft.border.all(2, ft.Colors.RED_300)
        else:
            self._label.color = ft.Colors.BLUE_900
            self.bgcolor = ft.Colors.with_opacity(0.12, ft.Colors.BLUE_200)
            self.border = ft.border.all(2, ft.Colors.BLUE_300)

# Demo: share_data=True allows data to persist between pages
@app.page("/", share_data=True)
def counter_page(data: fs.Datasy):
    count = data.share.get("count") or 0
    data.share.set("count", count)
    card = CounterCard(count)

    def increment(_):
        new_count = data.share.get("count") + 1
        data.share.set("count", new_count)
        card.set_value(new_count)
        card.update()
        data.page.update()

    def decrement(_):
        new_count = data.share.get("count") - 1
        data.share.set("count", new_count)
        card.set_value(new_count)
        card.update()
        data.page.update()

    return ft.View(
        controls=[
            Header("Counter Controls"),
            ft.Container(height=16),
            card,

            # Controls
            ft.Container(height=15),
            ft.Row([
                IconButtonPill("−", ft.Colors.RED_600, decrement),
                ft.Container(width=20),
                IconButtonPill("+", ft.Colors.TEAL_600, increment),
            ], alignment=ft.MainAxisAlignment.CENTER),

            # Navigation
            ft.Container(height=20),
            NavButton("View Value →", ft.Colors.INDIGO_700, data.go("/display")),

            # Info
            ft.Container(height=15),
            InfoText("💡 share_data=True: Counter persists between pages"),
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        bgcolor=ft.Colors.GREY_100,
    )

# Demo: share_data=True allows accessing the same shared data
@app.page("/display", share_data=True)
def display_page(data: fs.Datasy):
    count = data.share.get("count") or 0

    # Components
    card = CounterCard(count)
    status = ft.Text(
        f"Status: {'↑ Positive' if count > 0 else '→ Zero' if count == 0 else '↓ Negative'}",
        size=18,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.GREY_800,
        text_align=ft.TextAlign.CENTER,
    )

    return ft.View(
        controls=[
            Header("Shared Value"),
            ft.Container(height=16),
            card,
            ft.Container(height=12),
            status,
            ft.Container(height=20),
            NavButton("← Back to Controls", ft.Colors.AMBER_700, data.go("/")),
            ft.Container(height=12),
            InfoText("🔄 Same shared value from previous page"),
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        bgcolor=ft.Colors.GREY_100,
    )

# Run the demo app
if __name__ == "__main__":
    app.run()
```

## Intermediate Examples

### Todo List App

```python
import flet as ft
import flet_easy as fs
from datetime import datetime

app = fs.FletEasy()

@app.page("/", title="Todo List", share_data=True)
def todo_page(data: fs.Datasy):
    todos = data.share.get("todos") or []

    new_task = ft.TextField(hint_text="Enter a new task")
    task_list = ft.Column()

    def add_task(_):
        if new_task.value:
            task = {
                "id": len(todos),
                "text": new_task.value,
                "completed": False,
                "created": datetime.now().isoformat()
            }
            todos.append(task)
            data.share.set("todos", todos)
            new_task.value = ""
            update_task_list()
            data.page.update()

    def toggle_task(task_id):
        def toggle(_):
            todos[task_id]["completed"] = not todos[task_id]["completed"]
            data.share.set("todos", todos)
            update_task_list()
            data.page.update()
        return toggle

    def delete_task(task_id):
        def delete(_):
            todos.pop(task_id)
            # Reindex tasks
            for i, task in enumerate(todos):
                task["id"] = i
            data.share.set("todos", todos)
            update_task_list()
            data.page.update()
        return delete

    def update_task_list():
        task_list.controls.clear()
        for task in todos:
            task_list.controls.append(
                ft.Row([
                    ft.Checkbox(
                        value=task["completed"],
                        on_change=toggle_task(task["id"])
                    ),
                    ft.Text(
                        task["text"],
                        style=ft.TextThemeStyle.BODY_MEDIUM if not task["completed"] 
                        else ft.TextThemeStyle.BODY_SMALL,
                        color=ft.Colors.BLACK if not task["completed"] 
                        else ft.Colors.GREY_500
                    ),
                    ft.IconButton(
                        ft.Icons.DELETE,
                        on_click=delete_task(task["id"]),
                        icon_color=ft.Colors.RED
                    )
                ])
            )

    update_task_list()

    return ft.View(
        controls=[
            ft.Text("Todo List", size=24),
            ft.Row([
                new_task,
                ft.ElevatedButton("Add", on_click=add_task)
            ]),
            ft.Divider(),
            task_list
        ]
    )

app.run()
```

### User Authentication System

```python
import flet as ft
import flet_easy as fs
from datetime import timedelta

app = fs.FletEasy(
    route_init="/dashboard",
    route_login="/login",
    secret_key=fs.SecretKey(algorithm=fs.Algorithm.HS256, secret="demo-secret-key"),
    auto_logout=True,
    on_Keyboard=True,
)

# Mock user database
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "user": {"password": "user123", "role": "user"},
}


# ---------- Small reusable components ----------
class Card(ft.Container):
    def __init__(self, title: str, body_controls: list[ft.Control]):
        super().__init__(
            content=ft.Column(
                controls=[
                    ft.Text(title, size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Container(height=8),
                    ft.Column(spacing=12, controls=body_controls),
                ]
            ),
            padding=20,
            width=360,
            border_radius=16,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[ft.Colors.INDIGO_700, ft.Colors.BLUE_600],
            ),
        )


class PrimaryButton(ft.ElevatedButton):
    def __init__(self, text: str, on_click):
        super().__init__(
            text,
            on_click=on_click,
            height=44,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.AMBER_600,
                color=ft.Colors.BLACK,
                shape=ft.RoundedRectangleBorder(radius=12),
                elevation=6,
            ),
        )


@app.login
def check_auth(data: fs.Datasy):
    return data.page.client_storage.get("auth_token") is not None


@app.page("/login", title="Login")
def login_page(data: fs.Datasy):
    username = ft.TextField(label="Username")
    password = ft.TextField(label="Password", password=True)
    error_text = ft.Text(color=ft.Colors.RED_800, size=14, weight=ft.FontWeight.W_500)

    async def handle_login(_):
        user = USERS.get(username.value)
        if user and user["password"] == password.value:
            payload = {"username": username.value, "role": user["role"]}
            await data.login_async(
                "auth_token", payload, next_route="/dashboard", time_expiry=timedelta(seconds=10)
            )
        else:
            error_text.value = "Invalid credentials"
            data.page.update()

    # Handle key down event
    async def handle_key_down():
        if data.on_keyboard_event.key() == "Enter":
            await handle_login(None)

    # Add key down event listener
    data.on_keyboard_event.add_control(handle_key_down)

    content = Card(
        "Welcome",
        [
            ft.Container(content=ft.Text("Please sign in", color=ft.Colors.WHITE70), padding=0),
            username,
            password,
            error_text,
            PrimaryButton("Login", handle_login),
        ],
    )

    return ft.View(
        controls=[content],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )


@app.page("/dashboard", title="Dashboard", protected_route=True)
def dashboard_page(data: fs.Datasy):
    user = fs.decode("auth_token", data)

    if not user:
        return data.go("/login")

    def logout(_):
        data.logout("auth_token")()

    content = Card(
        "Dashboard",
        [
            ft.Text(f"Welcome, {user.get('username', '-')}", size=22, color=ft.Colors.WHITE),
            ft.Text(f"Role: {user.get('role', '-')}", color=ft.Colors.WHITE70),
            PrimaryButton("Logout", logout),
        ],
    )

    return ft.View(
        controls=[content],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )


app.run()
```

## Advanced Examples

### E-commerce Product Catalog

```python
import flet as ft
import flet_easy as fs
import json
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

app = fs.FletEasy()

# Small fetcher using a free API with images (Fake Store API)
def fetch_products():
    try:
        req = Request("https://fakestoreapi.com/products", headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        # Map to our shape
        return [
            {
                "id": it.get("id"),
                "name": it.get("title", ""),
                "price": float(it.get("price", 0)),
                "category": it.get("category", ""),
                "image": it.get("image", ""),
            }
            for it in data
        ]
    except (URLError, HTTPError, TimeoutError, ValueError):
        # Fallback to a minimal local list if API fails
        return [
            {"id": 1, "name": "Sample Shirt", "price": 19.99, "category": "clothing", "image": "https://picsum.photos/200?1"},
            {"id": 2, "name": "Sample Book", "price": 9.99, "category": "books", "image": "https://picsum.photos/200?2"},
        ]


# --- Small reusable UI components (classes) ---
class PillButton(ft.ElevatedButton):
    def __init__(self, text: str, on_click, color: str = ft.Colors.INDIGO_400):
        super().__init__(
            text,
            on_click=on_click,
            height=42,
            style=ft.ButtonStyle(
                bgcolor=color,
                color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=22),
                elevation=4,
            ),
        )


class ProductCard(ft.Card):
    def __init__(self, product: dict, on_add):
        price = f"${product['price']:.2f}"
        super().__init__(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Image(src=product.get("image", ""), height=120, fit=ft.ImageFit.CONTAIN),
                            height=130,
                            alignment=ft.alignment.center,
                            border_radius=10,
                            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                            bgcolor=ft.Colors.BLUE_GREY_900,
                        ),
                        ft.Text(product["name"], size=18, weight=ft.FontWeight.W_700, color=ft.Colors.WHITE),
                        ft.Text(price, size=16, color=ft.Colors.TEAL_200),
                        ft.Text(f"Category: {product['category']}", size=12, color=ft.Colors.GREY_400),
                        PillButton("Add to Cart", on_add, ft.Colors.INDIGO_400),
                    ],
                    spacing=6,
                ),
                padding=15,
                bgcolor=ft.Colors.BLUE_GREY_800,
                border=ft.border.all(1, ft.Colors.BLUE_GREY_700),
                border_radius=12,
            )
        )


class CartItemRow(ft.Row):
    def __init__(self, name: str, price: float, on_remove):
        super().__init__(
            controls=[
                ft.Text(name, size=16, weight=ft.FontWeight.W_500),
                ft.Text(f"${price:.2f}", color=ft.Colors.GREY_700),
                ft.Container(expand=True),
                ft.IconButton(ft.Icons.DELETE_OUTLINE, on_click=on_remove, icon_color=ft.Colors.RED_600),
            ]
        )


@app.page("/", title="Product Catalog", share_data=True)
def catalog_page(data: fs.Datasy):
    # Load products once and cache in shared data
    if not data.share.get("products"):
        products = fetch_products()
        data.share.set("products", products)

    def create_product_card(product):
        def add_to_cart(_):
            cart = data.share.get("cart") or []
            cart.append(product)
            data.share.set("cart", cart)
            # Live update cart button text
            cart_btn.text = f"Cart ({len(cart)})"
            cart_btn.update()
            data.page.open(
                ft.SnackBar(
                    content=ft.Text(f"Added {product['name']}", color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.GREEN_700,
                    show_close_icon=True,
                )
            )

        return ProductCard(product, add_to_cart)

    def view_cart(_):
        data.go("/cart")()

    products = data.share.get("products") or []
    cart_count = len(data.share.get("cart") or [])
    cart_btn = PillButton(f"Cart ({cart_count})", view_cart, ft.Colors.AMBER_500)

    return ft.View(
        controls=[
            ft.Container(
                content=ft.Row([
                    ft.Text("Product Catalog", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Container(expand=True),
                    cart_btn,
                ], alignment=ft.MainAxisAlignment.START),
                padding=14,
                border_radius=12,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.center_left,
                    end=ft.alignment.center_right,
                    colors=[ft.Colors.BLUE_GREY_900, ft.Colors.GREY_900],
                ),
            ),
            ft.Container(
                content=ft.GridView(
                    controls=[create_product_card(p) for p in products],
                    runs_count=2,
                    max_extent=320,
                    child_aspect_ratio=0.8,
                    spacing=10,
                    run_spacing=10,
                ),
                padding=10,
                bgcolor=ft.Colors.BLUE_GREY_900,
                border_radius=12,
            ),
        ],
        scroll=ft.ScrollMode.AUTO,
        bgcolor=ft.Colors.BLUE_GREY_900,
    )


@app.page("/cart", title="Shopping Cart", share_data=True)
def cart_page(data: fs.Datasy):
    cart = data.share.get("cart") or []

    def remove_item(index):
        def remove(_):
            cart.pop(index)
            data.share.set("cart", cart)
            data.page_reload()

        return remove

    def clear_cart(_):
        data.share.set("cart", [])
        data.page_reload()

    total = sum(item["price"] for item in cart)

    cart_items = []
    for i, item in enumerate(cart):
        cart_items.append(CartItemRow(item["name"], item["price"], remove_item(i)))

    return ft.View(
        controls=[
            ft.Container(
                content=ft.Row([
                    ft.IconButton(ft.Icons.ARROW_BACK, on_click=data.go("/")),
                    ft.Text("Shopping Cart", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ]),
                padding=14,
                border_radius=12,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.center_left,
                    end=ft.alignment.center_right,
                    colors=[ft.Colors.BLUE_GREY_900, ft.Colors.GREY_900],
                ),
            ),
            ft.Container(
                content=(ft.Column(cart_items) if cart_items else ft.Text("Cart is empty", color=ft.Colors.GREY_400)),
                padding=10,
                border_radius=12,
                bgcolor=ft.Colors.BLUE_GREY_800,
            ),
            ft.Row([
                ft.Text(f"Total: ${total:.2f}", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Container(expand=True),
                PillButton("Clear", clear_cart, ft.Colors.RED_400),
                PillButton("Checkout", lambda _: None, ft.Colors.INDIGO_400),
            ]),
        ],
        scroll=ft.ScrollMode.AUTO,
        bgcolor=ft.Colors.BLUE_GREY_900,
    )


app.run()
```

### Real-time Chat Application

```python
import flet as ft
import flet_easy as fs
from datetime import datetime

app = fs.FletEasy()

@app.page("/", title="Chat App", share_data=True)
def chat_page(data: fs.Datasy):
    messages = data.share.get("messages") or []
    username = data.page.client_storage.get("username") or "Anonymous"

    def sync_messages(msg: dict):
        messages.append(msg)
        data.share.set("messages", messages)
        message_input.value = ""
        update_chat()
        data.page.update()
        
        

    data.page.pubsub.subscribe(sync_messages)

    message_input = ft.TextField(
        hint_text="Type a message...",
        expand=True,
        on_submit=lambda _: send_message()
    )

    chat_container = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        height=400
    )

    def send_message():
        if message_input.value.strip():
            message = {
                "user": username,
                "text": message_input.value,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
            data.page.pubsub.send_all(message)

    def update_chat():
        chat_container.controls.clear()
        for msg in messages:
            is_own = msg["user"] == username
            chat_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            f"{msg['user']} - {msg['timestamp']}",
                            size=10,
                            color=ft.Colors.GREY_600
                        ),
                        ft.Text(msg["text"])
                    ]),
                    bgcolor=ft.Colors.BLUE_100 if is_own else ft.Colors.GREY_100,
                    padding=ft.padding.all(10),
                    margin=ft.margin.only(bottom=5),
                    border_radius=10,
                    alignment=ft.alignment.center_right if is_own else ft.alignment.center_left
                )
            )

    def change_username(_):
        def save_username(e):
            if username_field.value:
                data.page.client_storage.set("username", username_field.value)
                data.page_reload()  # Refresh page
            data.page.close(dialog)

        username_field = ft.TextField(
            label="Username",
            value=username
        )

        dialog = ft.AlertDialog(
            title=ft.Text("Change Username"),
            content=username_field,
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: data.page.close(dialog)),
                ft.TextButton("Save", on_click=save_username)
            ]
        )
        data.page.open(dialog)

    update_chat()

    return ft.View(
        controls=[
            ft.Row([
                ft.Text("Chat Room", size=24),
                ft.IconButton(
                    ft.Icons.PERSON,
                    tooltip="Change Username",
                    on_click=change_username
                )
            ]),
            ft.Text(f"Logged in as: {username}", size=12),
            chat_container,
            ft.Row([
                message_input,
                ft.IconButton(
                    ft.Icons.SEND,
                    on_click=lambda _: send_message()
                )
            ])
        ]
    )

app.run(view=ft.AppView.WEB_BROWSER)
```

## Responsive Design Examples

## More Examples

For additional examples and tutorials, visit:

- [GitHub Repository Examples](https://github.com/Daxexs/flet-easy/tree/main/tests)
- [Community Examples](https://github.com/Daxexs/flet-easy/discussions)
- [Video Tutorials](https://youtube.com/playlist?list=example)

Each example includes:

- Complete source code
- Step-by-step explanations
- Best practices
- Common pitfalls to avoid
- Extension ideas

Start with the basic examples and gradually work your way up to more complex applications as you become comfortable with Flet-Easy concepts.
