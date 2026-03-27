# import sys
# import os
# import tkinter as tk
# from tkinter import ttk, filedialog, messagebox, scrolledtext
# import threading
# from pathlib import Path
# import time
# import json
# from Hex_Bulding import MultiFileHexParser, display_file_boundaries, display_extracted_files

# # تعريف نظام الألوان
# BG_COLOR = "#ffffff"
# PRIMARY_COLOR = "#2c3e50"
# SECONDARY_COLOR = "#3498db"
# ACCENT_COLOR = "#e74c3c"
# SUCCESS_COLOR = "#2ecc71"
# WARNING_COLOR = "#f39c12"
# TEXT_COLOR = "#2c3e50"
# BORDER_COLOR = "#ecf0f1"

# class RedirectText:
#     def __init__(self, text_widget):
#         self.text_widget = text_widget

#     def write(self, string):
#         self.text_widget.config(state=tk.NORMAL)
#         self.text_widget.insert(tk.END, string)
#         self.text_widget.see(tk.END)
#         self.text_widget.config(state=tk.DISABLED)

#     def flush(self):
#         pass

# class HexExtractorGUI:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("أداة استخراج وبناء ملفات الهيكس")
#         self.root.geometry("1000x700")
#         self.root.config(bg=BG_COLOR)
        
#         self.parser = MultiFileHexParser()
#         self.setup_ui()
        
#         # إعداد رد اتصال التقدم
#         self.parser.set_progress_callback(self.update_progress_display)

#     def setup_ui(self):
#         # الإطار الرئيسي
#         main_frame = ttk.Frame(self.root, padding="10")
#         main_frame.pack(fill=tk.BOTH, expand=True)
        
#         # العنوان
#         title_frame = ttk.Frame(main_frame)
#         title_frame.pack(fill=tk.X, pady=(0, 10))
        
#         title_label = ttk.Label(
#             title_frame, 
#             text="أداة استخراج ملفات الهيكس المتعددة", 
#             font=("Arial", 16, "bold")
#         )
#         title_label.pack(pady=5)
        
#         subtitle_label = ttk.Label(
#             title_frame,
#             text="يدعم: JPG, PNG, EXE, DLL, TXT, PDF, BMP, MP3, MP4, MOV",
#             font=("Arial", 10)
#         )
#         subtitle_label.pack()
        
#         # عنصر تحكم علامات التبويب
#         self.tab_control = ttk.Notebook(main_frame)
#         self.tab_control.pack(fill=tk.BOTH, expand=True)
        
#         # علامة التبويب 1: الإدخال
#         input_tab = ttk.Frame(self.tab_control)
#         self.tab_control.add(input_tab, text="إدخال الهيكس")
#         self.setup_input_tab(input_tab)
        
#         # علامة التبويب 2: الملفات المستخرجة
#         files_tab = ttk.Frame(self.tab_control)
#         self.tab_control.add(files_tab, text="الملفات المستخرجة")
#         self.setup_files_tab(files_tab)
        
#         # علامة التبويب 3: الإخراج
#         output_tab = ttk.Frame(self.tab_control)
#         self.tab_control.add(output_tab, text="إعادة بناء الملفات")
#         self.setup_output_tab(output_tab)
        
#         # إطار إخراج وحدة التحكم
#         console_frame = ttk.LabelFrame(main_frame, text="إخراج وحدة التحكم", padding="5")
#         console_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
#         self.console = scrolledtext.ScrolledText(console_frame, height=12)
#         self.console.pack(fill=tk.BOTH, expand=True)
#         self.console.config(state=tk.DISABLED)
        
#         # توجيه stdout إلى وحدة التحكم
#         self.text_redirect = RedirectText(self.console)
#         sys.stdout = self.text_redirect
        
#         # شريط الحالة
#         status_frame = ttk.Frame(main_frame)
#         status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
#         self.status_var = tk.StringVar()
#         self.status_var.set("جاهز")
#         status_label = ttk.Label(status_frame, textvariable=self.status_var)
#         status_label.pack(side=tk.LEFT)
        
#         self.progress_var = tk.DoubleVar()
#         self.progress = ttk.Progressbar(status_frame, variable=self.progress_var, length=200)
#         self.progress.pack(side=tk.RIGHT, padx=10)
        
#     def setup_input_tab(self, parent):
#         # إطار طرق الإدخال
#         input_methods_frame = ttk.LabelFrame(parent, text="طرق الإدخال", padding="10")
#         input_methods_frame.pack(fill=tk.X, pady=10)
        
#         # الخيار 1: لصق الهيكس
#         paste_frame = ttk.Frame(input_methods_frame)
#         paste_frame.pack(fill=tk.BOTH, pady=5)
        
#         paste_label = ttk.Label(paste_frame, text="لصق بيانات الهيكس:")
#         paste_label.pack(anchor=tk.W)
        
#         self.hex_input = scrolledtext.ScrolledText(paste_frame, height=10, wrap=tk.WORD, font=("Consolas", 10))
#         self.hex_input.pack(fill=tk.BOTH, expand=True, pady=5)
        
#         # زر المعالجة
#         process_btn_frame = ttk.Frame(paste_frame)
#         process_btn_frame.pack(fill=tk.X, pady=5)
        
#         paste_btn = ttk.Button(
#             process_btn_frame, 
#             text="🔍 معالجة بيانات الهيكس", 
#             command=self.process_pasted_hex,
#             style="Accent.TButton"
#         )
#         paste_btn.pack(pady=5, fill=tk.X)
        
#         # الخيار 2: التحميل من ملف
#         file_frame = ttk.Frame(input_methods_frame)
#         file_frame.pack(fill=tk.X, pady=10)
        
#         file_label = ttk.Label(file_frame, text="أو التحميل من ملف:")
#         file_label.pack(anchor=tk.W)
        
#         # إدخال اختيار الملف وزر التصفح
#         file_select_frame = ttk.Frame(file_frame)
#         file_select_frame.pack(fill=tk.X, pady=5)
        
#         self.file_path_var = tk.StringVar()
#         file_entry = ttk.Entry(file_select_frame, textvariable=self.file_path_var, width=50)
#         file_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        
#         browse_btn = ttk.Button(
#             file_select_frame, 
#             text="📂 تصفح...", 
#             command=self.browse_file
#         )
#         browse_btn.pack(side=tk.LEFT)
        
#         # زر التحميل
#         file_buttons_frame = ttk.Frame(file_frame)
#         file_buttons_frame.pack(fill=tk.X, pady=5)
        
#         load_btn = ttk.Button(
#             file_buttons_frame, 
#             text="📥 تحميل ومعالجة الملف", 
#             command=self.load_from_file,
#             style="Accent.TButton"
#         )
#         load_btn.pack(side=tk.RIGHT, padx=5, fill=tk.X, expand=True)

#     def setup_files_tab(self, parent):
#         # إطار عرض الملفات
#         files_frame = ttk.Frame(parent, padding="10")
#         files_frame.pack(fill=tk.BOTH, expand=True)
        
#         # عرض الشجرة للملفات
#         columns = ('file_id', 'type', 'size', 'header', 'trailer')
#         self.files_tree = ttk.Treeview(files_frame, columns=columns, show='headings')
        
#         # تعريف العناوين
#         self.files_tree.heading('file_id', text='معرف الملف')
#         self.files_tree.heading('type', text='النوع')
#         self.files_tree.heading('size', text='الحجم (بايت)')
#         self.files_tree.heading('header', text='الهيدر')
#         self.files_tree.heading('trailer', text='الترايلر')
        
