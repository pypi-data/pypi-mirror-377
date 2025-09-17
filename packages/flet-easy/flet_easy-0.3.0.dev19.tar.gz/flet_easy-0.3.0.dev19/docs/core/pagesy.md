# Page Management (Pagesy)

The `Pagesy` class is the foundation for defining pages in Flet-Easy applications. It provides comprehensive configuration options for routing, middleware, authentication, caching, and parameter validation.

## Overview

`Pagesy` enables you to:

- **Define Routes**: Create URL patterns with dynamic parameters
- **Configure Security**: Set up route protection and authentication
- **Add Middleware**: Implement request/response processing
- **Enable Caching**: Preserve page state during navigation
- **Validate Parameters**: Custom validation for route parameters
- **Share Data**: Enable cross-page data sharing

## Class Definition

```python
class Pagesy:
    def __init__(
        self,
        route: str,
        view: ViewHandler,
        title: Optional[str] = None,
        index: Optional[int] = None,
        clear: bool = False,
        share_data: bool = False,
        protected_route: bool = False,
        custom_params: Optional[Dict[str, Callable[[], bool]]] = None,
        middleware: Optional[Middleware] = None,
        cache: bool = False
    )
```

## Parameters

### `route` (Required)

- **Type**: `str`
- **Description**: URL pattern for the page, supports dynamic parameters

**Static Routes:**

```python
# Simple static route
Pagesy("/home", home_view)
Pagesy("/about", about_view)
Pagesy("/contact", contact_view)
```

**Dynamic Routes:**

```python
# Integer parameter
Pagesy("/user/{id:int}", user_view)

# String parameter
Pagesy("/category/{name:str}", category_view)

# Multiple parameters
Pagesy("/blog/{year:int}/{month:int}/{slug:str}", blog_post_view)

# Optional parameters with defaults
Pagesy("/search/{query:str}/{page:int}", search_view)
```

**Parameter Types:**

- `{name:int}` - Integer
- `{name:str}` - String
- `{name:str}` - Lowercase string
- `{name:float}` - Float

### `view` (Required)

- **Type**: `ViewHandler` (Callable[[Datasy], View])
- **Description**: Function that returns a Flet View

```python
def my_page_view(data: fs.Datasy) -> ft.View:
    return ft.View(
        controls=[
            ft.Text("Hello World!")
        ]
    )

# Register the page
page = Pagesy("/my-page", my_page_view)
```

### `title`

- **Type**: `Optional[str]`
- **Default**: `None`
- **Description**: Page title displayed in browser/window title bar

```python
Pagesy("/dashboard", dashboard_view, title="User Dashboard")
Pagesy("/settings", settings_view, title="Application Settings")
```

### `index`

- **Type**: `Optional[int]`
- **Default**: `None`
- **Description**: Navigation index for use with NavigationBar controls

```python
# Define pages with navigation indices
Pagesy("/home", home_view, index=0)
Pagesy("/search", search_view, index=1)
Pagesy("/profile", profile_view, index=2)

# Use in NavigationBar
navigation_bar = ft.NavigationBar(
    selected_index=data.current_page_index,  # Use the index
    destinations=[
        ft.NavigationDestination(icon=ft.Icons.HOME, label="Home"),
        ft.NavigationDestination(icon=ft.Icons.SEARCH, label="Search"),
        ft.NavigationDestination(icon=ft.Icons.PERSON, label="Profile"),
    ]
)
```

### `clear`

- **Type**: `bool`
- **Default**: `False`
- **Description**: Clears navigation history when navigating to this page

```python
# Clear history for main landing pages
Pagesy("/home", home_view, clear=True)
Pagesy("/login", login_view, clear=True)

# Preserve history for detail pages
Pagesy("/user/{id:int}", user_detail_view, clear=False)
```

### `share_data`

- **Type**: `bool`
- **Default**: `False`
- **Description**: Enables data sharing between pages using session storage

