#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Perso.py
#  
#  Copyright 2019 Adriano_Meledina_-_6tb

import pygame

from pygame.locals import *

class Perso():
	def __init__(self):
		self.score = 0
		self.pvmax = 3
		self.pv = self.pvmax
		self.vie = pygame.image.load("vie.png").convert_alpha()
		self.vie= pygame.transform.scale(self.vie, (45,45))
		self.posviex = 450
		self.posviey = 15 
		self.image = pygame.image.load("vaisseau.png").convert_alpha()
		self.image= pygame.transform.scale(self.image, (80,80))
		self.last = pygame.time.get_ticks()
		self.cooldown = 300
		self.position = self.image.get_rect()
		self.position.x = 225
		self.position.y = 720
		self.missiles = []	
	
	def Tirer(self):
		now = pygame.time.get_ticks()
		if now - self.last >= self.cooldown:
			self.last = now
			self.missile = pygame.image.load("missile.png").convert_alpha()
			self.missile = pygame.transform.scale(self.missile, (13, 54 ) )
			self.original_missile_rect = self.missile.get_rect() # Utilisé pour placer des missiles
			self.missile_rect = self.original_missile_rect.copy()
			self.missile_rect.midbottom = self.position.midtop  
			self.missiles.append(self.missile_rect)
			print(self.missiles)
			
	def Droit(self):
		self.position.x += 6
		#~ print(self.position.x)
		 #limites
		while self.position.x >= 520:
			self.position.x = 519
		
	def Gauche(self):
		self.position.x -= 6
		#~ print(self.position.x)
		 #limites
		while self.position.x <= 0:
			self.position.x = 1
			

#~ class Item(self):
