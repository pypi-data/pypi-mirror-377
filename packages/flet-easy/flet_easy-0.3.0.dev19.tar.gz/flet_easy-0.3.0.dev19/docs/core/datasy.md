# Datasy Object

The `Datasy` class is the central data management object in Flet-Easy that provides access to page data, routing functionality, authentication, and event handling. Every page function receives a `Datasy` instance as its first parameter.

## Overview

The `Datasy` object serves as your main interface for:

- **Page Access**: Direct access to Flet's Page object
- **URL Parameters**: Extract dynamic route parameters
- **Navigation**: Advanced routing and navigation methods
- **Authentication**: Login/logout functionality with JWT support
- **Data Sharing**: Session-based data sharing between pages
- **Event Handling**: Keyboard and resize event management
- **View Management**: Access to configured view templates

## Core Properties

### `page`

- **Type**: `ft.Page`
- **Description**: Direct access to the Flet Page object

```python
@app.page("/example")
def example_page(data: fs.Datasy):
    # Access page properties
    data.page.title = "My Page Title"
    data.page.window_width = 800
    data.page.window_height = 600
    data.page.update()
```

### `url_params`

- **Type**: `Dict[str, Any]`
- **Description**: Dictionary containing URL route parameters

```python
@app.page("/user/{id:d}/profile/{tab:str}")
def user_profile(data: fs.Datasy, id: int, tab: str):
    # Access via function parameters (recommended)
    user_id = id
    active_tab = tab
    
    # Or via url_params dictionary
    user_id = data.url_params["id"]
    active_tab = data.url_params["tab"]
```

### `view`

- **Type**: `fs.Viewsy`
- **Description**: Access to the configured global view template

```python
@app.page("/example")
def example_page(data: fs.Datasy):
    # Modify the global view
    data.view.appbar.title = ft.Text("New Title")
    data.view.appbar.bgcolor = ft.Colors.RED
    
    return ft.View(
        controls=[ft.Text("Content")],
        appbar=data.view.appbar,
        drawer=data.view.drawer
    )
```

### Route Properties

```python
# Access route configuration
data.route_prefix    # App route prefix
data.route_init      # Initial route
data.route_login     # Login redirect route
data.route           # Current route path
```

## Navigation Methods

### `go(route, clear_history=False)`

Navigate to a specific route with optional history clearing.

```python
@app.page("/home")
def home_page(data: fs.Datasy):
    return ft.View(
        controls=[
            ft.ElevatedButton(
                "Go to Profile",
                on_click=data.go("/profile")
            ),
            ft.ElevatedButton(
                "Go to Settings (Clear History)",
                on_click=data.go("/settings", clear_history=True)
            ),
            # Using lambda for event handlers
            ft.ElevatedButton(
                "Go to About",
                on_click=lambda _: data.go("/about")
            )
        ]
    )
```

### `go_back()`

Navigate to the previous route in history.

```python
@app.page("/details")
def details_page(data: fs.Datasy):
    return ft.View(
        controls=[
            ft.Text("Details Page"),
            ft.ElevatedButton(
                "Go Back",
                on_click=lambda _: data.go_back()
            )
        ]
    )
```

### `go_navigation_bar(index)`

Handle navigation bar changes for `ft.NavigationBar` or `ft.CupertinoNavigationBar`.

```python
@app.page("/main")
def main_page(data: fs.Datasy):
    # Define navigation destinations
    destinations = ["/home", "/search", "/profile"]
    
    def on_nav_change(e):
        data.go_navigation_bar(e.control.selected_index)
    
    return ft.View(
        controls=[
            ft.Text("Main Content"),
        ],
        navigation_bar=ft.NavigationBar(
            destinations=[
                ft.NavigationDestination(icon=ft.Icons.HOME, label="Home"),
                ft.NavigationDestination(icon=ft.Icons.SEARCH, label="Search"),
                ft.NavigationDestination(icon=ft.Icons.PERSON, label="Profile"),
            ],
            on_change=on_nav_change
        )
    )
```

### `history_routes`

- **Type**: `deque[Tuple[str, int]]`
- **Description**: Get navigation history as a deque of (route, timestamp) tuples

```python
@app.page("/debug")
def debug_page(data: fs.Datasy):
    history = data.history_routes
    history_text = "\n".join([f"{route} at {timestamp}" for route, timestamp in history])
    
    return ft.View(
        controls=[
            ft.Text("Navigation History:"),
            ft.Text(history_text),
        ]
    )
```

## Authentication Methods

### `login(key, value)`

Store authentication data in client storage.

