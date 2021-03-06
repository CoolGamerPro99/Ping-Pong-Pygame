import pygame, sys, random, os
from pygame.locals import *

class Block(pygame.sprite.Sprite):
	def __init__(self,path,x_pos,y_pos):
		super().__init__()
		self.image = pygame.image.load(path)
		self.rect = self.image.get_rect(center = (x_pos,y_pos))

class Player(Block):
	def __init__(self,path,x_pos,y_pos,speed):
		super().__init__(path,x_pos,y_pos)
		self.speed = speed
		self.movement = 0

	def screen_constrain(self):
		if self.rect.top <= 0:
			self.rect.top = 0
		if self.rect.bottom >= screen.get_height():
			self.rect.bottom = screen.get_height()

	def update(self,ball_group):
		self.rect.y += self.movement
		self.screen_constrain()

class Ball(Block):
	def __init__(self,path,x_pos,y_pos,speed_x,speed_y,paddles):
		super().__init__(path,x_pos,y_pos)
		self.speed_x = ball_speedX * random.choice((-1,1))
		self.speed_y = ball_speedY * random.choice((-1,1))
		self.paddles = paddles
		self.active = False
		self.score_time = 0

	def update(self):
		if self.active:
			self.rect.x += self.speed_x
			self.rect.y += self.speed_y
			self.collisions()
		else:
			self.restart_counter()
		
	def collisions(self):
		if self.rect.top <= 0 or self.rect.bottom >= screen.get_height():
			pygame.mixer.Sound.play(plob_sound)
			self.speed_y *= -1.0005
			self.speed_x *= 1.0005

		if pygame.sprite.spritecollide(self,self.paddles,False):
			pygame.mixer.Sound.play(plob_sound)
			collision_paddle = pygame.sprite.spritecollide(self,self.paddles,False)[0].rect
			if abs(self.rect.right - collision_paddle.left) < 10 and self.speed_x > 0:
				self.speed_x *= -1.0005
				self.speed_y *= 1.0005
				print("x=",self.speed_x,"y=",self.speed_y)
			if abs(self.rect.left - collision_paddle.right) < 10 and self.speed_x < 0:
				self.speed_x *= -1.0005
				self.speed_y *= 1.0005
			if abs(self.rect.top - collision_paddle.bottom) < 10 and self.speed_y < 0:
				self.rect.top = collision_paddle.bottom
				self.speed_y *= -1.0005
				self.speed_x *= 1.0005
			if abs(self.rect.bottom - collision_paddle.top) < 10 and self.speed_y > 0:
				self.rect.bottom = collision_paddle.top
				self.speed_y *= -1.0005
				self.speed_x *= 1.0005

	def reset_ball(self):
		self.active = False
		self.speed_x *= random.choice((-1,1))
		self.speed_y *= random.choice((-1,1))
		self.score_time = pygame.time.get_ticks()
		self.rect.center = (screen.get_width()/2,screen.get_height()/2)
		pygame.mixer.Sound.play(score_sound)

	def restart_counter(self):
		current_time = pygame.time.get_ticks()
		countdown_number = 3

		if current_time - self.score_time <= 700:
			countdown_number = 3
		if 700 < current_time - self.score_time <= 1400:
			countdown_number = 2
		if 1400 < current_time - self.score_time <= 2100:
			countdown_number = 1
		if current_time - self.score_time >= 2100:
			self.active = True

		time_counter = basic_font.render(str(countdown_number),True,accent_color)
		time_counter_rect = time_counter.get_rect(center = (screen.get_width()/2,screen.get_height()/2 + 50))
		pygame.draw.rect(screen,bg_color,time_counter_rect)
		screen.blit(time_counter,time_counter_rect)

