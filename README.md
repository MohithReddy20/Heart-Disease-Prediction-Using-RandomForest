# heart-disease-prediction

## Current stack (this repo)

- **Backend:** Flask app in `p1_heartdiseaseprediction/app.py`, SQLite `mohithheart.db` next to `app.py`, pickled model `heartdiseaseprediction.model`.
- **Frontend:** React (Vite) in `frontend/`. Use **`http://localhost:5173`** in the browser so session cookies match the API host (see `frontend/src/config.js`).
- **Run locally (two terminals):**
  1. `cd p1_heartdiseaseprediction && source ../venv/bin/activate && python3 app.py` — API defaults to **`http://localhost:5001`** (override with `PORT=5000`).
  2. `cd frontend && npm install && npm run dev` — SPA on port **5173**.
- **Environment (optional):** `FLASK_SECRET_KEY` for Flask; `VITE_API_URL` in `frontend/.env` if the API is not at `http://localhost:5001`.
- **Routes:** App uses **lowercase** paths (`/login`, `/signup`, `/dashboard`, `/prediction`, `/history`). Old capitalized URLs redirect automatically.
- **History API (JSON):** `GET /api/history` (the browser path `/history` is the React page).

### Easiest hosting: Render.com (recommended)

One **Web Service** serves **Flask + the built React app** on the **same HTTPS URL**, so login cookies work with no extra CORS setup.

1. Push this repo to GitHub/GitLab.
2. In [Render](https://render.com): **New → Web Service**, connect the repo.
3. Render can read **`render.yaml`** (build + start commands are defined there). Or set manually:
   - **Build:** `chmod +x scripts/build.sh && ./scripts/build.sh && pip install -r requirements.txt`
   - **Start:** `cd p1_heartdiseaseprediction && gunicorn app:app --bind 0.0.0.0:$PORT --workers 1`
4. **Environment variables:** set `FLASK_SECRET_KEY` (Render can generate one). Optional: `MAIL_USERNAME`, `MAIL_PASSWORD` for Flask-Mail. On Render, `RENDER` is set automatically (enables secure session cookies).
5. **Node:** `render.yaml` sets `NODE_VERSION` so `npm ci` works during the build.

After deploy, open your `*.onrender.com` URL; the UI is served by Flask from `p1_heartdiseaseprediction/static/spa/` (created by `scripts/build.sh`).

### PythonAnywhere

Possible, but more manual: run `./scripts/build.sh` on your machine, upload `p1_heartdiseaseprediction/static/spa/` via the Files tab, point the WSGI file at `p1_heartdiseaseprediction.app`, and map static URLs for `/assets/` to `static/spa/assets/`. Render is usually simpler for this stack.

The sections below describe the original course / deployment write-up; some wording (e.g. “Bootstrap only”) reflects the older HTML UI, while the React client is the primary interface today.

---

Deployed Application:
link - https://10monica.pythonanywhere.com/

Introduction-
This is a fully validated multi-user application, where a user can check if he/she has heart disease or not by filling a short form which collects data from the heart disease prediction model and returns with a response based on the dataset used. 

Keywords- 
ML, Flask, RandomForestClassifier, HTML, CSS, Bootstrap

Dataset-
Heart Disease Prediction dataset from kaggle.com
Link - https://www.kaggle.com/rishidamarla/heart-disease-prediction

Machine Learning - 
Made use of Random Forest Classifier Algorithm, used random state = 3136

Model prediction Accuracy - 
87%

Flask-
Backend of the entire web application has been programmed in Flask, with a app.py controlling the major functionalities and the connections to all pages. 
Used Flask mail for sending randomly generated passwords to users when they try to sign in, and will then be redirected to the login page as soon as we send the email containing the password of the particular user. 
Re-using the same username won't be possible as it has been set as the primary key. 
A forgot password page has been made just in case the user forgets their password to the application.
All the forms are fully validated, including the quiz form inside which is the main functionality of the application. Responses to the form are used alongside the data present in the dataset to make the prediction.

HTML, CSS, BOOTSTRAP -
The entire frontend of the application have been made using html, css and bootstrap. And the application is fully responsive and is fully functional on all device widths.

Database-Sqlite3
name - monicaheart.db
table name - user

Screenshots-
Signup page-
![image](https://user-images.githubusercontent.com/82702672/145677319-294c2f3f-3384-42d0-848a-2ecdae03e70b.png)

Login page-
![image](https://user-images.githubusercontent.com/82702672/145677364-c4020995-e143-463b-9c46-652ab26eb8b2.png)

Forgot Password-
![image](https://user-images.githubusercontent.com/82702672/145677379-0a27c60a-0abc-4ca1-9254-c8910b96d66b.png)

Home Page-
![image](https://user-images.githubusercontent.com/82702672/145677406-a3940c4a-a6e2-451c-b790-a9df910e899f.png)
![image](https://user-images.githubusercontent.com/82702672/145677419-c6f720a2-bf2f-4f8c-9a46-0babb0cc28a1.png)
![image](https://user-images.githubusercontent.com/82702672/145677424-c5497e31-1f57-406c-b838-287f54a12112.png)
![image](https://user-images.githubusercontent.com/82702672/145677431-91c5cf18-25ce-49a6-be78-e47f2b23355f.png)

Quiz Page-
![image](https://user-images.githubusercontent.com/82702672/145677438-292c9ddd-a508-4fe7-9f3e-234b9beb7446.png)

Contributors-
Solo Project - Monica Gullapalli

Deployed Web Application link -
https://10monica.pythonanywhere.com/signup







