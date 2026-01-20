import sys
import math
import time
import shutil
import random

def main():
    # --- KONFIGURACJA ---
    ASCII_RAMP = " .:-=+*#%@"
    
    C_BG = "\033[48;5;232m"
    C_DIM = "\033[38;5;236m"
    C_MED = "\033[38;5;242m"
    C_LGT = "\033[38;5;252m"
    C_RED = "\033[38;5;196m" 
    C_DRK_RED = "\033[38;5;52m"
    RESET = "\033[0m"

    SPEED = 0.02
    
    font_map = {
        'K': ["#...#", "#..#.", "##...", "#..#.", "#...#"],
        'O': [".###.", "#...#", "#...#", "#...#", ".###."],
        'M': ["#...#", "##.##", "#.#.#", "#...#", "#...#"],
        'P': ["####.", "#...#", "####.", "#....", "#...."],
        'T': ["#####", "..#..", "..#..", "..#..", "..#.."]
    }
    
    text = "KOMPOT"
    particles = []
    
    spacing = 1.2
    thickness = 3
    
    total_width = len(text) * 5 + (len(text)-1) * spacing
    start_x = -total_width / 2.0 * 0.25 
    
    current_x = start_x
    
    for char in text:
        bitmap = font_map.get(char, font_map['O'])
        for r, row in enumerate(bitmap):
            for c, pixel in enumerate(row):
                if pixel == '#':
                    for z_layer in range(thickness):
                        px = current_x + (c * 0.25)
                        py = (r - 2) * 0.25
                        pz = (z_layer * 0.2) - (thickness * 0.1)
                        particles.append([px, py, pz, px, py, pz])
                        if random.random() < 0.3:
                            particles.append([px + random.uniform(-0.05, 0.05), 
                                              py + random.uniform(-0.05, 0.05), 
                                              pz + random.uniform(-0.05, 0.05), 
                                              px, py, pz])
        current_x += (5 * 0.25) + (spacing * 0.25)

    t = 0.0
    
    # --- GLITCH STATE MACHINE ---
    glitch_frames = 0
    current_glitch_mode = 0

    try:
        sys.stdout.write("\033[?25l")

        while True:
            try:
                cols, rows = shutil.get_terminal_size()
            except:
                cols, rows = 80, 24
            
            buffer = [" "] * (cols * rows)
            z_buffer = [-99.0] * (cols * rows)
            color_buffer = [C_DIM] * (cols * rows)

            cx, cy = cols / 2, rows / 2
            scale_y = rows * 0.25
            scale_x = scale_y * 2.0 

            # Rotacja
            rot_y = t * 0.6
            rot_x = math.sin(t * 0.6) * 0.3
            
            cos_y, sin_y = math.cos(rot_y), math.sin(rot_y)
            cos_x, sin_x = math.cos(rot_x), math.sin(rot_x)
            
            # --- GLITCH LOGIC UPDATE ---
            is_glitching = False
            
            if glitch_frames > 0:
                # Trwa glitch
                is_glitching = True
                glitch_frames -= 1
            else:
                # Czy losujemy nowy?
                # BARDZO RZADKO (0.5% szansy)
                if random.random() < 0.005: 
                    glitch_frames = random.randint(10, 25) # Trwa 10-25 klatek (ok. 0.5 sekundy)
                    current_glitch_mode = random.randint(1, 3)
                    is_glitching = True

            for p in particles:
                bx, by, bz = p[3], p[4], p[5]
                
                bx += math.sin(t * 5 + by) * 0.01
                by += math.cos(t * 5 + bx) * 0.01

                # GLITCH: Position Shift (Mocne, bo rzadkie)
                if is_glitching and current_glitch_mode == 1:
                    bx += random.uniform(-0.3, 0.3)
                
                if is_glitching and current_glitch_mode == 3:
                     bx += random.uniform(-0.8, 0.8)
                     by += random.uniform(-0.8, 0.8)

                # Rot Y
                x1 = bx * cos_y - bz * sin_y
                z1 = bx * sin_y + bz * cos_y
                
                # Rot X
                y2 = by * cos_x - z1 * sin_x
                z2 = by * sin_x + z1 * cos_x
                
                # Projekcja
                z_depth = z2 + 4.0
                if z_depth <= 0.1: continue
                
                ooz = 1.0 / z_depth
                
                proj_x = int(cx + x1 * scale_x * ooz)
                proj_y = int(cy + y2 * scale_y * ooz)
                
                if 0 <= proj_x < cols and 0 <= proj_y < rows:
                    idx = proj_y * cols + proj_x
                    
                    if ooz > z_buffer[idx]:
                        z_buffer[idx] = ooz
                        
                        val = ooz * 0.8
                        char_idx = int(val * len(ASCII_RAMP))
                        char_idx = max(0, min(len(ASCII_RAMP) - 1, char_idx))
                        
                        char = ASCII_RAMP[char_idx]
                        col = C_MED
                        
                        if char_idx > 5: col = C_LGT
                        if char_idx < 3: col = C_DIM
                        
                        # GLITCH: Color Flash
                        if is_glitching:
                            if current_glitch_mode >= 2:
                                col = C_RED
                                if random.random() < 0.5: col = C_DRK_RED
                            if current_glitch_mode == 3:
                                char = random.choice(["X", "!", "?", "/", "\\\\"])
                                col = C_LGT if random.random() < 0.5 else C_RED

                        color_buffer[idx] = col
                        buffer[idx] = char

            # --- HUD ---
            target_text = "SYSTEM: KOMPOT_OS // KERNEL: STABLE // THINKPAD_NINJA_MODE"
            if is_glitching: # Zmiana tekstu przy glitchu
                 target_text = "SYSTEM: CRITICAL ERROR // MEMORY DUMP // REBOOTING..."
                 
            decoded_len = int((math.sin(t * 0.5) + 1) / 2 * len(target_text))
            display_text = target_text[:decoded_len] 
            padding = len(target_text) - decoded_len
            if padding > 0: display_text += "".join([random.choice("X01_.:") for _ in range(padding)])
            
            hud_y = int(rows * 0.9)
            hud_x_start = int(cx - len(display_text) // 2)
            
            if 0 <= hud_y < rows:
                for i, char in enumerate(display_text):
                    bx = hud_x_start + i
                    if 0 <= bx < cols:
                        b_idx = hud_y * cols + bx
                        buffer[b_idx] = char
                        color_buffer[b_idx] = C_RED if random.random() > 0.8 else C_LGT

            # --- RENDER ---
            output_string = f"\033[H{C_BG}"
            
            for y in range(rows):
                row_str = ""
                current_color = ""
                for x in range(cols):
                    idx = y * cols + x
                    char = buffer[idx]
                    color = color_buffer[idx]
                    
                    if color != current_color:
                        row_str += color
                        current_color = color
                    row_str += char
                output_string += row_str + "\n"
            
            output_string += f"{RESET}"
            sys.stdout.write(output_string)
            sys.stdout.flush()
            
            t += SPEED
            time.sleep(0.01)

    except KeyboardInterrupt:
        sys.stdout.write("\033[?25h\033[0m\033[2J\033[H")
        print("DEMO-3D HALTED.")

if __name__ == "__main__":
    main()
