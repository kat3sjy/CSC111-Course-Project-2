"""CSC111 Winter 2025 Project: Spotify Song Recommendation System

This Python module contains the data and functions for a visual and
interactive system on Pygame.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2025 Cindy Yang, Kate Shen, Kristen Wong, Sara Kopilovic.
"""
import pygame
import csv
from recommender import WeightedGraph

# pygame setup waaaaaa
pygame.init()
screen = pygame.display.set_mode((1280, 720))
current = "home"
window_y = screen.get_height()
window_x = screen.get_width()
# title_x = 750
# title_y = 150
clock = pygame.time.Clock()
running = True
user_input_active = False
user_input_text = ''

# different fonts
TITLE_FONT = pygame.font.Font("Fonts/Audiowide/Audiowide-Regular.ttf", int(window_y * 0.06))
SUBTITLE_FONT = pygame.font.Font("Fonts/Audiowide/Audiowide-Regular.ttf", int(window_y * 0.04))
PARAGRAPH_FONT = pygame.font.Font("Fonts/Lexend/Lexend-VariableFont_wght.ttf", int(window_y * 0.03))
BIG_PARAGRAPH_FONT = pygame.font.Font("Fonts/Lexend/Lexend-VariableFont_wght.ttf", int(window_y * 0.04))

start_button = None
user_input = None
input_enter = None
test_button = None
limit_enter = None

song_list = ["Comedy", "Ghost - Acoustic", "To Begin Again", "Can't Help Falling In Love", "Hold On", "Days I Will Remember",
             "Say Something"]
song_names = []
recommendations = []
dropdown_menu = []
dropdown_selected = [0, 0, 0, 0, 0, 0, 0]
limit_selected = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
limit_menu = []
rec_limit = None

error_message = False


