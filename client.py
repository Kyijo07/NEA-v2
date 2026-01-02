import pygame

pygame.init()

screen_width = 800
screen_height = 600
fps = 60
white = (255, 255, 255)

def main():
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Client")
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Instructions
        font = pygame.font.Font(None, 24)
        instructions = [""]
        for i, text in enumerate(instructions):
            rendered_text = font.render(text, True, white)
            screen.blit(rendered_text, (10, 10 + i * 25))

        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()
    quit()


if __name__ == "__main__":
    main()