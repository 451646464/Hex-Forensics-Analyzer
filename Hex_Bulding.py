# import re
# import os
# import hashlib
# import json
# import time
# import threading
# import concurrent.futures
# from threading import Lock
# from queue import Queue
# from pathlib import Path

# class MultiFileHexParser:
#     def __init__(self):
#         self.files_data = {}
#         self.extraction_history = {}
#         self.progress_callback = None

#     def set_progress_callback(self, callback):
#         """تعيين دالة للاتصال بتحديثات التقدم"""
#         self.progress_callback = callback

#     def update_progress(self, message, percent=None):
#         """تحديث تقدم المعالجة"""
#         if self.progress_callback:
#             self.progress_callback(message, percent)

#     def clean_hex_data(self, hex_string):
#         """تنظيف بيانات الهيكس"""
#         import time
#         start_time = time.time()
#         self.update_progress("⏳ جاري تنظيف بيانات الهيكس...")
        
#         if not hex_string:
#             self.update_progress("تحذير: سلسلة الهيكس المدخلة فارغة!")
#             return ""
            
#         self.update_progress(f"سلسلة الهيكس المدخلة: {len(hex_string)} حرف")
        
#         # تحقق من نسبة أحرف الهيكس في البيانات
#         hex_chars = set("0123456789ABCDEFabcdef")
#         hex_count = sum(1 for c in hex_string if c in hex_chars)
#         hex_ratio = hex_count / max(1, len(hex_string))
        
#         self.update_progress(f"نسبة أحرف الهيكس: {hex_ratio:.2%}")
        
#         if hex_ratio < 0.3:
#             self.update_progress("تحذير: الإدخال قد لا يكون بيانات هيكس صالحة!")
#         elif hex_ratio > 0.9:
#             self.update_progress("جيد: الإدخال يبدو كبيانات هيكس صالحة.")
        
#         # إزالة جميع الأحرف غير الهيكس
#         cleaned = ''.join(char for char in hex_string if char in hex_chars)
        
#         # تأكد من الطول الزوجي
#         if len(cleaned) % 2 != 0:
#             cleaned = cleaned[:-1]
        
#         elapsed = time.time() - start_time
#         self.update_progress(f"✅ اكتمل تنظيف الهيكس في {elapsed:.2f} ثانية. تمت معالجة {len(cleaned)} حرف.")
        
#         return cleaned.upper()

#     def detect_file_boundaries(self, combined_hex):
#         """الكشف التلقائي عن حدود الملفات من الهيكس المدمج"""
#         import time
#         start_time = time.time()
#         self.update_progress("⏳ بدء الكشف عن حدود الملفات...")
        
#         boundaries = []

#         # توقيعات الملفات لأنواع الملفات المطلوبة فقط
#         file_signatures = {
#             # الصور
#             'JPG': ['FFD8FF'],  # JPEG
#             'PNG': ['89504E47'],  # PNG
#             'BMP': ['424D'],  # BMP
            
#             # المستندات
#             'PDF': ['25504446'],  # %PDF
            
#             # الملفات التنفيذية
#             'EXE': ['4D5A'],  # MZ
#             'DLL': ['4D5A'],  # MZ
            
#             # الصوت
#             'MP3': ['FFFB', 'FFF3', 'FFE3', '494433'],  # MP3 with ID3
            
#             # الفيديو
#             'MP4': ['0000001866747970', '0000002066747970', '66747970'],  # MP4
#             'MOV': ['6D6F6F76', '66747970'],  # QuickTime
            
#             # النص
#             'TXT': [],  # سيتم الكشف عن طريق تحليل المحتوى النصي
#         }

#         # تحويل إلى حروف كبيرة
#         combined_hex = combined_hex.upper()
#         hex_length = len(combined_hex)
        
#         self.update_progress(f"طول بيانات الهيكس: {hex_length} حرف ({hex_length // 2} بايت)")
        
#         # إنشاء قائمة المؤشرات المحتملة
#         potential_markers = {}
#         for ftype, signatures in file_signatures.items():
#             for signature in signatures:
#                 if signature and len(signature) >= 2:
#                     marker = signature[:2]
#                     if marker not in potential_markers:
#                         potential_markers[marker] = []
#                     potential_markers[marker].append((signature, ftype))
        
#         current_pos = 0
#         last_report_time = time.time()
#         signature_found_count = 0
        
#         self.update_progress(f"🔍 بدء المسح العميق مع {len(potential_markers)} مؤشر توقيع...")
        
#         while current_pos < hex_length - 8:  # تأكد من وجود مساحة كافية للتوقيعات
#             # عرض التقدم
#             current_time = time.time()
#             percent_done = int((current_pos / hex_length) * 100)
            
#             if current_time - last_report_time > 0.5:
#                 self.update_progress(f"⏳ تقدم الكشف: {percent_done}% ({current_pos//2}/{hex_length//2} بايت)", percent_done)
#                 last_report_time = current_time
            
#             # التحقق من التوقيعات السريعة الشائعة
#             quick_checks = [
#                 ('FFD8FF', 'JPG'), 
#                 ('89504E47', 'PNG'), 
#                 ('25504446', 'PDF'),
#                 ('4D5A', 'EXE/DLL'),
#                 ('424D', 'BMP'),
#                 ('FFFB', 'MP3'),
#                 ('FFF3', 'MP3'),
#                 ('494433', 'MP3'),
#                 ('66747970', 'MP4/MOV'),
#                 ('6D6F6F76', 'MOV')
#             ]
            
#             for sig_check, ftype_check in quick_checks:
#                 if current_pos + len(sig_check) <= hex_length:
#                     if combined_hex[current_pos:current_pos+len(sig_check)] == sig_check:
#                         # تحقق مما إذا كان هذا التوقيع جديداً
#                         is_new = True
#                         min_distance = 1024  # 512 بايت كحد أدنى للمسافة بين الملفات من نفس النوع
                        
#                         for existing in boundaries:
#                             if existing['file_type'] == ftype_check and abs(current_pos - existing['start']) < min_distance:
#                                 is_new = False
#                                 break
                        
#                         if is_new:
#                             # تحديد النوع الدقيق
#                             file_type = ftype_check
#                             if ftype_check == 'EXE/DLL':
#                                 # محاولة التمييز بين EXE و DLL (صعب عادة، نستخدم EXE كافتراضي)
#                                 file_type = 'EXE'
                            
#                             self.update_progress(f"اكتشاف سريع: تم العثور على {file_type} عند 0x{current_pos//2:X}")
                            
#                             # إنشاء حد ملف جديد
#                             boundary = {
#                                 'start': current_pos,
#                                 'end': None,
#                                 'signature': sig_check,
#                                 'file_type': file_type,
#                                 'size_hex': 0
#                             }
#                             boundaries.append(boundary)
#                             signature_found_count += 1
            
#             # التحقق من وجود مؤشر محتمل
#             if current_pos + 2 <= hex_length:
#                 current_marker = combined_hex[current_pos:current_pos+2]
#                 if current_marker in potential_markers:
#                     for signature, ftype in potential_markers[current_marker]:
#                         sig_len = len(signature)
#                         if current_pos + sig_len <= hex_length and combined_hex[current_pos:current_pos+sig_len] == signature:
                            
#                             # إنشاء حد ملف جديد
#                             should_add = True
                            
#                             # تحقق من التكرارات القريبة
#                             for existing in boundaries:
#                                 if existing['signature'] == signature and abs(current_pos - existing['start']) < 1024:
#                                     should_add = False
#                                     break
                            
#                             if should_add:
#                                 # تحديث نهاية الملف السابق
#                                 if boundaries:
#                                     boundaries[-1]['end'] = current_pos
#                                     boundaries[-1]['size_hex'] = current_pos - boundaries[-1]['start']
                                
#                                 boundary = {
#                                     'start': current_pos,
#                                     'end': None,
#                                     'signature': signature,
#                                     'file_type': ftype,
#                                     'size_hex': 0
#                                 }
#                                 boundaries.append(boundary)
                                
#                                 self.update_progress(f"تم العثور على توقيع {ftype} '{signature}' عند الموضع 0x{current_pos//2:X}")
#                                 signature_found_count += 1
                            
#                             current_pos += max(1, sig_len // 2)
#                             break
#                     else:
#                         current_pos += 1
#                 else:
#                     current_pos += 1
#             else:
#                 current_pos += 1

#         # الكشف عن الملفات النصية في المناطق غير المكتشفة
#         if len(boundaries) == 0 or len(boundaries) < 3:
#             self.update_progress("\n🔍 إجراء الكشف عن الملفات النصية في المناطق غير المكتشفة...")
#             text_boundaries = self.detect_text_files(combined_hex, boundaries)
#             boundaries.extend(text_boundaries)
        
#         # تحديث نهاية آخر ملف
#         if boundaries and boundaries[-1]['end'] is None:
#             boundaries[-1]['end'] = hex_length
#             boundaries[-1]['size_hex'] = hex_length - boundaries[-1]['start']

#         # فرز الحدود حسب الموضع
#         boundaries.sort(key=lambda x: x['start'])

#         elapsed = time.time() - start_time
        
#         # عرض النتائج النهائية
#         if len(boundaries) > 0:
#             self.update_progress(f"✅ اكتمل الكشف عن حدود الملفات في {elapsed:.2f} ثانية")
#             self.update_progress(f"📁 تم العثور على {len(boundaries)} ملف محتمل")
#             self.update_progress(f"📊 تم إجراء {signature_found_count} مطابقة توقيع")
            