```python
@app.page("/login")
def login_page(data: fs.Datasy):
    username_field = ft.TextField(label="Username")
    password_field = ft.TextField(label="Password", password=True)
    
    def handle_login(_):
        username = username_field.value
        password = password_field.value
        
        # Validate credentials (your logic here)
        if authenticate_user(username, password):
            # Store authentication token
            token = generate_jwt_token(username)
            data.login("auth_token", token)
            
            # Store additional user data
            data.login("user_id", get_user_id(username))
            data.login("username", username)
            
            # Redirect to protected area
            data.go("/dashboard")
        else:
            data.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Invalid credentials"))
            )
    
    return ft.View(
        controls=[
            ft.Text("Login", size=24),
            username_field,
            password_field,
            ft.ElevatedButton("Login", on_click=handle_login)
        ]
    )
```

### `logout(key_or_control)`

Remove authentication data from client storage.

```python
@app.page("/dashboard")
def dashboard_page(data: fs.Datasy):
    def handle_logout(_):
        # Remove specific keys
        data.logout("auth_token")
        data.logout("user_id")
        data.logout("username")
        
        # Redirect to login
        data.go("/login")
    
    def handle_full_logout(_):
        # Clear all client storage
        data.page.client_storage.clear()
        data.go("/login")
    
    return ft.View(
        controls=[
            ft.Text("Welcome to Dashboard"),
            ft.ElevatedButton("Logout", on_click=handle_logout),
            ft.ElevatedButton("Full Logout", on_click=handle_full_logout)
        ]
    )
```

## Data Sharing System

The `share` property provides enhanced session storage with additional methods.

### Basic Usage

```python
@app.page("/page1", share_data=True)
def page1(data: fs.Datasy):
    def save_data(_):
        # Store shared data
        data.share.set("user_preferences", {
            "theme": "dark",
            "language": "en"
        })
        data.share.set("cart_items", ["item1", "item2", "item3"])
        data.go("/page2")
    
    return ft.View(
        controls=[
            ft.Text("Page 1 - Set Data"),
            ft.ElevatedButton("Save & Go to Page 2", on_click=save_data)
        ]
    )

@app.page("/page2", share_data=True)
def page2(data: fs.Datasy):
    # Retrieve shared data
    preferences = data.share.get("user_preferences")
    cart_items = data.share.get("cart_items")
    
    return ft.View(
        controls=[
            ft.Text("Page 2 - Retrieved Data"),
            ft.Text(f"Theme: {preferences.get('theme') if preferences else 'None'}"),
            ft.Text(f"Cart Items: {len(cart_items) if cart_items else 0}"),
        ]
    )
```

### Enhanced Methods

```python
@app.page("/data-manager", share_data=True)
def data_manager_page(data: fs.Datasy):
    # Check if shared data exists
    has_data = data.share.contains()
    
    # Get all shared values as a list
    all_values = data.share.get_values()
    
    # Get complete shared data dictionary
    all_data = data.share.get_all()
    
    return ft.View(
        controls=[
            ft.Text(f"Has shared data: {has_data}"),
            ft.Text(f"Number of values: {len(all_values)}"),
            ft.Text(f"All keys: {list(all_data.keys())}"),
        ]
    )
```

## Event Handling

### Keyboard Events

```python
@app.page("/keyboard-demo")
def keyboard_demo(data: fs.Datasy):
    output_text = ft.Text("Press any key...")
    
    # Add keyboard event handler
    def handle_keyboard():
        key_info = data.on_keyboard_event.test()  # Get all key info
        key = data.on_keyboard_event.key()
        shift = data.on_keyboard_event.shift()
        ctrl = data.on_keyboard_event.ctrl()
        alt = data.on_keyboard_event.alt()
        meta = data.on_keyboard_event.meta()
        
        output_text.value = f"Key: {key}, Shift: {shift}, Ctrl: {ctrl}, Alt: {alt}, Meta: {meta}"
        data.page.update()
    
    # Register the handler
    data.on_keyboard_event.add_control(handle_keyboard)
    
    return ft.View(
        controls=[
            ft.Text("Keyboard Event Demo"),
            output_text,
        ]
    )
```

### Resize Events

```python
@app.page("/resize-demo")
def resize_demo(data: fs.Datasy):
    size_text = ft.Text("Resize the window...")
    
    def handle_resize():
        width = data.on_resize.width()
        height = data.on_resize.height()
        size_text.value = f"Window size: {width}x{height}"
        data.page.update()
    
    # Register resize handler
    data.on_resize.add_control(handle_resize)
    
    return ft.View(
        controls=[
            ft.Text("Resize Event Demo"),
            size_text,
        ]
    )
```

## Advanced Usage Examples

### Dynamic Content Based on Authentication

