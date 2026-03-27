import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import struct
import binascii
import threading
from pathlib import Path
import json
from datetime import datetime
import re
import hashlib

class ForensicFileAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Forensic File Analyzer & Recovery Tool")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TNotebook.Tab', font=('Arial', 10, 'bold'))
        self.style.configure('Title.TLabel', font=('Arial', 14, 'bold'))
        self.style.configure('Subtitle.TLabel', font=('Arial', 12, 'bold'))
        self.style.configure('Success.TLabel', foreground='green')
        self.style.configure('Error.TLabel', foreground='red')
        self.style.configure('Action.TButton', font=('Arial', 9, 'bold'))
        
        # Create main notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_file_analysis_tab()
        self.create_hex_processing_tab()
        self.create_hex_text_analysis_tab()
        self.create_data_recovery_tab()
        self.create_results_tab()
        
        # Initialize data storage
        self.file_signatures = self.load_file_signatures()
        self.analysis_results = {}
        self.detected_files_from_hex = []
        
    def create_file_analysis_tab(self):
        """Create the file analysis tab"""
        self.analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_frame, text="File Analysis")
        
        # Title
        title_label = ttk.Label(self.analysis_frame, text="File Header, Trailer & Block Analysis", 
                               style='Title.TLabel')
        title_label.pack(pady=10)
        
        # File selection
        file_frame = ttk.LabelFrame(self.analysis_frame, text="File Selection", padding=10)
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.file_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path, width=80).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_file).pack(side=tk.LEFT, padx=5)
        
        # Analysis options
        options_frame = ttk.LabelFrame(self.analysis_frame, text="Analysis Options", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.header_size = tk.IntVar(value=512)
        self.trailer_size = tk.IntVar(value=512)
        self.block_size = tk.IntVar(value=4096)
        
        ttk.Label(options_frame, text="Header Size (bytes):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(options_frame, textvariable=self.header_size, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(options_frame, text="Trailer Size (bytes):").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(options_frame, textvariable=self.trailer_size, width=10).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(options_frame, text="Block Size (bytes):").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(options_frame, textvariable=self.block_size, width=10).grid(row=0, column=5, padx=5, pady=5)
        
        # Analysis button
        ttk.Button(self.analysis_frame, text="Analyze File", 
                  command=self.analyze_file).pack(pady=10)
        
        # Results display
        results_frame = ttk.LabelFrame(self.analysis_frame, text="Analysis Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create notebook for different result views
        results_notebook = ttk.Notebook(results_frame)
        results_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Header view
        header_frame = ttk.Frame(results_notebook)
        results_notebook.add(header_frame, text="Header")
        self.header_text = scrolledtext.ScrolledText(header_frame, height=10, width=100)
        self.header_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Trailer view
        trailer_frame = ttk.Frame(results_notebook)
        results_notebook.add(trailer_frame, text="Trailer")
        self.trailer_text = scrolledtext.ScrolledText(trailer_frame, height=10, width=100)
        self.trailer_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Block view
        block_frame = ttk.Frame(results_notebook)
        results_notebook.add(block_frame, text="Blocks")
        self.block_text = scrolledtext.ScrolledText(block_frame, height=10, width=100)
        self.block_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # File info view
        info_frame = ttk.Frame(results_notebook)
        results_notebook.add(info_frame, text="File Information")
        self.info_text = scrolledtext.ScrolledText(info_frame, height=10, width=100)
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def create_hex_processing_tab(self):
        """Create the hex processing tab"""
        self.hex_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.hex_frame, text="Hex Processing")
        
        # Title
        title_label = ttk.Label(self.hex_frame, text="Hex File Processing & File Reconstruction", 
                               style='Title.TLabel')
        title_label.pack(pady=10)
        
        # Hex file selection
        hex_file_frame = ttk.LabelFrame(self.hex_frame, text="Hex File Selection", padding=10)
        hex_file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.hex_file_path = tk.StringVar()
        ttk.Entry(hex_file_frame, textvariable=self.hex_file_path, width=80).pack(side=tk.LEFT, padx=5)
        ttk.Button(hex_file_frame, text="Browse", command=self.browse_hex_file).pack(side=tk.LEFT, padx=5)
        
        # Output directory
        output_frame = ttk.LabelFrame(self.hex_frame, text="Output Directory", padding=10)
        output_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.output_dir = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_dir, width=80).pack(side=tk.LEFT, padx=5)
        ttk.Button(output_frame, text="Browse", command=self.browse_output_dir).pack(side=tk.LEFT, padx=5)
        
        # Processing options
        options_frame = ttk.LabelFrame(self.hex_frame, text="Processing Options", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.detect_file_types = tk.BooleanVar(value=True)
        self.reconstruct_files = tk.BooleanVar(value=True)
        self.save_hex_files = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="Detect File Types", 
                       variable=self.detect_file_types).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Reconstruct Files", 
                       variable=self.reconstruct_files).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Save Hex Files", 
                       variable=self.save_hex_files).grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        
        # Process button
        ttk.Button(self.hex_frame, text="Process Hex File", 
                  command=self.process_hex_file).pack(pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.hex_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=10, pady=5)
        
        # Log display
        log_frame = ttk.LabelFrame(self.hex_frame, text="Processing Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=100)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def create_hex_text_analysis_tab(self):
        """Create a new tab for analyzing text files containing hex data"""
        self.hex_text_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.hex_text_frame, text="Hex Text Analysis")
        
        # Title
        title_label = ttk.Label(self.hex_text_frame, text="Hex Text File Analysis & File Reconstruction", 
                               style='Title.TLabel')
        title_label.pack(pady=10)
        
        # Hex text file selection
        hex_text_file_frame = ttk.LabelFrame(self.hex_text_frame, text="Hex Text File Selection", padding=10)
        hex_text_file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.hex_text_file_path = tk.StringVar()
        ttk.Entry(hex_text_file_frame, textvariable=self.hex_text_file_path, width=80).pack(side=tk.LEFT, padx=5)
        ttk.Button(hex_text_file_frame, text="Browse", command=self.browse_hex_text_file).pack(side=tk.LEFT, padx=5)
        
        # Output directory
        output_frame = ttk.LabelFrame(self.hex_text_frame, text="Output Directory", padding=10)
        output_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.hex_text_output_dir = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.hex_text_output_dir, width=80).pack(side=tk.LEFT, padx=5)
        ttk.Button(output_frame, text="Browse", command=self.browse_hex_text_output_dir).pack(side=tk.LEFT, padx=5)
        
        # Analysis options
        options_frame = ttk.LabelFrame(self.hex_text_frame, text="Analysis Options", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.auto_detect_files = tk.BooleanVar(value=True)
        self.rebuild_files = tk.BooleanVar(value=True)
        self.extract_all_headers = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="Auto Detect Files", 
                       variable=self.auto_detect_files).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Rebuild Detected Files", 
                       variable=self.rebuild_files).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Extract All Headers", 
                       variable=self.extract_all_headers).grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        
        # Process button
        ttk.Button(self.hex_text_frame, text="Analyze Hex Text File", 
                  command=self.analyze_hex_text_file).pack(pady=10)
        
        # Progress bar
        self.hex_text_progress = ttk.Progressbar(self.hex_text_frame, mode='indeterminate')
        self.hex_text_progress.pack(fill=tk.X, padx=10, pady=5)
        
        # Create notebook for results
        hex_text_results_notebook = ttk.Notebook(self.hex_text_frame)
        hex_text_results_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Detected files table
        detected_files_frame = ttk.Frame(hex_text_results_notebook)
        hex_text_results_notebook.add(detected_files_frame, text="Detected Files Table")
        
        # Create treeview for detected files
        columns = ('index', 'file_type', 'header_hex', 'trailer_hex', 'block_sample', 'size', 'offset', 'action')
        self.detected_files_tree = ttk.Treeview(detected_files_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        self.detected_files_tree.heading('index', text='#')
        self.detected_files_tree.heading('file_type', text='File Type')
        self.detected_files_tree.heading('header_hex', text='Header (First 16 bytes)')
        self.detected_files_tree.heading('trailer_hex', text='Trailer (Last 16 bytes)')
        self.detected_files_tree.heading('block_sample', text='Block Sample')
        self.detected_files_tree.heading('size', text='Size')
        self.detected_files_tree.heading('offset', text='Offset')
        self.detected_files_tree.heading('action', text='Action')
        
        # Define columns
        self.detected_files_tree.column('index', width=50, anchor=tk.CENTER)
        self.detected_files_tree.column('file_type', width=120, anchor=tk.CENTER)
        self.detected_files_tree.column('header_hex', width=200)
        self.detected_files_tree.column('trailer_hex', width=200)
        self.detected_files_tree.column('block_sample', width=150)
        self.detected_files_tree.column('size', width=100, anchor=tk.CENTER)
        self.detected_files_tree.column('offset', width=100, anchor=tk.CENTER)
        self.detected_files_tree.column('action', width=120, anchor=tk.CENTER)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(detected_files_frame, orient=tk.VERTICAL, command=self.detected_files_tree.yview)
        h_scrollbar = ttk.Scrollbar(detected_files_frame, orient=tk.HORIZONTAL, command=self.detected_files_tree.xview)
        self.detected_files_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.detected_files_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind selection event
        self.detected_files_tree.bind('<<TreeviewSelect>>', self.on_detected_file_select)
        self.detected_files_tree.bind('<Button-1>', self.on_treeview_click)
        
        # File details frame
        details_frame = ttk.Frame(hex_text_results_notebook)
        hex_text_results_notebook.add(details_frame, text="File Details")
        
        # Create notebook for file details
        file_details_notebook = ttk.Notebook(details_frame)
        file_details_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Header details
        header_details_frame = ttk.Frame(file_details_notebook)
        file_details_notebook.add(header_details_frame, text="Header")
        self.header_details_text = scrolledtext.ScrolledText(header_details_frame, height=10, width=100)
        self.header_details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Trailer details
        trailer_details_frame = ttk.Frame(file_details_notebook)
        file_details_notebook.add(trailer_details_frame, text="Trailer")
        self.trailer_details_text = scrolledtext.ScrolledText(trailer_details_frame, height=10, width=100)
        self.trailer_details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Blocks details
        blocks_details_frame = ttk.Frame(file_details_notebook)
        file_details_notebook.add(blocks_details_frame, text="Blocks")
        self.blocks_details_text = scrolledtext.ScrolledText(blocks_details_frame, height=10, width=100)
        self.blocks_details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Hex view
        hex_view_frame = ttk.Frame(file_details_notebook)
        file_details_notebook.add(hex_view_frame, text="Hex View")
        self.hex_view_text = scrolledtext.ScrolledText(hex_view_frame, height=10, width=100)
        self.hex_view_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # File info view
        file_info_frame = ttk.Frame(file_details_notebook)
        file_details_notebook.add(file_info_frame, text="File Information")
        self.file_info_text = scrolledtext.ScrolledText(file_info_frame, height=10, width=100)
        self.file_info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Action buttons frame
        action_frame = ttk.Frame(self.hex_text_frame)
        action_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(action_frame, text="Rebuild All Files", 
                  command=self.rebuild_all_files, style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Export File Table", 
                  command=self.export_file_table, style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Clear Results", 
                  command=self.clear_hex_text_results, style='Action.TButton').pack(side=tk.LEFT, padx=5)
        
        # Log display
        log_frame = ttk.LabelFrame(self.hex_text_frame, text="Analysis Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.hex_text_log = scrolledtext.ScrolledText(log_frame, height=10, width=100)
        self.hex_text_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def create_data_recovery_tab(self):
        """Create the data recovery tab"""
        self.recovery_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.recovery_frame, text="Data Recovery")
        
        # Title
        title_label = ttk.Label(self.recovery_frame, text="Flash Drive Data Recovery", 
                               style='Title.TLabel')
        title_label.pack(pady=10)
        
        # Drive selection
        drive_frame = ttk.LabelFrame(self.recovery_frame, text="Drive Selection", padding=10)
        drive_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.drive_path = tk.StringVar()
        ttk.Entry(drive_frame, textvariable=self.drive_path, width=80).pack(side=tk.LEFT, padx=5)
        ttk.Button(drive_frame, text="Browse", command=self.browse_drive).pack(side=tk.LEFT, padx=5)
        
        # Recovery options
        options_frame = ttk.LabelFrame(self.recovery_frame, text="Recovery Options", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.recover_deleted = tk.BooleanVar(value=True)
        self.recover_fragmented = tk.BooleanVar(value=True)
        self.deep_scan = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(options_frame, text="Recover Deleted Files", 
                       variable=self.recover_deleted).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Recover Fragmented Files", 
                       variable=self.recover_fragmented).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Deep Scan (Slower)", 
                       variable=self.deep_scan).grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        
        # Recovery button
        ttk.Button(self.recovery_frame, text="Start Recovery", 
                  command=self.start_recovery).pack(pady=10)
        
        # Recovery progress
        recovery_progress_frame = ttk.LabelFrame(self.recovery_frame, text="Recovery Progress", padding=10)
        recovery_progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.recovery_progress = ttk.Progressbar(recovery_progress_frame, mode='determinate')
        self.recovery_progress.pack(fill=tk.X, padx=5, pady=5)
        
        self.recovery_status = ttk.Label(recovery_progress_frame, text="Ready")
        self.recovery_status.pack(pady=5)
        
        # Recovery log
        recovery_log_frame = ttk.LabelFrame(self.recovery_frame, text="Recovery Log", padding=10)
        recovery_log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.recovery_log = scrolledtext.ScrolledText(recovery_log_frame, height=15, width=100)
        self.recovery_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def create_results_tab(self):
        """Create the results display tab"""
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="Results")
        
        # Title
        title_label = ttk.Label(self.results_frame, text="Analysis & Recovery Results", 
                               style='Title.TLabel')
        title_label.pack(pady=10)
        
        # Results table
        table_frame = ttk.LabelFrame(self.results_frame, text="Detected Files", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create treeview with scrollbars
        columns = ('filename', 'filetype', 'size', 'status', 'location')
        self.results_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        # Define headings
        self.results_tree.heading('filename', text='Filename')
        self.results_tree.heading('filetype', text='File Type')
        self.results_tree.heading('size', text='Size')
        self.results_tree.heading('status', text='Status')
        self.results_tree.heading('location', text='Location')
        
        # Define columns
        self.results_tree.column('filename', width=200)
        self.results_tree.column('filetype', width=150)
        self.results_tree.column('size', width=100)
        self.results_tree.column('status', width=100)
        self.results_tree.column('location', width=300)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Export buttons
        button_frame = ttk.Frame(self.results_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Export Results", 
                  command=self.export_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Results", 
                  command=self.clear_results).pack(side=tk.LEFT, padx=5)
        
    def browse_file(self):
        """Browse for a file to analyze"""
        filename = filedialog.askopenfilename(
            title="Select File for Analysis",
            filetypes=[("All files", "*.*")]
        )
        if filename:
            self.file_path.set(filename)
            
    def browse_hex_file(self):
        """Browse for a hex file to process"""
        filename = filedialog.askopenfilename(
            title="Select Hex File",
            filetypes=[("Binary files", "*.bin"), ("All files", "*.*")]
        )
        if filename:
            self.hex_file_path.set(filename)
            
    def browse_hex_text_file(self):
        """Browse for a text file containing hex data"""
        filename = filedialog.askopenfilename(
            title="Select Hex Text File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.hex_text_file_path.set(filename)
            
    def browse_output_dir(self):
        """Browse for an output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir.set(directory)
            
    def browse_hex_text_output_dir(self):
        """Browse for an output directory for hex text analysis"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.hex_text_output_dir.set(directory)
            
    def browse_drive(self):
        """Browse for a drive or directory to recover data from"""
        directory = filedialog.askdirectory(title="Select Drive or Directory")
        if directory:
            self.drive_path.set(directory)
            
    def analyze_file(self):
        """Analyze the selected file"""
        if not self.file_path.get():
            messagebox.showerror("Error", "Please select a file to analyze")
            return
            
        try:
            file_path = self.file_path.get()
            header_size = self.header_size.get()
            trailer_size = self.trailer_size.get()
            block_size = self.block_size.get()
            
            # Read file
            with open(file_path, 'rb') as f:
                file_data = f.read()
                
            # Extract header
            header = file_data[:header_size] if len(file_data) >= header_size else file_data
            header_hex = binascii.hexlify(header).decode('ascii')
            header_hex_formatted = ' '.join(header_hex[i:i+2] for i in range(0, len(header_hex), 2))
            
            # Extract trailer
            trailer = file_data[-trailer_size:] if len(file_data) >= trailer_size else file_data
            trailer_hex = binascii.hexlify(trailer).decode('ascii')
            trailer_hex_formatted = ' '.join(trailer_hex[i:i+2] for i in range(0, len(trailer_hex), 2))
            
            # Extract blocks
            blocks = []
            for i in range(0, len(file_data), block_size):
                block = file_data[i:i+block_size]
                block_hex = binascii.hexlify(block).decode('ascii')
                block_hex_formatted = ' '.join(block_hex[i:i+2] for i in range(0, len(block_hex), 2))
                blocks.append(f"Block {i//block_size + 1} (Offset: {i}):\n{block_hex_formatted}\n")
            
            # Get file information
            file_info = self.get_file_info(file_path, file_data)
            
            # Display results
            self.header_text.delete(1.0, tk.END)
            self.header_text.insert(tk.END, header_hex_formatted)
            
            self.trailer_text.delete(1.0, tk.END)
            self.trailer_text.insert(tk.END, trailer_hex_formatted)
            
            self.block_text.delete(1.0, tk.END)
            self.block_text.insert(tk.END, '\n'.join(blocks))
            
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, file_info)
            
            # Add to results table
            file_type = self.identify_file_type(header)
            file_size = os.path.getsize(file_path)
            self.results_tree.insert('', tk.END, values=(
                os.path.basename(file_path),
                file_type,
                f"{file_size} bytes",
                "Analyzed",
                file_path
            ))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze file: {str(e)}")
            
    def process_hex_file(self):
        """Process the hex file to extract and reconstruct files"""
        if not self.hex_file_path.get():
            messagebox.showerror("Error", "Please select a hex file")
            return
            
        if not self.output_dir.get():
            messagebox.showerror("Error", "Please select an output directory")
            return
            
        # Start processing in a separate thread
        threading.Thread(target=self._process_hex_file_thread, daemon=True).start()
        
    def _process_hex_file_thread(self):
        """Thread for processing hex file"""
        try:
            self.progress.start()
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(tk.END, "Starting hex file processing...\n")
            
            hex_file_path = self.hex_file_path.get()
            output_dir = self.output_dir.get()
            
            # Read hex file
            with open(hex_file_path, 'rb') as f:
                hex_data = f.read()
                
            # Detect files in hex data
            detected_files = self.detect_files_in_data(hex_data)
            
            self.log_text.insert(tk.END, f"Detected {len(detected_files)} potential files\n")
            
            # Reconstruct files
            for i, (file_type, file_data, offset) in enumerate(detected_files):
                filename = f"recovered_file_{i+1}.{self.get_extension(file_type)}"
                file_path = os.path.join(output_dir, filename)
                
                # Save reconstructed file
                with open(file_path, 'wb') as f:
                    f.write(file_data)
                    
                # Save hex file if requested
                if self.save_hex_files.get():
                    hex_filename = f"recovered_file_{i+1}.hex"
                    hex_path = os.path.join(output_dir, hex_filename)
                    with open(hex_path, 'w') as f:
                        f.write(binascii.hexlify(file_data).decode('ascii'))
                
                # Add to results table
                self.root.after(0, self.add_to_results_table, 
                               filename, file_type, len(file_data), "Recovered", file_path)
                
                self.log_text.insert(tk.END, f"Recovered: {filename} ({file_type}, {len(file_data)} bytes)\n")
                
            self.log_text.insert(tk.END, "Processing completed successfully!\n")
            
        except Exception as e:
            self.log_text.insert(tk.END, f"Error during processing: {str(e)}\n")
        finally:
            self.progress.stop()
            
    def analyze_hex_text_file(self):
        """Analyze a text file containing hex data"""
        if not self.hex_text_file_path.get():
            messagebox.showerror("Error", "Please select a hex text file")
            return
            
        # Start analysis in a separate thread
        threading.Thread(target=self._analyze_hex_text_file_thread, daemon=True).start()
        
    def _analyze_hex_text_file_thread(self):
        """Thread for analyzing hex text file"""
        try:
            self.hex_text_progress.start()
            self.hex_text_log.delete(1.0, tk.END)
            self.hex_text_log.insert(tk.END, "Starting hex text file analysis...\n")
            
            hex_text_file_path = self.hex_text_file_path.get()
            output_dir = self.hex_text_output_dir.get()
            
            # Read hex text file
            with open(hex_text_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                hex_text = f.read()
                
            # Parse hex text to binary data
            binary_data = self.parse_hex_text(hex_text)
            
            self.hex_text_log.insert(tk.END, f"Parsed {len(binary_data)} bytes from hex text\n")
            
            # Detect files in the binary data
            self.detected_files_from_hex = self.detect_files_with_details(binary_data)
            
            self.hex_text_log.insert(tk.END, f"Detected {len(self.detected_files_from_hex)} files\n")
            
            # Clear the treeview
            for item in self.detected_files_tree.get_children():
                self.detected_files_tree.delete(item)
                
            # Populate the treeview with detected files
            for i, file_info in enumerate(self.detected_files_from_hex):
                file_type = file_info['file_type']
                
                # Format header (first 16 bytes)
                header_hex = binascii.hexlify(file_info['header'][:16]).decode('ascii')
                header_formatted = ' '.join(header_hex[j:j+2] for j in range(0, min(32, len(header_hex)), 2))
                
                # Format trailer (last 16 bytes)
                trailer_hex = binascii.hexlify(file_info['trailer'][-16:]).decode('ascii')
                trailer_formatted = ' '.join(trailer_hex[j:j+2] for j in range(0, min(32, len(trailer_hex)), 2))
                
                # Format block sample (first block)
                block_sample = file_info['data'][:16] if len(file_info['data']) >= 16 else file_info['data']
                block_hex = binascii.hexlify(block_sample).decode('ascii')
                block_formatted = ' '.join(block_hex[j:j+2] for j in range(0, min(32, len(block_hex)), 2))
                
                size = len(file_info['data'])
                offset = file_info['offset']
                
                # Insert into treeview with rebuild button text
                item_id = self.detected_files_tree.insert('', tk.END, values=(
                    i+1,
                    file_type,
                    header_formatted,
                    trailer_formatted,
                    block_formatted,
                    f"{size} bytes",
                    f"0x{offset:X}",
                    "Rebuild File"
                ))
                
            # Rebuild files if requested
            if self.rebuild_files.get() and output_dir:
                self.hex_text_log.insert(tk.END, "Rebuilding detected files...\n")
                self.rebuild_all_files()
                
            self.hex_text_log.insert(tk.END, "Analysis completed successfully!\n")
            
        except Exception as e:
            self.hex_text_log.insert(tk.END, f"Error during analysis: {str(e)}\n")
        finally:
            self.hex_text_progress.stop()
            
    def parse_hex_text(self, hex_text):
        """Parse hex text into binary data"""
        # Remove any non-hex characters and whitespace
        hex_chars = re.sub(r'[^0-9A-Fa-f]', '', hex_text)
        
        # Ensure even length
        if len(hex_chars) % 2 != 0:
            hex_chars = hex_chars[:-1]
            
        # Convert to binary
        try:
            binary_data = binascii.unhexlify(hex_chars)
            return binary_data
        except Exception as e:
            raise ValueError(f"Invalid hex data: {str(e)}")
            
    def detect_files_with_details(self, data):
        """Detect files in binary data with detailed information - FIXED VERSION"""
        detected_files = []
        i = 0
        
        while i < len(data):
            found_file = False
            # Look for file signatures in order of signature length (longest first)
            for signature, file_type in sorted(self.file_signatures.items(), 
                                            key=lambda x: len(x[0]), reverse=True):
                if i + len(signature) <= len(data) and data[i:i+len(signature)] == signature:
                    # Found a potential file, try to extract it
                    file_data = self.extract_file_by_type(data, i, file_type)
                    if file_data and len(file_data) > 0:
                        # Calculate header (first 512 bytes or entire file if smaller)
                        header_size = min(512, len(file_data))
                        header = file_data[:header_size]
                        
                        # Calculate trailer (last 512 bytes or entire file if smaller)
                        trailer_size = min(512, len(file_data))
                        trailer = file_data[-trailer_size:] if len(file_data) > trailer_size else file_data
                        
                        detected_files.append({
                            'file_type': file_type,
                            'data': file_data,
                            'offset': i,
                            'header': header,
                            'trailer': trailer,
                            'size': len(file_data)
                        })
                        
                        # Move to the end of this file
                        i += len(file_data)
                        found_file = True
                        self.hex_text_log.insert(tk.END, 
                            f"Found {file_type} at offset 0x{i:X}, size: {len(file_data)} bytes\n")
                        break
            
            if not found_file:
                i += 1  # Move forward one byte if no file signature found
                
            # Prevent infinite loop
            if i >= len(data):
                break
                
        return detected_files
        
    def extract_file_by_type(self, data, offset, file_type):
        """Extract file data based on file type with proper boundaries"""
        max_size = 50 * 1024 * 1024  # 50MB maximum file size
        
        if file_type == 'JPEG':
            # JPEG ends with FF D9
            end_marker = b'\xff\xd9'
            end_pos = data.find(end_marker, offset + 2)
            if end_pos != -1:
                return data[offset:end_pos + 2]
        
        elif file_type == 'PNG':
            # PNG ends with IEND chunk
            iend_marker = b'IEND\xae\x42\x60\x82'
            end_pos = data.find(iend_marker, offset + 8)
            if end_pos != -1:
                return data[offset:end_pos + 8]
        
        elif file_type == 'PDF':
            # PDF ends with %%EOF
            eof_marker = b'%%EOF'
            end_pos = data.find(eof_marker, offset + 5)
            if end_pos != -1:
                # Include some trailing data after EOF
                return data[offset:min(end_pos + 20, offset + max_size)]
        
        elif file_type == 'ZIP':
            # ZIP has end of central directory record
            eocd_marker = b'PK\x05\x06'
            end_pos = data.find(eocd_marker, offset + 4)
            if end_pos != -1:
                # End of central directory is 22 bytes
                return data[offset:end_pos + 22]
        
        elif file_type == 'GIF':
            # GIF ends with 3B
            end_marker = b';'
            end_pos = data.find(end_marker, offset + 6)
            if end_pos != -1:
                return data[offset:end_pos + 1]
        
        elif file_type == 'BMP':
            # BMP has file size in header
            if offset + 14 <= len(data):
                # Read file size from BMP header (bytes 2-5)
                try:
                    file_size = struct.unpack('<I', data[offset+2:offset+6])[0]
                    if file_size > 0 and file_size <= max_size:
                        return data[offset:offset+file_size]
                except:
                    pass
        
        # Default: extract until next file signature or max_size
        next_file_offset = len(data)
        for signature in self.file_signatures.keys():
            pos = data.find(signature, offset + 1)
            if pos != -1 and pos < next_file_offset:
                next_file_offset = pos
                
        end_pos = min(offset + max_size, next_file_offset)
        return data[offset:end_pos]
        
    def on_treeview_click(self, event):
        """Handle click events on the treeview for rebuild buttons"""
        item = self.detected_files_tree.identify_row(event.y)
        column = self.detected_files_tree.identify_column(event.x)
        
        if item and column == '#8':  # Action column
            index = int(self.detected_files_tree.item(item, 'values')[0]) - 1
            self.rebuild_single_file(index)
            
    def on_detected_file_select(self, event):
        """Handle selection of a detected file in the treeview"""
        selection = self.detected_files_tree.selection()
        if not selection:
            return
            
        # Get the selected item
        item = selection[0]
        index = int(self.detected_files_tree.item(item, 'values')[0]) - 1
        
        if index < 0 or index >= len(self.detected_files_from_hex):
            return
            
        file_info = self.detected_files_from_hex[index]
        
        # Display header details
        header_hex = binascii.hexlify(file_info['header']).decode('ascii')
        header_hex_formatted = self.format_hex_display(header_hex, 16)
        self.header_details_text.delete(1.0, tk.END)
        self.header_details_text.insert(tk.END, header_hex_formatted)
        
        # Display trailer details
        trailer_hex = binascii.hexlify(file_info['trailer']).decode('ascii')
        trailer_hex_formatted = self.format_hex_display(trailer_hex, 16)
        self.trailer_details_text.delete(1.0, tk.END)
        self.trailer_details_text.insert(tk.END, trailer_hex_formatted)
        
        # Display blocks
        block_size = 512
        blocks_text = ""
        num_blocks = min(10, len(file_info['data']) // block_size + 1)
        
        for block_num in range(num_blocks):
            start = block_num * block_size
            end = min(start + block_size, len(file_info['data']))
            block_data = file_info['data'][start:end]
            block_hex = binascii.hexlify(block_data).decode('ascii')
            block_formatted = self.format_hex_display(block_hex, 16)
            blocks_text += f"Block {block_num + 1} (Offset: {start}-{end}):\n{block_formatted}\n\n"
            
        self.blocks_details_text.delete(1.0, tk.END)
        self.blocks_details_text.insert(tk.END, blocks_text)
        
        # Display hex view (first 2KB)
        preview_size = min(2048, len(file_info['data']))
        preview_data = file_info['data'][:preview_size]
        full_hex = binascii.hexlify(preview_data).decode('ascii')
        full_hex_formatted = self.format_hex_display(full_hex, 32)
        self.hex_view_text.delete(1.0, tk.END)
        self.hex_view_text.insert(tk.END, full_hex_formatted)
        
        # Display file information
        file_info_text = f"File Type: {file_info['file_type']}\n"
        file_info_text += f"File Size: {file_info['size']} bytes\n"
        file_info_text += f"Offset in Hex: 0x{file_info['offset']:X}\n"
        file_info_text += f"Offset in Decimal: {file_info['offset']}\n"
        file_info_text += f"Header Size: {len(file_info['header'])} bytes\n"
        file_info_text += f"Trailer Size: {len(file_info['trailer'])} bytes\n"
        file_info_text += f"MD5 Hash: {hashlib.md5(file_info['data']).hexdigest()}\n"
        file_info_text += f"SHA-1 Hash: {hashlib.sha1(file_info['data']).hexdigest()}\n"
        file_info_text += f"File Extension: {self.get_extension(file_info['file_type'])}\n"
        file_info_text += f"Estimated File End: 0x{file_info['offset'] + file_info['size']:X}\n"
        
        self.file_info_text.delete(1.0, tk.END)
        self.file_info_text.insert(tk.END, file_info_text)
        
    def format_hex_display(self, hex_string, bytes_per_line):
        """Format hex string for display with specified bytes per line"""
        lines = []
        for i in range(0, len(hex_string), bytes_per_line * 2):
            line_hex = hex_string[i:i + bytes_per_line * 2]
            formatted_line = ' '.join([line_hex[j:j+2] for j in range(0, len(line_hex), 2)])
            lines.append(formatted_line)
        return '\n'.join(lines)
        
    def rebuild_all_files(self):
        """Rebuild all detected files from hex analysis"""
        if not self.hex_text_output_dir.get():
            messagebox.showerror("Error", "Please select an output directory first")
            return
            
        output_dir = self.hex_text_output_dir.get()
        
        # Start rebuilding in a separate thread
        threading.Thread(target=self._rebuild_all_files_thread, args=(output_dir,), daemon=True).start()
        
    def _rebuild_all_files_thread(self, output_dir):
        """Thread for rebuilding all files"""
        try:
            self.hex_text_log.insert(tk.END, "Starting to rebuild all files...\n")
            
            for i, file_info in enumerate(self.detected_files_from_hex):
                file_type = file_info['file_type']
                file_data = file_info['data']
                
                # Create directory for file type
                type_dir = os.path.join(output_dir, file_type)
                os.makedirs(type_dir, exist_ok=True)
                
                # Save the file
                filename = f"recovered_{i+1}_{file_info['offset']:x}.{self.get_extension(file_type)}"
                file_path = os.path.join(type_dir, filename)
                
                with open(file_path, 'wb') as f:
                    f.write(file_data)
                    
                # Also save hex version
                hex_filename = f"recovered_{i+1}_{file_info['offset']:x}.hex"
                hex_path = os.path.join(type_dir, hex_filename)
                
                with open(hex_path, 'w') as f:
                    f.write(binascii.hexlify(file_data).decode('ascii'))
                    
                # Add to results table
                self.root.after(0, self.add_to_results_table, 
                               filename, file_type, len(file_data), "Rebuilt", file_path)
                
                self.hex_text_log.insert(tk.END, 
                    f"Rebuilt: {filename} ({file_type}, {len(file_data)} bytes, offset: 0x{file_info['offset']:X})\n")
                
            self.hex_text_log.insert(tk.END, f"All {len(self.detected_files_from_hex)} files rebuilt successfully!\n")
            
        except Exception as e:
            self.hex_text_log.insert(tk.END, f"Error during file rebuilding: {str(e)}\n")
            
    def rebuild_single_file(self, index):
        """Rebuild a single file by index"""
        if not self.hex_text_output_dir.get():
            messagebox.showerror("Error", "Please select an output directory first")
            return
            
        if index < 0 or index >= len(self.detected_files_from_hex):
            return
            
        file_info = self.detected_files_from_hex[index]
        file_type = file_info['file_type']
        file_data = file_info['data']
        output_dir = self.hex_text_output_dir.get()
        
        # Create directory for file type
        type_dir = os.path.join(output_dir, file_type)
        os.makedirs(type_dir, exist_ok=True)
        
        # Save the file
        filename = f"recovered_{index+1}_{file_info['offset']:x}.{self.get_extension(file_type)}"
        file_path = os.path.join(type_dir, filename)
        
        try:
            with open(file_path, 'wb') as f:
                f.write(file_data)
                
            # Also save hex version
            hex_filename = f"recovered_{index+1}_{file_info['offset']:x}.hex"
            hex_path = os.path.join(type_dir, hex_filename)
            
            with open(hex_path, 'w') as f:
                f.write(binascii.hexlify(file_data).decode('ascii'))
                
            # Add to results table
            self.add_to_results_table(filename, file_type, len(file_data), "Rebuilt", file_path)
            
            self.hex_text_log.insert(tk.END, 
                f"Rebuilt single file: {filename} ({file_type}, {len(file_data)} bytes, offset: 0x{file_info['offset']:X})\n")
            messagebox.showinfo("Success", f"File {filename} rebuilt successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to rebuild file: {str(e)}")
            
    def export_file_table(self):
        """Export the file table to CSV"""
        if not self.detected_files_from_hex:
            messagebox.showwarning("Warning", "No files to export")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Export File Table",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    # Write header
                    f.write("Index,File Type,Header Hex,Trailer Hex,Block Sample,Size,Offset\n")
                    
                    # Write data
                    for i, file_info in enumerate(self.detected_files_from_hex):
                        file_type = file_info['file_type']
                        
                        # Format header (first 16 bytes)
                        header_hex = binascii.hexlify(file_info['header'][:16]).decode('ascii')
                        header_formatted = ' '.join(header_hex[j:j+2] for j in range(0, min(32, len(header_hex)), 2))
                        
                        # Format trailer (last 16 bytes)
                        trailer_hex = binascii.hexlify(file_info['trailer'][-16:]).decode('ascii')
                        trailer_formatted = ' '.join(trailer_hex[j:j+2] for j in range(0, min(32, len(trailer_hex)), 2))
                        
                        # Format block sample (first block)
                        block_sample = file_info['data'][:16] if len(file_info['data']) >= 16 else file_info['data']
                        block_hex = binascii.hexlify(block_sample).decode('ascii')
                        block_formatted = ' '.join(block_hex[j:j+2] for j in range(0, min(32, len(block_hex)), 2))
                        
                        size = len(file_info['data'])
                        offset = file_info['offset']
                        
                        f.write(f'{i+1},"{file_type}","{header_formatted}","{trailer_formatted}","{block_formatted}",{size},0x{offset:X}\n')
                        
                messagebox.showinfo("Success", f"File table exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export file table: {str(e)}")
                
    def clear_hex_text_results(self):
        """Clear hex text analysis results"""
        for item in self.detected_files_tree.get_children():
            self.detected_files_tree.delete(item)
            
        self.header_details_text.delete(1.0, tk.END)
        self.trailer_details_text.delete(1.0, tk.END)
        self.blocks_details_text.delete(1.0, tk.END)
        self.hex_view_text.delete(1.0, tk.END)
        self.file_info_text.delete(1.0, tk.END)
        self.hex_text_log.delete(1.0, tk.END)
        
        self.detected_files_from_hex = []
        
    def start_recovery(self):
        """Start data recovery from the selected drive"""
        if not self.drive_path.get():
            messagebox.showerror("Error", "Please select a drive or directory")
            return
            
        # Start recovery in a separate thread
        threading.Thread(target=self._recovery_thread, daemon=True).start()
        
    def _recovery_thread(self):
        """Thread for data recovery"""
        try:
            self.recovery_progress['value'] = 0
            self.recovery_status['text'] = "Starting recovery..."
            self.recovery_log.delete(1.0, tk.END)
            self.recovery_log.insert(tk.END, "Starting data recovery...\n")
            
            drive_path = self.drive_path.get()
            
            # Simulate recovery process
            recovered_files = self.scan_for_deleted_files(drive_path)
            
            self.recovery_log.insert(tk.END, f"Found {len(recovered_files)} recoverable files\n")
            
            # Update progress
            for i, (filename, file_type, file_data, status) in enumerate(recovered_files):
                progress = (i + 1) / len(recovered_files) * 100
                self.recovery_progress['value'] = progress
                self.recovery_status['text'] = f"Recovering {filename}..."
                
                # Save recovered file
                output_dir = os.path.join(drive_path, "recovered_files")
                os.makedirs(output_dir, exist_ok=True)
                
                file_path = os.path.join(output_dir, filename)
                with open(file_path, 'wb') as f:
                    f.write(file_data)
                    
                # Add to results table
                self.root.after(0, self.add_to_results_table, 
                               filename, file_type, len(file_data), status, file_path)
                
                self.recovery_log.insert(tk.END, f"Recovered: {filename} ({file_type}, {len(file_data)} bytes)\n")
                
            self.recovery_status['text'] = "Recovery completed!"
            self.recovery_log.insert(tk.END, "Recovery completed successfully!\n")
            
        except Exception as e:
            self.recovery_log.insert(tk.END, f"Error during recovery: {str(e)}\n")
            self.recovery_status['text'] = "Recovery failed!"
            
    def add_to_results_table(self, filename, file_type, size, status, location):
        """Add an entry to the results table"""
        self.results_tree.insert('', tk.END, values=(
            filename, file_type, f"{size} bytes", status, location
        ))
        
    def export_results(self):
        """Export results to a file"""
        filename = filedialog.asksaveasfilename(
            title="Export Results",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                results = []
                for item in self.results_tree.get_children():
                    values = self.results_tree.item(item)['values']
                    results.append({
                        'filename': values[0],
                        'file_type': values[1],
                        'size': values[2],
                        'status': values[3],
                        'location': values[4]
                    })
                    
                with open(filename, 'w') as f:
                    json.dump(results, f, indent=2)
                    
                messagebox.showinfo("Success", f"Results exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export results: {str(e)}")
                
    def clear_results(self):
        """Clear the results table"""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
            
    def load_file_signatures(self):
        """Load file signatures for identification"""
        signatures = {
            b'\xff\xd8\xff': 'JPEG',
            b'\x89PNG\r\n\x1a\n': 'PNG',
            b'GIF8': 'GIF',
            b'%PDF': 'PDF',
            b'PK\x03\x04': 'ZIP',
            b'\x50\x4b\x03\x04': 'ZIP',
            b'\x50\x4b\x05\x06': 'ZIP',
            b'\x50\x4b\x07\x08': 'ZIP',
            b'RIFF': 'WAV/AVI',
            b'\x1a\x45\xdf\xa3': 'MKV',
            b'\x47\x49\x46\x38': 'GIF',
            b'\x42\x4d': 'BMP',
            b'\x49\x49\x2a\x00': 'TIFF',
            b'\x4d\x4d\x00\x2a': 'TIFF',
            b'\x25\x21': 'PS',
            b'\x7fELF': 'ELF',
            b'MZ': 'EXE/DLL',
            b'\x52\x61\x72\x21': 'RAR',
            b'\x37\x7a\xbc\xaf\x27\x1c': '7Z',
        }
        return signatures
        
    def identify_file_type(self, data):
        """Identify file type based on signature"""
        for signature, file_type in self.file_signatures.items():
            if data.startswith(signature):
                return file_type
        return "Unknown"
        
    def get_file_info(self, file_path, file_data):
        """Get detailed file information"""
        stat = os.stat(file_path)
        file_info = f"Filename: {os.path.basename(file_path)}\n"
        file_info += f"Full Path: {file_path}\n"
        file_info += f"Size: {len(file_data)} bytes\n"
        file_info += f"Created: {datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')}\n"
        file_info += f"Modified: {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}\n"
        file_info += f"Accessed: {datetime.fromtimestamp(stat.st_atime).strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        # File type identification
        file_type = self.identify_file_type(file_data[:20])
        file_info += f"File Type: {file_type}\n"
        
        # MD5 hash
        file_info += f"MD5: {hashlib.md5(file_data).hexdigest()}\n"
        
        return file_info
        
    def get_extension(self, file_type):
        """Get file extension from file type"""
        extensions = {
            'JPEG': 'jpg',
            'PNG': 'png',
            'GIF': 'gif',
            'PDF': 'pdf',
            'ZIP': 'zip',
            'WAV/AVI': 'wav',
            'MKV': 'mkv',
            'BMP': 'bmp',
            'TIFF': 'tiff',
            'PS': 'ps',
            'ELF': 'elf',
            'EXE/DLL': 'exe',
            'RAR': 'rar',
            '7Z': '7z'
        }
        return extensions.get(file_type, 'bin')
        
    def scan_for_deleted_files(self, drive_path):
        """Scan for deleted files (simulated)"""
        recovered_files = []
        
        # Simulate finding some files
        sample_files = [
            ("document.pdf", "PDF", b"%PDF-1.4\nSample PDF content...", "Recovered"),
            ("image.jpg", "JPEG", b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00", "Recovered"),
            ("archive.zip", "ZIP", b"PK\x03\x04\x14\x00\x00\x00\x08\x00\x00\x00\x00\x00Sample ZIP content", "Recovered"),
            ("video.mkv", "MKV", b"\x1a\x45\xdf\xa3\x01\x00\x00\x00\x00\x00\x00\x1f\x42\x86\x81\x01\x42\x85\x81\x01", "Fragmented"),
        ]
        
        return sample_files

def main():
    root = tk.Tk()
    app = ForensicFileAnalyzer(root)
    root.mainloop()

if __name__ == "__main__":
    main()