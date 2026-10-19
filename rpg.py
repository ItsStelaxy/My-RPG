import pygame, sys, time, math



# future self: We need the following features: potions, then inventory, XP, NPC, change everything to classes, add more enemies
def collision_with_walls(walls, player):
    for wall in walls:
        if player.colliderect(wall):
            return True
    return False


def reset():
    global player_health, player_immunity, player_real_x, player_real_y, enemy_1_real_x, enemy_1_real_y, enemy_1_health, attacking_cooldown, melee_attack, player_facing_x, player_facing_y
    
    player_health = 10
    enemy_1_health = 5
    attacking_cooldown = 0
    melee_attack = False
    player_immunity = 0

    player_facing_x, player_facing_y = 1,0
    player.x = player_starting_x
    player.y = player_starting_y
    player_real_x = player_starting_x
    player_real_y = player_starting_y
    enemy_1.x, enemy_1.y = 200,200
    enemy_1_real_x, enemy_1_real_y = 200,200
    

pygame.init()
pygame.display.set_caption("Sami's RPG")

game_active = True
clock = pygame.time.Clock()
width, height = 1920, 1200
screen = pygame.display.set_mode((width, height), display = 0)
screen_rect = screen.get_rect()


player = pygame.Rect(960, 550, 45, 45)
player_real_x, player_real_y = 960, 550
movement_speed = 360
player_damage = 2
player_health = 10
player_immunity = 0
player_starting_x, player_starting_y = 0,0
melee_attack = False
player_facing_x, player_facing_y = 1,0

enemy_1 = pygame.Rect(200, 200, 45, 45)
enemy_1_speed = 300
enemy_1_real_x, enemy_1_real_y = 200, 200
enemy_1_damage = 1
enemy_1_health = 5
attacking_cooldown = 0

player_attacking_rect = pygame.Rect(player_starting_x, player_starting_y, 50, 50)

time_in_previous_frame = time.perf_counter()
FPS = 144
chase_range = 400
diagonal_factor = 0.7071
tile_size = 50
deadzone = 40
dt = 0 #time since last frame


#  use P for player spawn, . for empty space, # for walls
level_1_layout = [
    "####################",
    "#..............P...#",
    "#..................#",
    "#..................#",
    "#..................#",
    "#..................#",
    "#..................#",
    "#..................#",
    "#..................#",
    "#..................#",
    "#..................#",
    "#..................#",
    "#..................#",
    "#################..#"
]

level_1 = []

# level maker
for row_counter, row in enumerate(level_1_layout):
        for column_counter, char in enumerate(row):
            if char == '#':
                level_1.append(pygame.Rect((column_counter * tile_size, row_counter * tile_size, tile_size, tile_size)))
            elif char == 'P':
                player.topleft = (column_counter * tile_size, row_counter * tile_size)
                player_real_x = player.x # for syncing
                player_real_y = player.y # for syncing
                player_starting_x = column_counter * tile_size
                player_starting_y = row_counter * tile_size