#             # إحصائيات أنواع الملفات
#             file_types_found = {}
#             for b in boundaries:
#                 file_type = b['file_type']
#                 file_types_found[file_type] = file_types_found.get(file_type, 0) + 1
                
#             self.update_progress("\n📋 الملفات حسب النوع:")
#             for ftype, count in sorted(file_types_found.items(), key=lambda x: x[1], reverse=True):
#                 self.update_progress(f"   {ftype}: {count} ملفات")
                
#         else:
#             self.update_progress(f"⚠️ لم يتم العثور على توقيعات ملفات في {elapsed:.2f} ثانية!")
            
#         return boundaries

#     def detect_text_files(self, combined_hex, existing_boundaries):
#         """الكشف عن الملفات النصية في المناطق غير المكتشفة"""
#         text_boundaries = []
        
#         # إنشاء قائمة بالمناطق المكتشفة
#         discovered_regions = []
#         for boundary in existing_boundaries:
#             discovered_regions.append((boundary['start'], boundary['end']))
        
#         # فرز المناطق
#         discovered_regions.sort()
        
#         # البحث عن فجوات بين الملفات المكتشفة
#         current_pos = 0
#         for start, end in discovered_regions:
#             if start > current_pos:
#                 # هناك فجوة، نتحقق إذا كانت تحتوي على نص
#                 gap_size = start - current_pos
#                 if gap_size >= 100:  # على الأقل 50 بايت
#                     gap_hex = combined_hex[current_pos:start]
#                     try:
#                         gap_bytes = bytes.fromhex(gap_hex)
#                         text_analysis = self.analyze_text_content(gap_bytes)
                        
#                         if text_analysis['is_likely_text'] and text_analysis['printable_ratio'] > 0.8:
#                             text_boundary = {
#                                 'start': current_pos,
#                                 'end': start,
#                                 'signature': 'TEXT_CONTENT',
#                                 'file_type': 'TXT',
#                                 'size_hex': gap_size
#                             }
#                             text_boundaries.append(text_boundary)
#                             self.update_progress(f"تم العثور على ملف نصي (TXT) في الفجوة عند 0x{current_pos//2:X}")
                            
#                     except Exception as e:
#                         pass  # تجاهل الأخطاء في التحويل
                        
#             current_pos = max(current_pos, end)
        
#         # التحقق من المنطقة بعد آخر ملف
#         if current_pos < len(combined_hex):
#             remaining_hex = combined_hex[current_pos:]
#             if len(remaining_hex) >= 100:
#                 try:
#                     remaining_bytes = bytes.fromhex(remaining_hex)
#                     text_analysis = self.analyze_text_content(remaining_bytes)
                    
#                     if text_analysis['is_likely_text'] and text_analysis['printable_ratio'] > 0.8:
#                         text_boundary = {
#                             'start': current_pos,
#                             'end': len(combined_hex),
#                             'signature': 'TEXT_CONTENT',
#                             'file_type': 'TXT',
#                             'size_hex': len(remaining_hex)
#                         }
#                         text_boundaries.append(text_boundary)
#                         self.update_progress(f"تم العثور على ملف نصي (TXT) في النهاية: 0x{current_pos//2:X}")
                        
#                 except Exception as e:
#                     pass
        
#         return text_boundaries

#     def analyze_text_content(self, sample_bytes):
#         """تحليل المحتوى النصي"""
#         result = {
#             'is_likely_text': False,
#             'text_type': 'UNKNOWN',
#             'printable_ratio': 0.0,
#         }
        
#         if not sample_bytes:
#             return result
        
#         # حساب نسبة الأحرف القابلة للطباعة
#         printable_count = 0
#         control_count = 0
        
#         for b in sample_bytes:
#             if 32 <= b <= 126:  # ASCII printable
#                 printable_count += 1
#             elif b in [9, 10, 13]:  # tab, LF, CR
#                 printable_count += 1
#                 control_count += 1
#             else:
#                 control_count += 1
        
#         total_chars = len(sample_bytes)
#         result['printable_ratio'] = printable_count / total_chars if total_chars > 0 else 0
        
#         # تحديد إذا كان نصاً
#         if result['printable_ratio'] > 0.8:
#             result['is_likely_text'] = True
#             result['text_type'] = 'TXT'
        
#         return result

#     def extract_individual_files(self, combined_hex, boundaries):
#         """استخراج الملفات الفردية من الهيكس المدمج"""
#         self.update_progress("⏳ بدء استخراج الملفات...")
#         start_time = time.time()
        
#         results = {}
        
#         for i, boundary in enumerate(boundaries):
#             file_hex = combined_hex[boundary['start']:boundary['end']]
#             file_id = f"file_{i + 1}_{boundary['file_type']}"
            
#             file_data = {
#                 'hex_data': file_hex,
#                 'file_type': boundary['file_type'],
#                 'signature': boundary['signature'],
#                 'size_hex': boundary['size_hex'],
#                 'size_bytes': len(file_hex) // 2,
#                 'start_offset': boundary['start'],
#                 'end_offset': boundary['end']
#             }
            
#             results[file_id] = file_data
#             self.update_progress(f"✅ تم استخراج: {file_id} - {file_data['size_bytes']} بايت")
        
#         elapsed = time.time() - start_time
#         self.update_progress(f"✅ اكتمل الاستخراج لـ {len(results)} ملف في {elapsed:.2f} ثانية")
#         return results

#     def analyze_extracted_file(self, file_data):
#         """تحليل الملف المستخرج مع استخراج الهيدر والترايلر"""
#         hex_data = file_data['hex_data']
#         file_size_bytes = len(hex_data) // 2
        
#         self.update_progress(f"تحليل الملف: {file_data.get('file_type', 'غير معروف')} - {file_size_bytes} بايت")

#         # استخراج الهيدر والترايلر
#         header_info = self.detect_header(hex_data, file_data['file_type'])
#         trailer_info = self.detect_trailer(hex_data, file_data['file_type'])

#         header_hex = header_info['hex']
#         trailer_hex = trailer_info['hex']
        
#         # إنشاء تحليل ملف شامل
#         result = {
#             **file_data,
#             'header_hex': header_hex,
#             'trailer_hex': trailer_hex,
#             'header_size': header_info['size'],
#             'trailer_size': trailer_info['size'],
#             'header_info': header_info['info'],
#             'trailer_info': trailer_info['info'],
#             'md5': hashlib.md5(bytes.fromhex(hex_data)).hexdigest(),
#             'analysis_timestamp': time.time()
#         }
        
#         return result
        
#     def analyze_files_parallel(self, files_data):
#         """تحليل جميع الملفات المستخرجة"""
#         self.update_progress("⏳ بدء تحليل الملفات...")
#         start_time = time.time()
        
#         results = {}
        
#         for file_id, file_data in files_data.items():
#             analyzed_data = self.analyze_extracted_file(file_data)
#             results[file_id] = analyzed_data
#             self.update_progress(f"✅ تم تحليل: {file_id} - {analyzed_data['size_bytes']} بايت")
        
#         elapsed = time.time() - start_time
#         self.update_progress(f"✅ اكتمل تحليل {len(results)} ملف في {elapsed:.2f} ثانية")
#         return results

#     def detect_header(self, hex_data, file_type):
#         """كشف الهيدر بناءً على نوع الملف"""
#         header_info = {
#             'hex': '',
#             'size': 0,
#             'info': ''
#         }
        
#         if file_type == 'JPG':
#             # هيدر JPEG: FFD8FF
#             header_info['hex'] = hex_data[:6] if len(hex_data) >= 6 else hex_data
#             header_info['size'] = 3
#             header_info['info'] = 'JPEG Header (FFD8FF)'
            
#         elif file_type == 'PNG':
#             # هيدر PNG: 89504E470D0A1A0A
#             header_info['hex'] = hex_data[:16] if len(hex_data) >= 16 else hex_data
#             header_info['size'] = 8
#             header_info['info'] = 'PNG Header (89504E470D0A1A0A)'
            
#         elif file_type == 'BMP':
#             # هيدر BMP: 424D
#             header_info['hex'] = hex_data[:4] if len(hex_data) >= 4 else hex_data
#             header_info['size'] = 2
#             header_info['info'] = 'BMP Header (424D)'
            
#         elif file_type == 'PDF':
#             # هيدر PDF: 25504446
#             header_info['hex'] = hex_data[:8] if len(hex_data) >= 8 else hex_data
#             header_info['size'] = 4
#             header_info['info'] = 'PDF Header (%PDF)'
            
#         elif file_type in ['EXE', 'DLL']:
#             # هيدر EXE/DLL: 4D5A
#             header_info['hex'] = hex_data[:4] if len(hex_data) >= 4 else hex_data
#             header_info['size'] = 2
#             header_info['info'] = 'EXE/DLL Header (MZ)'
            
#         elif file_type == 'MP3':
#             # البحث عن هيدر MP3 (قد يكون ID3 أو frame sync)
#             if hex_data.startswith('494433'):  # ID3
#                 header_info['hex'] = hex_data[:10] if len(hex_data) >= 10 else hex_data
#                 header_info['size'] = 5
#                 header_info['info'] = 'MP3 ID3 Header'
#             else:
#                 # frame sync
#                 header_info['hex'] = hex_data[:4] if len(hex_data) >= 4 else hex_data
#                 header_info['size'] = 2
#                 header_info['info'] = 'MP3 Frame Sync'
                
