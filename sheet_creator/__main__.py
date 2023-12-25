import sys

import pygame
import keyboard


pygame.mixer.init()

pygame.mixer.music.load(sys.argv[1])


def get_timestamp():
    millis = pygame.mixer.music.get_pos()
    seconds = (millis / 1000) % 60
    minutes = (millis / (1000 * 60)) % 60
    hours = (millis / (1000 * 60 * 60)) % 24
    return f'{int(hours):02}:{int(minutes):02}:{int(seconds):02}.{millis % 1000:03}'


pygame.mixer.music.play()

try:
    with open(sys.argv[2], 'w') as file:
        print('Press number key to record a timestamp. Press ESC to exit.')

        while pygame.mixer.music.get_busy():
            event = keyboard.read_event(suppress=False)

            if event.event_type == keyboard.KEY_DOWN and event.name.isdigit():
                timestamp = get_timestamp()
                line = f'{timestamp},0.100,{event.name},#ffffff\n'
                file.write(line)
                file.flush()
                print(line, end='')

            elif keyboard.is_pressed('esc'):
                print('Exiting...')
                break

finally:
    pygame.mixer.music.stop()
    pygame.quit()
