'''
Monster Game

V0  Initial Version
V1  Adding the following features
      Pause button V1.01
      'Game Over' displayed at conclusion of the game V1.02
      Fix bug where hearts are not displayed until after first dead life. V1.03
      Fixed bug where the last life remained on the screen V1.04
      Variable speed of monsters v1.05
      added sound for monster movement v1.06

TODO
Add High Score Capability - save High Score to disk
Add Play Again Option
'''




import pygame
import time
import random
from sys import exit
from pygame.locals import *

#colours
white = (255,255,255)
black = (0,0,0)
green = (0, 255, 62)
light_blue = ( 59, 211, 255)

# screen dimensions
screen_width = 750
screen_depth = 500
sky_depth = 400
grass_depth= screen_depth - sky_depth

# sprite dimensions
monster_depth = 25
monster_width = 25
basket_width = 40
basket_depth = 10

# variation in movement
wiggle = 3      #how far from side to side they can move
max_speed = 3   # what is the maximum down speed
frames = 20     # maximum number of frames per second (speed control)
sound_delay = 10

# score keeping
lives_remaining = 5


class MonsterSprite(pygame.sprite.DirtySprite):

  def __init__(self,filename, wiggle, max_speed):
    pygame.sprite.DirtySprite.__init__(self)
    self.image = pygame.image.load(filename).convert()
    self.image.set_colorkey(white)
    self.rect = self.image.get_rect()
    # set start position
    self.rect.x = random.randint(0, screen_width - monster_width)
    self.rect.y = 0
    #print('Position of monster %s, %s' % (self.rect.x, self.rect.y))  #DEBUG
    #print ('Bottom of sprite %s' %self.rect.bottom)    #DEBUG
    self.dirty = 1
    self.wiggle = wiggle
    self.speed = random.randint(1,max_speed)
    self.beepcount = 1
    # check if the mixer has been initialised
    if not pygame.mixer.get_init():
      #initialise the sound channel
      pygame.mixer.init(44100,-16,2,4096)
    return

  def MoveDown(self):
    self.rect.x = self.rect.x + random.randint(-wiggle, wiggle)
    # Check if the monster is going off the page
    if self.rect.x > screen_width - monster_width:
      self.rect.x = screen_width - monster_width
    if self.rect.x < 0:
      self.rect.x = 0
    self.rect.y =self.rect.y + self.speed
    self.dirty = 1
    return



class BasketSprite(pygame.sprite.DirtySprite):

  def __init__(self,filename):
    pygame.sprite.DirtySprite.__init__(self)
    self.image = pygame.image.load(filename).convert()
    self.image.set_colorkey(white)
    self.rect = self.image.get_rect()
    # set start position
    self.rect.x = (screen_width - basket_width) /2
    self.rect.y = sky_depth - basket_depth
    #print('Position of basket %s, %s' % (self.rect.x, self.rect.y))  #DEBUG
    self.dirty = 1
    return

  def Move(self):
    self.rect.x, ignore = pygame.mouse.get_pos()
    self.dirty = 1
    return


class ScoreLevel():

  def __init__(self):
    self.score = 0
    self.level = 1
    self.lastscore = 0

  def AddScore(self):
    self.score +=1
    #print('Score %02d' % self.score)    #DEBUG
    return

  def AddLevel(self):
    self.level +=1
    return

  def ReadScore(self):
    return self.score

  def ReadLevel(self):
    return self.level

  def NextLevel(self):
    # determine if the next level has been reached and return true or false
    # Needs to cater for being called several times per score
    self.lvl = divmod(self.score, 10)
    # check if the score has changed since last time I checked, if not return False
    if self.score == self.lastscore:
      return False
    self.lastscore = self.score
    # check if the score is now divisble by 10, if so return True & add 1 to the level
    if self.lvl[1] == 0:
      #print ('Next Level: ', self.lvl)   #DEBUG
      self.level += 1
      return True
    # else return false
    return False


