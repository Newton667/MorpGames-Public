import pygame
import sys #smooth exit from game
import os

pygame.init()

Width = 876
Height = 800
Jump = False
jumpVel = 30
jumpDist = 20
jumpVel = jumpDist
jumpGravity = 1
TileSize = 50
pygame.display.set_caption("Evil Morph")
displayRes = pygame.display.set_mode((Width, Height))
background = pygame.image.load('pictures/bgmorph.jpg')
tile = pygame.image.load('pictures/tile.png')

#Create the Morp character, evil aspects will be added later
class Character(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        image = pygame.image.load('pictures/Morp.png')
        self.image = pygame.transform.scale(image, (30,30))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
    
    
    def update(self):
        cx=0
        cy=0

        key = pygame.key.get_pressed()

        if key[pygame.K_LEFT]:
            cx -= 1
        if key[pygame.K_RIGHT]:
            cx += 1
        if key[pygame.K_SPACE]:
            Jump = True
        #if Jump:
          #  cy -= jumpVel
          #  jumpVel -= gravity
            


        self.rect.x += cx
        self.rect.y += cy
        
    

  
EvilMorp = Character(30, 30)

tile_map =  [
'                                                        ',
'       t             t                     t            ',
'   t        t               t       t                   ',
' t                    tt                        ttt     ',
'                   t                                    ',
'                t                                       ', 
'            tttt                                        ',
'tttttttt            tttttttttttt       t  t           t ',
'           tt    t                 t          t t  t    ',
't   t                   t   t           t               ',
'                ttt              ttt          t      t  ',
'  t      t                                       t      ',
't     t     t          t   t                            ',
'   t                                                    ',
'        t         t                                     ',
'c                                                       ',
'ttttt                   t            t                  '
]


class Tiles(pygame.sprite.Sprite):
    def __init__(self, x,y):
        super().__init__()
        self.image = tile
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

tiles = pygame.sprite.Group()

for row_cell, row in enumerate(tile_map):
    for col_cell, cell in enumerate(row):
        x,y = col_cell * TileSize, row_cell * TileSize
        if cell == 't':
            generateTile = Tiles(x,y)
            tiles.add(generateTile)
        elif cell == 'c':
            characterStartPosition = (x,y)

EvilMorp = Character(*characterStartPosition)


running = True 

while running:
    EvilMorp.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

   
    displayRes.blit(background,(0,0))
    tiles.draw(displayRes)
    displayRes.blit(EvilMorp.image, EvilMorp.rect)
    pygame.display.update()

    
