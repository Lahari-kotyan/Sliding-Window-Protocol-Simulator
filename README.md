# Computer Networks Sliding Window Protocol Simulator

An interactive, graphical **Sliding Window Protocol Simulator** developed as a Computer Networks student academic project. The application demonstrates, animates, and compares three fundamental transport/data-link layer flow control protocols:

1. **One-Bit Sliding Window (Alternating Bit Protocol)**
2. **Go-Back-N (GBN)**
3. **Selective Repeat (SR)**

Available as both a **Python Tkinter Desktop Application** and a **Web Application (Vercel Ready)**.

---

## 🌐 Deploy to Vercel (Web Version)

The project includes a web version (`index.html`, `css/`, `js/`, `vercel.json`) equipped with HTML5 Canvas animation and Chart.js graphs ready for 1-click deployment on Vercel.

### Method 1: Deploy using Vercel CLI
Run the following command in your terminal inside the project directory:
```bash
npx vercel
```
Follow the interactive prompts:
* **Set up and deploy?** `Y`
* **Which scope?** (Select your account)
* **Link to existing project?** `N`
* **What's your project's name?** `sliding-window-simulator`
* **In which directory is your code located?** `./`

Vercel will output your live URL (e.g. `https://sliding-window-simulator.vercel.app`).

### Method 2: Deploy via GitHub / Vercel Dashboard
1. Push this project folder to a repository on GitHub / GitLab.
2. Go to [vercel.com/new](https://vercel.com/new) and import the repository.
3. Click **Deploy**. Vercel will automatically detect `vercel.json` and publish your site!

---

## 💻 Run Desktop Version (Python Tkinter)

Run:
```bash
python main.py
```

To run unit tests:
```bash
python -m unittest tests/test_protocols.py
```
