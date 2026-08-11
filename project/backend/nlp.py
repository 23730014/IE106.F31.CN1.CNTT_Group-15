import re
from datetime import datetime

def extract_fields(text: str):
    """
    NLP đơn giản cho prototype ClearGov.
    Trích xuất các trường:
    - name
    - birth_year
    - id_number
    - address

    Có thể thay phần này bằng mô hình NLP/LLM thật ở phiên bản nâng cao.
    """
    result = {}

    # Số CCCD: ưu tiên chuỗi 12 chữ số
    id_match = re.search(r'(?<!\d)\d{12}(?!\d)', text)
    if id_match:
        result["id_number"] = id_match.group()

    # Năm sinh: "sinh năm 1962", "năm 1962"
    year_match = re.search(r'(?:sinh\s*năm|năm\s*sinh|sinh)\s*(?:là\s*)?(\d{4})', text.lower())
    if year_match:
        year = int(year_match.group(1))
        if 1900 <= year <= datetime.now().year:
            result["birth_year"] = year

    # Họ tên: một số mẫu câu phổ biến
    name_patterns = [
        r'(?:tôi|mình|cháu)\s*(?:tên|là)\s+([A-Za-zÀ-ỹĐđ\s]{2,60}?)(?:,|\.|$)',
        r'(?:họ và tên|họ tên)\s*(?:là|:)?\s*([A-Za-zÀ-ỹĐđ\s]{2,60}?)(?:,|\.|$)',
    ]

    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            name = " ".join(match.group(1).strip().split())
            if len(name.split()) >= 2:
                result["name"] = name.title()
                break

    # Địa chỉ
    address_patterns = [
        r'(?:địa chỉ|đang ở|ở tại|hiện ở)\s*(?:là|:)?\s*(.+)$'
    ]

    for pattern in address_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            address = match.group(1).strip(" .")
            if len(address) >= 5:
                result["address"] = address
                break

    return {
        "fields": result,
        "raw_text": text
    }
