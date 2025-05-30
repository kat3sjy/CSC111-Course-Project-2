"""CSC111 Winter 2025 Project: Spotify Song Recommendation System

This Python module is the main module where the program is run.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2025 Cindy Yang, Kate Shen, Kristen Wong, Sara Kopilovic.
"""
from __future__ import annotations

import csv
import random
import webbrowser
import pygame
from recommender import WeightedGraph


def load_graph(songs_file: str) -> WeightedGraph:
    """Load song data and build similarity graph."""
    graph2 = WeightedGraph()
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
                graph2.add_vertex(track_name, metadata)
                songs.append(track_name)
            except (IndexError, ValueError):
                continue

    for m in range(len(songs)):
        song1 = songs[m]
        if song1 not in graph2.get_all_vertices():
            continue

        similarities = []
        for j in range(m + 1, len(songs)):
            song2 = songs[j]
            if song2 not in graph2.get_all_vertices():
                continue

            similarity = graph2.get_similarity_score(song1, song2)
            similarity_threshold = 0.3
            if similarity > similarity_threshold:
                similarities.append((song2, similarity))

        # Keep top 20 most similar songs
        similarities.sort(key=lambda x: -x[1])
        for song2, similarity in similarities[:20]:
            graph2.add_edge(song1, song2, similarity)

    return graph2


def get_spotify_search_url(track1: str, artist1: str) -> str:
    """Generate a Spotify search URL from a track and artist."""
    query = f"{track1} {artist1}"
    return f"https://open.spotify.com/search/{query.replace(' ', '%20')}"


def generate_random_song_list(graph1: WeightedGraph, sample_size: int = 7) -> list[tuple[str, str]]:
    """Generate a new random list of songs from the graph."""
    all_vertices = list(graph1.get_all_vertices())
    sample_size = min(sample_size, len(all_vertices))
    random_songs = random.sample(all_vertices, sample_size)

    song_list_ = []
    for s in random_songs:
        vertex = graph1.get_vertex(s)
        if vertex:
            meta = vertex.metadata
            song_list_.append((meta['track_name'], meta['artists']))

    return song_list_


def truncate_text(text: str, max_length: int) -> str:
    """Truncate the text to the specified maximum length and append '...' if it exceeds the limit."""
    if len(text) > max_length:
        return text[:max_length - 3] + "..."
    return text


