import re

a="Python release"
b="Data123 is awesome"
c="CS123 Intro to AI"
d="The rain in india"
e="Data sciEnce is fun"
f="Hello World python"
g="Price are 45.67, 89.00, and 100.5"
m="abc@dev.com abc@mail.org abc@company.com"
h='<title>Sample</title><title>Another</title><a href="https://x.com">x</a>'
t="Contact abc@example.com or abc@example.org"
p=r"[\w.%+-]+@[\w.-]+\.[A-Za-z]{2,}"

num = re.search(r"\d+\.\d+", a)
print(num.group() if num else "No match")

print(re.findall(r"\w+", b))
print(re.findall(r"\D+", c))
print(re.findall(r"[aeiouAEIOU]{2,}", d))
print(re.findall(r"\b\w{3,5}\b", e))
print(re.findall(r"\b[A-Z][a-z]*\b", f))
print(re.findall(r"\d+\.?\d*", g))
print(re.findall(p, m))
print(re.findall(r"<title>(.*?)</title>", h))
print(re.findall(r'href=["\'](.*?)["\']', h))
print(re.search(p, t).group())
print(re.findall(p, t))
print(re.sub(p, "[REDACTED]", t))
