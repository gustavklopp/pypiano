#!/usr/bin/env python
#-*coding:utf-8-*-
import os
import pygame
from pygame.locals import *
import sys
pygame.init()

# CONSTANTS :
FPS = 60 # desired framerate in frames per second. try out other values !
KEYBOARDX = 5   # Top left of the full keyboard
KEYBOARDY = 5   # Top left of the full keyboard
KEYBETWEEN = 0  # distance between the key
KEY_HEIGHT = 0 # height of white key (useful for put the text at the right distance
DISTKEY_TEXT = 10 # distance between the key and the text with the name of the key below
BLUE = (0,0,255)
BLACK = (0,0,0)
SCANCODE_UNICODE = dict(zip([ # correspondance azerty keyboard with its scancode
49,10,11,12,13,14,15,16,17,18,19,20,21,
23,24,25,26,27,28,29,30,31,32,33,
38,39,40,41,42,43,44,45,46,47,48,51,
50,94,52,53,54,55,56,57,58,59,60,61,62
], [
'²','&','é','"','\'','(','-','è','_','ç','à',')','=',
'tab','a','z','e','r','t','y','u','i','o','p',
'q','s','d','f','g','h','j','k','l','m','ù','*',
'lsh','<','w','x','c','v','b','n',',',';',':','!','rsh'
]))

# DEFINING THE KEYBOARD SETTING:
# we use 'freesound_med' folder with 4 octaves: C2 to G5
# Create the list of note filenames, sorted according to classic notation c, db, d, eb, etc...
pygame.mixer.pre_init(44100, -16, 2, 4096) # setup mixer to avoid sound lag
music_order = ['c','db','d','eb','e','f','gb','g','ab','a','bb','b']
note_sounds = [] # list of all the note filename
for octave in range(2,6):
    for idx, insidenote in enumerate(music_order):
        note_sounds.append(pygame.mixer.Sound(\
            # it needs 16bits audio files:
            # wav files make it crash after some times...
             os.path.join('pythonpiano_sounds','16_piano-med-'+insidenote+str(octave)+'.ogg')))
# Create a dict of filename sound, and keyboard key:
with open('computer_typewriter.kb', 'r') as f:
    KEY_ASCII = f.read().split('\n') 
KEY_SOUND = dict(zip(KEY_ASCII, note_sounds)) # Keyboard with the corresponding sound filename
IS_PLAYING = {k: False for k in KEY_ASCII}    # Dict of the note to know whether it's playing or not.

# Create the Key sprites:
class Key(pygame.sprite.Sprite):
    keyobj_list = []

    def __init__(self, name, keyevent):
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        self.color = self.name.split('_')[1]
        self.image = pygame.image.load(os.path.join('pythonpiano_pictures',self.name+'_unpressed.png'))
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect() # need to be defined for the group updates!
        self.width = self.image.get_width()
        self.keyevent = keyevent # name of the key returned by 'pygame.event.scancode' = Key code number
        self.pressed = False
        Key.keyobj_list.append(self)
        self.rect.x = 0  # temporary, the position of the key is '0'
        self.rect.y = KEYBOARDY
        self._layer = 0 # the order with which the key is drawn
        # Preloading of the key picture for faster load
        self._img_down = pygame.image.load(os.path.join('pythonpiano_pictures',self.name+'_pressed.png'))
        self._img_up = pygame.image.load(os.path.join('pythonpiano_pictures',self.name+'_unpressed.png'))
        
        
    def update(self):
        if self.pressed:
            self.image = self._img_down
#             print("the key {} is being pressed".format(self.keyevent))
        else:
            self.image = self._img_up


class Game(object):
    def __init__(self):
        
        # Draw the background:
        self.screen=pygame.display.set_mode((900,250)) # set screensize of pygame window
        self.background = pygame.Surface(self.screen.get_size())  #create empty pygame surface
        self.background.fill((255,255,255))     #fill the background white color (red,green,blue)
        # Useless if it's not a sprite...:
