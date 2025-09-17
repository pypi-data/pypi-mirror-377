from typing import Iterable, Tuple, Any, Iterator
import numbers
import random


class Color:
    RGB_MIN = 0
    RGB_MAX = 255

    def __init__(self, *args):
        if len(args) == 0:
            # Default to black
            self._r, self._g, self._b = 0, 0, 0
        elif len(args) == 1:
            self._init_single_arg(args[0])
        elif len(args) == 3:
            self._init_three_args(*args)
        else:
            raise ValueError(f"Color() takes 0, 1, or 3 arguments ({len(args)} given)")

    def _init_single_arg(self, arg):
        if isinstance(arg, Color):
            # Copy constructor
            self._r, self._g, self._b = arg._r, arg._g, arg._b
        elif isinstance(arg, str):
            # Parse string like "255,128,0"
            self._init_str(arg)
        elif hasattr(arg, "__iter__") and not isinstance(arg, (str, bytes)):
            # Handle iterables (list, tuple, etc.)
            self._init_iter(arg)
        else:
            raise TypeError(f"Cannot initialize Color from {type(arg).__name__}")

    def _init_str(self, color_str: str):
        try:
            values = [int(x.strip()) for x in color_str.split(",")]
            if len(values) != 3:
                raise ValueError("String must contain exactly 3 comma-separated values")
            self._init_three_args(*values)
        except ValueError as e:
            raise ValueError(f"Invalid Color string format: {e}")

    def _init_iter(self, iterable):
        try:
            values = list(iterable)
            if len(values) != 3:
                raise ValueError(
                    f"Iterable must contain exactly 3 values, got {len(values)}"
                )
            self._init_three_args(*values)
        except TypeError:
            raise TypeError("Argument must be iterable")

    def _init_three_args(self, r, g, b):
        self._r = self._validate_color_value(r, "red")
        self._g = self._validate_color_value(g, "green")
        self._b = self._validate_color_value(b, "blue")

    def _validate_color_value(self, value: Any, color_name: str = "color") -> int:
        """Validate and convert color value to integer in range [0, 255]."""
        if not isinstance(value, numbers.Real):
            raise TypeError(
                f"{color_name} value must be numeric, got {type(value).__name__}"
            )

        int_value = int(value)

        if not (self.RGB_MIN <= int_value <= self.RGB_MAX):
            raise ValueError(
                f"{color_name} value must be in range [{self.RGB_MIN}, {self.RGB_MAX}], got {int_value}"
            )

        return int_value

    def _get_component(self, char: str) -> int:
        """Get color component by swizzle character (r/g/b)."""
        if char == "r":
            return self._r
        elif char == "g":
            return self._g
        elif char == "b":
            return self._b
        else:
            raise ValueError(f"Invalid swizzle character: {char}")

    def _set_component(self, char: str, value: int):
        """Set color component by swizzle character (r/g/b)."""
        validated_value = self._validate_color_value(value, char)
        if char == "r":
            self._r = validated_value
        elif char == "g":
            self._g = validated_value
        elif char == "b":
            self._b = validated_value
        else:
            raise ValueError(f"Invalid swizzle character: {char}")

    def __getattr__(self, name: str):
        """Handle GLSL-style swizzling access like .rgb, .rg, .gbr, etc."""
        if all(c in "rgb" for c in name):
            if len(name) == 1:
                return self._get_component(name)
            else:
                return tuple(self._get_component(c) for c in name)
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def __setattr__(self, name: str, value):
        """Handle GLSL-style swizzling assignment like .rgb = (255, 128, 0)."""
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return

        if all(c in "rgb" for c in name):
            if len(name) == 1:
                # Single component assignment: .r = 255
                self._set_component(name, value)
            else:
                # Multi-component assignment: .rgb = (255, 128, 0)
                if not hasattr(value, "__iter__") or isinstance(value, (str, bytes)):
                    raise TypeError(
                        f"Cannot assign {type(value).__name__} to swizzle pattern '{name}'"
                    )

                values = list(value)
                if len(values) != len(name):
                    raise ValueError(
                        f"Cannot assign {len(values)} values to {len(name)} components"
                    )

                for char, val in zip(name, values):
                    self._set_component(char, val)
        else:
            object.__setattr__(self, name, value)

    # === PROPERTIES ===
    @property
    def r(self) -> int:
        """Red component (0–255)."""
        return self._r

    @property
    def g(self) -> int:
        """Green component (0–255)."""
        return self._g

    @property
    def b(self) -> int:
        """Blue component (0–255)."""
        return self._b

    @property
    def rgb(self) -> "Color":
        """RGB values as a tuple."""
        return Color(self._r, self._g, self._b)

    @r.setter
    def r(self, value: int):
        self._r = self._validate_color_value(value, "red")

    @g.setter
    def g(self, value: int):
        self._g = self._validate_color_value(value, "green")

    @b.setter
    def b(self, value: int):
        self._b = self._validate_color_value(value, "blue")

    @rgb.setter
    def rgb(self, value: Iterable[int]):
        values = list(value)
        if len(values) != 3:
            raise ValueError(f"Color requires exactly 3 values, got {len(values)}")
        self._r, self._g, self._b = [
            self._validate_color_value(v, ["red", "green", "blue"][i])
            for i, v in enumerate(values)
        ]

    # === CONVERSIONS ===
    def to_hex(self) -> str:
        """Convert to hex string (#RRGGBB)."""
        return f"#{self._r:02x}{self._g:02x}{self._b:02x}"

    @classmethod
    def from_hex(cls, hex_string: str) -> "Color":
        """Create Color from a hex string (#RRGGBB or RRGGBB)."""
        hex_string = hex_string.lstrip("#")
        if len(hex_string) != 6:
            raise ValueError("Hex string must be 6 characters long")
        r, g, b = (
            int(hex_string[0:2], 16),
            int(hex_string[2:4], 16),
            int(hex_string[4:6], 16),
        )
        return cls(r, g, b)

    @classmethod
    def from_normalized(cls, r: float, g: float, b: float) -> "Color":
        """Create Color from normalized values [0.0–1.0]."""
        return cls(int(r * 255), int(g * 255), int(b * 255))

    @classmethod
    def random(cls) -> "Color":
        """Generate a random Color."""
        return cls(
            random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
        )

    # === ITERATION & ACCESS ===
    def __iter__(self) -> Iterator[int]:
        yield self._r
        yield self._g
        yield self._b

    def __getitem__(self, index: int) -> int:
        if index == 0:
            return self._r
        elif index == 1:
            return self._g
        elif index == 2:
            return self._b
        else:
            raise IndexError("Color index out of range (0–2)")

    def __len__(self) -> int:
        return 3

    # === COMPARISON & HASH ===
    def __eq__(self, other: "Color") -> bool:
        return isinstance(other, Color) and (self._r, self._g, self._b) == (
            other._r,
            other._g,
            other._b,
        )

    def __hash__(self) -> int:
        return hash((self._r, self._g, self._b))

    # === STRING REPRESENTATIONS ===
    def __str__(self) -> str:
        return f"Color({self._r}, {self._g}, {self._b})"

    def __repr__(self) -> str:
        return f"Color({self._r}, {self._g}, {self._b})"

    # === EXTRA UTILITIES ===
    def to_tuple(self) -> Tuple[int, int, int]:
        return (self._r, self._g, self._b)

    def to_list(self) -> list:
        return [self._r, self._g, self._b]

    def to_dict(self) -> dict:
        return {"r": self._r, "g": self._g, "b": self._b}

    def to_bytesv3_32(self) -> bytes:
        """Convert to 3 32-bit floats (RGB) in little-endian format.
        Note: Some precision loss is normal when converting to 32-bit floats."""
        from struct import pack
        return pack('<3f', *self.normalized())

    def to_bytesv4_32(self, alpha: float = 1.0) -> bytes:
        """Convert to 4 32-bit floats (RGBA) in little-endian format.
        Note: Some precision loss is normal when converting to 32-bit floats."""
        from struct import pack
        # Clamp alpha to [0.0, 1.0] range
        alpha = max(0.0, min(1.0, alpha))
        return pack('<4f', *self.normalized(), alpha)

    def to_bytesv3_64(self) -> bytes:
        """Convert to 3 64-bit doubles (RGB) for higher precision."""
        from struct import pack
        return pack('<3d', *self.normalized())

    def to_bytesv4_64(self, alpha: float = 1.0) -> bytes:
        """Convert to 4 64-bit doubles (RGBA) for higher precision."""
        from struct import pack
        alpha = max(0.0, min(1.0, alpha))
        return pack('<4d', *self.normalized(), alpha)

    def to_bytesv3_u8(self) -> bytes:
        """Convert to 3 unsigned bytes (RGB)."""
        from struct import pack
        return pack('3B', self._r, self._g, self._b)

    def to_bytesv4_u8(self, alpha: int = 255) -> bytes:
        """Convert to 4 unsigned bytes (RGBA)."""
        from struct import pack
        alpha = max(0, min(255, int(alpha)))
        return pack('4B', self._r, self._g, self._b, alpha)

    def css_rgb(self) -> str:
        return f"rgb({self._r}, {self._g}, {self._b})"

    def css_rgba(self, alpha: float = 1.0) -> str:
        alpha = max(0.0, min(1.0, alpha))
        return f"rgba({self._r}, {self._g}, {self._b}, {alpha})"

    def normalized(self) -> Tuple[float, float, float]:
        return (self._r / 255.0, self._g / 255.0, self._b / 255.0)

    @property
    def luminance(self) -> float:
        """Relative luminance (0–1), sRGB standard."""

        def linearize(c):
            c = c / 255.0
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

        r_lin, g_lin, b_lin = linearize(self._r), linearize(self._g), linearize(self._b)
        return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin

    # === VARIANT CREATORS ===
    def with_red(self, r: int) -> "Color":
        return Color(r, self._g, self._b)

    def with_green(self, g: int) -> "Color":
        return Color(self._r, g, self._b)

    def with_blue(self, b: int) -> "Color":
        return Color(self._r, self._g, b)


