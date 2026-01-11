import sys
import math
import time
import shutil

def main():
    # Zestaw znaków od najlżejszego do najcięższego wizualnie
    CHARS = " .'`^,:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
    
    # Prędkość animacji
    SPEED = 0.05
    
    KOMPOT_ART = [
        "▗▖ ▗▖ ▄▄▄  ▄▄▄▄  ▄▄▄▄   ▄▄▄▗▄▄▄▖",
        "▐▌▗▞▘█   █ █ █ █ █   █ █   █ █  ",
        "▐▛▚▖ ▀▄▄▄▀ █   █ █▄▄▄▀ ▀▄▄▄▀ █  ",
        "▐▌ ▐▌            █           █  "
    ]
    kompot_height = len(KOMPOT_ART)
    # Obliczamy szerokość najdłuższego wiersza
    kompot_width = max(len(line) for line in KOMPOT_ART)

    try:
        # Ukryj kursor
        sys.stdout.write("\033[?25l")
        
        t = 0
        while True:
            # Pobierz aktualny rozmiar terminala 
            try:
                cols, rows = shutil.get_terminal_size()
            except:
                cols, rows = 80, 24

            # Centrowanie napisu
            start_y = (rows // 2) - (kompot_height // 2)
            start_x = (cols // 2) - (kompot_width // 2)

            frame = []
            frame.append("\033[H") # Powrót kursora na górę ekranu 
            
            for y in range(rows - 1):
                line = ""
                is_text_row = start_y <= y < start_y + kompot_height
                
                text_row_str = ""
                if is_text_row:
                    text_row_str = KOMPOT_ART[y - start_y]

                for x in range(cols):
                    is_text_pixel = False
                    if is_text_row:
                        local_x = x - start_x
                        if 0 <= local_x < len(text_row_str):
                            # Jeśli znak w ASCII art nie jest spacją, uznajemy go za część logo
                            if text_row_str[local_x] != " ":
                                is_text_pixel = True
                    
                    if is_text_pixel:
                        # RENDEROWANIE NAPISU - Biały, pogrubiony
                        char = text_row_str[x - start_x]
                        line += f"\033[1;37m{char}" 
                    else:
                        # RENDEROWANIE PLAZMY (TŁO) - Matematyka sinusów
                        cx = x / 4.0
                        cy = y / 2.0
                        
                        val = math.sin(cx + t)
                        val += math.sin((cy + t) / 2.0)
                        val += math.sin((cx + cy + t) / 2.0)
                        val += math.sin(math.sqrt(cx**2 + cy**2 + 1) + t)
                        
                        idx = int((val + 4) / 8 * len(CHARS))
                        idx = max(0, min(len(CHARS) - 1, idx))
                        
                        # Kolory ANSI 256 (tło)
                        color_code = 16 + (idx % 216)
                        line += f"\033[0m\033[38;5;{color_code}m{CHARS[idx]}"
                
                frame.append(line)
            
            frame.append("\033[0m") # Reset kolorów na końcu klatki
            
            sys.stdout.write("\n".join(frame))
            sys.stdout.flush()
            
            t += SPEED
            time.sleep(0.01)

    except KeyboardInterrupt:
        # Przywrócenie ustawień terminala po Ctrl+C
        sys.stdout.write("\033[?25h\033[0m\033[2J\033[H")
        print("Dzięki za oglądanie demka!")

if __name__ == "__main__":
    main()
