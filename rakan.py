import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import re
from pathlib import Path
import json

class FileRecoveryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("نظام استعادة الملفات من الفلاش")
        self.root.geometry("1400x800")
        self.root.configure(bg='#2c3e50')
        
        # قاموس أنواع الملفات بناءً على Header
        self.file_signatures = {
            'FFD8FF': {'ext': '.jpg', 'name': 'JPEG Image', 'trailer': 'FFD9'},
            '89504E47': {'ext': '.png', 'name': 'PNG Image', 'trailer': '49454E44AE426082'},
            '474946383961': {'ext': '.gif', 'name': 'GIF Image (89a)', 'trailer': '003B'},
            '474946383761': {'ext': '.gif', 'name': 'GIF Image (87a)', 'trailer': '003B'},
            '25504446': {'ext': '.pdf', 'name': 'PDF Document', 'trailer': '0A2525454F46'},
            '504B0304': {'ext': '.zip', 'name': 'ZIP Archive', 'trailer': '504B0506'},
            '504B0506': {'ext': '.zip', 'name': 'ZIP Archive (empty)', 'trailer': '504B0506'},
            '504B0708': {'ext': '.zip', 'name': 'ZIP Archive (spanned)', 'trailer': '504B0506'},
            '52617221': {'ext': '.rar', 'name': 'RAR Archive', 'trailer': 'C43D7B00400700'},
            '377ABCAF271C': {'ext': '.7z', 'name': '7-Zip Archive', 'trailer': None},
            '1F8B08': {'ext': '.gz', 'name': 'GZIP Archive', 'trailer': None},
            '425A68': {'ext': '.bz2', 'name': 'BZIP2 Archive', 'trailer': None},
            '49492A00': {'ext': '.tif', 'name': 'TIFF Image (little endian)', 'trailer': None},
            '4D4D002A': {'ext': '.tif', 'name': 'TIFF Image (big endian)', 'trailer': None},
            '424D': {'ext': '.bmp', 'name': 'BMP Image', 'trailer': None},
            '00000100': {'ext': '.ico', 'name': 'Icon File', 'trailer': None},
            '52494646': {'ext': '.avi', 'name': 'AVI Video', 'trailer': None},
            '000001BA': {'ext': '.mpg', 'name': 'MPEG Video', 'trailer': None},
            '000001B3': {'ext': '.mpg', 'name': 'MPEG Video', 'trailer': None},
            '66747970': {'ext': '.mp4', 'name': 'MP4 Video', 'trailer': None},
            '1A45DFA3': {'ext': '.mkv', 'name': 'Matroska Video', 'trailer': None},
            '494433': {'ext': '.mp3', 'name': 'MP3 Audio', 'trailer': None},
            'FFFB': {'ext': '.mp3', 'name': 'MP3 Audio (no ID3)', 'trailer': None},
            '664C6143': {'ext': '.flac', 'name': 'FLAC Audio', 'trailer': None},
            '4F676753': {'ext': '.ogg', 'name': 'OGG Audio', 'trailer': None},
            '52494646': {'ext': '.wav', 'name': 'WAV Audio', 'trailer': None},
            '3C3F786D6C': {'ext': '.xml', 'name': 'XML Document', 'trailer': None},
            '3C68746D6C': {'ext': '.html', 'name': 'HTML Document', 'trailer': None},
            '7B5C727466': {'ext': '.rtf', 'name': 'RTF Document', 'trailer': None},
            'D0CF11E0A1B11AE1': {'ext': '.doc', 'name': 'MS Office Document', 'trailer': None},
            '504B030414000600': {'ext': '.docx', 'name': 'MS Word Document', 'trailer': '504B0506'},
            'CAFEBABE': {'ext': '.class', 'name': 'Java Class File', 'trailer': None},
            '4D5A': {'ext': '.exe', 'name': 'Windows Executable', 'trailer': None},
            '7F454C46': {'ext': '.elf', 'name': 'Linux Executable', 'trailer': None},
            '213C617263683E': {'ext': '.deb', 'name': 'Debian Package', 'trailer': None},
            'EDABEEDB': {'ext': '.rpm', 'name': 'RPM Package', 'trailer': None},
        }
        
        self.hex_data = ""
        self.recovered_files = []
        
        # إنشاء الواجهة
        self.create_widgets()
    
    def create_widgets(self):
        # الإطار الرئيسي
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # العنوان
        title_label = tk.Label(main_frame, text="نظام استعادة الملفات من الفلاش", 
                               font=('Arial', 20, 'bold'), bg='#2c3e50', fg='#ecf0f1')
        title_label.pack(pady=10)
        
        # إطار الأزرار العلوية
        button_frame = tk.Frame(main_frame, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        button_frame.pack(fill=tk.X, pady=5)
        
        # الأزرار الرئيسية
        btn_style = {'font': ('Arial', 11, 'bold'), 'bg': '#3498db', 'fg': 'white', 
                     'activebackground': '#2980b9', 'relief': tk.RAISED, 'borderwidth': 2,
                     'padx': 15, 'pady': 8}
        
        tk.Button(button_frame, text="📁 رفع ملف Hex", command=self.load_hex_file, **btn_style).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(button_frame, text="🔍 استخراج Header/Trailer", command=self.extract_headers_trailers, **btn_style).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(button_frame, text="📊 عرض البيانات المسترجعة", command=self.show_recovery_page, **btn_style).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(button_frame, text="💾 استعادة الملفات", command=self.recover_files, **btn_style).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(button_frame, text="🗑️ مسح البيانات", command=self.clear_data, **btn_style).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Notebook للصفحات المختلفة
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # تخصيص ستايل Notebook
        style = ttk.Style()
        style.configure('TNotebook', background='#34495e')
        style.configure('TNotebook.Tab', font=('Arial', 10, 'bold'), padding=[20, 10])
        
        # صفحة استخراج Header/Trailer
        self.extraction_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.notebook.add(self.extraction_frame, text='استخراج Header/Trailer/Block')
        self.create_extraction_page()
        
        # صفحة البيانات المسترجعة
        self.recovery_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.notebook.add(self.recovery_frame, text='البيانات المسترجعة')
        self.create_recovery_page()
        
        # صفحة Metadata
        self.metadata_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.notebook.add(self.metadata_frame, text='Metadata')
        self.create_metadata_page()
        
        # شريط الحالة
        self.status_bar = tk.Label(self.root, text="جاهز...", bg='#34495e', fg='#ecf0f1', 
                                   font=('Arial', 10), anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_extraction_page(self):
        # معلومات الملف المحمل
        info_frame = tk.LabelFrame(self.extraction_frame, text="معلومات الملف", 
                                   bg='#ecf0f1', font=('Arial', 12, 'bold'), fg='#2c3e50')
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.file_info_label = tk.Label(info_frame, text="لم يتم تحميل ملف", 
                                        bg='#ecf0f1', font=('Arial', 10), fg='#7f8c8d')
        self.file_info_label.pack(pady=10, padx=10)
        
        # جدول Headers/Trailers
        table_frame = tk.Frame(self.extraction_frame, bg='#ecf0f1')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrollbars
        tree_scroll_y = tk.Scrollbar(table_frame)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree_scroll_x = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        columns = ('رقم', 'نوع الملف', 'Header', 'Trailer', 'موقع Header', 'موقع Trailer', 'الحجم')
        self.extraction_tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                                           yscrollcommand=tree_scroll_y.set,
                                           xscrollcommand=tree_scroll_x.set)
        
        tree_scroll_y.config(command=self.extraction_tree.yview)
        tree_scroll_x.config(command=self.extraction_tree.xview)
        
        # تعريف الأعمدة
        for col in columns:
            self.extraction_tree.heading(col, text=col)
            self.extraction_tree.column(col, width=150, anchor=tk.CENTER)
        
        self.extraction_tree.pack(fill=tk.BOTH, expand=True)
        
        # تلوين الصفوف
        self.extraction_tree.tag_configure('oddrow', background='#d5dbdb')
        self.extraction_tree.tag_configure('evenrow', background='#ecf0f1')
    
    def create_recovery_page(self):
        # جدول الملفات المسترجعة
        table_frame = tk.Frame(self.recovery_frame, bg='#ecf0f1')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbars
        tree_scroll_y = tk.Scrollbar(table_frame)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree_scroll_x = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        columns = ('رقم الملف', 'اسم الملف', 'نوع الملف', 'Header', 'Trailer', 'Block Size', 'الحالة')
        self.recovery_tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                                         yscrollcommand=tree_scroll_y.set,
                                         xscrollcommand=tree_scroll_x.set)
        
        tree_scroll_y.config(command=self.recovery_tree.yview)
        tree_scroll_x.config(command=self.recovery_tree.xview)
        
        for col in columns:
            self.recovery_tree.heading(col, text=col)
            self.recovery_tree.column(col, width=150, anchor=tk.CENTER)
        
        self.recovery_tree.pack(fill=tk.BOTH, expand=True)
        
        self.recovery_tree.tag_configure('recovered', background='#2ecc71', foreground='white')
        self.recovery_tree.tag_configure('pending', background='#f39c12', foreground='white')
    
    def create_metadata_page(self):
        # عرض Metadata
        metadata_text_frame = tk.Frame(self.metadata_frame, bg='#ecf0f1')
        metadata_text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(metadata_text_frame, text="Metadata المسترجعة", 
                bg='#ecf0f1', font=('Arial', 14, 'bold'), fg='#2c3e50').pack(pady=5)
        
        self.metadata_text = scrolledtext.ScrolledText(metadata_text_frame, 
                                                       font=('Courier', 10), 
                                                       bg='#2c3e50', fg='#00ff00',
                                                       wrap=tk.WORD)
        self.metadata_text.pack(fill=tk.BOTH, expand=True)
    
    def load_hex_file(self):
        file_path = filedialog.askopenfilename(
            title="اختر ملف Hex",
            filetypes=[("Text files", "*.txt"), ("Hex files", "*.hex"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # تنظيف البيانات - إزالة المسافات والأسطر الجديدة
                self.hex_data = re.sub(r'[^0-9A-Fa-f]', '', content).upper()
                
                file_size = len(self.hex_data) // 2  # بالبايت
                
                info_text = f"الملف: {os.path.basename(file_path)}\n"
                info_text += f"الحجم: {file_size:,} بايت ({file_size/1024:.2f} KB)\n"
                info_text += f"طول البيانات: {len(self.hex_data):,} حرف hex"
                
                self.file_info_label.config(text=info_text, fg='#27ae60')
                self.status_bar.config(text=f"تم تحميل الملف: {os.path.basename(file_path)}")
                
                messagebox.showinfo("نجاح", "تم تحميل ملف Hex بنجاح!")
                
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل تحميل الملف:\n{str(e)}")
                self.status_bar.config(text="فشل التحميل")
    
    def extract_headers_trailers(self):
        if not self.hex_data:
            messagebox.showwarning("تحذير", "يرجى تحميل ملف Hex أولاً!")
            return
        
        # مسح الجدول
        for item in self.extraction_tree.get_children():
            self.extraction_tree.delete(item)
        
        self.recovered_files = []
        file_count = 0
        
        # البحث عن كل نوع ملف
        for header, file_info in self.file_signatures.items():
            positions = self.find_all_occurrences(self.hex_data, header)
            
            for pos in positions:
                file_count += 1
                
                # البحث عن Trailer
                trailer = file_info.get('trailer')
                trailer_pos = -1
                file_size = 0
                
                if trailer:
                    # البحث عن أقرب trailer بعد header
                    trailer_positions = self.find_all_occurrences(self.hex_data[pos:], trailer)
                    if trailer_positions:
                        trailer_pos = pos + trailer_positions[0] + len(trailer)
                        file_size = (trailer_pos - pos) // 2
                else:
                    # إذا لم يكن هناك trailer معروف، نحاول تقدير الحجم
                    # بالبحث عن header التالي
                    next_pos = len(self.hex_data)
                    for next_header in self.file_signatures.keys():
                        next_positions = self.find_all_occurrences(self.hex_data[pos+len(header):], next_header)
                        if next_positions and (pos + len(header) + next_positions[0]) < next_pos:
                            next_pos = pos + len(header) + next_positions[0]
                    
                    trailer_pos = next_pos
                    file_size = (next_pos - pos) // 2
                
                # إضافة إلى الجدول
                tag = 'evenrow' if file_count % 2 == 0 else 'oddrow'
                
                self.extraction_tree.insert('', tk.END, values=(
                    file_count,
                    file_info['name'],
                    header,
                    trailer if trailer else 'غير معروف',
                    f"0x{pos:08X}",
                    f"0x{trailer_pos:08X}" if trailer_pos != -1 else 'N/A',
                    f"{file_size:,} bytes"
                ), tags=(tag,))
                
                # حفظ معلومات الملف
                self.recovered_files.append({
                    'number': file_count,
                    'type': file_info['name'],
                    'extension': file_info['ext'],
                    'header': header,
                    'trailer': trailer,
                    'start_pos': pos,
                    'end_pos': trailer_pos,
                    'size': file_size,
                    'data': self.hex_data[pos:trailer_pos] if trailer_pos != -1 else None
                })
        
        self.status_bar.config(text=f"تم اكتشاف {file_count} ملف")
        
        if file_count > 0:
            messagebox.showinfo("نجاح", f"تم اكتشاف {file_count} ملف!")
            self.update_metadata()
        else:
            messagebox.showinfo("معلومات", "لم يتم العثور على ملفات قابلة للاستعادة")
    
    def find_all_occurrences(self, data, pattern):
        """البحث عن جميع مواقع pattern في data"""
        positions = []
        start = 0
        
        while True:
            pos = data.find(pattern, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1
        
        return positions
    
    def show_recovery_page(self):
        # مسح الجدول
        for item in self.recovery_tree.get_children():
            self.recovery_tree.delete(item)
        
        # إضافة الملفات المسترجعة
        for file_info in self.recovered_files:
            tag = 'recovered' if file_info.get('data') else 'pending'
            
            self.recovery_tree.insert('', tk.END, values=(
                file_info['number'],
                f"file_{file_info['number']}{file_info['extension']}",
                file_info['type'],
                file_info['header'],
                file_info['trailer'] if file_info['trailer'] else 'N/A',
                f"{file_info['size']:,} bytes",
                'جاهز للاستعادة' if file_info.get('data') else 'غير مكتمل'
            ), tags=(tag,))
        
        self.notebook.select(self.recovery_frame)
        self.status_bar.config(text=f"عرض {len(self.recovered_files)} ملف")
    
    def recover_files(self):
        if not self.recovered_files:
            messagebox.showwarning("تحذير", "لا توجد ملفات للاستعادة!")
            return
        
        # اختيار مجلد الحفظ
        save_dir = filedialog.askdirectory(title="اختر مجلد لحفظ الملفات المستعادة")
        
        if not save_dir:
            return
        
        recovered_count = 0
        
        for file_info in self.recovered_files:
            if not file_info.get('data'):
                continue
            
            try:
                # إنشاء مجلد لكل نوع ملف
                ext = file_info['extension'].replace('.', '')
                type_dir = os.path.join(save_dir, ext.upper())
                os.makedirs(type_dir, exist_ok=True)
                
                # حفظ الملف
                filename = f"recovered_{file_info['number']}{file_info['extension']}"
                filepath = os.path.join(type_dir, filename)
                
                # تحويل hex إلى binary
                binary_data = bytes.fromhex(file_info['data'])
                
                with open(filepath, 'wb') as f:
                    f.write(binary_data)
                
                # حفظ hex أيضاً
                hex_filename = f"recovered_{file_info['number']}_hex.txt"
                hex_filepath = os.path.join(type_dir, hex_filename)
                
                with open(hex_filepath, 'w') as f:
                    f.write(file_info['data'])
                
                recovered_count += 1
                
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل حفظ الملف {file_info['number']}:\n{str(e)}")
        
        self.status_bar.config(text=f"تم استعادة {recovered_count} ملف")
        messagebox.showinfo("نجاح", f"تم استعادة {recovered_count} ملف بنجاح!\n\nتم الحفظ في:\n{save_dir}")
    
    def update_metadata(self):
        metadata = {
            'total_files': len(self.recovered_files),
            'file_types': {},
            'total_size': 0
        }
        
        for file_info in self.recovered_files:
            file_type = file_info['type']
            if file_type not in metadata['file_types']:
                metadata['file_types'][file_type] = {'count': 0, 'total_size': 0}
            
            metadata['file_types'][file_type]['count'] += 1
            metadata['file_types'][file_type]['total_size'] += file_info['size']
            metadata['total_size'] += file_info['size']
        
        # عرض Metadata
        self.metadata_text.delete(1.0, tk.END)
        
        text = "=" * 60 + "\n"
        text += "تقرير Metadata للملفات المسترجعة\n"
        text += "=" * 60 + "\n\n"
        
        text += f"إجمالي الملفات: {metadata['total_files']}\n"
        text += f"إجمالي الحجم: {metadata['total_size']:,} bytes ({metadata['total_size']/1024:.2f} KB)\n\n"
        
        text += "تفصيل أنواع الملفات:\n"
        text += "-" * 60 + "\n"
        
        for file_type, info in metadata['file_types'].items():
            text += f"\n{file_type}:\n"
            text += f"  العدد: {info['count']}\n"
            text += f"  الحجم الإجمالي: {info['total_size']:,} bytes ({info['total_size']/1024:.2f} KB)\n"
            text += f"  متوسط الحجم: {info['total_size']/info['count']:.2f} bytes\n"
        
        text += "\n" + "=" * 60 + "\n"
        text += "تفاصيل كل ملف:\n"
        text += "=" * 60 + "\n"
        
        for file_info in self.recovered_files:
            text += f"\nملف #{file_info['number']}:\n"
            text += f"  النوع: {file_info['type']}\n"
            text += f"  الامتداد: {file_info['extension']}\n"
            text += f"  Header: {file_info['header']}\n"
            text += f"  Trailer: {file_info['trailer'] if file_info['trailer'] else 'غير معروف'}\n"
            text += f"  الموقع: 0x{file_info['start_pos']:08X} - 0x{file_info['end_pos']:08X}\n"
            text += f"  الحجم: {file_info['size']:,} bytes\n"
            text += f"  الحالة: {'مكتمل' if file_info.get('data') else 'غير مكتمل'}\n"
        
        self.metadata_text.insert(1.0, text)
    
    def clear_data(self):
        if messagebox.askyesno("تأكيد", "هل أنت متأكد من مسح جميع البيانات؟"):
            self.hex_data = ""
            self.recovered_files = []
            
            for item in self.extraction_tree.get_children():
                self.extraction_tree.delete(item)
            
            for item in self.recovery_tree.get_children():
                self.recovery_tree.delete(item)
            
            self.metadata_text.delete(1.0, tk.END)
            self.file_info_label.config(text="لم يتم تحميل ملف", fg='#7f8c8d')
            self.status_bar.config(text="تم مسح البيانات")
            
            messagebox.showinfo("نجاح", "تم مسح جميع البيانات بنجاح!")

# تشغيل البرنامج
if __name__ == "__main__":
    root = tk.Tk()
    app = FileRecoveryApp(root)
    root.mainloop()