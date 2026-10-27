# BookNest – Execution Guide, Video Script and Viva

Replace `YOUR_DOCKERHUB_USERNAME` and `YOUR_GITHUB_USERNAME` everywhere (Jenkinsfile, k8s/deployment.yaml, commands below).
Note: data lives in a Python list in memory, so **added books reset when the app restarts**.

---
## 1. Run Flask locally (Command Prompt, inside the project folder)

| Command | What it does |
|---|---|
| `cd booknest-reading-tracker` | Moves into the project folder. |
| `python -m venv venv` | Creates an isolated Python environment. |
| `venv\Scripts\activate` | Activates that environment (PowerShell: `venv\Scripts\Activate.ps1`). |
| `pip install -r requirements.txt` | Installs Flask. |
| `python app.py` | Starts the website on port 5000. |

## 2. Test the four pages
Open in the browser: `http://localhost:5000/` (Home), `/library` (try the search box, status/genre filters), `/add` (submit the form; try invalid values too), `/journal` (Journal), `/goals` (Reading Goals, with an editable yearly goal). Mood tiles on the home page link to filtered library views. Press `Ctrl + C` to stop Flask.

## 3. Docker (Docker Desktop must be running)

| Command | What it does |
|---|---|
| `docker build -t YOUR_DOCKERHUB_USERNAME/booknest-reading-tracker:latest .` | Builds the image from the Dockerfile. |
| `docker run -d --name booknest -p 5000:5000 YOUR_DOCKERHUB_USERNAME/booknest-reading-tracker:latest` | Runs the container in the background and maps port 5000 to your PC. |
| Open `http://localhost:5000` | Shows the website served from the container. |
| `docker ps` | Lists running containers. |
| `docker stop booknest` | Stops the container. |
| `docker rm booknest` | Removes the stopped container (needed before reusing the name). |

## 4. Push code to GitHub
First create an empty repo named `booknest-reading-tracker` on github.com (no README).

| Command | What it does |
|---|---|
| `git init` | Starts a Git repository. |
| `git add .` | Stages all files. |
| `git commit -m "BookNest first version"` | Saves a snapshot. |
| `git branch -M main` | Names the branch `main`. |
| `git remote add origin https://github.com/YOUR_GITHUB_USERNAME/booknest-reading-tracker.git` | Links your folder to the GitHub repo. |
| `git push -u origin main` | Uploads the code (sign in when asked; use a Personal Access Token as password if prompted). |

## 5. Push image to Docker Hub

| Command | What it does |
|---|---|
| `docker login` | Logs in to Docker Hub (use your username and password/access token). |
| `docker push YOUR_DOCKERHUB_USERNAME/booknest-reading-tracker:latest` | Uploads the image to Docker Hub. |

## 6. Deploy on Kubernetes (Docker Desktop)
One-time: Docker Desktop → Settings → Kubernetes → tick **Enable Kubernetes** → Apply & Restart. Make sure `deployment.yaml` has your Docker Hub username and the image is pushed (step 5).

| Command | What it does |
|---|---|
| `kubectl config use-context docker-desktop` | Points kubectl at Docker Desktop's cluster. |
| `kubectl get nodes` | Checks the cluster is Ready. |
| `kubectl apply -f k8s/deployment.yaml` | Creates the Deployment (one pod). |
| `kubectl apply -f k8s/service.yaml` | Creates the NodePort Service. |
| `kubectl get pods` | Shows the pod; wait for `Running`. |
| Open `http://localhost:30080` | Opens the app through the NodePort. |

## 7. Jenkins on Windows

**Prerequisites:** Java 17 or 21, Git, Docker Desktop (running), Kubernetes enabled, `kubectl` working in Command Prompt.

**Important Windows tip:** run Jenkins as *your own user* so it can use Docker Desktop and your kubeconfig (`C:\Users\<you>\.kube\config`). The Windows service runs as SYSTEM and usually cannot see them.

1. Download `jenkins.war` from jenkins.io (Generic Java package).
2. `java -jar jenkins.war --httpPort=8080` – starts Jenkins (keep this window open).
3. Open `http://localhost:8080`, paste the initial admin password shown in the console, choose **Install suggested plugins**, create an admin user.
4. **Manage Jenkins → Plugins → Available:** make sure *Git*, *Pipeline* and *GitHub* plugins are installed.
5. **Add credentials:** Manage Jenkins → Credentials → System → Global → Add Credentials.
   - Kind: *Username with password*
   - Username: your Docker Hub username
   - Password: your Docker Hub password (an access token is safer)
   - ID: `dockerhub-credentials` (must match the Jenkinsfile)
