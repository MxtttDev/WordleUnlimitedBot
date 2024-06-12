from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from collections import Counter
import time
import logging

# Suppress SSL errors and other irrelevant logs
logging.getLogger('selenium.webdriver.remote.remote_connection').setLevel(logging.WARNING)

# Selenium setup for interaction with Chrome
chrome_options = Options()

# if you would like to hide ads, uncomment the line below and correct path
# chrome_options.add_extension('path/to/adblocker.crx')

# Suppress other SSL errors
chrome_options.add_argument('--log-level=3')

# Initialize the Chrome service and WebDriver
service = ChromeService(executable_path='path/to/chromedriver') # CHANGE THIS TO CHROMEDRIVER PATH
driver = webdriver.Chrome(service=service, options=chrome_options)

# Setup ActionChains to allow keyboard input without specified target elements
actions = ActionChains(driver)

def setupAndLoad(driver=driver):
    """
    Navigate to the Wordle Unlimited website and perform initial setup such as accepting cookies.
    """
    # Navigate to WORDLE and wait for it to load
    driver.get("https://www.wordleunlimited.org/")
    time.sleep(2)

    # Accept cookies by clicking the appropriate button
    driver.find_element(By.XPATH, "/html/body/div/div[2]/div[1]/div[2]/div[2]/button[1]/p").click()
    time.sleep(2)
    

def submitGuess(guess, actions=actions):
    """
    Submits a word guess by typing each letter and hitting enter.
    """
    # Iteratively type each letter in the guess for visual effect
    for i in guess:
        actions.send_keys(i)
        actions.perform()
        time.sleep(0.15)
    
    # Submit the full guess
    actions.send_keys(Keys.RETURN)
    actions.perform()
    time.sleep(2)

def collectRowFeedback(row_number, board_feedback, driver=driver):
    """
    Collect feedback from a specific row on the Wordle board to determine correct, present, and absent letters.
    """
    # Retrieving the game element and its shadow root
    game = driver.find_element(By.TAG_NAME, 'game-app')
    game_shadow_root = driver.execute_script('return arguments[0].shadowRoot', game)
    
    # Retrieving an array of row elements
    rows = game_shadow_root.find_elements(By.CSS_SELECTOR, 'game-row')
    
    # Getting array of tile elements from the specified row
    row_shadow_root = driver.execute_script('return arguments[0].shadowRoot', rows[row_number])
    tiles = row_shadow_root.find_elements(By.CSS_SELECTOR, 'game-tile')
    
    # Initializing an empty list for feedback from this row
    row_feedback = []
    
    # Iterating through the tiles on this row and collecting feedback for each tile based on the HTML attributes
    for tile in tiles:
        letter = tile.get_attribute('letter')
        evaluation = tile.get_attribute('evaluation')  # 'correct', 'present', or 'absent'
        row_feedback.append((letter, evaluation))
    
    # Appending row feedback to the board feedback
    board_feedback.append(row_feedback)
    
    return row_feedback

def updateKnown(row_feedback, present_letters, correct_letters, wrong_letters, wrong_positions):
    """
    Update the lists of known letters based on the feedback from a row.
    """
    for position, (letter, evaluation) in enumerate(row_feedback):
        if evaluation == "correct":
            # Update the correct letters list
            correct_letters[position] = letter
            # Ensure the letter is not in the present or wrong letters list
            if letter in present_letters:
                present_letters.remove(letter)
            if letter in wrong_letters:
                wrong_letters.remove(letter)
        elif evaluation == "present":
            # Add the letter to the present letters list if not already present and not correct
            if letter not in present_letters and letter not in correct_letters:
                present_letters.append(letter)
            # Track the positions where the letter should not appear
            wrong_positions[position].add(letter)
        else:  # evaluation == "absent"
            # Add the letter to the wrong letters list if it's not in any other list
            if letter not in wrong_letters and letter not in correct_letters and letter not in present_letters:
                wrong_letters.append(letter)
    return

