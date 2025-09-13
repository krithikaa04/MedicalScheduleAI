import spacy
import re
from nltk.tokenize import word_tokenize
import nltk

# Download required NLTK resources
import nltk
nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    # If model is not available, download it
    import os
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def extract_medication_info(text):
    """
    Extract medication information from text using NLP techniques
    
    Args:
        text (str): The input text containing medication information
        
    Returns:
        dict: A dictionary containing extracted medication details
    """
    # Process the text with spaCy
    doc = nlp(text)
    
    # Initialize result dictionary
    medication_info = {
        "medicine_name": "",
        "dosage": "",
        "frequency": "",
        "timing": "",
        "duration": "",
        "instructions": ""
    }
    
    # Extract medicine name (look for medication names)
    medicine_name = extract_medicine_name(doc)
    if medicine_name:
        medication_info["medicine_name"] = medicine_name
    
    # Extract dosage (look for numbers followed by units like mg, ml, etc.)
    dosage = extract_dosage(doc)
    if dosage:
        medication_info["dosage"] = dosage
    
    # Extract frequency (how often to take the medication)
    frequency = extract_frequency(doc)
    if frequency:
        medication_info["frequency"] = frequency
    
    # Extract timing (when to take the medication)
    timing = extract_timing(doc)
    if timing:
        medication_info["timing"] = timing
    
    # Extract duration (how long to take the medication)
    duration = extract_duration(doc)
    if duration:
        medication_info["duration"] = duration
    
    # Extract special instructions
    instructions = extract_instructions(doc)
    if instructions:
        medication_info["instructions"] = instructions
    
    return medication_info

def extract_medicine_name(doc):
    """
    Extract medicine name from the spaCy doc
    
    Args:
        doc: spaCy doc object
        
    Returns:
        str: Extracted medicine name
    """
    # Common medicine names to look for - this is a limited list, in a real app this would be more comprehensive
    common_medicines = [
        "lisinopril", "metformin", "amlodipine", "atorvastatin", "metoprolol", 
        "omeprazole", "losartan", "albuterol", "gabapentin", "hydrochlorothiazide",
        "simvastatin", "levothyroxine", "montelukast", "pantoprazole", "furosemide",
        "citalopram", "sertraline", "fluoxetine", "tramadol", "amoxicillin",
        "azithromycin", "ibuprofen", "acetaminophen", "aspirin", "naproxen",
        "clonazepam", "alprazolam", "zolpidem", "prednisone", "hydrocortisone",
        "insulin", "warfarin", "xarelto", "eliquis", "plavix",
        "crestor", "lipitor", "zocor", "nexium", "prilosec",
        "protonix", "synthroid", "ventolin", "advair", "spiriva",
        "flovent", "lantus", "humalog", "novolog", "tresiba",
        "januvia", "jardiance", "trulicity", "ozempic", "farxiga",
        "eliquis", "xarelto", "pradaxa", "savaysa", "brilinta",
        "plavix", "effient", "brilinta", "multivitamin", "vitamin d",
        "calcium", "iron", "zinc", "magnesium", "potassium",
        "coq10", "fish oil", "omega-3", "probiotics", "melatonin"
    ]
    
    # Look for known medicine names
    text_lower = doc.text.lower()
    for medicine in common_medicines:
        pattern = r'\b' + re.escape(medicine) + r'\b'
        match = re.search(pattern, text_lower)
        if match:
            # Get the actual casing from the original text
            start, end = match.span()
            # Find all words in the text
            words = word_tokenize(doc.text)
            # Find words that overlap with the match
            medicine_words = []
            for word in words:
                word_lower = word.lower()
                if word_lower in medicine:
                    medicine_words.append(word)
            
            if medicine_words:
                return " ".join(medicine_words)
            else:
                return medicine.title()  # Use title case if we can't find the exact word
    
    # If no common medicine is found, try to extract entities that might be medicines
    for ent in doc.ents:
        if ent.label_ in ["PRODUCT", "ORG", "GPE"]:  # These entity types might capture medicine names
            return ent.text
    
    # If still not found, look for words following "take", "taking", "prescribed"
    for i, token in enumerate(doc):
        if token.lemma_ in ["take", "prescribe"] and i < len(doc) - 1:
            # Skip over articles and prepositions
            j = i + 1
            while j < len(doc) and doc[j].pos_ in ["DET", "ADP"]:
                j += 1
            
            if j < len(doc):
                # Extract a potential medicine name (up to 3 words)
                end_idx = min(j + 3, len(doc))
                med_span = doc[j:end_idx]
                return med_span.text
    
    # If no specific pattern is found, try to extract nouns that might be medicines
    for chunk in doc.noun_chunks:
        if len(chunk) <= 3:  # Limit to reasonable length noun phrases
            return chunk.text
    
    return ""

def extract_dosage(doc):
    """
    Extract dosage information from the spaCy doc
    
    Args:
        doc: spaCy doc object
        
    Returns:
        str: Extracted dosage information
    """
    # Common patterns for dosage
    dosage_patterns = [
        r'\d+\s*(?:mg|mcg|g|ml|cc|tablet|pill|capsule|dose|tab|cap)s?(?:\b|\s)',
        r'(?:one|two|three|four|five|half|quarter)\s+(?:tablet|pill|capsule|dose|tab|cap)s?(?:\b|\s)',
        r'\d+/\d+\s*(?:mg|mcg|g|ml|cc)(?:\b|\s)'
    ]
    
    text = doc.text.lower()
    
    for pattern in dosage_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0).strip()
    
    # Look for numbers followed by units
    for token in doc:
        if token.like_num:
            # Check if the next token is a unit
            if token.i + 1 < len(doc) and doc[token.i + 1].text.lower() in ["mg", "mcg", "g", "ml", "cc", "tablet", "pill", "capsule", "dose", "tab", "cap"]:
                return token.text + " " + doc[token.i + 1].text
    
    return ""