#         # تعريف عرض الأعمدة
#         self.files_tree.column('file_id', width=120)
#         self.files_tree.column('type', width=80)
#         self.files_tree.column('size', width=100)
#         self.files_tree.column('header', width=150)
#         self.files_tree.column('trailer', width=150)
        
#         # إضافة أشرطة التمرير
#         vsb = ttk.Scrollbar(files_frame, orient="vertical", command=self.files_tree.yview)
#         hsb = ttk.Scrollbar(files_frame, orient="horizontal", command=self.files_tree.xview)
#         self.files_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
#         self.files_tree.grid(column=0, row=0, sticky='nsew')
#         vsb.grid(column=1, row=0, sticky='ns')
#         hsb.grid(column=0, row=1, sticky='ew')
        
#         files_frame.grid_columnconfigure(0, weight=1)
#         files_frame.grid_rowconfigure(0, weight=1)
        
#         # إطار الأزرار
#         button_frame = ttk.Frame(parent, padding="10")
#         button_frame.pack(fill=tk.X)
        
#         refresh_btn = ttk.Button(button_frame, text="تحديث قائمة الملفات", command=self.refresh_files_list)
#         refresh_btn.pack(side=tk.LEFT, padx=5)
        
#         analyze_btn = ttk.Button(button_frame, text="تحليل الملف المحدد", command=self.analyze_selected_file)
#         analyze_btn.pack(side=tk.LEFT, padx=5)

#     def setup_output_tab(self, parent):
#         # إطار خيارات الإخراج
#         output_frame = ttk.LabelFrame(parent, text="خيارات الإخراج", padding="10")
#         output_frame.pack(fill=tk.X, pady=10)
        
#         # دليل الإخراج
#         dir_frame = ttk.Frame(output_frame)
#         dir_frame.pack(fill=tk.X, pady=5)
        
#         dir_label = ttk.Label(dir_frame, text="دليل الإخراج:")
#         dir_label.pack(anchor=tk.W)
        
#         dir_select_frame = ttk.Frame(dir_frame)
#         dir_select_frame.pack(fill=tk.X, pady=5)
        
#         self.output_dir_var = tk.StringVar(value="reconstructed_files")
#         dir_entry = ttk.Entry(dir_select_frame, textvariable=self.output_dir_var, width=50)
#         dir_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        
#         browse_dir_btn = ttk.Button(dir_select_frame, text="تصفح...", command=self.browse_directory)
#         browse_dir_btn.pack(side=tk.LEFT)
        
#         # أزرار الإجراء
#         action_frame = ttk.Frame(parent, padding="10")
#         action_frame.pack(fill=tk.X, pady=10)
        
#         rebuild_btn = ttk.Button(
#             action_frame, 
#             text="إعادة بناء جميع الملفات", 
#             command=self.rebuild_files,
#             style="Accent.TButton"
#         )
#         rebuild_btn.pack(side=tk.LEFT, padx=5)
        
#         save_hex_btn = ttk.Button(
#             action_frame, 
#             text="حفظ ملفات الهيكس", 
#             command=self.save_hex_files
#         )
#         save_hex_btn.pack(side=tk.LEFT, padx=5)
        
#         save_report_btn = ttk.Button(
#             action_frame, 
#             text="حفظ تقرير الاستخراج", 
#             command=self.save_report
#         )
#         save_report_btn.pack(side=tk.LEFT, padx=5)

#     def update_progress_display(self, message, percent=None):
#         """تحديث عرض التقدم من المحلل"""
#         def update():
#             self.console.config(state=tk.NORMAL)
#             self.console.insert(tk.END, message + "\n")
#             self.console.see(tk.END)
#             self.console.config(state=tk.DISABLED)
            
#             if percent is not None:
#                 self.progress_var.set(percent)
                
#             self.status_var.set(message[:50] + "..." if len(message) > 50 else message)
#             self.root.update_idletasks()
        
#         self.root.after(0, update)

#     def process_pasted_hex(self):
#         hex_data = self.hex_input.get("1.0", tk.END).strip()
#         if not hex_data:
#             messagebox.showerror("خطأ", "الرجاء إدخال بيانات الهيكس أولاً!")
#             return
            
#         self.process_hex_data(hex_data)
    
#     def load_from_file(self):
#         file_path = self.file_path_var.get()
        
#         if not file_path:
#             file_path = filedialog.askopenfilename(
#                 title="حدد ملف الهيكس",
#                 filetypes=(("ملفات النص", "*.txt"), ("ملفات الهيكس", "*.hex"), ("جميع الملفات", "*.*"))
#             )
#             if not file_path:
#                 return
#             self.file_path_var.set(file_path)
        
#         if not os.path.exists(file_path):
#             messagebox.showerror("خطأ", f"الملف غير موجود: {file_path}")
#             return
        
#         self.status_var.set(f"جاري تحميل الملف: {os.path.basename(file_path)}...")
#         self.root.update_idletasks()
        
#         try:
#             with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
#                 hex_data = f.read()

#             self.process_hex_data(hex_data)
            
#         except Exception as e:
#             messagebox.showerror("خطأ", f"فشل في قراءة الملف: {str(e)}")
#             self.status_var.set(f"خطأ في تحميل الملف: {os.path.basename(file_path)}")
    
#     def process_hex_data(self, hex_data):
#         self.status_var.set("جاري معالجة بيانات الهيكس...")
#         self.progress_var.set(0)
        
#         self.console.config(state=tk.NORMAL)
#         self.console.delete("1.0", tk.END)
#         self.console.insert(tk.END, "بدء معالجة بيانات الهيكس...\n")
#         self.console.config(state=tk.DISABLED)
        
#         def process_task():
#             try:
#                 # تنظيف بيانات الهيكس
#                 self.update_progress_display("جاري تنظيف بيانات الهيكس...", 5)
#                 cleaned_hex = self.parser.clean_hex_data(hex_data)
                
#                 # الكشف عن حدود الملفات
#                 self.update_progress_display("جاري الكشف عن حدود الملفات...", 10)
#                 boundaries = self.parser.detect_file_boundaries(cleaned_hex)
                
#                 if boundaries:
#                     # استخراج الملفات الفردية
#                     self.update_progress_display("جاري استخراج الملفات...", 40)
#                     self.parser.files_data = self.parser.extract_individual_files(cleaned_hex, boundaries)
                    
#                     # تحليل جميع الملفات
#                     self.update_progress_display("جاري تحليل الملفات...", 60)
#                     self.parser.files_data = self.parser.analyze_files_parallel(self.parser.files_data)
                    
#                     # اكتمال المهمة
#                     self.update_progress_display("اكتملت المعالجة!", 100)
                    
#                     success_message = f"تمت معالجة بيانات الهيكس بنجاح واستخراج {len(boundaries)} ملف"
#                     self.update_progress_display("=" * 50)
#                     self.update_progress_display(success_message)
#                     self.update_progress_display("=" * 50)
                    
#                     # تحديث واجهة المستخدم
#                     self.root.after(0, self.refresh_files_list)
#                     self.root.after(0, lambda: self.status_var.set(f"تم استخراج {len(boundaries)} ملف بنجاح"))
                    
#                     # الانتقال إلى علامة تبويب الملفات
#                     if len(boundaries) > 0:
#                         self.root.after(0, lambda: self.tab_control.select(1))
                    
#                 else:
#                     self.update_progress_display("لم يتم العثور على ملفات", 100)
#                     self.root.after(0, lambda: self.status_var.set("لم يتم العثور على ملفات"))
                    
