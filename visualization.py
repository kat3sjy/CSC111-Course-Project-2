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
import random
import webbrowser
from recommender import WeightedGraph

# pygame setup
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
return_button = None
rec_limit = None

#song_list = [("Comedy", "Gen Hoshino"), ("Ghost - Acoustic", "Ben Woodward"), ("To Begin Again", "Ingrid Michaelson"),
#             ("Can't Help Falling In Love", "Elvis Presley"), ("Hold On", "Chord Overstreet"),
#             ("Days I Will Remember", "Tyrone Wells")
#    , ("Say Something", "A Great Big World, Christina Aguilera")
#             ]
#song_links = ["https://open.spotify.com/track/5SuOikwiRyPMVoIQDJUgSV?si=4e3ec55401cc41ac",
#              "https://open.spotify.com/track/4qPNDBW1i3p13qLCt0Ki3A?si=2cd3b308ec274546",
#              "https://open.spotify.com/track/3vtfVhvGaHWss7t3BAd2il?si=bbe1e00d12c045c2",
#              "https://open.spotify.com/track/0pYDUAXXUanILl4FrDtdIt?si=6c81c87329524f35",
#              "https://open.spotify.com/track/5vjLSffimiIP26QG5WcN2K?si=4f1b8f1c3e0445f1",
#              "https://open.spotify.com/track/5T24Zh9FPZ7Ku6NjrJZmcn?si=2c7385138d044f5c",
#             "https://open.spotify.com/track/6Vc5wAMmXdKIAM7WUoEb7N?si=53aaac621aff41a3"]


# HERE IT ISSSSS:
#def get_spotify_search_url(track: str, artist: str) -> str:
#    """Generate a Spotify search URL from a track and artist."""
#    query = f"{track} {artist}"
#    return f"https://open.spotify.com/search/{query.replace(' ', '%20')}"

recommendations = []
dropdown_menu = []
listen_menu = []
limit_menu = []
song_names = []
dropdown_selected = [0, 0, 0, 0, 0, 0, 0]
limit_selected = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

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

def get_spotify_search_url(track: str, artist: str) -> str:
    """Generate a Spotify search URL from a track and artist."""
    query = f"{track} {artist}"
    return f"https://open.spotify.com/search/{query.replace(' ', '%20')}"

graph = load_graph('data/spotify_songs_smaller.csv')
all_vertices = list(graph.get_all_vertices())
sample_size = min(7, len(all_vertices))
random_songs = random.sample(all_vertices, sample_size)

song_list = []
for s in random_songs:
    vertex = graph.get_vertex(s)
    if vertex:
        meta = vertex.metadata
        song_list.append((meta['track_name'], meta['artists']))

dropdown_selected = [0] * len(song_list)

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
                        song_names.append(song_list[option][0])
                        dropdown_selected[option] += 1
                        error_message = False
                    elif listen_menu[option].collidepoint(event.pos):
                        track, artist = song_list[option]
                        url = get_spotify_search_url(track, artist)
                        webbrowser.open(url)

                if input_enter and input_enter.collidepoint(event.pos):
                    # print(song_names)
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

            elif current == "recommendations":
                if return_button and return_button.collidepoint(event.pos):
                    song_names = []
                    rec_limit = None
                    dropdown_selected = [0, 0, 0, 0, 0, 0, 0]
                    limit_selected = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    error_message = False
                    current = "recommender"

    # fill the screen with a color to delete anything from last frame
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
            screen.blit(question_text, (40, 60))

        # displaying question
        question_text = SUBTITLE_FONT.render("From the following list below, select some songs that you like.", True,
                                             (255, 255, 255))
        screen.blit(question_text, (40, 30))

        # enter button
        input_enter = pygame.draw.rect(screen, (29, 185, 84), (window_x // 2 + 300, 640, 250, 50), 0)
        enter_text = SUBTITLE_FONT.render("NEXT", True, (255, 255, 255))
        screen.blit(enter_text, (window_x // 2 + 380, 647))

        # song options to choose from
        for i in range(7):
            # song options
            dropdown_option = pygame.draw.rect(screen, (255, 255, 255), (40, 100 + (75 * i), 820, 60), 1)
            dropdown_text = PARAGRAPH_FONT.render(f"{song_list[i][0]} by {song_list[i][1]}", True, (255, 255, 255))
            screen.blit(dropdown_text, (110, 117 + (75 * i)))

            if dropdown_option not in dropdown_menu:
                dropdown_menu.append(dropdown_option)

            # checkbox (circle)
            if dropdown_selected[i] % 2 == 0:
                checkbox_colour = (255, 255, 255)
                checkbox_width = 1
                if song_list[i][0] in song_names:
                    song_names.remove(song_list[i][0])
            else:
                checkbox_colour = (29, 185, 84)
                checkbox_width = 0

            check_button = pygame.draw.circle(screen, checkbox_colour, (75, 130 + (75 * i)), 10, checkbox_width)

            # listen on spotify buttons
            listen_button = pygame.draw.rect(screen, (29, 185, 84), (880, 102 + (75 * i), 360, 50), 0)
            listen_button_text = BIG_PARAGRAPH_FONT.render("Listen", True, (255, 255, 255))
            screen.blit(listen_button_text, (1015, 109 + (75 * i)))

            if listen_button not in listen_menu:
                listen_menu.append(listen_button)


    elif current == "limit":

        if error_message:
            question_text = PARAGRAPH_FONT.render("Please choose a number.",
                                                  True,
                                                  (255, 255, 255))
            screen.blit(question_text, (510, 260))

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

        return_button = pygame.draw.rect(screen, (29, 185, 84), (window_x // 2 + 325, 100, 250, 50), 0)
        return_button_text = SUBTITLE_FONT.render("TRY AGAIN", True, (255, 255, 255))
        screen.blit(return_button_text, (window_x // 2 + 365, 107))

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()

# import python_ta
# python_ta.check_all(config={
#     'max-line-length': 120,
# })
