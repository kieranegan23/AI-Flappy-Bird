import pygame
import random
import sys
from NN import NeuralNetwork

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 400, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 36)

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

# Bird settings
BIRD_X = 50
BIRD_SIZE = 30
GRAVITY = 1
FLAP_POWER = -10

# Pipe settings
PIPE_WIDTH = 40
PIPE_FREQUENCY = 2400
PIPE_GAP = 150
PIPE_SPEED = 5

# Bird
class Bird:
    def __init__(self):
        self.alive = True
        self.score = 0
        self.y = HEIGHT // 2
        self.vel = 0
        self.rect = pygame.Rect(BIRD_X, self.y, BIRD_SIZE, BIRD_SIZE)
        
        # color assignment
        gray_shade = random.randint(0, 100)  # 0 = black, 100 = light gray
        self.color = (gray_shade, gray_shade, gray_shade)
        
        # Nueral Network
        self.nn = NeuralNetwork(5,6,1)
       
        # game status
        self.passed_pipes = set()
        self.frames_alive = 0
        self.fitness = 0

    def think(self, next_pipe):
        inputs = [
            self.y / HEIGHT,                             # 1 bird y-position
            (self.vel + 9) / 32,                         # 2 bird velocity
            next_pipe.height / HEIGHT,                   # 3 height of top pipe
            (next_pipe.height + PIPE_GAP) / HEIGHT, # 4 height of botttom pipe
            (next_pipe.x - self.rect.x) / WIDTH          # 5 horizontal distance to pipe
        ]
        output = self.nn.feedForward(inputs)
        return output > 0.75

    def update(self):
        self.vel += GRAVITY
        self.y += self.vel
        self.rect.y = int(self.y)
        self.frames_alive += 1

    def flap(self):
        self.vel = FLAP_POWER

    def draw(self):
        if not self.alive:
            return

        center_x = self.rect.x + self.rect.width // 2
        center_y = self.rect.y + self.rect.height // 2
        radius = BIRD_SIZE // 2
        pygame.draw.circle(SCREEN, self.color, (center_x, center_y), radius)

# Pipe
class Pipe:
    PIPE_ID_COUNTER = 0

    def __init__(self):
        self.x = WIDTH
        self.height = random.randint(50, HEIGHT - PIPE_GAP - 50)
        self.top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.height)
        self.bottom_rect = pygame.Rect(self.x, self.height + PIPE_GAP, PIPE_WIDTH, HEIGHT - self.height - PIPE_GAP)
        self.id = Pipe.PIPE_ID_COUNTER
        Pipe.PIPE_ID_COUNTER += 1
    
    def update(self):
        self.x -= PIPE_SPEED
        self.top_rect.x = int(self.x)
        self.bottom_rect.x = int(self.x)

    def draw(self):
        pygame.draw.rect(SCREEN, GREEN, self.top_rect)
        pygame.draw.rect(SCREEN, GREEN, self.bottom_rect)

# Return birds with best fitness score
def select_best(birds, num_survivors):
    birds.sort(key=lambda b: b.fitness, reverse=True)
    return birds[:num_survivors]

# Return new generation of birds with different qualities
def breed(birds, population_size,  mutationRate=0.025, mutationStrength=0.25):
    new_generation = []

    while len(new_generation) < population_size:
        parent = random.choice(birds)
        child = Bird()
        child.nn = parent.nn.copy()
        child.nn.mutate(mutationRate, mutationStrength)
        new_generation.append(child)

    return new_generation