class Opponent(Block):
	def __init__(self,path,x_pos,y_pos,speed):
		super().__init__(path,x_pos,y_pos)
		self.speed = speed

	def update(self,ball_group):
		if self.rect.top < ball_group.sprite.rect.y:
			self.rect.y += self.speed
		if self.rect.bottom > ball_group.sprite.rect.y + random.choice((0,20)):
			self.rect.y -= self.speed
		self.constrain()

	def constrain(self):
		if self.rect.top <= 0:
			self.rect.top = 0
		if self.rect.bottom >= screen.get_height():
			self.rect.bottom = screen.get_height()

class GameManager:
	def __init__(self,ball_group,paddle_group):
		self.player_score = 0
		self.opponent_score = 0
		self.ball_group = ball_group
		self.paddle_group = paddle_group

	def run_game(self):
		# Drawing the game objects
		self.paddle_group.draw(screen)
		self.ball_group.draw(screen)

		# Updating the game objects
		self.paddle_group.update(self.ball_group)
		self.ball_group.update()
		self.reset_ball()
		self.draw_score()

	def reset_ball(self):
		if self.ball_group.sprite.rect.right >= screen.get_width():
			self.opponent_score += 1
			self.ball_group.sprite.reset_ball()
		if self.ball_group.sprite.rect.left <= 0:
			self.player_score += 1
			self.ball_group.sprite.reset_ball()

	def draw_score(self):
		player_score = basic_font.render(str(self.player_score),True,accent_color)
		opponent_score = basic_font.render(str(self.opponent_score),True,accent_color)

		player_score_rect = player_score.get_rect(midleft = (screen.get_width() / 2 + 40,screen.get_height()/2))
		opponent_score_rect = opponent_score.get_rect(midright = (screen.get_width() / 2 - 40,screen.get_height()/2))

		screen.blit(player_score,player_score_rect)
		screen.blit(opponent_score,opponent_score_rect)

	def reset_everything(self):
		self.player_score = 0
		self.opponent_score = 0
		ball.reset_ball()

def draw_text(text, font, color, surface, x, y):
	textobj = font.render(text, 1, color)
	textrect = textobj.get_rect()
	textrect.topleft = (x, y)
	screen.blit(textobj, textrect)

# All the path variables
current_path = os.path.dirname(__file__)
assets_path = os.path.join(current_path, 'assets')
image_path = os.path.join(assets_path, 'images')
sound_path = os.path.join(assets_path, 'sounds')

# General setup
pygame.mixer.pre_init(44100,-16,2,512)
pygame.init()
clock = pygame.time.Clock()
FPS = 120

# Music
pygame.mixer_music.load(os.path.join(sound_path, 'game_music.mp3'))
pygame.mixer_music.play(-1)

# Main Window
iconImg = pygame.image.load(os.path.join(image_path, 'icon.ico'))
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
pygame.display.set_caption('Pong')
pygame.display.set_icon(iconImg)

# Global Variables
ball_speedX = 6
ball_speedY = 4
bg_color = pygame.Color('#2F373F')
accent_color = (27,35,43)
red = (255, 0, 0)
red_accent = (220,0,0)
basic_font = pygame.font.Font('freesansbold.ttf', 32)
plob_sound = pygame.mixer.Sound(os.path.join(sound_path, 'pong.ogg'))
score_sound = pygame.mixer.Sound(os.path.join(sound_path, 'score.ogg'))
middle_strip = pygame.Rect(screen.get_width()/2 - 2,0,4,screen.get_height())

# Buttons rectangles
start_button = pygame.Rect(screen.get_width()/2 - 110, screen.get_height()/2 - 160, 200, 60)
options_button = pygame.Rect(screen.get_width()/2 - 110, screen.get_height()/2, 200, 60)
resume_button = pygame.Rect(screen.get_width()/2 - 110, screen.get_height()/2 - 160, 200, 60)
main_menu_button = pygame.Rect(screen.get_width()/2 - 140, screen.get_height()/2 + 180, 250, 60)
exit_button = pygame.Rect(screen.get_width()/2 - 110, screen.get_height()/2 + 150, 200, 60)
stop_music_button = pygame.Rect(screen.get_width()/2 - 270, screen.get_height()/2 - 150, 210, 60)
start_music_button = pygame.Rect(screen.get_width()/2 - 20, screen.get_height()/2 - 150, 210, 60)
back_pause_button = pygame.Rect(screen.get_width()/2 - 140, screen.get_height()/2 + 180, 210, 60)

