# Memory Game 🧠

A fun and interactive memory card matching game built with Python Flask and deployable to Kubernetes.

## Features

- ✨ 16 cards with 8 pairs to match
- 🎨 Multiple themes: Emoji, Star Wars (SWAPI), Pokemon (PokeAPI)
- 🔄 Cards are shuffled each game
- 🎯 Flip cards to find matching pairs
- 📊 Move counter and match tracker
- 🏆 Win state with congratulations modal
- 📱 Responsive design for mobile and desktop
- 🔄 New game button to restart anytime

## Local Development

### Prerequisites
- Python 3.11+
- pip

### Run Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:8080
```

## Docker Deployment

### Build the Docker image:
```bash
docker build -t memory-game:latest .
```

### Run with Docker:
```bash
docker run -p 8080:8080 memory-game:latest
```

## Kubernetes Deployment

### Prerequisites
- Kubernetes cluster (local or cloud)
- kubectl configured

### Deploy to Kubernetes:

1. Build and load the Docker image to your cluster:
```bash
# For local clusters like minikube or kind:
docker build -t memory-game:latest .

# For minikube:
minikube image load memory-game:latest

# For kind:
kind load docker-image memory-game:latest
```

2. Apply the Kubernetes manifests:
```bash
kubectl apply -f k8s-deployment.yaml
```

3. Check the deployment status:
```bash
kubectl get pods
kubectl get services
```

4. Access the application:
```bash
# For LoadBalancer (cloud providers):
kubectl get service memory-game-service
# Use the EXTERNAL-IP

# For minikube:
minikube service memory-game-service

# For kind or port-forward:
kubectl port-forward service/memory-game-service 8080:80
```

### Clean up:
```bash
kubectl delete -f k8s-deployment.yaml
```

## Architecture

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python Flask
- **Server**: Gunicorn WSGI
- **Container**: Docker
- **Orchestration**: Kubernetes

## Game Rules

1. **Choose a theme**: Emoji, Star Wars, or Pokemon
2. **Click cards** to flip them over and reveal their content
3. **Find matching pairs** - if two flipped cards match, they stay revealed
4. **Non-matching cards** flip back after a brief moment
5. **Match all 8 pairs** to win the game
6. **Try to win** in the fewest moves possible!

## Themes

- **🎨 Emoji**: Classic emoji symbols
- **⭐ Star Wars**: Character names from SWAPI (Star Wars API)
- **⚡ Pokemon**: Pokemon names from PokeAPI

## Files Structure

```
memory-game/
├── app.py                  # Flask application
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── k8s-deployment.yaml    # Kubernetes manifests
├── templates/
│   └── index.html         # HTML template
└── static/
    ├── style.css          # Styles
    └── game.js            # Game logic
```

## Customization

You can customize the game by:
- Modifying the emoji list in `app.py`
- Adding new themes by fetching from other public APIs
- Adjusting the grid size (requires updating both frontend and backend)
- Changing colors and styles in `static/style.css`

## License

MIT