```python
# Enable data sharing for form wizard pages
Pagesy("/wizard/step1", step1_view, share_data=True)
Pagesy("/wizard/step2", step2_view, share_data=True)
Pagesy("/wizard/step3", step3_view, share_data=True)

def step1_view(data: fs.Datasy):
    def save_and_continue(_):
        # Save form data
        data.share.set("user_info", {
            "name": name_field.value,
            "email": email_field.value
        })
        data.go("/wizard/step2")
    
    return ft.View("/wizard/step1", controls=[...])

def step2_view(data: fs.Datasy):
    # Access data from step1
    user_info = data.share.get("user_info")
    return ft.View("/wizard/step2", controls=[...])
```

### `protected_route`

- **Type**: `bool`
- **Default**: `False`
- **Description**: Requires authentication to access the page

```python
# Public pages
Pagesy("/home", home_view, protected_route=False)
Pagesy("/login", login_view, protected_route=False)

# Protected pages
Pagesy("/dashboard", dashboard_view, protected_route=True)
Pagesy("/admin", admin_view, protected_route=True)
Pagesy("/user/{id:int}/edit", edit_user_view, protected_route=True)

# Configure authentication handler in FletEasy
@app.login
def check_auth(data: fs.Datasy):
    token = data.page.client_storage.get("auth_token")
    return token is not None and verify_token(token)
```

### `custom_params`

- **Type**: `Optional[Dict[str, Callable[[], bool]]]`
- **Default**: `None`
- **Description**: Custom validators for route parameters

```python
def validate_user_id(user_id: str) -> bool:
    """Validate that user ID exists in database"""
    return user_exists(int(user_id))

def validate_email(email: str) -> bool:
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_date(date_str: str) -> bool:
    """Validate date format YYYY-MM-DD"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

# Apply custom validators
Pagesy(
    "/user/{id:id_profile}/profile",
    user_profile_view,
    custom_params={"id_profile": validate_user_id}
)

Pagesy(
    "/contact/{email:email_contact}",
    contact_view,
    custom_params={"email_contact": validate_email}
)

Pagesy(
    "/events/{date:date_event}",
    events_view,
    custom_params={"date_event": validate_date}
)
```

### `middleware`

- **Type**: `Optional[Middleware]`
- **Description**: Request/response processing pipeline

**Function-based Middleware:**

```python
def auth_middleware(data: fs.Datasy) -> Optional[fs.Redirect]:
    """Check if user is authenticated"""
    if not data.page.client_storage.get("auth_token"):
        return fs.Redirect("/login")
    return None

def admin_middleware(data: fs.Datasy) -> Optional[fs.Redirect]:
    """Check if user has admin privileges"""
    user_role = data.page.client_storage.get("user_role")
    if user_role != "admin":
        return fs.Redirect("/unauthorized")
    return None

# Apply middleware
Pagesy(
    "/admin/users",
    admin_users_view,
    middleware=[auth_middleware, admin_middleware]
)
```

**Class-based Middleware:**

```python
class LoggingMiddleware(fs.MiddlewareRequest):
    def before_request(self):
        print(f"Accessing route: {self.data.route}")
        # Log request details
        
    def after_request(self):
        print(f"Finished processing: {self.data.route}")
        # Log response details

class RateLimitMiddleware(fs.MiddlewareRequest):
    def before_request(self):
        user_id = self.data.page.client_storage.get("user_id")
        if is_rate_limited(user_id):
            return fs.Redirect("/rate-limited")

# Apply class-based middleware
Pagesy(
    "/api/data",
    api_data_view,
    middleware=[LoggingMiddleware, RateLimitMiddleware]
)
```

### `cache`

- **Type**: `bool`
- **Default**: `False`
- **Description**: Preserves page state during navigation

```python
# Cache expensive-to-render pages
Pagesy("/reports/dashboard", title="Dashboard", view=reports_view, cache=True)
Pagesy("/data/visualization", title="Visualization", view=charts_view, cache=True)

# Don't cache dynamic pages
Pagesy("/live/feed", title="Live Feed", view=live_feed_view, cache=False)
Pagesy("/user/{id:int}/messages", title="Messages", view=messages_view, cache=False)

def reports_view(data: fs.Datasy):
    # This page state will be preserved when user navigates away and back
    expensive_chart = generate_complex_chart()
    
    return ft.View(
        controls=[expensive_chart]
    )
```