def main():
    best_score = 0
    generation = 1
    POPULATION_SIZE = 1000
    birds = [Bird() for _ in range(POPULATION_SIZE)]

    while True:
        pipes = [Pipe()]
        last_pipe = pygame.time.get_ticks()
        score = 0
        running = True

        while running:
            CLOCK.tick(120)
            SCREEN.fill(WHITE)

            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # AI Logic
            next_pipe = None
            for pipe in pipes:
                if pipe.x + PIPE_WIDTH > BIRD_X:
                    next_pipe = pipe
                    break
            for bird in birds:
                if not bird.alive or next_pipe is None:
                    continue
                if bird.think(next_pipe):
                    bird.flap()
                
            # Create pipes
            now = pygame.time.get_ticks()
            if now - last_pipe > PIPE_FREQUENCY:
                pipes.append(Pipe())
                last_pipe = now

            # Update bird
            for bird in birds:
                if not bird.alive:
                    continue
                bird.update()
                    

            # Update pipes
            for pipe in pipes:
                pipe.update()

            # Remove off-screen pipes
            pipes = [pipe for pipe in pipes if pipe.x + PIPE_WIDTH > 0]

            # Collision detection
            for bird in birds:
                if not bird.alive:
                    continue
                for pipe in pipes:
                    if bird.rect.colliderect(pipe.top_rect) or bird.rect.colliderect(pipe.bottom_rect):
                        bird.alive = False
                if bird.rect.top <= 0 or bird.rect.bottom >= HEIGHT:
                        bird.alive = False

            # Draw everything
            for bird in birds:
                bird.draw()
            for pipe in pipes:
                pipe.draw()

            # Score: number of pipes passed
            for bird in birds:
                if not bird.alive:
                    continue
                for pipe in pipes:
                    pipe_id = pipe.id
                    if pipe.x + PIPE_WIDTH < BIRD_X and pipe_id not in bird.passed_pipes:
                        bird.passed_pipes.add(pipe_id)
                        bird.score += 1

            current_score = max((bird.score for bird in birds), default=0)
            
            # Win screen when score reaches 50
            if current_score >= 50:
                SCREEN.fill((255, 255, 0))  
                win_text = FONT.render("YOU WIN!", True, (0, 0, 0))  
                gen_text = FONT.render(f"GENERATIONS: {generation}", True, (0, 0, 0))
                SCREEN.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - 40))
                SCREEN.blit(gen_text, (WIDTH // 2 - gen_text.get_width() // 2, HEIGHT // 2 + 10))
                pygame.display.update()
                pygame.time.wait(10000)  
                pygame.quit()
                sys.exit()

            #best score
            if current_score > best_score:
                best_score = current_score

            # Displays Score, generation count, etc...
            score_surface = FONT.render(f"Score: {current_score}", True, (0,0,0))
            best_score_surface = FONT.render(f"Best: {best_score}", True, (0,0,0))
            birds_alive = sum(1 for bird in birds if bird.alive)
            alive_surface = FONT.render(f"Alive: {birds_alive}", True, (0,0,0))
            generation_surface = FONT.render(f"Generation: {generation}", True, (0, 0, 0))  
            SCREEN.blit(generation_surface, (WIDTH - 180, 10))
            SCREEN.blit(score_surface, (10, 10))
            SCREEN.blit(best_score_surface, (10, 50))
            SCREEN.blit(alive_surface, (WIDTH - alive_surface.get_width() - 10, 50))
            pygame.display.update()

            if all(not bird.alive for bird in birds):
                running = False
            
            pygame.display.update()
            CLOCK.tick(60)

        for bird in birds:
            bird.fitness = bird.score * 100 + bird.frames_alive

        any_success = any(bird.score > 0 for bird in birds)
        
        # Mutation process
        if any_success:
            survivors = select_best(birds, 5)
            num_elite = 5
            elite = []
            for i in range(num_elite):
                elite_bird = Bird()
                elite_bird.nn = survivors[i].nn.copy()
                elite.append(elite_bird)
            children = breed(survivors, POPULATION_SIZE - num_elite, mutationRate=0.05, mutationStrength=0.75)
            birds = elite + children
        else:
            # Retry the same generation
            birds = [Bird() for _ in range(POPULATION_SIZE)]

        generation += 1


if __name__ == "__main__":
    main()