```python
@app.page("/profile")
def profile_page(data: fs.Datasy):
    # Check authentication status
    auth_token = data.page.client_storage.get("auth_token")
    username = data.page.client_storage.get("username")
    
    if auth_token:
        # Authenticated user content
        controls = [
            ft.Text(f"Welcome, {username}!", size=24),
            ft.ElevatedButton(
                "Edit Profile",
                on_click=data.go("/profile/edit")
            ),
            ft.ElevatedButton(
                "Logout",
                on_click=lambda _: [
                    data.logout("auth_token"),
                    data.logout("username"),
                    data.go("/login")
                ]
            )
        ]
    else:
        # Guest user content
        controls = [
            ft.Text("Please log in to view your profile"),
            ft.ElevatedButton(
                "Login",
                on_click=data.go("/login")
            )
        ]
    
    return ft.View(controls=controls)
```

### Responsive Design with Resize Events

```python
@app.page("/responsive")
def responsive_page(data: fs.Datasy):
    content_container = ft.Container()
    
    def update_layout():
        if data.on_resize:
            width = data.on_resize.width()
            
            if width < 600:
                # Mobile layout
                content_container.content = ft.Column([
                    ft.Text("Mobile Layout"),
                    ft.ElevatedButton("Button 1"),
                    ft.ElevatedButton("Button 2"),
                ], tight=True)
            elif width < 1200:
                # Tablet layout
                content_container.content = ft.Row([
                    ft.Column([
                        ft.Text("Tablet Layout"),
                        ft.ElevatedButton("Button 1"),
                    ], expand=1),
                    ft.Column([
                        ft.ElevatedButton("Button 2"),
                    ], expand=1),
                ])
            else:
                # Desktop layout
                content_container.content = ft.Row([
                    ft.Container(ft.Text("Sidebar"), width=200, bgcolor=ft.Colors.GREY_200),
                    ft.Column([
                        ft.Text("Desktop Layout"),
                        ft.Row([
                            ft.ElevatedButton("Button 1"),
                            ft.ElevatedButton("Button 2"),
                        ])
                    ], expand=1),
                ])
            
            data.page.update()
    
    # Set initial layout
    update_layout()
    
    # Register resize handler
    data.on_resize.add_control(update_layout)
    
    return ft.View(controls=[content_container])
```

### Form Handling with Validation

```python
@app.page("/contact")
def contact_page(data: fs.Datasy):
    name_field = ft.TextField(label="Name", hint_text="Enter your full name")
    email_field = ft.TextField(label="Email", hint_text="Enter your email")
    message_field = ft.TextField(
        label="Message",
        multiline=True,
        min_lines=3,
        max_lines=5
    )
    status_text = ft.Text()
    
    def validate_form():
        errors = []
        
        if not name_field.value or len(name_field.value.strip()) < 2:
            errors.append("Name must be at least 2 characters")
        
        if not email_field.value or "@" not in email_field.value:
            errors.append("Please enter a valid email")
        
        if not message_field.value or len(message_field.value.strip()) < 10:
            errors.append("Message must be at least 10 characters")
        
        return errors
    
    def submit_form(_):
        errors = validate_form()
        
        if errors:
            status_text.value = "Errors:\n" + "\n".join(errors)
            status_text.color = ft.Colors.RED
        else:
            # Store form data in shared storage
            data.share.set("contact_form", {
                "name": name_field.value,
                "email": email_field.value,
                "message": message_field.value,
                "timestamp": datetime.now().isoformat()
            })
            
            status_text.value = "Form submitted successfully!"
            status_text.color = ft.Colors.GREEN
            
            # Clear form
            name_field.value = ""
            email_field.value = ""
            message_field.value = ""
        
        data.page.update()
    
    return ft.View(
        controls=[
            ft.Text("Contact Form", size=24),
            name_field,
            email_field,
            message_field,
            ft.ElevatedButton("Submit", on_click=submit_form),
            status_text,
        ]
    )
```

## Best Practices

### 1. **Navigation Patterns**

```python
# Use lambda for simple navigation
ft.ElevatedButton("Home", on_click=data.go("/home"))

# Use functions for complex navigation logic
def handle_navigation(_):
    if user_has_permission():
        data.go("/admin")
    else:
        data.go("/unauthorized")

ft.ElevatedButton("Admin", on_click=handle_navigation)
```

### 2. **State Management**

```python
# Use shared data for temporary state
data.share.set("form_draft", form_data)

# Use client storage for persistent state
data.page.client_storage.set("user_preferences", preferences)
```

### 3. **Performance Optimization**

```python
# Batch page updates
def update_multiple_controls():
    control1.value = "New Value 1"
    control2.value = "New Value 2"
    control3.value = "New Value 3"
    data.page.update()  # Single update call
```

The `Datasy` object is your primary interface for building interactive Flet-Easy applications. Master these methods and properties to create powerful, responsive applications with excellent user experience.