if __name__ == '__main__':
    import doctest

    doctest.testmod()
    import python_ta

    # pygame setup
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    current = "home"
    window_y = screen.get_height()
    window_x = screen.get_width()
    running = True
    user_input_active = False
    user_input_text = ''

    # different fonts
    TITLE_FONT = pygame.font.Font("Fonts/Audiowide/Audiowide-Regular.ttf", int(window_y * 0.06))
    SUBTITLE_FONT = pygame.font.Font("Fonts/Audiowide/Audiowide-Regular.ttf", int(window_y * 0.04))
    PARAGRAPH_FONT = pygame.font.Font("Fonts/MPPLUS Rounded 1c/MPLUSRounded1c-Regular.ttf", int(window_y * 0.03))
    BIG_PARAGRAPH_FONT = pygame.font.Font("Fonts/MPPLUS Rounded 1c/MPLUSRounded1c-Regular.ttf", int(window_y * 0.04))

    # button variables
    start_button = None
    user_input = None
    input_enter = None
    test_button = None
    limit_enter = None
    return_button = None
    rec_limit = None

    # other variables
    recommendations = []
    dropdown_menu = []
    listen_menu = []
    limit_menu = []
    song_names = []
    rec_listen_buttons = []
    limit_selected = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    error_message = False

    # creating graph and randomized song options
    graph = load_graph('data/spotify_songs_smaller.csv')
    song_list = generate_random_song_list(graph)
    dropdown_selected = [0] * len(song_list)

    while running:
        # getting position of user's mouse
        mouse = pygame.mouse.get_pos()

        for event in pygame.event.get():
            # quitting the program
            if event.type == pygame.QUIT:
                running = False
            # clicking buttons
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # start button on homepage
                if start_button and start_button.collidepoint(event.pos) and current == "home":
                    current = "recommender"
                # button functions in recommender tab
                elif current == "recommender":
                    # song options
                    for option in range(len(dropdown_menu)):
                        if dropdown_menu[option].collidepoint(event.pos):
                            song_names.append(song_list[option][0])
                            dropdown_selected[option] += 1
                            error_message = False
                        # spotify listen buttons
                        elif listen_menu[option].collidepoint(event.pos):
                            track, artist = song_list[option]
                            url = get_spotify_search_url(track, artist)
                            webbrowser.open(url)

                    # enter button once songs have been selected
                    if input_enter and input_enter.collidepoint(event.pos):
                        if not song_names:
                            error_message = True
                        else:
                            current = "limit"

                # recommendations limit tab
                elif current == "limit":
                    for limit in range(len(limit_menu)):
                        # selection conditions on limit buttons
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

                # song recommendations tab
                elif current == "recommendations":
                    # resetting variables when program resets (try again button)
                    if return_button and return_button.collidepoint(event.pos):
                        song_names = []
                        rec_limit = None
                        song_list = generate_random_song_list(graph)
                        dropdown_selected = [0] * len(song_list)
                        limit_selected = [0] * 10
                        error_message = False
                        current = "recommender"
                        dropdown_menu = []
                        listen_menu = []
                    # spotify links to recommended songs
                    for button, rec in rec_listen_buttons:
                        if button.collidepoint(event.pos):
                            url = get_spotify_search_url(rec['track'], rec['artist'])
                            webbrowser.open(url)

        # fill the screen with a color to delete anything from last frame
        screen.fill("black")

        if current == "home":
            # title and start button
            title = TITLE_FONT.render("Spotify Recommender System", True, (255, 255, 255))
            screen.blit(title, (window_x // 2 - window_x * 0.28, window_y // 2 - window_y * 0.1))
            start_button_rect = pygame.Rect(window_x // 2 - window_x * 0.11, window_y // 2, 250, 50)

            # start button colour change
            if start_button_rect.collidepoint(mouse):
                button_color = (40, 220, 100)  # Hover color
            else:
                button_color = (29, 185, 84)  # Normal color

            # drawing button
            start_button = pygame.draw.rect(screen, button_color, start_button_rect, border_radius=12)
            start_button_text = SUBTITLE_FONT.render("START", True, (255, 255, 255))
            screen.blit(start_button_text, (window_x // 2 - window_x * 0.052, window_y // 2 + window_y * 0.008))

        elif current == "recommender":

            # error message if song isn't selected
            if error_message:
                question_text = PARAGRAPH_FONT.render("Please select at least one song.",
                                                      True,
                                                      (255, 255, 255))
                screen.blit(question_text, (40, 60))

            # displaying question
            question_text = SUBTITLE_FONT.render("From the following list below, select some songs that you like.",
                                                 True,
                                                 (255, 255, 255))
            screen.blit(question_text, (40, 30))

            # enter button
            input_enter_rect = pygame.Rect(window_x // 2 + 300, 640, 250, 50)
            input_enter_color = (40, 220, 100) if input_enter_rect.collidepoint(mouse) else (29, 185, 84)
            input_enter = pygame.draw.rect(screen, input_enter_color, input_enter_rect, border_radius=12)
            enter_text = SUBTITLE_FONT.render("NEXT", True, (255, 255, 255))
            screen.blit(enter_text, (window_x // 2 + 380, 647))

            # song options to choose from
            for i in range(7):
                # song options
                dropdown_option = pygame.draw.rect(screen, (255, 255, 255), (40, 100 + (75 * i), 820, 60), 1)
                dropdown_text = PARAGRAPH_FONT.render(truncate_text(f"{song_list[i][0]} by {song_list[i][1]}", 70),
                                                      True, (255, 255, 255))
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
                listen_button_rect = pygame.Rect(880, 102 + (75 * i), 360, 50)
                listen_button_color = (40, 220, 100) if listen_button_rect.collidepoint(mouse) else (29, 185, 84)
                listen_button = pygame.draw.rect(screen, listen_button_color, listen_button_rect, border_radius=10)
                listen_button_text = BIG_PARAGRAPH_FONT.render("Listen", True, (255, 255, 255))
                screen.blit(listen_button_text, (1015, 109 + (75 * i)))

                if listen_button not in listen_menu:
                    listen_menu.append(listen_button)

        elif current == "limit":
            # error message if limit number is not selected
            if error_message:
                question_text = PARAGRAPH_FONT.render("Please choose a number.",
                                                      True,
                                                      (255, 255, 255))
                screen.blit(question_text, (510, 260))

            question_text = SUBTITLE_FONT.render("Choose the number of recommendations you want from 1-10", True,
                                                 (255, 255, 255))
            screen.blit(question_text, (160, 230))

            for i in range(10):
                # changing limit colour buttons if it is selected or not
                if limit_selected[i] % 2 != 0:
                    limit_colour = (29, 185, 84)
                    limit_width = 0
                else:
                    limit_colour = (255, 255, 255)
                    limit_width = 1

                # drawing limit buttons
                num_recs = pygame.draw.rect(screen, limit_colour, (70 + (114 * i), window_y // 2 - 50, 100, 100),
                                            limit_width)
                num_recs_text = SUBTITLE_FONT.render(f"{i + 1}", True, (255, 255, 255))
                # change in position of '10' since it is a wider character
                if i < 10:
                    screen.blit(num_recs_text, (108 + (114 * i), window_y // 2 - 20))
                else:
                    screen.blit(num_recs_text, (100 + (114 * i), window_y // 2 - 20))

                if num_recs not in limit_menu:
                    limit_menu.append(num_recs)

            # drawing enter button
            limit_enter_rect = pygame.Rect(window_x // 2 - 125, 460, 250, 50)
            limit_enter_color = (40, 220, 100) if limit_enter_rect.collidepoint(mouse) else (29, 185, 84)
            limit_enter = pygame.draw.rect(screen, limit_enter_color, limit_enter_rect, border_radius=12)
            limit_enter_text = SUBTITLE_FONT.render("ENTER", True, (255, 255, 255))
            screen.blit(limit_enter_text, (window_x // 2 - 55, 467))

        elif current == "recommendations":
            question_text = TITLE_FONT.render("Song Recommendations:", True,
                                              (255, 255, 255))
            screen.blit(question_text, (80, 100))

            rec_listen_buttons = []

            for i, rec in enumerate(recommendations, 1):
                question_text = BIG_PARAGRAPH_FONT.render(truncate_text(f"{i}. {rec['track']} by {rec['artist']}", 70),
                                                          True,
                                                          (255, 255, 255))
                screen.blit(question_text, (80, 140 + (50 * i)))

                # spotify link buttons
                listen_button_rect = pygame.Rect(1050, 135 + (50 * i), 150, 35)
                listen_button_color = (40, 220, 100) if listen_button_rect.collidepoint(mouse) else (29, 185, 84)
                listen_button = pygame.draw.rect(screen, listen_button_color, listen_button_rect, border_radius=10)

                button_text = PARAGRAPH_FONT.render("Listen", True, (255, 255, 255))
                screen.blit(button_text, (1090, 140 + (50 * i)))
                rec_listen_buttons.append((listen_button, rec))

            # try again button
            return_button_rect = pygame.Rect(window_x // 2 + 325, 100, 250, 50)
            return_button_color = (40, 220, 100) if return_button_rect.collidepoint(mouse) else (29, 185, 84)
            return_button = pygame.draw.rect(screen, return_button_color, return_button_rect, border_radius=12)
            return_button_text = SUBTITLE_FONT.render("TRY AGAIN", True, (255, 255, 255))
            screen.blit(return_button_text, (window_x // 2 + 365, 107))

        # flip() the display to put your work on screen
        pygame.display.flip()

    python_ta.check_all(config={
        'extra-imports': [
            'csv', 'random', 'webbrowser', 'pygame', 'recommender'
        ],  # the names (strs) of imported modules
        "forbidden-io-functions": ["print"],
        'max-line-length': 120,
    })

    pygame.quit()