def load_graph(songs_file: str) -> WeightedGraph:
    """Load song data and build similarity graph."""
    graph = WeightedGraph()
    songs = []

    with open(songs_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)

        for row in reader:
            try:
                metadata = {
                    'track_name': row[3],
                    'artists': row[1],
                    'album_name': row[2],
                    'popularity': float(row[4]),
                    'danceability': float(row[7]),
                    'energy': float(row[8]),
                    'valence': float(row[16]),
                    'tempo': float(row[17]),
                    'loudness': float(row[9]),
                    'acousticness': float(row[11]),
                    'instrumentalness': float(row[12])
                }
                track_name = metadata['track_name']
                graph.add_vertex(track_name, metadata)
                songs.append(track_name)
            except (IndexError, ValueError):
                continue

    for i in range(len(songs)):
        song1 = songs[i]
        if song1 not in graph.get_all_vertices():
            continue

        similarities = []
        for j in range(i + 1, len(songs)):
            song2 = songs[j]
            if song2 not in graph.get_all_vertices():
                continue

            similarity = graph.get_similarity_score(song1, song2)
            if similarity > 0.3:  # Threshold
                similarities.append((song2, similarity))

        # Keep top 20 most similar songs
        similarities.sort(key=lambda x: -x[1])
        for song2, similarity in similarities[:20]:
            graph.add_edge(song1, song2, similarity)

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
                        dropdown_selected[option] += 1
                        error_message = False

                if input_enter and input_enter.collidepoint(event.pos):
                    print(song_names)
                    if not song_names:
                        error_message = True
                    else:
                        current = "limit"

            elif current == "limit":
                for limit in range(len(limit_menu)):
                    if limit_menu[limit].collidepoint(event.pos):
                        if limit_selected[limit] % 2 != 0:
                            rec_limit = None
                            limit_selected[limit] -= 1
                        elif any({x % 2 != 0 for x in limit_selected}):
                            pass
                        else:
                            limit_selected[limit] += 1
                            rec_limit = limit + 1
                            error_message = False


                if limit_enter and limit_enter.collidepoint(event.pos):
                    # Get recommendations
                    if rec_limit is not None:
                        recommendations = graph.recommend_songs(song_names, rec_limit)
                        current = "recommendations"
                    else:
                        error_message = True


    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    if current == "home":
        # title stuff
        title = TITLE_FONT.render("Spotify Recommender System", True, (255, 255, 255))
        screen.blit(title, (window_x // 2 - window_x * 0.28, window_y // 2 - window_y * 0.1))
        start_button = pygame.draw.rect(screen, (29, 185, 84),
                                        (window_x // 2 - window_x * 0.11, window_y // 2, 250, 50), 0)
        start_button_text = SUBTITLE_FONT.render("START", True, (255, 255, 255))
        screen.blit(start_button_text, (window_x // 2 - window_x * 0.052, window_y // 2 + window_y * 0.008))


    elif current == "recommender":

        if error_message:
            question_text = PARAGRAPH_FONT.render("Please select at least one song.",
                                                 True,
                                                 (255, 255, 255))
            screen.blit(question_text, (20, 55))

        # displaying question
        question_text = SUBTITLE_FONT.render("From the following list below, select some songs that you like.", True,
                                             (255, 255, 255))
        screen.blit(question_text, (20, 30))

        # enter button
        input_enter = pygame.draw.rect(screen, (255, 255, 255), (window_x // 2, 670, 250, 50), 0)
        enter_text = SUBTITLE_FONT.render("ENTER", True, (0, 0, 0))
        screen.blit(enter_text, (window_x // 2, 670))

        # song options to choose from
        for i in range(7):
            # song options
            dropdown_option = pygame.draw.rect(screen, (255, 255, 255), (20, 100 + (75 * i), 800, 60), 1)
            dropdown_text = PARAGRAPH_FONT.render(f"{song_list[i]}", True, (255, 255, 255))
            screen.blit(dropdown_text, (90, 117 + (75 * i)))

            # checkbox (circle)
            if dropdown_selected[i] % 2 == 0:
                checkbox_colour = (255, 255, 255)
                checkbox_width = 1
                if song_list[i] in song_names:
                    song_names.remove(song_list[i])
            else:
                checkbox_colour = (29, 185, 84)
                checkbox_width = 0

            check_button = pygame.draw.circle(screen, checkbox_colour, (55, 130 + (75 * i)), 10, checkbox_width)

            if dropdown_option not in dropdown_menu:
                dropdown_menu.append(dropdown_option)


    elif current == "limit":

        if error_message:
            question_text = PARAGRAPH_FONT.render("Please choose a number.",
                                                 True,
                                                 (255, 255, 255))
            screen.blit(question_text, (20, 55))

        question_text = SUBTITLE_FONT.render("Choose the number of recommendations you want from 1-10", True,
                                             (255, 255, 255))
        screen.blit(question_text, (160, 230))

        for i in range(10):

            if limit_selected[i] % 2 != 0:
                limit_colour = (29, 185, 84)
                limit_width = 0
            else:
                limit_colour = (255, 255, 255)
                limit_width = 1

            num_recs = pygame.draw.rect(screen, limit_colour, (70 + (114 * i), window_y // 2 - 50, 100, 100),
                                        limit_width)
            num_recs_text = SUBTITLE_FONT.render(f"{i + 1}", True, (255, 255, 255))
            if i < 10:
                screen.blit(num_recs_text, (108 + (114 * i), window_y // 2 - 20))
            else:
                screen.blit(num_recs_text, (100 + (114 * i), window_y // 2 - 20))

            if num_recs not in limit_menu:
                limit_menu.append(num_recs)

        limit_enter = pygame.draw.rect(screen, (29, 185, 84), (window_x // 2 - 125, 460, 250, 50), 0)
        limit_enter_text = SUBTITLE_FONT.render("ENTER", True, (255, 255, 255))
        screen.blit(limit_enter_text, (window_x // 2 - 55, 467))

    elif current == "recommendations":
        question_text = TITLE_FONT.render("Song Recommendations:", True,
                                          (255, 255, 255))
        screen.blit(question_text, (80, 100))

        for i, rec in enumerate(recommendations, 1):
            question_text = BIG_PARAGRAPH_FONT.render(f"{i}. {rec['track']} by {rec['artist']} ({rec['score']:.2f})",
                                                      True,
                                                      (255, 255, 255))
            screen.blit(question_text, (80, 140 + (50 * i)))

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()

# import python_ta
# python_ta.check_all(config={
#     'max-line-length': 120,
# })