# Game objects
player = Player(os.path.join(image_path, 'Paddle.png'),screen.get_width() - 20,screen.get_height()/2,6)
opponent = Opponent(os.path.join(image_path, 'Paddle.png'),20,screen.get_width()/2+10,7)
paddle_group = pygame.sprite.Group()
paddle_group.add(player)
paddle_group.add(opponent)

ball = Ball(os.path.join(image_path, 'Ball.png'),screen.get_width()/2,screen.get_height()/2,ball_speedX,ball_speedY,paddle_group)
ball_sprite = pygame.sprite.GroupSingle()
ball_sprite.add(ball)

game_manager = GameManager(ball_sprite,paddle_group)

# All scenes
def main_menu():
	pygame.mouse.set_visible(True)
	pygame.mixer_music.unpause()
	pygame.mixer_music.set_volume(1)
	alt = False
	click = False
	while True:
		# Background
		screen.fill(bg_color)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				click = True
				while click:
					if pygame.Rect.collidepoint(start_button, pygame.mouse.get_pos()):
						game_manager.reset_everything()
						main_game()
						click = False
					if pygame.Rect.collidepoint(exit_button, pygame.mouse.get_pos()):
						pygame.quit()
						sys.exit()
					if pygame.Rect.collidepoint(options_button, pygame.mouse.get_pos()):
						settings_menu()
			if event.type == pygame.MOUSEBUTTONUP:
				click = False

		# Draw stuff
		draw_text("Main Menu", basic_font, red, screen, screen.get_width()/2 - 100, screen.get_height()/2 - 300)
		pygame.draw.rect(screen,red,start_button)
		pygame.draw.rect(screen, red, exit_button)
		pygame.draw.rect(screen, red, options_button)

		# Hovering color change
		if screen.get_width()/2 - 110 + 200 > pygame.mouse.get_pos()[0] > screen.get_width()/2 - 110 and screen.get_height()/2 - 160 + 60 > pygame.mouse.get_pos()[1] > screen.get_height()/2 - 160:
			pygame.draw.rect(screen,red_accent,start_button)
		if screen.get_width()/2 - 110 + 200 > pygame.mouse.get_pos()[0] > screen.get_width()/2 - 110 and screen.get_height()/2 + 150 + 60 > pygame.mouse.get_pos()[1] > screen.get_height()/2 + 150:
			pygame.draw.rect(screen,red_accent,exit_button)
		if screen.get_width()/2 - 110 + 200 > pygame.mouse.get_pos()[0] > screen.get_width()/2 - 110 and screen.get_height()/2 + 60 > pygame.mouse.get_pos()[1] > screen.get_height()/2:
			pygame.draw.rect(screen,red_accent,options_button)
		
		# Draw more stuff
		draw_text("Play",basic_font,accent_color,start_button,screen.get_width()/2 - 50,screen.get_height()/2 - 145)
		draw_text("Exit",basic_font,accent_color,exit_button,screen.get_width()/2 - 50,screen.get_height()/2 + 165)
		draw_text("Settings",basic_font,accent_color,options_button,screen.get_width()/2 - 70,screen.get_height()/2 + 10)

		# Rendering
		pygame.display.flip()
		clock.tick(FPS)