while True:
    for event in pygame.event.get():
        
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()
        if game_active:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                melee_attack = True
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_active = True
                reset()

    screen.fill('White')


    
    if player_health <= 0:
        game_active = False
    else: game_active = True

    if game_active:

        # Player movement

        keys = pygame.key.get_pressed()
        direction_x = 0
        direction_y = 0
        
        # calculating direction
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            direction_y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            direction_y += 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            direction_x += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            direction_x -= 1

        if direction_x != 0 or direction_y != 0:     
            player_facing_x, player_facing_y = direction_x, direction_y

        if direction_x != 0 and direction_y != 0:     # if we're going diagonally
            direction_x *= diagonal_factor
            direction_y *= diagonal_factor            # multiplying by 0.7(diagonal_factor) removes the extra 41% distance from moving diagonally
            player_facing_x, player_facing_y = direction_x, direction_y

        # distance = speed * time
        player_real_x += direction_x * movement_speed * dt
        player.x = player_real_x                      # we copy it so we dont chop off the decimals because rect doesnt allow decimals

        if collision_with_walls(level_1, player): 
            player_real_x -= direction_x * movement_speed * dt
            player.x = player_real_x
        
        # distance = speed * time
        player_real_y += direction_y * movement_speed * dt
        player.y = player_real_y                      # we copy it so we dont chop off the decimals since rect doesnt allow decimals
        
        if collision_with_walls(level_1, player):
            player_real_y -= direction_y * movement_speed * dt
            player.y = player_real_y


        player_position_before_clamp = player.topleft
        player.clamp_ip(screen_rect)
        if player.topleft != player_position_before_clamp:    # bug wherein after you clamp in place the player_real rect doesnt get clamped
            player_real_x, player_real_y = player.topleft


        

        # Enemy movement

        enemy_1_direction_x = 0
        enemy_1_direction_y = 0

        dx = player.centerx - enemy_1.centerx    # positive: player is to the right
        dy = player.centery - enemy_1.centery    # positive: player is below

        if math.hypot(dx, dy) < chase_range and enemy_1_health > 0:
            if dx > deadzone:
                enemy_1_direction_x += 1
            if dx < -deadzone:
                enemy_1_direction_x -= 1
            if dy > deadzone:
                enemy_1_direction_y += 1
            if dy < -deadzone:
                enemy_1_direction_y -= 1

            if enemy_1_direction_x != 0 and enemy_1_direction_y != 0:
                enemy_1_direction_y *= diagonal_factor
                enemy_1_direction_x *= diagonal_factor

            enemy_1_real_x += enemy_1_direction_x * enemy_1_speed * dt
            enemy_1.x = enemy_1_real_x
            if collision_with_walls(level_1, enemy_1):
                enemy_1_real_x -= enemy_1_direction_x * enemy_1_speed * dt
                enemy_1.x = enemy_1_real_x

            enemy_1_real_y += enemy_1_direction_y * enemy_1_speed * dt
            enemy_1.y = enemy_1_real_y
            if collision_with_walls(level_1, enemy_1):
                enemy_1_real_y -= enemy_1_direction_y * enemy_1_speed * dt
                enemy_1.y = enemy_1_real_y
        

        # health and damaging
        # player getting attacked
        if enemy_1.colliderect(player) and player_immunity == 0 and enemy_1_health > 0:
            player_health -= enemy_1_damage
            player_immunity = time.perf_counter()

        if (time.perf_counter() - player_immunity) > 2:
            player_immunity = 0

        player_health_outline = pygame.Rect(player.centerx - 50, player.centery - 50, 100 , 20)
        player_health_drawing = pygame.Rect(player.centerx - 50, player.centery - 50, 10*player_health , 20)

        # player attacking enemy

        if enemy_1_health > 0:
            enemy_1_health_outline = pygame.Rect(enemy_1.centerx - 50, enemy_1.centery - 50, 100 , 20)
            enemy_1_health_drawing = pygame.Rect(enemy_1.centerx - 50, enemy_1.centery - 50, 20*enemy_1_health , 20)

        
        player_attacking_rect.center = (player.centerx + 50*player_facing_x, player.centery +50 * player_facing_y)

        if melee_attack: 
            if attacking_cooldown == 0 and enemy_1_health >0:
                if player_attacking_rect.colliderect(enemy_1): # got a hit
                    enemy_1_health -= player_damage
                    attacking_cooldown = time.perf_counter()
                    melee_attack = False
                else:                                          # missed the attack 
                    melee_attack = False
            elif attacking_cooldown != 0:
                melee_attack = False

        if (time.perf_counter() - attacking_cooldown) > 1:
            attacking_cooldown = 0

    
        for wall in level_1:
            pygame.draw.rect(screen, "gold", wall)
        pygame.draw.rect(screen, "blue", player)
        pygame.draw.rect(screen, "Red", player_health_drawing)
        pygame.draw.rect(screen, "Black", player_health_outline, 4)
       

        if enemy_1_health > 0:
            pygame.draw.rect(screen, "red", enemy_1)
            pygame.draw.rect(screen, "Red", enemy_1_health_drawing)
            pygame.draw.rect(screen, "Black", enemy_1_health_outline, 4)
        


    else: # game is not active
        screen.fill("red")



    pygame.display.update()
    # for fps and movement (delta time)
    clock.tick(FPS)
    time_in_this_frame = time.perf_counter()
    dt = time_in_this_frame - time_in_previous_frame
    time_in_previous_frame = time_in_this_frame