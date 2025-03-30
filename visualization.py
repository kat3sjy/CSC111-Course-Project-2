import pygame
import csv
from recommender import WeightedGraph

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
current = "home"
window_y = screen.get_height()
window_x = screen.get_width()
title_x = 750
title_y = 150
clock = pygame.time.Clock()
running = True
user_input_active = False
user_input_text = ''

# different fonts
TITLE_FONT = pygame.font.Font("Fonts/Audiowide/Audiowide-Regular.ttf", int(window_y*0.06))
SUBTITLE_FONT = pygame.font.Font("Fonts/Audiowide/Audiowide-Regular.ttf", int(window_y*0.04))
PARAGRAPH_FONT = pygame.font.Font("Fonts/Lexend/Lexend-VariableFont_wght.ttf", 25)
BIG_PARAGRAPH_FONT = pygame.font.Font("Fonts/Lexend/Lexend-VariableFont_wght.ttf", 60)

start_button = None
user_input = None
input_enter = None
test_button = None

song_list = ["Comedy", "Ghost - Acoustic", "To Begin Again", "Can't Help Falling In Love", "Hold On"]
song_names = []
recommendations = []
dropdown_menu = []
limit_menu = []
rec_limit = None

def load_graph(songs_file: str) -> WeightedGraph:
    """Load song data using only essential features for similarity."""
    graph = WeightedGraph()

    with open(songs_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        headers = next(reader)  # Skip header row

        for row in reader:
            # Only store features we'll use for similarity
            metadata = {
                'track_name': row[3],  # track_name
                'artists': row[1],  # artists
                'album_name': row[2],  # album name
                'danceability': float(row[7]),  # danceability
                'energy': float(row[8]),  # energy
                'valence': float(row[16]),  # valence
                'tempo': float(row[17])  # tempo
            }

            graph.add_vertex(metadata['track_name'], metadata)

    # Create similarity edges
    songs = list(graph._vertices.values())
    for i, song1 in enumerate(songs):
        similarities = []
        for j, song2 in enumerate(songs):
            if i == j:
                continue
            similarity = song1.similarity_score(song2)
            similarities.append((song2, similarity))

        # Sort by similarity and keep top 20
        similarities.sort(key=lambda x: -x[1])
        for song2, similarity in similarities[:20]:
            if similarity > 0.3:  # Minimum similarity threshold
                graph.add_edge(song1.item, song2.item, similarity)

    return graph

graph = load_graph('data/spotify_songs_smaller.csv')

while running:

    mouse = pygame.mouse.get_pos()

    for event in pygame.event.get():
        # quitting the program
        if event.type == pygame.QUIT:
            running = False
        # clicking buttons
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if start_button and start_button.collidepoint(event.pos) and current == "home":
                current = "recommender"
            # elif user_input and user_input.collidepoint(event.pos) and current == "recommender":
            #     user_input_active = True
            elif current == "recommender":
                for option in range(len(dropdown_menu)):
                    if dropdown_menu[option].collidepoint(event.pos):
                        # print(dropdown_menu)
                        # print("option: ", option)
                        song_names.append(song_list[option])

                if input_enter and input_enter.collidepoint(event.pos):
                    current = "limit"

            elif current == "limit":
                for limit in range(len(limit_menu)):
                    if limit_menu[limit].collidepoint(event.pos):
                        rec_limit = limit

                # Get recommendations
                if rec_limit is not None:
                    recommendations = graph.recommend_songs(
                        [graph.find_song_id(name) for name in song_names],
                        rec_limit
                    )

                current = "recommendations"



        # # typing text
        # elif event.type == pygame.KEYDOWN:
        #         if user_input_active:
        #             if event.key == pygame.K_BACKSPACE:
        #                 user_input_text = user_input_text[:-1]
        #             else:
        #                 user_input_text += event.unicode

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    if current == "home":
        # title stuff
        title = TITLE_FONT.render("Spotify Recommender System", True, (255, 255, 255))
        screen.blit(title, (window_x // 2 - window_x*0.32, window_y // 2 - window_y*0.1))
        start_button = pygame.draw.rect(screen, (44, 201, 76), (window_x // 2 - window_x*0.11, window_y // 2, 500, 100), 0)
        start_button_text = SUBTITLE_FONT.render("START", True, (255,255,255))
        screen.blit(start_button_text, (window_x // 2 - window_x*0.05, window_y // 2 + window_y*0.008))

    elif current == "recommender":
        # displaying question
        question_text = SUBTITLE_FONT.render("From the following list below, select some songs that you like.", True, (255,255,255))
        screen.blit(question_text, (window_x // 2 - title_x/6, 200))

        # # user input
        # user_input = pygame.draw.rect(screen, (44, 201, 76), (window_x // 2 - title_x/3, window_y // 2, 500, 100), 0)
        # input_text = PARAGRAPH_FONT.render(user_input_text, True, (255,255,255))
        # screen.blit(input_text, (window_x // 2 - title_x/6, window_y // 2 +title_y/13))

        # enter button
        input_enter = pygame.draw.rect(screen, (255,255,255), (window_x // 2 - title_x/3, 400, 500, 100), 0)
        enter_text = SUBTITLE_FONT.render("ENTER", True, (0,0,0))
        screen.blit(enter_text, (window_x // 2 - title_x/6, title_y/13+400))

        for i in range(5):
            dropdown_option= pygame.draw.rect(screen, (255,255,255), (window_x // 2- title_x/3, window_y // 2 + (125*i), 2000, 100), 0)
            dropdown_text = SUBTITLE_FONT.render(f"{song_list[i]}", True, (0,0,0))
            screen.blit(dropdown_text, (window_x // 2 - title_x / 6, window_y // 2 + title_y / 13 + (125*i)))

            if dropdown_option not in dropdown_menu:
                dropdown_menu.append(dropdown_option)

    elif current == "limit":
        question_text = SUBTITLE_FONT.render("Choose the number of recommendations you want from 1-10", True,
                                             (255, 255, 255))
        screen.blit(question_text, (window_x // 2 - title_x / 6, 200))

        for i in range(10):
            num_recs = pygame.draw.rect(screen, (255,255,255), (10 + (125*i), window_y // 2, 100, 100), 0)
            num_recs_text = SUBTITLE_FONT.render(f"{i}", True, (0,0,0))
            screen.blit(num_recs_text, (10 + (125*i), window_y // 2))

            if num_recs not in limit_menu:
                limit_menu.append(num_recs)

    elif current == "recommendations":
        for i, rec in enumerate(recommendations, 1):

            question_text = SUBTITLE_FONT.render(f"{i}. {rec['track']} by {rec['artist']} ({rec['score']:.2f})", True, (255, 255, 255))
            screen.blit(question_text, (window_x // 2 - title_x / 6, 200+(100*i)))



    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()


# import python_ta
# python_ta.check_all(config={
#     'max-line-length': 120,
# })