class Life(pygame.sprite.DirtySprite):
  # class to instantiate a single life!

  def __init__(self,filename,life):
    pygame.sprite.DirtySprite.__init__(self)
    self.image = pygame.image.load(filename).convert()
    self.image.set_colorkey(white)
    self.rect = self.image.get_rect()
    self.rect.x = life * 10
    self.rect.y = 5
    self.dirty = 1
    self.lifenumber = life
    #print('Life %d  position %d:%d' % (life, self.rect.x, self.rect.y))   #DEBUG

  def Number(self):
    # return the number of the sprite
    return self.lifenumber


class Lives():

  def __init__(self,window,area):
    self.lives = 5
    self.window = window
    self.area = area
    self.lives_list = pygame.sprite.Group()
    #print(' lives, window and area ', self.lives, self.window, self.area)
    return

  def AddLives(self,filename):
    #creates an instance of each lives and draws them on the screen
    for h in range(self.lives):
      self.life = Life(filename,h)
      self.lives_list.add(self.life)
    #print('Add Lives - lives_list',self.lives_list)    #DEBUG
    return self.lives_list

  def LostLife(self):
    # remove the sprite from all groups for the lost life
    # If there are no more lives left, end the game
    self.lives -= 1
    for l in self.lives_list.sprites():
      if l.Number() == self.lives:
        l.kill()
    return

  def AnyLivesLeft(self):
    # returns true if the number of remaining lives is greater than zero
    # returns false if zero or less
    return (self.lives > 0)

  
  def DrawLives(self):
    #self.lives_list.draw(self.window)
    self.lives_list.clear(self.window,self.area)
    self.lives_list.draw(self.window)
    return

  def NumberOfLives(self):
    return self.lives


 
class MakeSound():

  def __init__(self,delay,sound1,sound2=0):
    # check if the mixer has been initialised
    if not pygame.mixer.get_init():
      #initialise the sound channel
      pygame.mixer.init(44100,-16,2,4096)
    self.delay = delay
    self.sound1 = sound1
    self.sound2 = sound2
    self.count = 0
    return

  def PlaySound(self,sound):
    # Play the sound from a choice
    if sound == 1:
      self.ps = pygame.mixer.Sound('Monster_Move1.wav')
      self.ps.set_volume(0.5)
      self.ps.play()
    elif sound == 2:
      self.ps = pygame.mixer.Sound('Monster_Move2.wav')
      self.ps.play()
    elif sound == 3:
      self.ps = pygame.mixer.Sound('Monster_Died.wav')
      self.ps.play()
    elif sound == 4:
      self.ps = pygame.mixer.Sound('Monster_Landed.wav')
      self.ps.play()
    return

  def PlayYet(self):
    # is it time to play another sound yet?
    # only play a sound every few moves
    if self.count >= self.delay:
      self.PlaySound(self.sound1)
      self.count = 0
    else:
      self.count +=1
    return

  def OverrideSound(self,wait,sound):
    # Function stops the current sound and starts the new ones
    self.ps.stop()
    self.PlaySound(sound)
    if wait:
      while pygame.mixer.get_busy():
        pass
    return

  def ChangeDelay(self,change=0,delay=-1):
    # change the dealy in the sound
    if delay != -1:
      self.delay = delay
    self.delay = self.delay + change
    return
  


def AddMonster():
  #TODO move this into the MonsterSprite class - need to work out how to instanstiate a new instance of the same class
  # Add a monster on the screen
  monster = MonsterSprite("monster.png", wiggle, max_speed)
  monster_list.add(monster)
  all_sprites_list.add(monster)
  return

def GamePaused(clearflag):
  # clear is a flag of True to mean it is Paused or False when it is cleared
  text = 'Game is Paused'
  textsize = font.size(text)
  if clearflag:
    textimg = font.render(text, 1, white, light_blue)
    # in the centre (subtracted half the text size)
    screen.blit(textimg, ((screen_width/ 2)- textsize[0]/2 , screen_depth / 2))  
  else:
    screen.fill(light_blue,
                (
                  screen_width/2 - textsize[0]/2,
                  screen_depth/2,
                  textsize[0],
                  textsize[1]
                  )
                ) # coordinates are the start positions plus the size