def trimWordPool(wordlist, wrong_letters, present_letters, correct_letters):
    """
    Trim the word pool based on known wrong letters, present letters, and correct letters.
    """
    # Filter out words containing any wrong letters
    trimmed_wordlist = [word for word in wordlist if not any(letter in word for letter in wrong_letters)]
    
    # Ensure words contain all present letters
    if present_letters:
        trimmed_wordlist = [word for word in trimmed_wordlist if all(letter in word for letter in present_letters)]
    
    # Ensure words match the known correct letters at specific positions
    if correct_letters:
        trimmed_wordlist = [
            word for word in trimmed_wordlist
            if all(correct_letters[i] == '-' or correct_letters[i] == word[i] for i in range(len(correct_letters)))
        ]
    
    return trimmed_wordlist

def calculateWordScores(wordlist, present_letters, correct_letters, wrong_positions):
    """
    Calculate scores for each word based on letter frequency and known positions.
    """
    # Count the frequency of each letter in the word list
    letter_freq = Counter("".join(wordlist))
    word_scores = {}

    for word in wordlist:
        score = 0
        unique_letters = set(word)
        for letter in unique_letters:
            score += letter_freq[letter]

        # Add penalty for present letters in wrong positions
        for pos, letter in enumerate(word):
            if letter in present_letters and correct_letters[pos] == '-' and letter in wrong_positions[pos]:
                score -= 1

        word_scores[word] = score

    return word_scores

def getBestWord(word_scores):
    """
    Get the word with the highest score from the calculated word scores.
    """
    best_word = max(word_scores, key=word_scores.get)
    return best_word

def resetBoard(driver=driver):
    """
    Reset the Wordle board by clicking the "Play again!" button.
    """
    time.sleep(3)  # Wait before resetting to ensure any animations or transitions are complete
    
    # Retrieve the game element and its shadow root
    game = driver.find_element(By.TAG_NAME, 'game-app')
    game_shadow_root = driver.execute_script('return arguments[0].shadowRoot', game)
    
    # Retrieve the game-stats element inside the shadow DOM
    game_stats = game_shadow_root.find_element(By.CSS_SELECTOR, 'game-stats')
    stats_shadow_root = driver.execute_script('return arguments[0].shadowRoot', game_stats)
    
    # Click the "Play again!" button inside the shadow DOM
    refresh_button = stats_shadow_root.find_element(By.ID, 'refresh-button')
    refresh_button.click()
    return

if __name__ == "__main__":
    # Perform initial setup
    setupAndLoad()

    # Initialize game counters
    total_games = 0
    successful_games = 0

    # Read the original word list from the file
    with open('words.txt', 'r') as file:
        original_wordlist = [line.strip() for line in file.readlines()]

    # Loop to play multiple games
    while True:
        total_games += 1

        # Initialize feedback and known letters for the new game
        board_feedback = []
        present_letters = []
        correct_letters = ['-', '-', '-', '-', '-']
        wrong_letters = []
        wordlist = original_wordlist.copy()
        wrong_positions = [set() for _ in range(5)]

        success = False
        for i in range(6):
            if not wordlist:
                print("No more words to guess.")
                break

            # Calculate word scores and choose the best word to guess
            word_scores = calculateWordScores(wordlist, present_letters, correct_letters, wrong_positions)
            guess = getBestWord(word_scores)
            wordlist.remove(guess)
            print(f"Guessing: {guess}")
            submitGuess(guess)
            feedback = collectRowFeedback(i, board_feedback)
            updateKnown(feedback, present_letters, correct_letters, wrong_letters, wrong_positions)
            wordlist = trimWordPool(wordlist, wrong_letters, present_letters, correct_letters)

            # Check if the word was guessed correctly
            if '-' not in correct_letters:
                success = True
                print(f"Success! The word is: {guess}")
                break
        
        if success:
            successful_games += 1

        # Calculate and print success percentage
        success_percentage = (successful_games / total_games) * 100
        print(f"\nTotal Games: {total_games}")
        print(f"Success Percentage: {success_percentage:.2f}%")
        print('')

        # Reset the board for a new game
        resetBoard()

        # Add a delay before starting a new game
        time.sleep(1)