# === CONSTANT COLORS ===
class Colors:
    BLACK = Color(0, 0, 0)
    WHITE = Color(255, 255, 255)
    RED = Color(255, 0, 0)
    GREEN = Color(0, 255, 0)
    BLUE = Color(0, 0, 255)
    YELLOW = Color(255, 255, 0)
    CYAN = Color(0, 255, 255)
    MAGENTA = Color(255, 0, 255)
    GRAY = Color(128, 128, 128)
    LIGHT_GRAY = Color(192, 192, 192)
    DARK_GRAY = Color(64, 64, 64)
    ORANGE = Color(255, 165, 0)
    PINK = Color(255, 192, 203)
    PURPLE = Color(128, 0, 128)
    BROWN = Color(165, 42, 42)
    LIME = Color(0, 255, 0)
    TEAL = Color(0, 128, 128)
    NAVY = Color(0, 0, 128)
    OLIVE = Color(128, 128, 0)
    MAROON = Color(128, 0, 0)
    AQUA = Color(0, 255, 255)
    CRIMSON = Color(220, 20, 60)
    CORNFLOWER_BLUE = Color(100, 149, 237)
    DARK_ORANGE = Color(255, 140, 0)
    DARK_GREEN = Color(0, 100, 0)
    DARK_RED = Color(139, 0, 0)
    STEEL_BLUE = Color(70, 130, 180)
    DARK_SLATE_GRAY = Color(47, 79, 79)
    MEDIUM_PURPLE = Color(147, 112, 219)
    FIREBRICK = Color(178, 34, 34)
    SALMON = Color(250, 128, 114)
    LIME_GREEN = Color(50, 205, 50)
    SKY_BLUE = Color(135, 206, 235)
    GOLD = Color(255, 215, 0)
    SILVER = Color(192, 192, 192)