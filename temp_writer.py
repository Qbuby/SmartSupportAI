import sys

# 从命令行参数获取文件名和内容
if len(sys.argv) < 3:
    print("Usage: python temp_writer.py <filename> <content>")
    sys.exit(1)

filename = sys.argv[1]
content = sys.argv[2]

with open(filename, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"File {filename} created successfully")
