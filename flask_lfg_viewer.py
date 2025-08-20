from flask import Flask, render_template, request
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
import humanize

# --- LOAD ENV ---
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    # Hard-coded list of supported systems
    systems = [
        "Any",
        "AVATAR LEGENDS",
        "5E",
        "BIOPUNK",
        "CALL OF CTHULHU",
        "CYBERPUNK",
        "DAGGERHEART",
        "DRAW STEEL",
        "FABULA ULTIMA",
        "LANCER",
        "MIST ENGINE",
        "PATHFINDER",
        "PF2E",
        "SAVAGE WORLDS",
        "SHADOWDARK",
        "STARFINDER",
        "VTM"
    ]

    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

    selected_system = request.args.get('system', 'Any')
    selected_days = request.args.getlist('day')

    # Most recent first, then limit to 1,000 rows
    query = (
        supabase
        .table("posts")
        .select("*")
        .order("created_utc", desc=True)
    )

    if selected_system != "Any":
        query = query.eq("system", selected_system)

    for day in selected_days:
        query = query.eq(day, 1)

    # Apply the limit last so it limits the filtered, ordered set
    query = query.limit(1000)  # or: .range(0, 999)

    results = query.execute().data

    for post in results:
        post['days'] = [d.capitalize() for d in days if post.get(d) == 1]
        dt = datetime.fromtimestamp(post['created_utc'], tz=timezone.utc)
        post['created'] = humanize.naturaltime(datetime.now(timezone.utc) - dt)

    return render_template(
        "index.html",
        systems=systems,
        days=days,
        selected_system=selected_system,
        selected_days=selected_days,
        results=results
    )

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
