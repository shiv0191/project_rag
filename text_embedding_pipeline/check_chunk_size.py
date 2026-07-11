import json

lengths = []

with open("input/chunks_final.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        doc = json.loads(line)
        lengths.append(len(doc["page_content"]))

print(f"Chunks        : {len(lengths)}")
print(f"Average chars : {sum(lengths)/len(lengths):.0f}")
print(f"Maximum chars : {max(lengths)}")
print(f"Minimum chars : {min(lengths)}")
