import pygame
pygame.mixer.init()
pygame.mixer.music.load("test.mp3")
pygame.mixer.music.play()
print 'start'
while pygame.mixer.music.get_busy() == True:
    continue

print 'end'

