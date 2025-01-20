from PIL import Image, ImageDraw, ImageFont
import os

def generate_logo():
    # 創建一個 400x200 的白色圖片
    img = Image.new('RGB', (400, 200), color='white')
    d = ImageDraw.Draw(img)
    
    # 添加文字
    try:
        # 嘗試使用系統字體
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        # 如果找不到字體，使用默認字體
        font = ImageFont.load_default()
    
    # 繪製文字
    d.text((50, 80), "Line AI Assistant", font=font, fill='black')
    
    # 確保目錄存在
    os.makedirs("assets", exist_ok=True)
    
    # 保存圖片
    img.save("assets/logo.png")

if __name__ == "__main__":
    generate_logo() 