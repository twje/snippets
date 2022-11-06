"""
todo: 
- Use Hazel renderer instead of ProgrammablePipelineRenderer
- Remove 'glfw' dependency
- Remove 'glViewport' call
reference implementation: imgui.integrations.glfw.GlfwRenderer
"""

from typing import TYPE_CHECKING
from .application import Application
from .layer import Layer
from .events import EventDispatcher
from .events import MouseButtonPressedEvent
from .events import MouseButtonReleasedEvent
from .events import MouseMovedEvent
from .events import MouseScrolledEvent
from .events import KeyPressedEvent
from .events import KeyReleasedEvent
from .events import KeyTypedEvent
from .events import WindowResizeEvent
from OpenGL.GL import glViewport
import imgui


# temporary
from imgui.integrations.glfw import ProgrammablePipelineRenderer
import glfw


if TYPE_CHECKING:
    from .events import Event

__all__ = ["ImGuiLayer"]


class ImGuiRenderer(ProgrammablePipelineRenderer):
    def __init__(self, app: Application):
        super().__init__()
        self.app = app

        self._map_keys()
        self._gui_time = None

    def _map_keys(self):
        # Backend platform support
        self.io.backend_flags |= imgui.BACKEND_HAS_MOUSE_CURSORS
        self.io.backend_flags |= imgui.BACKEND_HAS_SET_MOUSE_POS

        # TEMPORARY: should eventually use Hazel key codes
        key_map = self.io.key_map
        key_map[imgui.KEY_TAB] = glfw.KEY_TAB
        key_map[imgui.KEY_LEFT_ARROW] = glfw.KEY_LEFT
        key_map[imgui.KEY_RIGHT_ARROW] = glfw.KEY_RIGHT
        key_map[imgui.KEY_UP_ARROW] = glfw.KEY_UP
        key_map[imgui.KEY_DOWN_ARROW] = glfw.KEY_DOWN
        key_map[imgui.KEY_PAGE_UP] = glfw.KEY_PAGE_UP
        key_map[imgui.KEY_PAGE_DOWN] = glfw.KEY_PAGE_DOWN
        key_map[imgui.KEY_HOME] = glfw.KEY_HOME
        key_map[imgui.KEY_END] = glfw.KEY_END
        key_map[imgui.KEY_DELETE] = glfw.KEY_DELETE
        key_map[imgui.KEY_BACKSPACE] = glfw.KEY_BACKSPACE
        key_map[imgui.KEY_ENTER] = glfw.KEY_ENTER
        key_map[imgui.KEY_ESCAPE] = glfw.KEY_ESCAPE
        key_map[imgui.KEY_A] = glfw.KEY_A
        key_map[imgui.KEY_C] = glfw.KEY_C
        key_map[imgui.KEY_V] = glfw.KEY_V
        key_map[imgui.KEY_X] = glfw.KEY_X
        key_map[imgui.KEY_Y] = glfw.KEY_Y
        key_map[imgui.KEY_Z] = glfw.KEY_Z

    def update(self):
        self.io.display_size = [self.app.window.width, self.app.window.height]

        current_time = glfw.get_time()
        if self._gui_time:
            self.io.delta_time = current_time - self._gui_time
        else:
            self.io.delta_time = 1. / 60.

        self._gui_time = current_time

    def on_event(self, event: "Event"):
        dispatcher = EventDispatcher(event)

        dispatcher.dispatch(
            MouseButtonPressedEvent,
            self._on_mouse_button_pressed_event
        )
        dispatcher.dispatch(
            MouseButtonReleasedEvent,
            self._on_mouse_button_released_event
        )
        dispatcher.dispatch(
            MouseMovedEvent,
            self._on_mouse_moved_event
        )
        dispatcher.dispatch(
            MouseScrolledEvent,
            self._on_mouse_scrolled_event
        )
        dispatcher.dispatch(
            KeyPressedEvent,
            self._on_key_pressed_event
        )
        dispatcher.dispatch(
            KeyReleasedEvent,
            self._on_key_released_event
        )
        dispatcher.dispatch(
            KeyTypedEvent,
            self._on_key_typed_event
        )
        dispatcher.dispatch(
            WindowResizeEvent,
            self._on_window_resize_event
        )

    def _on_mouse_button_pressed_event(self, event: MouseButtonPressedEvent) -> bool:
        self.io.mouse_down[event.button] = True
        return False

    def _on_mouse_button_released_event(self, event: MouseButtonReleasedEvent) -> bool:
        self.io.mouse_down[event.button] = False
        return False

    def _on_mouse_moved_event(self, event: MouseMovedEvent) -> bool:
        self.io.mouse_pos = (event.mouse_x, event.mouse_y)
        return False

    def _on_mouse_scrolled_event(self, event: MouseScrolledEvent) -> bool:
        self.io.mouse_wheel_horizontal += event.x_offset
        self.io.mouse_wheel += event.y_offset
        return False

    def _on_key_pressed_event(self, event: KeyPressedEvent) -> bool:
        self.io.keys_down[event.keycode] = True

        self.io.key_ctrl = self.io.keys_down[glfw.KEY_LEFT_CONTROL] or self.io.keys_down[glfw.KEY_RIGHT_CONTROL]
        self.io.key_shift = self.io.keys_down[glfw.KEY_LEFT_SHIFT] or self.io.keys_down[glfw.KEY_RIGHT_SHIFT]
        self.io.key_alt = self.io.keys_down[glfw.KEY_LEFT_ALT] or self.io.keys_down[glfw.KEY_RIGHT_ALT]
        self.io.key_super = self.io.keys_down[glfw.KEY_LEFT_SUPER] or self.io.keys_down[glfw.KEY_RIGHT_SUPER]
        return False

    def _on_key_released_event(self, event: KeyReleasedEvent) -> bool:
        self.io.keys_down[event.keycode] = False
        return False

    def _on_key_typed_event(self, event: KeyTypedEvent) -> bool:
        keycode = event.keycode
        if keycode > 0 and keycode < 0x10000:
            self.io.add_input_character(keycode)
        return False

    def _on_window_resize_event(self, event: WindowResizeEvent) -> bool:
        size = (event.width, event.height)
        self.io.display_size = size
        self.io.display_fb_scale = (1, 1)
        glViewport(0, 0, size[0], size[1])
        return False


class ImGuiLayer(Layer):
    def __init__(self) -> None:
        super().__init__("ImGuiLayer")
        self.renderer: ImGuiRenderer = None

    def destroy(self):
        pass

    def on_attach(self):
        imgui.create_context()
        imgui.style_colors_dark()
        self.renderer = ImGuiRenderer(Application.instance)

    def on_detach(self):
        self.renderer.shutdown()
        imgui.destroy_context()

    def on_update(self):
        self.renderer.update()
        imgui.new_frame()
        imgui.show_demo_window()
        imgui.render()
        self.renderer.render(imgui.get_draw_data())

    def on_event(self, event: "Event"):
        self.renderer.on_event(event)