## Complete Examples

### E-commerce Product Page

```python
def validate_product_id(product_id: str) -> bool:
    """Validate product exists and is active"""
    return product_exists(int(product_id)) and product_is_active(int(product_id))

def product_analytics_middleware(data: fs.Datasy) -> Optional[fs.Redirect]:
    """Track product views"""
    product_id = data.url_params.get("id")
    if product_id:
        track_product_view(product_id, data.page.client_storage.get("user_id"))
    return None

def product_view(data: fs.Datasy, id: int):
    product = get_product(id)
    
    def add_to_cart(_):
        cart = data.share.get("cart") or []
        cart.append({"product_id": id, "quantity": 1})
        data.share.set("cart", cart)
        
        data.page.show_snack_bar(
            ft.SnackBar(content=ft.Text("Added to cart!"))
        )
    
    return ft.View(
        controls=[
            ft.Text(product.name, size=24),
            ft.Text(f"${product.price}", size=20),
            ft.Text(product.description),
            ft.ElevatedButton("Add to Cart", on_click=add_to_cart),
            ft.ElevatedButton("Back to Products", on_click=data.go("/products"))
        ]
    )

# Register the product page
product_page = Pagesy(
    route="/product/{id:int}",
    view=product_view,
    title="Product Details",
    share_data=True,  # Enable cart sharing
    custom_params={"id": validate_product_id},
    middleware=[product_analytics_middleware],
    cache=True  # Cache product details
)
```

### User Profile with Authentication

```python
class UserAccessMiddleware(fs.MiddlewareRequest):
    def before_request(self):
        # Check if user can access this profile
        current_user_id = self.data.page.client_storage.get("user_id")
        requested_user_id = self.data.url_params.get("id")
        
        if not current_user_id:
            return fs.Redirect("/login")
        
        # Users can only access their own profile unless they're admin
        user_role = self.data.page.client_storage.get("user_role")
        if str(current_user_id) != str(requested_user_id) and user_role != "admin":
            return fs.Redirect("/unauthorized")

def user_profile_view(data: fs.Datasy, id: int):
    user = get_user(id)
    current_user_id = data.page.client_storage.get("user_id")
    is_own_profile = str(current_user_id) == str(id)
    
    controls = [
        ft.Text(f"Profile: {user.name}", size=24),
        ft.Text(f"Email: {user.email}"),
        ft.Text(f"Joined: {user.created_at.strftime('%Y-%m-%d')}"),
    ]
    
    if is_own_profile:
        controls.extend([
            ft.Divider(),
            ft.ElevatedButton(
                "Edit Profile",
                on_click=data.go(f"/user/{id}/edit")
            ),
            ft.ElevatedButton(
                "Change Password",
                on_click=data.go(f"/user/{id}/password")
            )
        ])
    
    return ft.View(controls=controls)

# Register user profile page
user_profile_page = Pagesy(
    route="/user/{id:int}",
    view=user_profile_view,
    title="User Profile",
    middleware=[UserAccessMiddleware]
)
```

### Multi-step Form with Data Sharing

