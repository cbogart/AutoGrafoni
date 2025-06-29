#!/usr/bin/env python3
"""
Unit test for the _clean_text function
"""

import re
import os
from pathlib import Path

def _clean_text(text):
    """Clean and prepare text for conversion - copied from the main script"""
    # Remove Project Gutenberg header/footer
    text = re.sub(r'\*\*\* START OF .* \*\*\*.*?\*\*\* END OF .* \*\*\*', '', text, flags=re.DOTALL)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s.,!?;:\'\"()-]', '', text)
    
    return text.strip()

def test_clean_text_with_actual_book():
    """Test the _clean_text function with actual Pride and Prejudice text"""
    
    # Check if we have the cached book
    cache_file = Path("gutenberg_cache/1342.txt")
    
    if not cache_file.exists():
        print("No cached book found. Please run the main script first to download the book.")
        return
    
    print("Loading actual Pride and Prejudice text...")
    with open(cache_file, 'r', encoding='utf-8') as f:
        original_text = f.read()
    
    print(f"Original text length: {len(original_text)} characters")
    print(f"First 500 characters: {original_text[:500]}...")
    print(f"Last 500 characters: {original_text[-500:]}...")
    
    # Test the cleaning function
    print("\n" + "=" * 60)
    print("Testing _clean_text function...")
    
    cleaned_text = _clean_text(original_text)
    
    print(f"Cleaned text length: {len(cleaned_text)} characters")
    
    if len(cleaned_text) == 0:
        print("❌ PROBLEM: _clean_text returned empty string!")
        print("\nLet's debug step by step...")
        
        # Test each regex step separately
        print("\n1. Testing header/footer removal...")
        step1 = re.sub(r'\*\*\* START OF .* \*\*\*.*?\*\*\* END OF .* \*\*\*', '', original_text, flags=re.DOTALL)
        print(f"   After header removal: {len(step1)} characters")
        print(f"   First 200 chars: {step1[:200]}...")
        
        print("\n2. Testing whitespace normalization...")
        step2 = re.sub(r'\s+', ' ', step1)
        print(f"   After whitespace normalization: {len(step2)} characters")
        print(f"   First 200 chars: {step2[:200]}...")
        
        print("\n3. Testing special character removal...")
        step3 = re.sub(r'[^\w\s.,!?;:\'\"()-]', '', step2)
        print(f"   After special char removal: {len(step3)} characters")
        print(f"   First 200 chars: {step3[:200]}...")
        
        print("\n4. Testing final strip...")
        step4 = step3.strip()
        print(f"   After final strip: {len(step4)} characters")
        print(f"   First 200 chars: {step4[:200]}...")
        
        # Check what characters are being removed
        print("\nAnalyzing what characters are being removed...")
        unique_chars = set(step2)
        removed_chars = [c for c in unique_chars if c not in step3]
        print(f"Characters removed by special char regex: {removed_chars[:20]}...")
        
    else:
        print("✅ _clean_text worked correctly!")
        print(f"First 200 characters of cleaned text: {cleaned_text[:200]}...")
        
        # Test sentence splitting
        sentences = re.split(r'[.!?]+', cleaned_text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 5]
        print(f"\nNumber of sentences found: {len(sentences)}")
        
        if sentences:
            print("First few sentences:")
            for i, sentence in enumerate(sentences[:3]):
                print(f"{i+1}. {sentence[:100]}...")

def test_improved_clean_text():
    """Test an improved version of the clean_text function"""
    
    cache_file = Path("gutenberg_cache/1342.txt")
    if not cache_file.exists():
        print("No cached book found. Skipping improved test.")
        return
    
    with open(cache_file, 'r', encoding='utf-8') as f:
        original_text = f.read()
    
    print("\n" + "=" * 60)
    print("Testing improved _clean_text function...")
    
    def improved_clean_text(text):
        """Improved version that's less aggressive"""
        # Remove Project Gutenberg header/footer more carefully
        text = re.sub(r'\*\*\* START OF THE PROJECT GUTENBERG EBOOK .*? \*\*\*', '', text, flags=re.DOTALL)
        text = re.sub(r'\*\*\* START OF THIS PROJECT GUTENBERG EBOOK .*? \*\*\*', '', text, flags=re.DOTALL)
        text = re.sub(r'\*\*\* END OF THE PROJECT GUTENBERG EBOOK .*? \*\*\*', '', text, flags=re.DOTALL)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove some special characters but keep more content
        text = re.sub(r'[^\w\s.,!?;:\'\"()-]', ' ', text)
        
        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    cleaned_text = improved_clean_text(original_text)
    print(f"Improved cleaned text length: {len(cleaned_text)} characters")
    
    if len(cleaned_text) > 0:
        print("✅ Improved version worked!")
        print(f"First 200 characters: {cleaned_text[:200]}...")
        
        # Test sentence splitting
        sentences = re.split(r'[.!?]+', cleaned_text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 5]
        print(f"Number of sentences: {len(sentences)}")
        
        if sentences:
            print("First sentence: {sentences[0][:100]}...")
    else:
        print("❌ Even improved version returned empty string!")

if __name__ == "__main__":
    test_clean_text_with_actual_book()
    test_improved_clean_text() 