#         elif file_type == 'MP4':
#             # البحث عن ftyp في MP4
#             ftyp_pos = hex_data.find('66747970')
#             if ftyp_pos != -1 and ftyp_pos < 20:
#                 header_info['hex'] = hex_data[ftyp_pos:ftyp_pos+32] if len(hex_data) >= ftyp_pos+32 else hex_data[ftyp_pos:]
#                 header_info['size'] = 16
#                 header_info['info'] = 'MP4 ftyp Header'
#             else:
#                 header_info['hex'] = hex_data[:16] if len(hex_data) >= 16 else hex_data
#                 header_info['size'] = 8
#                 header_info['info'] = 'MP4 Header'
                
#         elif file_type == 'MOV':
#             # هيدر MOV مشابه لـ MP4
#             ftyp_pos = hex_data.find('66747970')
#             if ftyp_pos != -1 and ftyp_pos < 20:
#                 header_info['hex'] = hex_data[ftyp_pos:ftyp_pos+32] if len(hex_data) >= ftyp_pos+32 else hex_data[ftyp_pos:]
#                 header_info['size'] = 16
#                 header_info['info'] = 'MOV ftyp Header'
#             else:
#                 header_info['hex'] = hex_data[:16] if len(hex_data) >= 16 else hex_data
#                 header_info['size'] = 8
#                 header_info['info'] = 'MOV Header'
                
#         elif file_type == 'TXT':
#             # للملفات النصية، نأخذ أول 100 بايت كهيدر
#             header_size = min(200, len(hex_data))
#             header_info['hex'] = hex_data[:header_size]
#             header_info['size'] = header_size // 2
#             header_info['info'] = 'Text Header'
            
#         else:
#             # افتراضي: أول 16 بايت
#             header_size = min(32, len(hex_data))
#             header_info['hex'] = hex_data[:header_size]
#             header_info['size'] = header_size // 2
#             header_info['info'] = 'Generic Header'
        
#         return header_info

#     def detect_trailer(self, hex_data, file_type):
#         """كشف الترايلر بناءً على نوع الملف"""
#         trailer_info = {
#             'hex': '',
#             'size': 0,
#             'info': ''
#         }
        
#         if file_type == 'JPG':
#             # ترايلر JPEG: FFD9
#             if hex_data.endswith('FFD9'):
#                 trailer_info['hex'] = hex_data[-4:]
#                 trailer_info['size'] = 2
#                 trailer_info['info'] = 'JPEG Trailer (FFD9)'
#             else:
#                 # إذا لم يكن هناك ترايلر صحيح، نأخذ آخر 4 بايت
#                 trailer_size = min(8, len(hex_data))
#                 trailer_info['hex'] = hex_data[-trailer_size:]
#                 trailer_info['size'] = trailer_size // 2
#                 trailer_info['info'] = 'JPEG End Data'
                
#         elif file_type == 'PNG':
#             # ترايلر PNG: IEND chunk
#             iend_pos = hex_data.find('49454E44AE426082')
#             if iend_pos != -1:
#                 trailer_info['hex'] = hex_data[iend_pos:iend_pos+16]
#                 trailer_info['size'] = 8
#                 trailer_info['info'] = 'PNG IEND Trailer'
#             else:
#                 trailer_size = min(16, len(hex_data))
#                 trailer_info['hex'] = hex_data[-trailer_size:]
#                 trailer_info['size'] = trailer_size // 2
#                 trailer_info['info'] = 'PNG End Data'
                
#         elif file_type == 'PDF':
#             # ترايلر PDF: %%EOF
#             eof_pos = hex_data.find('2525454F46')  # %%EOF
#             if eof_pos != -1:
#                 trailer_info['hex'] = hex_data[eof_pos:eof_pos+10]
#                 trailer_info['size'] = 5
#                 trailer_info['info'] = 'PDF EOF Trailer'
#             else:
#                 trailer_size = min(20, len(hex_data))
#                 trailer_info['hex'] = hex_data[-trailer_size:]
#                 trailer_info['size'] = trailer_size // 2
#                 trailer_info['info'] = 'PDF End Data'
                
#         elif file_type in ['EXE', 'DLL']:
#             # لا يوجد ترايلر ثابت لـ EXE/DLL، نأخذ آخر 16 بايت
#             trailer_size = min(32, len(hex_data))
#             trailer_info['hex'] = hex_data[-trailer_size:]
#             trailer_info['size'] = trailer_size // 2
#             trailer_info['info'] = 'EXE/DLL End Data'
            
#         elif file_type == 'MP3':
#             # لا يوجد ترايلر ثابت لـ MP3، نأخذ آخر 16 بايت
#             trailer_size = min(32, len(hex_data))
#             trailer_info['hex'] = hex_data[-trailer_size:]
#             trailer_info['size'] = trailer_size // 2
#             trailer_info['info'] = 'MP3 End Data'
            
#         elif file_type in ['MP4', 'MOV']:
#             # البحث عن moov atom في النهاية
#             moov_pos = hex_data.rfind('6D6F6F76')
#             if moov_pos != -1 and moov_pos > len(hex_data) - 100:
#                 trailer_info['hex'] = hex_data[moov_pos:moov_pos+32] if len(hex_data) >= moov_pos+32 else hex_data[moov_pos:]
#                 trailer_info['size'] = 16
#                 trailer_info['info'] = 'MP4/MOV moov Trailer'
#             else:
#                 trailer_size = min(32, len(hex_data))
#                 trailer_info['hex'] = hex_data[-trailer_size:]
#                 trailer_info['size'] = trailer_size // 2
#                 trailer_info['info'] = 'MP4/MOV End Data'
                
#         elif file_type == 'TXT':
#             # للملفات النصية، نأخذ آخر 100 بايت كترايلر
#             trailer_size = min(200, len(hex_data))
#             trailer_info['hex'] = hex_data[-trailer_size:]
#             trailer_info['size'] = trailer_size // 2
#             trailer_info['info'] = 'Text Trailer'
            
#         else:
#             # افتراضي: آخر 16 بايت
#             trailer_size = min(32, len(hex_data))
#             trailer_info['hex'] = hex_data[-trailer_size:]
#             trailer_info['size'] = trailer_size // 2
#             trailer_info['info'] = 'Generic Trailer'
        
#         return trailer_info

#     def rebuild_all_files(self, extracted_files, output_dir):
#         """إعادة بناء جميع الملفات المستخرجة"""
#         self.update_progress("⏳ بدء إعادة بناء الملفات...")
#         start_time = time.time()
        
#         results = {
#             'successful': [],
#             'failed': [],
#             'total_files': len(extracted_files),
#             'output_directory': output_dir
#         }

#         # إنشاء دليل الإخراج إذا لم يكن موجوداً
#         Path(output_dir).mkdir(parents=True, exist_ok=True)
        
#         # إنشاء أدلة لكل نوع ملف
#         file_types = set(file_data['file_type'] for file_data in extracted_files.values())
#         for file_type in file_types:
#             type_dir = os.path.join(output_dir, file_type)
#             Path(type_dir).mkdir(parents=True, exist_ok=True)
#             self.update_progress(f"تم إنشاء مجلد للنوع: {file_type}")
        
#         for file_id, file_data in extracted_files.items():
#             try:
#                 file_extension = self.get_file_extension(file_data['file_type'])
#                 file_type = file_data['file_type']
                
#                 # استخراج رقم الملف للتسمية المتسقة
#                 file_number = file_id.split('_')[1]
#                 formatted_number = f"{int(file_number):03d}"
                
#                 # إنشاء مسار دليل محدد للنوع
#                 type_dir = os.path.join(output_dir, file_type)
                
#                 # إنشاء اسم الملف مع الرقم المنسق
#                 filename = f"{formatted_number}_{file_type}{file_extension}"
#                 output_path = os.path.join(type_dir, filename)

#                 # تحضير بيانات الهيكس
#                 hex_data = file_data['hex_data']
                
#                 # تنظيف بيانات الهيكس
#                 hex_data = ''.join(c for c in hex_data if c in "0123456789ABCDEF")
#                 if len(hex_data) % 2 != 0:
#                     hex_data = hex_data[:-1]
                
#                 # التحويل إلى بايتات
#                 binary_data = bytes.fromhex(hex_data)
                
#                 # إعادة بناء الملف
#                 try:
#                     self.update_progress(f"كتابة ملف {file_type} إلى {output_path}, الحجم: {len(binary_data):,} بايت")
                    
#                     # تأكد من وجود المجلد المستهدف
#                     os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
#                     # احفظ الملف
#                     with open(output_path, 'wb') as f:
#                         f.write(binary_data)
                    
#                     # التحقق من صحة الملف
#                     if not os.path.exists(output_path):
#                         raise Exception(f"فشل في إنشاء الملف: {output_path}")
                        
#                     if os.path.getsize(output_path) == 0:
#                         raise Exception(f"تم إنشاء الملف لكنه فارغ: {output_path}")
                        
#                     # تأكد من صحة الملف
#                     self.update_progress(f"تمت كتابة ملف {file_type} بنجاح: {filename} ({os.path.getsize(output_path):,} بايت)")
#                 except Exception as e:
#                     raise Exception(f"خطأ في كتابة الملف: {str(e)}")

