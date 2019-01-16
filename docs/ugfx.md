# Primitives
## Draw
### ugfx.init()
```
ugfx.init()
```

### ugfx.clear()
### ugfx.clear(COLOR)
```
ugfx.clear()
ugfx.clear(ugfx.BLUE)
```

### ugfx.pixel(X, Y, COLOR)
```
ugfx.clear(ugfx.BLACK)
for y in range(60, 180, 5):
    for x in range(80, 240, 5):
        ugfx.pixel(x, y, ugfx.WHITE)
```

### ugfx.line(X_START, Y_START, X_END, Y_END, COLOR)
### ugfx.thickline(X_START, Y_START, X_END, Y_END, COLOR, WIDTH, ROUNDED)
```
ugfx.clear()
ugfx.line(50, 50, 200, 100, ugfx.BLUE)
ugfx.thickline(50, 100, 200, 150, ugfx.GREEN, 5, False)
ugfx.thickline(50, 150, 200, 200, ugfx.RED, 10, True)
```

### ugfx.circle(X, Y, RADIUS, COLOR)
### ugfx.fill_circle(X, Y, RADIUS, COLOR)
```
ugfx.clear()
ugfx.circle(160, 120, 80, ugfx.AQUA)
ugfx.fill_circle(160, 120, 40, ugfx.BLUE)
```

### ugfx.arc(X, Y, RADIUS, ANGLE_START, ANGLE_END, COLOR)
### ugfx.fill_arc(X, Y, RADIUS, ANGLE_START, ANGLE_END, COLOR)
```
ugfx.clear()
ugfx.arc(160, 120, 80, 0, 90, ugfx.RED)
ugfx.fill_arc(160, 120, 50, 180, 270, ugfx.BLUE)
```

### ugfx.ellipse(X, Y, A, B, COLOR)
### ugfx.fill_ellipse(X, Y, A, B, COLOR)
```
ugfx.clear()
ugfx.ellipse(160, 120, 80, 60, ugfx.OLIVE)
ugfx.fill_ellipse(160, 120, 20, 40, ugfx.BLUE)
```

### ugfx.polygon(X, Y, ARRAY, COLOR)
### ugfx.fill_polygon(X, Y, ARRAY, COLOR)
```
ugfx.clear()
points = [[10, 40], [40, 40], [50, 10], [60, 40], [90, 40], [65, 60], [75, 90], [50, 70], [25, 90], [35, 60], [10, 40]]
ugfx.polygon(50, 60, points, ugfx.LIME)
ugfx.fill_polygon(200, 60, points, ugfx.RED)
```

## Text

### ugfx.text(X, Y, STRING, COLOR)
```
ugfx.clear(ugfx.WHITE)
ugfx.text(40, 40, 'Hello World', ugfx.BLACK)
```

### ugfx.fonts_list()
```
ugfx.fonts_list()
```

### ugfx.set_default_font(FONT_NAME)
```
ugfx.set_default_font('IBMPlexMono_Light24')
ugfx.text(40, 120, 'Hello Light World', ugfx.BLACK)
```

### ugfx.string(X, Y, STRING, FONT_NAME, COLOR)
```
ugfx.clear()
ugfx.string(10, 40, 'IBM Plex Sans Bold 24', 'IBMPlexSans_Bold24', ugfx.BLACK)
ugfx.string(10, 80, 'IBM Plex Sans Regular 24', 'IBMPlexSans_Regular24', ugfx.BLACK)
ugfx.string(10, 120, 'IBM Plex Mono Bold 24', 'IBMPlexMono_Bold24', ugfx.BLACK)
ugfx.string(10, 160, 'IBM Plex Mono Light 24', 'IBMPlexMono_Light24', ugfx.BLACK)
```

### ugfx.string_box(X, Y, W, H, STRING, FONT, COLOR, JUSTIFY)
```
ugfx.clear()
ugfx.string_box(40, 40, 240, 40, 'RIGHT??', 'IBMPlexMono_Bold36', ugfx.AQUA, ugfx.justifyRight)
ugfx.string_box(40, 100, 240, 40, 'LEFT!!', 'IBMPlexMono_Bold36', ugfx.TEAL, ugfx.justifyLeft)
ugfx.string_box(40, 160, 240, 40, '[CENTER]', 'IBMPlexMono_Bold36', ugfx.MAROON, ugfx.justifyCenter)
```

### ugfx.char(X, Y, CHAR, FONT_NAME, COLOR)
```
ugfx.clear()
ugfx.char(50, 50, ord('A'), 'IBMPlexSans_Regular24', ugfx.CYAN)
ugfx.char(100, 50, ord('B'), 'IBMPlexMono_Light32', ugfx.ORANGE)
ugfx.char(100, 100, ord('C'), 'IBMPlexMono_Bold48', ugfx.PURPLE)
```

### ugfx.get_char_width(CHAR, FONT_NAME)
```
ugfx.get_char_width(ord('i'), 'IBMPlexSans_Regular26')
ugfx.get_char_width(ord('O'), 'IBMPlexSans_Regular26')
```

### ugfx.get_string_width(STRING, FONT_NAME)
```
ugfx.get_string_width('IBM', 'IBMPlexSans_Regular26')
```

## Utils


### ugfx.width()
```
ugfx.width()
```

### ugfx.height()
```
ugfx.height()
```

### ugfx.orientation()
### ugfx.orientation(DEGREE)
```
ugfx.clear()
ugfx.orientation()
ugfx.text(50, 50, 'Hello World', ugfx.GRAY)
ugfx.orientation(ugfx.orientation() + 90)
ugfx.text(50, 50, 'Rotated World', ugfx.GRAY)
```

### ugfx.HTML2COLOR(HEXCOLOR)
```
light_blue = ugfx.HTML2COLOR(0x01d7dd)
ugfx.clear(light_blue)
```

### ugfx.RGB2COLOR(RED, GREEN, BLACK)
```
green20 = ugfx.RGB2COLOR(87, 215, 133)
ugfx.clear(green20)
```

## Etc

### ugfx.send_tab()

### ugfx.set_default_style(STYLE_OBJ)
