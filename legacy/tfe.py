#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  tfe2019.py
#  
#  Copyright 2019 Adriano_Meledina_-_6tb

"""

Jeu Space Shooter TFE 2019

Script Python

Fichiers : tfe.py, perso.py, images

"""

#Importation des bibliothèques nécessaires


from random import randrange
from pygame.locals import *
import pygame

from perso import *

fichier = open("./best.txt", 'r')


def crash():
   
    largeText = pygame.font.SysFont("comicsansms",75)
    largeText2 = pygame.font.SysFont("comicsansms",50)
    TextSurf = largeText.render("Game Over", True, (255, 255, 255))
    TextSurf2 = largeText2.render("Score = {}".format(score), True, (255, 255, 255))
    TextSurf3 = largeText2.render("Best Score = {}".format(bestscore), True, (255, 255, 255))
    fenetre.blit(TextSurf, (100,250))
    fenetre.blit(TextSurf2, (170,350))
    fenetre.blit(TextSurf3, (100,420))
    
    while True:
        for event in pygame.event.get():
            #print(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        pygame.display.update()
        clock.tick(15) 
        

bestscore = fichier.readline()
print(bestscore)
fichier.close()

#Initialisation de la bibliothèque Pygame

pygame.init()

#Ouverture de la fenêtre Pygame

fenetre = pygame.display.set_mode((600, 800))


#Chargement et collage du fond

fond = pygame.image.load("starfield.png").convert()
fond = pygame.transform.scale(fond, (600, 1000))
fenetre.blit(fond, (0,0))
font = pygame.font.SysFont("comicsansms", 25)

boost = pygame.image.load("shield.png").convert_alpha()
boost = pygame.transform.scale(boost, (30, 30))
boost_rect = boost.get_rect()
logo_boost = boost.get_rect()
boostvie = pygame.image.load("vie.png").convert_alpha()
boostvie= pygame.transform.scale(boostvie, (45,45))  
boostvie_rect = boostvie.get_rect()
yboost1=randrange(-1000,-400)
xboost1=randrange(0,500)
yboost2=randrange(-1000,-400)
xboost2=randrange(0,500)
boost_rect.move_ip(xboost1,yboost1)
boostvie_rect.move_ip(xboost2,yboost2)

#Chargement et collage du personnage
vaisseau = Perso()
fenetre.blit(vaisseau.image, vaisseau.position)
score = 0

grpmeteo=[]

for i in range(0,3):
	xcol1=randrange(0,100)
	xcol2=randrange(150,250)
	xcol3=randrange(300,450)
	y1=randrange(-400,-200)
	imgmeteo = pygame.image.load("meteorite.png").convert_alpha()
	imgmeteo = pygame.transform.scale(imgmeteo, (100,100))
	imgrect= imgmeteo.get_rect()
	grpmeteo.append(imgrect) # liste de rectangles
	if i == 0:
		grpmeteo[i].move_ip(xcol1,y1)
		print(grpmeteo[i])
	if i == 1:
		grpmeteo[i].move_ip(xcol2,y1)
	if i == 2:
		grpmeteo[i].move_ip(xcol3,y1)
	print (grpmeteo[i])

 
#Rafraîchissement de l'écran

pygame.display.flip()
clock = pygame.time.Clock()

              
#BOUCLE INFINIE

continuer = 1
perdu = False
cdb = False
cd = 0
buff = 0
v1=1
v2=5

