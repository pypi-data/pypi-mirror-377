"""
Scene Registration for {{ project_name_upper }} project.

Register your custom scenes here using the @register decorator.

Example:

Registering Scene On Creation.

    ```python
    from xodex.scenes.manager import register
    from xodex.scenes import Scene

    # Register a menu scene with default name (class name)
    @register
    class MenuScene(Scene):
        ...

    # Register a scene with a custom name
    @register(name="main_menu")
    class MenuScene(Scene):
        ...
    ```

Registering Existing Scene.

    ```python
    from xodex.scenes.manager import register
    from .menu_scene import MenuScene

    # Register a menu scene with default name (class name)
    register(MenuScene)

    # Register a scene with a custom name
    register(MenuScene,name="main_menu")
    ```

How it works:
- The @register decorator adds your scene class to the global registry.
- You can then instantiate or reference these scenes by name in your game flow.
- Use inheritance to create custom scene logic, transitions, and layouts.

See the Xodex documentation for more advanced scene management and transitions.
"""

from xodex.scenes.manager import register

# Register your {{ project_name }} Scenes here.
