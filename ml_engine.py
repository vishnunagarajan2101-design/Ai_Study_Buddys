from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import pandas as pd
import numpy as np

class ChatAnalyzer:
    def __init__(self):
        self.vectorizer = CountVectorizer()
        self.model = MultinomialNB()
        self.is_trained = False
        
        # Initial training on startup with dummy data
        self._initial_train()

    def _initial_train(self):
        """
        Trains the model on a small embedded dataset to distinguish 
        Study vs Distraction.
        """
        # Small dataset for demonstration
        data = {
            'text': [
                "I need help with calculus", "Let's study python", "What is photosynthesis?", 
                "Explain Newton's laws", "When is the exam?", "homework is due tomorrow",
                "solving equations is hard", "reading history book", "focusing on chemistry",
                "let's play a game", "watch movie tonight?", "send me the meme", 
                "hahaha that's funny", "bored tired sleepy", "going to sleep", 
                "ordering pizza", "check instagram", "playing valorant", "listening to music"
            ],
            'label': [
                'Study', 'Study', 'Study', 'Study', 'Study', 'Study', 'Study', 'Study', 'Study',
                'Distraction', 'Distraction', 'Distraction', 'Distraction', 'Distraction', 
                'Distraction', 'Distraction', 'Distraction', 'Distraction', 'Distraction'
            ]
        }
        
        df = pd.DataFrame(data)
        
        # Convert text to numerical vectors
        X = self.vectorizer.fit_transform(df['text'])
        y = df['label']
        
        # Train the Naive Bayes classifier
        self.model.fit(X, y)
        self.is_trained = True
        print("ML Model trained successfully on dummy data.")

    def predict(self, message):
        """
        Predicts if a message is 'Study' or 'Distraction'.
        """
        if not self.is_trained:
            return "Unknown"
        
        # Transform the new message
        message_vector = self.vectorizer.transform([message])
        prediction = self.model.predict(message_vector)
        return prediction[0]

    def analyze_messages(self, messages):
        """
        Takes a list of message strings and returns stats.
        """
        if not messages:
            return {
                "study_count": 0,
                "distraction_count": 0,
                "focus_score": 0,
                "insights": "No messages to analyze yet."
            }
            
        study_count = 0
        distraction_count = 0
        
        for msg in messages:
            if self.predict(msg) == 'Study':
                study_count += 1
            else:
                distraction_count += 1
                
        total = study_count + distraction_count
        focus_score = (study_count / total * 100) if total > 0 else 0
        
        # Generate simple insights
        if focus_score > 75:
            insight = "Excellent focus! Keep it up."
        elif focus_score > 50:
            insight = "Good study session, but try to minimize distractions."
        else:
            insight = "High distraction level detected. Suggest taking a break or using Focus Mode."
            
        return {
            "study_count": study_count,
            "distraction_count": distraction_count,
            "focus_score": round(focus_score, 1),
            "insights": insight
        }

# Singleton instance
analyzer = ChatAnalyzer()
