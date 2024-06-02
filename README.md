# Mood of Music

Mood of Music creates Spotify playlists from your environment images and embeds them on the site for instant listening.

## Description

Mood of Music transforms your environment into a personalized auditory experience! Simply upload an image of your surroundings—be it a serene landscape or a bustling cityscape—and watch as the app curates a Spotify playlist that perfectly matches the mood. The best part? The playlist is instantly added to your Spotify account and seamlessly embedded on the website for you to enjoy without missing a beat.

## Features

- **Image Upload**: Upload an image of your environment, such as a landscape.
- **Playlist Generation**: Generates a playlist of songs that match the setting/theme.
- **Spotify Integration**: Adds the playlist directly to your Spotify account.
- **Embedded Playlist**: The generated playlist is embedded on the website for immediate listening.

## Technologies Used

- **Python**: Backend logic
- **Flask**: Web framework
- **HTML/CSS/JavaScript**: Frontend development
- **Spotify API**: Authentication and playlist management
- **Spotipy**: Python library for Spotify
- **Docker**: Containerization and deployment
- **OpenAI API**: Image description and playlist generation

## Getting Started

Follow these steps to get the app up and running on your local machine.

### Prerequisites

- Python 3.8 or higher
- Docker
- Spotify Developer Account
- OpenAI API Key

### Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/mood-of-music.git
    cd mood-of-music
    ```

2. **Set up environment variables**:
    Create a `.env` file in the root directory and add your credentials:
    ```env
    APP_SECRET_KEY=your_flask_app_secret_key

    OPENAI_API_KEY=your_openai_api_key

    CLIENT_ID=your_spotify_client_id
    CLIENT_SECRET=your_spotify_client_secret
    REDIRECT_URI=http://localhost:5001/callback

    AUTH_URL=https://accounts.spotify.com/authorize
    TOKEN_URL=https://accounts.spotify.com/api/token
    API_BASE_URL=https://api.spotify.com/v1

    DB_HOST=database_host
    DB_USER=database_root
    DB_PASSWORD=database_password
    DB_DATABASE=database_name
    DATABASE_URL=your_database_url
    ```

3. **Build and run the Docker container**:
    ```sh
    docker-compose up --build
    ```

### Usage

1. Open your browser and go to `http://localhost:5001`.
2. Log in with your Spotify account.
3. Upload an image, enter a playlist name and theme, and submit the form.
4. The app will generate a playlist and add it to your Spotify account.
5. Listen to the generated playlist embedded on the website.

## Contact

For any questions or suggestions, please contact [alzureiqi2@gmail.com](mailto:alzureiqi2@gmail.com).
