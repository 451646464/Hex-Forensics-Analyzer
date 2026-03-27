import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import time
import hashlib
import struct
from pathlib import Path

# Modern color scheme
BG_COLOR = "#1e1e2e"
CARD_BG = "#2a2a3e"
PRIMARY_COLOR = "#7e57c2"
SECONDARY_COLOR = "#42a5f5"
ACCENT_COLOR = "#ef5350"
SUCCESS_COLOR = "#66bb6a"
WARNING_COLOR = "#ffa726"
TEXT_COLOR = "#e2e2e2"
BORDER_COLOR = "#393952"

class AdvancedHexExtractor:
    def __init__(self):
        self.files_data = {}
        self.progress_callback = None

    def set_progress_callback(self, callback):
        self.progress_callback = callback

    def update_progress(self, message, percent=None):
        if self.progress_callback:
            self.progress_callback(message, percent)

    def clean_hex_data(self, hex_string):
        """تنظيف بيانات الهيكس"""
        self.update_progress("🔄 جاري تنظيف بيانات الهيكس...")
        
        if not hex_string:
            return ""
        
        # إزالة جميع الأحرف غير الهيكس
        hex_chars = "0123456789ABCDEFabcdef"
        cleaned = ''.join(c for c in hex_string if c in hex_chars)
        
        # التأكد من الطول الزوجي
        if len(cleaned) % 2 != 0:
            cleaned = cleaned[:-1]
            
        self.update_progress(f"✅ اكتمل التنظيف - {len(cleaned)//2} بايت")
        return cleaned.upper()

    def detect_files(self, hex_data):
        """اكتشاف الملفات في بيانات الهيكس مع تحسينات PDF"""
        self.update_progress("🔍 بدء اكتشاف الملفات...")
        
        files_found = []
        hex_data = hex_data.upper()
        position = 0
        total_length = len(hex_data)
        
        # توقيعات الملفات المحسنة
        signatures = [
            # الصور
            ('FFD8FF', 'JPG', self.find_jpg_end),
            ('89504E47', 'PNG', self.find_png_end),
            ('424D', 'BMP', self.find_bmp_end),
            
            # المستندات - تحسين PDF
            ('25504446', 'PDF', self.find_pdf_end),  # %PDF
            ('25504446', 'PDF', self.find_pdf_end),  # تأكيد إضافي
            
            # التنفيذيات
            ('4D5A', 'EXE', self.find_exe_end),
            ('4D5A', 'DLL', self.find_exe_end),
            
            # الصوت
            ('FFFB', 'MP3', self.find_mp3_end),
            ('FFF3', 'MP3', self.find_mp3_end),
            ('494433', 'MP3', self.find_mp3_id3_end),
            
            # الفيديو
            ('66747970', 'MP4', self.find_mp4_end),
            ('0000001866747970', 'MP4', self.find_mp4_end),
            ('6D6F6F76', 'MOV', self.find_mov_end),
        ]
        
        while position < total_length - 16:
            file_found = False
            
            for signature, file_type, find_end_func in signatures:
                sig_end = position + len(signature)
                if sig_end <= total_length and hex_data[position:sig_end] == signature:
                    # وجدنا توقيع ملف
                    end_pos = find_end_func(hex_data, position, total_length)
                    
                    if end_pos > position + 100:  # الحد الأدنى لحجم الملف
                        file_size = (end_pos - position) // 2
                        
                        file_info = {
                            'start': position,
                            'end': end_pos,
                            'type': file_type,
                            'signature': signature,
                            'size': file_size,
                            'valid_structure': True
                        }
                        
                        # التحقق من هيكل الملف
                        file_info['valid_structure'] = self.validate_file_structure(hex_data, position, end_pos, file_type)
                        
                        files_found.append(file_info)
                        
                        self.update_progress(f"✅ تم العثور على {file_type} - الحجم: {file_size:,} بايت")
                        position = end_pos
                        file_found = True
                        break
            
            if not file_found:
                position += 2

        self.update_progress(f"🎉 اكتمل الاكتشاف - تم العثور على {len(files_found)} ملف")
        return files_found

    def find_jpg_end(self, hex_data, start_pos, max_length):
        """البحث عن نهاية ملف JPEG"""
        # ابحث عن علامة نهاية JPEG FFD9
        end_pos = hex_data.find('FFD9', start_pos)
        if end_pos != -1:
            return end_pos + 4
        return min(start_pos + 5000000, max_length)

    def find_png_end(self, hex_data, start_pos, max_length):
        """البحث عن نهاية ملف PNG"""
        # ابحث عن chunk IEND في PNG
        end_pos = hex_data.find('49454E44AE426082', start_pos)
        if end_pos != -1:
            return end_pos + 16
        return min(start_pos + 50000000, max_length)

    def find_pdf_end(self, hex_data, start_pos, max_length):
        """البحث عن نهاية ملف PDF مع تحسينات"""
        # ابحث عن علامة %%EOF في PDF
        eof_pos = hex_data.find('2525454F46', start_pos)  # %%EOF
        if eof_pos != -1:
            return eof_pos + 10
        
        # إذا لم يتم العثور على %%EOF، ابحث عن بداية ملف آخر
        next_sigs = ['FFD8FF', '89504E47', '4D5A', '424D', 'FFFB', 'FFF3', '494433', '66747970', '6D6F6F76']
        for sig in next_sigs:
            pos = hex_data.find(sig, start_pos + 1000)
            if pos != -1:
                return pos
        
        # البحث عن نمط نهاية PDF البديل
        for i in range(start_pos + 1000, min(start_pos + 1000000, max_length), 2):
            if i + 20 <= max_length:
                # ابحث عن كلمات رئيسية في نهاية PDF
                chunk = hex_data[i:i+100]
                if '454F46' in chunk or '454E444F42' in chunk:  # EOF أو endobj
                    return i + 50
        
        return min(start_pos + 100000000, max_length)

    def find_mp3_end(self, hex_data, start_pos, max_length):
        """البحث عن نهاية ملف MP3"""
        next_sigs = ['FFD8FF', '89504E47', '25504446', '4D5A', '424D', '66747970', '6D6F6F76']
        for sig in next_sigs:
            pos = hex_data.find(sig, start_pos + 1000)
            if pos != -1:
                return pos
        return min(start_pos + 20000000, max_length)

    def find_mp3_id3_end(self, hex_data, start_pos, max_length):
        """البحث عن نهاية MP3 مع ID3v2"""
        if start_pos + 20 <= len(hex_data):
            try:
                size_bytes = hex_data[start_pos + 6:start_pos + 14]
                id3_size = int(size_bytes, 16)
                id3_size = (id3_size & 0x7F000000) >> 3 | (id3_size & 0x7F0000) >> 2 | (id3_size & 0x7F00) >> 1 | (id3_size & 0x7F)
                total_id3_size = 10 + id3_size
                return start_pos + (total_id3_size * 2)
            except:
                pass
        return self.find_mp3_end(hex_data, start_pos, max_length)

    def find_mp4_end(self, hex_data, start_pos, max_length):
        """البحث عن نهاية MP4"""
        return self.parse_mp4_atoms(hex_data, start_pos, max_length)

    def find_mov_end(self, hex_data, start_pos, max_length):
        """البحث عن نهاية MOV"""
        return self.parse_mp4_atoms(hex_data, start_pos, max_length)

    def parse_mp4_atoms(self, hex_data, start_pos, max_length):
        """تحليل ذرات MP4/MOV"""
        pos = start_pos
        max_file_size = 500000000
        
        while pos < min(start_pos + max_file_size * 2, max_length - 16):
            if pos + 16 > len(hex_data):
                break
                
            size_hex = hex_data[pos:pos+8]
            try:
                atom_size = int(size_hex, 16)
                if atom_size < 8 or atom_size > 1000000000:
                    break
                    
                pos += atom_size * 2
                
                if atom_size > 1000000:
                    break
                    
            except:
                break
        
        return min(pos, max_length)

    def find_bmp_end(self, hex_data, start_pos, max_length):
        """البحث عن نهاية BMP"""
        if start_pos + 8 <= len(hex_data):
            try:
                size_bytes = hex_data[start_pos + 4:start_pos + 12]
                bmp_size = int(size_bytes, 16)
                return start_pos + (bmp_size * 2)
            except:
                pass
        return min(start_pos + 10000000, max_length)

    def find_exe_end(self, hex_data, start_pos, max_length):
        """البحث عن نهاية EXE"""
        next_sigs = ['FFD8FF', '89504E47', '25504446', '424D', 'FFFB', 'FFF3', '494433', '66747970', '6D6F6F76']
        for sig in next_sigs:
            pos = hex_data.find(sig, start_pos + 1000)
            if pos != -1:
                return pos
        return min(start_pos + 50000000, max_length)

    def validate_file_structure(self, hex_data, start_pos, end_pos, file_type):
        """التحقق من هيكل الملف"""
        try:
            file_size = (end_pos - start_pos) // 2
            if file_size < 100:  # أقل من 100 بايت
                return False
                
            file_data = hex_data[start_pos:end_pos]
            
            # Comprehensive file signatures with offset checks
            signatures = {
                'PDF': [('25504446', 0)],  # %PDF at start
                'MP4': [('66747970', 4), ('6D6F6F76', None)],  # ftyp at 4, moov anywhere
                'MOV': [('66747970', 4), ('6D6F6F76', None)],  # same as MP4
                'JPG': [('FFD8FF', 0)],
                'PNG': [('89504E470D0A1A0A', 0)],
                'GIF': [('47494638', 0)],  # GIF8
                'BMP': [('424D', 0)],  # BM
                'MP3': [('FFFB', 0), ('FFF3', 0), ('FFE3', 0)],
                'WAV': [('52494646', 0), ('57415645', 8)],  # RIFF....WAVE
                'ZIP': [('504B0304', 0)],
                'EXE': [('4D5A', 0)],  # MZ
                'RAR': [('52617221', 0)],
                '7Z': [('377ABCAF271C', 0)],
                'DOCX': [('504B0304', 0), ('776F72642F', 30)],  # PK..word/
                'XLSX': [('504B0304', 0), ('786C2F', 30)],  # PK..xl/
                'PPTX': [('504B0304', 0), ('7070742F', 30)]  # PK..ppt/
            }
            
            if file_type in signatures:
                for sig, offset in signatures[file_type]:
                    if offset is not None:
                        if not file_data[offset:].startswith(sig):
                            return False
                    elif sig not in file_data:
                        return False
                return True
                
            return False  # Default to False for unknown types
        except:
            return False

    def extract_files(self, hex_data, file_boundaries):
        """استخراج الملفات الفردية مع التحليل المفصل"""
        self.update_progress("🔄 جاري استخراج الملفات...")
        
        extracted_files = {}
        
        for i, boundary in enumerate(file_boundaries):
            file_hex = hex_data[boundary['start']:boundary['end']]
            file_id = f"file_{i+1:03d}_{boundary['type']}"
            
            try:
                # حساب MD5
                file_bytes = bytes.fromhex(file_hex)
                file_md5 = hashlib.md5(file_bytes).hexdigest()
                
                # تحليل هيكل الملف
                header_info = self.analyze_header(file_hex, boundary['type'])
                trailer_info = self.analyze_trailer(file_hex, boundary['type'])
                blocks_info = self.analyze_blocks(file_hex, boundary['type'])
                
            except Exception as e:
                file_md5 = "غير متوفر"
                header_info = {"hex": "", "size": 0, "description": "خطأ"}
                trailer_info = {"hex": "", "size": 0, "description": "خطأ"}
                blocks_info = []
            
            file_data = {
                'hex_data': file_hex,
                'file_type': boundary['type'],
                'size_bytes': boundary['size'],
                'start_offset': boundary['start'],
                'end_offset': boundary['end'],
                'signature': boundary['signature'],
                'md5': file_md5,
                'valid_structure': boundary.get('valid_structure', True),
                'header_info': header_info,
                'trailer_info': trailer_info,
                'blocks_info': blocks_info
            }
            
            extracted_files[file_id] = file_data
            status = "✅" if file_data['valid_structure'] else "⚠️"
            self.update_progress(f"{status} تم استخراج: {file_id}")
        
        return extracted_files

    def analyze_header(self, hex_data, file_type):
        """تحليل رأس الملف"""
        header_sizes = {
            'JPG': 20, 'PNG': 8, 'PDF': 8, 'EXE': 2, 'DLL': 2,
            'BMP': 14, 'MP3': 10, 'MP4': 16, 'MOV': 16
        }
        
        size = header_sizes.get(file_type, 16)
        header_hex = hex_data[:min(size * 2, len(hex_data))]
        
        descriptions = {
            'JPG': 'رأس JPEG (FFD8FF)',
            'PNG': 'رأس PNG (89504E47)',
            'PDF': 'رأس PDF (%PDF)',
            'EXE': 'رأس EXE (MZ)',
            'DLL': 'رأس DLL (MZ)',
            'BMP': 'رأس BMP (BM)',
            'MP3': 'رأس MP3',
            'MP4': 'رأس MP4',
            'MOV': 'رأس MOV'
        }
        
        return {
            "hex": header_hex,
            "size": len(header_hex) // 2,
            "description": descriptions.get(file_type, "رأس الملف")
        }

    def analyze_trailer(self, hex_data, file_type):
        """تحليل ذيل الملف"""
        trailer_sizes = {
            'JPG': 4, 'PNG': 16, 'PDF': 10
        }
        
        size = trailer_sizes.get(file_type, 0)
        if size == 0 or len(hex_data) <= size * 2:
            return {"hex": "", "size": 0, "description": "لا يوجد ذيل"}
        
        trailer_hex = hex_data[-size * 2:]
        
        descriptions = {
            'JPG': 'نهاية JPEG (FFD9)',
            'PNG': 'نهاية PNG (IEND)',
            'PDF': 'نهاية PDF (%%EOF)'
        }
        
        return {
            "hex": trailer_hex,
            "size": size,
            "description": descriptions.get(file_type, "ذيل الملف")
        }

    def analyze_blocks(self, hex_data, file_type):
        """تحليل بلوكات الملف"""
        blocks = []
        
        if file_type == 'JPG':
            # تحليل مقاطع JPEG
            markers = [
                ('FFD8', 'بداية الصورة'),
                ('FFE0', 'مقطع APP0'),
                ('FFE1', 'مقطع APP1 (EXIF)'),
                ('FFDB', 'جدول الكم'),
                ('FFC0', 'بداية الإطار'),
                ('FFC2', 'بداية الإطار (تقدمي)'),
                ('FFDA', 'بداية المسح'),
                ('FFD9', 'نهاية الصورة')
            ]
            
            for marker, description in markers:
                pos = hex_data.find(marker)
                if pos != -1:
                    blocks.append({
                        'type': 'مقطع JPEG',
                        'position': pos // 2,
                        'hex': marker,
                        'description': description,
                        'size': len(marker) // 2
                    })
        
        elif file_type == 'PNG':
            # تحليل قطع PNG
            chunks = [
                ('49484452', 'IHDR - رأس الصورة'),
                ('504C5445', 'PLTE - اللوحة'),
                ('49444154', 'IDAT - بيانات الصورة'),
                ('49454E44', 'IEND - نهاية الصورة')
            ]
            
            for chunk, description in chunks:
                pos = hex_data.find(chunk)
                if pos != -1:
                    blocks.append({
                        'type': 'قطعة PNG',
                        'position': pos // 2,
                        'hex': chunk,
                        'description': description,
                        'size': len(chunk) // 2
                    })
        
        elif file_type == 'PDF':
            # تحليل كائنات PDF
            objects = [
                ('0A2525454F46', 'نهاية الملف'),
                ('2F547970652F50616765', 'نوع الصفحة'),
                ('2F4D65646961426F782F', 'مربع الوسائط'),
                ('73747265616D', 'بداية الدفق'),
                ('656E6473747265616D', 'نهاية الدفق')
            ]
            
            for obj, description in objects:
                pos = hex_data.find(obj)
                if pos != -1:
                    blocks.append({
                        'type': 'كائن PDF',
                        'position': pos // 2,
                        'hex': obj[:16] + '...' if len(obj) > 16 else obj,
                        'description': description,
                        'size': len(obj) // 2
                    })
        
        return blocks

    def rebuild_files(self, extracted_files, output_dir):
        """إعادة بناء الملفات مع تنظيم المجلدات"""
        self.update_progress("🔨 جاري إعادة بناء الملفات...")
        
        results = {
            'successful': [],
            'failed': [],
            'total': len(extracted_files)
        }
        
        # إنشاء المجلد الرئيسي
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # إنشاء مجلدات لأنواع الملفات
        file_types = set(file_data['file_type'] for file_data in extracted_files.values())
        for file_type in file_types:
            type_dir = Path(output_dir) / file_type
            type_dir.mkdir(exist_ok=True)
            
            # إنشاء مجلد للهيكس
            hex_dir = Path(output_dir) / "hex_files" / file_type
            hex_dir.mkdir(parents=True, exist_ok=True)
        
        for file_id, file_data in extracted_files.items():
            try:
                file_type = file_data['file_type']
                file_number = file_id.split('_')[1]
                
                # الحصول على الامتداد المناسب
                extensions = {
                    'JPG': '.jpg', 'PNG': '.png', 'PDF': '.pdf', 
                    'EXE': '.exe', 'DLL': '.dll', 'BMP': '.bmp', 
                    'MP3': '.mp3', 'MP4': '.mp4', 'MOV': '.mov'
                }
                ext = extensions.get(file_type, '.bin')
                
                # إنشاء اسم الملف
                filename = f"{file_number}_{file_type}{ext}"
                type_dir = Path(output_dir) / file_type
                file_path = type_dir / filename
                
                # تنظيف الهيكس وتحويله إلى بايتات
                hex_clean = ''.join(c for c in file_data['hex_data'] if c in '0123456789ABCDEF')
                if len(hex_clean) % 2 != 0:
                    hex_clean = hex_clean[:-1]
                
                file_bytes = bytes.fromhex(hex_clean)
                
                # حفظ الملف
                with open(file_path, 'wb') as f:
                    f.write(file_bytes)
                
                # حفظ ملف الهيكس
                hex_dir = Path(output_dir) / "hex_files" / file_type
                hex_filename = f"{file_number}_{file_type}.hex"
                hex_path = hex_dir / hex_filename
                
                with open(hex_path, 'w', encoding='utf-8') as f:
                    # كتابة معلومات الملف
                    f.write(f"# معلومات الملف\n")
                    f.write(f"# المعرف: {file_id}\n")
                    f.write(f"# النوع: {file_type}\n")
                    f.write(f"# الحجم: {file_data['size_bytes']:,} بايت\n")
                    f.write(f"# MD5: {file_data.get('md5', 'غير متوفر')}\n")
                    f.write(f"# التوقيع: {file_data['signature']}\n")
                    f.write(f"# الرأس: {file_data['header_info']['hex'][:64]}...\n")
                    f.write(f"# الذيل: {file_data['trailer_info']['hex']}\n")
                    f.write("#" + "-" * 50 + "\n\n")
                    
                    # كتابة بيانات الهيكس
                    hex_data = file_data['hex_data']
                    for i in range(0, len(hex_data), 64):
                        line = hex_data[i:i+64]
                        offset = i // 2
                        f.write(f"{offset:08X}: {line}\n")
                
                # التحقق من الملف
                if file_path.exists() and file_path.stat().st_size > 0:
                    results['successful'].append({
                        'file_id': file_id,
                        'filename': filename,
                        'path': str(file_path),
                        'hex_path': str(hex_path),
                        'size': len(file_bytes),
                        'type': file_type
                    })
                    
                    self.update_progress(f"✅ تم حفظ: {filename} ({len(file_bytes):,} بايت)")
                else:
                    raise Exception("فشل إنشاء الملف")
                
            except Exception as e:
                results['failed'].append({
                    'file_id': file_id,
                    'error': str(e)
                })
                self.update_progress(f"❌ فشل: {file_id} - {e}")
        
        self.update_progress(f"🎉 اكتملت إعادة البناء - {len(results['successful'])}/{results['total']} ملف")
        return results


class ProfessionalHexExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("أداة استخراج ملفات الهيكس المحترفة")
        self.root.geometry("1300x850")
        self.root.configure(bg=BG_COLOR)
        
        self.extractor = AdvancedHexExtractor()
        self.setup_gui()
        
        self.extractor.set_progress_callback(self.update_progress)

    def setup_gui(self):
        """إعداد واجهة المستخدم"""
        # الإطار الرئيسي
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # العنوان
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = tk.Label(
            header_frame,
            text="🔧 أداة استخراج ملفات الهيكس المحترفة",
            font=("Arial", 20, "bold"),
            fg=SECONDARY_COLOR,
            bg=BG_COLOR
        )
        title_label.pack(pady=5)
        
        subtitle_label = tk.Label(
            header_frame,
            text="استخرج الصور، PDF، الفيديو، الصوت، والملفات التنفيذية من بيانات الهيكس",
            font=("Arial", 12),
            fg=TEXT_COLOR,
            bg=BG_COLOR
        )
        subtitle_label.pack()
        
        # علامات التبويب
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # تبويب الإدخال
        input_tab = ttk.Frame(self.notebook)
        self.notebook.add(input_tab, text="📥 الإدخال")
        self.setup_input_tab(input_tab)
        
        # تبويب النتائج
        results_tab = ttk.Frame(self.notebook)
        self.notebook.add(results_tab, text="📊 النتائج")
        self.setup_results_tab(results_tab)
        
        # تبويب الإخراج
        output_tab = ttk.Frame(self.notebook)
        self.notebook.add(output_tab, text="🔨 الإخراج")
        self.setup_output_tab(output_tab)
        
        # وحدة التحكم
        console_frame = ttk.LabelFrame(main_frame, text="سجل المعالجة", padding="10")
        console_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        self.console = scrolledtext.ScrolledText(
            console_frame,
            height=8,
            bg=CARD_BG,
            fg=TEXT_COLOR,
            font=("Consolas", 9)
        )
        self.console.pack(fill=tk.BOTH, expand=True)
        self.console.config(state=tk.DISABLED)
        
        # شريط الحالة
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_var = tk.StringVar(value="جاهز")
        status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Arial", 9),
            fg=TEXT_COLOR,
            bg=BG_COLOR
        )
        status_label.pack(side=tk.LEFT)
        
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, length=200)
        progress_bar.pack(side=tk.RIGHT)

    def setup_input_tab(self, parent):
        """إعداد تبويب الإدخال"""
        # إدخال النص
        text_frame = ttk.LabelFrame(parent, text="لصق بيانات الهيكس", padding="15")
        text_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.hex_text = scrolledtext.ScrolledText(
            text_frame,
            height=15,
            bg=CARD_BG,
            fg=TEXT_COLOR,
            font=("Consolas", 10)
        )
        self.hex_text.pack(fill=tk.BOTH, expand=True)
        
        # الأزرار
        btn_frame = ttk.Frame(text_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        process_btn = tk.Button(
            btn_frame,
            text="🚀 معالجة البيانات",
            command=self.process_hex_data,
            bg=ACCENT_COLOR,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=8
        )
        process_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = tk.Button(
            btn_frame,
            text="🗑️ مسح",
            command=self.clear_input,
            bg=WARNING_COLOR,
            fg="white",
            font=("Arial", 10),
            padx=15
        )
        clear_btn.pack(side=tk.LEFT)
        
        # تحميل الملف
        file_frame = ttk.LabelFrame(parent, text="تحميل من ملف", padding="15")
        file_frame.pack(fill=tk.X, pady=10)
        
        file_input_frame = ttk.Frame(file_frame)
        file_input_frame.pack(fill=tk.X)
        
        self.file_path = tk.StringVar()
        file_entry = ttk.Entry(file_input_frame, textvariable=self.file_path, font=("Arial", 10))
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = tk.Button(
            file_input_frame,
            text="📂 تصفح",
            command=self.browse_file,
            bg=PRIMARY_COLOR,
            fg="white",
            font=("Arial", 10)
        )
        browse_btn.pack(side=tk.LEFT)
        
        load_btn = tk.Button(
            file_frame,
            text="📥 تحميل ومعالجة",
            command=self.load_file,
            bg=SUCCESS_COLOR,
            fg="white",
            font=("Arial", 10, "bold"),
            pady=8
        )
        load_btn.pack(fill=tk.X, pady=(10, 0))

    def setup_results_tab(self, parent):
        """إعداد تبويب النتائج"""
        # شجرة النتائج
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("id", "type", "size", "signature", "status")
        self.results_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
        
        # تعريف العناوين
        self.results_tree.heading("id", text="معرف الملف")
        self.results_tree.heading("type", text="النوع")
        self.results_tree.heading("size", text="الحجم (بايت)")
        self.results_tree.heading("signature", text="التوقيع")
        self.results_tree.heading("status", text="الحالة")
        
        # تعريف العرض
        self.results_tree.column("id", width=120)
        self.results_tree.column("type", width=80)
        self.results_tree.column("size", width=100)
        self.results_tree.column("signature", width=100)
        self.results_tree.column("status", width=80)
        
        # أشرطة التمرير
        v_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        h_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.results_tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # أزرار التحكم
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=10)
        
        analyze_btn = tk.Button(
            control_frame,
            text="🔍 تحليل الملف المحدد",
            command=self.analyze_file,
            bg=SECONDARY_COLOR,
            fg="white",
            font=("Arial", 10)
        )
        analyze_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        refresh_btn = tk.Button(
            control_frame,
            text="🔄 تحديث",
            command=self.refresh_results,
            bg=PRIMARY_COLOR,
            fg="white",
            font=("Arial", 10)
        )
        refresh_btn.pack(side=tk.LEFT)

    def setup_output_tab(self, parent):
        """إعداد تبويب الإخراج"""
        # إعدادات الإخراج
        settings_frame = ttk.LabelFrame(parent, text="إعدادات الإخراج", padding="15")
        settings_frame.pack(fill=tk.X, pady=10)
        
        # مجلد الإخراج
        dir_frame = ttk.Frame(settings_frame)
        dir_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(dir_frame, text="مجلد الإخراج:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        dir_input_frame = ttk.Frame(dir_frame)
        dir_input_frame.pack(fill=tk.X, pady=5)
        
        self.output_dir = tk.StringVar(value="الملفات_المستخرجة")
        dir_entry = ttk.Entry(dir_input_frame, textvariable=self.output_dir, font=("Arial", 10))
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        dir_browse_btn = tk.Button(
            dir_input_frame,
            text="📁 تصفح",
            command=self.browse_output_dir,
            bg=PRIMARY_COLOR,
            fg="white",
            font=("Arial", 9)
        )
        dir_browse_btn.pack(side=tk.LEFT)
        
        # أزرار الإجراء
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, pady=20)
        
        rebuild_btn = tk.Button(
            action_frame,
            text="🔨 إعادة بناء جميع الملفات",
            command=self.rebuild_files,
            bg=SUCCESS_COLOR,
            fg="white",
            font=("Arial", 12, "bold"),
            pady=10
        )
        rebuild_btn.pack(fill=tk.X, pady=5)
        
        save_hex_btn = tk.Button(
            action_frame,
            text="💾 حفظ ملفات الهيكس فقط",
            command=self.save_hex_files,
            bg=SECONDARY_COLOR,
            fg="white",
            font=("Arial", 10),
            pady=8
        )
        save_hex_btn.pack(fill=tk.X, pady=2)

    def update_progress(self, message, percent=None):
        """تحديث التقدم في الواجهة"""
        def update():
            self.console.config(state=tk.NORMAL)
            self.console.insert(tk.END, message + "\n")
            self.console.see(tk.END)
            self.console.config(state=tk.DISABLED)
            
            if percent is not None:
                self.progress_var.set(percent)
            
            self.status_var.set(message)
            self.root.update()
        
        self.root.after(0, update)

    def process_hex_data(self):
        """معالجة بيانات الهيكس المدخلة"""
        hex_data = self.hex_text.get("1.0", tk.END).strip()
        if not hex_data:
            messagebox.showerror("خطأ", "الرجاء إدخال بيانات الهيكس أولاً!")
            return
        
        self.start_processing(hex_data)

    def load_file(self):
        """تحميل ملف الهيكس"""
        file_path = self.file_path.get()
        if not file_path:
            file_path = filedialog.askopenfilename(
                title="اختر ملف الهيكس",
                filetypes=[("ملفات نصية", "*.txt"), ("جميع الملفات", "*.*")]
            )
            if not file_path:
                return
            self.file_path.set(file_path)
        
        if not os.path.exists(file_path):
            messagebox.showerror("خطأ", "الملف غير موجود!")
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                hex_data = f.read()
            
            self.start_processing(hex_data)
            
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في قراءة الملف: {e}")

    def start_processing(self, hex_data):
        """بدء المعالجة في thread منفصل"""
        self.update_progress("بدء معالجة بيانات الهيكس...")
        self.progress_var.set(0)
        
        def process():
            try:
                # تنظيف البيانات
                self.update_progress("جاري تنظيف بيانات الهيكس...")
                cleaned_hex = self.extractor.clean_hex_data(hex_data)
                
                if not cleaned_hex:
                    self.update_progress("❌ بيانات الهيكس فارغة أو غير صالحة!")
                    return
                
                # اكتشاف الملفات
                file_boundaries = self.extractor.detect_files(cleaned_hex)
                
                if not file_boundaries:
                    self.update_progress("❌ لم يتم العثور على أي ملفات في البيانات!")
                    return
                
                # استخراج الملفات
                self.extractor.files_data = self.extractor.extract_files(cleaned_hex, file_boundaries)
                
                self.update_progress(f"✅ اكتملت المعالجة - تم العثور على {len(file_boundaries)} ملف")
                
                # تحديث الواجهة
                self.root.after(0, self.refresh_results)
                self.root.after(0, lambda: self.notebook.select(1))  # الانتقال إلى تبويب النتائج
                
            except Exception as e:
                self.update_progress(f"❌ حدث خطأ: {str(e)}")
        
        threading.Thread(target=process, daemon=True).start()

    def refresh_results(self):
        """تحديث قائمة النتائج"""
        # مسح القائمة الحالية
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # إضافة الملفات الجديدة
        if hasattr(self.extractor, 'files_data') and self.extractor.files_data:
            for file_id, file_data in self.extractor.files_data.items():
                status = "✅ صالح" if file_data['valid_structure'] else "⚠️ يحتاج فحص"
                
                self.results_tree.insert("", tk.END, values=(
                    file_id,
                    file_data['file_type'],
                    f"{file_data['size_bytes']:,}",
                    file_data['signature'],
                    status
                ))

    def analyze_file(self):
        """تحليل ملف محدد"""
        selection = self.results_tree.selection()
        if not selection:
            messagebox.showinfo("معلومة", "الرجاء اختيار ملف أولاً!")
            return
        
        item = selection[0]
        file_id = self.results_tree.item(item)['values'][0]
        
        if file_id in self.extractor.files_data:
            file_data = self.extractor.files_data[file_id]
            self.show_file_details(file_id, file_data)

    def show_file_details(self, file_id, file_data):
        """عرض تفاصيل الملف"""
        details_window = tk.Toplevel(self.root)
        details_window.title(f"تفاصيل الملف: {file_id}")
        details_window.geometry("800x600")
        details_window.configure(bg=BG_COLOR)
        
        # إنشاء علامات التبويب
        detail_notebook = ttk.Notebook(details_window)
        detail_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # تبويب النظرة العامة
        overview_tab = ttk.Frame(detail_notebook)
        detail_notebook.add(overview_tab, text="📊 النظرة العامة")
        
        info_text = f"""
معلومات الملف:
──────────────
معرف الملف: {file_id}
نوع الملف: {file_data['file_type']}
الحجم: {file_data['size_bytes']:,} بايت
التوقيع: {file_data['signature']}
موقع البداية: 0x{file_data['start_offset']//2:08X}
موقع النهاية: 0x{file_data['end_offset']//2:08X}
MD5: {file_data.get('md5', 'غير متوفر')}
الهيكل: {'✅ صالح' if file_data['valid_structure'] else '⚠️ يحتاج فحص'}

معلومات الرأس:
─────────────
الوصف: {file_data['header_info']['description']}
الحجم: {file_data['header_info']['size']} بايت
الهيكس: {file_data['header_info']['hex'][:64]}...

معلومات الذيل:
─────────────
الوصف: {file_data['trailer_info']['description']}
الحجم: {file_data['trailer_info']['size']} بايت
الهيكس: {file_data['trailer_info']['hex']}
"""
        
        overview_text = scrolledtext.ScrolledText(
            overview_tab,
            bg=CARD_BG,
            fg=TEXT_COLOR,
            font=("Consolas", 10)
        )
        overview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        overview_text.insert(tk.END, info_text.strip())
        overview_text.config(state=tk.DISABLED)
        
        # تبويب البلوكات
        if file_data['blocks_info']:
            blocks_tab = ttk.Frame(detail_notebook)
            detail_notebook.add(blocks_tab, text="🧱 البلوكات")
            
            # إنشاء شجرة للبلوكات
            blocks_tree = ttk.Treeview(blocks_tab, columns=("type", "position", "hex", "description"), show="headings", height=10)
            
            blocks_tree.heading("type", text="النوع")
            blocks_tree.heading("position", text="الموقع")
            blocks_tree.heading("hex", text="الهيكس")
            blocks_tree.heading("description", text="الوصف")
            
            blocks_tree.column("type", width=100)
            blocks_tree.column("position", width=80)
            blocks_tree.column("hex", width=120)
            blocks_tree.column("description", width=200)
            
            for block in file_data['blocks_info']:
                blocks_tree.insert("", tk.END, values=(
                    block['type'],
                    f"0x{block['position']:08X}",
                    block['hex'],
                    block['description']
                ))
            
            blocks_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # تبويب معاينة الهيكس
        hex_tab = ttk.Frame(detail_notebook)
        detail_notebook.add(hex_tab, text="🔍 معاينة الهيكس")
        
        hex_preview = scrolledtext.ScrolledText(
            hex_tab,
            bg=CARD_BG,
            fg=TEXT_COLOR,
            font=("Consolas", 9)
        )
        hex_preview.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # عرض أول 2KB من بيانات الهيكس
        preview_data = file_data['hex_data'][:4096]
        hex_preview.insert(tk.END, preview_data)
        if len(file_data['hex_data']) > 4096:
            hex_preview.insert(tk.END, f"\n\n... [مقتطع - عرض 2KB من {len(file_data['hex_data'])//2:,} بايت إجمالاً]")
        hex_preview.config(state=tk.DISABLED)
        
        # زر الإغلاق
        close_btn = tk.Button(
            details_window,
            text="إغلاق",
            command=details_window.destroy,
            bg=ACCENT_COLOR,
            fg="white",
            font=("Arial", 10),
            pady=5
        )
        close_btn.pack(pady=10)

    def rebuild_files(self):
        """إعادة بناء الملفات"""
        if not hasattr(self.extractor, 'files_data') or not self.extractor.files_data:
            messagebox.showinfo("معلومة", "لا توجد ملفات لإعادة البناء!")
            return
        
        output_dir = self.output_dir.get()
        if not output_dir:
            messagebox.showerror("خطأ", "الرجاء تحديد مجلد الإخراج!")
            return
        
        def rebuild():
            try:
                results = self.extractor.rebuild_files(self.extractor.files_data, output_dir)
                
                message = f"تم إعادة بناء {len(results['successful'])} من {results['total']} ملف بنجاح!\n\n"
                message += f"✅ الملفات الناجحة: {len(results['successful'])}\n"
                message += f"❌ الملفات الفاشلة: {len(results['failed'])}\n\n"
                message += f"تم حفظ الملفات في:\n{output_dir}"
                
                self.root.after(0, lambda: messagebox.showinfo("نجاح", message))
                
                # فتح مجلد الإخراج
                if os.path.exists(output_dir):
                    os.startfile(output_dir)
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("خطأ", f"فشل إعادة البناء: {e}"))
        
        threading.Thread(target=rebuild, daemon=True).start()

    def save_hex_files(self):
        """حفظ ملفات الهيكس فقط"""
        if not hasattr(self.extractor, 'files_data') or not self.extractor.files_data:
            messagebox.showinfo("معلومة", "لا توجد ملفات لحفظها!")
            return
        
        output_dir = self.output_dir.get()
        if not output_dir:
            messagebox.showerror("خطأ", "الرجاء تحديد مجلد الإخراج!")
            return
        
        try:
            hex_dir = Path(output_dir) / "hex_files"
            hex_dir.mkdir(parents=True, exist_ok=True)
            
            saved_count = 0
            for file_id, file_data in self.extractor.files_data.items():
                file_type = file_data['file_type']
                file_number = file_id.split('_')[1]
                
                # إنشاء مجلد للنوع
                type_hex_dir = hex_dir / file_type
                type_hex_dir.mkdir(exist_ok=True)
                
                hex_filename = f"{file_number}_{file_type}.hex"
                hex_path = type_hex_dir / hex_filename
                
                with open(hex_path, 'w', encoding='utf-8') as f:
                    # كتابة معلومات الملف
                    f.write(f"# معلومات الملف\n")
                    f.write(f"# المعرف: {file_id}\n")
                    f.write(f"# النوع: {file_type}\n")
                    f.write(f"# الحجم: {file_data['size_bytes']:,} بايت\n")
                    f.write(f"# MD5: {file_data.get('md5', 'غير متوفر')}\n")
                    f.write(f"# التوقيع: {file_data['signature']}\n")
                    f.write(f"# الرأس: {file_data['header_info']['hex'][:64]}...\n")
                    f.write(f"# الذيل: {file_data['trailer_info']['hex']}\n")
                    f.write("#" + "-" * 50 + "\n\n")
                    
                    # كتابة بيانات الهيكس
                    hex_data = file_data['hex_data']
                    for i in range(0, len(hex_data), 64):
                        line = hex_data[i:i+64]
                        offset = i // 2
                        f.write(f"{offset:08X}: {line}\n")
                
                saved_count += 1
            
            messagebox.showinfo("نجاح", f"تم حفظ {saved_count} ملف هيكس!")
            os.startfile(hex_dir)
            
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل حفظ الملفات: {e}")

    def browse_file(self):
        """تصفح لاختيار ملف"""
        file_path = filedialog.askopenfilename(
            title="اختر ملف الهيكس",
            filetypes=[("ملفات نصية", "*.txt"), ("جميع الملفات", "*.*")]
        )
        if file_path:
            self.file_path.set(file_path)

    def browse_output_dir(self):
        """تصفح لاختيار مجلد الإخراج"""
        directory = filedialog.askdirectory(title="اختر مجلد الإخراج")
        if directory:
            self.output_dir.set(directory)

    def clear_input(self):
        """مسح الإدخال"""
        self.hex_text.delete("1.0", tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = ProfessionalHexExtractorGUI(root)
    root.mainloop()