6. **Create the job:** New Item → name `booknest-pipeline` → *Pipeline* → OK.
   - Build Triggers: tick **GitHub hook trigger for GITScm polling**.
   - Pipeline → Definition: **Pipeline script from SCM** → SCM: Git → Repository URL: `https://github.com/YOUR_GITHUB_USERNAME/booknest-reading-tracker.git` → Branch: `*/main` → Script Path: `Jenkinsfile` → Save.
7. Click **Build Now** and watch the five stages turn green.
8. Check: `kubectl get pods` and open `http://localhost:30080`.

(If your repo is private, add a GitHub credential in Jenkins and select it in the job.)

### GitHub webhook (automatic builds)
A webhook is GitHub calling a URL when you push. GitHub's servers are on the internet, so they **cannot reach `http://localhost:8080`** – localhost only exists on your laptop. You need a public URL that tunnels to your Jenkins:

1. Install ngrok, then run `ngrok http 8080`. It prints a URL like `https://abcd-1234.ngrok-free.app`.
2. GitHub repo → **Settings → Webhooks → Add webhook**.
   - Payload URL: `https://abcd-1234.ngrok-free.app/github-webhook/` (keep the trailing slash)
   - Content type: `application/json`
   - Event: *Just the push event* → Add webhook.
3. A green tick appears after a successful delivery. The free ngrok URL changes each time you restart it, so update the webhook then.

(No webhook? Fallback: in the job set Build Triggers → *Poll SCM* with schedule `* * * * *`.)

## 8. Test automatic deployment
1. Edit `templates/index.html`, change the label `Your personal reading club` to `Your personal reading club – v2`.
2. `git add .` – stages the change.
3. `git commit -m "Change heading"` – saves it.
4. `git push` – GitHub fires the webhook, Jenkins builds, pushes, and deploys.
5. Watch Jenkins, then run `kubectl get pods` (you will see a new pod replace the old one) and refresh `http://localhost:30080`.

**Troubleshooting:** `docker` or `kubectl` not found in Jenkins → restart Jenkins from a fresh Command Prompt after installing them. `ImagePullBackOff` → image name wrong or not pushed (or repo is private). Port 5000 busy → `docker stop booknest`.

---
## 9. 60-second video script

**(0–10s, browser)** "This is booknest., a Flask reading tracker with a luxury editorial design: home, My Library with search and filters, Add a Book, Reading Journal, and My Goals."

**(10–22s, VS Code)** "app.py has four routes and a Python list as data. Templates and style.css make the pages. requirements.txt lists Flask, and the Dockerfile packages everything on Python 3.12 slim."

**(22–32s)** "deployment.yaml runs one pod of our image, and service.yaml exposes it on NodePort 30080."

**(32–42s, Jenkinsfile)** "The Jenkinsfile pulls code from GitHub, builds the Docker image, logs in to Docker Hub with Jenkins credentials, pushes the image, and deploys with kubectl. A GitHub webhook triggers it on every push."

**(42–50s, browser)** "Here is the app running on localhost:30080 from Kubernetes."

**(50–60s, terminal)** "These commands prove orchestration: one deployment, one running pod, and a NodePort service. Thank you!"

**Commands to show:**
```
kubectl get pods
kubectl get deployments
kubectl get services
```
(Or all at once: `kubectl get all`)

---
## 10. Viva questions

- **Flask?** A small Python web framework used to build websites with routes and templates.
- **Docker?** A tool that packs an app and everything it needs into a container so it runs the same anywhere.
- **Kubernetes?** A system that runs, scales, and heals containers across machines.
- **Orchestration?** Automatically managing many containers: starting, restarting, scaling, and connecting them.
- **Jenkins?** An open-source automation server that builds, tests, and deploys code.
- **CI/CD?** Continuous Integration/Continuous Delivery: every code change is automatically built, tested, and delivered.
- **GitHub?** An online platform that stores Git repositories and supports teamwork on code.
- **Docker Hub?** An online registry where Docker images are stored and shared.
- **Dockerfile?** A text file with step-by-step instructions to build a Docker image.
- **Jenkinsfile?** A text file that defines the Jenkins pipeline stages as code.
- **Kubernetes Deployment?** An object that keeps the desired number of identical pods running and handles updates.
- **Service?** A stable network address that exposes pods and balances traffic to them (NodePort opens a port on the node).
- **Webhook?** An automatic HTTP call one system sends to another when an event happens, e.g. GitHub notifying Jenkins of a push.
