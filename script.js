// --- Global State & Initialization ---
const STORAGE_KEY_MESSAGES = 'ai_study_buddy_messages';
const STORAGE_KEY_USER = 'ai_study_buddy_user_id';

let currentTargetId = null;
let currentMode = 'private'; // 'private' only for this static demo
let myUserId = localStorage.getItem(STORAGE_KEY_USER);

// Initialize User ID
if (!myUserId) {
    myUserId = 'user_' + Math.floor(Math.random() * 1000000); // Simple ID generation
    localStorage.setItem(STORAGE_KEY_USER, myUserId);
}
document.getElementById('my-user-id').innerText = myUserId;


// --- Navigation ---
function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));

    document.getElementById(sectionId + '-section').classList.add('active');

    // Highlight button
    const buttons = document.querySelectorAll('.nav-btn');
    if (sectionId === 'chat') buttons[0].classList.add('active');
    if (sectionId === 'analysis') buttons[1].classList.add('active');
    if (sectionId === 'study') buttons[2].classList.add('active');
}

// --- Chat Logic (LocalStorage) ---

function getStoredMessages() {
    const raw = localStorage.getItem(STORAGE_KEY_MESSAGES);
    return raw ? JSON.parse(raw) : [];
}

function saveMessage(msg) {
    const messages = getStoredMessages();
    messages.push(msg);
    localStorage.setItem(STORAGE_KEY_MESSAGES, JSON.stringify(messages));
}

function setChatTarget() {
    const input = document.getElementById('target-id-input').value.trim();
    if (!input) return alert("Please enter a User ID");

    currentTargetId = input;
    document.getElementById('active-chat-status').innerText = `Chatting with: ${currentTargetId}`;
    loadMessages();
}

function handleEnter(e) {
    if (e.key === 'Enter') sendMessage();
}

function sendMessage() {
    if (!currentTargetId) return alert("Set a chat partner ID first!");
    const input = document.getElementById('message-input');
    const content = input.value.trim();
    if (!content) return;

    const msg = {
        id: Date.now(),
        sender_id: myUserId,
        receiver_id: currentTargetId,
        content: content,
        timestamp: new Date().toISOString(),
        type: 'private'
    };

    saveMessage(msg);
    input.value = '';
    loadMessages();
}

function loadMessages() {
    if (!currentTargetId) return;

    const allMessages = getStoredMessages();
    // Filter messages between me and target
    const chatMessages = allMessages.filter(m =>
        (m.sender_id === myUserId && m.receiver_id === currentTargetId) ||
        (m.sender_id === currentTargetId && m.receiver_id === myUserId)
    );

    renderMessages(chatMessages);
}

function renderMessages(messages) {
    const window = document.getElementById('chat-window');
    window.innerHTML = '';

    if (messages.length === 0) {
        window.innerHTML = '<div style="text-align: center; color: #888; margin-top: 20px;">No messages yet. Say hi!</div>';
        return;
    }

    messages.forEach(msg => {
        const div = document.createElement('div');
        const isMe = msg.sender_id === myUserId;
        div.className = `message ${isMe ? 'sent' : 'received'}`;
        div.innerHTML = `
            ${msg.content}
            <div class="meta">${new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
        `;
        window.appendChild(div);
    });

    window.scrollTop = window.scrollHeight;
}

// Poll for new messages (simulate real-time in local context too, useful if multiple tabs open)
setInterval(() => {
    if (document.getElementById('chat-section').classList.contains('active') && currentTargetId) {
        loadMessages();
    }
}, 3000);


// --- Analysis Logic (Client-Side ML) ---
let currentFilter = 'all';

function setFilter(mode) {
    currentFilter = mode;
    document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
    const buttons = document.querySelectorAll('.filter-btn');
    if (mode === 'all') buttons[0].classList.add('active');
    if (mode === 'today') buttons[1].classList.add('active');
    if (mode === 'week') buttons[2].classList.add('active');
}

// Simple Keyword-based Classifier
function predictMessageCategory(text) {
    const studyKeywords = ["study", "calculus", "math", "physics", "homework", "exam", "test", "read", "learn", "assignment", "project", "python", "code", "history", "chemistry", "biology", "algebra", "focus", "research"];
    const textLower = text.toLowerCase();

    // Check if any study keyword is in the text
    for (let word of studyKeywords) {
        if (textLower.includes(word)) return 'Study';
    }
    return 'Distraction'; // Default (naive)
}

function runAnalysis() {
    const allMessages = getStoredMessages();
    // Only analyze messages sent by ME
    let myMessages = allMessages.filter(m => m.sender_id === myUserId);

    // Apply Time Filters
    const now = new Date();
    if (currentFilter === 'today') {
        myMessages = myMessages.filter(m => new Date(m.timestamp).toDateString() === now.toDateString());
    } else if (currentFilter === 'week') {
        const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        myMessages = myMessages.filter(m => new Date(m.timestamp) >= oneWeekAgo);
    } else if (currentFilter === 'custom') {
        const start = document.getElementById('start-date').value;
        const end = document.getElementById('end-date').value;
        if (start) myMessages = myMessages.filter(m => new Date(m.timestamp) >= new Date(start));
        if (end) myMessages = myMessages.filter(m => new Date(m.timestamp) <= new Date(end)); // simplified
    }

    if (myMessages.length === 0) {
        updateStats(0, 0, 0, "No messages found for this period.");
        return;
    }

    let studyCount = 0;
    let distCount = 0;

    myMessages.forEach(msg => {
        if (predictMessageCategory(msg.content) === 'Study') {
            studyCount++;
        } else {
            distCount++;
        }
    });

    const total = studyCount + distCount;
    const score = total === 0 ? 0 : Math.round((studyCount / total) * 100);

    let insight = "";
    if (score > 75) insight = "Excellent focus! Keep it up.";
    else if (score > 50) insight = "Good study session, but try to minimize distractions.";
    else insight = "High distraction level detected. Suggest taking a break or using Focus Mode.";

    updateStats(score, studyCount, distCount, insight);
}

