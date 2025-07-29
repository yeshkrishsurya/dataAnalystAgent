#!/usr/bin/env python3
"""
Data Analyst API Endpoint Tester
A GUI application to test the Data Analyst Agent API endpoints
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import requests
import json
import tempfile
import os
import threading
import time
from datetime import datetime
from typing import Optional

class EndpointTester:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Analyst API Endpoint Tester")
        self.root.geometry("1000x800")
        
        # API Configuration
        self.api_base_url = "http://127.0.0.1:8000"
        self.request_history = []
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Main testing tab
        self.setup_main_tab(notebook)
        
        # History tab
        self.setup_history_tab(notebook)
        
        # Settings tab
        self.setup_settings_tab(notebook)
    
    def setup_main_tab(self, notebook):
        """Setup the main testing tab"""
        main_frame = ttk.Frame(notebook)
        notebook.add(main_frame, text="API Tester")
        
        # Configure grid
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        # API URL Configuration
        ttk.Label(main_frame, text="API Base URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_var = tk.StringVar(value=self.api_base_url)
        url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=60)
        url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Health Check Section
        health_frame = ttk.LabelFrame(main_frame, text="Health Check", padding="10")
        health_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        health_frame.columnconfigure(1, weight=1)
        
        ttk.Button(health_frame, text="Check Health", command=self.check_health).grid(row=0, column=0)
        self.health_status = ttk.Label(health_frame, text="Status: Unknown", foreground="gray")
        self.health_status.grid(row=0, column=1, sticky=tk.W, padx=(10,0))
        
        # Question Input Section
        question_frame = ttk.LabelFrame(main_frame, text="Question/Task Input", padding="10")
        question_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        question_frame.columnconfigure(0, weight=1)
        question_frame.rowconfigure(1, weight=1)
        
        # Sample questions buttons
        sample_frame = ttk.Frame(question_frame)
        sample_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0,10))
        
        ttk.Button(sample_frame, text="Load Movie Sample", 
                  command=self.load_movie_sample).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(sample_frame, text="Load Court Sample", 
                  command=self.load_court_sample).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(sample_frame, text="Load from File", 
                  command=self.load_from_file).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(sample_frame, text="Clear", 
                  command=self.clear_question).pack(side=tk.LEFT, padx=(0,5))
        
        # Question text area
        self.question_text = scrolledtext.ScrolledText(question_frame, height=8, width=80)
        self.question_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Test Controls
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.test_button = ttk.Button(controls_frame, text="🚀 Test API Endpoint", 
                                     command=self.test_api, style="Accent.TButton")
        self.test_button.pack(side=tk.LEFT, padx=(0,10))
        
        ttk.Button(controls_frame, text="💾 Save Response", 
                  command=self.save_response).pack(side=tk.LEFT, padx=(0,10))
        
        ttk.Button(controls_frame, text="🗑️ Clear Response", 
                  command=self.clear_response).pack(side=tk.LEFT)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Response Section
        response_frame = ttk.LabelFrame(main_frame, text="API Response", padding="10")
        response_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        response_frame.columnconfigure(0, weight=1)
        response_frame.rowconfigure(0, weight=1)
        
        self.response_text = scrolledtext.ScrolledText(response_frame, height=15, width=80)
        self.response_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def setup_history_tab(self, notebook):
        """Setup the request history tab"""
        history_frame = ttk.Frame(notebook)
        notebook.add(history_frame, text="Request History")
        
        # History controls
        controls_frame = ttk.Frame(history_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(controls_frame, text="Clear History", 
                  command=self.clear_history).pack(side=tk.LEFT)
        ttk.Button(controls_frame, text="Export History", 
                  command=self.export_history).pack(side=tk.LEFT, padx=(10,0))
        
        # History tree
        self.history_tree = ttk.Treeview(history_frame, columns=('time', 'status', 'duration'), show='headings')
        self.history_tree.heading('time', text='Time')
        self.history_tree.heading('status', text='Status')
        self.history_tree.heading('duration', text='Duration (s)')
        
        self.history_tree.column('time', width=150)
        self.history_tree.column('status', width=100)
        self.history_tree.column('duration', width=100)
        
        # Scrollbar for history
        history_scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=history_scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10,0), pady=(0,10))
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0,10), pady=(0,10))
        
        # Bind double-click to view details
        self.history_tree.bind('<Double-1>', self.view_history_details)
    
    def setup_settings_tab(self, notebook):
        """Setup the settings tab"""
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="Settings")
        
        # API Settings
        api_frame = ttk.LabelFrame(settings_frame, text="API Configuration", padding="10")
        api_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(api_frame, text="Timeout (seconds):").grid(row=0, column=0, sticky=tk.W)
        self.timeout_var = tk.StringVar(value="300")
        ttk.Entry(api_frame, textvariable=self.timeout_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=(10,0))
        
        ttk.Label(api_frame, text="Retry Attempts:").grid(row=1, column=0, sticky=tk.W, pady=(10,0))
        self.retry_var = tk.StringVar(value="3")
        ttk.Entry(api_frame, textvariable=self.retry_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=(10,0), pady=(10,0))
        
        # Logging Settings
        log_frame = ttk.LabelFrame(settings_frame, text="Logging", padding="10")
        log_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.log_requests_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(log_frame, text="Log all requests", 
                       variable=self.log_requests_var).pack(anchor=tk.W)
        
        self.verbose_logging_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(log_frame, text="Verbose logging", 
                       variable=self.verbose_logging_var).pack(anchor=tk.W)
    
    def check_health(self):
        """Check API health endpoint"""
        try:
            self.update_status("Checking API health...")
            response = requests.get(f"{self.url_var.get()}/health", timeout=5)
            if response.status_code == 200:
                self.health_status.config(text="Status: Healthy ✅", foreground="green")
                self.update_status("API is healthy")
            else:
                self.health_status.config(text=f"Status: Error {response.status_code} ❌", foreground="red")
                self.update_status(f"API health check failed: {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.health_status.config(text="Status: Offline ❌", foreground="red")
            self.update_status("API is offline")
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
        self.update_status("Movie sample question loaded")
    
    def load_court_sample(self):
        """Load sample court data analysis question"""
        sample = """The Indian high court judgement dataset contains judgements from the Indian High Courts.

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
        self.update_status("Court sample question loaded")
    
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
                self.update_status(f"Question loaded from {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not load file: {str(e)}")
                self.update_status("Failed to load file")
    
    def clear_question(self):
        """Clear the question text area"""
        self.question_text.delete(1.0, tk.END)
        self.update_status("Question cleared")
    
    def clear_response(self):
        """Clear the response text area"""
        self.response_text.delete(1.0, tk.END)
        self.update_status("Response cleared")
    
    def save_response(self):
        """Save current response to a file"""
        response_content = self.response_text.get(1.0, tk.END).strip()
        if not response_content:
            messagebox.showwarning("Warning", "No response to save.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save response as",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(response_content)
                messagebox.showinfo("Success", "Response saved successfully!")
                self.update_status(f"Response saved to {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")
                self.update_status("Failed to save response")
    
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
        self.response_text.insert(1.0, "🚀 Sending request to API...\n\n")
        self.update_status("Testing API endpoint...")
        
        # Run API test in separate thread
        thread = threading.Thread(target=self._test_api_thread, args=(question,))
        thread.daemon = True
        thread.start()
    
    def _test_api_thread(self, question: str):
        """Run API test in background thread"""
        start_time = time.time()
        
        try:
            # Create temporary file with question
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(question)
                temp_file_path = f.name
            
            try:
                # Get timeout setting
                timeout = int(self.timeout_var.get())
                
                # Send request to API
                with open(temp_file_path, 'rb') as f:
                    files = {'file': ('question.txt', f, 'text/plain')}
                    response = requests.post(
                        f"{self.url_var.get()}/api/",
                        files=files,
                        timeout=timeout
                    )
                
                duration = time.time() - start_time
                
                # Update UI in main thread
                self.root.after(0, self._handle_api_response, response, duration, question)
                
            finally:
                # Clean up temp file
                os.unlink(temp_file_path)
                
        except Exception as e:
            duration = time.time() - start_time
            self.root.after(0, self._handle_api_error, str(e), duration, question)
    
    def _handle_api_response(self, response, duration: float, question: str):
        """Handle API response in main thread"""
        try:
            self.progress.stop()
            self.test_button.config(state='normal')
            
            # Log request if enabled
            if self.log_requests_var.get():
                self.log_request(question, response.status_code, duration)
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    formatted_result = json.dumps(result, indent=2, ensure_ascii=False)
                    
                    self.response_text.delete(1.0, tk.END)
                    self.response_text.insert(1.0, f"✅ Success (Status: {response.status_code}) - Duration: {duration:.2f}s\n\n")
                    self.response_text.insert(tk.END, formatted_result)
                    
                    # Check for base64 images
                    result_str = str(result)
                    if "data:image/" in result_str:
                        image_count = result_str.count("data:image/")
                        self.response_text.insert(tk.END, f"\n\n📊 Response contains {image_count} base64-encoded image(s)")
                    
                    self.update_status(f"Request completed successfully in {duration:.2f}s")
                    
                except json.JSONDecodeError:
                    # Response is not JSON
                    self.response_text.delete(1.0, tk.END)
                    self.response_text.insert(1.0, f"✅ Success (Status: {response.status_code}) - Duration: {duration:.2f}s\n\n")
                    self.response_text.insert(tk.END, response.text)
                    self.update_status(f"Request completed (non-JSON response) in {duration:.2f}s")
                    
            else:
                self.response_text.delete(1.0, tk.END)
                self.response_text.insert(1.0, f"❌ Error (Status: {response.status_code}) - Duration: {duration:.2f}s\n\n")
                self.response_text.insert(tk.END, response.text)
                self.update_status(f"Request failed with status {response.status_code}")
                
        except Exception as e:
            self._handle_api_error(f"Response parsing error: {str(e)}", duration, "")
    
    def _handle_api_error(self, error_msg: str, duration: float, question: str):
        """Handle API error in main thread"""
        self.progress.stop()
        self.test_button.config(state='normal')
        
        # Log request if enabled
        if self.log_requests_var.get():
            self.log_request(question, "ERROR", duration, error_msg)
        
        self.response_text.delete(1.0, tk.END)
        self.response_text.insert(1.0, f"❌ Request Failed - Duration: {duration:.2f}s\n\n")
        self.response_text.insert(tk.END, f"Error: {error_msg}")
        
        self.update_status(f"Request failed: {error_msg}")
        messagebox.showerror("API Error", f"Request failed: {error_msg}")
    
    def log_request(self, question: str, status, duration: float, error: str = ""):
        """Log a request to history"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        request_data = {
            'timestamp': timestamp,
            'question': question[:100] + "..." if len(question) > 100 else question,
            'status': status,
            'duration': duration,
            'error': error
        }
        
        self.request_history.append(request_data)
        
        # Add to tree view
        status_text = f"{status}" if status != "ERROR" else f"ERROR"
        self.history_tree.insert('', 0, values=(timestamp, status_text, f"{duration:.2f}"))
    
    def clear_history(self):
        """Clear request history"""
        self.request_history.clear()
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        self.update_status("Request history cleared")
    
    def export_history(self):
        """Export request history to JSON file"""
        if not self.request_history:
            messagebox.showwarning("Warning", "No history to export.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export history as",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.request_history, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Success", "History exported successfully!")
                self.update_status(f"History exported to {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not export history: {str(e)}")
                self.update_status("Failed to export history")
    
    def view_history_details(self, event):
        """View details of selected history item"""
        selection = self.history_tree.selection()
        if selection:
            item_index = len(self.history_tree.get_children()) - 1 - self.history_tree.index(selection[0])
            if 0 <= item_index < len(self.request_history):
                request_data = self.request_history[item_index]
                
                # Create details window
                details_window = tk.Toplevel(self.root)
                details_window.title("Request Details")
                details_window.geometry("600x400")
                
                details_text = scrolledtext.ScrolledText(details_window, wrap=tk.WORD)
                details_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                details_content = f"""Request Details:

Timestamp: {request_data['timestamp']}
Status: {request_data['status']}
Duration: {request_data['duration']:.2f} seconds

Question:
{request_data['question']}

"""
                if request_data['error']:
                    details_content += f"\nError Details:\n{request_data['error']}"
                
                details_text.insert(1.0, details_content)
                details_text.config(state=tk.DISABLED)
    
    def update_status(self, message: str):
        """Update status bar message"""
        self.status_var.set(message)
        self.root.update_idletasks()

def main():
    root = tk.Tk()
    app = EndpointTester(root)
    root.mainloop()

if __name__ == "__main__":
    main()