#             except Exception as e:
#                 error_message = str(e)
#                 self.update_progress_display("حدث خطأ")
#                 self.update_progress_display("=" * 50)
#                 self.update_progress_display("❌ خطأ: فشلت المعالجة!")
#                 self.update_progress_display(f"تفاصيل الخطأ: {error_message}")
#                 self.update_progress_display("=" * 50)
#                 self.root.after(0, lambda: self.status_var.set("فشلت المعالجة"))
        
#         threading.Thread(target=process_task, daemon=True).start()
    
#     def browse_file(self):
#         file_path = filedialog.askopenfilename(
#             title="حدد ملف الهيكس",
#             filetypes=(("ملفات النص", "*.txt"), ("ملفات الهيكس", "*.hex"), ("جميع الملفات", "*.*"))
#         )
#         if file_path:
#             self.file_path_var.set(file_path)
    
#     def browse_directory(self):
#         directory = filedialog.askdirectory(title="حدد دليل الإخراج")
#         if directory:
#             self.output_dir_var.set(directory)
    
#     def refresh_files_list(self):
#         for item in self.files_tree.get_children():
#             self.files_tree.delete(item)
            
#         if hasattr(self.parser, 'files_data') and self.parser.files_data:
#             for file_id, file_data in self.parser.files_data.items():
#                 header = file_data.get('header_hex', '')[:16] + '...' if len(file_data.get('header_hex', '')) > 16 else file_data.get('header_hex', '')
#                 trailer = file_data.get('trailer_hex', '')[:16] + '...' if len(file_data.get('trailer_hex', '')) > 16 else file_data.get('trailer_hex', '')
                
#                 self.files_tree.insert('', tk.END, values=(
#                     file_id,
#                     file_data['file_type'],
#                     file_data['size_bytes'],
#                     header,
#                     trailer
#                 ))
    
#     def analyze_selected_file(self):
#         selected = self.files_tree.selection()
#         if not selected:
#             messagebox.showinfo("معلومات", "الرجاء تحديد ملف أولاً!")
#             return
            
#         file_id = self.files_tree.item(selected[0])['values'][0]
#         if file_id in self.parser.files_data:
#             file_data = self.parser.files_data[file_id]
            
#             # إنشاء نافذة جديدة لعرض المعلومات التفصيلية
#             detail_window = tk.Toplevel(self.root)
#             detail_window.title(f"تفاصيل الملف: {file_id}")
#             detail_window.geometry("800x600")
            
#             detail_notebook = ttk.Notebook(detail_window)
#             detail_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
#             # علامة التبويب 1: نظرة عامة
#             overview_tab = ttk.Frame(detail_notebook, padding=10)
#             detail_notebook.add(overview_tab, text="نظرة عامة")
            
#             # معلومات أساسية
#             info_frame = ttk.LabelFrame(overview_tab, text="معلومات الملف", padding="5")
#             info_frame.pack(fill=tk.X, pady=5)
            
#             info_columns = ttk.Frame(info_frame)
#             info_columns.pack(fill=tk.X, expand=True, padx=5, pady=5)
            
#             left_column = ttk.Frame(info_columns)
#             left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
#             right_column = ttk.Frame(info_columns)
#             right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
            
#             # معلومات العمود الأيسر
#             labels_left = [
#                 ("معرف الملف:", file_id),
#                 ("النوع:", file_data['file_type']),
#                 ("الحجم:", f"{file_data['size_bytes']:,} بايت"),
#                 ("التوقيع:", file_data['signature'])
#             ]
            
#             for i, (label, value) in enumerate(labels_left):
#                 frame = ttk.Frame(left_column)
#                 frame.pack(fill=tk.X, pady=2)
#                 ttk.Label(frame, text=label, width=12, font=("Arial", 9, "bold")).pack(side=tk.LEFT)
#                 ttk.Label(frame, text=str(value)).pack(side=tk.LEFT)
            
#             # معلومات العمود الأيمن
#             labels_right = [
#                 ("MD5:", file_data.get('md5', 'غير متوفر')),
#                 ("حجم الهيدر:", f"{file_data.get('header_size', 'غير متوفر')} بايت"),
#                 ("حجم الترايلر:", f"{file_data.get('trailer_size', 'غير متوفر')} بايت"),
#             ]
            
#             for i, (label, value) in enumerate(labels_right):
#                 frame = ttk.Frame(right_column)
#                 frame.pack(fill=tk.X, pady=2)
#                 ttk.Label(frame, text=label, width=12, font=("Arial", 9, "bold")).pack(side=tk.LEFT)
#                 ttk.Label(frame, text=str(value)).pack(side=tk.LEFT)
            
#             # معلومات الهيدر والترايلر
#             header_frame = ttk.LabelFrame(overview_tab, text="معلومات الهيدر", padding="5")
#             header_frame.pack(fill=tk.X, pady=5)
            
#             header_text = scrolledtext.ScrolledText(header_frame, height=3, wrap=tk.WORD, font=("Consolas", 9))
#             header_text.pack(fill=tk.BOTH, expand=True)
#             header_text.insert(tk.END, f"{file_data.get('header_info', '')}\n{file_data.get('header_hex', '')}")
#             header_text.config(state=tk.DISABLED)
            
#             trailer_frame = ttk.LabelFrame(overview_tab, text="معلومات الترايلر", padding="5")
#             trailer_frame.pack(fill=tk.X, pady=5)
            
#             trailer_text = scrolledtext.ScrolledText(trailer_frame, height=3, wrap=tk.WORD, font=("Consolas", 9))
#             trailer_text.pack(fill=tk.BOTH, expand=True)
#             trailer_text.insert(tk.END, f"{file_data.get('trailer_info', '')}\n{file_data.get('trailer_hex', '')}")
#             trailer_text.config(state=tk.DISABLED)
            
#             # زر الإغلاق
#             ttk.Button(
#                 detail_window,
#                 text="إغلاق",
#                 command=detail_window.destroy
#             ).pack(pady=10)
            
#     def rebuild_files(self):
#         if not hasattr(self.parser, 'files_data') or not self.parser.files_data:
#             messagebox.showinfo("معلومات", "لا توجد ملفات لإعادة البناء! قم بمعالجة بيانات الهيكس أولاً.")
#             return
            
#         output_dir = self.output_dir_var.get()
#         if not output_dir:
#             messagebox.showerror("خطأ", "الرجاء تحديد دليل الإخراج!")
#             return
            
#         self.status_var.set("جاري إعادة بناء الملفات...")
        
#         def rebuild_task():
#             try:
#                 results = self.parser.rebuild_all_files(self.parser.files_data, output_dir)
                
#                 self.root.after(0, lambda: messagebox.showinfo(
#                     "نجاح", 
#                     f"تمت إعادة بناء {len(results['successful'])} ملف بنجاح.\n"
#                     f"تم حفظ الملفات في {output_dir}"
#                 ))
#                 self.root.after(0, lambda: self.status_var.set(f"تمت إعادة بناء {len(results['successful'])} ملف"))
                
#                 if os.path.exists(output_dir):
#                     os.startfile(output_dir)
                
#             except Exception as e:
#                 self.root.after(0, lambda: messagebox.showerror("خطأ", f"فشلت إعادة البناء: {str(e)}"))
#                 self.root.after(0, lambda: self.status_var.set("فشلت إعادة البناء"))
        
#         threading.Thread(target=rebuild_task, daemon=True).start()
        
#     def save_hex_files(self):
#         if not hasattr(self.parser, 'files_data') or not self.parser.files_data:
#             messagebox.showinfo("معلومات", "لا توجد ملفات لحفظ الهيكس! قم بمعالجة بيانات الهيكس أولاً.")
#             return
            
