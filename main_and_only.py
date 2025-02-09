import pygame
import math
import random

class Vector2:
    def __init__(self, x:float=0, y:float=0):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        return Vector2(self.x / scalar, self.y / scalar)
    
    def magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)
    
    def normalized(self):
        mag = self.magnitude()
        return Vector2(self.x / mag, self.y / mag) if mag != 0 else Vector2()
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y
    
    def __iter__(self):
        return iter((self.x, self.y))
    
    def __getitem__(self, index):
        return (self.x, self.y)[index]
    
    def __repr__(self):
        return f"Vector2({self.x}, {self.y})"

class Bullet():
    def __init__(self, pos, vel, damage, is_player):
        self.position = pos
        self.velocity = vel
        self.damage = damage
        self.is_player = is_player
    
    def update(self, player_vel):
        self.position += self.velocity - player_vel

class Gun():
    def __init__(self, am_of_bu, spread, bullet_speed, fire_rate, damage):
        self.amount_of_bullets = am_of_bu
        self.spread = spread
        self.bullet_speed = bullet_speed
        self.fire_rate = fire_rate
        self.damage = damage
        self.can_fire = True
        self.current_reload_time = 0

    def reload(self):
        self.can_fire = False
        self.current_reload_time = 0

    def reload_cooldown(self):
        if self.current_reload_time < self.fire_rate:
            self.current_reload_time += 1
        else:
            self.can_fire = True
            self.current_reload_time = 0

class SniperEnemy():
    def __init__(self, pos, og_sprite, gun):
        self.position = pos
        self.velocity = Vector2()
        
        self.original_sprite = og_sprite
        self.final_sprite = og_sprite
        self.final_rect = None
        
        self.should_move = False
        self.desired_distance = 300
        self.speed = 3

        self.angle = 0
        
        self.current_gun = Gun(5, 0, 10, 30, 1)
        self.bullets = []

    def update(self, player_vel):
        delta_pos = Vector2(400, 300) - self.position
        if math.sqrt((delta_pos.x**2) + (delta_pos.y**2)) > self.desired_distance:
            self.velocity = delta_pos.normalized() * self.speed
        else:
            self.velocity = Vector2()
        
        self.position += self.velocity - player_vel
        self.final_rect = self.final_sprite.get_rect()
        self.final_rect.center = (self.position.x, self.position.y)
        self.player_aim()
        
        if self.current_gun.can_fire and math.sqrt((delta_pos.x**2) + (delta_pos.y**2)) <= self.desired_distance:
            self.fire()
        else:
            self.current_gun.reload_cooldown()

    def get_pos(self):
        return Vector2(self.final_rect.topleft[0], self.final_rect.topleft[1])

    def angle_between_two_points(self, point1, point2):
        aim_vector = point2 - point1
        aim_angle = math.degrees(math.atan2(aim_vector.y, aim_vector.x))

        return aim_angle

    def player_aim(self):
        aim_angle = self.angle_between_two_points(Vector2(400,300), self.position)

        self.final_sprite = pygame.transform.rotate(self.original_sprite, -aim_angle + 90)
        self.angle = aim_angle
    
    def fire(self):
        if self.current_gun.can_fire == False: return
        print("hi")

        for i in range(self.current_gun.amount_of_bullets):
            bullet_position = self.position + (Vector2(math.cos(math.radians(self.angle)), math.sin(math.radians(self.angle))) * 20)
            
            angle = self.angle - 180
            if self.current_gun.spread > 0:
                angle += random.randrange(-self.current_gun.spread, self.current_gun.spread)

            bullet_velocity = Vector2(math.cos(math.radians(angle)), math.sin(math.radians(angle))) * self.current_gun.bullet_speed

            b = Bullet(bullet_position, bullet_velocity, 1, True)
            self.bullets.append(b)
        
        self.current_gun.reload()
    
    def get_bullets(self):
        return self.bullets

