import wikipedia

class StudyBuddy:
    def __init__(self):
        # Explicitly set the user agent to avoid Wikipedia API blocking
        wikipedia.set_user_agent("AI_Study_Buddy/1.0 (Educational Purpose)")

    def get_explanation(self, topic, level):
        """
        Returns a structured explanation based on the topic and level.
        Prioritizes Wikipedia for dynamic knowledge, falls back to static content.
        Includes resource recommendations.
        """
        topic_lower = topic.lower()
        
        # 1. Get Core Content (Try Wikipedia first)
        wiki_data = self._fetch_wikipedia_content(topic, level)
        
        if wiki_data:
            content_html = wiki_data['content']
            source = "Source: Wikipedia"
        else:
            # Fallback to internal knowledge base if Wiki fails (e.g., offline)
            content_html = self._get_fallback_content(topic_lower, level)
            source = "Source: Internal Database"

        # 2. Get Resource Recommendations
        resources = self._get_resource_recommendations(topic_lower)

        # 3. Construct Final Response
        final_html = content_html
        
        if resources:
            final_html += "<h3>Recommended Study Resources</h3><ul>"
            for res in resources:
                final_html += f"<li><a href='{res['url']}' target='_blank'>{res['name']}</a> - {res['type']}</li>"
            final_html += "</ul>"
            
        final_html += f"<p><small><i>{source}</i></small></p>"

        return {
            "title": f"{topic} ({level})",
            "content": final_html
        }

    def _fetch_wikipedia_content(self, topic, level):
        try:
            # Limit sentences based on level
            sentences = 2 if level == "Basic" else 5 if level == "Intermediate" else 10
            
            # Fetch summary
            summary = wikipedia.summary(topic, sentences=sentences)
            
            # For Advanced, try to get sections (simplified here by just getting more summary or full page intro)
            # A real robustness improvement would be checking disambiguation
            
            page = wikipedia.page(topic, auto_suggest=True)
            url = page.url
            
            html = f"<h3>Overview</h3><p>{summary}</p>"
            
            if level == "Intermediate" or level == "Advanced":
                 html += f"<p>Read the full article at: <a href='{url}' target='_blank'>Wikipedia</a></p>"
                 
            return {"content": html}
            
        except wikipedia.exceptions.DisambiguationError as e:
            # If ambiguous, list options
            options = e.options[:5]
            html = f"<p>'{topic}' is ambiguous. Did you mean:</p><ul>"
            for opt in options:
                html += f"<li>{opt}</li>"
            html += "</ul>"
            return {"content": html}
            
        except wikipedia.exceptions.PageError:
            return None # Fallback
        except Exception as e:
            print(f"Wiki Error: {e}")
            return None # Fallback

    def _get_resource_recommendations(self, topic):
        """
        Returns a list of curated resources based on keywords.
        """
        resources = []
        
        # Keyword matching
        if any(w in topic for w in ['python', 'java', 'code', 'programming', 'c++']):
            resources.append({"name": "Codecademy", "url": "https://www.codecademy.com/", "type": "Interactive Course"})
            resources.append({"name": "LeetCode", "url": "https://leetcode.com/", "type": "Practice Problems"})
            resources.append({"name": "GeeksforGeeks", "url": "https://www.geeksforgeeks.org/", "type": "Tutorials"})
            
        if any(w in topic for w in ['math', 'calculus', 'algebra', 'geometry', 'physics']):
            resources.append({"name": "Khan Academy", "url": "https://www.khanacademy.org/", "type": "Video Lessons"})
            resources.append({"name": "Desmos", "url": "https://www.desmos.com/", "type": "Graphing Tool"})
             
        if any(w in topic for w in ['history', 'revolution', 'war', 'ancient']):
            resources.append({"name": "CrashCourse History", "url": "https://thecrashcourse.com/topic/history/", "type": "Video Series"})
            resources.append({"name": "History.com", "url": "https://www.history.com/", "type": "Articles"})

        if any(w in topic for w in ['ml', 'ai', 'machine learning', 'neural']):
            resources.append({"name": "Coursera (Andrew Ng)", "url": "https://www.coursera.org/", "type": "Online Course"})
            resources.append({"name": "Hugging Face", "url": "https://huggingface.co/", "type": "Models & Datasets"})
            resources.append({"name": "Kaggle", "url": "https://www.kaggle.com/", "type": "Data Science Community"})

        # Default Generic
        if not resources:
             resources.append({"name": "YouTube Search", "url": f"https://www.youtube.com/results?search_query={topic}", "type": "Videos"})
             resources.append({"name": "Google Scholar", "url": f"https://scholar.google.com/scholar?q={topic}", "type": "Academic Papers"})

        return resources

    def _get_fallback_content(self, topic, level):
        # Simplified fallback for offline/error cases
        knowledge_base = {
             # ... (We can keep a few small ones or just a generic message to save space)
             "python": "Python is a high-level general-purpose programming language.",
             "photosynthesis": "The process by which green plants and some other organisms use sunlight to synthesize foods."
        }
        
        definition = knowledge_base.get(topic, f"Sorry, I couldn't find detailed info on '{topic}'. Please check your spelling or internet connection.")
        
        return f"""
        <h3>Definition (Offline Mode)</h3>
        <p>{definition}</p>
        """

# Singleton
study_buddy = StudyBuddy()
