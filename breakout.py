#!/usr/bin/env python3

import pygame
import random
import sys
import time


class Overlay(pygame.sprite.Sprite):
    def __init__(self):
        # Equivalent statements:
        # pygame.sprite.Sprite.__init__(self)
        super(pygame.sprite.Sprite, self).__init__()
        self.image = pygame.Surface((800, 20))
        # self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.font = pygame.font.Font('freesansbold.ttf', 18)
        self.render('Score: 0        Lives: 5')

    def render(self, text):
        self.text = self.font.render(text, True, (255, 255, 255))
        self.image.blit(self.text, self.rect)

    def draw(self, screen):
        screen.blit(self.text, (0, 0))

    def update(self, score, lives):
        self.render('Score: ' + str(score) + '        Lives: ' + str(lives))


class Ship(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((48, 63))
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.image = pygame.image.load("assets/ship.png")
        self.rect.x = 375
        self.rect.y = 500

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Alien(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((32, 32))
        self.color = (0, 0, 0)
        self.image.fill(self.color)
        self.vector = [-1, 0]
        self.start = 0
        self.rect = self.image.get_rect()

    def update(self):
        if self.rect.x < self.start - 100 or self.rect.x > self.start + 150:
            self.vector[0] *= -1
        self.rect.x += self.vector[0]


class Bullet(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((2, 15))
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = 400
        self.rect.y = 485
        self.owner = 0
        self.vector = [0, 0]
        self.thud_sound = pygame.mixer.Sound('assets/thud.wav')

    def update(self, game, aliens, ship):
        if self.rect.y < 0:
            game.bullets.remove(self)
            # pygame.event.post(game.new_life_event)
        hitObject = pygame.sprite.spritecollideany(self, aliens)
        if hitObject and self.owner == 1:
            self.thud_sound.play()
            hitObject.kill()
            game.aliens.remove(hitObject)
            game.bullets.remove(self)
            game.score += 10
        if pygame.sprite.collide_rect(self, ship) and self.owner == 0:
            ship.kill()
            pygame.event.post(game.new_life_event)

        self.rect.x += self.vector[0]
        self.rect.y += self.vector[1]

class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super(pygame.sprite.Sprite, self).__init__()
        self.type = random.choice(['speed', 'explode', 'extra-life'])

class Game:
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(50)
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((800, 600))
        self.bullets = pygame.sprite.Group()
        self.bullets.add(Bullet())
        self.ship = Ship()
        self.new_life_event = pygame.event.Event(pygame.USEREVENT + 1)
        self.aliens = pygame.sprite.Group()
        self.overlay = Overlay()
        self.outro = Outro()
        self.screen.fill((0, 0, 0))
        self.ready = True
        self.score = 0
        self.lives = 1
        for i in range(0, 1):
            for j in range(0, 1):
                alien = Alien()
                alien.rect.x = j * 60 + 155
                alien.start = alien.rect.x
                alien.rect.y = i * 45
                if i == 0:
                    alien.image = pygame.image.load("assets/red-alien.png")
                elif i == 1:
                    alien.image = pygame.image.load("assets/yello-alien.png")
                elif i == 2:
                    alien.image = pygame.image.load("assets/fuscia-alien.png")
                else:
                    alien.image = pygame.image.load("assets/green-alien.png")

                self.aliens.add(alien)

    def run(self):
        self.done = False
        last_time = time.time() - 1
        fire_interval = random.randrange(1, 4, 1)
        enemy_hold = time.time()

        while not self.done:
            self.screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == self.new_life_event.type:
                    self.lives -= 1
                    if self.lives > -1:
                        self.ship = Ship()
                        self.ready = True
                    else:
                        self.outro.draw(self.screen, 'You Lose!')
                        self.done = True
                if event.type == pygame.QUIT:
                    self.done = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.ready:
                        this_time = time.time()
                        if this_time - last_time > 1:
                            bullet = Bullet()
                            bullet.image.fill((255, 255, 0))
                            bullet.vector = [0, -1]
                            bullet.owner = 1
                            bullet.rect.x = self.ship.rect.x + 23
                            self.bullets.add(bullet)
                            last_time = time.time()
                    if event.key == pygame.K_LEFT:
                        self.ship.rect.x -= 5
                        if self.ship.rect.x <= 0:
                            self.ship.rect.x = 0
                    if event.key == pygame.K_RIGHT:
                        self.ship.rect.x += 5
                        if self.ship.rect.x >= 750:
                            self.ship.rect.x = 750

            if len(self.aliens) == 0:
                self.outro.draw(self.screen, 'You win!')
                self.done = True
            else:
                enemy_fire = time.time()
                if enemy_fire - enemy_hold >= fire_interval:
                    angry_fellow = self.aliens.sprites()[random.randrange(0, len(self.aliens), 1)]
                    angry_bullet = Bullet()
                    angry_bullet.image.fill([255, 0, 0])
                    angry_bullet.vector = [0, 1]
                    angry_bullet.rect.x = angry_fellow.rect.x + 20
                    angry_bullet.rect.y = angry_fellow.rect.y + 35
                    self.bullets.add(angry_bullet)
                    enemy_hold = time.time()
                    fire_interval = random.randrange(1, 4, 1)

            self.bullets.update(self, self.aliens, self.ship)
            self.overlay.update(self.score, self.lives)
            self.aliens.update()
            self.bullets.draw(self.screen)
            self.ship.draw(self.screen)
            self.aliens.draw(self.screen)
            self.overlay.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(60)

        time.sleep(3)
        pygame.quit()
        sys.exit(0)

class Outro(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((800, 120))
        self.image.fill((255, 255, 255))
        self.font = pygame.font.Font('freesansbold.ttf', 96)
        self.rect = self.image.get_rect()

    def draw(self, screen, text):
        text = self.font.render(text, True, (0, 255, 255))
        screen.blit(text, (150, 200))

if __name__ == "__main__":
    game = Game()
    game.run()
