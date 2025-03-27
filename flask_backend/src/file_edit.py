from bson.binary import Binary
import PyPDF2
import docx
import io

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(file_data, file_ext):
    """从不同类型的文件中提取文本"""
    
    if file_ext == '.txt':
        return file_data.decode('utf-8')
    
    elif file_ext == '.pdf':
        text = ""
        pdf_file = io.BytesIO(file_data)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
        return text
    
    elif file_ext in ['.doc', '.docx']:
        doc_file = io.BytesIO(file_data)
        doc = docx.Document(doc_file)
        return " ".join([paragraph.text for paragraph in doc.paragraphs])
    
    return "File type not supported for text extraction"