def GameOver():
  text = 'Game Over'
  textsize = font.size(text)
  textimg = font.render(text, 1, white, light_blue)
  screen.blit(textimg, ((screen_width/ 2)- textsize[0]/2 , screen_depth / 2))
  pygame.display.flip()
  time.sleep(5)
  pygame.quit()
  exit()

 
'''
Main Loop
'''

pygame.init()

# Build the screen - blue sky and gree grass
screen = pygame.display.set_mode([screen_width, screen_depth])
window = pygame.Surface((screen_width, screen_depth))

sky = pygame.Surface.subsurface(window, pygame.Rect((0,0),(screen_width,sky_depth)))
sky.fill(light_blue)

grass = pygame.Surface.subsurface(window, pygame.Rect((0,sky_depth),(screen_width, grass_depth)))
grass.fill(green)

# create group for the sprites
monster_list = pygame.sprite.Group()
all_sprites_list = pygame.sprite.LayeredDirty()

# create the first monster and add it to the group of monsters
AddMonster()

# create the basket & add it to the all sprites group for drawing later
basket = BasketSprite("basket.png")
all_sprites_list.add(basket)

# turn off the cursor for the game
pygame.mouse.set_visible(0)


# draw the initial screen
screen.blit(window, (0,0))
pygame.display.flip()

# initiate the score
sl = ScoreLevel()

# initiate the font for the text to be displayed on screen
font = pygame.font.Font(None,20)

# initiate the sound
beep = MakeSound(sound_delay,1)

# do i move this into the Lives class????
lives = Lives(screen,sky)
all_sprites_list.add(lives.AddLives("Heart Life.png"))


clock = pygame.time.Clock()

#countdown is used to delay till the next monster.
# It is set to -1 to be off.
countdown = -1

pygame.event.clear()

paused = False

while lives.NumberOfLives() > 0:
  for event in pygame.event.get():
    if event.type == QUIT:
      pygame.quit()
      exit()
    if event.type == KEYDOWN:
      if event.key == ord(' '):
        #print ('Game is Paused')
        paused = not(paused)
        GamePaused(paused)  
  
  if paused == False:
    # Move all the monsters down
    for m in monster_list.sprites():
      MonsterSprite.MoveDown(m)
      # did it get caught in the basket?
      if m.rect.y > (sky_depth - monster_depth):
        # bottom of the sprite is on the grass, remove a life and remove the sprite, putting a new one on the screen
        beep.OverrideSound(True,4)
        m.kill()
        lives.LostLife()
        if lives.AnyLivesLeft():
          # only draw a new monster if there is at least 1 life left
          AddMonster()

    if pygame.sprite.spritecollide(basket,monster_list,True):
      # monster has been caught in the basket. Increase the score and add a new monster
      beep.OverrideSound(True,3)
      sl.AddScore()
      AddMonster()



    # Check for the next level and prepare to add another monster when countdown reached zero
    # This provides some variation of when the next monster appears
    if sl.NextLevel():
      # have we reached the next level, if so, restart the counter
      countdown = random.randint(10,sky_depth)
      beep.ChangeDelay(-1)

    # if the countdown is zero, add a new monster, else reduce it by 1. Set to -1 for off
    if countdown == 0:
      AddMonster()
      countdown = -1
    elif countdown > 0:
      countdown -= 1

    # update the position of the basket
    BasketSprite.Move(basket)

    # play the sound
    beep.PlayYet()

    # Clear the monsters & then redraw them
    all_sprites_list.clear(screen,sky)
    all_sprites_list.draw(screen)

    # update the score
    text = 'Score: ' + str(sl.ReadScore())
    textimg = font.render(text, 1, white, light_blue)
    screen.blit(textimg, (screen_width - 100,0))  

  # Wait for the right number fo frames to pass before updating.
  clock.tick(frames)

  pygame.display.flip()



GameOver()