class Game():
    def __init__(self):
        pygame.init()

        self.WIDTH, self.HEIGHT = 800, 600

        # Create the window
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Shok's Low Budget Fortnite")

        # Player setup
        self.player_pos = Vector2(self.WIDTH // 2, self.HEIGHT // 2)
        self.player_speed = 5
        self.player_angle = 0

        self.original_player_sprite = pygame.image.load("sprites/white_triangle.png")
        self.original_player_sprite = pygame.transform.scale(self.original_player_sprite, (50, 50))


        self.player_rect = self.original_player_sprite.get_rect()

        self.final_player_sprite = self.original_player_sprite

        # Shooting
        self.current_gun = Gun(5, 0, 10, 30, 1)
        self.bullets = []

        self.bullet_sprite = pygame.image.load("sprites/white_circle.png")
        self.bullet_sprite = pygame.transform.scale(self.bullet_sprite, (10, 10))

        # Enemy Generation
        self.enemies = []
        self.enemy_sprite = pygame.image.load("sprites/bad_triangle.png")
        self.enemy_sprite = pygame.transform.scale(self.enemy_sprite, (50, 50))
        self.enemies.append(SniperEnemy(Vector2(400,300), self.enemy_sprite, self.current_gun))

        # Miscellaneous
        self.clock = pygame.time.Clock()
        self.room_sprite = pygame.image.load("sprites/room.png")
        self.room_sprite = pygame.transform.scale(self.room_sprite, (1500,1500))
        
        self.game_loop()

    def game_loop(self):
        running = True
        while running:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            if pygame.mouse.get_pressed()[0]: 
                self.fire()
            
            move_input = self.handle_input(pygame.key.get_pressed())

            self.player_pos += move_input.normalized() * self.player_speed
            self.player_rect.center = (self.player_pos.x, self.player_pos.y)

            self.player_aim()

            self.screen.fill((60, 100, 100))

            if self.current_gun.can_fire == False:
                self.current_gun.reload_cooldown()
            
            # drawing player
            final_rect = self.final_player_sprite.get_rect()
            final_rect.center = (400, 300)
            
            self.update_bullets(move_input.normalized() * self.player_speed)
            self.update_enemies(move_input.normalized() * self.player_speed)
            self.draw()
            self.screen.blit(self.final_player_sprite, final_rect.topleft)


            # Update the display
            pygame.display.flip()

    def handle_input(self, keys):
        move_input = Vector2()

        if keys[pygame.K_w]:
            move_input.y = -1
        if keys[pygame.K_s]:
            move_input.y = 1
        if keys[pygame.K_a]:
            move_input.x = -1
        if keys[pygame.K_d]:
            move_input.x = 1
        
        if keys[pygame.K_w] == False and keys[pygame.K_s] == False:
            move_input.y = 0
        if keys[pygame.K_a] == False and keys[pygame.K_d] == False:
            move_input.x = 0
        
        return move_input

    def angle_between_two_points(self, point1, point2):
        aim_vector = point2 - point1
        aim_angle = math.degrees(math.atan2(aim_vector.y, aim_vector.x))

        return aim_angle

    def update_enemies(self, player_vel):
        for enemy in self.enemies:
            enemy.update(player_vel)

    def camera_effect(self, actual_position):
        new_pos = actual_position - (self.player_pos - Vector2(400, 300))
        return new_pos

    def player_aim(self):
        mouse_pos = pygame.mouse.get_pos()
        aim_angle = self.angle_between_two_points(Vector2(400,300), Vector2(mouse_pos[0], mouse_pos[1]))

        self.final_player_sprite = pygame.transform.rotate(self.original_player_sprite, -aim_angle - 90)
        self.player_angle = aim_angle

    def update_bullets(self, vel):
        
        new_bullets = []
        for i in self.enemies:
            new_bullets.extend(i.get_bullets())
        
        new_bullets.extend(self.bullets)

        for bullet in new_bullets:
            bullet.update(vel)

    def draw(self):
        room_pos = self.camera_effect(Vector2(-350, -450))
        self.screen.blit(self.room_sprite, (room_pos.x, room_pos.y))

        new_bullets = []
        for i in self.enemies:
            new_bullets.extend(i.get_bullets())
        
        new_bullets.extend(self.bullets)

        for i in new_bullets:
            self.screen.blit(self.bullet_sprite, (i.position.x, i.position.y))
        
        for i in self.enemies:
            self.screen.blit(i.final_sprite, (i.get_pos().x, i.get_pos().y))
        
        #effect = pygame.image.load("sprites/effect.png")
        #self.screen.blit(effect, (0,0))

    def fire(self):
        if self.current_gun.can_fire == False: return

        for i in range(self.current_gun.amount_of_bullets):
            bullet_position = Vector2(400, 300) + (Vector2(math.cos(math.radians(self.player_angle)), math.sin(math.radians(self.player_angle))) * 20)
            
            angle = self.player_angle 
            if self.current_gun.spread > 0:
                angle += random.randrange(-self.current_gun.spread, self.current_gun.spread)

            bullet_velocity = Vector2(math.cos(math.radians(angle)), math.sin(math.radians(angle))) * self.current_gun.bullet_speed

            b = Bullet(bullet_position, bullet_velocity, 1, True)
            self.bullets.append(b)
        
        self.current_gun.reload()


game = Game()

pygame.quit()
