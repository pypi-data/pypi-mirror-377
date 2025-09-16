import re

# Pattern & sequences
print(re.search(r"\d+\.\d+", "Python 3.10 released").group())
print(re.findall(r"\w+", "Data123 Science_2025 is awesome"))
print(re.findall(r"\D+", "CS101 - Intro to AI"))

# Quantifiers & special patterns
print(re.findall(r"[aeiouAEIOU]{2,}", "The rain in Spain stays mainly in the plain."))
print(re.findall(r"\b\w{3,5}\b", "Data science is fun and useful"))
print(re.findall(r"\b[A-Z][a-z]*\b", "Dr. John and Mr. Smith went to Washington."))
print(re.findall(r"\d+\.\d+|\d+", "Prices are: 12, 45.67, and 89.0 USD."))

# Emails from file
open("email.txt","w").write("john@example.com jane@mail.org sales@company.com")
print(re.findall(r"[\w.%+-]+@[\w.-]+\.[A-Za-z]{2,}", open("email.txt").read()))

# HTML parsing
open("sample.html","w").write('<title>Sample</title><title>Another</title><a href="https://x.com">x</a>')
html=open("sample.html").read()
print(re.findall(r"<title>(.*?)</title>",html))
print(re.findall(r'href=["\'](.*?)["\']',html))

# Regex functions
t="Contact info@example.com or sales@example.org"
print(re.search(r"[\w.%+-]+@[\w.-]+\.[A-Za-z]{2,}",t).group())
print(re.findall(r"[\w.%+-]+@[\w.-]+\.[A-Za-z]{2,}",t))
print(re.sub(r"[\w.%+-]+@[\w.-]+\.[A-Za-z]{2,}","[REDACTED]",t))
