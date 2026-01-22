import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
import os
import random
import time
from datetime import datetime
import google.generativeai as genai

class StudyBuddyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personalized AI Study Buddy")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f4f8")
        
        # API key for Google Gemini
        self.api_key = "AIzaSyDytty4RiWuzz2oYoksVvYt4gszlJHOxRs"  # Replace with your actual API key
        self.model_name = "gemini-1.5-pro-latest"  # Using Gemini Pro model
        
        # Initialize Gemini
        if self.api_key and self.api_key != "YOUR_GEMINI_API_KEY":
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        
        # User preferences
        self.user_name = "Student"
        self.current_subject = "General"
        self.difficulty_level = "Intermediate"
        self.learning_style = "Visual"
        
        # Study session data
        self.study_history = []
        self.quiz_results = []
        self.current_quiz = []
        self.quiz_active = False
        
        # Setup UI components
        self.setup_ui()
        
        # Initialize conversation
        self.messages = []
        self.add_system_message("You are an educational AI assistant called 'Study Buddy'. Your purpose is to help students learn by providing tailored study materials, answering questions, and creating practice tests. Be encouraging, clear, and adapt to the student's learning style and difficulty level.")
        
        # Welcome message
        self.root.after(500, self.display_bot_message, f"👋 Hello {self.user_name}! I'm your personal Study Buddy. I can help you with study materials, answer questions, and create practice tests. What subject would you like to study today?")
    
    def setup_ui(self):
        # Create main container
        self.main_container = tk.Frame(self.root, bg="#f0f4f8")
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create header
        header_frame = tk.Frame(self.main_container, bg="#f0f4f8")
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Logo/Title
        title_label = tk.Label(header_frame, text="Personalized AI Study Buddy", 
                              font=("Arial", 20, "bold"), bg="#f0f4f8", fg="#2a4365")
        title_label.pack(side=tk.LEFT)
        
        # Settings button
        settings_button = tk.Button(header_frame, text="⚙️ Settings", 
                                   command=self.open_settings,
                                   bg="#4299e1", fg="white", 
                                   font=("Arial", 10), padx=10, pady=5)
        settings_button.pack(side=tk.RIGHT)
        
        # Create sidebar for subject selection
        self.sidebar = tk.Frame(self.main_container, width=200, bg="#e2e8f0", padx=10, pady=10)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        
        # Make sure sidebar maintains its width
        self.sidebar.pack_propagate(False)
        
        # Subject selection label
        subject_label = tk.Label(self.sidebar, text="Study Subjects", 
                                font=("Arial", 14, "bold"), bg="#e2e8f0", fg="#2a4365")
        subject_label.pack(anchor="w", pady=(0, 10))
        
        # Subject buttons
        subjects = ["Mathematics", "Science", "History", "Language Arts", "Computer Science"]
        for subject in subjects:
            subject_btn = tk.Button(self.sidebar, text=subject, 
                                   command=lambda s=subject: self.change_subject(s),
                                   bg="#4299e1", fg="white", 
                                   font=("Arial", 10), padx=10, pady=5,
                                   width=15, anchor="w")
            subject_btn.pack(pady=5, fill=tk.X)
        
        # Tools section
        tools_label = tk.Label(self.sidebar, text="Study Tools", 
                              font=("Arial", 14, "bold"), bg="#e2e8f0", fg="#2a4365")
        tools_label.pack(anchor="w", pady=(20, 10))
        
        # Tool buttons
        quiz_btn = tk.Button(self.sidebar, text="Generate Quiz", 
                            command=self.generate_quiz,
                            bg="#38b2ac", fg="white", 
                            font=("Arial", 10), padx=10, pady=5,
                            width=15, anchor="w")
        quiz_btn.pack(pady=5, fill=tk.X)
        
        flashcards_btn = tk.Button(self.sidebar, text="Create Flashcards", 
                                  command=self.create_flashcards,
                                  bg="#38b2ac", fg="white", 
                                  font=("Arial", 10), padx=10, pady=5,
                                  width=15, anchor="w")
        flashcards_btn.pack(pady=5, fill=tk.X)
        
        summary_btn = tk.Button(self.sidebar, text="Summarize Topic", 
                               command=self.summarize_topic,
                               bg="#38b2ac", fg="white", 
                               font=("Arial", 10), padx=10, pady=5,
                               width=15, anchor="w")
        summary_btn.pack(pady=5, fill=tk.X)
        
        # Create main chat area
        chat_frame = tk.Frame(self.main_container, bg="white", padx=15, pady=15)
        chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, 
                                                     bg="white", height=20, 
                                                     font=("Arial", 12))
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.chat_display.config(state=tk.DISABLED)
        
        # Configure tags for text styling
        self.chat_display.tag_configure("user_tag", foreground="#3182ce", font=("Arial", 12, "bold"))
        self.chat_display.tag_configure("user_message", font=("Arial", 12))
        self.chat_display.tag_configure("bot_tag", foreground="#38a169", font=("Arial", 12, "bold"))
        self.chat_display.tag_configure("bot_message", font=("Arial", 12))
        self.chat_display.tag_configure("system", foreground="#718096", font=("Arial", 10, "italic"))
        self.chat_display.tag_configure("quiz", foreground="#805ad5", font=("Arial", 12))
        self.chat_display.tag_configure("quiz_question", font=("Arial", 12, "bold"), foreground="#805ad5")
        self.chat_display.tag_configure("quiz_option", font=("Arial", 12))
        self.chat_display.tag_configure("quiz_correct", foreground="#38a169", font=("Arial", 12, "bold"))
        self.chat_display.tag_configure("quiz_incorrect", foreground="#e53e3e", font=("Arial", 12, "bold"))
        
        # Input area
        input_frame = tk.Frame(chat_frame, bg="white")
        input_frame.pack(fill=tk.X, expand=False)
        
        # Message input field
        self.message_input = tk.Text(input_frame, height=3, width=40, 
                                    font=("Arial", 12), wrap=tk.WORD,
                                    padx=10, pady=10)
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.message_input.bind("<Return>", self.send_on_enter)
        
        # Placeholder text
        self.message_input.insert("1.0", "Ask a question or request study materials...")
        self.message_input.bind("<FocusIn>", self.clear_placeholder)
        self.message_input.bind("<FocusOut>", self.add_placeholder)
        
        # Send button
        send_button = tk.Button(input_frame, text="Send", command=self.send_message,
                               bg="#4299e1", fg="white", font=("Arial", 12, "bold"),
                               relief=tk.FLAT, padx=15, pady=10)
        send_button.pack(side=tk.RIGHT)
        
        # Status bar
        self.status_bar = tk.Label(chat_frame, text="Ready to help with your studies", 
                                  bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                  bg="#e2e8f0", fg="#4a5568", font=("Arial", 10))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def clear_placeholder(self, event):
        if self.message_input.get("1.0", "end-1c") == "Ask a question or request study materials...":
            self.message_input.delete("1.0", tk.END)
    
    def add_placeholder(self, event):
        if not self.message_input.get("1.0", "end-1c").strip():
            self.message_input.insert("1.0", "Ask a question or request study materials...")
    
    def send_on_enter(self, event):
        if not event.state & 0x1:  # Check if Shift key is not pressed
            self.send_message()
            return "break"
    
    def send_message(self):
        user_message = self.message_input.get("1.0", tk.END).strip()
        if not user_message or user_message == "Ask a question or request study materials...":
            return
        
        # Clear input field
        self.message_input.delete("1.0", tk.END)
        
        # Handle quiz answers if quiz is active
        if self.quiz_active and user_message.lower() in ["a", "b", "c", "d"]:
            self.check_quiz_answer(user_message.upper())
            return
        
        # Display user message
        self.display_user_message(user_message)
        
        # Add to messages
        self.add_user_message(user_message)
        
        # Update status
        self.status_bar.config(text="Thinking...")
        
        # Process in a separate thread
        threading.Thread(target=self.get_ai_response, daemon=True).start()
    
    def add_system_message(self, content):
        self.messages.append({"role": "system", "content": content})
    
    def add_user_message(self, content):
        self.messages.append({"role": "user", "content": content})
    
    def add_assistant_message(self, content):
        self.messages.append({"role": "assistant", "content": content})
    
    def get_ai_response(self):
        try:
            if not self.api_key or self.api_key == "YOUR_GEMINI_API_KEY":
                response_text = "Please set your Google Gemini API key in the settings to enable AI responses."
            else:
                # Prepare context with user preferences
                context = f"Current subject: {self.current_subject}. Difficulty level: {self.difficulty_level}. Learning style: {self.learning_style}."
                
                # Add context to the last user message
                if len(self.messages) > 0 and self.messages[-1]["role"] == "user":
                    self.messages[-1]["content"] += f"\n\n[Context: {context}]"
                
                # Convert messages to Gemini format
                chat = self.model.start_chat(history=[])
                
                # Combine all previous messages into a single prompt for Gemini
                prompt = ""
                for msg in self.messages:
                    if msg["role"] == "system":
                        prompt += f"System: {msg['content']}\n"
                    elif msg["role"] == "user":
                        prompt += f"User: {msg['content']}\n"
                    elif msg["role"] == "assistant":
                        prompt += f"Assistant: {msg['content']}\n"
                
                # Get response from Gemini
                response = chat.send_message(prompt)
                response_text = response.text
                
                # Add the response to messages
                self.add_assistant_message(response_text)
                
                # Log the interaction for study history
                self.study_history.append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "subject": self.current_subject,
                    "interaction": {
                        "user": self.messages[-2]["content"],
                        "assistant": response_text
                    }
                })
            
            # Update status and display response
            self.root.after(0, lambda: self.status_bar.config(text=f"Studying {self.current_subject} | {self.difficulty_level} level"))
            self.root.after(0, self.display_bot_message, response_text)
        except Exception as e:
            error_message = f"Error: {str(e)}"
            self.root.after(0, lambda: self.status_bar.config(text="Error occurred"))
            self.root.after(0, self.display_bot_message, error_message)
    
    def display_user_message(self, message):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{self.user_name}: ", "user_tag")
        self.chat_display.insert(tk.END, f"{message}\n\n", "user_message")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def display_bot_message(self, message):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "Study Buddy: ", "bot_tag")
        self.chat_display.insert(tk.END, f"{message}\n\n", "bot_message")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def display_system_message(self, message):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"System: {message}\n\n", "system")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def change_subject(self, subject):
        self.current_subject = subject
        self.status_bar.config(text=f"Studying {subject} | {self.difficulty_level} level")
        self.display_system_message(f"Subject changed to {subject}")
        
        # Inform the AI about the subject change
        prompt = f"The student has changed the subject to {subject}. Please provide a brief introduction to this subject and suggest some key topics to study."
        self.add_user_message(prompt)
        
        # Process in a separate thread
        threading.Thread(target=self.get_ai_response, daemon=True).start()
    
    def open_settings(self):
        # Create settings popup
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Study Buddy Settings")
        settings_window.geometry("400x500")
        settings_window.configure(bg="#f0f4f8")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Settings container
        settings_frame = tk.Frame(settings_window, bg="#f0f4f8", padx=20, pady=20)
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # API Key
        api_label = tk.Label(settings_frame, text="Google Gemini API Key:", 
                            font=("Arial", 12), bg="#f0f4f8", anchor="w")
        api_label.pack(fill=tk.X, pady=(0, 5))
        
        api_entry = tk.Entry(settings_frame, font=("Arial", 12), show="*")
        api_entry.pack(fill=tk.X, pady=(0, 15))
        if self.api_key and self.api_key != "YOUR_GEMINI_API_KEY":
            api_entry.insert(0, self.api_key)
        
        # User Name
        name_label = tk.Label(settings_frame, text="Your Name:", 
                             font=("Arial", 12), bg="#f0f4f8", anchor="w")
        name_label.pack(fill=tk.X, pady=(0, 5))
        
        name_entry = tk.Entry(settings_frame, font=("Arial", 12))
        name_entry.pack(fill=tk.X, pady=(0, 15))
        name_entry.insert(0, self.user_name)
        
        # Difficulty Level
        difficulty_label = tk.Label(settings_frame, text="Difficulty Level:", 
                                   font=("Arial", 12), bg="#f0f4f8", anchor="w")
        difficulty_label.pack(fill=tk.X, pady=(0, 5))
        
        difficulty_var = tk.StringVar(value=self.difficulty_level)
        difficulty_options = ["Beginner", "Intermediate", "Advanced", "Expert"]
        difficulty_menu = ttk.Combobox(settings_frame, textvariable=difficulty_var, 
                                      values=difficulty_options, font=("Arial", 12))
        difficulty_menu.pack(fill=tk.X, pady=(0, 15))
        
        # Learning Style
        style_label = tk.Label(settings_frame, text="Learning Style:", 
                              font=("Arial", 12), bg="#f0f4f8", anchor="w")
        style_label.pack(fill=tk.X, pady=(0, 5))
        
        style_var = tk.StringVar(value=self.learning_style)
        style_options = ["Visual", "Auditory", "Reading/Writing", "Kinesthetic"]
        style_menu = ttk.Combobox(settings_frame, textvariable=style_var, 
                                 values=style_options, font=("Arial", 12))
        style_menu.pack(fill=tk.X, pady=(0, 15))
        
        # Save button
        save_button = tk.Button(settings_frame, text="Save Settings", 
                               command=lambda: self.save_settings(
                                   api_entry.get(),
                                   name_entry.get(),
                                   difficulty_var.get(),
                                   style_var.get(),
                                   settings_window
                               ),
                               bg="#4299e1", fg="white", 
                               font=("Arial", 12, "bold"), padx=10, pady=5)
        save_button.pack(pady=20)
    
    def save_settings(self, api_key, user_name, difficulty, learning_style, window):
        # Update settings
        if api_key and api_key != "YOUR_GEMINI_API_KEY":
            self.api_key = api_key
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
            except Exception as e:
                messagebox.showerror("API Error", f"Failed to initialize Gemini API: {str(e)}")
        
        self.user_name = user_name if user_name else "Student"
        self.difficulty_level = difficulty
        self.learning_style = learning_style
        
        # Update status bar
        self.status_bar.config(text=f"Studying {self.current_subject} | {self.difficulty_level} level")
        
        # Close settings window
        window.destroy()
        
        # Inform the AI about the settings change
        self.add_system_message(f"User settings updated: Name: {self.user_name}, Difficulty: {self.difficulty_level}, Learning Style: {self.learning_style}")
        
        # Display confirmation
        self.display_system_message("Settings updated successfully!")
    
    def generate_quiz(self):
        # End any active quiz
        if self.quiz_active:
            self.quiz_active = False
            self.current_quiz = []
            self.display_system_message("Previous quiz ended.")
        
        # Request a quiz from the AI
        prompt = f"Generate a quiz with 5 multiple-choice questions about {self.current_subject} at {self.difficulty_level} level. Format each question with options A, B, C, and D. After each question, indicate the correct answer with 'Correct: [letter]' on a new line."
        
        self.display_system_message(f"Generating a quiz on {self.current_subject}...")
        self.add_user_message(prompt)
        
        # Process in a separate thread
        threading.Thread(target=self.get_quiz_from_ai, daemon=True).start()
    
    def get_quiz_from_ai(self):
        try:
            if not self.api_key or self.api_key == "YOUR_GEMINI_API_KEY":
                response_text = "Please set your Google Gemini API key in the settings to enable quiz generation."
                self.root.after(0, self.display_bot_message, response_text)
                return
            
            # Prepare the prompt for quiz generation
            prompt = f"Generate a quiz with 5 multiple-choice questions about {self.current_subject} at {self.difficulty_level} level. Format each question with options A, B, C, and D. After each question, indicate the correct answer with 'Correct: [letter]' on a new line."
            
            # Get response from Gemini
            chat = self.model.start_chat(history=[])
            response = chat.send_message(prompt)
            quiz_text = response.text
            
            # Add the response to messages
            self.add_assistant_message(quiz_text)
            
            # Parse the quiz
            self.parse_and_display_quiz(quiz_text)
            
        except Exception as e:
            error_message = f"Error generating quiz: {str(e)}"
            self.root.after(0, lambda: self.status_bar.config(text="Error occurred"))
            self.root.after(0, self.display_bot_message, error_message)
    
    def parse_and_display_quiz(self, quiz_text):
        # Split the quiz into questions
        questions = []
        current_question = ""
        
        for line in quiz_text.split('\n'):
            if line.strip().startswith(('1.', '2.', '3.', '4.', '5.')) and current_question:
                questions.append(current_question)
                current_question = line
            else:
                if current_question or line.strip():
                    current_question += line + '\n'
        
        if current_question:
            questions.append(current_question)
        
        # Process each question
        self.current_quiz = []
        for q in questions:
            # Extract the correct answer
            correct = None
            q_lines = q.split('\n')
            for i, line in enumerate(q_lines):
                if line.strip().startswith('Correct:'):
                    correct = line.strip().split(':')[1].strip()
                    q_lines.pop(i)
                    break
            
            if correct:
                self.current_quiz.append({
                    'question': '\n'.join(q_lines),
                    'correct': correct
                })
        
        # Display the first question
        self.quiz_active = True
        self.display_quiz_question(0)
    
    def display_quiz_question(self, index):
        if index < len(self.current_quiz):
            question = self.current_quiz[index]
            
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.insert(tk.END, f"Quiz Question {index+1}/{len(self.current_quiz)}\n", "quiz_question")
            self.chat_display.insert(tk.END, f"{question['question']}\n", "quiz")
            self.chat_display.insert(tk.END, "Type A, B, C, or D to answer.\n\n", "system")
            self.chat_display.see(tk.END)
            self.chat_display.config(state=tk.DISABLED)
            
            # Update the current question index
            self.current_quiz_index = index
        else:
            # Quiz completed
            self.quiz_active = False
            correct_count = sum(1 for q in self.quiz_results if q['result'] == 'correct')
            
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.insert(tk.END, f"Quiz Completed!\n", "quiz_question")
            self.chat_display.insert(tk.END, f"You got {correct_count} out of {len(self.quiz_results)} questions correct.\n\n", "quiz")
            self.chat_display.see(tk.END)
            self.chat_display.config(state=tk.DISABLED)
            
            # Add quiz results to history
            self.quiz_history = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "subject": self.current_subject,
                "score": f"{correct_count}/{len(self.quiz_results)}",
                "questions": self.current_quiz,
                "answers": self.quiz_results
            }
            
            # Ask AI to provide feedback on quiz performance
            prompt = f"The student completed a quiz on {self.current_subject} and got {correct_count} out of {len(self.quiz_results)} questions correct. Please provide feedback on their performance and suggest topics they might want to review."
            self.add_user_message(prompt)
            threading.Thread(target=self.get_ai_response, daemon=True).start()
    
    def check_quiz_answer(self, answer):
        if not self.quiz_active or not hasattr(self, 'current_quiz_index'):
            return
        
        current_q = self.current_quiz[self.current_quiz_index]
        is_correct = answer == current_q['correct']
        
        # Display result
        self.chat_display.config(state=tk.NORMAL)
        if is_correct:
            self.chat_display.insert(tk.END, f"Your answer: {answer} - Correct! ✓\n\n", "quiz_correct")
        else:
            self.chat_display.insert(tk.END, f"Your answer: {answer} - Incorrect. ✗ The correct answer is {current_q['correct']}.\n\n", "quiz_incorrect")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # Record result
        self.quiz_results.append({
            'question_index': self.current_quiz_index,
            'user_answer': answer,
            'correct_answer': current_q['correct'],
            'result': 'correct' if is_correct else 'incorrect'
        })
        
        # Move to next question after a short delay
        self.root.after(1500, lambda: self.display_quiz_question(self.current_quiz_index + 1))
    
    def create_flashcards(self):
        # Request flashcards from the AI
        prompt = f"Create a set of 5 flashcards for studying {self.current_subject} at {self.difficulty_level} level. Format each flashcard with 'Term:' and 'Definition:' on separate lines."
        
        self.display_system_message(f"Generating flashcards for {self.current_subject}...")
        self.add_user_message(prompt)
        
        # Process in a separate thread
        threading.Thread(target=self.get_ai_response, daemon=True).start()
    
    def summarize_topic(self):
        # Open a dialog to get the topic
        topic_window = tk.Toplevel(self.root)
        topic_window.title("Summarize Topic")
        topic_window.geometry("400x200")
        topic_window.configure(bg="#f0f4f8")
        topic_window.transient(self.root)
        topic_window.grab_set()
        
        # Topic container
        topic_frame = tk.Frame(topic_window, bg="#f0f4f8", padx=20, pady=20)
        topic_frame.pack(fill=tk.BOTH, expand=True)
        
        # Topic label
        topic_label = tk.Label(topic_frame, text=f"Enter a {self.current_subject} topic to summarize:", 
                              font=("Arial", 12), bg="#f0f4f8", anchor="w")
        topic_label.pack(fill=tk.X, pady=(0, 10))
        
        # Topic entry
        topic_entry = tk.Entry(topic_frame, font=("Arial", 12))
        topic_entry.pack(fill=tk.X, pady=(0, 20))
        topic_entry.focus_set()
        
        # Submit button
        submit_button = tk.Button(topic_frame, text="Get Summary", 
                                 command=lambda: self.request_summary(topic_entry.get(), topic_window),
                                 bg="#4299e1", fg="white", 
                                 font=("Arial", 12, "bold"), padx=10, pady=5)
        submit_button.pack()
        
        # Bind Enter key
        topic_entry.bind("<Return>", lambda event: self.request_summary(topic_entry.get(), topic_window))
    
    def request_summary(self, topic, window):
        if not topic.strip():
            messagebox.showwarning("Input Required", "Please enter a topic to summarize.")
            return
        
        window.destroy()
        
        # Request summary from the AI
        prompt = f"Please provide a comprehensive summary of the topic '{topic}' in {self.current_subject}. Include key concepts, important facts, and any formulas or principles that are essential to understanding this topic. Make the explanation suitable for a {self.difficulty_level} level student with a {self.learning_style} learning style."
        
        self.display_system_message(f"Generating summary for '{topic}'...")
        self.add_user_message(prompt)
        
        # Process in a separate thread
        threading.Thread(target=self.get_ai_response, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = StudyBuddyApp(root)
    root.mainloop()