#                 file_info = {
#                     'file_id': file_id,
#                     'filename': filename,
#                     'output_path': output_path,
#                     'file_type': file_data['file_type'],
#                     'size_bytes': file_data['size_bytes'],
#                     'md5': file_data.get('md5', ''),
#                     'reconstructed': True
#                 }

#                 results['successful'].append(file_info)
#                 self.update_progress(f"✅ أعيد بناء: {filename} - {file_data['size_bytes']} بايت في مجلد {file_type}")

#             except Exception as e:
#                 results['failed'].append({
#                     'file_id': file_id,
#                     'error': str(e),
#                     'reconstructed': False
#                 })
#                 self.update_progress(f"❌ فشل في إعادة بناء: {file_id} - {str(e)}")
        
#         elapsed = time.time() - start_time
#         self.update_progress(f"✅ اكتملت إعادة بناء {len(results['successful'])} ملف من {results['total_files']} في {elapsed:.2f} ثانية")
#         return results

#     def get_file_extension(self, file_type):
#         """الحصول على امتداد الملف المناسب لنوع الملف"""
#         extensions = {
#             'JPG': '.jpg',
#             'PNG': '.png',
#             'BMP': '.bmp',
#             'PDF': '.pdf',
#             'EXE': '.exe',
#             'DLL': '.dll',
#             'MP3': '.mp3',
#             'MP4': '.mp4',
#             'MOV': '.mov',
#             'TXT': '.txt',
#         }
#         return extensions.get(file_type, '.bin')

#     def save_extraction_report(self, extracted_files, report_path):
#         """حفظ تقرير الاستخراج"""
#         report = {
#             'extraction_timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
#             'total_files': len(extracted_files),
#             'files': {}
#         }

#         # إنشاء نسخة قابلة للتسلسل من بيانات الملفات
#         for file_id, file_data in extracted_files.items():
#             serializable_data = file_data.copy()
#             report['files'][file_id] = serializable_data

#         with open(report_path, 'w', encoding='utf-8') as f:
#             json.dump(report, f, indent=2, ensure_ascii=False)
            
#     def save_hex_files(self, extracted_files, output_dir):
#         """حفظ كود الهيكس لكل ملف في ملفات نصية منظمة منفصلة"""
#         self.update_progress("⏳ بدء عملية حفظ ملفات الهيكس...")
#         start_time = time.time()
        
#         results = {
#             'successful': [],
#             'failed': [],
#             'total_files': len(extracted_files),
#             'output_directory': output_dir
#         }

#         # إنشاء دليل الإخراج الأساسي إذا لم يكن موجوداً
#         hex_base_dir = os.path.join(output_dir, "hex_files")
#         Path(hex_base_dir).mkdir(parents=True, exist_ok=True)
        
#         # إنشاء أدلة لكل نوع ملف
#         file_types = set(file_data['file_type'] for file_data in extracted_files.values())
#         for file_type in file_types:
#             type_dir = os.path.join(hex_base_dir, file_type)
#             Path(type_dir).mkdir(parents=True, exist_ok=True)
#             self.update_progress(f"تم إنشاء مجلد هيكس للنوع: {file_type}")
        
#         for file_id, file_data in extracted_files.items():
#             try:
#                 # استخراج رقم الملف من معرف الملف
#                 file_number = file_id.split('_')[1]
#                 file_type = file_data['file_type']
                
#                 # تنسيق رقم الملف للتسمية المتسقة
#                 formatted_number = f"{int(file_number):03d}"
                
#                 # إنشاء مسار دليل محدد للنوع
#                 type_dir = os.path.join(hex_base_dir, file_type)
                
#                 # إنشاء اسم الملف والمسار الكامل
#                 filename = f"{formatted_number}_{file_type}.hex"
#                 output_path = os.path.join(type_dir, filename)

#                 # حفظ بيانات الهيكس في ملف نصي
#                 with open(output_path, 'w', encoding='utf-8') as f:
#                     # إضافة بيانات وصفية في بداية الملف
#                     f.write(f"# رقم الملف: {formatted_number}\n")
#                     f.write(f"# النوع: {file_type}\n")
#                     f.write(f"# الحجم: {file_data['size_bytes']} بايت\n")
#                     f.write(f"# MD5: {file_data.get('md5', '')}\n")
#                     f.write(f"# الهيدر: {file_data.get('header_hex', '')[:64]}...\n")
#                     f.write(f"# الترايلر: {file_data.get('trailer_hex', '')[-64:] if file_data.get('trailer_hex') else 'N/A'}\n")
#                     f.write("#" + "-" * 50 + "\n\n")
                    
#                     # كتابة بيانات الهيكس في صفوف من 32 بايت
#                     hex_data = file_data['hex_data']
#                     for i in range(0, len(hex_data), 64):
#                         line = hex_data[i:i+64]
#                         offset = i // 2
#                         f.write(f"{offset:08X}: {line}\n")

#                 file_info = {
#                     'file_id': file_id,
#                     'filename': filename,
#                     'output_path': output_path,
#                     'file_type': file_data['file_type'],
#                     'size_bytes': file_data['size_bytes'],
#                     'hex_saved': True
#                 }

#                 results['successful'].append(file_info)
#                 self.update_progress(f"✅ تم حفظ الهيكس: {filename} - {file_data['size_bytes']} بايت في مجلد {file_type}")

#             except Exception as e:
#                 results['failed'].append({
#                     'file_id': file_id,
#                     'error': str(e),
#                     'hex_saved': False
#                 })
#                 self.update_progress(f"❌ فشل في حفظ الهيكس: {file_id} - {str(e)}")
        
#         elapsed = time.time() - start_time
#         self.update_progress(f"✅ اكتمل حفظ {len(results['successful'])} ملف هيكس من {results['total_files']} في {elapsed:.2f} ثانية")
#         return results


# def display_file_boundaries(boundaries):
#     """عرض حدود الملفات المكتشفة"""
#     print(f"\n🔍 حدود الملفات المكتشفة ({len(boundaries)} ملفات):")
#     print("=" * 80)

#     for i, boundary in enumerate(boundaries):
#         print(f"\n📄 الملف {i + 1}:")
#         print(f"   النوع: {boundary['file_type']}")
#         print(f"   البداية: {boundary['start']} (0x{boundary['start']//2:X})")
#         print(f"   النهاية: {boundary['end']} (0x{boundary['end']//2:X})")
#         print(f"   الحجم: {boundary['size_hex'] // 2} بايت")
#         print(f"   التوقيع: {boundary['signature']}")


# def display_extracted_files(extracted_files):
#     """عرض معلومات الملفات المستخرجة"""
#     print(f"\n✅ الملفات المستخرجة ({len(extracted_files)} ملفات):")
#     print("=" * 80)

#     for file_id, file_data in extracted_files.items():
#         print(f"\n📁 {file_id}:")
#         print(f"   النوع: {file_data['file_type']}")
#         print(f"   الحجم: {file_data['size_bytes']} بايت")
#         print(f"   الهيدر: {file_data.get('header_hex', '')[:32]}...")
#         print(f"   الترايلر: {file_data.get('trailer_hex', '')[:32]}...")
#         print(f"   MD5: {file_data.get('md5', '')}")


# def display_reconstruction_results(results):
#     """عرض نتائج إعادة البناء"""
#     print(f"\n🔨 نتائج إعادة البناء:")
#     print("=" * 80)
#     print(f"📁 المجلد: {results['output_directory']}")
#     print(f"📊 إجمالي الملفات: {results['total_files']}")
#     print(f"✅ الناجحة: {len(results['successful'])}")
#     print(f"❌ الفاشلة: {len(results['failed'])}")

#     if results['successful']:
#         print(f"\n📜 الملفات التي أعيد بناؤها بنجاح:")
#         for file_info in results['successful']:
#             print(f"   ✓ {file_info['filename']} - {file_info['size_bytes']} بايت - النوع: {file_info['file_type']}")

#     if results['failed']:
#         print(f"\n⚠️ الملفات التي فشل إعادة بنائها:")
#         for file_info in results['failed']:
#             print(f"   ✗ {file_info['file_id']}: {file_info['error']}")


# def main():
#     print("🔧 أداة استخراج وبناء ملفات الهيكس المتعددة")
#     print("=" * 60)

#     parser = MultiFileHexParser()

#     while True:
#         print("\n" + "=" * 50)
#         print("📋 الخيارات الرئيسية:")
#         print("1 - إدخال هيكس مدمج لملفات متعددة")
#         print("2 - تحميل هيكس مدمج من ملف")
#         print("3 - عرض الملفات المستخرجة")
#         print("4 - إعادة بناء جميع الملفات")
#         print("5 - حفظ تقرير الاستخراج")
#         print("6 - حفظ كود الهيكس لكل ملف في ملفات منفصلة")
#         print("0 - خروج")

#         choice = input("\nادخل اختيارك: ").strip()

#         if choice == '1':
#             print("\n📥 أدخل الهيكس المدمج لملفات متعددة:")
#             print("ملاحظة: سيتم الكشف عن حدود الملفات تلقائياً")
#             combined_hex = ""
#             while True:
#                 line = input()
#                 if line.strip().upper() == "END":
#                     break
#                 combined_hex += line

#             cleaned_hex = parser.clean_hex_data(combined_hex)
#             print(f"✅ تم تنظيف الهيكس: {len(cleaned_hex)} حرف")

#             # الكشف عن حدود الملفات
#             boundaries = parser.detect_file_boundaries(cleaned_hex)
#             display_file_boundaries(boundaries)