def extract_frequency(doc):
    """
    Extract frequency information from the spaCy doc
    
    Args:
        doc: spaCy doc object
        
    Returns:
        str: Extracted frequency information
    """
    # Common patterns for frequency
    frequency_patterns = [
        r'(?:once|twice|three times|four times)\s+(?:a|per|every)\s+day',
        r'(?:once|twice|three times|four times)\s+daily',
        r'(?:every|each)\s+(?:day|morning|evening|night|afternoon)',
        r'(?:every|each)\s+\d+\s+hours',
        r'(?:every|each)\s+\d+\s*(?:hr|hrs)',
        r'\d+\s+times\s+(?:a|per)\s+day',
        r'\d+\s+times\s+daily',
        r'(?:daily|weekly|monthly|yearly)'
    ]
    
    text = doc.text.lower()
    
    for pattern in frequency_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0).strip()
    
    # Look for frequency-related keywords
    frequency_keywords = ["daily", "weekly", "monthly", "twice", "thrice", "once", "every"]
    for token in doc:
        if token.text.lower() in frequency_keywords:
            # Try to get context by looking at nearby tokens
            start = max(0, token.i - 2)
            end = min(len(doc), token.i + 3)
            return doc[start:end].text
    
    return ""

def extract_timing(doc):
    """
    Extract timing information from the spaCy doc
    
    Args:
        doc: spaCy doc object
        
    Returns:
        str: Extracted timing information
    """
    # Common patterns for timing
    timing_patterns = [
        r'(?:in|at|during)\s+(?:the\s+)?(?:morning|evening|night|afternoon|noon|midday|midnight|bedtime)',
        r'(?:before|after|with)\s+(?:meals?|breakfast|lunch|dinner|food|eating)',
        r'(?:on|with)\s+(?:an?\s+)?(?:empty\s+stomach|full\s+stomach)',
        r'(?:before|at|after)\s+bedtime'
    ]
    
    text = doc.text.lower()
    
    for pattern in timing_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0).strip()
    
    # Look for time-related keywords
    timing_keywords = ["morning", "evening", "night", "afternoon", "breakfast", "lunch", "dinner", "bedtime", "noon", "midnight"]
    for token in doc:
        if token.text.lower() in timing_keywords:
            # Try to get context by looking at nearby tokens
            start = max(0, token.i - 2)
            end = min(len(doc), token.i + 3)
            return doc[start:end].text
    
    return ""

def extract_duration(doc):
    """
    Extract duration information from the spaCy doc
    
    Args:
        doc: spaCy doc object
        
    Returns:
        str: Extracted duration information
    """
    # Common patterns for duration
    duration_patterns = [
        r'for\s+\d+\s+(?:day|week|month|year)s?',
        r'for\s+(?:a|one|two|three|four|five|six|seven|eight|nine|ten)\s+(?:day|week|month|year)s?',
        r'until\s+\w+',
        r'continue\s+for\s+\d+\s+(?:day|week|month|year)s?',
        r'(?:long[-\s]term|short[-\s]term|maintenance)\s+(?:treatment|therapy|medication|use)?'
    ]
    
    text = doc.text.lower()
    
    for pattern in duration_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0).strip()
    
    # Look for duration-related keywords
    duration_keywords = ["until", "long-term", "short-term", "maintenance", "continue", "ongoing", "chronic"]
    for token in doc:
        if token.text.lower() in duration_keywords or (token.text.lower() == "for" and token.i + 1 < len(doc) and doc[token.i + 1].like_num):
            # Try to get context by looking at nearby tokens
            start = token.i
            end = min(len(doc), token.i + 5)
            return doc[start:end].text
    
    return ""

def extract_instructions(doc):
    """
    Extract special instructions from the spaCy doc
    
    Args:
        doc: spaCy doc object
        
    Returns:
        str: Extracted special instructions
    """
    # Common patterns for special instructions
    instruction_patterns = [
        r'(?:with|without)\s+(?:food|water|milk)',
        r'(?:do\s+not|don\'t)\s+(?:take|use|consume)\s+with\s+\w+',
        r'avoid\s+\w+',
        r'store\s+(?:in|at)\s+\w+',
        r'(?:shake|swallow|chew|dissolve)\s+(?:well|thoroughly)?',
        r'keep\s+(?:out\s+of\s+reach|refrigerated|at\s+room\s+temperature)',
        r'take\s+on\s+an\s+empty\s+stomach',
        r'take\s+with\s+food',
        r'do\s+not\s+crush\s+or\s+chew',
        r'may\s+cause\s+drowsiness'
    ]
    
    text = doc.text.lower()
    
    all_instructions = []
    for pattern in instruction_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            all_instructions.append(match.group(0).strip())
    
    # Look for instruction-related keywords
    instruction_keywords = ["avoid", "store", "shake", "swallow", "chew", "dissolve", "keep", "refrigerate", "caution", "warning"]
    for token in doc:
        if token.text.lower() in instruction_keywords:
            # Try to get context by looking at nearby tokens
            start = token.i
            end = min(len(doc), token.i + 5)
            instruction = doc[start:end].text
            if instruction not in all_instructions:
                all_instructions.append(instruction)
    
    return "; ".join(all_instructions) if all_instructions else ""