function updateStats(score, study, distract, insight) {
    document.getElementById('focus-score').innerText = score + '%';
    document.getElementById('study-count').innerText = study;
    document.getElementById('distract-count').innerText = distract;

    const insightBox = document.getElementById('insight-box');
    insightBox.style.display = 'block';
    document.getElementById('insight-text').innerText = insight;
}


// --- AI Tutor Logic (Wikipedia API) ---

async function getExplanation() {
    const topic = document.getElementById('topic-input').value.trim();
    const level = document.getElementById('level-select').value;

    if (!topic) return alert("Please enter a topic");

    const output = document.getElementById('explanation-output');
    const titleEl = document.getElementById('exp-title');
    const contentEl = document.getElementById('exp-content');

    // Show loading state
    output.style.display = 'block';
    titleEl.innerText = `Searching for "${topic}"...`;
    contentEl.innerHTML = '<div class="spinner"></div>'; // You might want to add CSS for a spinner

    try {
        // 1. Fetch from Wikipedia
        // Using 'extracts' prop to get summary
        const searchRes = await fetch(`https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=${encodeURIComponent(topic)}&format=json&origin=*`);
        const searchData = await searchRes.json();

        if (!searchData.query.search.length) {
            titleEl.innerText = "Topic Not Found";
            contentEl.innerText = "Sorry, we couldn't find anything on Wikipedia for that topic.";
            return;
        }

        const bestMatch = searchData.query.search[0];
        const pageTitle = bestMatch.title;

        // Fetch actual content
        // sentences: 2 for Basic, 5 for Intermediate, 10 for Advanced
        let sentences = 2;
        if (level === 'Intermediate') sentences = 5;
        if (level === 'Advanced') sentences = 10;

        const contentRes = await fetch(`https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exsentences=${sentences}&exlimit=1&titles=${encodeURIComponent(pageTitle)}&explaintext=1&format=json&origin=*`);
        const contentData = await contentRes.json();

        const pages = contentData.query.pages;
        const pageId = Object.keys(pages)[0];
        const extract = pages[pageId].extract;

        // 2. Resource Recommendations (Client-side)
        const resources = getResourceRecommendations(topic);

        // 3. Construct HTML
        let html = `<h3>Overview</h3><p>${extract}</p>`;

        if (level !== 'Basic') {
            const url = `https://en.wikipedia.org/?curid=${pageId}`;
            html += `<p>Read more on <a href="${url}" target="_blank" style="color: var(--accent-color);">Wikipedia</a></p>`;
        }

        if (resources.length > 0) {
            html += `<h3>Recommended Resources</h3><ul>`;
            resources.forEach(res => {
                html += `<li><a href="${res.url}" target="_blank" style="color: var(--text-color);">${res.name}</a> <span style="color: var(--text-muted);">(${res.type})</span></li>`;
            });
            html += `</ul>`;
        }

        titleEl.innerText = `${pageTitle} (${level})`;
        contentEl.innerHTML = html;

    } catch (e) {
        console.error("Wiki Fetch Error:", e);
        titleEl.innerText = "Error";
        contentEl.innerText = "Failed to fetch explanation. Please check your connection.";
    }
}

function getResourceRecommendations(topic) {
    const t = topic.toLowerCase();
    const resources = [];

    // Simple keyword mapping
    if (t.includes('python') || t.includes('code') || t.includes('java')) {
        resources.push({ name: "Codecademy", url: "https://www.codecademy.com/", type: "Interactive Course" });
        resources.push({ name: "LeetCode", url: "https://leetcode.com/", type: "Practice" });
    }
    if (t.includes('math') || t.includes('calculus') || t.includes('algebra')) {
        resources.push({ name: "Khan Academy", url: "https://www.khanacademy.org/", type: "Videos" });
        resources.push({ name: "Desmos", url: "https://www.desmos.com/", type: "Graphing" });
    }
    if (t.includes('history') || t.includes('war')) {
        resources.push({ name: "CrashCourse History", url: "https://thecrashcourse.com/", type: "YouTube" });
    }
    if (t.includes('ml') || t.includes('ai') || t.includes('neural')) {
        resources.push({ name: "Hugging Face", url: "https://huggingface.co/", type: "Models" });
        resources.push({ name: "Coursera", url: "https://www.coursera.org/", type: "Courses" });
    }

    // Default
    if (resources.length === 0) {
        resources.push({ name: "Google Scholar", url: `https://scholar.google.com/scholar?q=${topic}`, type: "Research" });
        resources.push({ name: "YouTube", url: `https://www.youtube.com/results?search_query=${topic}`, type: "Videos" });
    }

    return resources;
}
