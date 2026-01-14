#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generador de icono de hongo para DescargasOrdenadas - Creado por Champi
"""

try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

def create_mushroom_icon(size=256):
    """
    Crea un icono de hongo estilo Super Mario.
    
    Args:
        size: Tamaño del icono en píxeles
    """
    if not PIL_AVAILABLE:
        print("⚠️  PIL no disponible, no se puede crear el icono")
        return None
    
    # Crear imagen con fondo transparente
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Colores del hongo de Super Mario
    red = (220, 20, 60)      # Rojo del sombrero
    white = (255, 255, 255)   # Puntos blancos
    beige = (245, 222, 179)   # Tallo del hongo
    dark_beige = (210, 180, 140)  # Sombra del tallo
    
    # Dibujar el tallo del hongo
    stalk_width = size // 3
    stalk_height = size // 2
    stalk_x = (size - stalk_width) // 2
    stalk_y = size - stalk_height - size // 10
    
    # Tallo principal
    draw.ellipse([
        stalk_x, stalk_y,
        stalk_x + stalk_width, stalk_y + stalk_height
    ], fill=beige)
    
    # Sombra del tallo
    shadow_margin = max(2, size // 50)
    if stalk_width > shadow_margin * 2:
        draw.ellipse([
            stalk_x + shadow_margin, stalk_y + shadow_margin,
            stalk_x + stalk_width - shadow_margin, stalk_y + stalk_height
        ], fill=dark_beige)
    
    # Dibujar el sombrero del hongo
    hat_size = int(size * 0.8)
    hat_x = (size - hat_size) // 2
    hat_y = size // 6
    
    # Sombrero principal (rojo)
    draw.ellipse([
        hat_x, hat_y,
        hat_x + hat_size, hat_y + hat_size // 2 + 20
    ], fill=red)
    
    # Puntos blancos en el sombrero
    dot_size = size // 12
    
    # Punto central grande
    center_x = size // 2
    center_y = hat_y + hat_size // 4
    if dot_size > 0:
        draw.ellipse([
            center_x - dot_size, center_y - dot_size//2,
            center_x + dot_size, center_y + dot_size//2
        ], fill=white)
    
    # Puntos laterales
    for i, (dx, dy) in enumerate([(-1.5, -0.5), (1.5, -0.5), (-1, 1), (1, 1)]):
        dot_x = int(center_x + dx * dot_size * 2)
        dot_y = int(center_y + dy * dot_size * 1.5)
        dot_radius = max(1, dot_size // 2 if i < 2 else dot_size // 3)
        
        if dot_radius > 0:
            draw.ellipse([
                dot_x - dot_radius, dot_y - dot_radius,
                dot_x + dot_radius, dot_y + dot_radius
            ], fill=white)
    
    return img

def create_all_icon_sizes():
    """Crea iconos en múltiples tamaños."""
    if not PIL_AVAILABLE:
        print("❌ No se puede crear iconos sin PIL/Pillow")
        return False
    
    sizes = [16, 32, 48, 64, 128, 256]
    
    print("🍄 Creando iconos de hongo...")
    
    for size in sizes:
        icon = create_mushroom_icon(size)
        if icon:
            filename = f"resources/mushroom_{size}.png"
            icon.save(filename, 'PNG')
            print(f"✅ Creado: {filename}")
    
    # Crear favicon
    icon_16 = create_mushroom_icon(16)
    if icon_16:
        icon_16.save("resources/favicon.ico", 'ICO')
        print("✅ Creado: resources/favicon.ico")
    
    # Crear icono principal
    main_icon = create_mushroom_icon(256)
    if main_icon:
        main_icon.save("resources/icon.png", 'PNG')
        print("✅ Creado: resources/icon.png")
    
    print("🎉 ¡Iconos de hongo creados exitosamente!")
    return True

if __name__ == "__main__":
    # Asegurar que existe la carpeta resources
    import os
    os.makedirs("resources", exist_ok=True)
    
    create_all_icon_sizes() 