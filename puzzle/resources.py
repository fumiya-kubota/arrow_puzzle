#coding: utf-8
import pygame
import os

img = 'images'
blocksize = 50
barwidth = int(blocksize * .57)
barheight = int(blocksize * .14)


class Resources(object):
    east_image = pygame.transform.smoothscale(pygame.image.load(os.path.join(img, 'green.png')), (blocksize, blocksize))
    west_image = pygame.transform.smoothscale(pygame.image.load(os.path.join(img, 'yellow.png')), (blocksize, blocksize))
    south_image = pygame.transform.smoothscale(pygame.image.load(os.path.join(img, 'blue.png')), (blocksize, blocksize))
    north_image = pygame.transform.smoothscale(pygame.image.load(os.path.join(img, 'red.png')), (blocksize, blocksize))

resource = Resources()