while continuer:
	for event in pygame.event.get():    #Attente des événements
		
		if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
			
			continuer = 0
	
	
	key_pressed = pygame.key.get_pressed()
	
	if key_pressed[K_RIGHT]:
		vaisseau.Droit()
	
	if key_pressed[K_LEFT]:
		vaisseau.Gauche()
	
	if key_pressed[K_SPACE] or key_pressed[K_UP] :
		vaisseau.Tirer()
	 
		
	#Re-collage
	fenetre.blit(fond, (0,0))
	
	indiceVie = 0 

	
	y2col1=randrange(-400,-200)
	y2col2=randrange(-400,-200)
	y2col3=randrange(-400,-200)

		
	for i in range(0,3):
		if score == buff+8:
			v1 += 1
			v2 += 1
			buff = score
						
		speed = randrange(v1,v2)
			
		for vaisseau.missile_rect in vaisseau.missiles:
			if pygame.Rect.colliderect(grpmeteo[i], vaisseau.missile_rect):
				score += 1 
				print(score)
				grpmeteo[i].move_ip(1000,1000)
				vaisseau.missiles.remove(vaisseau.missile_rect)
				
		if pygame.Rect.colliderect(grpmeteo[i], vaisseau.position):	
			if cdb == False:
				vaisseau.pv -= 1
				grpmeteo[i].move_ip(1000,1000)
				if vaisseau.pv <=0: 
					if score > int(bestscore):
						fichier = open("./best.txt", 'w')
						fichier.write(str(score))
						bestscore = score
					fichier.close()
					crash()
					
							
					 
		for i in range (0,3):
			
			if grpmeteo[i].y > 800 : # si on arrive en bas on réinitialise y
				grpmeteo[i].y = y2col1
				if i == 0:
					x2col1=randrange(0,100)
					grpmeteo[i].x= x2col1
				if i == 1:
					x2col2=randrange(150,250)
					grpmeteo[i].x= x2col2
				if i == 2:
					x2col3=randrange(300,450)
					grpmeteo[i].x= x2col3
			else : 
				grpmeteo[i]=grpmeteo[i].move(0,speed)
				fenetre.blit(imgmeteo, grpmeteo[i]) 
				
		
		if boost_rect.y > 800 : # si on arrive en bas on réinitialise y
			yboost=randrange(-2000,-1000)
			boost_rect.y = yboost
			xboost=randrange(0,500)
			boost_rect.x= xboost
		else : 
			boost_rect=boost_rect.move(0,1)
			fenetre.blit(boost,boost_rect)
			
		if boostvie_rect.y > 800 : # si on arrive en bas on réinitialise y
			yboost=randrange(-2000,-1000)
			boostvie_rect.y = yboost
			xboost=randrange(0,500)
			boostvie_rect.x= xboost
		else : 
			boostvie_rect=boostvie_rect.move(0,1)
			fenetre.blit(boostvie,boostvie_rect)
				
		if pygame.Rect.colliderect(boost_rect, vaisseau.position):	
			cdb = True
			boost_rect.move_ip(1000,1000)
			
		if pygame.Rect.colliderect(boostvie_rect, vaisseau.position):	
			if vaisseau.pv < 3:
				vaisseau.pv += 1
			boostvie_rect.move_ip(1000,1000)
				
	text = font.render("Score: {}".format(score), True, (255, 255, 255))
	fenetre.blit(text, (5,20))
		
	
	while indiceVie < vaisseau.pv:
		fenetre.blit(vaisseau.vie, (vaisseau.posviex + (50*indiceVie), vaisseau.posviey))
		indiceVie += 1
	
	for vaisseau.missile_rect in vaisseau.missiles:
		vaisseau.missile_rect.top -= 10
		if vaisseau.missile_rect.bottom < 0:
			vaisseau.missiles.remove(vaisseau.missile_rect)
	for vaisseau.missile_rect in vaisseau.missiles:
		fenetre.blit(vaisseau.image, vaisseau.position)
		fenetre.blit(vaisseau.missile,vaisseau.missile_rect)
	fenetre.blit(vaisseau.image, vaisseau.position)			
	
	if cdb == True:
		if cd < 250:	
			cd += 1
			logo_boost.x = 400
			logo_boost.y = 25
			fenetre.blit(boost,logo_boost)	
		else:
			cdb=False
			cd = 0
	print(cd)
	 
	#Rafraichissement

	pygame.display.flip()
	clock.tick(60)