#         output_dir = self.output_dir_var.get()
#         if not output_dir:
#             messagebox.showerror("خطأ", "الرجاء تحديد دليل الإخراج!")
#             return
            
#         self.status_var.set("جاري حفظ ملفات الهيكس...")
        
#         def save_hex_task():
#             try:
#                 results = self.parser.save_hex_files(self.parser.files_data, output_dir)
                
#                 self.root.after(0, lambda: messagebox.showinfo(
#                     "نجاح", 
#                     f"تم حفظ {len(results['successful'])} ملف هيكس بنجاح.\n"
#                     f"تم حفظ الملفات في {os.path.join(output_dir, 'hex_files')}"
#                 ))
#                 self.root.after(0, lambda: self.status_var.set(f"تم حفظ {len(results['successful'])} ملف هيكس"))
                
#                 hex_output_dir = os.path.join(output_dir, "hex_files")
#                 if os.path.exists(hex_output_dir):
#                     os.startfile(hex_output_dir)
                
#             except Exception as e:
#                 self.root.after(0, lambda: messagebox.showerror("خطأ", f"فشل حفظ الهيكس: {str(e)}"))
#                 self.root.after(0, lambda: self.status_var.set("فشل حفظ الهيكس"))
        
#         threading.Thread(target=save_hex_task, daemon=True).start()
    
#     def save_report(self):
#         if not hasattr(self.parser, 'files_data') or not self.parser.files_data:
#             messagebox.showinfo("معلومات", "لا توجد ملفات للتقرير! قم بمعالجة بيانات الهيكس أولاً.")
#             return
            
#         report_path = filedialog.asksaveasfilename(
#             defaultextension=".json",
#             filetypes=[("ملفات JSON", "*.json"), ("جميع الملفات", "*.*")],
#             title="حفظ تقرير الاستخراج"
#         )
        
#         if not report_path:
#             return
            
#         try:
#             self.parser.save_extraction_report(self.parser.files_data, report_path)
#             messagebox.showinfo("نجاح", f"تم حفظ التقرير في {report_path}")
            
#             if os.path.exists(report_path):
#                 os.startfile(report_path)
            
#         except Exception as e:
#             messagebox.showerror("خطأ", f"فشل حفظ التقرير: {str(e)}")

# if __name__ == "__main__":
#     root = tk.Tk()
#     root.title("أداة استخراج وبناء ملفات الهيكس المتقدمة")
    
#     # تطبيق السمة والأنماط
#     style = ttk.Style()
#     style.theme_use('clam')
    
#     style.configure("TFrame", background=BG_COLOR)
#     style.configure("TLabel", background=BG_COLOR, foreground=TEXT_COLOR, font=("Arial", 10))
#     style.configure("TLabelframe", background=BG_COLOR, foreground=TEXT_COLOR, bordercolor=BORDER_COLOR)
#     style.configure("TLabelframe.Label", background=BG_COLOR, foreground=PRIMARY_COLOR, font=("Arial", 11, "bold"))
    
#     style.configure("TButton", 
#                   background=SECONDARY_COLOR, 
#                   foreground="white", 
#                   font=("Arial", 10),
#                   borderwidth=1)
    
#     style.configure("Accent.TButton", 
#                   background=ACCENT_COLOR, 
#                   foreground="white", 
#                   font=("Arial", 10, "bold"))
                  
#     style.configure("Treeview", 
#                   background=BG_COLOR,
#                   foreground=TEXT_COLOR,
#                   rowheight=25,
#                   fieldbackground=BG_COLOR,
#                   font=("Arial", 9))
#     style.configure("Treeview.Heading", 
#                   font=("Arial", 10, "bold"),
#                   background=PRIMARY_COLOR,
#                   foreground="white")
                  
#     style.configure("TNotebook", background=BG_COLOR)
#     style.configure("TNotebook.Tab", 
#                   background=BORDER_COLOR, 
#                   foreground=TEXT_COLOR,
#                   padding=[10, 5],
#                   font=("Arial", 10))
#     style.map("TNotebook.Tab", 
#              background=[('selected', PRIMARY_COLOR)],
#              foreground=[('selected', 'white')])
        
#     # إنشاء التطبيق الرئيسي
#     app = HexExtractorGUI(root)
    
#     # توسيط النافذة على الشاشة
#     root.update_idletasks()
#     width = root.winfo_width()
#     height = root.winfo_height()
#     x = (root.winfo_screenwidth() // 2) - (width // 2)
#     y = (root.winfo_screenheight() // 2) - (height // 2)
#     root.geometry(f"{width}x{height}+{x}+{y}")
    
#     # بدء الحلقة الرئيسية
#     root.mainloop()


import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from pathlib import Path
import time
import json
from Hex_Bulding import MultiFileHexParser

# Color scheme definition
BG_COLOR = "#f5f5f5"
PRIMARY_COLOR = "#2c3e50"
SECONDARY_COLOR = "#3498db"
ACCENT_COLOR = "#e74c3c"
SUCCESS_COLOR = "#27ae60"
WARNING_COLOR = "#f39c12"
TEXT_COLOR = "#2c3e50"
BORDER_COLOR = "#bdc3c7"

class RedirectText:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.config(state=tk.DISABLED)

    def flush(self):
        pass

class HexExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Hex File Extractor and Builder")
        self.root.geometry("1200x800")
        self.root.config(bg=BG_COLOR)
        
        # Prevent multiple clicks
        self.processing = False
        
        self.parser = MultiFileHexParser()
        self.setup_ui()
        
        # Set up progress callback
        self.parser.set_progress_callback(self.update_progress_display)

    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(
            title_frame, 
            text="🔧 Advanced Hex File Extractor and Builder", 
            font=("Segoe UI", 18, "bold"),
            foreground=PRIMARY_COLOR
        )
        title_label.pack(pady=5)
        
        subtitle_label = ttk.Label(
            title_frame,
            text="Extract and rebuild multiple files from combined hex data | Supports: JPG, PNG, EXE, DLL, TXT, PDF, BMP, MP3, MP4, MOV",
            font=("Segoe UI", 10)
        )
        subtitle_label.pack()
        
        # Tab control
        self.tab_control = ttk.Notebook(main_frame)
        self.tab_control.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Input
        input_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(input_tab, text="📥 Hex Input")
        self.setup_input_tab(input_tab)
        
        # Tab 2: Extracted Files
        files_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(files_tab, text="📁 Extracted Files")
        self.setup_files_tab(files_tab)
        
        # Tab 3: Output
        output_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(output_tab, text="🔨 File Reconstruction")
        self.setup_output_tab(output_tab)
        
        # Console output frame
        console_frame = ttk.LabelFrame(main_frame, text="📝 Console Output", padding="10")
        console_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.console = scrolledtext.ScrolledText(console_frame, height=10, wrap=tk.WORD, font=("Consolas", 9))
        self.console.pack(fill=tk.BOTH, expand=True)
        self.console.config(state=tk.DISABLED, background="#1e1e1e", foreground="#ffffff")
        
        # Redirect stdout to console
        self.text_redirect = RedirectText(self.console)
        sys.stdout = self.text_redirect
        
        # Status bar
        status_frame = ttk.Frame(main_frame, relief=tk.SUNKEN)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
        
        self.status_var = tk.StringVar()
        self.status_var.set("🟢 Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, font=("Segoe UI", 9))
        status_label.pack(side=tk.LEFT, padx=10)
        
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(status_frame, variable=self.progress_var, length=300, mode='determinate')
        self.progress.pack(side=tk.RIGHT, padx=10, pady=5)
        
    def setup_input_tab(self, parent):
        # Input methods frame
        input_methods_frame = ttk.LabelFrame(parent, text="Input Methods", padding="15")
        input_methods_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        
        # Option 1: Paste Hex
        paste_frame = ttk.LabelFrame(input_methods_frame, text="Paste Hex Data", padding="10")
        paste_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.hex_input = scrolledtext.ScrolledText(paste_frame, height=15, wrap=tk.WORD, font=("Consolas", 10))
        self.hex_input.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Process button
        process_btn_frame = ttk.Frame(paste_frame)
        process_btn_frame.pack(fill=tk.X, pady=5)
        
        self.paste_btn = ttk.Button(
            process_btn_frame, 
            text="🔍 Process Hex Data", 
            command=self.process_pasted_hex,
            style="Accent.TButton"
        )
        self.paste_btn.pack(pady=5, fill=tk.X)
        
        # Option 2: Load from file
        file_frame = ttk.LabelFrame(input_methods_frame, text="Load from File", padding="10")
        file_frame.pack(fill=tk.X, pady=10)
        
        # File selection entry and browse button
        file_select_frame = ttk.Frame(file_frame)
        file_select_frame.pack(fill=tk.X, pady=5)
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_select_frame, textvariable=self.file_path_var, width=60, font=("Segoe UI", 10))
        file_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(
            file_select_frame, 
            text="📂 Browse...", 
            command=self.browse_file,
            width=15
        )
        browse_btn.pack(side=tk.LEFT)
        
        # Load button
        file_buttons_frame = ttk.Frame(file_frame)
        file_buttons_frame.pack(fill=tk.X, pady=5)
        
        self.load_btn = ttk.Button(
            file_buttons_frame, 
            text="📥 Load and Process File", 
            command=self.load_from_file,
            style="Accent.TButton"
        )
        self.load_btn.pack(fill=tk.X)
        
        # File info label
        self.file_info_label = ttk.Label(file_frame, text="", font=("Segoe UI", 9, "italic"), foreground=PRIMARY_COLOR)
        self.file_info_label.pack(anchor=tk.W, pady=5)

    def setup_files_tab(self, parent):
        # Files display frame
        files_frame = ttk.Frame(parent, padding="10")
        files_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for files
        columns = ('file_id', 'type', 'size', 'header_preview', 'trailer_preview', 'signature')
        self.files_tree = ttk.Treeview(files_frame, columns=columns, show='headings', selectmode='browse')
        
        # Define headings
        self.files_tree.heading('file_id', text='File ID')
        self.files_tree.heading('type', text='Type')
        self.files_tree.heading('size', text='Size (bytes)')
        self.files_tree.heading('header_preview', text='Header Preview')
        self.files_tree.heading('trailer_preview', text='Trailer Preview')
        self.files_tree.heading('signature', text='Signature')
        
        # Define column widths
        self.files_tree.column('file_id', width=120, anchor=tk.W)
        self.files_tree.column('type', width=80, anchor=tk.CENTER)
        self.files_tree.column('size', width=100, anchor=tk.CENTER)
        self.files_tree.column('header_preview', width=180, anchor=tk.W)
        self.files_tree.column('trailer_preview', width=180, anchor=tk.W)
        self.files_tree.column('signature', width=120, anchor=tk.W)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(files_frame, orient="vertical", command=self.files_tree.yview)
        hsb = ttk.Scrollbar(files_frame, orient="horizontal", command=self.files_tree.xview)
        self.files_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.files_tree.grid(column=0, row=0, sticky='nsew')
        vsb.grid(column=1, row=0, sticky='ns')
        hsb.grid(column=0, row=1, sticky='ew')
        
        files_frame.grid_columnconfigure(0, weight=1)
        files_frame.grid_rowconfigure(0, weight=1)
        
        # Button frame
        button_frame = ttk.Frame(parent, padding="10")
        button_frame.pack(fill=tk.X)
        
        refresh_btn = ttk.Button(button_frame, text="🔄 Refresh File List", command=self.refresh_files_list)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        analyze_btn = ttk.Button(button_frame, text="🔍 Analyze Selected File", command=self.analyze_selected_file)
        analyze_btn.pack(side=tk.LEFT, padx=5)
        
        view_hex_btn = ttk.Button(button_frame, text="📊 View Full Hex Data", command=self.view_hex_data)
        view_hex_btn.pack(side=tk.LEFT, padx=5)
        
        # Info label
        info_label = ttk.Label(button_frame, text="Double-click a file to view details", font=("Segoe UI", 9, "italic"))
        info_label.pack(side=tk.RIGHT, padx=10)
        
        # Bind double-click event
        self.files_tree.bind('<Double-1>', lambda e: self.analyze_selected_file())

    def setup_output_tab(self, parent):
        # Output options frame
        output_frame = ttk.LabelFrame(parent, text="Output Options", padding="15")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        
        # Output directory
        dir_frame = ttk.Frame(output_frame)
        dir_frame.pack(fill=tk.X, pady=10)
        
        dir_label = ttk.Label(dir_frame, text="Output Directory:", font=("Segoe UI", 10, "bold"))
        dir_label.pack(anchor=tk.W, pady=(0, 5))
        
        dir_select_frame = ttk.Frame(dir_frame)
        dir_select_frame.pack(fill=tk.X, pady=5)
        
        self.output_dir_var = tk.StringVar(value="reconstructed_files")
        dir_entry = ttk.Entry(dir_select_frame, textvariable=self.output_dir_var, width=60, font=("Segoe UI", 10))
        dir_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        browse_dir_btn = ttk.Button(dir_select_frame, text="📁 Browse...", command=self.browse_directory, width=15)
        browse_dir_btn.pack(side=tk.LEFT)
        
        # Action buttons
        action_frame = ttk.LabelFrame(output_frame, text="Actions", padding="10")
        action_frame.pack(fill=tk.X, pady=10)
        
        button_grid = ttk.Frame(action_frame)
        button_grid.pack(fill=tk.X, expand=True)
        
        # Row 1
        row1 = ttk.Frame(button_grid)
        row1.pack(fill=tk.X, pady=5)
        
        self.rebuild_btn = ttk.Button(
            row1, 
            text="🔨 Rebuild All Files", 
            command=self.rebuild_files,
            style="Accent.TButton"
        )
        self.rebuild_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.save_hex_btn = ttk.Button(
            row1, 
            text="💾 Save Hex Files", 
            command=self.save_hex_files
        )
        self.save_hex_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Row 2
        row2 = ttk.Frame(button_grid)
        row2.pack(fill=tk.X, pady=5)
        
        save_report_btn = ttk.Button(
            row2, 
            text="📄 Save Extraction Report", 
            command=self.save_report
        )
        save_report_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        clear_btn = ttk.Button(
            row2, 
            text="🗑️ Clear All Data", 
            command=self.clear_all_data
        )
        clear_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(output_frame, text="Statistics", padding="10")
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.stats_label = ttk.Label(stats_frame, text="No files processed yet", font=("Segoe UI", 10))
        self.stats_label.pack()

    def update_progress_display(self, message, percent=None):
        """Update progress display from parser"""
        def update():
            self.console.config(state=tk.NORMAL)
            self.console.insert(tk.END, message + "\n")
            self.console.see(tk.END)
            self.console.config(state=tk.DISABLED)
            
            if percent is not None:
                self.progress_var.set(percent)
                
            self.status_var.set(message[:60] + "..." if len(message) > 60 else message)
            self.root.update_idletasks()
        
        self.root.after(0, update)

    def update_button_state(self, state):
        """Update button states (enable/disable)"""
        def update():
            if state == "disabled":
                self.paste_btn.config(state=tk.DISABLED)
                self.load_btn.config(state=tk.DISABLED)
                self.rebuild_btn.config(state=tk.DISABLED)
                self.save_hex_btn.config(state=tk.DISABLED)
                self.processing = True
            else:
                self.paste_btn.config(state=tk.NORMAL)
                self.load_btn.config(state=tk.NORMAL)
                self.rebuild_btn.config(state=tk.NORMAL)
                self.save_hex_btn.config(state=tk.NORMAL)
                self.processing = False
        
        self.root.after(0, update)

    def process_pasted_hex(self):
        if self.processing:
            messagebox.showwarning("Processing", "Another process is already running. Please wait.")
            return
            
        hex_data = self.hex_input.get("1.0", tk.END).strip()
        if not hex_data:
            messagebox.showerror("Error", "Please enter hex data first!")
            return
            
        # Validate hex data
        hex_chars = set("0123456789ABCDEFabcdef \n\t\r")
        valid_chars = all(c in hex_chars for c in hex_data)
        
        if not valid_chars:
            if messagebox.askyesno("Warning", 
                                 "The data contains non-hex characters. Do you want to clean it automatically?"):
                # Clean the data
                hex_data = ''.join(c for c in hex_data if c in "0123456789ABCDEFabcdef")
            else:
                return
        
        self.process_hex_data(hex_data, source="pasted")
    
    def load_from_file(self):
        if self.processing:
            messagebox.showwarning("Processing", "Another process is already running. Please wait.")
            return
            
        file_path = self.file_path_var.get()
        
        if not file_path:
            file_path = filedialog.askopenfilename(
                title="Select Hex File",
                filetypes=[
                    ("Text files", "*.txt"),
                    ("Hex files", "*.hex"),
                    ("All files", "*.*")
                ]
            )
            if not file_path:
                return
            self.file_path_var.set(file_path)
        
        if not os.path.exists(file_path):
            messagebox.showerror("Error", f"File not found: {file_path}")
            return
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > 50 * 1024 * 1024:  # 50 MB
            if not messagebox.askyesno("Warning", 
                                     f"File size is {file_size/1024/1024:.1f} MB. This may take a long time.\nDo you want to continue?"):
                return
        
        # Update file info
        self.file_info_label.config(text=f"File: {os.path.basename(file_path)} | Size: {file_size:,} bytes")
        
        self.status_var.set(f"Loading file: {os.path.basename(file_path)}...")
        self.progress_var.set(10)
        self.root.update_idletasks()
        
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'utf-16']
        hex_data = None
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                    content = f.read()
                
                # Check if content looks like hex
                hex_chars = set("0123456789ABCDEFabcdef \n\t\r")
                sample = content[:1000]
                hex_ratio = sum(1 for c in sample if c in hex_chars) / max(1, len(sample))
                
                if hex_ratio > 0.7:  # At least 70% hex characters
                    hex_data = content
                    self.update_progress_display(f"✓ Successfully read file with {encoding} encoding")
                    break
                else:
                    self.update_progress_display(f"⚠ File doesn't appear to be hex data ({encoding})")
                    
            except UnicodeDecodeError:
                self.update_progress_display(f"✗ Failed to read with {encoding} encoding")
                continue
            except Exception as e:
                self.update_progress_display(f"✗ Error with {encoding}: {str(e)}")
                continue
        
        if hex_data is None:
            # Try binary read
            try:
                self.update_progress_display("⚠ Trying binary read...")
                with open(file_path, 'rb') as f:
                    binary_data = f.read()
                # Convert binary to hex string
                hex_data = binary_data.hex().upper()
                self.update_progress_display("✓ Converted binary file to hex")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read file with any encoding:\n{str(e)}")
                self.status_var.set("File read failed")
                return
        
        self.process_hex_data(hex_data, source="file")

    def process_hex_data(self, hex_data, source="unknown"):
        self.update_button_state("disabled")
        self.status_var.set("Processing hex data...")
        self.progress_var.set(0)
        
        self.console.config(state=tk.NORMAL)
        self.console.delete("1.0", tk.END)
        self.console.insert(tk.END, "=" * 60 + "\n")
        self.console.insert(tk.END, f"Starting hex data processing (Source: {source})\n")
        self.console.insert(tk.END, f"Data length: {len(hex_data):,} characters\n")
        self.console.insert(tk.END, "=" * 60 + "\n\n")
        self.console.config(state=tk.DISABLED)
        
        def process_task():
            try:
                # Clean hex data
                self.update_progress_display("Cleaning hex data...", 5)
                cleaned_hex = self.parser.clean_hex_data(hex_data)
                
                if not cleaned_hex:
                    self.update_progress_display("❌ Error: No valid hex data after cleaning", 100)
                    self.root.after(0, lambda: messagebox.showerror("Error", "No valid hex data found!"))
                    self.update_button_state("enabled")
                    return
                
                self.update_progress_display(f"Cleaned hex data length: {len(cleaned_hex):,} characters", 20)
                
                # Detect file boundaries
                self.update_progress_display("Detecting file boundaries...", 30)
                boundaries = self.parser.detect_file_boundaries(cleaned_hex)
                
                if boundaries:
                    self.update_progress_display(f"Found {len(boundaries)} potential files", 40)
                    
                    # Extract individual files
                    self.update_progress_display("Extracting files...", 50)
                    self.parser.files_data = self.parser.extract_individual_files(cleaned_hex, boundaries)
                    
                    # Analyze all files
                    self.update_progress_display("Analyzing files...", 70)
                    self.parser.files_data = self.parser.analyze_files_parallel(self.parser.files_data)
                    
                    # Task completion
                    self.update_progress_display("Processing complete!", 100)
                    
                    success_message = f"✅ Successfully processed hex data and extracted {len(boundaries)} files"
                    self.update_progress_display("=" * 60)
                    self.update_progress_display(success_message)
                    self.update_progress_display("=" * 60)
                    
                    # Update UI
                    self.root.after(0, self.refresh_files_list)
                    self.root.after(0, lambda: self.status_var.set(f"Extracted {len(boundaries)} files successfully"))
                    
                    # Update statistics
                    total_size = sum(f['size_bytes'] for f in self.parser.files_data.values())
                    self.root.after(0, lambda: self.stats_label.config(
                        text=f"Total Files: {len(boundaries)} | Total Size: {total_size:,} bytes"
                    ))
                    
                    # Switch to files tab
                    if len(boundaries) > 0:
                        self.root.after(0, lambda: self.tab_control.select(1))
                    
                else:
                    self.update_progress_display("No files found", 100)
                    self.root.after(0, lambda: messagebox.showinfo("Information", "No files found in the hex data."))
                    self.root.after(0, lambda: self.status_var.set("No files found"))
                    
            except Exception as e:
                error_message = str(e)
                self.update_progress_display("An error occurred")
                self.update_progress_display("=" * 60)
                self.update_progress_display("❌ Error: Processing failed!")
                self.update_progress_display(f"Error details: {error_message}")
                self.update_progress_display("=" * 60)
                self.root.after(0, lambda: self.status_var.set("Processing failed"))
                self.root.after(0, lambda: messagebox.showerror("Error", f"Processing failed:\n{error_message}"))
            
            finally:
                self.update_button_state("enabled")
        
        threading.Thread(target=process_task, daemon=True).start()
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Hex File",
            filetypes=[
                ("Text files", "*.txt"),
                ("Hex files", "*.hex"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.file_path_var.set(file_path)
            # Update file info label
            try:
                file_size = os.path.getsize(file_path)
                self.file_info_label.config(text=f"File: {os.path.basename(file_path)} | Size: {file_size:,} bytes")
            except:
                self.file_info_label.config(text=f"File: {os.path.basename(file_path)}")
    
    def browse_directory(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)
    
    def refresh_files_list(self):
        for item in self.files_tree.get_children():
            self.files_tree.delete(item)
            
        if hasattr(self.parser, 'files_data') and self.parser.files_data:
            for file_id, file_data in self.parser.files_data.items():
                header_hex = file_data.get('header_hex', '')
                trailer_hex = file_data.get('trailer_hex', '')
                
                # Create previews (first 20 chars)
                header_preview = header_hex[:40] + '...' if len(header_hex) > 40 else header_hex
                trailer_preview = trailer_hex[:40] + '...' if len(trailer_hex) > 40 else trailer_hex
                
                self.files_tree.insert('', tk.END, values=(
                    file_id,
                    file_data['file_type'],
                    f"{file_data['size_bytes']:,}",
                    header_preview,
                    trailer_preview,
                    file_data.get('signature', 'N/A')
                ))
    
    def analyze_selected_file(self):
        selected = self.files_tree.selection()
        if not selected:
            messagebox.showinfo("Information", "Please select a file first!")
            return
            
        file_id = self.files_tree.item(selected[0])['values'][0]
        if file_id in self.parser.files_data:
            file_data = self.parser.files_data[file_id]
            self.show_file_details(file_data, file_id)
            
    def show_file_details(self, file_data, file_id):
        """Show detailed file information in a new window"""
        # Create a new window for detailed information
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"File Details: {file_id}")
        detail_window.geometry("1000x800")
        detail_window.minsize(900, 700)
        
        # Main notebook for tabs
        detail_notebook = ttk.Notebook(detail_window)
        detail_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Overview
        overview_tab = ttk.Frame(detail_notebook, padding=15)
        detail_notebook.add(overview_tab, text="📋 Overview")
        
        # Basic info frame
        info_frame = ttk.LabelFrame(overview_tab, text="File Information", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Create grid for info
        info_grid = ttk.Frame(info_frame)
        info_grid.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        # Left column
        left_column = ttk.Frame(info_grid)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        # Right column
        right_column = ttk.Frame(info_grid)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Left column info
        left_info = [
            ("File ID:", file_id),
            ("Type:", file_data['file_type']),
            ("Size:", f"{file_data['size_bytes']:,} bytes"),
            ("Signature:", file_data['signature']),
            ("Start Offset:", f"0x{file_data.get('start_offset', 0)//2:X}"),
            ("End Offset:", f"0x{file_data.get('end_offset', 0)//2:X}"),
        ]
        
        for label, value in left_info:
            frame = ttk.Frame(left_column)
            frame.pack(fill=tk.X, pady=3)
            ttk.Label(frame, text=label, width=15, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
            ttk.Label(frame, text=str(value), font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(10, 0))
        
        # Right column info
        right_info = [
            ("MD5:", file_data.get('md5', 'N/A')),
            ("Header Size:", f"{file_data.get('header_size', 0)} bytes"),
            ("Trailer Size:", f"{file_data.get('trailer_size', 0)} bytes"),
            ("Header Info:", file_data.get('header_info', 'N/A')),
            ("Trailer Info:", file_data.get('trailer_info', 'N/A')),
        ]
        
        for label, value in right_info:
            frame = ttk.Frame(right_column)
            frame.pack(fill=tk.X, pady=3)
            ttk.Label(frame, text=label, width=15, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
            ttk.Label(frame, text=str(value), font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(10, 0))
        
        # Tab 2: Blocks (Header and Trailer Details)
        blocks_tab = ttk.Frame(detail_notebook, padding=15)
        detail_notebook.add(blocks_tab, text="🔧 Blocks")
        
        # Header block
        header_frame = ttk.LabelFrame(blocks_tab, text="Header Block", padding="10")
        header_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        header_info_label = ttk.Label(header_frame, text=f"Info: {file_data.get('header_info', 'N/A')} | Size: {file_data.get('header_size', 0)} bytes", font=("Segoe UI", 9, "bold"))
        header_info_label.pack(anchor=tk.W, pady=(0, 10))
        
        header_text = scrolledtext.ScrolledText(header_frame, wrap=tk.WORD, font=("Consolas", 9))
        header_text.pack(fill=tk.BOTH, expand=True)
        
        header_hex = file_data.get('header_hex', '')
        header_content = f"HEX DATA:\n{header_hex}\n\n"
        header_content += "ASCII REPRESENTATION:\n"
        
        # Try to convert hex to ASCII
        try:
            header_bytes = bytes.fromhex(header_hex)
            ascii_repr = ''
            for i, b in enumerate(header_bytes):
                if 32 <= b <= 126:
                    ascii_repr += chr(b)
                else:
                    ascii_repr += '.'
                if (i + 1) % 16 == 0:
                    ascii_repr += '\n'
            header_content += ascii_repr
        except:
            header_content += "Unable to convert to ASCII"
        
        header_text.insert(tk.END, header_content)
        header_text.config(state=tk.DISABLED)
        
        # Trailer block
        trailer_frame = ttk.LabelFrame(blocks_tab, text="Trailer Block", padding="10")
        trailer_frame.pack(fill=tk.BOTH, expand=True)
        
        trailer_info_label = ttk.Label(trailer_frame, text=f"Info: {file_data.get('trailer_info', 'N/A')} | Size: {file_data.get('trailer_size', 0)} bytes", font=("Segoe UI", 9, "bold"))
        trailer_info_label.pack(anchor=tk.W, pady=(0, 10))
        
        trailer_text = scrolledtext.ScrolledText(trailer_frame, wrap=tk.WORD, font=("Consolas", 9))
        trailer_text.pack(fill=tk.BOTH, expand=True)
        
        trailer_hex = file_data.get('trailer_hex', '')
        trailer_content = f"HEX DATA:\n{trailer_hex}\n\n"
        trailer_content += "ASCII REPRESENTATION:\n"
        
        # Try to convert hex to ASCII
        try:
            trailer_bytes = bytes.fromhex(trailer_hex)
            ascii_repr = ''
            for i, b in enumerate(trailer_bytes):
                if 32 <= b <= 126:
                    ascii_repr += chr(b)
                else:
                    ascii_repr += '.'
                if (i + 1) % 16 == 0:
                    ascii_repr += '\n'
            trailer_content += ascii_repr
        except:
            trailer_content += "Unable to convert to ASCII"
        
        trailer_text.insert(tk.END, trailer_content)
        trailer_text.config(state=tk.DISABLED)
        
        # Tab 3: Hex View
        hex_tab = ttk.Frame(detail_notebook, padding=15)
        detail_notebook.add(hex_tab, text="📊 Full Hex View")
        
        hex_frame = ttk.LabelFrame(hex_tab, text="Complete Hex Data", padding="10")
        hex_frame.pack(fill=tk.BOTH, expand=True)
        
        hex_view = scrolledtext.ScrolledText(hex_frame, wrap=tk.NONE, font=("Consolas", 9))
        hex_view.pack(fill=tk.BOTH, expand=True)
        
        hex_data = file_data.get('hex_data', '')
        # Format hex data with offsets
        formatted_hex = ""
        for i in range(0, len(hex_data), 32):
            chunk = hex_data[i:i+32]
            offset = i // 2
            ascii_part = ""
            
            # Convert to ASCII for the right side
            try:
                chunk_bytes = bytes.fromhex(chunk)
                for b in chunk_bytes:
                    if 32 <= b <= 126:
                        ascii_part += chr(b)
                    else:
                        ascii_part += '.'
            except:
                ascii_part = " " * (len(chunk) // 2)
            
            formatted_hex += f"{offset:08X}: {chunk}  {ascii_part}\n"
        
        hex_view.insert(tk.END, formatted_hex)
        hex_view.config(state=tk.DISABLED)
        
        # Close button
        close_frame = ttk.Frame(detail_window)
        close_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            close_frame,
            text="Close",
            command=detail_window.destroy
        ).pack(side=tk.RIGHT)
        
    def view_hex_data(self):
        selected = self.files_tree.selection()
        if not selected:
            messagebox.showinfo("Information", "Please select a file first!")
            return
            
        file_id = self.files_tree.item(selected[0])['values'][0]
        if file_id in self.parser.files_data:
            file_data = self.parser.files_data[file_id]
            self.show_file_details(file_data, file_id)
            # Switch to hex tab
            for win in self.root.winfo_children():
                if isinstance(win, tk.Toplevel) and "File Details" in win.title():
                    for child in win.winfo_children():
                        if isinstance(child, ttk.Notebook):
                            child.select(2)  # Select hex tab
                            break
                    break
            
    def rebuild_files(self):
        if self.processing:
            messagebox.showwarning("Processing", "Another process is already running. Please wait.")
            return
            
        if not hasattr(self.parser, 'files_data') or not self.parser.files_data:
            messagebox.showinfo("Information", "No files to rebuild! Please process hex data first.")
            return
            
        output_dir = self.output_dir_var.get()
        if not output_dir:
            messagebox.showerror("Error", "Please specify output directory!")
            return
            
        self.status_var.set("Rebuilding files...")
        self.update_button_state("disabled")
        
        def rebuild_task():
            try:
                results = self.parser.rebuild_all_files(self.parser.files_data, output_dir)
                
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success", 
                    f"✅ Successfully rebuilt {len(results['successful'])} files.\n\n"
                    f"📁 Directory: {output_dir}\n"
                    f"📊 Total: {results['total_files']} files\n"
                    f"✅ Successful: {len(results['successful'])}\n"
                    f"❌ Failed: {len(results['failed'])}"
                ))
                self.root.after(0, lambda: self.status_var.set(f"Rebuilt {len(results['successful'])} files"))
                
                # Open directory if successful
                if len(results['successful']) > 0 and os.path.exists(output_dir):
                    os.startfile(output_dir)
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Rebuild failed: {str(e)}"))
                self.root.after(0, lambda: self.status_var.set("Rebuild failed"))
            
            finally:
                self.update_button_state("enabled")
        
        threading.Thread(target=rebuild_task, daemon=True).start()
        
    def save_hex_files(self):
        if self.processing:
            messagebox.showwarning("Processing", "Another process is already running. Please wait.")
            return
            
        if not hasattr(self.parser, 'files_data') or not self.parser.files_data:
            messagebox.showinfo("Information", "No hex files to save! Please process hex data first.")
            return
            
        output_dir = self.output_dir_var.get()
        if not output_dir:
            messagebox.showerror("Error", "Please specify output directory!")
            return
            
        self.status_var.set("Saving hex files...")
        self.update_button_state("disabled")
        
        def save_hex_task():
            try:
                results = self.parser.save_hex_files(self.parser.files_data, output_dir)
                
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success", 
                    f"✅ Successfully saved {len(results['successful'])} hex files.\n\n"
                    f"📁 Directory: {os.path.join(output_dir, 'hex_files')}\n"
                    f"📊 Total: {results['total_files']} files\n"
                    f"✅ Successful: {len(results['successful'])}\n"
                    f"❌ Failed: {len(results['failed'])}"
                ))
                self.root.after(0, lambda: self.status_var.set(f"Saved {len(results['successful'])} hex files"))
                
                hex_output_dir = os.path.join(output_dir, "hex_files")
                if os.path.exists(hex_output_dir):
                    os.startfile(hex_output_dir)
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Hex save failed: {str(e)}"))
                self.root.after(0, lambda: self.status_var.set("Hex save failed"))
            
            finally:
                self.update_button_state("enabled")
        
        threading.Thread(target=save_hex_task, daemon=True).start()
    
    def save_report(self):
        if not hasattr(self.parser, 'files_data') or not self.parser.files_data:
            messagebox.showinfo("Information", "No files for report! Please process hex data first.")
            return
            
        report_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Extraction Report"
        )
        
        if not report_path:
            return
            
        try:
            self.parser.save_extraction_report(self.parser.files_data, report_path)
            messagebox.showinfo("Success", f"✅ Report saved to:\n{report_path}")
            
            if os.path.exists(report_path):
                os.startfile(report_path)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save report: {str(e)}")
    
    def clear_all_data(self):
        """Clear all processed data"""
        if self.processing:
            messagebox.showwarning("Processing", "Cannot clear while processing is in progress.")
            return
            
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all data? This cannot be undone."):
            self.parser.files_data = {}
            self.hex_input.delete("1.0", tk.END)
            self.file_path_var.set("")
            self.file_info_label.config(text="")
            self.refresh_files_list()
            self.console.config(state=tk.NORMAL)
            self.console.delete("1.0", tk.END)
            self.console.config(state=tk.DISABLED)
            self.stats_label.config(text="No files processed yet")
            self.status_var.set("🟢 Ready")
            self.progress_var.set(0)
            messagebox.showinfo("Cleared", "All data has been cleared.")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Advanced Hex File Extractor and Builder")
    
    # Apply theme and styles
    style = ttk.Style()
    style.theme_use('clam')
    
    # Configure styles
    style.configure("TFrame", background=BG_COLOR)
    style.configure("TLabel", background=BG_COLOR, foreground=TEXT_COLOR, font=("Segoe UI", 10))
    style.configure("TLabelframe", background=BG_COLOR, foreground=TEXT_COLOR, bordercolor=BORDER_COLOR, font=("Segoe UI", 10, "bold"))
    style.configure("TLabelframe.Label", background=BG_COLOR, foreground=PRIMARY_COLOR, font=("Segoe UI", 11, "bold"))
    
    style.configure("TButton", 
                  background=SECONDARY_COLOR, 
                  foreground="white", 
                  font=("Segoe UI", 10),
                  borderwidth=1,
                  padding=8)
    
    style.configure("Accent.TButton", 
                  background=ACCENT_COLOR, 
                  foreground="white", 
                  font=("Segoe UI", 10, "bold"),
                  padding=8)
                  
    style.configure("Treeview", 
                  background="white",
                  foreground=TEXT_COLOR,
                  rowheight=28,
                  fieldbackground="white",
                  font=("Segoe UI", 9))
    style.configure("Treeview.Heading", 
                  font=("Segoe UI", 10, "bold"),
                  background=PRIMARY_COLOR,
                  foreground="white",
                  padding=5)
    
    style.map("Treeview", 
              background=[('selected', SECONDARY_COLOR)],
              foreground=[('selected', 'white')])
    
    style.configure("TNotebook", background=BG_COLOR)
    style.configure("TNotebook.Tab", 
                  background="#e0e0e0", 
                  foreground=TEXT_COLOR,
                  padding=[15, 5],
                  font=("Segoe UI", 10))
    style.map("TNotebook.Tab", 
             background=[('selected', PRIMARY_COLOR)],
             foreground=[('selected', 'white')])
    
    # Create main application
    app = HexExtractorGUI(root)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    # Start main loop
    root.mainloop()