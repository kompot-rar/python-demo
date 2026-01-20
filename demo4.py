import sys
import math
import time
import shutil
import random

def main():
    # Zestaw znaków - ASCII Gradient
    CHARS = " .'`^,:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
    
    SPEED = 0.04
    
    KOMPOT_ART = [
        "▗▖ ▗▖ ▄▄▄  ▄▄▄▄  ▄▄▄▄   ▄▄▄▗▄▄▄▖",
        "▐▌▗▞▘█   █ █ █ █ █   █ █   █ █  ",
        "▐▛▚▖ ▀▄▄▄▀ █   █ █▄▄▄▀ ▀▄▄▄▀ █  ",
        "▐▌ ▐▌            █           █  "
    ]
    kompot_height = len(KOMPOT_ART)
    kompot_width = max(len(line) for line in KOMPOT_ART)

    try:
        sys.stdout.write("\033[?25l") # Ukryj kursor
        
        t = 0
        
        # --- STATE MACHINE ---
        logo_glitch_frames = 0
        screen_glitch_frames = 0
        
        total_glitch_events = 0 # Licznik, żeby pilnować proporcji 1:2
        
        while True:
            try:
                cols, rows = shutil.get_terminal_size()
            except:
                cols, rows = 80, 24

            curr_start_x = (cols // 2) - (kompot_width // 2)
            curr_start_y = (rows // 2) - (kompot_height // 2)

            # --- LOGIC TRIGGER ---
            # Decrementatory
            if logo_glitch_frames > 0: logo_glitch_frames -= 1
            if screen_glitch_frames > 0: screen_glitch_frames -= 1

            # Czy odpalamy nowy glitch?
            # Tylko jeśli jest spokój
            if logo_glitch_frames == 0 and screen_glitch_frames == 0:
                # Bardziej rzadko: 2% szansy na klatkę (było 3%+)
                if random.random() < 0.02:
                    total_glitch_events += 1
                    
                    # 1. ZAWSZE odpalamy Logo Glitch (Red Alert)
                    logo_glitch_frames = random.randint(6, 18) # Dłuższy czas trwania
                    
                    # 2. Co PIĄTY raz dorzucamy Screen Glitch (Rzadki event)
                    if total_glitch_events % 5 == 0:
                        screen_glitch_frames = random.randint(8, 20)

            # --- PRE-CALCULATE GLITCH PARAMETERS (PER FRAME) ---
            
            # Parametry dla LOGO (Kompot)
            lg_offset_x = 0
            lg_offset_y = 0
            if logo_glitch_frames > 0:
                # OGROMNY Glitch (Massive Shake)
                # Skacze nawet o 15 znaków w bok
                lg_offset_x = random.randint(-15, 15)
                lg_offset_y = random.randint(-2, 2)
            
            # Parametry dla EKRANU (Screen)
            sg_offset_y = 0
            if screen_glitch_frames > 0:
                # Rozrywanie ekranu w pionie
                sg_offset_y = random.randint(-1, 1)

            frame = []
            frame.append("\033[H") 
            
            # Puls reaktora
            pulse = (math.sin(t * 3) + 1) / 2 

            for y in range(rows):
                line = ""
                
                # --- SCREEN GLITCH: LINE TEARING ---
                # Przesunięcie linii w pionie (efekt V-Sync)
                render_y = y
                if screen_glitch_frames > 0:
                    # Czasami przesuwamy całą sekcję
                    if random.random() < 0.4:
                        render_y += sg_offset_y
                        
                # --- SCANLINES ---
                is_scanline = (y % 2 == 1)
                
                # --- LOGO DETECTION ---
                # Uwzględniamy tu przesunięcie LOGO (lg_offset_y)
                is_text_row = curr_start_y <= (render_y - lg_offset_y) < curr_start_y + kompot_height
                
                text_row_str = ""
                if is_text_row:
                    try:
                        # Pobieramy odpowiedni wiersz artu
                        art_idx = (render_y - lg_offset_y) - curr_start_y
                        if 0 <= art_idx < len(KOMPOT_ART):
                            text_row_str = KOMPOT_ART[art_idx]
                    except:
                        text_row_str = ""

                for x in range(cols):
                    # --- TŁO: MATH ---
                    cx = (x - cols/2) / 4.0
                    cy = (y - rows/2) / 2.0
                    
                    # Screen Glitch: Distortion of coordinates
                    if screen_glitch_frames > 0 and random.random() < 0.05:
                        cx += random.uniform(-0.5, 0.5)

                    dist = math.sqrt(cx*cx + cy*cy)
                    angle = math.atan2(cy, cx)
                    
                    val = math.sin(dist - t * 1.0) 
                    val += math.sin(angle * 3 + t * 0.5)
                    val += math.sin((cx + cy + t * 0.5) / 2.0)
                    val += pulse * 0.5 

                    idx = int((val + 3) / 6.5 * len(CHARS))
                    idx = max(0, min(len(CHARS) - 1, idx))
                    
                    # --- PIXEL RENDER ---
                    is_text_pixel = False
                    
                    if is_text_row:
                        # Obliczamy pozycję wewnątrz stringa logo
                        # Uwzględniamy OGROMNE przesunięcie poziome (lg_offset_x)
                        local_x = x - curr_start_x - lg_offset_x
                        
                        # Logo Glitch: Lokalne szumy (rozpad liter)
                        if logo_glitch_frames > 0 and random.random() < 0.2:
                            local_x += random.randint(-3, 3)

                        if 0 <= local_x < len(text_row_str):
                            char_at_pos = text_row_str[local_x]
                            if char_at_pos != " ":
                                is_text_pixel = True
                                # Logo Glitch: Dziury w logo
                                if logo_glitch_frames > 0 and random.random() < 0.1:
                                    is_text_pixel = False

                    if is_text_pixel:
                        # --- RENDEROWANIE KOMPOTA ---
                        char = text_row_str[local_x]
                        
                        if logo_glitch_frames > 0:
                            # MASSIVE RED GLITCH
                            # Zamiana znaków na śmieci
                            if random.random() < 0.6: # 60% szans na zmianę znaku
                                char = random.choice(["█", "▓", "▒", "░", "$", "&", "!", "?", "/", "\\", "#", "@"])
                            
                            # Kolory: Czerwony (Głównie) lub Żółty
                            if random.random() < 0.8:
                                line += f"\033[1;31m{char}" # CZERWONY BOLD
                            else:
                                line += f"\033[1;33m{char}" # ŻÓŁTY
                        else:
                            line += f"\033[1;37m{char}" # Normalny biały
                    else:
                        # --- RENDEROWANIE TŁA ---
                        
                        if is_scanline:
                            idx = max(0, idx - 15) # Scanlines
                        
                        # Screen Glitch: Inwersja tła (rzadko, ale zauważalnie)
                        invert_bg = False
                        if screen_glitch_frames > 0 and random.random() < 0.1:
                            invert_bg = True

                        # Kolory Thinkpad Ninja
                        if idx < len(CHARS) * 0.4:
                            gray_offset = idx % 8
                            color_code = 232 + gray_offset
                        elif idx < len(CHARS) * 0.7:
                             gray_offset = idx % 6
                             color_code = 240 + gray_offset
                        else:
                            reds = [52, 88, 124, 160, 196, 196, 202]
                            red_idx = (idx - int(len(CHARS) * 0.7)) % len(reds)
                            color_code = reds[red_idx]
                        
                        if invert_bg:
                             line += f"\033[0m\033[7m\033[38;5;{color_code}m{CHARS[idx]}"
                        else:
                             line += f"\033[0m\033[38;5;{color_code}m{CHARS[idx]}"
                
                frame.append(line)
            
            sys.stdout.write("\n".join(frame))
            sys.stdout.flush()
            
            t += SPEED
            time.sleep(0.01)

    except KeyboardInterrupt:
        sys.stdout.write("\033[?25h\033[0m\033[2J\033[H")
        print("Glitch demo terminated.")

if __name__ == "__main__":
    main()