```python
# Step 1: Personal Information
def step1_view(data: fs.Datasy):
    # Load existing data if returning to this step
    form_data = data.share.get("registration_form") or {}
    
    name_field = ft.TextField(
        label="Full Name",
        value=form_data.get("name", "")
    )
    email_field = ft.TextField(
        label="Email",
        value=form_data.get("email", "")
    )
    phone_field = ft.TextField(
        label="Phone",
        value=form_data.get("phone", "")
    )
    
    def save_and_continue(_):
        # Validate fields
        if not name_field.value or not email_field.value:
            data.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Please fill all required fields"))
            )
            return
        
        # Save form data
        form_data = data.share.get("registration_form") or {}
        form_data.update({
            "name": name_field.value,
            "email": email_field.value,
            "phone": phone_field.value
        })
        data.share.set("registration_form", form_data)
        
        # Go to next step
        data.go("/register/step2")()
    
    return ft.View(
        controls=[
            ft.Text("Registration - Step 1", size=24),
            ft.Text("Personal Information", size=16),
            name_field,
            email_field,
            phone_field,
            ft.Row([
                ft.ElevatedButton("Next", on_click=save_and_continue),
            ])
        ]
    )

# Step 2: Address Information
def step2_view(data: fs.Datasy):
    form_data = data.share.get("registration_form") or {}
    
    # Redirect if step 1 not completed
    if not form_data.get("name"):
        data.go("/register/step1")()
        return ft.View("/register/step2", controls=[])
    
    address_field = ft.TextField(
        label="Address",
        value=form_data.get("address", "")
    )
    city_field = ft.TextField(
        label="City",
        value=form_data.get("city", "")
    )
    
    def save_and_continue(_):
        form_data = data.share.get("registration_form", {})
        form_data.update({
            "address": address_field.value,
            "city": city_field.value
        })
        data.share.set("registration_form", form_data)
        data.go("/register/step3")()
    
    def go_back(_):
        # Save current data before going back
        form_data = data.share.get("registration_form", {})
        form_data.update({
            "address": address_field.value,
            "city": city_field.value
        })
        data.share.set("registration_form", form_data)
        data.go("/register/step1")()
    
    return ft.View(
        controls=[
            ft.Text("Registration - Step 2", size=24),
            ft.Text("Address Information", size=16),
            address_field,
            city_field,
            ft.Row([
                ft.ElevatedButton("Back", on_click=go_back),
                ft.ElevatedButton("Next", on_click=save_and_continue),
            ])
        ]
    )

# Register form steps
step1_page = Pagesy(
    step1_view,
    title="Registration - Personal Info",
    share_data=True,
    clear=True  # Clear history when starting registration
)

step2_page = Pagesy(
    "/register/step2",
    step2_view,
    title="Registration - Address",
    share_data=True
)
```

## Best Practices

### 1. **Route Organization**

```python
# Group related routes with common prefixes
Pagesy("/admin/users",  title="Admin Users", view=admin_users_view, protected_route=True)
Pagesy("/admin/settings", title="Admin Settings", view=admin_settings_view, protected_route=True)
Pagesy("/admin/reports", title="Admin Reports", view=admin_reports_view, protected_route=True)

# Use consistent parameter naming
Pagesy("/user/{id:int}/profile", title="User Profile", view=user_profile_view)
Pagesy("/user/{id:int}/settings", title="User Settings", view=user_settings_view)
Pagesy("/user/{id:int}/orders", title="User Orders", view=user_orders_view)
```

### 2. **Security Configuration**

```python
# Always protect sensitive routes
Pagesy("/admin/*", title="Admin", view=admin_view, protected_route=True)
Pagesy("/user/{id:int}/private", title="User Private", view=private_view, protected_route=True)

# Use middleware for complex authorization
class AdminOnlyMiddleware(fs.MiddlewareRequest):
    def before_request(self):
        if self.data.page.client_storage.get("role") != "admin":
            return fs.Redirect("/unauthorized")
```

### 3. **Performance Optimization**

```python
# Cache static or expensive pages
Pagesy("/reports", title="Reports", view=reports_view, cache=True)

# Don't cache dynamic content
Pagesy("/live-chat", title="Live Chat", view=chat_view, cache=False)

# Clear history for major navigation points
Pagesy("/dashboard", title="Dashboard", view=dashboard_view, clear=True)
```

### 4. **User Experience**

```python
# Use descriptive titles
Pagesy("/checkout", title="Checkout - Complete Your Order", view=checkout_view)

# Enable data sharing for multi-step processes
Pagesy("/wizard/step1", title="Wizard Step 1", view=step1_view, share_data=True)
Pagesy("/wizard/step2", title="Wizard Step 2", view=step2_view, share_data=True)

# Set navigation indices for tab-like interfaces
Pagesy("/home", title="Home", view=home_view, index=0)
Pagesy("/search", title="Search", view=search_view, index=1)
```

The `Pagesy` class provides the foundation for creating sophisticated, secure, and user-friendly page routing in Flet-Easy applications. Use these features to build robust navigation systems that enhance your application's functionality and user experience.
