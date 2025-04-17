# Kufar Scraper

This project is a scraper for Kufar, designed to notify users about new listings via Telegram and email.

## Prerequisites

- Docker

## Setup and Running

1. **Install Docker**
   
   If you haven't installed Docker yet, follow these steps:

   - For Ubuntu:
     ```
     sudo apt-get update
     sudo apt-get install docker-ce docker-ce-cli containerd.io
     ```

   - For macOS:
     Download and install Docker Desktop from [Docker's official website](https://www.docker.com/products/docker-desktop)

   - For Windows:
     Download and install Docker Desktop from [Docker's official website](https://www.docker.com/products/docker-desktop)

2. **Create .env file**

   Create a file named `.env` in the project root directory with the following content:

Replace the placeholder values with your actual credentials.

3. **Build the Docker image**

Navigate to the project directory in your terminal and run:

```bash
docker build -t kufar:latest .
```

4. **Run the Docker container**

After the image is built, run the container with:

```bash
docker run -it --env-file .env kufar:latest
```

5. **Run the Docker container with auto-restart**

To run the container with auto-restart (it will restart unless explicitly stopped), use:
This will run the container in detached mode (-d) and restart it automatically unless you explicitly stop it.

```bash
docker run -d --restart unless-stopped --env-file .env kufar:latest
```

## Notes

- Ensure that your Gmail account has "Less secure app access" enabled or use an App Password if you have 2-factor authentication enabled.
- Keep your `.env` file secure and do not share it publicly.
- The scraper will run continuously. To stop it, use `docker stop <container_id>`.

## Troubleshooting

If you encounter any issues, please check the following:

- Ensure all environment variables in the `.env` file are correctly set.
- Check that your Docker installation is up to date.
- Verify that your internet connection is stable.

For any other problems, please open an issue in the project repository.