def pause_menu():
	pygame.mouse.set_visible(True)
	pygame.mixer_music.unpause()
	pygame.mixer_music.set_volume(1)
	click = False
	while True:
		# Background
		screen.fill(bg_color)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				click = True
				if click == True:
					if pygame.Rect.collidepoint(resume_button, pygame.mouse.get_pos()):
						main_game()
						running = True
					if pygame.Rect.collidepoint(main_menu_button, pygame.mouse.get_pos()):
						main_menu()
					if pygame.Rect.collidepoint(options_button, pygame.mouse.get_pos()):
						pause_settings_menu()
			if event.type == pygame.MOUSEBUTTONUP:
				click = False

		# Draw stuff
		draw_text("Pause Menu", basic_font, red, screen, screen.get_width()/2 - 110, screen.get_height()/2 - 300)
		pygame.draw.rect(screen,red,resume_button)
		pygame.draw.rect(screen,red,main_menu_button)
		pygame.draw.rect(screen, red, options_button)

		if screen.get_width()/2 - 110 + 200 > pygame.mouse.get_pos()[0] > screen.get_width()/2 - 110 and screen.get_height()/2 - 160 + 60 > pygame.mouse.get_pos()[1] > screen.get_height()/2 - 160:
			pygame.draw.rect(screen,red_accent,resume_button)
		if screen.get_width()/2 - 110 + 200 > pygame.mouse.get_pos()[0] > screen.get_width()/2 - 110 and screen.get_height()/2 + 60 > pygame.mouse.get_pos()[1] > screen.get_height()/2:
			pygame.draw.rect(screen,red_accent,options_button)
		if screen.get_width()/2 - 140 + 250 > pygame.mouse.get_pos()[0] > screen.get_width()/2 - 140 and screen.get_height()/2 + 180 + 60 > pygame.mouse.get_pos()[1] > screen.get_height()/2 + 180:
			pygame.draw.rect(screen,red_accent,main_menu_button)

		# Draw more stuff
		draw_text("Resume",basic_font,accent_color,resume_button,screen.get_width()/2 - 70,screen.get_height()/2 - 145)
		draw_text("Back to Menu",basic_font,accent_color,main_menu_button,screen.get_width()/2 - 120,screen.get_height()/2 + 200)
		draw_text("Settings",basic_font,accent_color,options_button,screen.get_width()/2 - 70,screen.get_height()/2 + 10)

		# Rendering
		pygame.display.flip()
		clock.tick(FPS)

def settings_menu():
	pygame.mouse.set_visible(True)
	pygame.mixer_music.unpause()
	pygame.mixer_music.set_volume(1)
	click = False
	while True:
		# Background
		screen.fill(bg_color)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				click = True
				if click == True:
					if pygame.Rect.collidepoint(main_menu_button, pygame.mouse.get_pos()):
						main_menu()
					if pygame.Rect.collidepoint(stop_music_button, pygame.mouse.get_pos()):
						pygame.mixer_music.stop()
					if pygame.Rect.collidepoint(start_music_button, pygame.mouse.get_pos()):
						pygame.mixer_music.play(-1)
			if event.type == pygame.MOUSEBUTTONUP:
				click = False
			
		# Draw stuff
		draw_text("Settings", basic_font, red, screen, screen.get_width()/2 - 90, screen.get_height()/2 - 300)
		pygame.draw.rect(screen,red,main_menu_button)
		pygame.draw.rect(screen,red,stop_music_button)
		pygame.draw.rect(screen,red,start_music_button)

		if screen.get_width()/2 - 140 + 250 > pygame.mouse.get_pos()[0] > screen.get_width()/2 - 140 and screen.get_height()/2 + 180 + 60 > pygame.mouse.get_pos()[1] > screen.get_height()/2 + 180:
			pygame.draw.rect(screen,red_accent,main_menu_button)
		if screen.get_width()/2 - 270 + 210 > pygame.mouse.get_pos()[0] > screen.get_width()/2 - 270 and screen.get_height()/2 - 150 + 60 > pygame.mouse.get_pos()[1] > screen.get_height()/2 - 150:
			pygame.draw.rect(screen,red_accent,stop_music_button)
		if screen.get_width()/2 - 20 + 210 > pygame.mouse.get_pos()[0] > screen.get_width()/2 - 20 and screen.get_height()/2 - 150 + 60 > pygame.mouse.get_pos()[1] > screen.get_height()/2 - 150:
			pygame.draw.rect(screen,red_accent,start_music_button)

		# Draw more stuff
		draw_text("Back",basic_font,accent_color,main_menu_button,screen.get_width()/2 - 65,screen.get_height()/2 + 195)
		draw_text("Stop Music",basic_font,accent_color,stop_music_button,screen.get_width()/2 - 250,screen.get_height()/2 - 130)
		draw_text("Start Music",basic_font,accent_color,stop_music_button,screen.get_width()/2,screen.get_height()/2 - 130)

		# Rendering
		pygame.display.flip()
		clock.tick(FPS)