#             if boundaries:
#                 # استخراج الملفات الفردية
#                 parser.files_data = parser.extract_individual_files(cleaned_hex, boundaries)

#                 # تحليل جميع الملفات
#                 parser.files_data = parser.analyze_files_parallel(parser.files_data)

#                 display_extracted_files(parser.files_data)
#             else:
#                 print("❌ لم يتم العثور على ملفات في بيانات الإدخال")

#         elif choice == '2':
#             hex_file = input("أدخل مسار ملف الهيكس المدمج: ").strip()
#             if os.path.exists(hex_file):
#                 with open(hex_file, 'r', encoding='utf-8') as f:
#                     combined_hex = f.read()

#                 cleaned_hex = parser.clean_hex_data(combined_hex)
#                 print(f"✅ تم تحميل ملف الهيكس: {len(cleaned_hex)} حرف")

#                 boundaries = parser.detect_file_boundaries(cleaned_hex)
#                 display_file_boundaries(boundaries)

#                 if boundaries:
#                     parser.files_data = parser.extract_individual_files(cleaned_hex, boundaries)
#                     parser.files_data = parser.analyze_files_parallel(parser.files_data)
#                     display_extracted_files(parser.files_data)
#                 else:
#                     print("❌ لم يتم العثور على ملفات في ملف الإدخال")
#             else:
#                 print("❌ الملف غير موجود!")

#         elif choice == '3':
#             if not parser.files_data:
#                 print("❌ لم يتم استخراج أي ملفات بعد")
#             else:
#                 display_extracted_files(parser.files_data)

#         elif choice == '4':
#             if not parser.files_data:
#                 print("❌ لا توجد ملفات مستخرجة لإعادة البناء")
#                 continue

#             output_dir = input("أدخل مجلد الإخراج [الافتراضي: reconstructed_files]: ").strip()
#             if not output_dir:
#                 output_dir = "reconstructed_files"

#             results = parser.rebuild_all_files(parser.files_data, output_dir)
#             display_reconstruction_results(results)

#         elif choice == '5':
#             if not parser.files_data:
#                 print("❌ لا توجد بيانات للحفظ")
#                 continue

#             report_path = input("أدخل مسار التقرير [الافتراضي: extraction_report.json]: ").strip()
#             if not report_path:
#                 report_path = "extraction_report.json"

#             parser.save_extraction_report(parser.files_data, report_path)
#             print(f"✅ تم حفظ التقرير في: {report_path}")

#         elif choice == '6':
#             if not parser.files_data:
#                 print("❌ لا توجد ملفات مستخرجة لحفظ كود الهيكس")
#                 continue

#             output_dir = input("أدخل مجلد الإخراج [الافتراضي: hex_output]: ").strip()
#             if not output_dir:
#                 output_dir = "hex_output"

#             results = parser.save_hex_files(parser.files_data, output_dir)
            
#             print(f"\n💾 نتائج حفظ ملفات الهيكس:")
#             print("=" * 80)
#             print(f"📁 مجلد الإخراج: {os.path.join(results['output_directory'], 'hex_files')}")
#             print(f"📊 إجمالي الملفات: {results['total_files']}")
#             print(f"✅ الناجحة: {len(results['successful'])}")
#             print(f"❌ الفاشلة: {len(results['failed'])}")

#         elif choice == '0':
#             break
#         else:
#             print("❌ اختيار غير صحيح!")


# if __name__ == "__main__":
#     main()

import re
import os
import hashlib
import json
import time
import threading
import concurrent.futures
from threading import Lock
from queue import Queue
from pathlib import Path

