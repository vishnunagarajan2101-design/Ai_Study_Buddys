import os
import uuid
from flask import Flask, render_template, request, jsonify, session
import database


app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')
app.secret_key = "super_secret_key_for_this_app_2026"  # Needed for session usage

# Initialize Database on Startup
if not os.path.exists(database.DB_NAME):
    database.init_db()
else:
    # ensuring tables exist even if file exists
    database.init_db()


@app.route('/')
def index():
    """
    Simulated 'Login':
    If user has no ID in session, generate one and save it.
    This ID acts like their phone number.
    """
    if 'user_id' not in session:
        user_id = str(uuid.uuid4())[:8]  # Short 8-char ID for simplicity
        session['user_id'] = user_id
        
        # Save to DB
        conn = database.get_db_connection()
        conn.execute('INSERT INTO users (id) VALUES (?)', (user_id,))
        conn.commit()
        conn.close()
    
    return render_template('index.html', user_id=session['user_id'])

# --- Placeholder API Routes (to be implemented fully) ---

@app.route('/api/chat/send', methods=['POST'])
def send_message():
    data = request.json
    sender_id = session.get('user_id')
    
    if not sender_id:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    receiver_id = data.get('receiver_id')
    group_id = data.get('group_id')
    content = data.get('content')
    msg_type = data.get('type', 'private') # 'private' or 'group'

    if not content:
        return jsonify({"status": "error", "message": "No content"}), 400

    conn = database.get_db_connection()
    c = conn.cursor()
    c.execute(
        'INSERT INTO messages (sender_id, receiver_id, group_id, content, type) VALUES (?, ?, ?, ?, ?)',
        (sender_id, receiver_id, group_id, content, msg_type)
    )
    conn.commit()
    conn.close()
    
    return jsonify({"status": "success", "sender_id": sender_id})

@app.route('/api/chat/get', methods=['GET'])
def get_messages():
    """
    Fetch messages where I am the sender OR receiver.
    For groups, fetch if I am a member (simplified here: fetch all group msgs for demo).
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"messages": []})
    
    target_id = request.args.get('target_id') # Other user or group ID
    mode = request.args.get('mode') # 'private' or 'group'
    
    conn = database.get_db_connection()
    c = conn.cursor()
    
    if mode == 'private':
        # Get messages between me and target
        c.execute('''
            SELECT * FROM messages 
            WHERE (sender_id = ? AND receiver_id = ?) 
            OR (sender_id = ? AND receiver_id = ?)
            ORDER BY timestamp ASC
        ''', (user_id, target_id, target_id, user_id))
    elif mode == 'group':
        # Get messages for this group
        c.execute('''
            SELECT * FROM messages 
            WHERE group_id = ? AND type = 'group'
            ORDER BY timestamp ASC
        ''', (target_id,))
    else:
        # Fetch nothing
        return jsonify({"messages": []})
        
    messages = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return jsonify({"messages": messages, "current_user_id": user_id})

# Import the ML and Study Buddy engines
from ml_engine import analyzer
from study_buddy import study_buddy

@app.route('/api/analyze', methods=['POST'])
def analyze_chat():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json or {}
    filter_mode = data.get('filter_mode', 'all') # 'all', 'today', 'week', 'custom'
    
    query = 'SELECT content FROM messages WHERE sender_id = ?'
    params = [user_id]
    
    if filter_mode == 'today':
        query += " AND date(timestamp) = date('now', 'localtime')"
    elif filter_mode == 'week':
        query += " AND date(timestamp) >= date('now', 'localtime', '-7 days')"
    elif filter_mode == 'custom':
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        if start_date:
            query += " AND date(timestamp) >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date(timestamp) <= ?"
            params.append(end_date)
            
    conn = database.get_db_connection()
    c = conn.cursor()
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    
    texts = [row['content'] for row in rows]
    
    result = analyzer.analyze_messages(texts)
    result['filter_applied'] = filter_mode
    
    return jsonify(result)

@app.route('/api/explain', methods=['POST'])
def explain_topic():
    data = request.json
    topic = data.get('topic')
    level = data.get('level')
    
    if not topic or not level:
        return jsonify({"error": "Missing topic or level"}), 400
        
    response = study_buddy.get_explanation(topic, level)
    return jsonify({"explanation": response})

if __name__ == '__main__':
    app.run(debug=True, port=5000)


