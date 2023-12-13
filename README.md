# 🚀 wav.finder

Connecting user with songs all over the cosmos using comprehensive filters and song metrics. 

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Overview

  Ditch the playlist fatigue and dive into a tailored music experience. Our project taps into the science behind music preferences, analyzing energy, danceability, emotion, and genre to give a varied listening eperience. Using advanced metrics like cosine similarity and a genre distance matrix, we refine your choices for a seamless, mood-enhancing experience. Imagine different galaxies of songs you can trevel to, instead of just the same ones you've already heard over and over. It's not hype; it's just a smart way to rediscover the joy in your music. Elevate your listening game with a blend of data and tunes that speaks to your adventurous nature.

## Getting Started

### Prerequisites

There are 2 required datasets:
* .csv (Data files)
  * https://www.kaggle.com/datasets/georgeggcoco/closeness-of-music-genres (preprocessed_matrix.cxv)
  * https://www.kaggle.com/datasets/nikitricky/every-noise-at-once (processed_songs.csv)
  
Both these datasets will need to be downloaded with the second link being able to substituted with 

### Setup

You will also need to have Streamlit and other dependencies installed.
For a simple setup:

* Make a local directory, and ```git clone``` the repository
* Set up a virtual environment
  * ```python3 -m venv venv ```
* Activate the environment
  * ```. venv/bin/activate ```
* Install dependencies
  * ```pip install -r requirements.txt```
* Run the app
  * ``` streamlit run Spotifytest.py ```
* Try it out! 

