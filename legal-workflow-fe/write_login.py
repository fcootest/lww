
import os
path = os.path.join("src", "pages", "LoginPage.tsx")
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