#         self.background = self.background.convert()  #convert Surface object to make blitting faster

        # Create all the sprites beforehand:
        # Position of key for one octave:
        key_octave = ['key_white_Left','key_black','key_white_Middle','key_black',
                      'key_white_Right','key_white_Left','key_black','key_white_Middle','key_black',\
                      'key_white_Middle','key_black','key_white_Right']
        music_octave = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
        keyevent_idx = 0 # each key must have a reference to the keyboard ascii with their correct position:
        keyboardx_position = KEYBOARDX
        # assign groups for the Sprite:
        self.keysprites = pygame.sprite.LayeredUpdates()

        for i in range(4):
            for idx,key in enumerate(key_octave):
                key_obj = Key(key, KEY_ASCII[keyevent_idx])
                keyevent_idx += 1
                # Draw the keys:
                if key_obj.color == 'white':
                    key_obj.rect.x = keyboardx_position
                    keyboardx_position += key_obj.width + KEYBETWEEN
                elif key_obj.color == 'black':
                    key_obj.rect.x = keyboardx_position - key_obj.width/4 
                    key_obj._layer = 1 # move it to the front position (the bigger the number
                self.background.blit(key_obj.image, key_obj.rect)
                self.keysprites.add(key_obj) # add the key sprite to the group
                # Print the Name of the key below:
                fontObj = pygame.font.Font('freesansbold.ttf', 12)
                # Display the letter on the keyboard and the music note bellow)
                text_keyboardSurf = fontObj.render(SCANCODE_UNICODE[int(key_obj.keyevent)], True, BLUE)
                text_musicnoteSurf = fontObj.render(music_octave[idx]+str(i+2), True, BLACK)

                text_keyboardRect = text_keyboardSurf.get_rect()
                text_musicnoteRect = text_musicnoteSurf.get_rect()

                # position the rect under the key (using KEY_HEIGHT which is defined only now
                if key_obj.color == 'black':
                    text_musicnoteRect.topright = key_obj.rect.centerx, KEY_HEIGHT + 5*DISTKEY_TEXT
                    text_keyboardRect.topright = key_obj.rect.centerx, KEY_HEIGHT + 0.5*DISTKEY_TEXT
                elif key_obj.color == 'white':
                    KEY_HEIGHT = key_obj.rect.height
                    text_musicnoteRect.midtop = key_obj.rect.centerx, KEY_HEIGHT+ 6*DISTKEY_TEXT
                    text_keyboardRect.midtop = key_obj.rect.centerx, KEY_HEIGHT+ DISTKEY_TEXT

                self.background.blit(text_keyboardSurf, text_keyboardRect)
                self.background.blit(text_musicnoteSurf, text_musicnoteRect)

        self.screen.blit(self.background, (0,0))     #draw the background on screen
        pygame.display.flip()                        # then flip it 

        self.clock = pygame.time.Clock()        #create a pygame clock object
        

    def run(self):
        print("Starting Event loop")
        running = True                    


        while running:
            milliseconds = self.clock.tick(FPS) # do not go faster than this framerate
            
            # handle pygame events -- if user closes game, stop running
            running = self.handlerEvents() 

            # update our sprites
            for keysprite in self.keysprites:
                keysprite.update()

            # render our sprites
            self.keysprites.clear(self.screen, self.background)    # clears the window where the sprites currently are, using the background
            dirty = self.keysprites.draw(self.screen)              # calculates the 'dirty' rectangles that need to be redrawn

            # blit the dirty areas of the screen
            pygame.display.update(dirty)                        # updates just the 'dirty' areas
          
            # print the framerate into the pygame window title
            pygame.display.set_caption("FPS: {:.2f} Python Piano".format(self.clock.get_fps()))

        print("Good Bye!")
        sys.exit()
    
    def handlerEvents(self):
        # Event checker:
        for event in pygame.event.get():
            if event.type in (KEYDOWN, KEYUP):
                key = str(event.scancode)

            if event.type == QUIT:
                return False # pygame window closed by user

            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return False # user pressed ESC
                if (key in KEY_SOUND.keys()) and (not IS_PLAYING[key]):
                    KEY_SOUND[key].play()
                    IS_PLAYING[key] = True
                    for keyobj in Key.keyobj_list:
                        if keyobj.keyevent == key:
                            keyobj.pressed = True
                            

            elif event.type == KEYUP and key in KEY_SOUND.keys():
                # Stops with 50ms fadeout
                KEY_SOUND[key].fadeout(500)
                IS_PLAYING[key] = False
                for keyobj in Key.keyobj_list:
                    if keyobj.keyevent == key:
                        keyobj.pressed = False
        return True

if __name__ == "__main__":
    game = Game()    
    game.run()