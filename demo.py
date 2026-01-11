import sys
import math
import time
import shutil

def main():
    # Zestaw znaków od najlżejszego do najcięższego wizualnie
    CHARS = " .'`^,:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
    
    # Prędkość animacji
    SPEED = 0.05
    
    # ASCII Art "KOMPOT"
    KOMPOT_ART = [
        "K   K  OOO  M   M PPPP   OOO  TTTTT",
        "K  K  O   O MM MM P   P O   O   T  ",
        "KKK   O   O M M M PPPP  O   O   T  ",
        "K  K  O   O M   M P     O   O   T  ",
        "K   K  OOO  M   M P      OOO    T  "
    ]
    kompot_height = len(KOMPOT_ART)
    kompot_width = len(KOMPOT_ART[0])

    try:
        # Ukryj kursor (ANSI escape sequence)
        sys.stdout.write("\033[?25l")
        
        t = 0
        while True:
            # Pobierz aktualny rozmiar terminala
            try:
                cols, rows = shutil.get_terminal_size()
            except:
                cols, rows = 80, 24

            # Oblicz pozycję startową napisu, aby był wyśrodkowany
            start_y = (rows // 2) - (kompot_height // 2)
            start_x = (cols // 2) - (kompot_width // 2)

            frame = []
            frame.append("\033[H") # Home cursor
            
            for y in range(rows - 1):
                line = ""
                # Sprawdź, czy aktualny wiersz 'y' przecina się z napisem w pionie
                is_text_row = start_y <= y < start_y + kompot_height
                
                # Jeśli jesteśmy w wierszu tekstu, pobierz odpowiednią linię ASCII artu
                text_row_str = ""
                if is_text_row:
                    text_row_str = KOMPOT_ART[y - start_y]

                for x in range(cols):
                    # Sprawdź, czy aktualny piksel jest częścią napisu
                    is_text_pixel = False
                    if is_text_row:
                        # Przelicz x na lokalne współrzędne wewnątrz napisu
                        local_x = x - start_x
                        if 0 <= local_x < len(text_row_str):
                            if text_row_str[local_x] != " ":
                                is_text_pixel = True
                    
                    if is_text_pixel:
                        # --- RENDEROWANIE NAPISU ---
                        # Biały (37m), pogrubiony (1m)
                        # Używamy znaku z ASCII artu (lub można podmienić na '#')
                        char = text_row_str[x - start_x]
                        line += f"\033[1;37m{char}" 
                    else:
                        # --- RENDEROWANIE PLAZMY (TŁO) ---
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
                        # Reset stylu (0m) przed kolorem, żeby nie dziedziczył pogrubienia z tekstu
                        line += f"\033[0m\033[38;5;{color_code}m{CHARS[idx]}"
                
                frame.append(line)
            
            frame.append("\033[0m") # Reset na koniec
            
            sys.stdout.write("\n".join(frame))
            sys.stdout.flush()
            
            t += SPEED
            time.sleep(0.01)

    except KeyboardInterrupt:
        sys.stdout.write("\033[?25h")
        sys.stdout.write("\033[0m")
        sys.stdout.write("\033[2J")
        sys.stdout.write("\033[H")
        print("Dzięki za oglądanie demka!")

if __name__ == "__main__":
    main()
