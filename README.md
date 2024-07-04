# Mood of Music

[Mood of Music](https://moodofmusic.onrender.com) creates Spotify playlists from your environment images and embeds them on the site for instant listening.

## Description

Mood of Music transforms your environment into a personalized auditory experience! Simply upload an image of your surroundings—be it a serene landscape or a bustling cityscape—and watch as the app curates a Spotify playlist that perfectly matches the mood. The best part? The playlist is instantly added to your Spotify account and seamlessly embedded on the website for you to enjoy without missing a beat.

## Features

- **Image Upload**: Upload an image of your environment, such as a landscape.
- **Playlist Generation**: Generates a playlist of songs that match the setting/theme.
- **Spotify Integration**: Adds the playlist directly to your Spotify account.
- **Embedded Playlist**: The generated playlist is embedded on the website for immediate listening.
- **PostgreSQL Database**: Stores the account names of users and the details of each playlist created.

## Technologies Used

- **Python**: Backend logic
- **Flask**: Web framework
- **HTML/CSS/JavaScript**: Frontend development
- **Spotify API**: Authentication and playlist management
- **Spotipy**: Python library for Spotify
- **PyTorch**: Neural network framework for image processing
- **OpenAI API**: Image description and playlist generation
- **PostgreSQL**: Database management
- **MySQL**: Alternative database management (via Docker)
- **Docker**: Containerization
- **Render.com**: Hosting and deployment

## Song Recommendations
Song recommendations are based on detected emotions from the environment images. The application uses a neural network model implemented with PyTorch to analyze images and extract emotional parameters such as valence, energy, danceability, tempo, loudness, and acousticness. These parameters are then used in conjunction with Spotify's recommendation API to generate playlists tailored to the detected mood.

## Getting Started

Follow these steps to get the app up and running on your local machine.

### Prerequisites

- Python 3.8 or higher
- Spotify Developer Account
- OpenAI API Key
- PostgreSQL Database

### Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/moodofmusic.git
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

    POSTGRES_HOST=your_database_host
    POSTGRES_USER=your_database_user
    POSTGRES_PASSWORD=your_database_password
    POSTGRES_DB=your_database_name
    ```

3. **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up the PostgreSQL database**:
    Make sure your PostgreSQL database is running and the credentials match those in your `.env` file. Initialize the database using the provided SQL script or commands in your application.

5. **Run the application**:
    ```sh
    python main.py
    ```

### Usage

1. Open your browser and go to `http://localhost:5001`.
2. Log in with your Spotify account.
3. Upload an image, enter a playlist name and theme, and submit the form.
4. The app will generate a playlist and add it to your Spotify account.
5. Listen to the generated playlist embedded on the website.

## Deployment

The website and the PostgreSQL database are hosted on Render.com. To deploy the application on Render.com or any other hosting platform, ensure that you configure the environment variables and database settings as per the hosting platform's requirements.

## Docker
For those who prefer using Docker, a dockerized file is provided to run the web app using MySQL instead of PostgreSQL. The Docker setup encapsulates all the dependencies and database configurations, simplifying the deployment process. To use the Dockerized version, ensure Docker is installed on your machine, and follow the instructions in the dockerized file.

## Contact

For any questions or suggestions, please contact [alzureiqi2@gmail.com](mailto:alzureiqi2@gmail.com).
