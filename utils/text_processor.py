"""
Text processing utilities for PDF content analysis.
"""

import re
import nltk
from typing import Dict, List, Any, Tuple
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np

class TextProcessor:
    """Handles text processing and NLP tasks for PDF content."""
    
    def __init__(self):
        """Initialize the text processor with required resources."""
        # Ensure NLTK data is available
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            pass  # Already handled in main processor
        
        self.stop_words = set(nltk.corpus.stopwords.words('english'))
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', ' ', text)
        
        # Remove multiple consecutive punctuation
        text = re.sub(r'[\.]{2,}', '.', text)
        text = re.sub(r'[\,]{2,}', ',', text)
        
        return text
    
    def extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text using NLTK."""
        if not text:
            return []
        
        try:
            sentences = nltk.sent_tokenize(text)
            return [s.strip() for s in sentences if len(s.strip()) > 10]
        except Exception:
            # Fallback to simple sentence splitting
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences if len(s.strip()) > 10]
    
    def extract_keywords(self, text: str, max_keywords: int = 20) -> List[Tuple[str, float]]:
        """Extract keywords using TF-IDF."""
        if not text or len(text.strip()) < 50:
            return []
        
        try:
            # Clean text for keyword extraction
            cleaned_text = self.clean_text(text.lower())
            
            # Use TF-IDF to extract keywords
            vectorizer = TfidfVectorizer(
                max_features=max_keywords * 2,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.95
            )
            
            tfidf_matrix = vectorizer.fit_transform([cleaned_text])
            feature_names = vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]
            
            # Get top keywords with scores
            keyword_scores = list(zip(feature_names, tfidf_scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            return keyword_scores[:max_keywords]
            
        except Exception as e:
            # Fallback to simple word frequency
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            word_freq = {}
            for word in words:
                if word not in self.stop_words:
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            return sorted_words[:max_keywords]
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text."""
        entities = {
            'persons': [],
            'organizations': [],
            'locations': [],
            'dates': [],
            'emails': [],
            'phones': [],
            'urls': []
        }
        
        if not text:
            return entities
        
        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        entities['emails'] = list(set(re.findall(email_pattern, text)))
        
        # Extract phone numbers
        phone_pattern = r'(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'
        entities['phones'] = list(set(re.findall(phone_pattern, text)))
        
        # Extract URLs
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        entities['urls'] = list(set(re.findall(url_pattern, text)))
        
        # Extract dates (basic patterns)
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b'
        ]
        
        for pattern in date_patterns:
            entities['dates'].extend(re.findall(pattern, text, re.IGNORECASE))
        
        entities['dates'] = list(set(entities['dates']))
        
        # Use TextBlob for basic NER (fallback approach)
        try:
            blob = TextBlob(text)
            for sentence in blob.sentences:
                for word, tag in sentence.tags:
                    if tag in ['NNP', 'NNPS']:  # Proper nouns
                        # Simple heuristics for classification
                        word_str = str(word)
                        if len(word_str) > 2:
                            if any(indicator in text.lower() for indicator in ['company', 'corp', 'inc', 'ltd']):
                                if word_str not in entities['organizations']:
                                    entities['organizations'].append(word_str)
                            elif any(indicator in text.lower() for indicator in ['city', 'country', 'state']):
                                if word_str not in entities['locations']:
                                    entities['locations'].append(word_str)
                            else:
                                if word_str not in entities['persons']:
                                    entities['persons'].append(word_str)
        except Exception:
            pass
        
        return entities
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of the text."""
        if not text:
            return {'polarity': 0.0, 'subjectivity': 0.0}
        
        try:
            blob = TextBlob(text)
            return {
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity
            }
        except Exception:
            return {'polarity': 0.0, 'subjectivity': 0.0}
    
    def extract_topics(self, text: str, num_topics: int = 5) -> List[Dict[str, Any]]:
        """Extract topics from text using clustering."""
        if not text or len(text.strip()) < 100:
            return []
        
        try:
            sentences = self.extract_sentences(text)
            if len(sentences) < 3:
                return []
            
            # Vectorize sentences
            vectorizer = TfidfVectorizer(
                max_features=100,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            sentence_vectors = vectorizer.fit_transform(sentences)
            
            # Cluster sentences
            n_clusters = min(num_topics, len(sentences))
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(sentence_vectors)
            
            # Extract topics
            topics = []
            feature_names = vectorizer.get_feature_names_out()
            
            for i in range(n_clusters):
                # Get centroid for this cluster
                centroid = kmeans.cluster_centers_[i]
                
                # Get top terms for this topic
                top_indices = centroid.argsort()[-10:][::-1]
                top_terms = [feature_names[idx] for idx in top_indices if centroid[idx] > 0]
                
                # Get sentences in this cluster
                cluster_sentences = [sentences[j] for j in range(len(sentences)) if clusters[j] == i]
                
                if top_terms and cluster_sentences:
                    topics.append({
                        'topic_id': i,
                        'terms': top_terms[:5],
                        'sentences': cluster_sentences[:3],
                        'weight': float(centroid.max())
                    })
            
            return sorted(topics, key=lambda x: x['weight'], reverse=True)
            
        except Exception:
            return []
    
    def get_text_statistics(self, text: str) -> Dict[str, Any]:
        """Get basic statistics about the text."""
        if not text:
            return {
                'character_count': 0,
                'word_count': 0,
                'sentence_count': 0,
                'paragraph_count': 0,
                'avg_words_per_sentence': 0,
                'avg_chars_per_word': 0
            }
        
        # Basic counts
        char_count = len(text)
        words = re.findall(r'\b\w+\b', text)
        word_count = len(words)
        sentences = self.extract_sentences(text)
        sentence_count = len(sentences)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        paragraph_count = len(paragraphs)
        
        # Averages
        avg_words_per_sentence = word_count / sentence_count if sentence_count > 0 else 0
        avg_chars_per_word = sum(len(word) for word in words) / word_count if word_count > 0 else 0
        
        return {
            'character_count': char_count,
            'word_count': word_count,
            'sentence_count': sentence_count,
            'paragraph_count': paragraph_count,
            'avg_words_per_sentence': round(avg_words_per_sentence, 2),
            'avg_chars_per_word': round(avg_chars_per_word, 2)
        }
    
    def process_text(self, text: str) -> Dict[str, Any]:
        """Process text and return comprehensive analysis."""
        if not text:
            return {}
        
        cleaned_text = self.clean_text(text)
        
        return {
            'cleaned_text': cleaned_text,
            'statistics': self.get_text_statistics(text),
            'keywords': self.extract_keywords(cleaned_text),
            'entities': self.extract_entities(text),
            'sentiment': self.analyze_sentiment(cleaned_text),
            'topics': self.extract_topics(cleaned_text),
            'sentences': self.extract_sentences(cleaned_text)
        }