class MultiFileHexParser:
    def __init__(self):
        self.files_data = {}
        self.extraction_history = {}
        self.progress_callback = None

    def set_progress_callback(self, callback):
        """Set callback function for progress updates"""
        self.progress_callback = callback

    def update_progress(self, message, percent=None):
        """Update processing progress"""
        if self.progress_callback:
            self.progress_callback(message, percent)

    def clean_hex_data(self, hex_string):
        """Clean hex data"""
        import time
        start_time = time.time()
        self.update_progress("⏳ Cleaning hex data...")
        
        if not hex_string:
            self.update_progress("Warning: Input hex string is empty!")
            return ""
            
        self.update_progress(f"Input hex string: {len(hex_string)} characters")
        
        # Check hex character ratio in data
        hex_chars = set("0123456789ABCDEFabcdef")
        hex_count = sum(1 for c in hex_string if c in hex_chars)
        hex_ratio = hex_count / max(1, len(hex_string))
        
        self.update_progress(f"Hex character ratio: {hex_ratio:.2%}")
        
        if hex_ratio < 0.3:
            self.update_progress("Warning: Input may not be valid hex data!")
        elif hex_ratio > 0.9:
            self.update_progress("Good: Input appears to be valid hex data.")
        
        # Remove all non-hex characters
        cleaned = ''.join(char for char in hex_string if char in hex_chars)
        
        # Ensure even length
        if len(cleaned) % 2 != 0:
            cleaned = cleaned[:-1]
        
        elapsed = time.time() - start_time
        self.update_progress(f"✅ Hex cleaning completed in {elapsed:.2f} seconds. Processed {len(cleaned)} characters.")
        
        return cleaned.upper()

    def detect_file_boundaries(self, combined_hex):
        """Automatic detection of file boundaries from combined hex"""
        import time
        start_time = time.time()
        self.update_progress("⏳ Starting file boundary detection...")
        
        boundaries = []

        # File signatures for required file types only
        file_signatures = {
            # Images
            'JPG': ['FFD8FF'],  # JPEG
            'PNG': ['89504E47'],  # PNG
            'BMP': ['424D'],  # BMP
            
            # Documents
            'PDF': ['25504446'],  # %PDF
            
            # Executables
            'EXE': ['4D5A'],  # MZ
            'DLL': ['4D5A'],  # MZ
            
            # Audio
            'MP3': ['FFFB', 'FFF3', 'FFE3', '494433'],  # MP3 with ID3
            
            # Video
            'MP4': ['0000001866747970', '0000002066747970', '66747970'],  # MP4
            'MOV': ['6D6F6F76', '66747970'],  # QuickTime
            
            # Text
            'TXT': [],  # Will be detected via content analysis
        }

        # Convert to uppercase
        combined_hex = combined_hex.upper()
        hex_length = len(combined_hex)
        
        self.update_progress(f"Hex data length: {hex_length} characters ({hex_length // 2} bytes)")
        
        # Create list of potential markers
        potential_markers = {}
        for ftype, signatures in file_signatures.items():
            for signature in signatures:
                if signature and len(signature) >= 2:
                    marker = signature[:2]
                    if marker not in potential_markers:
                        potential_markers[marker] = []
                    potential_markers[marker].append((signature, ftype))
        
        current_pos = 0
        last_report_time = time.time()
        signature_found_count = 0
        
        self.update_progress(f"🔍 Starting deep scan with {len(potential_markers)} signature markers...")
        
        while current_pos < hex_length - 8:  # Ensure enough space for signatures
            # Show progress
            current_time = time.time()
            percent_done = int((current_pos / hex_length) * 100)
            
            if current_time - last_report_time > 0.5:
                self.update_progress(f"⏳ Detection progress: {percent_done}% ({current_pos//2}/{hex_length//2} bytes)", percent_done)
                last_report_time = current_time
            
            # Check for quick common signatures
            quick_checks = [
                ('FFD8FF', 'JPG'), 
                ('89504E47', 'PNG'), 
                ('25504446', 'PDF'),
                ('4D5A', 'EXE/DLL'),
                ('424D', 'BMP'),
                ('FFFB', 'MP3'),
                ('FFF3', 'MP3'),
                ('494433', 'MP3'),
                ('66747970', 'MP4/MOV'),
                ('6D6F6F76', 'MOV')
            ]
            
            for sig_check, ftype_check in quick_checks:
                if current_pos + len(sig_check) <= hex_length:
                    if combined_hex[current_pos:current_pos+len(sig_check)] == sig_check:
                        # Check if this is a new signature
                        is_new = True
                        min_distance = 1024  # 512 bytes minimum distance between files of same type
                        
                        for existing in boundaries:
                            if existing['file_type'] == ftype_check and abs(current_pos - existing['start']) < min_distance:
                                is_new = False
                                break
                        
                        if is_new:
                            # Determine exact type
                            file_type = ftype_check
                            if ftype_check == 'EXE/DLL':
                                # Try to distinguish between EXE and DLL (usually difficult, use EXE as default)
                                file_type = 'EXE'
                            
                            self.update_progress(f"Quick detection: Found {file_type} at 0x{current_pos//2:X}")
                            
                            # Create new file boundary
                            boundary = {
                                'start': current_pos,
                                'end': None,
                                'signature': sig_check,
                                'file_type': file_type,
                                'size_hex': 0
                            }
                            boundaries.append(boundary)
                            signature_found_count += 1
            
            # Check for potential marker
            if current_pos + 2 <= hex_length:
                current_marker = combined_hex[current_pos:current_pos+2]
                if current_marker in potential_markers:
                    for signature, ftype in potential_markers[current_marker]:
                        sig_len = len(signature)
                        if current_pos + sig_len <= hex_length and combined_hex[current_pos:current_pos+sig_len] == signature:
                            
                            # Create new file boundary
                            should_add = True
                            
                            # Check for close duplicates
                            for existing in boundaries:
                                if existing['signature'] == signature and abs(current_pos - existing['start']) < 1024:
                                    should_add = False
                                    break
                            
                            if should_add:
                                # Update previous file's end
                                if boundaries:
                                    boundaries[-1]['end'] = current_pos
                                    boundaries[-1]['size_hex'] = current_pos - boundaries[-1]['start']
                                
                                boundary = {
                                    'start': current_pos,
                                    'end': None,
                                    'signature': signature,
                                    'file_type': ftype,
                                    'size_hex': 0
                                }
                                boundaries.append(boundary)
                                
                                self.update_progress(f"Found {ftype} signature '{signature}' at position 0x{current_pos//2:X}")
                                signature_found_count += 1
                            
                            current_pos += max(1, sig_len // 2)
                            break
                    else:
                        current_pos += 1
                else:
                    current_pos += 1
            else:
                current_pos += 1

        # Detect text files in undiscovered areas
        if len(boundaries) == 0 or len(boundaries) < 3:
            self.update_progress("\n🔍 Performing text file detection in undiscovered areas...")
            text_boundaries = self.detect_text_files(combined_hex, boundaries)
            boundaries.extend(text_boundaries)
        
        # Update end of last file
        if boundaries and boundaries[-1]['end'] is None:
            boundaries[-1]['end'] = hex_length
            boundaries[-1]['size_hex'] = hex_length - boundaries[-1]['start']

        # Sort boundaries by position
        boundaries.sort(key=lambda x: x['start'])

        elapsed = time.time() - start_time
        
        # Display final results
        if len(boundaries) > 0:
            self.update_progress(f"✅ File boundary detection completed in {elapsed:.2f} seconds")
            self.update_progress(f"📁 Found {len(boundaries)} potential files")
            self.update_progress(f"📊 Performed {signature_found_count} signature matches")
            
            # File type statistics
            file_types_found = {}
            for b in boundaries:
                file_type = b['file_type']
                file_types_found[file_type] = file_types_found.get(file_type, 0) + 1
                
            self.update_progress("\n📋 Files by type:")
            for ftype, count in sorted(file_types_found.items(), key=lambda x: x[1], reverse=True):
                self.update_progress(f"   {ftype}: {count} files")
                
        else:
            self.update_progress(f"⚠️ No file signatures found in {elapsed:.2f} seconds!")
            
        return boundaries

    def detect_text_files(self, combined_hex, existing_boundaries):
        """Detect text files in undiscovered areas"""
        text_boundaries = []
        
        # Create list of discovered regions
        discovered_regions = []
        for boundary in existing_boundaries:
            discovered_regions.append((boundary['start'], boundary['end']))
        
        # Sort regions
        discovered_regions.sort()
        
        # Look for gaps between discovered files
        current_pos = 0
        for start, end in discovered_regions:
            if start > current_pos:
                # There's a gap, check if it contains text
                gap_size = start - current_pos
                if gap_size >= 100:  # At least 50 bytes
                    gap_hex = combined_hex[current_pos:start]
                    try:
                        gap_bytes = bytes.fromhex(gap_hex)
                        text_analysis = self.analyze_text_content(gap_bytes)
                        
                        if text_analysis['is_likely_text'] and text_analysis['printable_ratio'] > 0.8:
                            text_boundary = {
                                'start': current_pos,
                                'end': start,
                                'signature': 'TEXT_CONTENT',
                                'file_type': 'TXT',
                                'size_hex': gap_size
                            }
                            text_boundaries.append(text_boundary)
                            self.update_progress(f"Found text file (TXT) in gap at 0x{current_pos//2:X}")
                            
                    except Exception as e:
                        pass  # Ignore conversion errors
                        
            current_pos = max(current_pos, end)
        
        # Check area after last file
        if current_pos < len(combined_hex):
            remaining_hex = combined_hex[current_pos:]
            if len(remaining_hex) >= 100:
                try:
                    remaining_bytes = bytes.fromhex(remaining_hex)
                    text_analysis = self.analyze_text_content(remaining_bytes)
                    
                    if text_analysis['is_likely_text'] and text_analysis['printable_ratio'] > 0.8:
                        text_boundary = {
                            'start': current_pos,
                            'end': len(combined_hex),
                            'signature': 'TEXT_CONTENT',
                            'file_type': 'TXT',
                            'size_hex': len(remaining_hex)
                        }
                        text_boundaries.append(text_boundary)
                        self.update_progress(f"Found text file (TXT) at the end: 0x{current_pos//2:X}")
                        
                except Exception as e:
                    pass
        
        return text_boundaries

    def analyze_text_content(self, sample_bytes):
        """Analyze text content"""
        result = {
            'is_likely_text': False,
            'text_type': 'UNKNOWN',
            'printable_ratio': 0.0,
        }
        
        if not sample_bytes:
            return result
        
        # Calculate printable character ratio
        printable_count = 0
        control_count = 0
        
        for b in sample_bytes:
            if 32 <= b <= 126:  # ASCII printable
                printable_count += 1
            elif b in [9, 10, 13]:  # tab, LF, CR
                printable_count += 1
                control_count += 1
            else:
                control_count += 1
        
        total_chars = len(sample_bytes)
        result['printable_ratio'] = printable_count / total_chars if total_chars > 0 else 0
        
        # Determine if it's text
        if result['printable_ratio'] > 0.8:
            result['is_likely_text'] = True
            result['text_type'] = 'TXT'
        
        return result

    def extract_individual_files(self, combined_hex, boundaries):
        """Extract individual files from combined hex"""
        self.update_progress("⏳ Starting file extraction...")
        start_time = time.time()
        
        results = {}
        
        for i, boundary in enumerate(boundaries):
            file_hex = combined_hex[boundary['start']:boundary['end']]
            file_id = f"file_{i + 1}_{boundary['file_type']}"
            
            file_data = {
                'hex_data': file_hex,
                'file_type': boundary['file_type'],
                'signature': boundary['signature'],
                'size_hex': boundary['size_hex'],
                'size_bytes': len(file_hex) // 2,
                'start_offset': boundary['start'],
                'end_offset': boundary['end']
            }
            
            results[file_id] = file_data
            self.update_progress(f"✅ Extracted: {file_id} - {file_data['size_bytes']} bytes")
        
        elapsed = time.time() - start_time
        self.update_progress(f"✅ Extraction of {len(results)} files completed in {elapsed:.2f} seconds")
        return results

    def analyze_extracted_file(self, file_data):
        """Analyze extracted file with header and trailer extraction"""
        hex_data = file_data['hex_data']
        file_size_bytes = len(hex_data) // 2
        
        self.update_progress(f"Analyzing file: {file_data.get('file_type', 'Unknown')} - {file_size_bytes} bytes")

        # Extract header and trailer
        header_info = self.detect_header(hex_data, file_data['file_type'])
        trailer_info = self.detect_trailer(hex_data, file_data['file_type'])

        header_hex = header_info['hex']
        trailer_hex = trailer_info['hex']
        
        # Create comprehensive file analysis
        result = {
            **file_data,
            'header_hex': header_hex,
            'trailer_hex': trailer_hex,
            'header_size': header_info['size'],
            'trailer_size': trailer_info['size'],
            'header_info': header_info['info'],
            'trailer_info': trailer_info['info'],
            'md5': hashlib.md5(bytes.fromhex(hex_data)).hexdigest(),
            'analysis_timestamp': time.time()
        }
        
        return result
        
    def analyze_files_parallel(self, files_data):
        """Analyze all extracted files"""
        self.update_progress("⏳ Starting file analysis...")
        start_time = time.time()
        
        results = {}
        
        for file_id, file_data in files_data.items():
            analyzed_data = self.analyze_extracted_file(file_data)
            results[file_id] = analyzed_data
            self.update_progress(f"✅ Analyzed: {file_id} - {analyzed_data['size_bytes']} bytes")
        
        elapsed = time.time() - start_time
        self.update_progress(f"✅ Analysis of {len(results)} files completed in {elapsed:.2f} seconds")
        return results

    def detect_header(self, hex_data, file_type):
        """Detect header based on file type"""
        header_info = {
            'hex': '',
            'size': 0,
            'info': ''
        }
        
        if file_type == 'JPG':
            # JPEG header: FFD8FF
            header_info['hex'] = hex_data[:6] if len(hex_data) >= 6 else hex_data
            header_info['size'] = 3
            header_info['info'] = 'JPEG Header (FFD8FF)'
            
        elif file_type == 'PNG':
            # PNG header: 89504E470D0A1A0A
            header_info['hex'] = hex_data[:16] if len(hex_data) >= 16 else hex_data
            header_info['size'] = 8
            header_info['info'] = 'PNG Header (89504E470D0A1A0A)'
            
        elif file_type == 'BMP':
            # BMP header: 424D
            header_info['hex'] = hex_data[:4] if len(hex_data) >= 4 else hex_data
            header_info['size'] = 2
            header_info['info'] = 'BMP Header (424D)'
            
        elif file_type == 'PDF':
            # PDF header: 25504446
            header_info['hex'] = hex_data[:8] if len(hex_data) >= 8 else hex_data
            header_info['size'] = 4
            header_info['info'] = 'PDF Header (%PDF)'
            
        elif file_type in ['EXE', 'DLL']:
            # EXE/DLL header: 4D5A
            header_info['hex'] = hex_data[:4] if len(hex_data) >= 4 else hex_data
            header_info['size'] = 2
            header_info['info'] = 'EXE/DLL Header (MZ)'
            
        elif file_type == 'MP3':
            # Look for MP3 header (could be ID3 or frame sync)
            if hex_data.startswith('494433'):  # ID3
                header_info['hex'] = hex_data[:10] if len(hex_data) >= 10 else hex_data
                header_info['size'] = 5
                header_info['info'] = 'MP3 ID3 Header'
            else:
                # frame sync
                header_info['hex'] = hex_data[:4] if len(hex_data) >= 4 else hex_data
                header_info['size'] = 2
                header_info['info'] = 'MP3 Frame Sync'
                
        elif file_type == 'MP4':
            # Look for ftyp in MP4
            ftyp_pos = hex_data.find('66747970')
            if ftyp_pos != -1 and ftyp_pos < 20:
                header_info['hex'] = hex_data[ftyp_pos:ftyp_pos+32] if len(hex_data) >= ftyp_pos+32 else hex_data[ftyp_pos:]
                header_info['size'] = 16
                header_info['info'] = 'MP4 ftyp Header'
            else:
                header_info['hex'] = hex_data[:16] if len(hex_data) >= 16 else hex_data
                header_info['size'] = 8
                header_info['info'] = 'MP4 Header'
                
        elif file_type == 'MOV':
            # MOV header similar to MP4
            ftyp_pos = hex_data.find('66747970')
            if ftyp_pos != -1 and ftyp_pos < 20:
                header_info['hex'] = hex_data[ftyp_pos:ftyp_pos+32] if len(hex_data) >= ftyp_pos+32 else hex_data[ftyp_pos:]
                header_info['size'] = 16
                header_info['info'] = 'MOV ftyp Header'
            else:
                header_info['hex'] = hex_data[:16] if len(hex_data) >= 16 else hex_data
                header_info['size'] = 8
                header_info['info'] = 'MOV Header'
                
        elif file_type == 'TXT':
            # For text files, take first 100 bytes as header
            header_size = min(200, len(hex_data))
            header_info['hex'] = hex_data[:header_size]
            header_info['size'] = header_size // 2
            header_info['info'] = 'Text Header'
            
        else:
            # Default: first 16 bytes
            header_size = min(32, len(hex_data))
            header_info['hex'] = hex_data[:header_size]
            header_info['size'] = header_size // 2
            header_info['info'] = 'Generic Header'
        
        return header_info

    def detect_trailer(self, hex_data, file_type):
        """Detect trailer based on file type"""
        trailer_info = {
            'hex': '',
            'size': 0,
            'info': ''
        }
        
        if file_type == 'JPG':
            # JPEG trailer: FFD9
            if hex_data.endswith('FFD9'):
                trailer_info['hex'] = hex_data[-4:]
                trailer_info['size'] = 2
                trailer_info['info'] = 'JPEG Trailer (FFD9)'
            else:
                # If no valid trailer, take last 4 bytes
                trailer_size = min(8, len(hex_data))
                trailer_info['hex'] = hex_data[-trailer_size:]
                trailer_info['size'] = trailer_size // 2
                trailer_info['info'] = 'JPEG End Data'
                
        elif file_type == 'PNG':
            # PNG trailer: IEND chunk
            iend_pos = hex_data.find('49454E44AE426082')
            if iend_pos != -1:
                trailer_info['hex'] = hex_data[iend_pos:iend_pos+16]
                trailer_info['size'] = 8
                trailer_info['info'] = 'PNG IEND Trailer'
            else:
                trailer_size = min(16, len(hex_data))
                trailer_info['hex'] = hex_data[-trailer_size:]
                trailer_info['size'] = trailer_size // 2
                trailer_info['info'] = 'PNG End Data'
                
        elif file_type == 'PDF':
            # PDF trailer: %%EOF
            eof_pos = hex_data.find('2525454F46')  # %%EOF
            if eof_pos != -1:
                trailer_info['hex'] = hex_data[eof_pos:eof_pos+10]
                trailer_info['size'] = 5
                trailer_info['info'] = 'PDF EOF Trailer'
            else:
                trailer_size = min(20, len(hex_data))
                trailer_info['hex'] = hex_data[-trailer_size:]
                trailer_info['size'] = trailer_size // 2
                trailer_info['info'] = 'PDF End Data'
                
        elif file_type in ['EXE', 'DLL']:
            # No fixed trailer for EXE/DLL, take last 16 bytes
            trailer_size = min(32, len(hex_data))
            trailer_info['hex'] = hex_data[-trailer_size:]
            trailer_info['size'] = trailer_size // 2
            trailer_info['info'] = 'EXE/DLL End Data'
            
        elif file_type == 'MP3':
            # No fixed trailer for MP3, take last 16 bytes
            trailer_size = min(32, len(hex_data))
            trailer_info['hex'] = hex_data[-trailer_size:]
            trailer_info['size'] = trailer_size // 2
            trailer_info['info'] = 'MP3 End Data'
            
        elif file_type in ['MP4', 'MOV']:
            # Look for moov atom at the end
            moov_pos = hex_data.rfind('6D6F6F76')
            if moov_pos != -1 and moov_pos > len(hex_data) - 100:
                trailer_info['hex'] = hex_data[moov_pos:moov_pos+32] if len(hex_data) >= moov_pos+32 else hex_data[moov_pos:]
                trailer_info['size'] = 16
                trailer_info['info'] = 'MP4/MOV moov Trailer'
            else:
                trailer_size = min(32, len(hex_data))
                trailer_info['hex'] = hex_data[-trailer_size:]
                trailer_info['size'] = trailer_size // 2
                trailer_info['info'] = 'MP4/MOV End Data'
                
        elif file_type == 'TXT':
            # For text files, take last 100 bytes as trailer
            trailer_size = min(200, len(hex_data))
            trailer_info['hex'] = hex_data[-trailer_size:]
            trailer_info['size'] = trailer_size // 2
            trailer_info['info'] = 'Text Trailer'
            
        else:
            # Default: last 16 bytes
            trailer_size = min(32, len(hex_data))
            trailer_info['hex'] = hex_data[-trailer_size:]
            trailer_info['size'] = trailer_size // 2
            trailer_info['info'] = 'Generic Trailer'
        
        return trailer_info

    def rebuild_all_files(self, extracted_files, output_dir):
        """Rebuild all extracted files"""
        self.update_progress("⏳ Starting file reconstruction...")
        start_time = time.time()
        
        results = {
            'successful': [],
            'failed': [],
            'total_files': len(extracted_files),
            'output_directory': output_dir
        }

        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Create directories for each file type
        file_types = set(file_data['file_type'] for file_data in extracted_files.values())
        for file_type in file_types:
            type_dir = os.path.join(output_dir, file_type)
            Path(type_dir).mkdir(parents=True, exist_ok=True)
            self.update_progress(f"Created folder for type: {file_type}")
        
        for file_id, file_data in extracted_files.items():
            try:
                file_extension = self.get_file_extension(file_data['file_type'])
                file_type = file_data['file_type']
                
                # Extract file number for consistent naming
                file_number = file_id.split('_')[1]
                formatted_number = f"{int(file_number):03d}"
                
                # Create type-specific directory path
                type_dir = os.path.join(output_dir, file_type)
                
                # Create filename with formatted number
                filename = f"{formatted_number}_{file_type}{file_extension}"
                output_path = os.path.join(type_dir, filename)

                # Prepare hex data
                hex_data = file_data['hex_data']
                
                # Clean hex data
                hex_data = ''.join(c for c in hex_data if c in "0123456789ABCDEF")
                if len(hex_data) % 2 != 0:
                    hex_data = hex_data[:-1]
                
                # Convert to bytes
                binary_data = bytes.fromhex(hex_data)
                
                # Reconstruct file
                try:
                    self.update_progress(f"Writing {file_type} file to {output_path}, size: {len(binary_data):,} bytes")
                    
                    # Ensure target folder exists
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
                    # Save file
                    with open(output_path, 'wb') as f:
                        f.write(binary_data)
                    
                    # Validate file
                    if not os.path.exists(output_path):
                        raise Exception(f"Failed to create file: {output_path}")
                        
                    if os.path.getsize(output_path) == 0:
                        raise Exception(f"File created but empty: {output_path}")
                        
                    # Ensure file is valid
                    self.update_progress(f"Successfully wrote {file_type} file: {filename} ({os.path.getsize(output_path):,} bytes)")
                except Exception as e:
                    raise Exception(f"File write error: {str(e)}")

                file_info = {
                    'file_id': file_id,
                    'filename': filename,
                    'output_path': output_path,
                    'file_type': file_data['file_type'],
                    'size_bytes': file_data['size_bytes'],
                    'md5': file_data.get('md5', ''),
                    'reconstructed': True
                }

                results['successful'].append(file_info)
                self.update_progress(f"✅ Rebuilt: {filename} - {file_data['size_bytes']} bytes in {file_type} folder")

            except Exception as e:
                results['failed'].append({
                    'file_id': file_id,
                    'error': str(e),
                    'reconstructed': False
                })
                self.update_progress(f"❌ Failed to rebuild: {file_id} - {str(e)}")
        
        elapsed = time.time() - start_time
        self.update_progress(f"✅ Reconstruction of {len(results['successful'])} out of {results['total_files']} files completed in {elapsed:.2f} seconds")
        return results

    def get_file_extension(self, file_type):
        """Get appropriate file extension for file type"""
        extensions = {
            'JPG': '.jpg',
            'PNG': '.png',
            'BMP': '.bmp',
            'PDF': '.pdf',
            'EXE': '.exe',
            'DLL': '.dll',
            'MP3': '.mp3',
            'MP4': '.mp4',
            'MOV': '.mov',
            'TXT': '.txt',
        }
        return extensions.get(file_type, '.bin')

    def save_extraction_report(self, extracted_files, report_path):
        """Save extraction report"""
        report = {
            'extraction_timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'total_files': len(extracted_files),
            'files': {}
        }

        # Create serializable copy of file data
        for file_id, file_data in extracted_files.items():
            serializable_data = file_data.copy()
            report['files'][file_id] = serializable_data

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
    def save_hex_files(self, extracted_files, output_dir):
        """Save hex code for each file in separate organized text files"""
        self.update_progress("⏳ Starting hex file saving process...")
        start_time = time.time()
        
        results = {
            'successful': [],
            'failed': [],
            'total_files': len(extracted_files),
            'output_directory': output_dir
        }

        # Create base output directory if it doesn't exist
        hex_base_dir = os.path.join(output_dir, "hex_files")
        Path(hex_base_dir).mkdir(parents=True, exist_ok=True)
        
        # Create directories for each file type
        file_types = set(file_data['file_type'] for file_data in extracted_files.values())
        for file_type in file_types:
            type_dir = os.path.join(hex_base_dir, file_type)
            Path(type_dir).mkdir(parents=True, exist_ok=True)
            self.update_progress(f"Created hex folder for type: {file_type}")
        
        for file_id, file_data in extracted_files.items():
            try:
                # Extract file number from file ID
                file_number = file_id.split('_')[1]
                file_type = file_data['file_type']
                
                # Format file number for consistent naming
                formatted_number = f"{int(file_number):03d}"
                
                # Create type-specific directory path
                type_dir = os.path.join(hex_base_dir, file_type)
                
                # Create filename and full path
                filename = f"{formatted_number}_{file_type}.hex"
                output_path = os.path.join(type_dir, filename)

                # Save hex data to text file
                with open(output_path, 'w', encoding='utf-8') as f:
                    # Add metadata at the beginning of the file
                    f.write(f"# File Number: {formatted_number}\n")
                    f.write(f"# Type: {file_type}\n")
                    f.write(f"# Size: {file_data['size_bytes']} bytes\n")
                    f.write(f"# MD5: {file_data.get('md5', '')}\n")
                    f.write(f"# Header: {file_data.get('header_hex', '')[:64]}...\n")
                    f.write(f"# Trailer: {file_data.get('trailer_hex', '')[-64:] if file_data.get('trailer_hex') else 'N/A'}\n")
                    f.write("#" + "-" * 50 + "\n\n")
                    
                    # Write hex data in rows of 32 bytes
                    hex_data = file_data['hex_data']
                    for i in range(0, len(hex_data), 64):
                        line = hex_data[i:i+64]
                        offset = i // 2
                        f.write(f"{offset:08X}: {line}\n")

                file_info = {
                    'file_id': file_id,
                    'filename': filename,
                    'output_path': output_path,
                    'file_type': file_data['file_type'],
                    'size_bytes': file_data['size_bytes'],
                    'hex_saved': True
                }

                results['successful'].append(file_info)
                self.update_progress(f"✅ Saved hex: {filename} - {file_data['size_bytes']} bytes in {file_type} folder")

            except Exception as e:
                results['failed'].append({
                    'file_id': file_id,
                    'error': str(e),
                    'hex_saved': False
                })
                self.update_progress(f"❌ Failed to save hex: {file_id} - {str(e)}")
        
        elapsed = time.time() - start_time
        self.update_progress(f"✅ Saved {len(results['successful'])} hex files out of {results['total_files']} in {elapsed:.2f} seconds")
        return results


def display_file_boundaries(boundaries):
    """Display detected file boundaries"""
    print(f"\n🔍 Detected File Boundaries ({len(boundaries)} files):")
    print("=" * 80)

    for i, boundary in enumerate(boundaries):
        print(f"\n📄 File {i + 1}:")
        print(f"   Type: {boundary['file_type']}")
        print(f"   Start: {boundary['start']} (0x{boundary['start']//2:X})")
        print(f"   End: {boundary['end']} (0x{boundary['end']//2:X})")
        print(f"   Size: {boundary['size_hex'] // 2} bytes")
        print(f"   Signature: {boundary['signature']}")


def display_extracted_files(extracted_files):
    """Display extracted file information"""
    print(f"\n✅ Extracted Files ({len(extracted_files)} files):")
    print("=" * 80)

    for file_id, file_data in extracted_files.items():
        print(f"\n📁 {file_id}:")
        print(f"   Type: {file_data['file_type']}")
        print(f"   Size: {file_data['size_bytes']} bytes")
        print(f"   Header: {file_data.get('header_hex', '')[:32]}...")
        print(f"   Trailer: {file_data.get('trailer_hex', '')[:32]}...")
        print(f"   MD5: {file_data.get('md5', '')}")


def display_reconstruction_results(results):
    """Display reconstruction results"""
    print(f"\n🔨 Reconstruction Results:")
    print("=" * 80)
    print(f"📁 Directory: {results['output_directory']}")
    print(f"📊 Total Files: {results['total_files']}")
    print(f"✅ Successful: {len(results['successful'])}")
    print(f"❌ Failed: {len(results['failed'])}")

    if results['successful']:
        print(f"\n📜 Successfully Reconstructed Files:")
        for file_info in results['successful']:
            print(f"   ✓ {file_info['filename']} - {file_info['size_bytes']} bytes - Type: {file_info['file_type']}")

    if results['failed']:
        print(f"\n⚠️ Failed to Reconstruct Files:")
        for file_info in results['failed']:
            print(f"   ✗ {file_info['file_id']}: {file_info['error']}")


def main():
    print("🔧 Multi-File Hex Extraction and Building Tool")
    print("=" * 60)

    parser = MultiFileHexParser()

    while True:
        print("\n" + "=" * 50)
        print("📋 Main Menu:")
        print("1 - Input combined hex for multiple files")
        print("2 - Load combined hex from file")
        print("3 - View extracted files")
        print("4 - Rebuild all files")
        print("5 - Save extraction report")
        print("6 - Save hex code for each file in separate files")
        print("0 - Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == '1':
            print("\n📥 Enter combined hex for multiple files:")
            print("Note: File boundaries will be detected automatically")
            combined_hex = ""
            while True:
                line = input()
                if line.strip().upper() == "END":
                    break
                combined_hex += line

            cleaned_hex = parser.clean_hex_data(combined_hex)
            print(f"✅ Cleaned hex: {len(cleaned_hex)} characters")

            # Detect file boundaries
            boundaries = parser.detect_file_boundaries(cleaned_hex)
            display_file_boundaries(boundaries)

            if boundaries:
                # Extract individual files
                parser.files_data = parser.extract_individual_files(cleaned_hex, boundaries)

                # Analyze all files
                parser.files_data = parser.analyze_files_parallel(parser.files_data)

                display_extracted_files(parser.files_data)
            else:
                print("❌ No files found in input data")

        elif choice == '2':
            hex_file = input("Enter path to combined hex file: ").strip()
            if os.path.exists(hex_file):
                with open(hex_file, 'r', encoding='utf-8') as f:
                    combined_hex = f.read()

                cleaned_hex = parser.clean_hex_data(combined_hex)
                print(f"✅ Loaded hex file: {len(cleaned_hex)} characters")

                boundaries = parser.detect_file_boundaries(cleaned_hex)
                display_file_boundaries(boundaries)

                if boundaries:
                    parser.files_data = parser.extract_individual_files(cleaned_hex, boundaries)
                    parser.files_data = parser.analyze_files_parallel(parser.files_data)
                    display_extracted_files(parser.files_data)
                else:
                    print("❌ No files found in input file")
            else:
                print("❌ File not found!")

        elif choice == '3':
            if not parser.files_data:
                print("❌ No files extracted yet")
            else:
                display_extracted_files(parser.files_data)

        elif choice == '4':
            if not parser.files_data:
                print("❌ No extracted files to rebuild")
                continue

            output_dir = input("Enter output directory [default: reconstructed_files]: ").strip()
            if not output_dir:
                output_dir = "reconstructed_files"

            results = parser.rebuild_all_files(parser.files_data, output_dir)
            display_reconstruction_results(results)

        elif choice == '5':
            if not parser.files_data:
                print("❌ No data to save")
                continue

            report_path = input("Enter report path [default: extraction_report.json]: ").strip()
            if not report_path:
                report_path = "extraction_report.json"

            parser.save_extraction_report(parser.files_data, report_path)
            print(f"✅ Report saved to: {report_path}")

        elif choice == '6':
            if not parser.files_data:
                print("❌ No extracted files to save hex code")
                continue

            output_dir = input("Enter output directory [default: hex_output]: ").strip()
            if not output_dir:
                output_dir = "hex_output"

            results = parser.save_hex_files(parser.files_data, output_dir)
            
            print(f"\n💾 Hex File Saving Results:")
            print("=" * 80)
            print(f"📁 Output Directory: {os.path.join(results['output_directory'], 'hex_files')}")
            print(f"📊 Total Files: {results['total_files']}")
            print(f"✅ Successful: {len(results['successful'])}")
            print(f"❌ Failed: {len(results['failed'])}")

        elif choice == '0':
            break
        else:
            print("❌ Invalid choice!")


if __name__ == "__main__":
    main()