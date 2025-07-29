import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import requests
import json
import tempfile
import os
import threading
from typing import Optional

class APITesterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Analyst API Tester")
        self.root.geometry("800x700")
        
        self.api_base_url = "https://your-vercel-app.vercel.app"
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # API URL Configuration
        ttk.Label(main_frame, text="API Base URL:").grid(row=0, column=0, sticky=tk.W, pady=(0,10))
        self.url_var = tk.StringVar(value=self.api_base_url)
        url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=50)
        url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0,10))
        
        # Health Check Button
        health_frame = ttk.Frame(main_frame)
        health_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0,20))
        
        ttk.Button(health_frame, text="Check API Health", command=self.check_health).pack(side=tk.LEFT)
        self.health_status = ttk.Label(health_frame, text="Status: Unknown", foreground="gray")
        self.health_status.pack(side=tk.LEFT, padx=(10,0))
        
        # Question Input Section
        ttk.Label(main_frame, text="Question/Task:").grid(row=2, column=0, sticky=(tk.W, tk.N), pady=(0,5))
        
        # Question text area
        self.question_text = scrolledtext.ScrolledText(main_frame, height=8, width=60)
        self.question_text.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0,10))
        
        # Sample questions buttons
        sample_frame = ttk.Frame(main_frame)
        sample_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0,10))
        
        ttk.Button(sample_frame, text="Load Movie Sample", 
                  command=self.load_movie_sample).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(sample_frame, text="Load Court Sample", 
                  command=self.load_court_sample).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(sample_frame, text="Clear", 
                  command=self.clear_question).pack(side=tk.LEFT, padx=(0,5))
        
        # File operations
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0,10))
        
        ttk.Button(file_frame, text="Load from File", 
                  command=self.load_from_file).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(file_frame, text="Save to File", 
                  command=self.save_to_file).pack(side=tk.LEFT, padx=(0,5))
        
        # Test API Button
        test_frame = ttk.Frame(main_frame)
        test_frame.grid(row=5, column=0, columnspan=2, pady=(0,20))
        
        self.test_button = ttk.Button(test_frame, text="Test API Endpoint", 
                                     command=self.test_api, style="Accent.TButton")
        self.test_button.pack()
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0,10))
        
        # Response Section
        ttk.Label(main_frame, text="Response:").grid(row=7, column=0, sticky=(tk.W, tk.N), pady=(0,5))
        
        self.response_text = scrolledtext.ScrolledText(main_frame, height=15, width=60)
        self.response_text.grid(row=7, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0,10))
        
        # Configure row weights for expansion
        main_frame.rowconfigure(7, weight=1)
        
    def check_health(self):
        """Check API health endpoint"""
        try:
            response = requests.get(f"{self.url_var.get()}/health", timeout=5)
            if response.status_code == 200:
                self.health_status.config(text="Status: Healthy ✓", foreground="green")
            else:
                self.health_status.config(text=f"Status: Error {response.status_code}", foreground="red")
        except requests.exceptions.RequestException as e:
            self.health_status.config(text="Status: Offline ✗", foreground="red")
            messagebox.showerror("Connection Error", f"Could not connect to API: {str(e)}")
    
    def load_movie_sample(self):
        """Load sample movie analysis question"""
        sample = """Scrape the list of highest grossing films from Wikipedia. It is at the URL:
https://en.wikipedia.org/wiki/List_of_highest-grossing_films

Answer the following questions and respond with a JSON array of strings containing the answer.

1. How many $2 bn movies were released before 2020?
2. Which is the earliest film that grossed over $1.5 bn?
3. What's the correlation between the Rank and Peak?
4. Draw a scatterplot of Rank and Peak along with a dotted red regression line through it.
   Return as a base-64 encoded data URI, `"data:image/png;base64,iVBORw0KG..."` under 100,000 bytes."""
        
        self.question_text.delete(1.0, tk.END)
        self.question_text.insert(1.0, sample)
    
    def load_court_sample(self):
        """Load sample court data analysis question"""
        sample = """The Indian high court judgement dataset contains judgements from the Indian High Courts, downloaded from ecourts website. It contains judgments of 25 high courts, along with raw metadata (as .json) and structured metadata (as .parquet).

This DuckDB query counts the number of decisions in the dataset:

SELECT COUNT(*) FROM read_parquet('s3://indian-high-court-judgments/metadata/parquet/year=*/court=*/bench=*/metadata.parquet?s3_region=ap-south-1');

Answer the following questions and respond with a JSON object containing the answer.

{
  "Which high court disposed the most cases from 2019 - 2022?": "...",
  "What's the regression slope of the date_of_registration - decision_date by year in the court=33_10?": "...",
  "Plot the year and # of days of delay from the above question as a scatterplot with a regression line. Encode as a base64 data URI under 100,000 characters": "data:image/webp:base64,..."
}"""
        
        self.question_text.delete(1.0, tk.END)
        self.question_text.insert(1.0, sample)
    
    def clear_question(self):
        """Clear the question text area"""
        self.question_text.delete(1.0, tk.END)
    
    def load_from_file(self):
        """Load question from a text file"""
        file_path = filedialog.askopenfilename(
            title="Select question file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.question_text.delete(1.0, tk.END)
                self.question_text.insert(1.0, content)
            except Exception as e:
                messagebox.showerror("Error", f"Could not load file: {str(e)}")
    
    def save_to_file(self):
        """Save current question to a text file"""
        file_path = filedialog.asksaveasfilename(
            title="Save question as",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                content = self.question_text.get(1.0, tk.END).strip()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Success", "Question saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")
    
    def test_api(self):
        """Test the API endpoint in a separate thread"""
        question = self.question_text.get(1.0, tk.END).strip()
        if not question:
            messagebox.showwarning("Warning", "Please enter a question or load a sample.")
            return
        
        # Disable button and start progress
        self.test_button.config(state='disabled')
        self.progress.start()
        self.response_text.delete(1.0, tk.END)
        self.response_text.insert(1.0, "Sending request to API...\n\n")
        
        # Run API test in separate thread
        thread = threading.Thread(target=self._test_api_thread, args=(question,))
        thread.daemon = True
        thread.start()
    
    def _test_api_thread(self, question: str):
        """Run API test in background thread"""
        try:
            # Create temporary file with question
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(question)
                temp_file_path = f.name
            
            try:
                # Send request to API
                with open(temp_file_path, 'rb') as f:
                    files = {'file': ('question.txt', f, 'text/plain')}
                    response = requests.post(
                        f"{self.url_var.get()}/api/",
                        files=files,
                        timeout=300  # 5 minute timeout
                    )
                
                # Update UI in main thread
                self.root.after(0, self._handle_api_response, response)
                
            finally:
                # Clean up temp file
                os.unlink(temp_file_path)
                
        except Exception as e:
            self.root.after(0, self._handle_api_error, str(e))
    
    def _handle_api_response(self, response):
        """Handle API response in main thread"""
        try:
            self.progress.stop()
            self.test_button.config(state='normal')
            
            if response.status_code == 200:
                result = response.json()
                formatted_result = json.dumps(result, indent=2, ensure_ascii=False)
                
                self.response_text.delete(1.0, tk.END)
                self.response_text.insert(1.0, f"✓ Success (Status: {response.status_code})\n\n")
                self.response_text.insert(tk.END, formatted_result)
                
                # If response contains base64 images, show info
                result_str = str(result)
                if "data:image/" in result_str:
                    image_count = result_str.count("data:image/")
                    self.response_text.insert(tk.END, f"\n\n📊 Response contains {image_count} base64-encoded image(s)")
                    
            else:
                self.response_text.delete(1.0, tk.END)
                self.response_text.insert(1.0, f"✗ Error (Status: {response.status_code})\n\n")
                self.response_text.insert(tk.END, response.text)
                
        except Exception as e:
            self._handle_api_error(f"Response parsing error: {str(e)}")
    
    def _handle_api_error(self, error_msg: str):
        """Handle API error in main thread"""
        self.progress.stop()
        self.test_button.config(state='normal')
        
        self.response_text.delete(1.0, tk.END)
        self.response_text.insert(1.0, f"✗ Request Failed\n\n")
        self.response_text.insert(tk.END, f"Error: {error_msg}")
        
        messagebox.showerror("API Error", f"Request failed: {error_msg}")

def main():
    root = tk.Tk()
    app = APITesterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()