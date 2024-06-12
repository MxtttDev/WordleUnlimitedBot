# Wordle Unlimited Bot

## Overview

This project is an automated bot designed to play the online game [Wordle Unlimited](https://wordleunlimited.org). Using the Selenium WebDriver, the bot interacts with the Wordle game, making educated guesses based on letter frequencies and feedback from previous guesses. The bot aims to guess the correct word within the allowed six attempts and tracks its success rate over multiple games.


## Prerequisites

- Python 3.6 or later
- Google Chrome browser
- ChromeDriver (compatible with your Chrome browser version)
- Selenium
- Adblocker Chrome extension CRX file (OPTIONAL)

There are some changes that must be made to succesfully run the script:
- Edit the path to your ChromeDriver on **Line 24**
- Uncomment and edit the path to your adblocker on **Line 18** (OPTIONAL)

## Showcase

https://github.com/MxtttDev/WordleUnlimitedBot/assets/102174560/86f3c5e6-9445-4b3c-aaed-307ad5ba63b7

Above is a video demonstrating the bot in action.

![statistics](https://github.com/MxtttDev/WordleUnlimitedBot/assets/102174560/ae7084cb-d3bc-4b30-8507-c2b46ad92646)

This is a screenshot of the statistics for 100 consecutive games. As shown the current success rate is approximately **95%**.
The bar graph represents how many games used each amount of gueses. As shown, the bot most commonly guesses the correct word on the fourth guess.
## Logic Overview

### Setup

- The script starts by setting up Selenium with Chrome options, including an ad blocker to prevent distractions.
- The `setupAndLoad` function navigates to the Wordle Unlimited website and handles initial setup tasks such as accepting cookies.

### Main Loop

The main loop plays multiple games of Wordle, resetting and tracking progress after each game:

1. **Initialisation:**
    
    - Reset the lists tracking correct, present, and wrong letters.
    - Copy the original word list to use for the current game.
    
1. **Guessing Process:**
    
    - For each of the six allowed guesses:
        - Calculate scores for the remaining possible words based on letter frequency.
        - Choose the word with the highest score.
        - Submit the guess and collect feedback on each letter's correctness.
        - Update the lists of known letters based on the feedback.
        - Trim the word list to exclude words that don't fit the known constraints.
        
1. **Success Check:**
    
    - If the correct word is guessed, increment the success counter and print a success message.
    
1. **Statistics:**
    
    - Calculate and print the success percentage after each game.
    
1. **Reset:**
    
    - Click the "Play again!" button to start a new game.



## Potential Improvements

- Revisit `calculateWordScores()` and improve logic to raise success percentage. Need to explore the idea of initially using words of unique and unknown letters to get the best coverage within `known_letters` before moving on.

 - Introduce timing functions to track and report time taken for each game and a running average.

- Improve speed of each game by optimising `time.sleep()` statements or introducing wait conditions within selenium to wait for objects to load and press them as soon as they do.