def pause_settings_menu():
	pygame.mouse.set_visible(True)
	pygame.mixer_music.unpause()
	pygame.mixer_music.set_volume(1)
	click = False
	while True:
		# Background
		screen.fill(bg_color)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				click = True
				if click == True:
					if pygame.Rect.collidepoint(main_menu_button, pygame.mouse.get_pos()):
						pause_menu()
					if pygame.Rect.collidepoint(stop_music_button, pygame.mouse.get_pos()):
						pygame.mixer_music.stop()
					if pygame.Rect.collidepoint(start_music_button, pygame.mouse.get_pos()):
						pygame.mixer_music.play(-1)
			if event.type == pygame.MOUSEBUTTONUP:
				click = False
			
		# Draw stuff
		draw_text("Settings", basic_font, red, screen, screen.get_width()/2 - 90, screen.get_height()/2 - 300)
		pygame.draw.rect(screen,red,back_pause_button)
		pygame.draw.rect(screen,red,stop_music_button)
		pygame.draw.rect(screen,red,start_music_button)

		if screen.get_width()/2 - 140 + 250 > pygame.mouse.get_pos()[0] > screen.get_width()/2 - 140 and screen.get_height()/2 + 180 + 60 > pygame.mouse.get_pos()[1] > screen.get_height()/2 + 180:
			pygame.draw.rect(screen,red_accent,back_pause_button)
		if screen.get_width()/2 - 270 + 210 > pygame.mouse.get_pos()[0] > screen.get_width()/2 - 270 and screen.get_height()/2 - 150 + 60 > pygame.mouse.get_pos()[1] > screen.get_height()/2 - 150:
			pygame.draw.rect(screen,red_accent,stop_music_button)
		if screen.get_width()/2 - 20 + 210 > pygame.mouse.get_pos()[0] > screen.get_width()/2 - 20 and screen.get_height()/2 - 150 + 60 > pygame.mouse.get_pos()[1] > screen.get_height()/2 - 150:
			pygame.draw.rect(screen,red_accent,start_music_button)

		# Draw more stuff
		draw_text("Back",basic_font,accent_color,back_pause_button,screen.get_width()/2 - 70,screen.get_height()/2 + 195)
		draw_text("Stop Music",basic_font,accent_color,stop_music_button,screen.get_width()/2 - 250,screen.get_height()/2 - 130)
		draw_text("Start Music",basic_font,accent_color,stop_music_button,screen.get_width()/2,screen.get_height()/2 - 130)

		# Rendering
		pygame.display.flip()
		clock.tick(FPS)

def main_game():
	pygame.mouse.set_visible(False)
	pygame.mixer_music.unpause()
	pygame.mixer_music.set_volume(0.5)
	running = True
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					pause_menu()
					running = False
				if event.key == pygame.K_UP or event.key == pygame.K_w:
					player.movement -= player.speed
				if event.key == pygame.K_DOWN or event.key == pygame.K_s:
					player.movement += player.speed
			if event.type == pygame.KEYUP:
				if event.key == pygame.K_UP or event.key == pygame.K_w:
					player.movement += player.speed
				if event.key == pygame.K_DOWN or event.key == pygame.K_s:
					player.movement -= player.speed
	
		# Background Stuff
		screen.fill(bg_color)
		pygame.draw.rect(screen,accent_color,middle_strip)
	
		# Run the game
		game_manager.run_game()

		# Rendering
		pygame.display.flip()
		clock.tick(FPS)

if __name__ == "__main__":		
	main_menu()
