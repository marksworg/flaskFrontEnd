from flask import Flask, render_template, request
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime

# --- LOAD ENV ---
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    systems = ["Any", "5E", "PF2E", "PATHFINDER", "CALL OF CTHULHU", "VTM"]
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

    selected_system = request.args.get('system', 'Any')
    selected_days = request.args.getlist('day')

    query = supabase.table("posts").select("*")
    if selected_system != "Any":
        query = query.eq("system", selected_system)
    for day in selected_days:
        query = query.eq(day, 1)

    results = query.execute().data

    for post in results:
        post['days'] = [d.capitalize() for d in days if post.get(d) == 1]
        post['created'] = datetime.utcfromtimestamp(post['created_utc']).strftime('%Y-%m-%d %H:%M UTC')

    return render_template("index.html", systems=systems, days=days,
                           selected_system=selected_system,
                           selected_days=selected_days,
                           results=results)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
